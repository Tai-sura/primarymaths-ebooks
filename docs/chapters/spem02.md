# spem02 — Electric Circuits (SPEM02)

- **book id**: `spem02` (never rename: it is the pen-ink storage key on every iPad)
- **form**: S5   **code**: SPEM02   **title**: Electric Circuits   **topic**: E and M (Circuit)
- **source**: 20-page QUE + 20-page ANS, both A4 595.3 x 841.9 pt, text layer present
- **ansPageOffset**: **0** (verified 2026-11-21: ANS page N carries the same running head and
  the same question numbers as QUE page N; the template default of -1 is wrong here)
- **status**: stage 2 done 2026-11-21 — pages rendered, questions listed, ANS crops taken;
  stage 3 started 2026-11-21 — `solutions.js` has q1–q2 (Current section)

## Sections

Section headings are the boxed titles printed in the notes (`extract_pages.py --scan` finds them,
confirmed on the page images):

| id | label | pages | questions |
| --- | --- | --- | --- |
| `current` | Current | 1 | q1–q2 (2) |
| `voltage` | Voltage | 1 | q3 (1) |
| `resistance` | Resistance | 2–4 | q4–q11 (8) |
| `network` | Resistor network | 5–13 | q12–q39 (29) |
| `rheostat` | Rheostat | 14–15 | q40–q45 (6) |
| `potential` | Electric potential in a circuit | 16 | q46–q48 (3) |
| `measurement` | Measurement of resistance | 17 | q49–q50 (2) |
| `internal` | Internal resistance | 18–20 | q51–q57 (7) |

## Question map

- **58 questions on 20 pages**, printed numbers **1–57**: the number **33 is printed twice**, on
  two different questions, so the second one gets the id **`q33b`** (label still "33"):
  - `q33` — p11, "Two cells of negligible internal resistance are connected with two resistors …"
    (MC, potential difference between X and Y);
  - `q33b` — p12, "Find the resistance between terminals m and n in the following network."
- Per page: p1 3, p2 1, p3 3, p4 4, p5 1, p6 1, p7 4, p8 2, p9 5, p10 4, p11 5, p12 3, p13 4,
  p14 3, p15 3, p16 3, p17 2, p18 3, p19 3, p20 1.
- The scan also reported four false hits on p19 (`q2`, `q4`, `q8`, `q16`) — numbers inside the
  question text, not new questions; they were dropped.
- **No printed worked examples** in this chapter: every question has blank working space.
- `layout.json` anchors: all 58 questions found, no page without a question, no `MISSING ANCHOR`.

## Answer regions

The default region (from the bottom of the printed text to the next question) is **36 pt** for
sixteen questions: q20, q21, q22, q24, q29, q32, q33, q37, q38, q42, q47, q48, q50, q51, q52, q54.
Most are MC where the working space is beside the options, so they need an explicit
`extract.overrides.<q>.region` (plus `square` for the printed MC box). No page needs the PDF opened
up: the chapter has no question that runs into the footer.

## ANS crops

`reference/ans/` holds 64 crops from the 20 ANS pages; `reference/ans_pages/` holds the full-page
previews. `ansPageOffset` 0 held for every page (no mismatch found).

## QA

`check_book.mjs` used to crash on a book with no solutions (no `.qa .abox`, null at
`check_book.mjs:332`). Chief fixed it on 2026-11-21: it now reports a WARN and skips the finger-tap
test, so a half-written book still gets a report.

`node tools/qa/check_book.mjs spem02` with q1–q2 written (2026-11-21):

- **q1, q2: no FAIL.** q1 has 1 WARN — see the region defect below;
- **56 FAIL**, all "listed in `book.json` but has no entry in `solutions.js`" (q3–q57 + `q33b`).

Static checks (stage 2): 58 questions in `book.json` ↔ 58 in `layout.json`; every page has a
question; 16 default regions are 36 pt (listed above) and need overrides.

## Region defects found while writing q1–q2 (handed to layout-engineer 2026-11-21)

