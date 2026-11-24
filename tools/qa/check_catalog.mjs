/**
 * One book, one folder, one listing: is books/catalog.json consistent with
 * books/ and with each book's own status?
 *
 *   node check_catalog.mjs            (whole site)
 *   node check_catalog.mjs p5m07a     (one book)
 *
 * book.json is the single source of truth: `status` says draft or live, and the
 * catalogue only lists books that exist. A book folder that is not listed never
 * appears in the library; a listed book with no folder is a 404 on the index.
 * Every live book must also have its chapter log in docs/chapters/<id>.md.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const only = process.argv[2];
const fails = [];
const warns = [];

const catalogPath = path.join(ROOT, "books", "catalog.json");
if (!fs.existsSync(catalogPath)) {
  console.log("no books/catalog.json");
  process.exit(2);
}
const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
const listed = new Set(catalog.books || []);

const folders = fs.readdirSync(path.join(ROOT, "books"), { withFileTypes: true })
  .filter((d) => d.isDirectory() && d.name !== "_template")
  .map((d) => d.name);

const ids = only ? [only] : [...new Set([...folders, ...listed])].sort();
let books = 0;
for (const id of ids) {
  const dir = path.join(ROOT, "books", id);
  const bookPath = path.join(dir, "book.json");
  if (!fs.existsSync(bookPath)) {
    fails.push(`${id}: listed in books/catalog.json but books/${id}/book.json does not exist`);
    continue;
  }
  const book = JSON.parse(fs.readFileSync(bookPath, "utf8"));
  books += 1;
  if (book.id !== id) fails.push(`${id}: book.json says id "${book.id}" - the folder and the id must match`);
  if (!["draft", "live"].includes(book.status)) fails.push(`${id}: status "${book.status}" is not draft or live`);
  if (listed.has(id) === false && book.status === "live") fails.push(`${id}: status is live but books/catalog.json does not list it`);
  if (!listed.has(id)) warns.push(`${id}: exists on disk but is not in the catalogue (invisible in the library)`);
  if (book.status === "live") {
    const log = path.join(ROOT, "docs", "chapters", `${id}.md`);
    if (!fs.existsSync(log)) fails.push(`${id}: live but docs/chapters/${id}.md is missing - record the book's decisions`);
  }
  const solutionPath = path.join(dir, "solutions.js");
  if (!fs.existsSync(solutionPath)) fails.push(`${id}: no solutions.js`);
  const layoutPath = path.join(dir, "layout.json");
  if (!fs.existsSync(layoutPath)) fails.push(`${id}: no layout.json (run extract_pages.py)`);
}
for (const id of listed) {
  if (!fs.existsSync(path.join(ROOT, "books", id))) fails.push(`books/catalog.json lists "${id}" but books/${id}/ does not exist`);
}

console.log(`catalog: ${listed.size} listed, ${folders.length} on disk, ${books} checked`);
fails.forEach((m) => console.log("  FAIL  " + m));
warns.forEach((m) => console.log("  WARN  " + m));
const ok = fails.length === 0;
console.log(ok ? (warns.length ? `  OK    no blocking problems, ${warns.length} warning(s)` : "  OK    catalogue and book folders agree") : `  ${fails.length} problem(s)`);
process.exit(ok ? 0 : 1);
