"""Decide how a book shows its answers, before any solution is written.

The reader has two ways to show worked solutions, and a book must pick one up
front, because the choice changes the page cuts, the region overrides and what
`check_book` measures:

    inline   the working sits in the printed blank space under its question;
             `space` opens more page at a cut and moves the rest of the page down
    cards    the working opens in a card over the page from a `?` chip in the
             margin; the printed page is never cut (`book.json` "answers": "cards")

Inline needs a blank row under each question to cut at, and a blank band tall
enough for the working. A worksheet page (a rule on every line, questions 10 pt
apart, a figure or a printed table running down the page) has neither, and a cut
there tears the figure or the table in two.

    python -X utf8 tools/layout_triage.py <book-id>

Reads `books/<id>/layout.json` and the page images, so run `extract_pages.py`
once first. Prints one row per page, a verdict for the book, and the exact
`book.json` / `extract.overrides` lines to apply. Exit code 0 is "reported";
1 means the layout has an inverted region that must be rebuilt first.
"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCALE = 2
INK = 200            # grey level under which a pixel counts as printed
ROW_GAP = 12.0       # two printed rows closer than this belong to one block
MIN_CUT = 3.0        # a cut needs at least this much blank height to be safe
ROOMY = 30.0         # a blank band this tall holds a short working without opening
CARD_SHARE = 0.10    # unused: kept out of the verdict, cards are per question now


def rows_of(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), colorspace=fitz.csGRAY, alpha=False)
    ink = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width) < INK
    return ink.any(axis=1), pix.height / SCALE


def blank_run(rows, y0, y1):
    """Tallest run of blank rows between y0 and y1, in points."""
    lo = max(0, int(round(y0 * SCALE)))
    hi = min(len(rows), int(round(y1 * SCALE)))
    best = run = 0
    for i in range(lo, hi):
        run = 0 if rows[i] else run + 1
        best = max(best, run)
    return best / SCALE


def has_blank(text, top, limit):
    """True when the question prints a fill-in blank (an underscore run) on its own lines."""
    for y0, y1, words in text:
        if not (top - 2 <= y0 < limit - 1):
            continue
        if any("_" in w[2] for w in words):
            return True
    return False


def block_bottom(text, top, limit):
    """Bottom of the printed block that starts at `top` (a question may print 2-3 lines)."""
    end = None
    for y0, y1, _ in text:
        if y0 < top - 2 or y0 > limit:
            continue
        if end is None or y0 <= end + ROW_GAP:
            end = max(end or y1, y1)
    return end if end is not None else top + 40


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    book_id = sys.argv[1]
    folder = ROOT / "books" / book_id
    book = json.loads((folder / "book.json").read_text(encoding="utf-8"))
    layout_path = folder / "layout.json"
    if not layout_path.exists():
        sys.exit(f"{book_id}: no layout.json - run python tools/extract_pages.py {book_id} first")
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    footer = book.get("extract", {}).get("footer", 822)
    doc = fitz.open(folder / book["source"]["que"])

    inverted = []
    per_page = []
    counts = {"inline": 0, "space": 0, "cards": 0}
    carded = []
    fillin = []
    for page in layout["pages"]:
        qs = page["questions"]
        if not qs:
            continue
        pdf = doc[page["page"] - 1]
        rows, height = rows_of(pdf)
        text = page.get("text") or []
        tall = 0
        for n, q in enumerate(qs):
            if q["region"][3] < q["region"][1]:
                inverted.append(f"{q['id']} p{page['page']}")
            top = q["anchor"][0]
            nxt = qs[n + 1]["anchor"][0] if n + 1 < len(qs) else footer
            bottom = block_bottom(text, top, min(nxt - 8, height))
            gap = max(0.0, min(nxt, height) - bottom)
            free = blank_run(rows, bottom + 1, bottom + gap)
            if has_blank(text, top, min(nxt, height)):
                fillin.append(q["id"])
            if free >= MIN_CUT and gap >= ROOMY:
                counts["inline"] += 1
            elif free >= MIN_CUT:
                counts["space"] += 1
                tall += 1
            else:
                counts["cards"] += 1
                carded.append(f"{q['id']}(p{page['page']})")
        per_page.append((page["page"], len(qs), gap, free, tall))

    # A card is for the questions the reader fills in; MC and long questions keep
    # the usual in-page working. A fill-in with no safe cut must be a card, and a
    # fill-in whose page is a worksheet is easier to read as one too.
    suggestion = [q["id"] for page in layout["pages"] for q in page["questions"]
                  if q["id"] in fillin or q["id"] in carded]

    total = sum(counts.values())
    if inverted:
        print("INVERTED REGIONS (bottom above top) - rebuild the layout first:")
        for item in inverted:
            print("  ", item)
        print("   run python tools/extract_pages.py", book_id)
        return 1

    print(f"{book['code']} {book['title']} ({book_id}): {total} questions on {len(per_page)} pages")
    print()
    print(" page  questions  last gap  blank band  open-page")
    for pg, n, gap, free, tall in per_page:
        print(f" p{pg:>3}  {n:>9}  {gap:>8.1f}  {free:>10.1f}  {tall:>9}")
    print()
    print(f" inline (fits the printed space): {counts['inline']}")
    print(f" inline + space (page opens under it): {counts['space']}")
    print(f" no blank row to cut at: {counts['cards']}")
    if carded:
        print("  ", ", ".join(carded[:14]), "..." if len(carded) > 14 else "")
    print()

    share = counts["cards"] / total if total else 0
    if counts["cards"]:
        print(f"VERDICT: a worksheet book - {counts['cards']} of {total} questions have no blank row to cut at.")
        print("  Put the FILL-IN questions in cards and leave MC / long questions inline, exactly")
        print("  like the physics books. A card opens from a ? chip at the top-right of the line")
        print("  that carries the blank, and the printed page never moves.")
        print()
        print('    "answerCards": [' + ", ".join(f'"{qid}"' for qid in suggestion) + "]")
        print()
        print(f"  no cut at all ({counts['cards']}): " + ", ".join(carded[:16]) + (" ..." if len(carded) > 16 else ""))
        print(f"  printed blank seen ({len(fillin)}): " + ", ".join(fillin[:16]) + (" ..." if len(fillin) > 16 else ""))
        print("  A circle-the-answer or table-cell question prints no underscore: add it by hand.")
        print("  For a card question do NOT add `space`: a card ignores it and the page must not move.")
        if counts["space"]:
            print(f'  Add "space" in extract.overrides for the {counts["space"]} inline questions that need room.')
        print("  Then run check_book.mjs and tools/qa/check_answer_chips.py.")
    else:
        print("VERDICT: inline answers (the usual in-page working)")
        if counts["space"]:
            print(f'  add "space" in extract.overrides for the {counts["space"]} questions that need room')
        print("  every cut must fall in a blank row: check the top of each page in pages/pNN.jpg")
    print()
    print("Record the decision in docs/chapters/<id>.md under 'How the answers show'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