Both are `book.json` `extract.overrides` work, not solution work. Chief passed them to
layout-engineer on **2026-11-21**, together with the sixteen 36 pt regions listed above.

1. **q1** — region `[66, 308.6, 546, 352.1]` is only 43.5 pt tall; the teacher's answer needs about
   200 pt, so the answer scrolls (WARN: "157 pt more would show it all"). It needs `space` to open
   p1 — that makes p1 taller than A4, so it is a user-facing decision.
2. **q2** — region `[66, 399.4, 546, 723.4]` was derived to the next anchor (`q3` at 733.4) and so
   swallows the whole printed **Voltage** concept box. The answer steps are painted over that box
   and the "Voltage" heading. The region must stop above the box (≈ 430 pt) and the rest must not be
   used as working space. `check_book` does **not** flag this (there is no overflow, the box is
   enormous), it was only visible in `sheet-01-p1.png`.

**Status 2026-11-21**: all of them are fixed and QA clean. q1–q4 now carry `space` 200 / 90 / 92 / 160
and q2's region was recut to `[66, 395, 546, 450]`; q5 / q6 got `space` 210 / 220 and q4's region was
moved below the printed (a)/(b). Every `space` was followed by a re-run of `extract_pages`. The same
pattern (tiny region, or a region that swallows a printed concept box / the question's own text)
recurs all through this book, so check the `sheet-*.png` shot, not just the WARN list — `check_book`
cannot report an overlap when the region is generous. Open at the time of writing: **q9** (84 pt
region, 266 pt short) and **q10** (74 pt, 125 pt short) — see the progress table.

## Known to-dos outside this log

- **`books/spem02/widgets.js`** still holds the skeleton example (`q1` = the green/blue marbles
  slider). It puts a graphic button on q1 that has nothing to do with this book. **Chief will clear
  it himself** (he maintains `widgets.js`); ebook does not touch that file.

## Solutions progress

| batch | questions | status | final answers |
| --- | --- | --- | --- |
| 1 (2026-11-21) | q1 | written | `300 C`; the key's extra question "Number of electron?" → `N = 300/(1.6×10⁻¹⁹) = 1.875×10²¹` (kept, it is the teacher's own extra) |
| 1 (2026-11-21) | q2 | written | `4.5 h` |
| 2 (2026-11-21) | q3 | written | `4 C` (12 J ÷ 3 V) |
| 2 (2026-11-21) | q4 | written | (a) `0.5 Ω` (slope, at 10 A / 5 V); (b) `R_Y = 0.25 Ω`, sketch = straight line from the origin, half the slope of X, through (20 A, 5 V) |
| 3 (2026-11-21) | q5 | written (MC) | **D** — `ΔR = 2/5 − 1/1 = −0.6 Ω`, so the resistance decreases by 0.6 Ω |
| 3 (2026-11-21) | q6 | written (MC) | **C** — 12 V/3 A → 4 Ω (A true); 14 V/7 A → 2 Ω (B, D true); at 5 A, V = 13 V → 2.6 Ω ≠ 0.5 Ω, so C is the incorrect statement |
| 4 (2026-11-21) | q7 | written (2 marks) | V↑ → I↑ → filament temperature↑ → `R`↑; alternative wording: electrons collide with the increasingly vibrating atoms / lattice ions, which impede their flow |
| 4 (2026-11-21) | q8 | written | `A = π(0.0005)² = 7.854×10⁻⁷ m²`; `5.60×10⁻⁴ = ρ·2/π(0.0005)²` → `ρ = 2.20×10⁻¹⁰ Ω m` |
| 5 (2026-11-21) | q9 | written | (a) `ρ = 6.73×10⁻⁷ Ω m`; (b) length halved → `R = 0.3 Ω`, resistivity unchanged `6.73×10⁻⁷ Ω m` |
| 5 (2026-11-21) | q10 | written | one strand: `R/l = ρ/A = 2.6×10⁻⁸/1.3×10⁻⁵ = 2.0×10⁻³ Ω m⁻¹` → `2.0 Ω km⁻¹` |
| 6 (2026-11-21) | q11 | written | same length → `A ∝ m` → `R ∝ 1/m`; `R_A/R_B = m_B/m_A = 9/4` → `R_A : R_B = 9 : 4` |
| 6 (2026-11-21) | q12 | written | four circuits, one line each: (a) `3 V/8 Ω = 0.375 A`, (b) `3/2 = 1.5 A`, (c) `1.5/8 = 0.1875 A`, (d) `1.5/2 = 0.75 A` |
| 6 (2026-11-21) | q14 | written | resistors in parallel across 6 V: `I₁ = 6/1 = 6 A`, `I₂ = 6/2 = 3 A` |
| 6 (2026-11-21) | q15 | written | (a) `(2+2)∥(2+2) = 2 Ω`; (b) `2∥(2+2+2) = 1.5 Ω` |
| — | **q13** | **BLOCKED** | the ANS page 6 is **blank** (no answer anywhere for the eight parts (a)–(h)); the computed values are in the book for now, waiting for the user's decision — see below |
| 7 (2026-11-21) | q16 | written | (a)(i) `3+6 = 9 Ω`; (ii) `I = 9/9 = 1 A`, `V₆ = 6 V`; (b)(i) `1/(1/3+1/6) = 2 Ω`; (ii) `9/6 = 1.5 A`; (iii) `9/2 = 4.5 A` |
| 7 (2026-11-21) | q17 | written | (a) `8+(6∥12) = 12 Ω`; (b) `1 A`; (c) `8 V`; (d) `4 V`; (e)(i) `4/6 = 0.667 A`; (ii) `4/12 = 0.333 A` |
| 7 (2026-11-21) | q18 | written | (a) `1/R_ABC = 1/3+1/6 → 2 Ω`, total `2+4 = 6 Ω`; (b) `I_D = 1.5 A`, `V_C = 1.5×2 = 3 V`; (c) `I_A = 3/3 = 1 A`; (d) `E` in parallel with `C` → total R falls → `I_D` increases |
| 8 (2026-11-21) | q19 | written | (a) `R₃∥R₄ = 1.5`, `R_AD = 4.5 Ω`; (b) `R₂∥1.5 = 1`, `R_AD = 4 Ω`; (c) `I = 3 A`, `V_R1 = 9 V`; (d) `V_AC = 12 V` |
| 8 (2026-11-21) | q20 | written (MC) | **A** — series: `I` ratio `1:1:1`, `V` ratio `1:2:3` |
| 8 (2026-11-21) | q21 | written (MC) | **D** — parallel: `V` ratio `1:1:1`, `I` ratio `1/2:1/3:1/4 = 6:4:3` |
| 9 (2026-11-21) | q22 | written (MC) | **D** — equal p.d.: `(1)(2R) = I₂R → I₂ = 2 A`, `I₃ = 1+2 = 3 A` |
| 9 (2026-11-21) | q23 | written (MC) | **C** — `I = 10/(8+2) = 1 A` |
| 9 (2026-11-21) | q24 | written (MC) | **C** — two 6 Ω in parallel `R' = 3 Ω`, `I = 0.3×2 = 0.6 A`, `V = 0.6(3+12) = 9.0 V`. (The key prints `1/6+1/6+1/6 = 1/3`; the circuit has **two** 6 Ω branches, so `1/6+1/6 = 1/3` is the right line and 3 Ω stands.) |
| 10 (2026-11-21) | q25 | written (MC) | **B** — `I = 1+I₂`; `3I₂+(1+I₂)6 = 12`; `9I₂ = 6`; `I₂ = 2/3 A` |
| 10 (2026-11-21) | q26 | written (MC) | **B** — `R = 4+(4×4)/8 = 6 Ω`; `I_XY = 0.5 A`; `V_XY = 3(0.5) = 1.5 V` |
| 10 (2026-11-21) | q27 | written (MC) | **B** — `R_XY = r/2`; `R_lower = 3r/2`; `I = 6/r`; `V_XY = 3.0 V` |
| — | **q28** | **BLOCKED** | the key has only the letter **B**; its working is an illegible photo. Under the wiring visible in Fig (a) the voltmeter carries no current in the top branch, so `V_a = E = 8 V`, and Fig (b) then gives `E/2 = 4 V` = option **A**, not B — needs the teacher's arbitration. See below. |
| 11 (2026-11-21) | q29 | written (MC) | **B** — a zero variable resistor short-circuits the bulb: all the current goes through it, none through the bulb |
| 11 (2026-11-21) | q30 | written (MC) | **B** — `S` open: `6 × r/(r+r) = 3 V`; `S` closed: voltmeter across the battery = `6 V` |
| — | q31–q57 + `q33b` (28) | **not written** | by batch |

