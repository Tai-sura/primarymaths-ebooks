/**
 * Is the published site actually serving this build?
 *
 *   node check_live.mjs p5m07a
 *   node check_live.mjs p5m07a --base https://example.github.io/site/ --expect-cache ebooks-v153
 *
 * A push that changed nothing looks exactly like a push that broke the page until
 * someone opens it. This opens it: the service worker's CACHE, the book's status,
 * the reader page and the three files the reader fetches must all answer 200, and
 * with --expect-cache the published cache must be the one just built.
 *
 * Exit code 0 = the live site serves this book; 1 = something is missing or stale.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const args = process.argv.slice(2);
const id = args.find((a) => !a.startsWith("--"));
if (!id) {
  console.log("usage: node check_live.mjs <book-id> [--base URL] [--expect-cache ebooks-vN]");
  process.exit(2);
}
const baseArg = args.indexOf("--base");
const cacheArg = args.indexOf("--expect-cache");
const book = JSON.parse(fs.readFileSync(path.join(ROOT, "books", id, "book.json"), "utf8"));
const localCache = /const CACHE = "([^"]+)"/.exec(fs.readFileSync(path.join(ROOT, "sw.js"), "utf8"))?.[1];
const base = baseArg >= 0 ? args[baseArg + 1] : (book.live || "").replace(/reader\.html.*$/, "") || "https://tai-sura.github.io/primarymaths-ebooks/";
const expect = cacheArg >= 0 ? args[cacheArg + 1] : localCache;
const root = base.endsWith("/") ? base : `${base}/`;

const fails = [];
const get = async (p, type = "json") => {
  const url = new URL(p, root).href;
  let res;
  try {
    res = await fetch(url, { cache: "no-store" });
  } catch (e) {
    fails.push(`${url}: ${String(e).slice(0, 90)}`);
    return null;
  }
  if (!res.ok) {
    fails.push(`${url}: HTTP ${res.status}`);
    return null;
  }
  return type === "text" ? res.text() : res.json();
};

const sw = await get("sw.js", "text");
const liveCache = sw ? /const CACHE = "([^"]+)"/.exec(sw)?.[1] : null;
if (liveCache && expect && liveCache !== expect) fails.push(`live sw.js has CACHE "${liveCache}", expected "${expect}" - the deploy did not land, or CACHE was not bumped`);
const live = await get(`books/${id}/book.json`);
if (live && live.status !== "live") fails.push(`live book.json status is "${live.status}", not live`);
for (const p of [`reader.html?book=${id}`, `books/${id}/layout.json`, `books/${id}/solutions.js`]) {
  const text = await get(p, "text");
  if (text === null && p.endsWith(".js")) fails.push(`${p}: not served`);
}
if (live?.answerStamps?.length) {
  const imgs = fs.readdirSync(path.join(ROOT, "books", id, "answers"));
  const first = await get(`books/${id}/answers/${imgs[0]}`, "text");
  if (first === null) fails.push("a stamp image is not served");
}

console.log(`${id} @ ${root}`);
console.log(`  CACHE  ${liveCache || "?"}${expect ? ` (expected ${expect})` : ""}`);
console.log(`  status ${live?.status || "?"}`);
console.log(`  reader, layout, solutions ${fails.length ? "FAIL" : "200"}`);
fails.forEach((m) => console.log("  FAIL  " + m));
console.log(fails.length ? "  FAIL  the live site does not serve this build" : "  OK    the live site serves this build");
process.exit(fails.length ? 1 : 0);
