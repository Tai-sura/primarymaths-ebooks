import io
import json
import subprocess

import numpy as np
from PIL import Image
from scipy.ndimage import minimum_filter

BOOK = "p5m07a"


def git_show(path):
    return subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=True).stdout


layout = json.loads(open(f"books/{BOOK}/layout.json", encoding="utf-8").read())
page_img = {}
red_tot_old = red_tot_new = 0
black_removed = black_removed_on_page = 0
red_changed = []
black_removed_off_page = []
rows = []

for p in layout["pages"]:
    img = Image.open(f"books/{BOOK}/pages/p{p['page']:02d}.jpg").convert("L")
    page_img[p["page"]] = img
    for q in p["questions"]:
        for s in q.get("stamps") or []:
            name = s["img"].split("/")[-1]
            try:
                old = Image.open(io.BytesIO(git_show(f"books/{BOOK}/answers/{name}"))).convert("RGBA")
            except subprocess.CalledProcessError:
                continue
            new = Image.open(f"books/{BOOK}/answers/{name}").convert("RGBA")
            if old.size != new.size:
                rows.append((name, "SIZE", old.size, new.size))
                continue
            a = np.asarray(old).astype("int32")
            b = np.asarray(new).astype("int32")
            red_a = (a[..., 0] > 140) & (a[..., 1] < 120) & (a[..., 2] < 120)
            red_b = (b[..., 0] > 140) & (b[..., 1] < 120) & (b[..., 2] < 120)
            ra, rb = int(red_a.sum()), int(red_b.sum())
            red_tot_old += ra
            red_tot_new += rb
            if ra != rb:
                red_changed.append((name, ra, rb))
            dark_a = (a[..., 3] > 0) & ~red_a
            dark_b = (b[..., 3] > 0) & ~red_b
            removed = dark_a & ~dark_b
            n_removed = int(removed.sum())
            if n_removed:
                r = s["rect"]
                x0, y0 = int(round(r[0] * 3)), int(round(r[1] * 3))
                crop = np.asarray(page_img[p["page"]].crop(
                    (x0, y0, x0 + new.size[0], y0 + new.size[1]))).astype("int16")
                if crop.shape == removed.shape:
                    near = minimum_filter(crop, size=7) < 210
                    on_page = int((removed & near).sum())
                    black_removed += n_removed
                    black_removed_on_page += on_page
                    if on_page < n_removed:
                        black_removed_off_page.append((name, n_removed - on_page))
            rows.append((name, q["id"], ra, rb, n_removed))

print("stamps compared:", len(rows))
print("red ink px  old", red_tot_old, "new", red_tot_new, "->", "IDENTICAL" if red_tot_old == red_tot_new else "CHANGED")
print("red changed per stamp:", red_changed or "none")
print("black px removed:", black_removed, "of which on page ink:", black_removed_on_page,
      f"({0 if not black_removed else round(black_removed_on_page / black_removed * 100, 1)}%)")
print("black removed where the page was blank (would be a lost answer):", black_removed_off_page or "none")
for name, qid, ra, rb, rem in rows:
    if rem and (qid in ("hw1", "hw3", "hw5", "hw6", "hw7", "hw8", "hw10", "q5", "q6", "q7")):
        print(f"  {name:14s} {qid:5s} red {ra}->{rb}  black removed {rem}")
