/**
 * Checks book.json "embeds" (interactive explainers opened from a page tab).
 *
 *   node check_embed.mjs <book-id> [site-root]
 *
 * Serves the site, opens reader.html?book=<id> as an iPad (1180×820, touch), and
 * for every embed tab on every page:
 *   - the tab exists at its book.json `at` position and is fully inside the page
 *   - clicking it opens the panel, the iframe loads with no page error
 *   - the explainer fits its frame: no vertical or horizontal scroll inside it
 *   - closing removes the iframe (the sketch stops running)
 * Writes one screenshot per embed to books/<id>/reference/qa/embed-*.png and
 * prints a table. Exit code 1 when a check fails.
 */

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const id = process.argv[2];
const ROOT = path.resolve(process.argv[3] || path.join(HERE, "../.."));
if (!id) {
  console.log("Usage: node check_embed.mjs <book-id> [site-root]");
  process.exit(2);
}
const CHROME = process.env.CHROME || [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
].find((p) => fs.existsSync(p));

const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".woff": "font/woff",
  ".ttf": "font/ttf", ".webmanifest": "application/manifest+json", ".mp4": "video/mp4",
};
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const file = path.join(ROOT, url.endsWith("/") ? `${url}index.html` : url);
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const book = JSON.parse(fs.readFileSync(path.join(ROOT, `books/${id}/book.json`), "utf8"));
const embeds = book.embeds || [];
const shotsDir = path.join(ROOT, `books/${id}/reference/qa`);
fs.mkdirSync(shotsDir, { recursive: true });

const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new", args: ["--no-sandbox", "--disable-dev-shm-usage"] });
const page = await browser.newPage();
await page.emulate({
  viewport: { width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  userAgent: "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
});
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });

await page.goto(`${base}/reader.html?book=${id}`, { waitUntil: "networkidle2" });
await page.waitForSelector(".emb-btn", { timeout: 15000 });

const rows = [];
let failed = 0;
const tabs = await page.$$eval(".emb-btn", (nodes) =>
  nodes.map((n) => ({
    index: Number(n.dataset.embed),
    page: n.closest(".sheet").dataset.key,
    left: n.style.left,
    top: n.style.top,
    w: n.getBoundingClientRect().width,
    h: n.getBoundingClientRect().height,
  }))
);

