// The Play buttons of a book: one per stamped answer, the same button as the
// inline (LQ) answer's Play, on blank paper, tappable.
//
//   node check_play.mjs <book-id> [--shots <dir>]
//
// A book whose answers are cut from the ANS page ("answerStamps") shows each one
// from its own ▸ button. That button must look and measure exactly like the ▶/▸
// button an LQ answer uses, must not cover printed ink or another button, must
// not sit under the reader's docked toolbar, and must open and close its answer.
// check_answer_chips.py proves the blank paper from the layout; this proves what
// the reader actually renders, in a real browser, at iPad size.
import http from "node:http"; import fs from "node:fs"; import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".webmanifest": "application/manifest+json" };
const book = process.argv[2];
if (!book) { console.error("usage: node check_play.mjs <book-id> [--shots <dir>]"); process.exit(2); }
const shotsAt = process.argv.indexOf("--shots");
const shots = shotsAt > 0 ? process.argv[shotsAt + 1] : null;
if (shots) fs.mkdirSync(shots, { recursive: true });

const layout = JSON.parse(fs.readFileSync(path.join(ROOT, "books", book, "layout.json"), "utf8"));
const stamped = layout.pages.flatMap((p) => p.questions.filter((q) => q.stamps?.length).map((q) => q.id));
// Only the questions whose widgets.js registers a picture get the amber button
// (hasGraphic in engine/book.js), so only those are counted below.
const widgetsPath = path.join(ROOT, "books", book, "widgets.js");
const widgetIds = fs.existsSync(widgetsPath)
  ? new Set([...fs.readFileSync(widgetsPath, "utf8").matchAll(/^\s{2}([A-Za-z]\w*)\s*:\s*\(root\)/gm)].map((m) => m[1]))
  : new Set();

