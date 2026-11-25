"""Check that every answer chip and Play button of a book sits on blank paper.

A question whose working opens in a card gets a 15 x 15 pt `?` chip at the
top-right of the printed line that carries its blank: `layout.json` records that
spot as `cardAt` (see `answer_row()` in tools/extract_pages.py). A question whose
answer is a stamp gets a 24 x 22 pt Play button recorded as `playAt` (see
`play_spot()` in the same tool; the box must stay in step with `.ans-play` in
engine/styles.css and engine/viewer/answers.js).
This reads books/<id>/layout.json and the page images, maps each box back onto
its page JPEG and reports the darkest pixel under it: anything below 245 means
the control sits on printed ink.

    py -3.12 tools/qa/check_answer_chips.py <book-id>

A book with `"answers": "cards"` gives every question a chip; a book with
`"answerCards": [...]` only the listed ones. Stamped questions are always checked.
Exit code 1 when a control covers ink.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BOOKS = ROOT / "books"
CHIP_W, CHIP_H = 15.0, 15.0
PLAY_W, PLAY_H, PLAY_STEP = 24.0, 22.0, 24.0


def card_ids(book):
    if book.get("answers") == "cards":
        return None  # every question
    return set(book.get("answerCards") or [])


def graphic_ids(folder):
    """Question ids whose widgets.js registers a picture (hasGraphic in answers.js).

    Only those questions get the second, amber button in the stamp branch, so only
    their `graphicAt` box is judged here: the others are measured but never drawn.
    """
    src_path = folder / "widgets.js"
    if not src_path.exists():
        return set()
    src = src_path.read_text(encoding="utf-8")
    return set(re.findall(r"^\s{2}([A-Za-z]\w*)\s*:\s*\(root\)", src, re.M))


def play_box(q):
    """Where answers.js puts the Play button of a stamped answer."""
    if q.get("playAt"):
        w, h = q.get("playSize") or (PLAY_W, PLAY_H)
        return (q["playAt"][0], q["playAt"][1], float(w), float(h))
    at = q["cardAt"]
    return (max(60.0, at[0] - PLAY_STEP), at[1], PLAY_W, PLAY_H)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = BOOKS / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    wanted = card_ids(book)
    layout = json.loads((folder / "layout.json").read_text(encoding="utf-8"))
    bad = 0
    chips = 0
    plays = 0
    graphics = 0
    have_graphic = graphic_ids(folder)
    for page in layout["pages"]:
        img_path = folder / "pages" / f"p{page['page']:02d}.jpg"
        if not img_path.exists():
            print(f"p{page['page']:02d}: no page image")
            bad += 1
            continue
        img = Image.open(img_path).convert("L")
        sx = img.width / page["width"]
        sy = img.height / page["height"]
        boxes = []
        for q in page["questions"]:
            at = q.get("cardAt")
            stamped = bool(q.get("stamps"))
            is_card = wanted is None or q["id"] in wanted
            if not stamped and not is_card:
                continue
            if not at:
                print(f"FAIL p{page['page']:02d} {q['id']}: no cardAt - re-run extract_pages.py")
                bad += 1
                continue
            left, top, w, h = play_box(q) if stamped else (at[0], at[1], CHIP_W, CHIP_H)
            if stamped:
                boxes.append((q["id"], left, top, left + w, top + h))
            box = (int(left * sx), int(top * sy), int((left + w) * sx), int((top + h) * sy))
            crop = img.crop(box)
            dark = crop.getextrema()[0] if crop.size[0] and crop.size[1] else 255
            if stamped:
                plays += 1
                kind = "play"
            else:
                chips += 1
                kind = "chip"
            if dark < 150:
                bad += 1
                print(f"FAIL p{page['page']:02d} {q['id']}: {kind} covers ink at ({left:.1f}, {top:.1f}) (darkest {dark})")
            # The Play belongs beside its own blank: a button parked in the left
            # margin passes the ink test but is useless to the reader. Compare
            # centres, because `blankAt` is the middle of the blank's strip.
            if stamped and q.get("blankAt"):
                ba = q["blankAt"]
                bx, by = ba[0], ba[1]
                cx = left + w / 2
                # Beside the blank, or at the right end of its own answer line
                # (`blankAt[2]` records that end; a line whose blank is followed by
                # printed words has no room at the blank itself).
                dist = abs(cx - bx)
                if len(ba) > 2:
                    dist = min(dist, abs(cx - ba[2]))
                if dist > 70 or abs(top - by) > 46:
                    bad += 1
                    print(f"FAIL p{page['page']:02d} {q['id']}: play is {dist:.0f} pt from its blank/line end, "
                          f"{abs(top - by):.0f} pt below/above it (limit 70 / 46)")
            # The second, amber button of a stamped answer that has a widget: same
            # ink rule, and it must clear both the red answer and the Play.
            if stamped and q["id"] in have_graphic and q.get("graphicAt"):
                gw, gh = q.get("graphicSize") or (q.get("playSize") or (PLAY_W, PLAY_H))
                gx, gy = q["graphicAt"]
                gbox = (int(gx * sx), int(gy * sy), int((gx + gw) * sx), int((gy + gh) * sy))
                gcrop = img.crop(gbox)
                gdark = gcrop.getextrema()[0] if gcrop.size[0] and gcrop.size[1] else 255
                graphics += 1
                if gdark < 150:
                    bad += 1
                    print(f"FAIL p{page['page']:02d} {q['id']}: graphic covers ink at ({gx:.1f}, {gy:.1f}) (darkest {gdark})")
                if gx < left + w and left < gx + gw and gy < top + h and top < gy + gh:
                    bad += 1
                    print(f"FAIL p{page['page']:02d} {q['id']}: graphic overlaps its Play")
                for s in q.get("stamps") or []:
                    r = s["rect"]
                    if gx < r[2] + 1.5 and r[0] - 1.5 < gx + gw and gy < r[3] + 1.5 and r[1] - 1.5 < gy + gh:
                        bad += 1
                        print(f"FAIL p{page['page']:02d} {q['id']}: graphic covers its red answer")
                        break
                boxes.append((q["id"] + " graphic", gx, gy, gx + gw, gy + gh))
        # Two buttons on one page must not share a box: answer lines sit as close
        # as 20 pt apart and the button is 22 pt tall.
        for i, (qid, l0, t0, r0, b0) in enumerate(boxes):
            for qid2, l1, t1, r1, b1 in boxes[i + 1:]:
                if l0 < r1 - 0.5 and l1 < r0 - 0.5 and t0 < b1 - 0.5 and t1 < b0 - 0.5:
                    bad += 1
                    print(f"FAIL p{page['page']:02d} {qid} play overlaps {qid2} play")
    verdict = "PASS" if not bad else f"{bad} control(s) on ink or overlapping"
    print(f"{book_id}: {chips} chips, {plays} plays, {graphics} graphics, {verdict}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