for (const tab of tabs) {
  const item = embeds[tab.index];
  const expect = item.at;
  const posOk = Math.abs(parseFloat(tab.left) - expect[0]) < 0.01 && Math.abs(parseFloat(tab.top) - expect[1]) < 0.01;

  // In-page geometry: the tab must sit wholly inside the sheet, measured in page points.
  const geo = await page.evaluate((i) => {
    const btn = document.querySelector(`.emb-btn[data-embed="${i}"]`);
    const sheet = btn.closest(".sheet");
    const s = sheet.getBoundingClientRect();
    const b = btn.getBoundingClientRect();
    const scale = s.width / 595.32;
    return {
      page: sheet.dataset.key,
      relLeft: (b.left - s.left) / scale,
      relTop: (b.top - s.top) / scale,
      relW: b.width / scale,
      relH: b.height / scale,
      pageW: s.width / scale,
      pageH: s.height / scale,
    };
  }, tab.index);
  const inside = geo.relLeft >= 0 && geo.relTop >= 0 && geo.relLeft + geo.relW <= geo.pageW + 0.01 && geo.relTop + geo.relH <= geo.pageH + 0.01;

  await page.evaluate((i) => document.querySelector(`.emb-btn[data-embed="${i}"]`).click(), tab.index);
  await page.waitForSelector(".embed-modal.open iframe", { timeout: 15000 });
  const frameHandle = await (await page.$(".embed-modal iframe")).contentFrame();
  await frameHandle.waitForSelector("body", { timeout: 20000 });
  await new Promise((r) => setTimeout(r, 1800)); // let the sketch draw its first frame

  const inner = await frameHandle.evaluate(() => {
    const d = document.documentElement;
    const b = document.body;
    return {
      url: location.pathname,
      scrollH: Math.max(d.scrollHeight, b.scrollHeight),
      scrollW: Math.max(d.scrollWidth, b.scrollWidth),
      clientH: window.innerHeight,
      clientW: window.innerWidth,
      canvas: document.querySelectorAll("canvas").length,
      svg: document.querySelectorAll("svg").length,
      text: (document.body.innerText || "").replace(/\s+/g, " ").slice(0, 120),
    };
  });

  const shot = path.join(shotsDir, `embed-p${item.page}-${tab.index}.png`);
  await page.screenshot({ path: shot });

  await page.click(".embed-close");
  const closed = await page.evaluate(() => !document.querySelector(".embed-modal iframe") && !document.querySelector(".embed-modal.open"));

  const vOk = inner.scrollH <= inner.clientH + 1;
  const hOk = inner.scrollW <= inner.clientW + 1;
  const draws = inner.canvas + inner.svg > 0;
  const ok = posOk && inside && vOk && hOk && draws && closed;
  if (!ok) failed++;
  rows.push({
    idx: tab.index, page: item.page, title: item.title,
    at: `${expect[0]},${expect[1]}`, geo: `${geo.relLeft.toFixed(1)},${geo.relTop.toFixed(1)} ${geo.relW.toFixed(0)}x${geo.relH.toFixed(0)}`,
    inside, pos: posOk, draw: inner.canvas ? `canvas ${inner.canvas}` : `svg ${inner.svg}`,
    scroll: `${inner.scrollW}x${inner.scrollH} / ${inner.clientW}x${inner.clientH}`,
    fit: vOk && hOk, closed, ok, shot: path.basename(shot),
  });
}

/* Embeds opened from a question's own graphic button (the amber chart icon). */
for (const [i, item] of embeds.entries()) {
  if (!item.q) continue;
  const sel = `[data-act="graphic"][data-q="${item.q}"]`;
  const buttons = await page.$$eval(sel, (els) => els.length);
  if (!buttons) {
    failed++;
    rows.push({ idx: i, q: item.q, ok: false, note: "no graphic button on the question" });
    continue;
  }
  await page.evaluate((s) => document.querySelector(s).click(), sel);
  await page.waitForSelector(".embed-modal.open iframe", { timeout: 15000 });
  const frame = await (await page.$(".embed-modal iframe")).contentFrame();
  await frame.waitForSelector("body", { timeout: 20000 });
  await new Promise((r) => setTimeout(r, 1800));
  const inner = await frame.evaluate(() => ({
    url: location.pathname,
    scrollH: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight),
    scrollW: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
    clientH: window.innerHeight,
    clientW: window.innerWidth,
    draws: document.querySelectorAll("canvas, svg").length,
  }));
  const shot = path.join(shotsDir, `embed-q-${item.q}.png`);
  await page.screenshot({ path: shot });
  await page.click(".embed-close");
  const closed = await page.evaluate(() => !document.querySelector(".embed-modal iframe"));
  const ok = inner.scrollH <= inner.clientH + 1 && inner.scrollW <= inner.clientW + 1 && inner.draws > 0 && closed;
  if (!ok) failed++;
  rows.push({
    idx: i, q: item.q, via: "question button", url: inner.url,
    draw: inner.draws, scroll: `${inner.scrollW}x${inner.scrollH} / ${inner.clientW}x${inner.clientH}`,
    closed, ok, shot: path.basename(shot),
  });
}

console.log(JSON.stringify(rows, null, 1));
if (errors.length) console.log("page errors:", errors.slice(0, 8));
console.log(failed === 0 && errors.length === 0 ? "EMBED CHECK PASS" : `EMBED CHECK FAIL (${failed} failing, ${errors.length} errors)`);

await browser.close();
server.close();
process.exit(failed === 0 && errors.length === 0 ? 0 : 1);
