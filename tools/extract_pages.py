"""Render a book's QUE pages and write the blank-region layout for its overlays.

Usage:
    python tools/extract_pages.py <book-id>          # pages/*.jpg + layout.json
    python tools/extract_pages.py <book-id> --scan   # draft the question list

Everything chapter-specific (question list, anchors, region overrides) is in
books/<book-id>/book.json under "extract". See docs/02-book-format.md.
"""

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

# The Play button of a stamped answer: its box in pt, kept in step with
# `engine/styles.css` `.ans-play` (24 x 22) and tools/qa/check_answer_chips.py.
PLAY_W, PLAY_H = 24.0, 22.0
# Full size first, then smaller: a blank inside a table cell or squeezed between
# two printed cells takes a smaller Play rather than one parked on the far side of
# the page. Keep in step with tools/qa/check_answer_chips.py and check_play.mjs.
PLAY_SIZES = ((24, 22), (22, 20), (20, 18), (18, 16), (16, 14), (14, 12))


def load_book(book_id):
    folder = ROOT / "books" / book_id
    path = folder / "book.json"
    if not path.exists():
        sys.exit(f"No {path}; create the book first with tools/new_book.py")
    return folder, json.loads(path.read_text(encoding="utf-8"))


def words_of(page):
    words = []
    for w in page.get_text("words"):
        x0, y0, x1, y1, text, *_ = w
        words.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "t": text})
    return words


def norm_word(text):
    """NFKC so mathematical italics (𝐴𝐵) match plain letters (AB)."""
    return unicodedata.normalize("NFKC", text)


def answer_row(rows, y_start, y_limit):
    """The printed row that carries a fill-in blank, or None.

    A worksheet answer card is opened from a `?` chip that belongs at the top-right
    of the line the reader fills in, not at the left margin: the blank may sit on
    the second line of the question (`the ________.`), so the row is found from the
    printed underscores rather than from the question number.

    The FIRST such row wins, not the one with the most underscores: a later
    question on the same page can carry six blanks in one line, and picking that
    row puts this question's chip (and its Play) beside the wrong question.
    """
    for y0, y1, words in rows:
        if not (y_start - 2 <= y0 < y_limit - 1):
            continue
        if any("_" in w[2] for w in words):
            return y0
    return None


def clear_spot(marks, x, y, w=15.0, h=15.0):
    """True when no printed mark overlaps the 15 pt chip box at x, y."""
    return not any(ax < x + w and bx > x and ay < y + h and by > y for (ax, ay, bx, by) in marks)


def card_spot(marks, rows, y0, y_limit, x_right, page_w):
    """Where the ? chip goes: the top-right of the line that carries the blank.

    The right margin is the first choice; a printed table or a figure that reaches
    into it pushes the chip above the line, further out, or - last resort - to the
    left margin, so the chip never covers a printed word.
    """
    row = answer_row(rows, y0, y_limit) or y0
    for dx, dy in ((0, 0), (16, 0), (-10, 0), (0, -19), (0, 19), (22, 0), (30, 0)):
        x = x_right + 6 + dx
        y = row - 17 + dy
        if 2 <= x and x + 15 <= page_w - 2 and clear_spot(marks, x, y):
            return [round(x, 1), round(y, 1)]
    for dy in (0, -19, 19, 38, -38):
        y = row - 17 + dy
        if clear_spot(marks, 5, y):
            return [5.0, round(y, 1)]
    return [round(x_right + 6, 1), round(row - 17, 1)]


