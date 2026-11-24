// Coverage check: every question has a solution, and every step is a known kind.
import { SOLUTIONS } from "../books/phy11/solutions.js";
import { readFileSync } from "node:fs";

const book = JSON.parse(readFileSync(new URL("../books/phy11/book.json", import.meta.url), "utf8"));
const qs = book.extract.questions.map((q) => q.id);
const ids = SOLUTIONS.map((s) => s.id);

const missing = qs.filter((id) => !ids.includes(id));
const extra = ids.filter((id) => !qs.includes(id));
const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);

const KINDS = ["m", "t", "h", "note", "nl", "tree", "table"];
const LETTERS = ["A", "B", "C", "D"];
let steps = 0, boxes = 0;
const odd = [];
for (const s of SOLUTIONS) {
  for (const b of s.boxes || []) {
    boxes++;
    for (const st of b.steps || []) {
      steps++;
      const kinds = KINDS.filter((k) => st[k] != null);
      if (kinds.length !== 1) odd.push(`${s.id}: ${JSON.stringify(st).slice(0, 60)}`);
    }
  }
  if (s.letter != null && !LETTERS.includes(s.letter)) odd.push(`${s.id}: bad letter ${s.letter}`);
}

const mc = SOLUTIONS.filter((s) => s.letter).map((s) => `${s.id}=${s.letter}`);
console.log(`questions ${qs.length}, solutions ${SOLUTIONS.length}, boxes ${boxes}, steps ${steps}`);
console.log(`mc letters: ${mc.join(" ")}`);
console.log(`missing: ${missing.length ? missing.join(",") : "none"}`);
console.log(`extra: ${extra.length ? extra.join(",") : "none"}`);
console.log(`duplicate ids: ${dupes.length ? dupes.join(",") : "none"}`);
console.log(`odd steps: ${odd.length ? odd.join(" | ") : "none"}`);
console.log(odd.length || missing.length || extra.length || dupes.length ? "FAIL" : "PASS");
