import http from "node:http"; import fs from "node:fs"; import path from "node:path";
import { fileURLToPath } from "node:url"; import puppeteer from "puppeteer-core";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".webmanifest": "application/manifest+json" };
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
const out = path.join(process.env.TEMP, "p5tapstamps"); fs.mkdirSync(out, { recursive: true });
const b = await puppeteer.launch({ executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", headless: "new" });
const p = await b.newPage();
const errs = []; p.on("pageerror", (e) => errs.push(String(e).slice(0, 160)));
await p.setViewport({ width: 1180, height: 900, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await p.goto(`${base}reader.html?book=p5m07a`, { waitUntil: "networkidle0" });
await sleep(1600);
const before = await p.evaluate(() => ({ stamps: document.querySelectorAll(".ans-stamp").length, visible: [...document.querySelectorAll(".ln.stamp-line")].filter(l => !l.classList.contains("hid")).length, inline: document.querySelectorAll(".qa:not(.card):not(.stamp)").length }));
console.log("mount", JSON.stringify(before));
await p.evaluate(() => { location.hash = "p3"; });
await sleep(800);
await p.screenshot({ path: path.join(out, "p3-closed.png") });
const hit = await p.evaluate(() => { const el = document.querySelector('.qa.stamp[data-q="q1"]'); const r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; });
await p.touchscreen.tap(hit.x, hit.y);
await sleep(500);
const after = await p.evaluate(() => document.querySelectorAll('.qa.stamp[data-q="q1"] .ln:not(.hid)').length);
console.log("tap q1 -> visible stamp lines:", after);
await p.screenshot({ path: path.join(out, "p3-q1-open.png") });
await p.touchscreen.tap(hit.x, hit.y);
await sleep(400);
const again = await p.evaluate(() => document.querySelectorAll('.qa.stamp[data-q="q1"] .ln:not(.hid)').length);
console.log("tap again -> visible:", again);
await p.evaluate(() => { location.hash = "p11"; });
await sleep(800);
await p.screenshot({ path: path.join(out, "p11.png") });
console.log("errors", errs.length ? JSON.stringify(errs.slice(0, 2)) : "none");
await b.close(); server.close();


