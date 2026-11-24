"""Open blank space on one page of a PDF without touching a single printed mark.

The page is cut at a horizontal line and the content below the cut is moved down by
`--add` points; the page becomes that much taller. Nothing is re-typeset, so every
glyph, figure and formula stays exactly as the teacher's notes print it. Answer
space in the e-book then comes from real blank paper instead of the reader cutting
the page at run time.

    python tools/relayout_pdf.py in.pdf out.pdf --page 7 --at 796.8 --add 150

The cut must land in a blank gap between printed rows (pick it from the page image:
1 pt = 3 px at the 3x render). A cut inside a row tears that row in two.

Requires: PyMuPDF (import as fitz).
"""
import argparse
import sys

import fitz


def relayout(src: str, dst: str, page_no: int, cut: float, add: float) -> None:
    doc = fitz.open(src)
    if not 1 <= page_no <= doc.page_count:
        sys.exit(f"page {page_no} is outside 1..{doc.page_count}")
    out = fitz.open()
    for i in range(doc.page_count):
        if i + 1 != page_no:
            out.insert_pdf(doc, from_page=i, to_page=i)
            continue
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        if not 0 < cut < h:
            sys.exit(f"--at {cut} is outside the page (0..{h:.1f})")
        new = out.new_page(width=w, height=h + add)
        # above the cut: unchanged, in place
        if cut > 0:
            new.show_pdf_page(fitz.Rect(0, 0, w, cut), doc, i, clip=fitz.Rect(0, 0, w, cut))
        # below the cut: the whole block moves down; the opened band is blank paper
        new.show_pdf_page(
            fitz.Rect(0, cut + add, w, h + add), doc, i, clip=fitz.Rect(0, cut, w, h)
        )
    out.save(dst, garbage=4, deflate=True)
    print(f"page {page_no}: {page.rect.width:.1f} x {page.rect.height:.1f} -> "
          f"{page.rect.width:.1f} x {page.rect.height + add:.1f}")
    print(f"blank band inserted: y {cut:.1f} .. {cut + add:.1f} ({add:.1f} pt)")
    out.close()
    doc.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--page", type=int, required=True, help="1-based page to open up")
    ap.add_argument("--at", type=float, required=True, help="cut line, PDF points from the top")
    ap.add_argument("--add", type=float, required=True, help="blank points to insert")
    a = ap.parse_args()
    if a.src == a.dst:
        sys.exit("refusing to overwrite the source PDF; write to a new file")
    relayout(a.src, a.dst, a.page, a.at, a.add)


if __name__ == "__main__":
    main()