QA after batch 6 (`--verbose`): **q1–q12, q14, q15 have 0 FAIL**; only **q13** still has no entry (see
below). Two WARNs, both plain scrolling:

- **q14** — region `[66, 126.4, 376, 194.4]` (68 pt) for 4 steps; **62 pt more**.
- **q15** — region `[66, 241.3, 306, 331.3]` (90 pt) for 3 steps; **39 pt more**.

QA after batch 7 (`--verbose`): **q1–q18 have 0 FAIL**. Two WARNs, both plain scrolling:

- **q17** — region `[66, 730.6, 388, 816.6]` (86 pt) for 6 steps; **69 pt more**.
- **q18** — region `[66, 216.3, 364, 408.3]` (192 pt) for 7 steps; **20 pt more**.

q13's eight computed values were checked against the figures by Chief the same day; they stay in the
book pending the user's decision.

QA after batch 11 (`--verbose`): **q1–q27, q29, q30 have 0 FAIL** (q28 blocked, see below). WARNs,
all plain scrolling, Chief fills them with `space`:

- q22 17 pt · q26 84 pt · q27 167 pt · q29 132 pt · q30 131 pt.

## q28 has no usable key (blocked 2026-11-21)

The ANS marks the answer **B** but its working is a photograph of the 2020 DSE paper and is not
legible at any zoom. Reading the printed Fig (a): the voltmeter sits in the top branch in series with
a resistor, so no current flows through that resistor and the voltmeter sees the whole battery,
`V_a = E = 8 V`. In Fig (b) the same battery then puts the middle junction at `E/2 = 4 V`, which is
option **A** — contradicting the key's B. Either the wiring in the printed figure or the key letter
is wrong, so this one waits for the teacher instead of being guessed.

