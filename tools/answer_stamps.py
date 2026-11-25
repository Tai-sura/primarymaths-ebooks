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


def nudge_plays(layout, folder):
    """Move a Play button that would sit on top of a red answer stamp.

    The stamps are cut from the ANS page after `extract_pages.py` has placed the
    Play buttons, so a button can end up over the printed red answer it opens.
    Here each one is checked against the stamps on its page and, when it clashes,
    nudged along its own line (shrinking if the gap is small) until it clears both
    the stamp and the printed ink.
    """
    moved = 0
    SIZES = ((24, 22), (20, 18), (18, 16), (16, 14), (14, 12), (12, 10))
    for page in layout["pages"]:
        img_path = folder / "pages" / f"p{page['page']:02d}.jpg"
        if not img_path.exists():
            continue
        img = Image.open(img_path).convert("L")
        sx = img.width / page["width"]
        sy = img.height / page["height"]
        rects = [s["rect"] for q in page["questions"] for s in (q.get("stamps") or [])]

        def stamp_clear(x, y, w, h):
            return not any(x < r[2] + 1.5 and r[0] - 1.5 < x + w
                           and y < r[3] + 1.5 and r[1] - 1.5 < y + h for r in rects)

        def ink_clear(x, y, w, h):
            crop = img.crop((int(x * sx), int(y * sy), int((x + w) * sx), int((y + h) * sy)))
            return crop.size[0] and crop.size[1] and crop.getextrema()[0] >= 150

        for q in page["questions"]:
            at = q.get("playAt")
            if not q.get("stamps") or not at:
                continue
            w, h = q.get("playSize") or [24, 22]
            if stamp_clear(at[0], at[1], w, h):
                continue
            reg = q["region"]
            right = min(reg[2], page["width"] - 18)
            best = None
            for size in SIZES:
                sw, sh = size
                for dy in (0, -3, 3, -6, 6, -10, 10, -14, 14):
                    for dx in (0, -6, 6, -12, 12, -20, 20, -28, 28, -40, 40, -56, 56, -72, 72):
                        cx, cy = at[0] + dx, at[1] + dy
                        if cx < reg[0] or cx + sw > right or cy < 2 or cy + sh > page["height"] - 2:
                            continue
                        if stamp_clear(cx, cy, sw, sh) and ink_clear(cx, cy, sw, sh):
                            best = (cx, cy, sw, sh)
                            break
                    if best:
                        break
                if best:
                    break
            if best:
                q["playAt"] = [round(best[0], 1), round(best[1], 1)]
                q["playSize"] = [best[2], best[3]]
                # The button now sits at a different point of the same line: record
                # that corner as the line's end so the proximity check stays honest.
                if q.get("blankAt"):
                    q["blankAt"] = [q["blankAt"][0], round(best[1], 1), round(best[0] + best[2], 1)]
                moved += 1
    return moved


