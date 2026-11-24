// Screenshot one question's answer region after the reveal animation has settled.
// Usage: node tools/qa/shot_settled.mjs <book-id> <qid> <out.png>
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const [id = "phy11", qid = "q19", out = "settled.png"] = process.argv.slice(2);
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

  const box = await page.evaluate(async (qid) => {
    const qa = document.querySelector(`.qa[data-q="${qid}"]`);
    if (!qa) return null;
    // jump the reader to this question the way the UI does
    qa.scrollIntoView?.({ block: "center" });
    qa.querySelector('.ctl button[data-act="all"]')?.click();
    return true;
  }, qid);
  if (!box) { console.log("question not found"); }
  await sleep(1200); // let every transition finish
  const clip = await page.evaluate((qid) => {
    const qa = document.querySelector(`.qa[data-q="${qid}"]`);
    const r = qa.getBoundingClientRect();
    return { x: Math.max(0, r.x - 12), y: Math.max(0, r.y - 12), width: r.width + 24, height: r.height + 24 };
  }, qid);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  await page.screenshot({ path: out, clip });
  console.log("wrote", out, JSON.stringify(clip));
} finally {
  await browser.close();
  server.close();
}
