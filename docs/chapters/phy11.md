# PHY CH11 Projectile Motion (`phy11`)

| | |
| --- | --- |
| Form | S4 |
| Book id / storage | `phy11` (never rename) |
| Source | `books/phy11/source/` QUE (10 pages), ANS (10 pages, offset 0) |
| Status | draft |
| Live | `reader.html?book=phy11` |

## Source facts

- Page structure: p1 concept notes (Resolving velocity; Horizontal projectile motion), p2 Q1–Q4, p3 Q5–Q7,
  p4 concept panel (Projectile motion with an angle) + Q8, p5 Q9–Q11, p6 Q12–Q13, p7 concept panel
  (Horizontal Range R) + Q14–Q16, p8 Q17–Q18, p9 Q19, p10 Q20. No cover page.
- Q5 and Q7–Q20 are free-response even though the section is "MC": only Q1–Q4, Q6, Q9, Q14–Q16 are MC
  with a printed answer square at the right margin.
- Q17's wording is printed as an image (only "17." is selectable text), so review links are impossible there.
- MC answers from the ANS: q1 C, q2 C, q3 B, q4 B, q6 C, q9 B, q14 B, q15 B, q16 B.
- The key mixes the value of g: Q1 uses 9.8, Q12 and Q16 use 10, the rest use 9.81. The teacher asked for
  g = 9.81 throughout, so Q12 and Q16 are recomputed with 9.81 (Q12: t = 1.55 s, v = 13.4 m s⁻¹;
  Q16: t = 5.46 s, R = 162 m, which is the printed option B — the key's own 159 m came from g = 10).
  Q1 keeps the key's 9.8: 0.784 m still rounds to the printed 0.78 m.

## Question map

| Section | Questions | Pages | Notes |
| --- | --- | --- | --- |
| mc | q1–q20 | 2–10 | one section for the whole chapter |

## Special cases

- `extract.overrides`: a `region` for all 20 questions, plus `square` for the nine MC squares, plus `space`
  for the 18 questions whose answer is taller than the printed blank band. Regions stop short of each
  printed figure; where a figure blocks the upper part of the band (q4, q5, q7, q8, q9, q11, q18) the answer
  moves to the blank area under the figure to keep full width.
- `space` opens the printed page under the region, so every answer shows whole without scrolling.
  **Every region ends at y ≤ 790**: the printed footer row ("警告: 不可翻印…") starts at 797.6, and a region
  that reached into it (the first pass used 812) let the answer run over the footer text, because the page
  image is cut at the region's bottom edge and anything above the cut does not move down.
  The cut must also land in a **free gap between printed rows**: a bottom edge inside a row (q3 at 596 cut
  through q4's first line, q4 at 812 through the footer, q16 at 790 through option D) torn that line in two.
  q3 now ends at 526, q4 at 790, q16 at 731–745; option D of q16 moves down whole with the opened page.
- **p7 is printed 150 pt taller** (`source/…(p7 opened) @Uni.pdf`, made with
  `tools/relayout_pdf.py --page 7 --at 796.8 --add 150`). The cut sits in the 1.3 pt gap between option
  D's ink (ends 796.3) and the footer (starts 797.6), so nothing printed moves except the footer.
  Page height 841.9 → 991.9; the book needs the engine's per-page height support.
- `space` cuts must also land in a measured blank gap: q14's cut is at **550** (blank rows 546.7–558.7),
  because 540 sliced option D's fraction in two. q15's cut at 682 is clear.
- q16 sits to the right of its options (`region` [150, 731, 505, 930]) and uses the blank opened in the
  PDF — no `space`, no scrolling.
- Q18 (a)(1) is a drawing task on the printed grid of Figure 4.2; the solution states what to mark
  (equal horizontal steps of 0.05 m) because the marks themselves are made in ink on the page.

## Graphics

| Question | Graphic | Notes |
| --- | --- | --- |
| q14 | `widgets.js` → `q14` | trajectory picture: sliders for `u` and `θ`, live `R = u²sin2θ/g`, apex and landing marked, quick buttons 45°, 30°, 60° |

## Review links

12 links over 12 questions (q17 skipped: its wording is an image, no selectable text; q1, q14 have no
wording that maps to one step). Each `q` phrase is copied word for word from the printed page
(ASCII `ms-1`, letter `o` for degrees) and every link has a marked answer part:

| Question | key | `q` phrase | colour | answer side |
| --- | --- | --- | --- | --- |
| q2 | `h` | 50 m tall | blue | `lk` on the `50 = ½gt²` step |
| q4 | `x0` | At what speed is it projected | blue | `lk` on `∴ (1.0) = u(0.404)` |
| q4 | `y0` | vertically below its point of projection | pink | `lk` on `∴ (0.8) = ½(9.81)t²` |
| q5 | `drop` | 1 m below the nozzle | amber | `lk` on `s_y = ½(9.81)t² = 1` |
| q8 | `t08` | 0.8 s after | blue | `lk` on `t = 0.8 s` |
| q10 | `target` | 18 m away from him | amber | `lk` on `17.2 m < 18 m` |
| q11 | `hoop` | 3.05 m high | blue | `lk` on the height equation |
| q12 | `h14` | height of 1.4 m | pink | `lk` on `−1.4 = vt sin30° − ½(9.81)t²` |
| q13 | `d210` | 21.0 m away | blue | `lk` on `21.0/0.714` |
| q15 | `r5` | 5 m away from the pool side | amber | `lk` on `5 = v²sin2(30°)/9.81` |
| q16 | `a42` | angle 42o | blue | `lk` on `u_y = 40 sin42°` |
| q19 | `u15` | 15 ms-1 | blue | `lk` on `u_x = 15 m s⁻¹` |
| q20 | `h100` | height 100 m | pink | `lk` on `s_y = 100 m` |

The matcher only searches the printed rows under a question's anchor, so q4's two links use the second
printed line: "1.0 m away" and "0.8 m" sit in the question's own anchor row and are not found.

## Feedback log

| Date | Request | What changed |
| --- | --- | --- |
| 2026-11-19 | Chief: skeleton (book.json, pages, layout, ANS crops, squares) | took over stage 3 |
| 2026-11-19 | own pass | wrote 20 solutions from `reference/ans_pages/`; added 20 regions + `space`; fixed the q14 widget crash and the q13 side-reason TeX |

## Known warnings

`node tools/qa/check_book.mjs phy11 --shots` → **0 FAIL，8 WARN**. Accepted warnings:

- seven questions still set one unbreakable line at 50–62 % (q4, q7, q8, q11, q13, q16, q18) — the line is a
  long `\text{}` sentence or a substituted equation; splitting it would break the teacher's single step;
- q13: one side reason drops under its step instead of beside it (no room at that width).
- Step buttons: the strip (`▸ » ◂ ↺`) now keeps its own column at the region's right edge, clear of the
  working. Fixed in the engine on the teacher's instruction (`placeCtl()` in `engine/viewer/answers.js`):
  the strip was placed after the ink until the fallback left it at x = 0, on top of the first lines,
  because `figureLeft()` scanned the grown region band (with authored `space`) and took the next question's
  printed text for a figure. It now scans only the printed band, and the answer never uses the strip's
  column (`answerRight()`).