const server = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const f = path.join(ROOT, u);
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404).end(); return; }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream", "Cache-Control": "no-store" });
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}/`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await puppeteer.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: "new" });
const page = await browser.newPage();
const errs = [];
page.on("pageerror", (e) => errs.push(String(e).slice(0, 160)));
await page.setViewport({ width: 1180, height: 900, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await page.goto(`${base}reader.html?book=${book}`, { waitUntil: "networkidle0" });
await sleep(1800);

const fails = [];
let sizesLine = null;
let graphicLine = 'no graphic button';
if (!stamped.length) {
  console.log(`${book}: no stamped answers, nothing to check`);
} else {
  const seen = await page.evaluate(() => document.querySelectorAll(".ans-play:not(.ans-graphic)").length);
  if (seen !== stamped.length) fails.push(`${seen} Play button(s) for ${stamped.length} stamped answer(s)`);

  const spec = {};
  let graphicCount = 0;
  for (const p of layout.pages) {
    for (const q of p.questions) {
      if (!q.stamps?.length) continue;
      const [w, h] = q.playSize || [24, 22];
      const g = q.graphicAt && widgetIds.has(q.id) ? [w, h] : null;
      if (g) graphicCount += 1;
      spec[q.id] = { w, h, blank: q.blankAt || null, pageW: p.width, pageH: p.height, g };
    }
  }

  const report = await page.evaluate((spec) => {
    const box = (el) => { const r = el.getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height }; };
    const plays = [...document.querySelectorAll(".ans-play:not(.ans-graphic)")];
    const lq = document.querySelector('.ctl button[data-act="next"]');
    const lqStyle = lq ? getComputedStyle(lq) : null;
    const bad = [];
    const near = [];
    const sizes = new Set();
    if (lq) {
      for (const el of plays) {
        const s = getComputedStyle(el), b = box(el);
        const want = spec[el.dataset.q] || { w: 24, h: 22 };
        const sh = el.closest(".sheet");
        const scale = sh ? sh.getBoundingClientRect().width / want.pageW : 1;
        sizes.add(`${want.w}x${want.h}`);
        if (Math.abs(b.w - want.w * scale) > 1.2 || Math.abs(b.h - want.h * scale) > 1.2) {
          bad.push(`${el.dataset.q}: drawn ${(b.w / scale).toFixed(1)}x${(b.h / scale).toFixed(1)} pt, layout says ${want.w}x${want.h}`);
        }
        if (s.backgroundColor !== lqStyle.backgroundColor) bad.push(`${el.dataset.q}: fill ${s.backgroundColor} vs LQ ${lqStyle.backgroundColor}`);
        if (s.color !== lqStyle.color) bad.push(`${el.dataset.q}: glyph colour ${s.color} vs LQ ${lqStyle.color}`);
        if ((el.textContent || "").trim() !== "▸") bad.push(`${el.dataset.q}: glyph ${JSON.stringify(el.textContent)}`);
        // Beside its own blank, not parked elsewhere on the page.
        if (want.blank && sh) {
          const sr = sh.getBoundingClientRect();
          const cxpt = (b.l + b.w / 2 - sr.left) / scale;
          const dxBlank = Math.abs(cxpt - want.blank[0]);
          const dxLine = want.blank.length > 2 ? Math.abs(cxpt - want.blank[2]) : Infinity;
          const dx = Math.min(dxBlank, dxLine);
          const dy = (b.t - sr.top) / scale - want.blank[1];
          near.push(dx);
          if (dx > 70 || Math.abs(dy) > 46) {
            bad.push(`${el.dataset.q}: ${Math.round(dx)} pt from its blank/line end, ${Math.round(dy)} pt below/above it (limit 70 / 46)`);
          }
        }
      }
    }
    for (let i = 0; i < plays.length; i++) {
      for (let j = i + 1; j < plays.length; j++) {
        const a = box(plays[i]), c = box(plays[j]);
        if (a.l < c.r - 0.5 && c.l < a.r - 0.5 && a.t < c.b - 0.5 && c.t < a.b - 0.5) bad.push(`${plays[i].dataset.q} overlaps ${plays[j].dataset.q}`);
      }
    }
    const tb = document.getElementById("toolbar")?.getBoundingClientRect();
    if (tb) for (const el of plays) {
      const b = box(el);
      if (b.r > tb.left && b.t < tb.bottom && b.b > tb.top) bad.push(`${el.dataset.q}: under the toolbar`);
    }
    return { bad, hasLq: Boolean(lq), sizes: [...sizes].join(" "), worst: near.length ? Math.max(...near) : null };
  }, spec);
  fails.push(...report.bad);
  sizesLine = report.sizes;
  if (!report.hasLq) console.log(`${book}: no inline answer on this book, matching the LQ Play was not measurable`);

  // The amber second button of a stamped answer that carries a widget: drawn at the
  // size recorded in layout.json, clear of the toolbar, and a tap opens the drawer.
  const gs = await page.evaluate((spec) => {
    const bad = [];
    const els = [...document.querySelectorAll('.ans-play[data-act="graphic"]')];
    const boxOf = (el) => el.getBoundingClientRect();
    for (const el of els) {
      const want = spec[el.dataset.q];
      if (!want || !want.g) { bad.push(`${el.dataset.q}: graphic button for a question with no graphicAt`); continue; }
      const sh = el.closest(".sheet");
      const scale = sh ? sh.getBoundingClientRect().width / want.pageW : 1;
      const b = boxOf(el);
      if (Math.abs(b.width - want.g[0] * scale) > 1.2 || Math.abs(b.height - want.g[1] * scale) > 1.2) {
        bad.push(`${el.dataset.q}: graphic drawn ${(b.width / scale).toFixed(1)}x${(b.height / scale).toFixed(1)} pt, layout says ${want.g[0]}x${want.g[1]}`);
      }
      if (!el.classList.contains("ans-graphic")) bad.push(`${el.dataset.q}: graphic button lost its ans-graphic class`);
      if (!(el.textContent || "").trim() && !el.querySelector("svg")) bad.push(`${el.dataset.q}: graphic button has no glyph`);
      const tb = document.getElementById("toolbar")?.getBoundingClientRect();
      if (tb && b.right > tb.left && b.top < tb.bottom && b.bottom > tb.top) bad.push(`${el.dataset.q}: graphic button under the toolbar`);
    }
    for (let i = 0; i < els.length; i++) {
      for (let j = i + 1; j < els.length; j++) {
        const a = boxOf(els[i]), c = boxOf(els[j]);
        if (a.left < c.right - 0.5 && c.left < a.right - 0.5 && a.top < c.bottom - 0.5 && c.top < a.bottom - 0.5) {
          bad.push(`${els[i].dataset.q} graphic overlaps ${els[j].dataset.q} graphic`);
        }
      }
    }
    const first = els[0] && { q: els[0].dataset.q, x: boxOf(els[0]).left + boxOf(els[0]).width / 2, y: boxOf(els[0]).top + boxOf(els[0]).height / 2 };
    return { n: els.length, bad, first };
  }, spec);
  graphicLine = `${gs.n} amber graphic button(s) open the drawer`;
  if (gs.n !== graphicCount) fails.push(`${gs.n} graphic button(s) for ${graphicCount} question(s) with a graphicAt`);
  fails.push(...gs.bad);
  if (gs.first) {
    await page.evaluate((q) => {
      const el = document.querySelector(`.ans-play[data-act="graphic"][data-q="${q}"]`);
      el.scrollIntoView({ block: "center" });
    }, gs.first.q);
    await sleep(250);
    const tapAt = await page.evaluate((q) => {
      const b = document.querySelector(`.ans-play[data-act="graphic"][data-q="${q}"]`).getBoundingClientRect();
      return { x: b.left + b.width / 2, y: b.top + b.height / 2 };
    }, gs.first.q);
    await page.touchscreen.tap(tapAt.x, tapAt.y);
    await sleep(500);
    const drawn = await page.evaluate(() => {
      const d = document.getElementById("graphic");
      return { open: Boolean(d && d.classList.contains("open")), kids: document.querySelectorAll("#graphic-body svg, #graphic-body .g-svg, #graphic-body input").length };
    });
    if (!drawn.open) fails.push(`${gs.first.q}: tapping the graphic button did not open the drawer`);
    else if (!drawn.kids) fails.push(`${gs.first.q}: the drawer opened empty`);
    await page.keyboard.press("Escape");
    await sleep(300);
  }

  // The button must open its answer and close it again.
  const first = await page.evaluate(() => {
    const el = document.querySelector(".ans-play:not(.ans-graphic)");
    const r = el.getBoundingClientRect();
    if (r.top < 0 || r.bottom > innerHeight) el.scrollIntoView({ block: "center" });
    const b = el.getBoundingClientRect();
    return { q: el.dataset.q, x: b.left + b.width / 2, y: b.top + b.height / 2 };
  });
  await sleep(250);
  await page.touchscreen.tap(first.x, first.y);
  await sleep(400);
  const open = await page.evaluate((q) => document.querySelectorAll(`.qa.stamp[data-q="${q}"] .ln:not(.hid)`).length, first.q);
  if (open !== 1) fails.push(`${first.q}: tap showed ${open} answer line(s), expected 1`);
  await page.touchscreen.tap(first.x, first.y);
  await sleep(300);
  const shut = await page.evaluate((q) => document.querySelectorAll(`.qa.stamp[data-q="${q}"] .ln:not(.hid)`).length, first.q);
  if (shut !== 0) fails.push(`${first.q}: second tap left ${shut} answer line(s) showing`);

  if (shots) {
    for (const pg of [...new Set(layout.pages.filter((p) => p.questions.some((q) => q.stamps?.length)).map((p) => p.page))]) {
      await page.evaluate((n) => { location.hash = `p${n}`; }, pg);
      await sleep(800);
      await page.screenshot({ path: path.join(shots, `p${String(pg).padStart(2, "0")}.png`) });
    }
  }
}
if (errs.length) fails.push(`page errors: ${errs.slice(0, 2).join(" | ")}`);
await browser.close();
server.close();

if (fails.length) {
  console.log(`FAIL ${book}: ${fails.length} problem(s)`);
  for (const f of fails.slice(0, 20)) console.log(`  ${f}`);
  process.exit(1);
}
console.log(`${book}: ${stamped.length} Play button(s) beside their blanks (sizes ${sizesLine || "-"}), same as the LQ Play, blank and tappable; ${graphicLine} / OK`);
