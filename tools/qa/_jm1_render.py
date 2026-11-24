"""Render the jpfm08 p1 concept film without touching book.json.

Two passes of tools/manim/jpfm08.py:MomentConcept at 1464x522 (3x of the 488x174 pt
region):
  1. last frame only  -> media/moment-concept-1-poster.png, must equal the printed
     region crop (that is the still the reader shows and the "last frame" acceptance)
  2. the movie        -> media/moment-concept-1.mp4, H.264, no audio

Then measures, and prints (it never edits anything but the two media files):
  * poster / rendered last frame vs the printed region crop
  * decoded first / last video frames vs the crop (h264 is lossy; reported for the
    record, with the best integer shift so a misalignment would show up as dx/dy != 0)
  * the 3 pt (9 px) band along all four edges
  * every printed text box from the PDF layer
  * that the scene creates no Text mobject (no new words, no numbers)
"""
import importlib
import os
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "tools" / "_manim"
OUT = Path(r"C:\Users\surat\.dsh\bot\workspace\.tmp2\jm1")
BOOK = ROOT / "books" / "jpfm08"
NAME = "MomentConcept"
REGION = (64.0, 214.0, 552.0, 388.0)
W, H = 1464, 522

sys.path.insert(0, str(ROOT / "tools" / "manim"))
import textsvg  # noqa: E402

textsvg.install()
from manim import Text, config, tempconfig  # noqa: E402

scene_cls = getattr(importlib.import_module("jpfm08"), NAME)

opts = {
    "pixel_width": W, "pixel_height": H, "frame_height": 8.0, "frame_width": 8.0 * W / H,
    "frame_rate": 30, "media_dir": str(WORK), "disable_caching": True, "verbosity": "WARNING",
    "progress_bar": "none", "background_color": "#ffffff", "format": "mp4",
}

OUT.mkdir(parents=True, exist_ok=True)
media = BOOK / "media"
media.mkdir(parents=True, exist_ok=True)
video = media / "moment-concept-1.mp4"
poster = media / "moment-concept-1-poster.png"

# ---- pass 1: the last frame, which is the poster ----
with tempconfig({**opts, "save_last_frame": True, "write_to_movie": False}):
    scene = scene_cls()
    scene.render()
    still_file = Path(scene.renderer.file_writer.image_file_path)
    length = scene.renderer.time
    texts = sum(1 for m in scene.mobjects if isinstance(m, Text))
print(f"still pass: {length:.2f} s, Text mobjects = {texts}")
shutil.copyfile(still_file, poster)

if "still" in sys.argv:
    pass
else:
    SNAP = OUT / "frames"
    if SNAP.exists():
        shutil.rmtree(SNAP)
    os.environ["JM1_SNAP"] = str(SNAP)
    with tempconfig(opts):
        scene = scene_cls()
        scene.render()
        movie = Path(scene.renderer.file_writer.movie_file_path)
    print(f"movie: {movie}")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess_ok = True  # noqa: F841
    import subprocess
    subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(movie), "-an", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "22", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(video)], check=True)
    print(f"video {video.relative_to(ROOT)} {video.stat().st_size} B")

# ---- reference ----
page = Image.open(BOOK / "pages" / "p01.jpg").convert("RGB")
s = page.width / 595.32
crop = page.crop((round(REGION[0] * s), round(REGION[1] * s), round(REGION[2] * s), round(REGION[3] * s)))
ref = np.asarray(crop).astype(int)
crop.save(OUT / "crop.png")
print("crop", crop.size)