def image_rules(img, page_w, page_h, y0, y1, min_len=55):
    """Printed fill-in rules found by looking at the page image.

    A scanned worksheet has no text layer to ask where its blanks are, but a blank
    is a long thin dark run: this finds those runs inside the question's band so
    the Play button can sit at the right end of the rule the reader fills in.
    Returns [(x0, y, x1, y)] in pt.
    """
    sx = img.width / page_w
    sy = img.height / page_h
    top = max(0, int(y0 * sy))
    bot = min(img.height, int(y1 * sy))
    if bot - top < 2:
        return []
    band = img.crop((0, top, img.width, bot)).point(lambda v: 255 if v < 120 else 0)
    px = band.load()
    runs = []
    for yy in range(band.height):
        x = 0
        while x < band.width:
            if px[x, yy]:
                x2 = x
                while x2 + 1 < band.width and px[x2 + 1, yy]:
                    x2 += 1
                if x2 - x >= min_len * sx:
                    runs.append(((top + yy) / sy, x / sx, (x2 + 1) / sx))
                x = x2 + 1
            else:
                x += 1
    # Merge runs that sit within 3 pt of each other vertically and overlap in x.
    merged = []
    for y, a, b in sorted(runs):
        for m in merged:
            if abs(m[0] - y) <= 3 and a < m[2] and m[1] < b:
                m[1] = min(m[1], a)
                m[2] = max(m[2], b)
                break
        else:
            merged.append([y, a, b])
    return [(a, y, b, y) for y, a, b in merged]


def play_gaps(rows, row, region_x0, region_x1):
    """Free horizontal strips on an answer line, widest first.

    A fill-in blank shows up one of two ways: printed underscores, or (in a
    worksheet table) an empty cell between two printed cells. Both are a gap in
    the line's words, so the gaps are measured rather than guessed - the widest
    gap carries the blank, and the button goes inside it.

    Only gaps *between* the line's first and last word count: the empty stretch
    from the column's left edge to the first word is page margin, not a blank, and
    a button parked there sits nowhere near what the reader has to fill in.
    """
    line = None
    for y0, y1, words in rows:
        if abs(y0 - row) <= 2.5:
            line = (y0, y1, words)
            break
    if line is None:
        return row, row + 12.0, []
    y0, y1, words = line
    spans = sorted((x0, x1) for x0, x1, t in words if x1 > region_x0 - 6 and x0 < region_x1 + 6)
    if not spans:
        return y0, y1, []
    gaps = []
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        if b0 - a1 > 10:
            gaps.append((a1, b0))
    gaps.sort(key=lambda g: -(g[1] - g[0]))
    return y0, y1, gaps


