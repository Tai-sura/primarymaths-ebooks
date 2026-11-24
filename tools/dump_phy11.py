# -*- coding: utf-8 -*-
"""Dump each question's printed text from layout.json, in reading order."""
import json, sys, io, pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

bk = pathlib.Path(__file__).resolve().parents[1] / "books" / "phy11"
layout = json.loads((bk / "layout.json").read_text(encoding="utf-8"))

# flatten questions in page order
qs = []
for pg in layout["pages"]:
    for q in pg.get("questions", []):
        q = dict(q)
        q["_pg"] = pg["page"]
        q["_text"] = pg.get("text", [])
        qs.append(q)

for i, q in enumerate(qs):
    y0 = q["anchor"][0] - 4
    # stop at next question on the same page, else page footer
    y1 = 790
    for r in qs[i + 1:]:
        if r["_pg"] == q["_pg"]:
            y1 = r["anchor"][0] - 4
            break
    print("=" * 78)
    print(f"{q['id']}  page {q['_pg']}  anchor y={q['anchor'][0]:.1f}  region={q['region']}")
    for row in q["_text"]:
        ry0, ry1, words = row[0], row[1], row[2]
        if ry1 < y0 or ry0 > y1:
            continue
        line = ""
        for x0, x1, w in words:
            if x0 < 60 and line == "":
                pass
            line += w + " "
        print(f"  [{ry0:6.1f}] {line.strip()}")
