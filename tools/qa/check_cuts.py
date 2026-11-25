"""Check that every answer cut line runs through blank paper, end to end.

An inline answer opens the page: the reader slices the page image across its
whole width at the answer region's bottom edge (`region[3]`) and inserts the
space the working needs (engine/viewer/answers.js, growSheet). Any printed mark
that crosses that row - a figure, a ruled answer line, a small answer box on the
far right - is cut in two and the reader sees a torn figure or a box with a gap.

This samples the page JPEG along the full width at each cut line and fails when
anything darker than 245 sits there. Stamped answers never cut the page, so
questions with no `space` are skipped.

    py -3.12 tools/qa/check_cuts.py <book-id>

Exit code 1 when a cut line crosses printed ink.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
HALF_BAND_PT = 1.5
INK = 245


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = BOOKS / book_id
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    bad = 0
    checked = 0
    for page in layout["pages"]:
        img_path = folder / "pages" / f"p{page['page']:02d}.jpg"
        if not img_path.exists():
            print(f"FAIL p{page['page']:02d}: no page image")
            bad += 1
            continue
        img = Image.open(img_path).convert("L")
        sy = img.height / page["height"]
        for q in page["questions"]:
            # A stamped answer never cuts the page: the engine sets its space to 0
            # and shows the teacher's mark in place (see answers.js, stamp branch).
            if q.get("stamps"):
                continue
            if not (q.get("space") or 0) > 0:
                continue
            y = q["region"][3]
            crop = img.crop((0, int((y - HALF_BAND_PT) * sy), img.width, int((y + HALF_BAND_PT) * sy)))
            dark = crop.getextrema()[0] if crop.size[0] and crop.size[1] else 255
            checked += 1
            if dark < INK:
                bad += 1
                print(f"FAIL p{page['page']:02d} {q['id']}: cut at y={y:.1f} crosses ink (darkest {dark})")
    verdict = "PASS" if not bad else f"{bad} cut line(s) across printed ink"
    print(f"{book_id}: {checked} cut line(s), {verdict}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
