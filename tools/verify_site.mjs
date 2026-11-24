// Poll the published site until the key assets answer 200.
import https from "node:https";

const base = "https://tai-sura.github.io/phy11-projectile-ebook";
const paths = [
  "/reader.html",
  "/index.html",
  "/books/catalog.json",
  "/books/phy11/book.json",
  "/books/phy11/layout.json",
  "/books/phy11/solutions.js",
  "/books/phy11/widgets.js",
  "/books/phy11/pages/p01.jpg",
  "/books/phy11/pages/p10.jpg",
  "/engine/authoring.js",
  "/engine/widgets/kit.js",
  "/vendor/katex/katex.min.css",
];

function get(path) {
  return new Promise((resolve) => {
    const req = https.get(base + path, { headers: { "User-Agent": "dsh-check" } }, (res) => {
      let n = 0;
      res.on("data", (c) => (n += c.length));
      res.on("end", () => resolve({ path, status: res.statusCode, bytes: n }));
    });
    req.on("error", (e) => resolve({ path, status: 0, bytes: 0, err: e.message }));
    req.setTimeout(20000, () => { req.destroy(); resolve({ path, status: 0, bytes: 0, err: "timeout" }); });
  });
}

const deadline = Date.now() + 240000;
let ok = false;
while (Date.now() < deadline) {
  const res = await Promise.all(paths.map(get));
  const bad = res.filter((r) => r.status !== 200);
  if (!bad.length) {
    ok = true;
    for (const r of res) console.log(`200  ${String(r.bytes).padStart(8)} B  ${r.path}`);
    break;
  }
  console.log(`waiting… ${bad.length} not ready (${bad.map((b) => `${b.path}:${b.status}`).slice(0, 3).join(" ")})`);
  await new Promise((r) => setTimeout(r, 15000));
}
console.log(ok ? "SITE OK" : "SITE NOT READY");
