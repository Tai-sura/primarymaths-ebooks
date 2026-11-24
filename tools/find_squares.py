# -*- coding: utf-8 -*-
"""Find the printed MC answer squares (small ~28pt rectangles at the right margin)."""
import json, sys, io, pathlib
import fitz

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

root = pathlib.Path(__file__).resolve().parents[1]
bk = root / "books" / "phy11"
book = json.loads((bk / "book.json").read_text(encoding="utf-8"))
doc = fitz.open(bk / book["source"]["que"])

for pno in range(len(doc)):
    page = doc[pno]
    found = []
    for d in page.get_drawings():
        r = d["rect"]
        w, h = r.width, r.height
        if 20 <= w <= 34 and 20 <= h <= 34 and abs(w - h) <= 4 and r.x0 > 480:
            found.append((round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)))
    if found:
        print(f"page {pno + 1}: {len(found)} squares")
        for f in found:
            print("   ", f)
doc.close()
