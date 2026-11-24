"""Cut the teacher's red answers out of the ANS pages, to show them in place.

For a fill-in book the answer *is* the red mark on the ANS page: a word in a red
box, a number, or a circle round the choice. Rather than typeset the answer in a
card, this copies the red marks of each question - exactly as the teacher's key
prints them - and records where they belong in `layout.json`:

    "stamps": [{ "img": "answers/p03_q01.png", "rect": [x0, y0, x1, y1] }]

The reader draws each stamp over the page at `rect` (page points), so the answer
appears in its own blank, with the teacher's red box, and never a word of
explanation.

    python -X utf8 tools/answer_stamps.py <book-id>

Only questions in `book.json` "answerStamps" get a stamp; MC and long questions
keep their in-page working. Run it after `extract_pages.py` (it rewrites the
layout), or let `extract_pages.py` call it, which it does when the list exists.

A scan can put a red answer where the automatic band rule cannot tell it apart
from the picture beside it. Pin those few by hand in `book.json`:

    "stampOverride": { "hw4": [128, 250, 250, 268] }

(the box in PDF points; the crop is that box plus the usual 2 pt margin).
"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3          # same as the page images
MARGIN = 2.0       # points of white kept round the red marks
GROW = 1           # px of dilation: joins a word's thin strokes, not two answers


def red_mask(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 140) & (g < 120) & (b < 120) & (r - g > 50) & (r - b > 50), pix


def red_blobs(mask):
    grown = ndimage.binary_dilation(mask, iterations=GROW) if GROW else mask
    labels, _n = ndimage.label(grown)
    out = []
    for sl in ndimage.find_objects(labels):
        if sl is None:
            continue
        ys, xs = sl
        b = (xs.start / SCALE, ys.start / SCALE, xs.stop / SCALE, ys.stop / SCALE)
        if b[2] - b[0] < 4 or b[3] - b[1] < 4:
            continue
        if mask[sl].sum() < 6:            # a stray dot, not an answer
            continue
        out.append(b)
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = ROOT / "books" / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    wanted = list(book.get("answerStamps") or [])
    if not wanted:
        print(f"{book_id}: no answerStamps list, nothing to do")
        return 0
    wanted = set(wanted)
    pinned = book.get("stampOverride") or {}
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    for page in layout["pages"]:
        for q in page["questions"]:
            q.pop("stamps", None)
    ans = fitz.open(folder / book["source"]["ans"])
    offset = book["source"].get("ansPageOffset", 0)
    out_dir = folder / "answers"
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    made = 0
    for page in layout["pages"]:
        qs = page["questions"]
        live = [q for q in qs if q["id"] in wanted]
        if not live:
            continue
        ans_page = page["page"] + offset
        if not 1 <= ans_page <= ans.page_count:
            print(f"p{page['page']}: no ANS page")
            continue
        mask, pix = red_mask(ans[ans_page - 1])
        blobs = red_blobs(mask) if mask.any() else []
        # The answer sits between its own printed line and the next question; a
        # blob that crosses a band edge (two touching circles) is clipped to each.
        per_q = {}
        for bbox in blobs:
            # The answer belongs to the question whose band holds its centre; a
            # box that starts a little above its line (q2's red box) still lands
            # with q2, not with the question above it.
            cy = (bbox[1] + bbox[3]) / 2
            for idx, q in enumerate(qs):
                start = q["anchor"][0] - 6
                end = (qs[idx + 1]["anchor"][0] - 6) if idx + 1 < len(qs) else page["height"]
                if start <= cy < end:
                    if q["id"] in wanted:
                        per_q.setdefault(q["id"], []).append(bbox)
                    break
        for q in live:
            boxes = per_q.get(q["id"])
            pinned_box = pinned.get(q["id"])
            if pinned_box:
                # One box, or several for a question whose answer is a boxed word
                # plus a construction drawing.
                specs = pinned_box if isinstance(pinned_box[0], list) else [pinned_box]
            elif boxes:
                specs = [[min(b[0] for b in boxes) - MARGIN,
                          min(b[1] for b in boxes) - MARGIN,
                          max(b[2] for b in boxes) + MARGIN,
                          max(b[3] for b in boxes) + MARGIN]]
            else:
                continue
            stamps = []
            for k, spec in enumerate(specs):
                x0, y0, x1, y1 = spec
                if not pinned_box:
                    # A scanned word comes apart into letter-sized blobs: take the
                    # red columns within 12 pt, so no letter is cut off.
                    idx = qs.index(q)
                    b0 = int(round((q["anchor"][0] - 6) * SCALE))
                    b1 = int(round(((qs[idx + 1]["anchor"][0] - 6) if idx + 1 < len(qs) else page["height"]) * SCALE))
                    cols = np.where(mask[b0:b1].any(axis=0))[0]
                    if cols.size:
                        near = cols[(cols >= (x0 - 12) * SCALE) & (cols <= (x1 + 12) * SCALE)]
                        if near.size:
                            x0 = min(x0, near.min() / SCALE)
                            x1 = max(x1, (near.max() + 1) / SCALE)
                x0, y0 = max(0.0, x0), max(0.0, y0)
                x1, y1 = min(page["width"], x1), min(page["height"], y1)
                if x1 - x0 < 2 or y1 - y0 < 2:
                    continue
                box = (int(round(x0 * SCALE)), int(round(y0 * SCALE)), int(round(x1 * SCALE)), int(round(y1 * SCALE)))
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).crop(box)
                name = f"p{page['page']:02d}_{q['id']}{'' if k == 0 else str(k + 1)}.png"
                img.save(out_dir / name, optimize=True)
                stamps.append({"img": f"answers/{name}", "rect": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)]})
            if stamps:
                q["stamps"] = stamps
                made += 1
        print(f"p{page['page']:02d}: {len(blobs)} red marks -> {sum(1 for q in live if q.get('stamps'))} stamps")
    (folder / "layout.json").write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    stamped = [q for p in layout["pages"] for q in p["questions"] if q.get("stamps")]
    missing = sorted(wanted - {q["id"] for q in stamped})
    big = [(q["id"], round(q["stamps"][0]["rect"][3] - q["stamps"][0]["rect"][1], 1), round(q["stamps"][0]["rect"][2] - q["stamps"][0]["rect"][0], 1))
           for q in stamped if (q["stamps"][0]["rect"][3] - q["stamps"][0]["rect"][1] > 40 or q["stamps"][0]["rect"][2] - q["stamps"][0]["rect"][0] > 320)]
    print(f"{book_id}: {made} stamps written to {out_dir}")
    if missing:
        print("no red answer found for:", " ".join(missing))
    if big:
        print("large stamps - check these against the key, pin any that are wrong with stampOverride:")
        for qid, h, w in big:
            print(f"  {qid}: {w} x {h} pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
