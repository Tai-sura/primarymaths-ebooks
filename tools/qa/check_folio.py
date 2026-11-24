"""Check that the printed page number of every page is really visible on the page image.

The PDF text layer can carry a page number that the rendered page never shows: it can sit
under a figure, under a white box, or be missing from the overlay the book was rendered from.
Reading the text layer is not enough -- this measures ink in `pages/pNN.jpg` inside the
folio's text-layer bbox.

    python tools/qa/check_folio.py <book-id> [--verbose]

Exit code 0 = every page's folio has ink, 1 = at least one page is missing it.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
INK = 170          # grayscale below this counts as ink (same threshold as the other QA tools)
INK_MIN = 20       # a real 2-digit folio at zoom 3 has 90-320 ink px; 20 is a safe floor
RING_MIN = 15      # ring ink below this is JPEG noise from a nearby mark, not a stroke crossing the box
PAD = 2.0          # pt of slack around the text-layer bbox


def load(book_id):
    folder = BOOKS / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    # books/<id>/folio.json records page numbers that had to be placed by hand, because the
    # rendered page did not show them where the PDF text layer says they are.
    placed = {}
    f = folder / "folio.json"
    if f.exists():
        placed = json.loads(f.read_text(encoding="utf-8"))
    return folder, book, layout, placed


def folio_word(page, footer, expected):
    """The right-most number-like word in the footer band of this page's text layer."""
    band = []
    for line in page.get("text", []):
        y0 = line[0]
        if y0 < footer - 60:      # books differ: some folios sit above the footer rule, some below
            continue
        for x0, x1, text in line[2]:
            t = text.strip()
            if t and all(ch.isdigit() for ch in t):
                band.append((x0, x1, line[0], line[1], t))
    if not band:
        return None
    band.sort(key=lambda w: w[1])
    exact = [w for w in band if w[4] == str(expected)]
    return exact[-1] if exact else band[-1]


def measure(img, bbox, zoom):
    """Ink inside the folio's text-layer box, and ink in a 2 px ring just outside it.

    A clean page number is the only mark in its own box. Ink in the ring means something
    else (a figure edge, a rule, a neighbour label) runs through that box, so a reader
    cannot be sure the number itself is visible -- that page gets flagged for an eye check.
    """
    x0, y0, x1, y1 = bbox
    ix0, iy0 = int(x0 * zoom), int(y0 * zoom)
    ix1, iy1 = int(x1 * zoom) + 1, int(y1 * zoom) + 1
    crop = img.crop((ix0, iy0, ix1, iy1)).convert("L")
    w, h = crop.size
    px = crop.load()
    inside = sum(1 for yy in range(h) for xx in range(w) if px[xx, yy] < INK)
    ring = 0
    outer = img.crop((ix0 - 2, iy0 - 2, ix1 + 2, iy1 + 2)).convert("L")
    o = outer.load()
    ow, oh = outer.size
    for yy in range(oh):
        for xx in range(ow):
            if o[xx, yy] < INK and not (2 <= xx < ow - 2 and 2 <= yy < oh - 2):
                ring += 1
    return inside, ring


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in sys.argv
    if not args:
        sys.exit(__doc__)
    book_id = args[0]
    folder, book, layout, placed = load(book_id)
    skip = set(placed.get("_skip", []))   # pages deliberately without a folio (cover)
    zoom = book["extract"].get("zoom", 3)
    footer = book["extract"].get("footer", 822)

    rows, bad, look = [], [], []
    for page in layout["pages"]:
        n = page["page"]
        if n in skip:
            rows.append((n, "skipped (folio.json _skip)", None, None, "SKIP"))
            continue
        img_path = folder / "pages" / f"p{n:02d}.jpg"
        if not img_path.exists():
            rows.append((n, "no page image", None, None, "MISS"))
            bad.append((n, "no page image"))
            continue
        img = Image.open(img_path)
        if str(n) in placed and isinstance(placed[str(n)], list):
            x0, y0, x1, y1 = placed[str(n)]
            ink, ring = measure(img, (x0, y0, x1, y1), zoom)
            state = "ok  " if ink >= INK_MIN and ring < RING_MIN else ("MISS" if ink < INK_MIN else "LOOK")
            what = f"hand-placed at x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f}"
            if state == "MISS":
                bad.append((n, f"hand-placed folio has ink {ink}"))
            elif state == "LOOK":
                look.append((n, f"hand-placed folio ink {ink}, ring {ring}"))
            rows.append((n, what, ink, ring, state))
            continue
        w = folio_word(page, footer, n)
        if w is None:
            rows.append((n, "no folio in text layer", None, None, "MISS"))
            bad.append((n, "no folio in text layer"))
            continue
        x0, x1, y0, y1, text = w
        ink, ring = measure(img, (x0, y0, x1, y1), zoom)
        if ink < INK_MIN:
            state = "MISS"
            bad.append((n, f'ink {ink} for "{text}"'))
        elif ring >= RING_MIN:
            state = "LOOK"
            look.append((n, f'"{text}" ink {ink}, ring {ring}'))
        else:
            state = "ok  "
        rows.append((n, f'"{text}" at x {x0:.1f}-{x1:.1f}, y {y0:.1f}-{y1:.1f}', ink, ring, state))

    print(f"\n{book.get('code', book_id)} page numbers ({book_id})")
    for n, what, ink, ring, state in rows:
        if verbose or state != "ok  ":
            extra = "" if ink is None else f"  ink {ink}, ring {ring}"
            print(f"  {state} p{n:<2} {what}{extra}")
    if look:
        print("  EYE CHECK: " + "; ".join(f"p{n} ({why})" for n, why in look)
              + " -- something else crosses the folio box")
    if bad:
        print("  MISSING / WRONG: " + ", ".join(f"p{n} ({why})" for n, why in bad))
        sys.exit(1)
    if look:
        sys.exit(2)
    print(f"  ok   all {len(rows)} pages show their page number")


if __name__ == "__main__":
    main()
