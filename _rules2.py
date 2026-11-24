from PIL import Image
import numpy as np
img = Image.open("books/p5m07a/pages/p11.jpg").convert("L")
a = np.array(img); h, w = a.shape; scale = h / 841.92
rows = []
for y in range(int(250*scale), int(835*scale)):
    line = a[y, int(60*scale):int(546*scale)]
    dark = (line < 150)
    if dark.mean() > 0.35:
        xs = np.where(dark)[0]
        rows.append((round(y/scale,1), round(60+xs.min()/scale), round(60+xs.max()/scale)))
groups = []
for y, x0, x1 in rows:
    if groups and y - groups[-1][0][-1] < 2:
        groups[-1][0].append(y); groups[-1][1].append(x0); groups[-1][2].append(x1)
    else:
        groups.append(([y],[x0],[x1]))
for g in groups:
    print(round(sum(g[0])/len(g[0]),1), "x", min(g[1]), "-", max(g[2]))
