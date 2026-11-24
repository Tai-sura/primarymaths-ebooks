"""Geometric clearing check for the jpfm08 p1 film's amber marks.

For every amber frame or tint the scene draws, measure on pages/p01.jpg the distance
from the mark's outline to the nearest printed ink pixel anywhere in the crop. A frame
stroke is 1.2 pt wide (3.6 px at 3 px/pt) so it needs half of that clear; the film's
rule for a frame round printed words is >= 2 pt (6 px) between the stroke and the ink.

Outlines are rounded rectangles: the shape is the Minkowski sum of its inner rectangle
(inset by the corner radius) and a disc, so the distance to the outline is
|signed distance to the inner rectangle - radius|.

This check is what caught the first cell-2 label frame (right edge 377.2 pt) cutting
the last "m" of "moment arm", whose ink really ends at 378.33 pt: it was measured in a
window that stopped at 375, so the box came out short. Always measure words with a
window well past the word.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "manim"))
import jpfm08  # noqa: E402

REGION = jpfm08.PageFilm.REGION
page = Image.open(ROOT / "books" / "jpfm08" / "pages" / "p01.jpg").convert("RGB")
s = page.width / 595.32
crop = page.crop((round(REGION[0] * s), round(REGION[1] * s), round(REGION[2] * s), round(REGION[3] * s)))
a = np.asarray(crop).astype(int)
g = a.mean(axis=2)
mx, mn = a.max(axis=2), a.min(axis=2)
ink = (g < 150) & ((mx - mn) < 70)          # grey/black print; the red force is not a frame target
pts = np.stack(np.nonzero(ink), axis=1)     # (y, x) in crop px


def sdf_rect(x, y, x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    qx, qy = np.abs(x - cx) - hx, np.abs(y - cy) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


def dist_to_mark(x, y, box, radius_pt):
    x0, y0, x1, y1 = [(v - (REGION[0] if i % 2 == 0 else REGION[1])) * s for i, v in enumerate(box)]
    r = radius_pt * s
    return np.abs(sdf_rect(x, y, x0 + r, y0 + r, x1 - r, y1 - r) - r)


marks = {
    "cell1 right-angle tint (fill)": (jpfm08.MARK_BOX, 1.3, "fill"),
    "cell1 = Fd frame": (jpfm08.FD_1, 1.3, "stroke"),
    "cell2 label frame": (jpfm08.LAB_2, 6.0, "stroke"),
    "cell2 = Fd sin th frame": (jpfm08.FD_2, 1.3, "stroke"),
    "cell3 label frame": (jpfm08.LAB_3, 1.3, "stroke"),
    "cell3 = 0 frame": (jpfm08.FD_3, 1.3, "stroke"),
}

print("mark                            kind    nearest ink      at page pt")
worst = {}
for name, (box, radius, kind) in marks.items():
    bx0 = (box[0] - REGION[0]) * s
    by0 = (box[1] - REGION[1]) * s
    bx1 = (box[2] - REGION[0]) * s
    by1 = (box[3] - REGION[1]) * s
    near = pts[(pts[:, 1] >= bx0 - 12) & (pts[:, 1] <= bx1 + 12) & (pts[:, 0] >= by0 - 12) & (pts[:, 0] <= by1 + 12)]
    d = dist_to_mark(near[:, 1].astype(float), near[:, 0].astype(float), box, radius)
    k = int(np.argmin(d))
    py, px = near[k]
    print(f"{name:30s} {kind:6s} {d[k]:5.1f} px / {d[k] / s:4.1f} pt   (x {REGION[0] + px / s:.2f}, y {REGION[1] + py / s:.2f})")
    worst[name] = d[k]

half_stroke = 1.2 * s / 2                    # 1.8 px
fill_min = min(v for n, v in worst.items() if marks[n][2] == "fill")
stroke_min = min(v for n, v in worst.items() if marks[n][2] == "stroke")
print(f"\nfill tint: nearest ink {fill_min:.1f} px (needs > 0, no stroke to cut anything)")
print(f"stroked frames: nearest ink {stroke_min:.1f} px = {stroke_min / s:.2f} pt; stroke half-width {half_stroke:.1f} px"
      f" -> clearance from the stroke edge {stroke_min - half_stroke:.1f} px")
print("PASS" if stroke_min > half_stroke + 2 and fill_min > 0 else "FAIL")