def play_spot(img, marks, rows, y0, y_limit, region_x0, region_x1, page_w, page_h, taken=(), rules=()):
    """Where a stamped answer's Play button goes: the top-right of its blank.

    The button belongs at the fill-in blank, not at the page margin: the first
    choice is inside the widest free strip of the answer line, level with the top
    of the line and right-aligned in that strip. A table cell, a circle grid or a
    second blank can leave less room than the 24 x 22 button needs, so the same
    search is repeated for smaller boxes (down to 14 x 12) - a slightly smaller
    Play beside its blank beats a full-size one on the far side of the page, and
    the reader draws it at the size recorded here (`playSize`).

    A spot has to pass two tests: the rendered page has no ink under it (a scan
    has no text layer to ask, and this is the same pixel test QA runs later), and
    no printed mark's bounding box overlaps it - white inside a printed circle is
    still the circle. `taken` holds the buttons already placed on the page.

    Returns ([x, y], [w, h], [blank_x, blank_y]).
    """
    row, row_bottom, gaps = play_gaps(rows, answer_row(rows, y0, y_limit) or y0,
                                      region_x0, region_x1)
    # A scanned page is one page-sized image: its bbox would veto every spot even
    # where the paper is white. The pixel test below is the one that sees its ink.
    page_area = page_w * page_h
    marks = [m for m in marks if (m[2] - m[0]) * (m[3] - m[1]) < 0.25 * page_area]
    line_h = max(12.0, row_bottom - row)
    sx = img.width / page_w
    sy = img.height / page_h
    pad = 1.5

    def clear(x, y, w, h):
        # Round the sample box outwards: a thin printed rule one pixel wide must
        # not slip between the exact edges (QA crops the box itself and would see it).
        box = (int(math.floor((x - pad) * sx)), int(math.floor((y - pad) * sy)),
               int(math.ceil((x + w + pad) * sx)), int(math.ceil((y + h + pad) * sy)))
        crop = img.crop(box)
        if not (crop.size[0] and crop.size[1]) or crop.getextrema()[0] < 150:
            return False
        if not clear_spot(marks, x, y, w, h):
            return False
        return not any(x < tx1 and tx0 < x + w and y < ty1 and ty0 < y + h
                       for (tx0, ty0, tx1, ty1) in taken)

    # Strips to try, widest first: the blank itself is the widest free strip on its
    # line, and a table row splits into several strips (one per empty cell).
    # `first` is where the button starts inside the strip: right after a printed
    # blank or a line's last word it starts at the strip's left edge; inside an
    # empty cell it fills the cell's top-right corner, which is what it is for.
    blank_mid = None
    line_end = region_x1
    strips = []
    runs = []
    for y0_, y1_, words in rows:
        if abs(y0_ - row) > 2.5:
            continue
        if words:
            line_end = max(x1_ for x0_, x1_, t in words)
        runs = [(x0_, x1_) for x0_, x1_, t in words if "_" in t]
        if runs:
            # The last blank on the line: its top-right corner is where the button
            # goes, and the space after it is the first strip to try.
            lx0, lx1 = runs[-1]
            blank_mid = (lx0 + lx1) / 2
            strips.append((lx1, min(lx1 + 45.0, region_x1), "left"))
        break
    # Then the end of the answer line itself, then any other strip on it.
    # A printed blank may be a drawn rule rather than underscore characters (the
    # scanned worksheet pages): the button then goes at the right end of that rule.
    rules_here = [(a, b) for (a, ay, b, by) in rules
                  if ay >= row - 3 and by <= row + line_h + 3 and b - a > 25]
    if not runs and not rules_here:
        rules_here = [(a, b) for (a, _ay, b, _by)
                      in image_rules(img, page_w, page_h, row - 4, row + line_h + 4)
                      if b - a > 25]
    if not runs and rules_here:
        rx0, rx1 = max(rules_here, key=lambda rr: rr[1])
        blank_mid = (rx0 + rx1) / 2
        strips.append((rx1, min(rx1 + 45.0, region_x1), "left"))
    strips.append((line_end, region_x1, "left"))
    strips += [(g[0], g[1], "right") for g in gaps]

    right_limit = min(region_x1, page_w - 18)
    left_limit = max(2.0, region_x0)

    def clip(x, w):
        return max(left_limit, min(x, right_limit - w))

    for w, h in PLAY_SIZES:
        # Inside the answer line only: a hop to the line above or below drops the
        # button into the neighbouring table row, which reads as the wrong answer.
        ys = (row - 1, row + max(0.0, line_h - h) / 2, row + line_h - h)
        for gx0, gx1, first in (strips or [(region_x0, region_x1, "right")]):
            # A strip that starts at a printed blank or at the line's last word is
            # used from its left edge; an empty table cell is filled from its
            # top-right corner, which is the corner the reader reads as "here".
            xs = ((gx0 + 2, gx1 - w - 2, (gx0 + gx1 - w) / 2) if first == "left"
                  else (gx1 - w - 2, gx0 + 2, (gx0 + gx1 - w) / 2))
            for x in xs:
                for y in ys:
                    cx, cy = clip(x, w), y
                    if cy < 2 or cy + h > page_h - 2:
                        continue
                    if clear(cx, cy, w, h):
                        # On a scanned page there is no text layer, so no blank can
                        # be measured: the button goes at the right end of the answer
                        # line and `blankAt` records that corner, not a guess.
                        if blank_mid is not None:
                            blank = [round(blank_mid, 1), round(row, 1), round(line_end, 1)]
                        elif gaps:
                            blank = [round((gx0 + gx1) / 2, 1), round(row, 1), round(line_end, 1)]
                        else:
                            blank = None
                        # Do not claim a blank the button did not reach: a measured
                        # blank this far away means the line had no room, and QA must
                        # not read that as "beside its blank".
                        if blank:
                            dx = min(abs(cx + w / 2 - blank[0]), abs(cx + w / 2 - blank[2]))
                            if dx > 70:
                                blank = None
                        return ([round(cx, 1), round(cy, 1)], [w, h], blank)
    # Last resort: search a window around the blank itself. A blank that is
    # followed straight away by printed words (`the ______ of the circle.`) leaves
    # no room on its own line, so the button goes just above or below the blank,
    # as near to its right-hand corner as the paper allows.
    blank_mid = None
    for y0_, y1_, words in rows:
        if abs(y0_ - row) <= 2.5:
            for x0_, x1_, t in words:
                if "_" in t:
                    blank_mid = (x0_ + x1_) / 2
                    break
            break
    if blank_mid is None and strips:
        blank_mid = (strips[0][0] + strips[0][1]) / 2
    if blank_mid is not None:
        bx = blank_mid
        for w, h in PLAY_SIZES:
            best = None
            for dy in range(-26, 31, 4):
                for dx in range(0, 61, 4):
                    for sgn in ((1,) if dx == 0 else (1, -1)):
                        x = bx + sgn * dx - w / 2
                        y = row + dy
                        if x < left_limit or x + w > right_limit or y < 2 or y + h > page_h - 2:
                            continue
                        if clear(x, y, w, h):
                            d = abs(dx) + abs(dy) * 0.6
                            if best is None or d < best[0]:
                                best = (d, x, y)
                if best:
                    break
            if best:
                return ([round(best[1], 1), round(best[2], 1)], [w, h],
                        [round(bx, 1), round(row, 1), round(line_end, 1)])

    # Last resort: step outwards from the blank (or the line's right end) along the
    # line, shrinking as it goes, so the button stays as near its blank as the
    # printed page allows instead of jumping to the far edge.
    anchor_x = (blank_mid - 24.0 / 2) if blank_mid is not None else (line_end - PLAY_SIZES[0][0] / 2)
    for w, h in PLAY_SIZES:
        ys = (row - 1, row + line_h - h, row + (line_h - h) / 2, row - h - 1, row + line_h + 1)
        base = anchor_x - w / 2 + 12.0
        for step in range(0, 260, 6):
            for x in ((base + step, base - step) if step else (base,)):
                x = clip(x, w)
                for y in ys:
                    if y < 2 or y + h > page_h - 2:
                        continue
                    if clear(x, y, w, h):
                        return ([round(x, 1), round(y, 1)], [w, h],
                                [round(x + w, 1), round(y, 1), round(x + w, 1)])
    w, h = PLAY_SIZES[0]
    y = max(2.0, min(row - 1, page_h - h - 2))
    bx = clip(right_limit - w, w)
    return ([round(bx, 1), round(y, 1)], [w, h], [round(bx + w, 1), round(y, 1), round(bx + w, 1)])


