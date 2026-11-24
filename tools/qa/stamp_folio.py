"""Stamp the hand-placed page numbers back onto a book's page images, and hide the printed
ones that must not show.

`tools/extract_pages.py` renders `pages/pNN.jpg` straight from the PDF every time it runs, so a
page number placed by hand is wiped (the PDF has no ink there -- that is why it was placed by
hand) and a page number the PDF draws in the wrong place comes back. This puts the first back and
whites out the second, and `extract_pages.py` calls it automatically at the end of every run.

What it needs, per book:

    books/<id>/folio.json       {"5": [x0, y0, x1, y1], ...}      the folio's box, in PDF points
                                "_hide": {"5": [[x0, y0, x1, y1]]} boxes to white out on that page
    books/<id>/folio/pNN.png    the folio image itself, at the page's 3x scale

`check_folio.py` measures the stamped box afterwards, so a run that fails to stamp is caught.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
Z = 3              # page images are rendered at 3x
QUALITY = 95


def stamp(book_id, verbose=True):
    folder = BOOKS / book_id
    spec_path = folder / "folio.json"
    if not spec_path.exists():
        return 0
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    hide = spec.get("_hide", {})
    pages = {k for k in spec if k not in ("_hide", "_skip")} | set(hide)
    done = 0
    for page in sorted(pages, key=lambda p: int(p)):
        page_jpg = folder / "pages" / f"p{int(page):02d}.jpg"
        if not page_jpg.exists():
            print(f"  folio p{page}: no page image")
            continue
        img = Image.open(page_jpg).convert("RGB")
        changed = False
        for (x0, y0, x1, y1) in hide.get(page, []):
            img.paste((255, 255, 255),
                      (int(x0 * Z), int(y0 * Z), int(x1 * Z) + 1, int(y1 * Z) + 1))
            changed = True
            if verbose:
                print(f"  folio p{page}: hid the printed mark at ({x0}, {y0})-({x1}, {y1})")
        if page in spec and page != "_hide":
            png = folder / "folio" / f"p{int(page):02d}.png"
            if png.exists():
                glyph = Image.open(png).convert("RGB")
                x0, y0, _x1, _y1 = spec[page]
                img.paste(glyph, (int(x0 * Z), int(y0 * Z)))
                changed = True
                done += 1
                if verbose:
                    print(f"  folio p{page}: stamped {glyph.size[0]}x{glyph.size[1]} px at ({x0}, {y0}) pt")
            else:
                print(f"  folio p{page}: missing {png}")
        if changed:
            img.save(page_jpg, quality=QUALITY, subsampling=0)
    return done


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    n = stamp(sys.argv[1])
    print(f"stamped {n} page number(s)")


if __name__ == "__main__":
    main()
