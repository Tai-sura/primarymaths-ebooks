"""Paste a book's hand-drawn panels back onto its page images.

`extract_pages.py` re-renders every page from the source PDF, which wipes any panel that was drawn
on top of a page by hand. A book records those panels in `books/<id>/panels.json`, and this script
puts them back; `extract_pages.py` calls it at the end, so "extract then re-paste" is one step.

    python tools/paste_panels.py <book-id>

    {
      "panels": [
        {"page": 5, "png": "panels/p05-diagram.png", "box": [296, 244, 584, 336],
         "clear": [[206, 244, 510, 584]]}
      ]
    }

`box` is [x0, y0, x1, y1] in page points: the PNG's top-left corner goes there and the PNG must be
exactly 3 x its size, or the run fails. Each `clear` entry is [y0, y1, x0, x1] and is filled white
before the paste, for parts of the old figure that reach outside the panel (a character's head, a
drawn cloud). The JPEG save options match the rest of the pipeline, so a re-paste of an unchanged
panel reproduces the previous page byte for byte.

ORDER MATTERS: this must run AFTER `tools/qa/stamp_folio.py`, which is why `extract_pages.py`
calls it last. `stamp_folio` re-saves a page at quality 95, so if it ran after a panel had been
pasted the page would be encoded a second time and the labels would drift (measured: max 26 per
channel against the approved p5 page, where the same paste onto the stamped page reproduces it byte
for byte). Keep folio first, panels last.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ZOOM = 3.0
SAVE = {"quality": 97, "progressive": True, "subsampling": 0, "optimize": True}


def paste_one(folder, item):
    page_no = int(item["page"])
    png = folder / item["png"]
    x0, y0, x1, y1 = [float(v) for v in item["box"]]
    if not png.exists():
        sys.exit(f"missing panel image {png}")
    panel = Image.open(png).convert("RGB")
    want = (round((x1 - x0) * ZOOM), round((y1 - y0) * ZOOM))
    if panel.size != want:
        sys.exit(f"{png.name}: {panel.size[0]}x{panel.size[1]} but box needs {want[0]}x{want[1]} (3x)")

    page = folder / "pages" / f"p{page_no:02d}.jpg"
    if not page.exists():
        sys.exit(f"missing page image {page}; run tools/extract_pages.py first")

    im = Image.open(page).convert("RGB")
    draw = ImageDraw.Draw(im)
    for clear in item.get("clear", []):
        cy0, cy1, cx0, cx1 = [float(v) for v in clear]
        draw.rectangle(
            (round(cx0 * ZOOM), round(cy0 * ZOOM), round(cx1 * ZOOM) - 1, round(cy1 * ZOOM) - 1),
            fill=(255, 255, 255),
        )
    im.paste(panel, (round(x0 * ZOOM), round(y0 * ZOOM)))
    im.save(page, **SAVE)
    print(
        f"  page {page_no}: pasted {png.name} at ({x0:g}, {y0:g}) {x1 - x0:g}x{y1 - y0:g} pt, "
        f"cleared {len(item.get('clear', []))} band(s), {page.stat().st_size} B"
    )


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python tools/paste_panels.py <book-id>")
    book = sys.argv[1]
    folder = ROOT / "books" / book
    cfg = folder / "panels.json"
    if not cfg.exists():
        sys.exit(f"no {cfg}")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    items = data.get("panels", data if isinstance(data, list) else [])
    print(f"{book}: {len(items)} panel(s) from {cfg.name}")
    for item in items:
        paste_one(folder, item)


if __name__ == "__main__":
    main()