def text_lines(page):
    """Printed text lines as [y0, y1, [[x0, x1, word], ...]] for snapping and review links."""
    lines = {}
    for x0, y0, x1, y1, text, block, line, _word in page.get_text("words"):
        lines.setdefault((block, line), []).append((x0, y0, x1, y1, norm_word(text)))
    rows = []
    for ws in sorted(lines.values(), key=lambda ws: min(w[1] for w in ws)):
        y0 = min(w[1] for w in ws)
        y1 = max(w[3] for w in ws)
        if y1 - y0 > 40:
            continue
        row = next((r for r in rows if min(r[1], y1) - max(r[0], y0) > 0.6 * min(r[1] - r[0], y1 - y0)), None)
        if row:
            row[0], row[1] = min(row[0], y0), max(row[1], y1)
            row[2].extend(ws)
        else:
            rows.append([y0, y1, list(ws)])
    out = []
    for y0, y1, ws in rows:
        ws.sort()
        out.append([round(y0, 1), round(y1, 1), [[round(w[0], 1), round(w[2], 1), w[4]] for w in ws]])
    return out


def find_anchor(words, label, pattern):
    if pattern:
        line = {}
        for w in words:
            key = round(w["y0"], 0)
            line.setdefault(key, []).append(w)
        for key in sorted(line):
            ws = sorted(line[key], key=lambda w: w["x0"])
            text = " ".join(w["t"] for w in ws)
            if pattern.search(text):
                return min(w["y0"] for w in ws), max(w["y1"] for w in ws)
        return None
    # Numbered question: a lone "12." or "12" near the left margin.
    target = label
    for w in words:
        if w["x0"] > 80:
            continue
        token = w["t"].rstrip(".")
        if token == target and w["t"].endswith("."):
            return w["y0"], w["y1"]
    for w in words:
        if w["x0"] > 70:
            continue
        if w["t"].rstrip(".") == target and len(w["t"]) <= len(target) + 1:
            return w["y0"], w["y1"]
    return None


