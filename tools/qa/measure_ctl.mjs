// Does the step-control strip ever sit on top of answer ink?
// Checks the toolbar "Show all answers" path and a tall-viewport relayout.
// Usage: node tools/qa/measure_ctl.mjs <book-id>
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

const MEASURE = () => {
  const out = [];
  for (const qa of document.querySelectorAll(".qa[data-q]")) {
    const ctl = qa.querySelector(".ctl");
    if (!ctl) continue;
    const qaR = qa.getBoundingClientRect();
    const cR = ctl.getBoundingClientRect();
    if (!cR.width || !qaR.width) continue;
    // Only visible text counts as ink: hidden steps keep their space but show nothing.
    let ink = -Infinity;
    for (const ln of qa.querySelectorAll(".ln")) {
      if (ln.classList.contains("hid") || ln.closest(".ctl")) continue;
      const r = ln.getBoundingClientRect();
      if (!r.width || r.height < 2) continue;
      let right = r.right;
      for (const rs of ln.querySelectorAll(".rs")) {
        const rr = rs.getBoundingClientRect();
        if (rr.width) right = Math.max(right, rr.right);
      }
      if (right > ink) ink = right;
    }
    const over = ink > cR.left + 1 ? Math.round(ink - cR.left) : 0;
    out.push({ q: qa.dataset.q, qaW: Math.round(qaR.width), ctlLeft: Math.round(cR.left - qaR.left), over });
  }
  return out;
};

const browser = await puppeteer.launch({ executablePath: CHROME, headless: "new" });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await page.goto(`${base}reader.html?book=${id}`, { waitUntil: "networkidle0" });
  await sleep(1500);

  const report = (label, rows) => {
    const bad = rows.filter((r) => r.over > 1);
    console.log(`\n[${label}] questions ${rows.length}, overlapping ${bad.length}`);
    for (const r of bad) console.log(`   OVER q${r.q.replace("q", "")} by ${r.over}px  (qaW ${r.qaW}, ctlLeft ${r.ctlLeft})`);
    return bad.length;
  };

  await page.tap("#show-all");
  await sleep(1200);
  let bad = report("Show all answers", await page.evaluate(MEASURE));

  // the shot path: a tall viewport forces a full relayout
  await page.setViewport({ width: 1180, height: 1800, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  await sleep(1200);
  bad += report("tall viewport relayout", await page.evaluate(MEASURE));

  // and back again
  await page.setViewport({ width: 1180, height: 820, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await sleep(1200);
  bad += report("back to iPad", await page.evaluate(MEASURE));

  // single question, step by step
  await page.tap("#hide-all");
  await sleep(600);
  for (let i = 0; i < 6; i++) {
    await page.evaluate((qid) => document.querySelector(`.qa[data-q="${qid}"] .ctl button[data-act="next"]`).click(), "q19");
    await sleep(120);
  }
  bad += report("q19 stepped by hand", await page.evaluate(MEASURE));

  console.log(bad ? "\nFAIL: the strip covers the working" : "\nPASS: no strip covers the working");
  process.exitCode = bad ? 1 : 0;
} finally {
  await browser.close();
  server.close();
}