def nudge_graphics(layout, folder):
    """Keep the second (amber graphic) button off the red answer and off the Play.

    `extract_pages.py` measures `graphicAt` with the Play box already taken, but the
    stamps are cut after that, and a hand-pinned `playAt` can land the pair badly.
    Here each graphic button is checked against the stamps, the ink and the Play, and
    moved along its line (shrinking if the gap is small) until it clears all three.
    """
    moved = 0
    SIZES = ((24, 22), (22, 20), (20, 18), (18, 16), (16, 14), (14, 12))
    for page in layout["pages"]:
        img_path = folder / "pages" / f"p{page['page']:02d}.jpg"
        if not img_path.exists():
            continue
        img = Image.open(img_path).convert("L")
        sx = img.width / page["width"]
        sy = img.height / page["height"]
        rects = [s["rect"] for q in page["questions"] for s in (q.get("stamps") or [])]
        plays = [(q["playAt"][0], q["playAt"][1],
                  q["playAt"][0] + (q.get("playSize") or [24, 22])[0],
                  q["playAt"][1] + (q.get("playSize") or [24, 22])[1])
                 for q in page["questions"] if q.get("playAt")]
        placed = []

        def stamp_clear(x, y, w, h):
            return not any(x < r[2] + 1.5 and r[0] - 1.5 < x + w
                           and y < r[3] + 1.5 and r[1] - 1.5 < y + h for r in rects)

        def ink_clear(x, y, w, h):
            crop = img.crop((int(x * sx), int(y * sy), int((x + w) * sx), int((y + h) * sy)))
            return crop.size[0] and crop.size[1] and crop.getextrema()[0] >= 150

        for q in page["questions"]:
            at = q.get("graphicAt")
            if not at:
                continue
            pw, ps = q.get("playAt"), q.get("playSize") or [24, 22]
            w, h = q.get("graphicSize") or ps

            def others_clear(x, y, ww, hh):
                # Clear of every Play on the page and of the graphic buttons already
                # placed: two graphics on neighbouring lines must not share a box.
                for (a, b, c, d) in plays + placed:
                    if x < c + 3 and a < x + ww + 3 and y < d + 3 and b < y + hh + 3:
                        return False
                return True

            if stamp_clear(at[0], at[1], w, h) and others_clear(at[0], at[1], w, h) \
                    and ink_clear(at[0], at[1], w, h):
                placed.append((at[0], at[1], at[0] + w, at[1] + h))
                continue
            best = None
            for size in SIZES:
                sw, sh = size
                for dy in (0, -3, 3, -6, 6, -10, 10, -14, 14, -20, 20, -26, 26):
                    for dx in (0, -6, 6, -12, 12, -20, 20, -28, 28, -40, 40, -56, 56, -72, 72, -100, 100):
                        cx, cy = at[0] + dx, at[1] + dy
                        if cx < 2 or cx + sw > page["width"] - 18 or cy < 2 or cy + sh > page["height"] - 2:
                            continue
                        if stamp_clear(cx, cy, sw, sh) and others_clear(cx, cy, sw, sh) \
                                and ink_clear(cx, cy, sw, sh):
                            best = (cx, cy, sw, sh)
                            break
                    if best:
                        break
                if best:
                    break
            if best:
                q["graphicAt"] = [round(best[0], 1), round(best[1], 1)]
                q["graphicSize"] = [best[2], best[3]]
                placed.append((best[0], best[1], best[0] + best[2], best[1] + best[3]))
                moved += 1
            else:
                placed.append((at[0], at[1], at[0] + w, at[1] + h))
    return moved


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
        # The printed page under the stamp: ink that the page already shows must not
        # be drawn a second time by the stamp (a table's "cm", a figure's arc). The
        # answer itself sits on white paper in the QUE page, so it survives.
        page_img = None
        for cand in (folder / "pages" / f"p{page['page']:02d}.jpg",):
            if cand.exists():
                page_img = Image.open(cand).convert("L")
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
                # Keep the red ink only: the crop is a rectangle round the answer, so
                # it also holds black print (the cell's "cm", a rule, a figure). An
                # opaque rectangle would paint over that print, and a plain white
                # cut-out would draw it twice, so alpha follows how red a pixel is.
                arr = np.asarray(img).astype("int32")
                # The answer on the ANS page is often the teacher's red box round a
                # printed word ("AD", "CF", "diameters"), so the black ink inside the
                # crop belongs to the answer: keep every inked pixel (dark or red) and
                # let only the white paper go transparent. A white rectangle would
                # paint over the table rule or figure that runs under the answer.
                lum = (arr[:, :, 0] * 299 + arr[:, :, 1] * 587 + arr[:, :, 2] * 114) // 1000
                red = arr[:, :, 0] - (arr[:, :, 1] + arr[:, :, 2]) // 2
                ink = np.minimum(lum, 255 - np.clip(red, 0, 255) // 2)
                alpha = np.clip((205 - ink) * 255 // 30, 0, 255).astype("uint8")
                # Drop what the printed page already carries: the crop is a rectangle
                # round the answer, so it can hold the cell's "cm", a table rule or a
                # figure's arc, and drawing those again doubles the print. The ANS scan
                # sits a few points off the QUE one, so the two are aligned first - a
                # fixed window big enough for the shift would eat a real answer word.
                if page_img is not None:
                    pq = page_img.crop(box)
                    parr = np.asarray(pq).astype("int16")
                    if parr.shape[:2] == alpha.shape:
                        from scipy.ndimage import minimum_filter
                        stamp_dark = ink < 170
                        best = (-1, 0, 0)
                        for dy in range(-12, 13, 2):
                            for dx in range(-12, 13, 2):
                                rolled = np.roll(np.roll(parr, dy, axis=0), dx, axis=1)
                                hit = int((stamp_dark & (rolled < 200)).sum())
                                if hit > best[0]:
                                    best = (hit, dy, dx)
                        _, dy, dx = best
                        parr = np.roll(np.roll(parr, dy, axis=0), dx, axis=1)
                        pmin = minimum_filter(parr, size=5)
                        alpha[(red <= 12) & (pmin < 200)] = 0
                img = img.convert("RGBA")
                img.putalpha(Image.fromarray(alpha))
                name = f"p{page['page']:02d}_{q['id']}{'' if k == 0 else str(k + 1)}.png"
                img.save(out_dir / name, optimize=True)
                stamps.append({"img": f"answers/{name}", "rect": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)]})
            if stamps:
                q["stamps"] = stamps
                made += 1
        print(f"p{page['page']:02d}: {len(blobs)} red marks -> {sum(1 for q in live if q.get('stamps'))} stamps")
    nudged = nudge_plays(layout, folder)
    gmoved = nudge_graphics(layout, folder)
    (folder / "layout.json").write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if nudged:
        print(f"{nudged} Play button(s) moved off a red answer stamp")
    if gmoved:
        print(f"{gmoved} graphic button(s) moved clear of the stamp and the Play")
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
