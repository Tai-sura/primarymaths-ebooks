# jpfm08 — Moment of force (JPFM08)

- **book id**: `jpfm08` (never rename: it is the pen-ink storage key on every iPad)
- **form**: S4   **code**: JPFM08   **title**: Moment of force   **topic**: Moment of force
- **source**: 15-page QUE + 15-page ANS, both A4
- **ansPageOffset**: **0** — verified 2026-11-21 by comparing, page by page, the set of printed
  question numbers in the QUE and ANS files: all 15 pages carry an identical set (p1 `1`, p2 `2`,
  p3 `3 4 5`, p4 `6–10`, p5 `11 12 13`, p6 `14–17`, p7 none, p8 `18–21`, p9 `22 23`, p10 `24 25`,
  p11 `26 27`, p12 `28`, p13 `29`, p14 `30`, p15 `31`). The template default `-1` was wrong.
- **status**: stage 2 done 2026-11-21 — pages rendered, 31 questions listed, sections set, layout built

## Sections

Section titles are the boxed panels printed in the notes:

| id | label | pages | questions |
| --- | --- | --- | --- |
| `moment` | Moment of a force | 1–2 | q1–q2 (2) |
| `principle` | Principle of moments | 3–6 | q3–q17 (15) |
| `couples` | Couples | 8–15 | q18–q31 (14) |

- **p5** also prints a sub-panel **"Conditions for equilibrium"**, but it sits inside the
  Principle of moments block and carries no question of its own → kept under `principle`.
- **p7** prints two panels, **Couples** and **Centre of gravity**, and no question at all (hence no
  ANS crop for that page). It is a pure concept spread.
- **p10** has no heading of its own: q24 (rolling ball) and q25 (scissors) are moment/equilibrium
  applications and stay in `couples`. No fourth section is needed unless the teacher wants the
  "Centre of gravity" panel exposed as a jump target.

## Question map

**31 questions, printed 1–31, no gap and no repeat.** Per page:

| page | questions | count |
| --- | --- | --- |
| 1 | q1 | 1 |
| 2 | q2 | 1 |
| 3 | q3, q4, q5 | 3 |
| 4 | q6, q7, q8, q9, q10 | 5 |
| 5 | q11, q12, q13 | 3 |
| 6 | q14, q15, q16, q17 | 4 |
| 7 | — (concept page) | 0 |
| 8 | q18, q19, q20, q21 | 4 |
| 9 | q22, q23 | 2 |
| 10 | q24, q25 | 2 |
| 11 | q26, q27 | 2 |
| 12 | q28 | 1 |
| 13 | q29 | 1 |
| 14 | q30 | 1 |
| 15 | q31 | 1 |

`extract_pages.py --scan` noise that was dropped (numbers inside the text, not question numbers):

- p3 — `300, 400, 450, 600, 350, 700, 1400` (force/moment values in the worked text)
- p5 — `1, 2` (list numbering) **and `18`** (a value in the text; q18 really starts on p8)
- p7 — `1, 2, 3, 4, 5` (the three conditions of a couple plus list items)

`layout.json`: **all 31 anchors found**, no `MISSING ANCHOR`, no page without a question except p7
(concept spread).

**Printed worked answers**: none. The QUE file has no `Solution` / `Ans` string on any page, so all
31 questions are blank for the student.

## Answer regions that need an override

18 questions get less than 60 pt of free band; four of those even come out negative (the question
text runs straight into the next question). `extract_pages.py` printed `NO FREE BAND` for q3, q4, q5,
q6, q7, q8, q9, q10, q11, q12, q13, q15, q19.

| question | page | default region | height |
| --- | --- | --- | --- |
| q3 | 3 | `[66, 524, 546, 548]` | 24 |
| q4 | 3 | `[66, 649, 546, 674]` | 24 |
| q5 | 3 | `[66, 822, 546, 818]` | **−4** |
| q6 | 4 | `[66, 193, 546, 210]` | 17 |
| q7 | 4 | `[66, 348, 546, 351]` | **4** |
| q8 | 4 | `[66, 525, 546, 519]` | **−6** |
| q9 | 4 | `[66, 647, 546, 658]` | 11 |
| q10 | 4 | `[66, 822, 546, 818]` | **−4** |
| q11 | 5 | `[66, 489, 546, 501]` | 12 |
| q12 | 5 | `[66, 638, 546, 652]` | 14 |
| q13 | 5 | `[66, 789, 546, 818]` | 29 |
| q15 | 6 | `[66, 387, 546, 417]` | 30 |
| q16 | 6 | `[66, 574, 336, 602]` | 28 |
| q17 | 6 | `[66, 761, 190, 817]` | 56 |
| q19 | 8 | `[66, 423, 546, 420]` | **−3** |
| q20 | 8 | `[66, 579, 376, 621]` | 42 |
| q21 | 8 | `[66, 792, 190, 818]` | 26 |
| q22 | 9 | `[66, 244, 398, 286]` | 42 |

