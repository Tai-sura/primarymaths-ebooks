from PIL import Image
import numpy as np
img = Image.open("books/p5m07a/pages/p11.jpg").convert("L")
a = np.array(img)
h, w = a.shape
scale = h / 841.92
rows = []
for y in range(int(250*scale), int(830*scale)):
    line = a[y, int(60*scale):int(546*scale)]
    dark = (line < 140).mean()
    if dark > 0.6:
        rows.append(round(y/scale, 1))
# group consecutive
groups = []
for y in rows:
    if groups and y - groups[-1][-1] < 2:
        groups[-1].append(y)
    else:
        groups.append([y])
print("ruled lines at pt:", [round(sum(g)/len(g),1) for g in groups])