def diff_of(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    assert im.shape == ref.shape, (im.shape, ref.shape)
    return np.abs(im - ref).max(axis=2)


d_poster = diff_of(poster)
print(f"\n[1] poster ({poster.name}, {poster.stat().st_size} B) vs printed crop")
print(f"  max {d_poster.max()}  differing px {(d_poster > 0).sum()}")

band = np.zeros_like(d_poster, dtype=bool)
band[:9, :] = band[-9:, :] = True
band[:, :9] = band[:, -9:] = True
print(f"  changed px in the 3 pt (9 px) border band: {(d_poster[band] > 0).sum()}")

if "still" in sys.argv:
    print("(still pass only: no video, no snapshots)")
    sys.exit(0)

boxes = {
    "Moment about O (1)": (104.66, 338.56, 186.64, 351.84),
    "= Fd": (128.66, 356.56, 151.70, 369.84),
    "Moment about O (2)": (263.69, 337.84, 345.69, 351.12),
    "= Fd sin theta": (275.69, 361.12, 324.52, 374.40),
    "d (cell 1)": (141.50, 236.53, 147.50, 249.81),
    "d (cell 2)": (297.53, 238.09, 303.53, 251.37),
    "Moment about O (3)": (430.27, 338.56, 512.28, 351.84),
    "= 0": (454.27, 356.56, 470.02, 369.84),
    "d sin theta": (327.53, 296.56, 359.34, 309.84),
}
print("\n[2] the nine printed text boxes, checked in the RENDERED frames (font protection is per frame, not per poster)")
if (OUT / "frames").exists():
    snaps = sorted((OUT / "frames").glob("*.png"))
    print(f"  snapshots: {len(snaps)} (one after every play, times {snaps[0].stem}-{snaps[-1].stem} s)")
    targets = [0.75, 2.1, 4.9, 8.6]
    chosen = []
    for t in targets:
        k = min(snaps, key=lambda p: abs(float(p.stem) - t))
        chosen.append((t, k))
    worst_ink = 0
    for name, (x0, y0, x1, y1) in boxes.items():
        c0, r0 = round((x0 - REGION[0]) * s), round((y0 - REGION[1]) * s)
        c1, r1 = round((x1 - REGION[0]) * s), round((y1 - REGION[1]) * s)
        blk = ref[r0:r1, c0:c1]
        glyph = blk.mean(axis=2) < 110              # the ink of the printed word itself
        line = [f"  {name:20s} glyphs {int(glyph.sum()):4d} px"]
        for t, path in chosen:
            fr = np.asarray(Image.open(path).convert("RGB")).astype(int)[r0:r1, c0:c1]
            d = np.abs(fr - blk).max(axis=2)
            inkd = int(d[glyph].max()) if glyph.any() else 0
            worst_ink = max(worst_ink, inkd)
            line.append(f"t={float(path.stem):.2f}: glyph diff {inkd}, box max {int(d.max())}")
        print("  " + " | ".join(line))
    all_ink = 0
    for path in snaps:
        arr = np.asarray(Image.open(path).convert("RGB")).astype(int)
        for (x0, y0, x1, y1) in boxes.values():
            c0, r0 = round((x0 - REGION[0]) * s), round((y0 - REGION[1]) * s)
            c1, r1 = round((x1 - REGION[0]) * s), round((y1 - REGION[1]) * s)
            blk = ref[r0:r1, c0:c1]
            glyph = blk.mean(axis=2) < 110
            if glyph.any():
                all_ink = max(all_ink, int(np.abs(arr[r0:r1, c0:c1] - blk).max(axis=2)[glyph].max()))
    print(f"  ALL {len(snaps)} snapshots, every glyph pixel of the nine boxes: worst diff = {all_ink}")
else:
    print("  no snapshots")

if video.exists():
    import subprocess
    for tag, grab in [("first", ["-i", str(video), "-frames:v", "1"]),
                      ("last", ["-sseof", "-0.2", "-i", str(video), "-frames:v", "1"])]:
        subprocess.run([ffmpeg, "-v", "error", "-y", *grab, "-update", "1", str(OUT / f"frame_{tag}.png")], check=True)
    print("\n[3] decoded video frames vs crop (h264 is lossy: for the record)")
    for tag in ("first", "last"):
        d = diff_of(OUT / f"frame_{tag}.png")
        f = np.asarray(Image.open(OUT / f"frame_{tag}.png").convert("RGB")).astype(int)
        best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                a = ref[max(0, dy):ref.shape[0] + min(0, dy), max(0, dx):ref.shape[1] + min(0, dx)]
                b = f[max(0, -dy):f.shape[0] + min(0, -dy), max(0, -dx):f.shape[1] + min(0, -dx)]
                m = np.abs(a - b).mean()
                if best is None or m < best[0]:
                    best = (m, dx, dy)
        print(f"  {tag}: max {d.max()}  mean|d| {np.abs(f - ref).mean():.3f}  best shift dx,dy = {best[1]},{best[2]}")

print("\n[4] Text( occurrences in the scene source:", (ROOT / "tools" / "manim" / "jpfm08.py").read_text(encoding="utf-8").count("Text("))
print("done")