def ink_marks(page):
    """Every printed mark as (x0, y0, x1, y1): text, drawings and images.

    The old region was built from text lines only, so it ran over circuit diagrams,
    option tables and the page number. Anything printed counts as occupied now, which
    is what the answer overlay actually has to avoid. On a scanned page the single
    page-sized image keeps its figures out of reach too - white inside a printed
    circle is still the circle.
    """
    marks = []
    for w in page.get_text("words"):
        marks.append(tuple(w[:4]))
    for d in page.get_drawings():
        r = d["rect"]
        fill = d.get("fill")
        if fill is None:
            # A small unfilled stroke (a table rule, a printed blank) only inks its
            # outline; treating the whole bbox as ink makes every cell solid. A big
            # one is a figure - a circle, a protractor - and its white inside is
            # still the figure, so its whole box stays blocked.
            if min(r.x1 - r.x0, r.y1 - r.y0) > 40:
                marks.append((r.x0, r.y0, r.x1, r.y1))
            else:
                t = 2.0
                marks.append((r.x0, r.y0, r.x1, r.y0 + t))
                marks.append((r.x0, r.y1 - t, r.x1, r.y1))
                marks.append((r.x0, r.y0, r.x0 + t, r.y1))
                marks.append((r.x1 - t, r.y0, r.x1, r.y1))
        elif sum(fill[:3]) / 3 < 0.85:
            marks.append((r.x0, r.y0, r.x1, r.y1))
        # A pale fill is a shaded band on a worksheet table, not ink: the pixel
        # test decides, and it does not mistake a light blue row for print.
    for img in page.get_images(full=True):
        try:
            r = page.get_image_bbox(img)
        except Exception:
            continue
        marks.append((r.x0, r.y0, r.x1, r.y1))
    return marks


def largest_free_rect(marks, x0, x1, y0, y1, step=2.0, min_h=50.0, min_w=120.0):
    """Biggest ink-free rectangle inside the box, so an answer can sit beside a figure."""
    nx = max(1, int((x1 - x0) / step))
    ny = max(1, int((y1 - y0) / step))
    grid = [[True] * nx for _ in range(ny)]
    for (ax, ay, bx, by) in marks:
        if bx < x0 or ax > x1 or by < y0 or ay > y1:
            continue
        i0 = max(0, int((ay - y0) / step))
        i1 = min(ny, int(math.ceil((by - y0) / step)))
        j0 = max(0, int((ax - x0) / step))
        j1 = min(nx, int(math.ceil((bx - x0) / step)))
        for i in range(i0, i1):
            row = grid[i]
            for j in range(j0, j1):
                row[j] = False
    best = None
    hist = [0] * nx
    for i in range(ny):
        for j in range(nx):
            hist[j] = hist[j] + 1 if grid[i][j] else 0
        stack = []
        j = 0
        while j <= nx:
            h = hist[j] if j < nx else 0
            if not stack or h >= hist[stack[-1]]:
                stack.append(j)
                j += 1
            else:
                top = stack.pop()
                width = (j - stack[-1] - 1) if stack else j
                hh = hist[top]
                w, hgt = width * step, hh * step
                if w >= min_w and hgt >= min_h:
                    area = w * hgt
                    if best is None or area > best[0]:
                        left = x0 + ((stack[-1] + 1) if stack else 0) * step
                        top_y = y0 + (i - hh + 1) * step
                        best = (area, left, top_y, left + w, top_y + hgt)
    return None if best is None else tuple(round(v, 1) for v in best[1:])


