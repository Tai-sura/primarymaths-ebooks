"""Everything needed to write a correct brief for one question, in one command.

Written after three briefs were sent from memory and were wrong (spem02 q6's axis, spem02
q36's question, jpfm08 q1's hinge side). Read this output before telling anybody what a
question says.

    python tools/qa/brief.py <book-id> <qid>

It prints, for that question and nothing else:
  1. the printed text, line by line, from the question's own anchor to the next one
  2. the solution entry from solutions.js
  3. the printed figure crop, saved to .tmp2/brief/<book>-<qid>.png
     (look at it: side, axis direction, labels, what is drawn and what is not)
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
OUT = ROOT.parent / ".tmp2" / "brief"
Z = 3


def clean(s):
    return "".join(ch if ord(ch) < 128 else "?" for ch in s)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    bid, qid = sys.argv[1], sys.argv[2]
    folder = BOOKS / bid
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))

    qmap = {q["id"]: q for q in book["extract"]["questions"]}
    if qid not in qmap:
        sys.exit(f"{bid} has no {qid}; it has {sorted(qmap)[:5]} ...")
    page_no = qmap[qid]["page"]
    page = next(p for p in layout["pages"] if p["page"] == page_no)

    order = sorted({q["page"] * 10000 + i: q for i, q in enumerate(qmap.values())}.values(),
                   key=lambda q: qmap[q["id"]]["page"])
    ids_on_page = [q["id"] for q in page.get("questions", [])]
    me = next(q for q in page["questions"] if q["id"] == qid)
    y0 = me["anchor"][1] - 6
    later = [q["anchor"][1] for q in page["questions"] if q["anchor"][1] > me["anchor"][1]]
    y1 = (min(later) - 4) if later else page["height"] - 40

    print(f"\n=== {book.get('code', bid)} {qid}  page {page_no}  (printed y {y0:.1f}..{y1:.1f}) ===\n")
    print("PRINTED TEXT")
    for line in page["text"]:
        if not (y0 - 12 <= line[0] <= y1):
            continue
        s = " ".join(w[2] for w in line[2])
        print(f"  {line[0]:6.1f} | {clean(s)}")

    print("\nSOLUTION (solutions.js)")
    text = (folder / "solutions.js").read_text(encoding="utf-8")
    m = re.search(r'id:\s*"' + re.escape(qid) + r'"', text)
    if not m:
        print("  (no entry)")
    else:
        rest = text[m.start():]
        nxt = re.search(r'\n\s{2}\},|\n\s*// -+ .*\n|id:\s*"', rest[10:])
        seg = rest[: (10 + nxt.start() if nxt else 900)]
        for line in seg.splitlines()[:26]:
            print("  " + clean(line))

    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(folder / "pages" / f"p{page_no:02d}.jpg")
    box = (0, max(0, int(y0 * Z)), img.size[0], min(img.size[1], int((y1 + 40) * Z)))
    crop = img.crop(box)
    out = OUT / f"{bid}-{qid}.png"
    crop.save(out)
    print(f"\nFIGURE CROP -> {out}  ({crop.size[0]}x{crop.size[1]} px)")
    print("Look at it before writing the brief: which side, which axis, how the force points,")
    print("what the printed figure actually contains (and what it does not).")


if __name__ == "__main__":
    main()
