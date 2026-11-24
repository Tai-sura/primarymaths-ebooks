# Verification reports

| book | scope | verdicts | per-question files |
|---|---|---|---|
| phy11 (PHY CH11 Projectile motion) | 20 / 20 | 16 PASS, 2 MISMATCH, 2 UNVERIFIABLE | `books/phy11/reference/verify/q1.md`…`q20.md` |
| phy06-force2 (PHY CH6 Force II) | 35 / 35 | 34 PASS, 0 MISMATCH, 2 UNVERIFIABLE items (q16(a), q29(a)(b)) | `books/phy06-force2/reference/verify/q1.md`…`q35.md` |

## phy11 — PHY CH11 Projectile motion (S4)

- verified: 2026-11-20
- verifier: independent recomputation in Python 3.12.14, sympy 1.14.0, pint 0.26.2
- read: `books/phy11/solutions.js`, `books/phy11/book.json`, `books/phy11/reference/ans_pages/ans_02.png`…`ans_10.png` (and spot-checked crops under `reference/ans/`)
- written: `books/phy11/reference/verify/q1.md`…`q20.md` and this file. No other file was touched: `solutions.js`, `book.json`, `layout.json`, `engine/`, `widgets.js` are unchanged.
- method: every numeric figure in `solutions.js` (final answers and intermediate steps) was recomputed from the question's own data; quadratics solved exactly with sympy; algebraic results simplified with sympy; every unit and formula dimension checked with pint. Comparison band 0.5% relative (3 s.f. convention), with g taken per question from the ANS key.

### Result summary

| qid | answer in solutions.js | verdict | key numbers (claimed vs recomputed) |
|---|---|---|---|
| q1 | C (0.78 m) | **PASS** | 0.784 m vs 0.7840 m (0.000%) |
| q2 | C (31.9 m) | **PASS** | 31.9 vs 31.9275 m (0.086%) |
| q3 | B (1.08 s) | **PASS** | 1.08 vs 1.0788 s (0.111%) |
| q4 | B (2.5 m s⁻¹) | **PASS** | 2.5 vs 2.47614 m s⁻¹ (0.964%, printed option) |
| q5 | 55.8° below horizontal | **PASS** | 55.8° vs 55.8908° (0.162%); v 5.33 vs 5.34977 m s⁻¹ |
| q6 | C (1)&(3) correct | **UNVERIFIABLE** | non-numeric; statements checked, C confirmed |
| q7 | (a) 0.143 s (b) 14.0 m s⁻¹ | **PASS** | 0.143 vs 0.142784 s; 14.0 vs 14.0071 m s⁻¹ |
| q8 | 11.3 m ; 8.17 m | **PASS** | 11.3 vs 11.3137 m; 8.17 vs 8.17451 m |
| q9 | B (2.92 s) | **MISMATCH** | answer 2.92 vs 2.92369 s PASS; rejected root −1.29 vs −1.39463 s (7.5%) |
| q10 | (a) 1.53 s (b) 17.2 m < 18 m | **PASS** | 1.53 vs 1.52563 s; 17.2 vs 17.1760 m |
| q11 | (a) 0.884 s (b) 1.81 m | **PASS** | 0.884 vs 0.884358 s; 1.81 vs 1.81481 m |
| q12 | (a) 1.55 s (b) 13.4 m s⁻¹ | **MISMATCH** | ANS g = 10 → 1.54 s / 13.5 m s⁻¹; solutions.js g = 9.81 → 1.55 / 13.4 (0.93% / 0.99%) |
| q13 | (a) 0.714 s … (e) 30.2 m s⁻¹ at 13.4° | **PASS** | 0.714 vs 0.713922 s; 30.2 vs 30.2373 m s⁻¹; 13.4 vs 13.3925° |
| q14 | B (400sin60°/g) | **PASS** | sympy difference to u²sin2θ/g = exactly 0 |
| q15 | B (7.53 m s⁻¹) | **PASS** | 7.53 vs 7.52583 m s⁻¹ (0.056%) |
| q16 | B (162 m) | **PASS** | 162 vs 162.205 m (0.127%); ANS's own g = 10 working gives 159 m, not an option |
| q17 | (i) 1.42 s (ii) 15.1 m | **PASS** | 1.42 vs 1.41890 s; 15.1 vs 15.1248 m |
| q18 | (a)(2) 1.78 m s⁻¹ | **PASS** | 1.78 vs 1.77541 m s⁻¹ (g = 9.78); (a)(1) graphical |
| q19 | (a) 9.81 (b) 60 m, 78.48 m (c) 42.0 m s⁻¹ (d) 69.1° | **PASS** | all exact; 42.0 vs 42.0093 m s⁻¹ |
| q20 | (a) 5.87 s (b) 23.6 m s⁻¹ (c) 50.2 m s⁻¹ | **PASS** | 5.87 vs 5.87470 s; 23.6 vs 23.5866; 50.2 vs 50.1829 |

