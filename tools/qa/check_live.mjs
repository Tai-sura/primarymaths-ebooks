/**
 * Is the published site actually serving this build?
 *
 *   node check_live.mjs jpfm08
 *   node check_live.mjs jpfm08 --base https://example.github.io/site/ --expect-cache physics-ebooks-v189
 *
 * A push that changed nothing looks exactly like a push that broke the page until
 * someone opens it. This opens it: the service worker's CACHE, the book's status,
 * the reader page and the three files the reader fetches must all answer 200, and
 * with --expect-cache the published cache must be the one just built.
 *
 * sw.js names its cache in one of two shapes, and BOTH must be read, or this check
 * silently stops checking CACHE at all:
 *   const CACHE = "ebooks-v174";                    (before the per-site prefix)
 *   const PREFIX = "physics-ebooks-"; const CACHE = PREFIX + "v189";
 * The second shape is what both sites use since 2026-11-28, because they share one
 * origin and therefore one CacheStorage.
 *
 * Exit code 0 = the live site serves this book; 1 = something is missing or stale.
 *
 * The default base comes from the book's own `live`, else from the `Site:` line of
 * this repository's REPO.md - never from a URL typed in here, which would be a
 * second copy of the truth to drift.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const args = process.argv.slice(2);
const id = args.find((a) => !a.startsWith("--"));
if (!id) {
  console.log("usage: node check_live.mjs <book-id> [--base URL] [--expect-cache <full cache name>]");
  process.exit(2);
}
const baseArg = args.indexOf("--base");
const cacheArg = args.indexOf("--expect-cache");

/** The cache name sw.js will end up using, whichever shape it is written in. */
function cacheName(src) {
  if (!src) return undefined;
  const direct = /const CACHE = "([^"]+)"/.exec(src)?.[1];
  if (direct) return direct;
  const prefix = /const PREFIX = "([^"]*)"/.exec(src)?.[1];
  const version = /const CACHE = PREFIX \+ "([^"]+)"/.exec(src)?.[1];
  return version ? `${prefix ?? ""}${version}` : undefined;
}

/** The site this repository publishes, as REPO.md records it. */
function siteFromRepo() {
  const md = path.join(ROOT, "REPO.md");
  if (!fs.existsSync(md)) return "";
  const m = /Site:\s*<([^>]+)>/.exec(fs.readFileSync(md, "utf8"));
  return m ? m[1] : "";
}

const book = JSON.parse(fs.readFileSync(path.join(ROOT, "books", id, "book.json"), "utf8"));
const localCache = cacheName(fs.readFileSync(path.join(ROOT, "sw.js"), "utf8"));
const base = baseArg >= 0
  ? args[baseArg + 1]
  : (book.live || "").replace(/reader\.html.*$/, "") || siteFromRepo();
if (!base) {
  console.log(`no base URL: books/${id}/book.json has no "live", and REPO.md has no "Site:" line`);
  console.log("pass --base https://<user>.github.io/<repo>/");
  process.exit(2);
}
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

if (!localCache) fails.push(`cannot read CACHE from ${path.join(ROOT, "sw.js")} - sw.js changed shape again`);

const sw = await get("sw.js", "text");
const liveCache = sw ? cacheName(sw) : null;
if (!liveCache) fails.push("cannot read the cache name from the published sw.js");
if (liveCache && expect && liveCache !== expect) {
  fails.push(`live sw.js has CACHE "${liveCache}", expected "${expect}" - the deploy did not land, or CACHE was not bumped`);
}

const live = await get(`books/${id}/book.json`);
if (live && live.status !== "live") fails.push(`live book.json status is "${live.status}", not live`);
for (const p of [`reader.html?book=${id}`, `books/${id}/layout.json`, `books/${id}/solutions.js`]) {
  const text = await get(p, "text");
  if (text === null && p.endsWith(".js")) fails.push(`${p}: not served`);
}

// The service worker only refetches when CACHE changes: if a file differs from the
// local one but the CACHE was not bumped, every reader keeps the old copy.
const same = (a, b) => a.replace(/\r\n/g, "\n") === b.replace(/\r\n/g, "\n");
for (const rel of [`books/${id}/book.json`, `books/${id}/layout.json`, `books/${id}/solutions.js`]) {
  const local = fs.readFileSync(path.join(ROOT, rel), "utf8");
  const liveText = await get(rel, "text");
  if (liveText !== null && !same(local, liveText) && liveCache === localCache) {
    fails.push(`${rel} differs from the local build but CACHE is still "${localCache}" - bump it, or readers keep the old file`);
  }
}
if (live?.answerStamps?.length) {
  const dir = path.join(ROOT, "books", id, "answers");
  const imgs = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  if (!imgs.length) fails.push(`books/${id}/book.json declares answerStamps but books/${id}/answers/ is empty or missing`);
  else {
    const first = await get(`books/${id}/answers/${imgs[0]}`, "text");
    if (first === null) fails.push("a stamp image is not served");
  }
}

console.log(`${id} @ ${root}`);
console.log(`  CACHE  ${liveCache || "?"}${expect ? ` (expected ${expect})` : ""}`);
console.log(`  status ${live?.status || "?"}`);
console.log(`  reader, layout, solutions ${fails.length ? "FAIL" : "200"}`);
fails.forEach((m) => console.log("  FAIL  " + m));
console.log(fails.length ? "  FAIL  the live site does not serve this build" : "  OK    the live site serves this build");
process.exit(fails.length ? 1 : 0);