## q13 has no answer in the key (reported 2026-11-21)

`q13` (p6) is "Find the equivalent resistance across A and B in each case" with **eight** circuits
(a)–(h). The ANS page 6 was checked at full size twice: it is the printed question page with **no red
box, no handwriting, no answer of any kind**. `extract_ans_refs.py` likewise produced no crop for p6.
So there is nothing to follow, and writing answers from my own working would break the rule that the
ANS key is the only authority.

For reference, the eight answers by ordinary series/parallel working are (a) 4 Ω, (b) 6 Ω, (c) 4R,
(d) 60R, (e) 1 Ω, (f) R, (g) 6 Ω, (h) 2 Ω. They are waiting for Chief / the teacher to confirm before
they go in the book.

Reminder: **after changing a `space` you must re-run `tools/extract_pages.py <id>`** — the reader
reads the merged value in `layout.json`, not `book.json`.

## Open points for the teacher / Chief

1. **Printed number 33 appears twice** (p11 and p12, different questions). The e-book keeps both as
   `q33` and `q33b`; if the notes are ever reprinted, one of them should be renumbered.
2. Section id `network` covers 29 questions over nine pages (p5–p13); if the teacher wants finer
   jumps ("series and parallel", "combination"), the headings for those are not printed in the notes.

## Batches 12-18 (2026-11-21): q36-q57 written