Counts: 16 PASS, 2 MISMATCH (q9, q12), 2 UNVERIFIABLE (q6, q18 drawing/worded part). 62 individual numeric checks were run against the questions' own data; 61 pass and 1 fails (the q9 rejected root). q12's mismatch is not a failed recomputation — both of its numbers are right for their own g; the conflict is that solutions.js and the ANS use different g for the same question.

### Mismatches to fix

#### q12 — g convention differs from the ANS (needs a decision)

The ANS solves this question with ½ × (−10) × t², i.e. g = 10:

```
-1.4 = 18tan30° - 5t²  ->  t² = 2.35846  ->  t = 1.5357 s ≈ 1.54 s
v = 18 / (1.5357 × cos30°) = 13.534 ≈ 13.5 m s⁻¹
```

`solutions.js` instead uses ½(9.81) = 4.905:

```
4.905t² = 18tan30° + 1.4  ->  t = 1.5505 s ≈ 1.55 s
v = 18 / (1.5505 × cos30°) = 13.405 ≈ 13.4 m s⁻¹
```

Each is internally consistent; the problem is that the book claims to follow the teacher's working. The house rule is to take g per question from the ANS, so the solution should read **1.54 s** and **13.5 m s⁻¹** (g = 10) — or, if 9.81 is deliberately preferred here, say so in one line so the 1.55 s / 13.4 m s⁻¹ does not look like an error.

#### q9 — rejected root mis-stated (answer unaffected)

`4.905t² − 7.5t − 20 = 0` has roots 2.92369 s and **−1.39463 s**. `solutions.js` prints "t = −1.29 s (reject)", and the ANS key prints the same wrong value. Substituting t = −1.29 back gives −17.84 m, not −20 m, so the figure is arithmetically impossible. The answer 2.92 s (option B) is correct and needs no change; only the discarded root should become −1.39 s.

### Notes that are not solution errors

- **q16**: the ANS's own red box works with g = −10 m s⁻² → t = 5.353 s, R = 159 m, but 159 m is not among the printed options (A 177, B 162, C 88.5, D 35.8). The ticked letter B corresponds to 162 m, which requires g = 9.81 — that is what `solutions.js` does, so the solution is right and the key's arithmetic is the loose end. Worth mentioning to whoever owns the source key.
- **q5**: the 5.33 m s⁻¹ comes from re-using the rounded v_y = 4.41; the unrounded chain gives 5.34977 m s⁻¹ (0.37%, inside the band). It also matches the ANS box exactly. Optional polish only.
- **q4**: 2.5 m s⁻¹ is 0.96% from the exact 2.47614, because option B is printed to 2 s.f. This is a rounding of the printed option, not an error.
- **q18**: g = 9.78 is unusual but is what the ANS uses and what its strobe timing (0.05 s × 3) implies — leave it.

### Units and dimensions (pint 0.26.2)

| formula | dimension produced | expected | result |
|---|---|---|---|
| R = u²sin2θ/g | meter | m | OK |
| v = u + at | meter/second | m s⁻¹ | OK |
| s = ut + ½at² | meter | m | OK |
| v² = u² + 2gh | meter²/second² | m² s⁻² | OK |
| v_y = gt | meter/second | m s⁻¹ | OK |

All answer units in `solutions.js` are written as m s⁻¹, m, s, °, matching the ANS convention. No dimensional mismatch found.

### Not verifiable

- **q6** — conceptual (statements (1)(2)(3)); recomputation of a number does not apply. Reasoning checked: (1) true, (2) false, (3) true → C, same as the boxed answer.
- **q13(f)** — worded effect of air resistance; reasoning agrees with the ANS (larger angle).
- **q18(a)(1)** — plotting positions on Figure 4.2 is a drawing task; the numeric part (a)(2) was verified.
- **q18(b)** — worded explanation of terminal speed; reasoning agrees with the ANS (drag = weight → zero net force → constant speed).

Nothing else in the book is unverifiable: all 20 questions have a computable answer except the graphical/worded parts listed above.

### Reproducibility