def blank_row_below(marks, x0, x1, y_from, y_to, height=2.0):
    """A blank band of `height` pt just under a printed line, or None when none fits.

    A dense page has no free band to put the answer in, so the answer opens the
    page at a row under the question. That band must cross no ink (the reader cuts
    the page at its bottom edge and measures a figure beside it from those rows),
    and it starts a little above the cut so the answer card itself stays still
    while everything below the cut moves down into the room it opened.
    """
    if y_to - y_from < height:
        return None
    step = 0.5
    y = y_from + height
    while y <= y_to:
        if not any(ay < y and by > y - height and ax < x1 and bx > x0
                   for (ax, ay, bx, by) in marks):
            return round(y, 1)
        y += step
    return None


def question_bottom(words, y_start, y_limit):
    """Bottom of printed question text before the blank working space."""
    ys = [w["y1"] for w in words if y_start - 1 <= w["y0"] < y_limit - 8 and w["x0"] < 560]
    if not ys:
        return y_start + 40
    # Cluster lines; the question body is the first run of lines.
    lines = sorted(set(round(w["y0"]) for w in words if y_start - 1 <= w["y0"] < y_limit - 8))
    if not lines:
        return y_start + 40
    end = lines[0]
    for y in lines[1:]:
        if y - end > 28:
            break
        end = y
    bottoms = [w["y1"] for w in words if abs(round(w["y0"]) - end) <= 2 or (y_start - 1 <= w["y0"] <= end + 2)]
    return max(bottoms) if bottoms else y_start + 40


