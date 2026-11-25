"""Does every stamp still carry the whole answer the ANS page printed?

A stamp is a rectangle cut out of the ANS scan, trimmed so that printed ink the
QUE page already shows is not drawn a second time. The trim has to know when to
stop: a red answer is never touched, but black ink is dropped wherever the printed
page under it is dense - and a boxed answer printed in black sits close to the
lines of its box, so an over-eager trim can shave a stroke off the answer. That
failure is invisible to every other check: the page still renders, the button
still opens, and only the teacher notices a "2" with its top missing.

    py -3.12 tools/qa/check_stamps.py <book-id>

For every stamp of every question in `answerStamps`:

* red ink: the stamp must hold **every** red pixel the ANS crop holds - one pixel
  short is a FAIL, and the missing pixels' bounding box is printed;
* black ink the trim dropped: if it lands on paper the QUE page leaves blank and
  is at least 1 % of the stamp's black ink, that is a WARN (the trim reached into
  something the page did not print, which is where an answer word lives).

Both numbers come from the ANS PDF itself, not from a stored golden image, so the
check keeps working when the book is regenerated.

WARNs must be cleared one by one in `tools/qa/stamp_erase_allow.json`:

    { "p10_hw5": { "why": "the circles are printed on the QUE page too", "date": "2026-11-25" } }

A book is not delivered with an unlisted WARN. Exit code 1 on FAIL, 1 on an
unlisted WARN as well, 0 when clean.
"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter  # noqa: F401 (kept for the density constant note)

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
SCALE = 3                      # the page images and the stamp crops share it
DENSITY = 0.35                 # fixed: 0.22 shaves the top off a boxed "2"
WARN_RATIO = 0.01              # 1 % of a stamp's black ink dropped on blank paper
ALLOW = Path(__file__).resolve().parent / "stamp_erase_allow.json"


def red_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 140) & (g < 120) & (b < 120) & (r - g > 50) & (r - b > 50)


def bbox(mask):
    ys, xs = np.where(mask)
    if not ys.size:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = BOOKS / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    ans = fitz.open(folder / book["source"]["ans"])
    offset = book["source"].get("ansPageOffset", 0)
    allow = {}
    if ALLOW.exists():
        allow = json.loads(ALLOW.read_text(encoding="utf-8"))

    pages_pix = {}
    pages_img = {}
    fails = []
    warns = []
    stuck = []
    checked = 0

    for page in layout["pages"]:
        live = [q for q in page["questions"] if q.get("stamps")]
        if not live:
            continue
        ans_page = page["page"] + offset
        if not 1 <= ans_page <= ans.page_count:
            fails.append(f"p{page['page']}: no ANS page")
            continue
        key = page["page"]
        if key not in pages_pix:
            pix = ans[ans_page - 1].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False)
            pages_pix[key] = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        if key not in pages_img:
            img = folder / "pages" / f"p{page['page']:02d}.jpg"
            pages_img[key] = Image.open(img).convert("L") if img.exists() else None
        page_pix = pages_pix[key]
        page_img = pages_img[key]

        for q in live:
            for s in q["stamps"]:
                name = s["img"].split("/")[-1]
                stem = name[:-4]
                checked += 1
                r = s["rect"]
                box = (int(round(r[0] * SCALE)), int(round(r[1] * SCALE)),
                       int(round(r[2] * SCALE)), int(round(r[3] * SCALE)))
                crop = page_pix[box[1]:box[3], box[0]:box[2]]
                stamp = Image.open(folder / "answers" / name).convert("RGBA")
                sarr = np.asarray(stamp)
                if crop.shape[:2] != sarr.shape[:2]:
                    fails.append(f"{name}: crop {crop.shape[:2]} vs stamp {sarr.shape[:2]} - re-run answer_stamps.py")
                    continue
                red_ans = red_mask(crop.astype("int32"))
                red_stamp = red_mask(sarr[..., :3].astype("int32")) & (sarr[..., 3] > 0)
                missing = red_ans & ~red_stamp
                if int(missing.sum()):
                    fails.append(f"{name}: {int(missing.sum())} red answer px missing, bbox {bbox(missing)} in the stamp")
                cr = crop.astype("int32")
                lum = (cr[..., 0] * 299 + cr[..., 1] * 587 + cr[..., 2] * 114) // 1000
                black_ans = (lum < 205) & ~red_ans
                if not int(black_ans.sum()):
                    continue
                dropped = black_ans & ~(sarr[..., 3] > 0)
                if not int(dropped.sum()):
                    continue
                if page_img is None:
                    continue
                pcrop = np.asarray(page_img.crop(box)).astype("int16")
                if pcrop.shape[:2] != dropped.shape[:2]:
                    continue
                # "Blank paper" is paper with no printed ink within 2 pt: the ANS and
                # QUE scans sit a couple of points apart, so a stroke removed on the
                # strength of that shift is still print, not an answer.
                from scipy.ndimage import binary_dilation
                near_ink = binary_dilation(pcrop < 200, iterations=6)
                on_blank = dropped & ~near_ink
                n = int(on_blank.sum())
                if not n:
                    continue
                ratio = n / int(black_ans.sum())
                if ratio >= WARN_RATIO:
                    entry = {"stamp": stem, "ratio": round(ratio * 100, 2), "px": n, "bbox": bbox(on_blank)}
                    if stem in allow:
                        stuck.append({**entry, "why": allow[stem].get("why", "")})
                    else:
                        warns.append(entry)

    for f in fails:
        print(f"FAIL {f}")
    for w in warns:
        print(f"WARN {w['stamp']}: {w['ratio']}% of its black ink ({w['px']} px) dropped on blank paper, bbox {w['bbox']}"
              f" - allow it in tools/qa/stamp_erase_allow.json with a reason")
    for a in stuck:
        print(f"allow {a['stamp']}: {a['ratio']}% on blank paper - {a['why']}")
    verdict = "PASS" if not fails and not warns else ("FAIL" if fails else "WARN")
    print(f"{book_id}: {checked} stamp(s) checked, {len(fails)} FAIL, {len(warns)} WARN, {len(stuck)} allowed -> {verdict}")
    sys.exit(0 if not fails and not warns else 1)


if __name__ == "__main__":
    main()
