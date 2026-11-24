# PHY MECH F2 Force II (`phy06-force2`)

| | |
| --- | --- |
| Form | S4 |
| Book id / storage | `phy06-force2` (never rename ??it is the saved-ink key on every iPad) |
| Source | `books/phy06-force2/source/` QUE (16 pages), ANS (16 pages, offset **0**) |
| Status | draft |
| Live | not deployed |

## Source facts

- Both PDFs have 16 pages and the same page 1, so `source.ansPageOffset` is **0** (not the template's ??).
- Page structure (QUE):
  - p1 concept panel **Resolution of force** + q1 (find components, figure) + q2 ((a)(b)(c), three figures)
  - p2 q3??6 (all MC)
  - p3 q7, q8 (MC), q9??11 (free response)
  - p4 q12??15 (free response, no square)
  - p5 q16 ((a)(b) draw the resultant on the printed grid + find magnitude), q17 and q18 (MC)
  - p6 full concept page, no questions: **Resolution of force in inclined plane**, **Motion along a smooth
    inclined plane**, **Motion along a rough inclined plane**, **Friction-compensated**
  - p7 q19??22 (MC), p8 q23??26 (MC)
  - p9 q27 (a)(b), q28 (a)(b)(c)
  - p10 q29, p11 q30, p12 q31, p13 q32, p14 q33, p15 q34, p16 q35 ??one long question per page, each with
    (a)(b)(c) parts and HKDSE-style mark allocations
- 35 questions: **16 MC with a printed answer square** (q3??8, q17, q18, q19??26) and **19 free response**
  (q1, q2, q9??16, q27??35).
- q16 (a) and q18 (q18's own figures) are **drawing tasks on a printed grid** ?like phy11 q18, the marks are
  made in ink, so the solution must state what to draw, not draw it.
- The concept page p6 has no printed answer area: nothing to solve, but it is the best candidate for a panel
  animation later (four panels, like phy11 p1/p4/p7).

## Question map

| Section | Questions | Pages | Notes |
| --- | --- | --- | --- |
| `resolve` (Resolution of force) | q1??18 | 1?? | p1 and p5 carry grid figures |
| `incline` (Inclined plane) | q19??35 | 7??6 | p6 is the concept page before q19 |

## Decisions

- **g**: 9.81 everywhere (the teacher's rule for the physics books; the key may print other values, keep the
  printed answer letter and state the recomputed number if they differ).
- **Squares**: 16, at `x ???5`, 28 pt; measure each one per page (not assumed) ?p5's squares sit at
  y = 584.1 (q17) and y = 732.9 (q18) while q16 has none.
- **Region cut**: `region[3] ???0` for the 841.92 pt pages (printed footer row starts at 798.9, so the
  usable ink band ends at 790). No page has been relaid out yet; if a question needs more room than the
  blank band, open space in the PDF with `tools/relayout_pdf.py` and record it here (page height changes,
  printing needs scaling ?see phy11 p7).
- **Sections**: two, from the two concept headings (p1 "Resolution of force", p6 "Resolution of force in
  inclined plane"). No other heading is printed, so q9??18 (addition / equilibrium / components) stay in the
  first section.

## Open items

- `extract.overrides`: regions and `space` for all 35 questions, `square` for the 16 MC ?**not written yet**
  (auto regions from `extract_pages.py` are provisional and run to y = 818).
- `solutions.js`: empty template. 35 solutions to write from `reference/ans_pages/` and the per-question
  crops in `reference/ans/`.
- Review links: pick the phrases that recur in the printed text (numbers and units only), each with its own
  answer end (`lk(...)`).
- Graphics: q16 and q18 (grid drawings), q1??5 (vector components) and q27??35 (inclined-plane systems) are
  the natural candidates for `widgets.js`; none written yet.

