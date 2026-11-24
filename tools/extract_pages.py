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

ROOT = Path(__file__).resolve().parents[1]


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
    """
    best = None
    for y0, y1, words in rows:
        if not (y_start - 2 <= y0 < y_limit - 1):
            continue
        blanks = sum(w[2].count("_") for w in words)
        if blanks and (best is None or blanks > best[0]):
            best = (blanks, y0)
    return None if best is None else best[1]


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
    is what the answer overlay actually has to avoid.
    """
    marks = []
    for w in page.get_text("words"):
        marks.append(tuple(w[:4]))
    for d in page.get_drawings():
        r = d["rect"]
        marks.append((r.x0, r.y0, r.x1, r.y1))
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
        anchors = []
        for q in by_page.get(i + 1, []):
            found = fixed.get(q["id"]) or find_anchor(words, q["label"], anchors_cfg.get(q["id"]))
            anchors.append((q, found))
            if not found:
                print("MISSING ANCHOR", q["id"], "page", i + 1)
        items = []
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
            marks = ink_marks(page)
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
                y = blank_row_below(marks, region_x[0], min(region_x[1] + 60, page.rect.width),
                                    text_bottom + 1, next_y - 1)
                if y is None:
                    y = round(text_bottom + 3, 1)
                region_out = [region_x[0], round(y - 2, 1), region_x[1], y]
            if blank_bottom - blank_top < 36:
                blank_top = min(blank_top, max(next_y - 40, y1))
            item = {
                "id": q["id"],
                "label": q["label"],
                "section": q["section"],
                "anchor": [round(y0, 1), round(y1, 1)],
                "region": region_out,
                # Where a fill-in answer's ? chip belongs: the top-right of the
                # printed line that carries the blank (see card_spot).
                "cardAt": card_spot(marks, rows, y0, next_y, region_x[1], page.rect.width),
            }
            item.update(overrides.get(q["id"], {}))
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


if __name__ == "__main__":
    main()
