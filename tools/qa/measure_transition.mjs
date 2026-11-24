// Compare the control strip's position right after a reveal and after it settles.
// Usage: node tools/qa/measure_transition.mjs <book-id>
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const id = process.argv[2] || "phy11";
const CHROME = process.env.CHROME || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".woff": "font/woff",
  ".ttf": "font/ttf", ".webmanifest": "application/manifest+json",
};
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const file = path.join(ROOT, url.endsWith("/") ? `${url}index.html` : url);
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404).end(); return; }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}/`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await page.goto(`${base}reader.html?book=${id}`, { waitUntil: "networkidle0" });
  await sleep(1500);

  const ids = await page.evaluate(() => [...document.querySelectorAll(".qa[data-q]")].map((e) => e.dataset.q));
  const rows = [];
  for (const q of ids) {
    const snap = () => page.evaluate((qid) => {
      const qa = document.querySelector(`.qa[data-q="${qid}"]`);
      const ctl = qa.querySelector(".ctl");
      return { left: Math.round(parseFloat(ctl.style.left) || 0), inline: ctl.style.left };
    }, q);
    await page.evaluate((qid) => {
      document.querySelector(`.qa[data-q="${qid}"]`).querySelector('.ctl button[data-act="all"]')?.click();
    }, q);
    const t0 = await snap();            // same tick + one frame
    await sleep(60);
    const t60 = await snap();
    await sleep(900);
    const t1 = await snap();
    rows.push({ q, t0: t0.left, t60: t60.left, t1: t1.left, css: t0.inline });
  }
  console.log("qid      t=0ms   t=60ms  t=960ms   css left");
  for (const r of rows) console.log(`${r.q.padEnd(6)} ${String(r.t0).padStart(7)} ${String(r.t60).padStart(7)} ${String(r.t1).padStart(7)}   ${r.css}`);
  const moving = rows.filter((r) => r.t0 !== r.t1);
  console.log(moving.length ? `MOVES on ${moving.length}/${rows.length} questions (transition between t=0 and t=960ms)` : "NO MOVEMENT");
} finally {
  await browser.close();
  server.close();
}
