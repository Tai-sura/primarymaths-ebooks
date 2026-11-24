"""Check that every answer chip of a card book sits on blank paper.

A question whose working opens in a card gets a 15 x 15 pt `?` chip at the
top-right of the printed line that carries its blank: `layout.json` records that
spot as `cardAt` (see `answer_row()` in tools/extract_pages.py). This reads
books/<id>/layout.json and the page images, maps the chip box back onto each page
JPEG and reports the darkest pixel under it: anything below 245 means the chip
sits on printed ink.

    py -3.12 tools/qa/check_answer_chips.py <book-id>

A book with `"answers": "cards"` gives every question a chip; a book with
`"answerCards": [...]` only the listed ones. Exit code 1 when a chip covers ink.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
CHIP_W, CHIP_H = 15.0, 15.0


def card_ids(book):
    if book.get("answers") == "cards":
        return None  # every question
    return set(book.get("answerCards") or [])


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = BOOKS / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    wanted = card_ids(book)
    if wanted == set():
        print(f"{book_id}: no answer cards, nothing to check")
        return
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    bad = 0
    checked = 0
    for page in layout["pages"]:
        img_path = folder / "pages" / f"p{page['page']:02d}.jpg"
        if not img_path.exists():
            print(f"p{page['page']:02d}: no page image")
            bad += 1
            continue
        img = Image.open(img_path).convert("L")
        sx = img.width / page["width"]
        sy = img.height / page["height"]
        for q in page["questions"]:
            if wanted is not None and q["id"] not in wanted:
                continue
            at = q.get("cardAt")
            if not at:
                print(f"FAIL p{page['page']:02d} {q['id']}: no cardAt - re-run extract_pages.py")
                bad += 1
                continue
            left, top = at
            box = (int(left * sx), int(top * sy), int((left + CHIP_W) * sx), int((top + CHIP_H) * sy))
            crop = img.crop(box)
            dark = crop.getextrema()[0] if crop.size[0] and crop.size[1] else 255
            checked += 1
            if dark < 245:
                bad += 1
                print(f"FAIL p{page['page']:02d} {q['id']}: chip covers ink at {at} (darkest {dark})")
    verdict = "PASS" if not bad else f"{bad} chip(s) on ink"
    print(f"{book_id}: {checked} chips, {verdict}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