| batch | questions | final answers |
| --- | --- | --- |
| 12 | q36 | (a) `12/3 = 4 Ω`; (b) `1/R = 1+1+1+1/2 → R = 2/7 Ω` |
| 13 | q37, q38, q39 | q37 **B** (`6×12/(6+12) = 4 Ω`); q38 **A** (`R_XY = 6 Ω`, `I = 2 A`, `I_R = 0.4 A`); q39 **A** (`2×2/(2+2) = 1 Ω`) |
| 14 | q40, q41, q42 | q40 connect `A` and `C`; (1) to `B`, (2) to `A`; q41 **B** (`R_p = 3.33 Ω`, `V_AX = 4.0 V`); q42 **A** (`R = 40 Ω`, rheostat `30 Ω`, `PX:XQ = 3:2`) |
| 15 | q43, q44, q45 | q43 **C** (ideal voltmeter reads the battery, constant 3 V); q44 **C** (decreases then increases); q45 **A** (`A₁ ↓`, `A₂ ↑`, `A₃ ↓`) |
| 16 | q46, q47, q48 | q46 (a) `1.2 A` (b) `−3.6 V` (c) `2.4 V` (d) `8.4 V`; q47 **D** (`+2 V` → `+3 V`); q48 **D** |
| 17 | q49, q50, q51, q52, q53 | q49 **D** ((2)(3) only); q50 **C** ((1)(2) only); q51 **A** (`R = 15 Ω`, `r = 2 Ω`, `V₆ = 1.8 V`); q52 **B** (`R = 2 Ω`, `V_term = 6 V`, `I₆ = 1 A`); q53 **A** (`R_X = 38 Ω`) |
| 18 | q54, q55, q56, q57 | q54 **B** (`r = 4.04 Ω`); q55 **C** (`r = 6 Ω` only for `I = 2.4 A`); q56 (a) `V = ε − Ir` (b) `ε = 1.6 V`, `r = 4 Ω`; q57 (a) `21.6 V` (b) `0.5 Ω` (c)(i) `R_eq = (1/6+1/R_V)⁻¹` (ii) `R_V = 360 Ω` (iii) `r = 0.156 Ω` |

**q48 note**: the ANS marks D, and the printed option D really does say the current through R₂
*increases*; closing S adds a parallel path, so the p.d. across R₂ falls and its current falls, which
makes D the incorrect statement. Earlier doubt came from the key's paraphrase ("should decrease"), not
from the book.

All 58 questions now have an entry. Final QA (2026-11-21): **0 FAIL, 3 WARN**. q54 / q55 were fixed
with `space` 65 / 170. The two left are **region** problems, handed to layout-engineer — not writing
length:

- **q48** — region `[245, 727, 384, 758]` is 139×31 pt; even after shortening every line to 14–23
  characters the widest still shrinks to 67 %, and the six lines need 209 pt more height.
- **q51** — region `[306, 415, 426, 483]`; its six short lines fit at full size but still want 6 pt
  more height.

Both answers are complete and correct; only the boxes are too small. Chief is finding wider positions.
## Display fixes 2026-11-21 (q19, q25, q36)

- **q36** — the two long `t()` sentences were folding in the 270 pt column, and `\underline{\tfrac{2}{7}}`
  drew the underline through the fraction. Now: three short text lines for (a); (b) reads
  `The network is four paths in parallel:` followed by an independent math line `1∥1∥1∥2`; the answer
  is `\underline{2/7\ \Omega}` (slash form, matching the key).
- **q25** — `\underline{\tfrac{2}{3}\ \text{A}}` → `\underline{2/3\ \text{A}}` (same fault).
- **q19** — `t()` with a `\parallel` chain (`$R_3\parallel R_4$`) → plain text `the pair $R_3,R_4$`.
- Whole-book sweep for `\underline{\tfrac…}` / `\underline{\frac…}` / `\parallel` inside `t()`: only
  these three lines were affected.

`check_book spem02 --shots` after the fixes: **0 FAIL, 0 WARN** (q48 and q51 became clean once
layout-engineer widened their regions).