The recomputation script and its library bootstrap live outside the book, in the session scratch folder at the workspace root (`.tmp-verify/`), not inside `ebook-engine`. To re-run: `python bootstrap.py` once (fetches the sympy/pint wheels and unpacks them), then `python recompute.py` with that folder first on `PYTHONPATH`. Every number above is printed by that run.

### Confidence

- Arithmetic and algebra: high — every value comes from an exact sympy solution or a directly reproducible closed form, and each is shown above with its relative difference.
- g-value judgement: high for the per-question g actually written in the ANS (9.8 q1; 9.81 q2–q11, q13, q15, q19, q20; 10 q12 and q16's working; 9.78 q18).
- Answer letters: high for q1, q2, q3, q4, q6, q9, q14, q15, q16 — each was read from the printed option list in the ANS pages, not inferred from the working.
- Lowest-confidence item: q16 (because the ANS key contradicts its own ticked option). Reported as two separate facts rather than resolved by guesswork.

## phy06-force2 — PHY CH6 Force II (q1–q17)

- verified: 2026-11-21
- read: `books/phy06-force2/solutions.js` (q1–q17), `book.json`, `reference/ans/p01_01.png`…`p05_04.png` (18 crops), `pages/p01.jpg`–`p05.jpg` for the question data and the two grids
- written: `books/phy06-force2/reference/verify/q1.md`…`q17.md` and this file. No other file was touched: `solutions.js`, `book.json`, `layout.json`, `engine/`, `widgets.js` are unchanged.
- method: every figure recomputed from the question's own data, not from the book's formula; g = 9.81 m s⁻² (book rule); sympy for the simultaneous-equation force balances (q9, q10); pint for dimensions; q16 and q17 grids measured from the page pixels rather than counted by eye.

| qid | answer in solutions.js | verdict | key numbers (claimed vs recomputed) |
|---|---|---|---|
| q1 | Fx 8.66 N, Fy 5.00 N | **PASS** | 8.66 vs 8.66025; 5.00 vs 5.00000 |
| q2 | (a) 3.88/14.5 (b) 82.1/22.0 (c) 52.1/295 | **PASS** | all six within 0.150% (worst 295 vs 295.442) |
| q3 | A (11.5 N) | **PASS** | 11.5 vs 11.5470 (0.407%) |
| q4 | C (15.1 N) | **PASS** | 15.1 vs 15.0628 (0.247%) |
| q5 | C (S49.9°W) | **PASS** | 49.9° vs 49.9306° (0.061%) |
| q6 | D ((4)(2)(1)(3)) | **PASS** | 1 < 2.125 < 4.635 < 5; no ANS box |
| q7 | B (50 N) | **PASS** | 50 vs 50.000; no ANS box |
| q8 | A (10 N) | **PASS** | 10 vs 10.000 |
| q9 | T1 86.6 N, T2 50 N | **PASS** | 86.6 vs 86.6025; 50 vs 50.000 |
| q10 | (a) 39.24 N (b) 36.9 N, 13.4 N | **PASS** | 39.24 vs 39.2400; 36.9 vs 36.8735; 13.4 vs 13.4209 |
| q11 | 8.5 N | **PASS** | 8.5 vs 8.45237 (0.564%, 2 s.f. display) |
| q12 | 159.6 N | **PASS** | 159.6 vs 159.627 (0.017%) |
| q13 | 76.6 N, 766 m s⁻² | **PASS** | 76.6 vs 76.6044; 766 vs 766.044 |
| q14 | 0.858 m s⁻² | **PASS** | 0.858 vs 0.858264 (0.031%) |
| q15 | (b) 1.73 m s⁻² | **PASS** | 1.73 vs 1.72977; (a) worded |
| q16 | (b) 7.07 N | **PASS** | (5,5) from grids → 7.07107 N, 45.000°; (a) drawing |
| q17 | B (5.4 N, lower-left) | **PASS** | (5,2) grid sum → 5.38516 N (0.276%) |

Counts: 17 PASS, 0 MISMATCH, 1 UNVERIFIABLE item (the q16(a) drawing; q15(a) is a worded answer). No numeric claim in q1–q17 disagreed with the independent recomputation.

### Points worth knowing

- **q10** — the answer key writes 40 N in the second equation but prints 36.9 N / 13.4 N, which are the 39.24 N answers. The book resolves this correctly by using 39.24 N and adding a note; both note figures (37.6 N / 13.7 N from 40 N) reproduce exactly.
- **q11** — 8.5 N is 20sin25° = 8.4524 N at 2 s.f.; the 0.564% difference is display precision, not an error. The ANS diagram confirms F is perpendicular to the string, which is the geometry the equations assume.
- **q16 / q17** — grids re-read from pixels (grid pitch 128 px on the 3× crops of p05): q16 F1 = (2,6), F2 = (3,−1) → (5,5); q17 F1 = (2,3), F2 = (3,−1) → (5,2). Both agree with the book, so the grid readings used in the solutions are right.
- **q6 / q7** — the ANS key has no red box for these two, so their letters are checked against the printed option lists and the physics, not against a teacher's boxed answer.

### Units and dimensions (pint 0.26.2)

| formula | dimension produced | expected | result |
|---|---|---|---|
| F = ma | kg m s⁻² = N | N | OK |
| T cosθ = mg | N | N | OK |
| a = g tanθ | m s⁻² | m s⁻² | OK |
| T = W/(4cos20°) | N | N | OK |
| f = 80cos60° − ma | N | N | OK |

### Not verifiable

- **q16(a)** — draw the resultant on the grid: a drawing task; the numeric part (b) was verified and the two arrows were measured independently.
- **q15(a)** — worded explanation in terms of inertia; matches the ANS wording but has no number.

### Confidence

- Arithmetic: high — every value comes from a direct trig/force evaluation or a sympy solve, each shown with its relative difference.
- Grid readings (q16, q17): high — measured from pixel positions with the grid pitch detected from the image, and they agree with the ANS's own equations.
- Answer letters: high for q3, q4, q5, q8, q17 (boxed in the ANS pages) and medium for q6, q7 (no box, checked against the printed options).

### Reproducibility

Scratch scripts live outside the repo at `.tmp-verify/` in the workspace root: `recompute_f2.py` (all numbers), `measure2.py` (grid pixel measurement), `crop*.py` (crops of `pages/p05.jpg`).

## phy06-force2 — PHY CH6 Force II (q18–q35, second half)

- verified: 2026-11-21
- read: `books/phy06-force2/solutions.js` (q18–q35), `reference/ans/p07_01.png`…`p12_02.png` (20 crops), `reference/ans-text/q32.md`…`q35.md`, `pages/p07.jpg`–`p12.jpg` for the question data, `pages/p05.jpg` for the q18 grid
- written: `books/phy06-force2/reference/verify/q18.md`…`q35.md` and this file. No other file was touched: `solutions.js`, `book.json`, `layout.json`, `engine/`, `widgets.js` are unchanged.
- method: each part recomputed from the question's own data; g = 9.81 m s⁻² (book rule); sympy for the simultaneous-equation force balances; pint for dimensions; the q18 grid measured from page pixels and verified with an overlay rather than counted by eye.

| qid | answer in solutions.js | verdict | key numbers (claimed vs recomputed) |
|---|---|---|---|
| q18 | D (4 N right, 1 N down) | **PASS** | grid re-read: sum (+4,−1) N; 4.123 N, 14.04° below (not asked) |
| q19 | B (2.9 N with g = 9.81) | **PASS** | 2.9 vs 2.905; key's g = 10 → 3.000; B is 0.095 N away, A is 0.905 N |
| q20 | A (0.95 N) | **PASS** | 0.9525 vs 0.9525 (0.000%) |
| q21 | B (1.44 m s⁻²) | **PASS** | 19.62 / 4.62 / 1.44 all exact |
| q22 | B (283 N) | **PASS** | 283 vs 283.284 (0.100%) |
| q23 | B (45.1 N) | **PASS** | 39.05 vs 39.05; F 45.1 vs 45.0911 |
| q24 | C (26.0 N) | **PASS** | 18.3 / 3.59 / 26.0 vs 18.3013 / 3.59071 / 25.9808 |
| q25 | B (1.80 → 2 m s⁻²) | **PASS** | 1.80 vs 1.80138 |
| q26 | A (X stays) | **PASS** | 14.7 vs 14.715; 4.91 vs 4.905 |
| q27 | a 4.90 m s⁻², T 2.81 N | **PASS** | 4.90 vs 4.90248; 2.81 vs 2.80653 |
| q28 | 27.4 N, 0.230, 24.4 N, 3.12 m s⁻² | **PASS** | all four within 0.204% |
| q29 | (a)(b) drawing/sketch, (c) u > V | **UNVERIFIABLE** | (a)(b) not numeric; (c) reasoning verified |
| q30 | f = 0.2 N | **PASS** | 0.2 vs 0.200 |
| q31 | 5.76 / 6.79 / 2.76 (g = 9.81) | **PASS** | 5.75522 / 6.78541 / 2.76437; key g = 10 → 5.82 / 6.82 / 2.86 all reproduce |
| q32 | 5.63 m s⁻², 32.1 N, 18.4 N, 222 N, 223 N | **PASS** | 0.057%–0.238%; every part checked |
| q33 | 56.6 N, 113 N, 4.91 m s⁻² | **PASS** | 56.6381 / 113.276 / 4.905 |
| q34 | 24.53 N, 12.74 N, 37.27 N, 0.546 m s⁻², 24.0 N | **PASS** | all within 0.053% |
| q35 | 3.75 m s⁻², 22.5°, 20.3 N, 53.1 N, 1.33 m s⁻² | **PASS** | 3.75 / 22.4739° / 20.291 / 53.0813 / 1.335 |

Counts: 17 PASS, 0 MISMATCH, 1 UNVERIFIABLE (q29, whose (a) and (b) are a diagram and a sketch). No numeric claim in q18–q35 disagreed with the independent recomputation.

### The questions the chief flagged

- **q18** — re-read from `pages/p05.jpg` with pixel work, not by eye: grid pitch fitted at 113 px (3× crop), the four arrows traced as masks, and the book's four vectors drawn back over the page. Every overlay line lands on a printed arrow and every tip on a grid node, so F1(−1,+3), F2(−2,−2), F3(+3,−3), F4(+4,+1) are confirmed. Sum = (+4,−1) N, and the printed option D is 4 N right / 1 N down. The book's reading is correct.
- **q19** — the 'nearest option' handling is sound. 2.905 N is 0.095 N from B (3 N) and 0.905 N from A (2 N); the 3% gap is purely the g convention (the key used g = 10 and got exactly 3 N). B is right under either convention.
- **q23** — the key's line `10(10)sin30 − 10` evaluates to 40.0 N, not the 39.05 N it states, so the key's own digits come from g = 9.81. The book's 39.05 N and F = 45.09 N are correct, and the printed option 45.1 N confirms 9.81 (g = 10 would give 46.2 N, which is not offered).
- **q27 / q28** — checked against `pages/p09.jpg` and the key crops: q27 is blocks A (1.5 kg, 18°) and B (2 kg, 40°) with a = 4.902 m s⁻² and T = 2.81 N; q28 is the 5 kg block with the 15 N and 20 N forces (27.4 N, 0.230 m s⁻², 24.4 N, 3.12 m s⁻²). Neither question is carrying the other's content, and the key's own red boxes are attached to the matching question.
- **q31** — both g conventions are reproduced exactly: the book's 9.81 set (5.75522 / 6.78541 / 2.76437) and the key's g = 10 set (5.82020 / 6.82361 / 2.85685). The merged note states both, so nothing is silently mixed.
- **q32, q35** — every part was recomputed separately (q32 (b)–(e); q35 (a)(i), (a)(ii), (b)(i), (b)(ii), (c)). All agree; the largest single difference is q35(c) at 0.374%, caused only by using 22.47° instead of the rounded 22.5°.

### Units and dimensions (pint 0.26.2)

| formula | dimension produced | expected | result |
|---|---|---|---|
| mg sinθ − f = ma | N | N | OK |
| a = (m₂g − m₁g sinθ)/(m₁+m₂) | m s⁻² | m s⁻² | OK |
| v = √(2as) | m s⁻¹ | m s⁻¹ | OK |
| N = mg cosθ + F sinθ | N | N | OK |

### Not verifiable

- **q29(a)** free-body diagram — drawing task.
- **q29(b)** velocity-time sketch — sketch task; the book's description matches the key's sketch.
- **q32(a)**, **q33(a)(i)** free-body diagrams — drawing tasks; their numeric parts were verified.

### Confidence

- Arithmetic: high — every part comes from a direct force resolution or a sympy solve, each with its relative difference above.
- q18 grid: high — pixel measurement plus an overlay check, the same method used for q16/q17 in the first half.
- MCQ letters: high for q18, q20, q21, q22, q23, q24, q25, q26 (each against the printed option list); q19 has no red box in the key, so its letter rests on the nearest-option argument given above.

### Reproducibility

Scratch scripts at `.tmp-verify/` (workspace root, outside the repo): `recompute_f2b.py` (all q18–q35 numbers), `overlay*.py` and `measure_q18*.py` (q18 grid measurement and overlay), `crop4.py`/`crop5.py` (crops of `pages/p05.jpg`).