Two more faults that `check_book` cannot see:

1. **q13, q17, q21** — their region bottoms are **818 / 817 / 817**, i.e. below the printed footer,
   which starts at 797.6. House rule is `region[3] <= 790`, so these three cover the red
   「警告: 不可翻印…」 line.
2. **q2** — region `[240, 99, 546, 797]` (698 pt) starts right under the stem, so the answer box would
   be painted over all six diagrams (a)–(f). The blank space for this question is the right-hand
   column: x ≈ 400–546 is clear of every figure, so the region should be something like
   `[400, 110, 546, 800]` and the six answers written as six short lines.

Pages that may need the PDF opened (a `space` cut) can only be judged once the answers are written —
the long questions are q2 (six parts), q24 (a)(b), q25 (a)(b)(c), q28, q29, q30, q31.

## Next

Stage 3 (solutions) starts only after Chief checks the table above. The region work above belongs to
layout-engineer (`extract.overrides`), not to `solutions.js`.

## Solutions progress

| batch | questions | status | final answers |
| --- | --- | --- | --- |
| 1 (2026-11-21) | q1 | written | (a) `20 sin30°(2) = 20 N m`; (b) `20 sin45°(2) = 28.3 N m`; (c) `0 N m` (no perpendicular distance) |
| 1 (2026-11-21) | q2 | written | (a) `30(0.4) = 12 N m` anticlockwise; (b) `30(0.4)sin60° = 10.4 N m` clockwise; (c) `120(1.5)cos40° = 138 N m` clockwise; (d) `50(1)sin0° = 0`; (e) `6(0.4) = 2.4 N m` clockwise; (f) `20(7+3)sin70° + 15(3)sin60° = 227 N m` anticlockwise |
| 1 (2026-11-21) | q3 | written (MC) | **B** — `600×6 = F×9 → F = 400 N` |
| 2 (2026-11-21) | q4 | written (MC) | **C** — `W(0.5) = 100(0.5)+200(1.5) → W = 700 N` |
| 2 (2026-11-21) | q5 | written (MC) | **D** — `500(5-x) = 300×5 → x = 2 m` |
| 2 (2026-11-21) | q6 | written (MC) | **B** — `4(1)-2(1) = 2 kN m` anti-clockwise (4 kN at 1 m, 2 kN at 1 m) |
| — | q7–q31 (25) | **not written** | by batch |

QA after batch 1: **q1, q2, q3 have 0 FAIL**. q1 and q2 are clean; **q3 has 1 WARN** (answer scrolls,
85 pt more would show it all). The other 28 report "no entry in `solutions.js`", which is expected.

Note: `q1` has **three** parts (a) θ = 30°, (b) θ = 45°, (c) θ = 0°; the ANS crop folder only holds
the box for part (c) (`0 N m`), so parts (a) and (b) were read from `reference/ans_pages/ans_01.png`.
Note: `q4` and `q5` sit on **p3** (not p4) — p3 carries q3–q5, p4 carries q6–q10. All five questions on those
two pages are MC.

QA after batch 2: **q1–q6 have 0 FAIL, 0 WARN**; the region work by layout-engineer (q3 `space` 120,
q4 `space` 120, q5 region `[110,717,546,789]`) already fits these answers. 25 questions remain.
## Solutions progress (all written 2026-11-21)

31 questions, batches 1-11. Answers by question:

