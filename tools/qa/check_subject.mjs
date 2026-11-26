#!/usr/bin/env node
/* Guard: this repository carries primary maths only.
 *
 * The mistake it catches: a physics book added to books/catalog.json, which would put a
 * physics book on the maths shelf. Physics codes live in the other repository
 * (Tai-sura/physics-ebooks).
 *
 * Usage: node tools/qa/check_subject.mjs      (exit 1 on a blocking problem)
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const BOOKS = path.join(ROOT, "books");

/* Physics codes belong to Tai-sura/physics-ebooks. Any of them here is a fault. */
const THEIRS = /^(phy\d|spem\d|jpfm\d|jpwm\d)/i;

let fail = 0;
const say = (tag, text) => console.log(`  ${tag.padEnd(7)}${text}`);
const bad = (text) => { fail++; say("FAIL", text); };

const catFile = path.join(BOOKS, "catalog.json");
if (!fs.existsSync(catFile)) { bad("books/catalog.json is missing"); process.exit(1); }
const catalog = JSON.parse(fs.readFileSync(catFile, "utf8")).books;
if (!Array.isArray(catalog) || !catalog.length) bad("books/catalog.json has no books");

console.log("primarymaths-ebooks  (subject: primary maths)");
console.log(`  catalogue: ${catalog.length} entries - ${catalog.join(", ")}`);

for (const code of catalog) {
  if (THEIRS.test(code)) bad(`${code} is a physics code - it belongs in Tai-sura/physics-ebooks`);
  const j = path.join(BOOKS, code, "book.json");
  if (!fs.existsSync(j)) bad(`${code} is in the catalogue but books/${code}/book.json is missing`);
}

const folders = fs.readdirSync(BOOKS, { withFileTypes: true })
  .filter((e) => e.isDirectory()).map((e) => e.name).sort();
const extra = folders.filter((f) => !catalog.includes(f));
if (extra.length) {
  say("frozen", `${extra.length} folder(s) are not in the catalogue and are left alone on purpose: ${extra.join(" ")}`);
}
for (const f of extra) if (THEIRS.test(f)) bad(`physics book folder present here: ${f}`);
const listedNotOnDisk = catalog.filter((c) => !folders.includes(c));
if (listedNotOnDisk.length) bad(`catalogue lists a missing folder: ${listedNotOnDisk.join(", ")}`);

if (fail) { console.log(`FAIL ${fail} blocking problem(s)`); process.exit(1); }
console.log("OK    no blocking problems");
