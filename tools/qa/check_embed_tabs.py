"""Every book.json "embeds" tab must sit on blank page pixels.

    python tools/qa/check_embed_tabs.py <book-id>

A tab is 20 x 22 pt. This reads the tab corners from book.json, maps each one
back through the page cuts that answers.js makes (a region's `space` opens room
under its own bottom edge, and everything below slides down), and reports the
darkest pixel of the page image inside the tab. 255 = pure white; anything under
245 means the tab would cover printed ink and must move.

Exit code 1 if a tab is off the page, spans a cut, or lands on ink.
"""
import json
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "books")
SCALE = 3.0          # page images are rendered at 3 px per point
TAB_W, TAB_H = 20.0, 22.0
BLANK = 245

book_id = sys.argv[1] if len(sys.argv) > 1 else ""
if not book_id:
    print("Usage: python tools/qa/check_embed_tabs.py <book-id>")
    sys.exit(2)

root = os.path.join(BOOKS, book_id)
book = json.load(open(os.path.join(root, "book.json"), encoding="utf-8"))
layout = json.load(open(os.path.join(root, "layout.json"), encoding="utf-8"))
pages = {p["page"]: p for p in layout["pages"]}


def cuts(page):
    """(bottom, room) for every region that opens answer space, top to bottom."""
    out = []
    for q in page.get("questions", []):
        room = q.get("space") or 0
        if room:
            out.append((q["region"][3], room))
    return sorted(out)


def offset(page, y):
    """How far a sheet y has slid down from the printed page y."""
    return sum(room for bottom, room in cuts(page) if bottom <= y)


fails = 0
rows = []
for item in book.get("embeds", []):
    n = item["page"]
    if "at" not in item:
        # opened from a question's own graphic button, not from a page tab
        rows.append((n, None, None, f"question button: {item.get('q')}"))
        continue
    x, y = item["at"]
    page = pages.get(n)
    img_path = os.path.join(root, "pages", f"p{n:02d}.jpg")
    if page is None or not os.path.exists(img_path):
        rows.append((n, x, y, "no page/layout/image"))
        fails += 1
        continue
    page_h = page.get("height") or 841.92
    if x < 0 or y < 0 or x + TAB_W > 595.32 or y + TAB_H > page_h + offset(page, page_h):
        rows.append((n, x, y, "off the sheet"))
        fails += 1
        continue
    # a tab that spans a cut has no single image row to sample
    if offset(page, y) != offset(page, y + TAB_H):
        rows.append((n, x, y, "spans a page cut"))
        fails += 1
        continue
    iy = y - offset(page, y)
    im = Image.open(img_path).convert("L")
    box = (round(x * SCALE), round(iy * SCALE), round((x + TAB_W) * SCALE), round((iy + TAB_H) * SCALE))
    crop = im.crop(box)
    dark = min(crop.getdata())
    ok = dark >= BLANK
    if not ok:
        fails += 1
    rows.append((n, x, y, f"image y {iy:.1f} box {box} darkest {dark} {'blank' if ok else 'INK' }"))

print(f"{book_id}: {len(rows)} embed tab(s)")
for n, x, y, note in rows:
    if x is None:
        print(f"  p{n:>2} (question)  {note}")
        continue
    print(f"  p{n:>2} ({x:7.1f},{y:7.1f})  {note}")
print("EMBED TABS PASS" if fails == 0 else f"EMBED TABS FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
