// Probe one question right after a viewport relayout: what the strip is measured against.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const id = process.argv[2] || "phy11";
const qid = process.argv[3] || "q1";
const CHROME = process.env.CHROME || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".webmanifest": "application/manifest+json" };
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

const probe = (qid) => {
  const qa = document.querySelector(`.qa[data-q="${qid}"]`);
  if (!qa) return { missing: true };
  const inner = qa.querySelector(".qa-in");
  const ctl = qa.querySelector(".ctl");
  const kids = [...inner.children].map((el) => ({ l: Math.round(el.offsetLeft), w: Math.round(el.offsetWidth), h: el.offsetHeight }));
  return {
    qaW: Math.round(qa.offsetWidth),
    qaH: Math.round(qa.offsetHeight),
    kids: kids.length,
    maxRight: Math.round(Math.max(0, ...kids.map((k) => k.l + k.w))),
    ctlLeft: ctl.style.left,
    rows: ctl.style.getPropertyValue("--rows"),
    scroll: qa.classList.contains("scroll"),
  };
};

const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await page.goto(`${base}reader.html?book=${id}`, { waitUntil: "networkidle0" });
  await sleep(1500);
  await page.tap("#show-all");
  await sleep(1200);
  console.log("after show-all      ", JSON.stringify(await page.evaluate(probe, qid)));

  await page.setViewport({ width: 1180, height: 1800, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  for (const wait of [50, 200, 600, 1500]) {
    await sleep(wait);
    console.log(`tall +${String(wait).padStart(4)}ms      `, JSON.stringify(await page.evaluate(probe, qid)));
  }
  await page.setViewport({ width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  for (const wait of [200, 1200]) {
    await sleep(wait);
    console.log(`back +${String(wait).padStart(4)}ms      `, JSON.stringify(await page.evaluate(probe, qid)));
  }
} finally {
  await browser.close();
  server.close();
}