| q | answer | q | answer |
| --- | --- | --- | --- |
| q1 | (a) 20 N m (b) 28.3 N m (c) 0 | q17 | **B** n = 12 |
| q2 | 12 / 10.4 / 138 / 0 / 2.4 / 227 N m | q18 | **A** (only (2)) |
| q3 | **B** 400 N | q19 | **D** ((2) and (3)) |
| q4 | **C** 700 N | q20 | **C** along OQ |
| q5 | **D** 2 m | q21 | **D** θ = 73.9°, R = 180 N |
| q6 | **B** 2 kN m a.c. | q22 | **D** T = 0.94Mg then falls |
| q7 | **C** 1.1 N m c.w. | q23 | 200 N / 1000 N, F_Y↓ F_X↑, 1.4 m, topples |
| q8 | **B** 19.3 N | q24 | FBDs; smooth slides, rough rolls |
| q9 | **B** 5 N | q25 | F₁L₁ = F₂L₂; F₁ > F₂ |
| q10 | **D** 110 N | q26 | 40.4 N; 17.5 N |
| q11 | **B** 15 N, 25 N | q27 | 25 N; 25 N; 25 N; 21.7 / 16.1 N |
| q12 | **C** 20.5 cm | q28 | 110 N; 55 N; 60 N; hinge; 95.4 N at 3°; diagram |
| q13 | **B** Q 30 N, P 20 N | q29 | 3 N; 6.53 N; 4.20 N / 3.0 N |
| q14 | **C** P 200 N, Q 100 N | q30 | 289 N; 289 N; 1.54 m |
| q15 | **B** 1 : 4 | q31 | six-point experiment |
| q16 | **B** 0.125 m | | |

Final QA: **`check_book jpfm08` 0 FAIL, 0 WARN**.

Two key slips, corrected in the book (both leave the printed answer valid):

- q12 — the key prints `0.4(9.81)(4.5 − d)`; the C.G. of a 90 cm bar is **0.45 m** from the end.
- q29(c) — the key prints `3.26 × cos 40°`; the term is `6.53 cos 40° = 5.00 N`, giving 3.0 N.
## Verifier corrections (2026-11-21)

`verifier` checked all 31 answers: 30 agreed, one text fault, three clarifications. All applied to
`solutions.js`:

1. **q20 (real fault)** — the working said the reaction acts along "OQ", but option C is **OR**, and OQ
   is horizontal (= option B), so the sentence contradicted its own letter. Rewritten as: the three
   forces must be concurrent; the line MY produced and the vertical through X meet below and to the
   right of O, so the reaction acts along **OR**.
2. **q22** — "the C.G. moves nearer P" was wrong for a uniform plank. Now: the C.G. stays at the
   mid-point; the horizontal distance `1.0cosθ` from P is what falls, so the moment of the weight and
   T fall. `0.94Mg` unchanged.
3. **q27(a)(c)** — the vertical forces' arms are the **horizontal** distances `0.6cos30°` / `0.6cos50°`,
   not `0.6sin60°` / `0.6sin40°` (same value, wrong label). Written in cos form, (d) included for
   consistency; answers still 25 N and 21.7 / 16.1 N.
4. **q29(b)** — added why 50° appears: the 40° in the figure is measured from the vertical, so the
   string makes 50° with the rod.

`check_book jpfm08` after the changes: **0 FAIL, 2 WARN** — q20 (30 pt) and q22 (31 pt) now want a
little more height because of the added lines.

## Final QA and page numbers (2026-11-21)

- `check_book jpfm08`: **0 FAIL, 0 WARN**. `measure_ctl jpfm08`: **PASS** (31 questions, 0 overlap).
- q20 and q22 got `space: 160` for the lines the verifier's clarifications added.
- **Page numbers: all 15 pages show theirs.** `python tools/qa/check_folio.py jpfm08` ends
  `ok all 15 pages show their page number`.
  - p5 was the one broken page: its folio box (x 536.4-541.4, y 798.9-815.5) sits under the q27
    dimension line, so the printed "5" never reached the page image. The glyph was lifted from the
    "15" on p15 (5.0 x 16.6 pt, same font and size) and pasted into the measured blank strip below the
    footer at x 536.4-541.4, y 821.0-837.6, on `pages/p05.jpg` (JPEG q95, subsampling 0).
  - The hand-placed box is recorded in `books/jpfm08/folio.json`
    (`{"5": [536.4, 821.0, 541.4, 837.6]}`) so `check_folio.py` measures it there and does not fall
    back to the text layer.
  - This check is now part of the standing QA gate: see `docs/05-engine-notes.md` -> "Page numbers"
    and `.cursor/skills/build-ebook/SKILL.md` -> "6. QA". Run it on every book after any engine
    change and whenever a book's page images or `layout.json` are rebuilt.