def scan(folder, book):
    """Print a draft "questions" list: numbered items and Example/Practice headings per page."""
    doc = fitz.open(folder / book["source"]["que"])
    heading = re.compile(r"^(Example|Practice|Exercise|Class\s*work|Challenge|Revision)\b", re.I)
    draft = []
    for i, page in enumerate(doc):
        big = set()
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"]).strip()
                size = max((s["size"] for s in line["spans"]), default=0)
                if size >= 14 and re.fullmatch(r"[A-Za-z][A-Za-z ()&'!?,-]{3,}", text):
                    big.add(text)
        for text in sorted(big):
            print(f"  page {i + 1}: possible section title: {text!r}")
        rows = {}
        for w in words_of(page):
            rows.setdefault(round(w["y0"]), []).append(w)
        for y in sorted(rows):
            ws = sorted(rows[y], key=lambda w: w["x0"])
            text = " ".join(w["t"] for w in ws)
            first = ws[0]
            m = re.match(r"^(\d+)\.?$", first["t"])
            if m and first["x0"] < 80:
                draft.append({"id": f"q{m.group(1)}", "page": i + 1, "label": m.group(1), "section": ""})
            elif heading.match(text):
                label = " ".join(text.split()[:2])
                qid = re.sub(r"[^a-z0-9]", "", label.lower().replace("example", "ex").replace("practice", "p"))
                draft.append({"id": qid, "page": i + 1, "label": label, "section": "", "anchor": re.escape(label).replace("\\ ", "\\s*")})
    print(json.dumps(draft, indent=2, ensure_ascii=False))
    print("Check the list, fill in each section, move any 'anchor' into extract.anchors, then paste into book.json.")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder, book = load_book(sys.argv[1])
    if "--scan" in sys.argv:
        scan(folder, book)
        return
    cfg = book["extract"]
    zoom = cfg.get("zoom", 3)
    region_x = cfg.get("regionX", [66, 546])
    footer = cfg.get("footer", 822)
    anchors_cfg = {k: re.compile(v) for k, v in cfg.get("anchors", {}).items()}
    fixed = {k: tuple(v) for k, v in cfg.get("fixedAnchors", {}).items()}
    overrides = cfg.get("overrides", {})

    pages_dir = folder / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(folder / book["source"]["que"])
    mat = fitz.Matrix(zoom, zoom)
    page_meta = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        # MuPDF here cannot write WebP; JPEG keeps the page sharp at a smaller size.
        out = pages_dir / f"p{i+1:02d}.jpg"
        pix.save(str(out), jpg_quality=86)
        page_meta.append({
            "page": i + 1,
            "width": round(page.rect.width, 2),
            "height": round(page.rect.height, 2),
        })
        print("rendered", out.name, pix.width, pix.height)

    by_page = {}
    for q in cfg["questions"]:
        by_page.setdefault(q["page"], []).append(q)

    layout_pages = []
    dense_pages = []
    for i, page in enumerate(doc):
        words = words_of(page)
        rows = text_lines(page)
        # The page as the reader sees it: the Play button is placed by looking at
        # these pixels, so a scan page is read exactly like a vector one.
        page_img = Image.open(pages_dir / f"p{i+1:02d}.jpg").convert("L")
        anchors = []
        for q in by_page.get(i + 1, []):
            found = fixed.get(q["id"]) or find_anchor(words, q["label"], anchors_cfg.get(q["id"]))
            anchors.append((q, found))
            if not found:
                print("MISSING ANCHOR", q["id"], "page", i + 1)
        items = []
        taken = []
        marks = ink_marks(page)
        # Printed blanks drawn as rules (the scanned worksheet pages): thin, unfilled,
        # wider than a character, so play_spot can put the button at their right end.
        page_rules = []
        for d in page.get_drawings():
            r = d["rect"]
            if d.get("fill") is None and (r.y1 - r.y0) < 4 and (r.x1 - r.x0) > 25:
                page_rules.append((r.x0, r.y0, r.x1, r.y1))
        for n, (q, found) in enumerate(anchors):
            if not found:
                continue
            y0, y1 = found
            next_y = footer
            for _, nxt in anchors[n + 1:]:
                if nxt:
                    next_y = nxt[0] - 6
                    break
            text_bottom = question_bottom(words, y0, next_y)
            blank_top = text_bottom + 6
            blank_bottom = next_y - 4
            # Any printed mark in the candidate strip - figure, option table, page
            # number - splits it; the answer goes in the first roomy free band.
            rect = largest_free_rect(marks, region_x[0], region_x[1], blank_top, blank_bottom)
            if not rect:
                rect = largest_free_rect(marks, region_x[0], region_x[1], blank_top, blank_bottom,
                                         min_h=36.0, min_w=90.0)
            if not rect:
                rect = largest_free_rect(marks, region_x[0], region_x[1], blank_top, blank_bottom,
                                         min_h=26.0, min_w=60.0)
            if rect:
                rx0, ry0, rx1, ry1 = rect
                region_out = [round(rx0, 1), round(ry0, 1), round(rx1, 1), round(ry1, 1)]
            else:
                dense_pages.append((q["id"], i + 1))
                # A dense page has no free band: the answer opens the page below the
                # question instead (layout "space" + growSheet). The band must be a
                # blank row just under the question's own text and above the next
                # printed line, because growSheet cuts the page at the band's bottom
                # edge and the reader reads a figure beside the band from that row.
                # An inverted band (bottom above top) cuts the page above the answer
                # and leaves the answer card sitting on the next question's text.
                # The reader cuts the sheet across its whole width at region[3], not
                # just across the text column, so the row has to be blank end to end:
                # a printed figure or answer box on the right would be sliced in two
                # (p5m07a q35 and hw14 were). Search the full page width.
                y = blank_row_below(marks, 0, page.rect.width, text_bottom + 1, next_y - 1)
                if y is None:
                    y = round(text_bottom + 3, 1)
                region_out = [region_x[0], round(y - 2, 1), region_x[1], y]
            if blank_bottom - blank_top < 36:
                blank_top = min(blank_top, max(next_y - 40, y1))
            spot = play_spot(page_img, marks, rows, y0, next_y, region_x[0], region_x[1],
                             page.rect.width, page.rect.height, taken, page_rules)
            item = {
                "id": q["id"],
                "label": q["label"],
                "section": q["section"],
                "anchor": [round(y0, 1), round(y1, 1)],
                "region": region_out,
                # Where a fill-in answer's ? chip belongs: the top-right of the
                # printed line that carries the blank (see card_spot).
                "cardAt": card_spot(marks, rows, y0, next_y, region_x[1], page.rect.width),
                # Where a stamped answer's Play button goes: the top-right of the
                # blank, at the largest of PLAY_SIZES that fits (see play_spot).
                # `blankAt` is the blank itself, so QA can prove the button is
                # beside it rather than somewhere else on the page.
                "playAt": spot[0],
                "playSize": spot[1],
                "blankAt": spot[2],
            }
            item.update(overrides.get(q["id"], {}))
            at, size = item["playAt"], item.get("playSize") or [PLAY_W, PLAY_H]
            # A fill-in answer with an interactive picture gets a second button in the
            # stamp branch (engine/viewer/answers.js): the same search again, with the
            # Play's box already taken, so the two buttons never share a spot. The
            # rules for the inline `.ctl` graphic button are untouched.
            play_box = (at[0], at[1], at[0] + size[0], at[1] + size[1])
            if "graphicAt" not in item:
                spot2 = play_spot(page_img, marks, rows, y0, next_y, region_x[0], region_x[1],
                                  page.rect.width, page.rect.height,
                                  taken + [play_box], page_rules)
                gx, gy = spot2[0]
                w2, h2 = spot2[1]
                # The last-resort branch of play_spot ignores `taken`: if the page is
                # that tight, put the second button beside the Play instead of under it.
                def hits(x, y, w, h):
                    return (x < play_box[2] and play_box[0] < x + w
                            and y < play_box[3] and play_box[1] < y + h)
                if hits(gx, gy, w2, h2):
                    for cx, cy in ((play_box[0] - w2 - 4, play_box[1]),
                                   (play_box[2] + 4, play_box[1]),
                                   (play_box[0], play_box[1] - h2 - 4),
                                   (play_box[0], play_box[3] + 4)):
                        cx = max(2.0, min(cx, page.rect.width - 18 - w2))
                        if 2 <= cy and cy + h2 <= page.rect.height - 2 and not hits(cx, cy, w2, h2):
                            gx, gy = cx, cy
                            break
                item["graphicAt"] = [round(gx, 1), round(gy, 1)]
                item["graphicSize"] = [w2, h2]
            taken.append(play_box)
            gsize = item.get("graphicSize") or size
            gx, gy = item["graphicAt"]
            taken.append((gx, gy, gx + gsize[0], gy + gsize[1]))
            items.append(item)
        layout_pages.append({**page_meta[i], "questions": items, "text": rows})

    text = json.dumps({"zoom": zoom, "pages": layout_pages}, indent=2, ensure_ascii=False)
    text = re.sub(r"\[\s+([-\d.]+),\s+([-\d.]+)\s+\]", r"[\1, \2]", text)
    text = re.sub(
        r'\[\s+([-\d.]+),\s+([-\d.]+),\s+("(?:\\.|[^"\\])*")\s+\]',
        r"[\1, \2, \3]",
        text,
    )
    layout = folder / "layout.json"
    layout.write_text(text, encoding="utf-8")
    if dense_pages:
        print("NO FREE BAND (answer region forced to 40 pt, need an override):")
        for qid, pg in dense_pages:
            print(f"  {qid} page {pg}")
    print("wrote", layout)
    # A page number placed by hand is not in the PDF, so the re-render above just wiped it.
    # books/<id>/folio.json + books/<id>/folio/pNN.png put it back (see tools/qa/stamp_folio.py).
    if (folder / "folio.json").exists():
        import subprocess
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "qa" / "stamp_folio.py"), sys.argv[1]],
            check=True,
        )
    # Panels drawn on top of a page by hand (books/<id>/panels.json + books/<id>/panels/*.png) are
    # wiped by the re-render above, so they go back on here, last, so the panel is not re-encoded
    # again by the folio stamp; see tools/paste_panels.py.
    if (folder / "panels.json").exists():
        import subprocess
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "paste_panels.py"), sys.argv[1]],
            check=True,
        )
    # The red answers on the ANS pages are the answer for a fill-in book: cut them
    # once the layout exists and record where they belong (see tools/answer_stamps.py).
    if book.get("answerStamps"):
        import subprocess
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "answer_stamps.py"), sys.argv[1]],
            check=True,
        )


if __name__ == "__main__":
    main()
