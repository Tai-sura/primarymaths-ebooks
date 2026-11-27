<!-- canon: ebook-starter-v2/docs/03-authoring-style.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# Authoring style

These rules make every book look and read like the teacher's own notes. Each one was approved, or asked for, during the JM26 (B) build. When a new chapter needs something these rules don't cover, decide it with the teacher, then add it here.

## 1. Page and answer boxes

- **Keep the original design.** The QUE page is the background, and nothing covers the printed question.
- **Answers sit inside the blank answer space**, in red-bordered boxes with a margin, laid out like the ANS key: side-by-side boxes where the key has them (parts (a), (b), (c), or MC working beside the options).
- **Controls** (▸ next, » all, ◂ back, ↺ reset, graphic, link) sit in a slim column right of the boxes, with a progress count such as "3/8".
- **Hidden steps** show as grey bars, and the next one is striped. Tapping a box reveals one step; tapping a bar reveals up to it.
- **When space is short:** shrink the text, then drop number lines, and only then continue on an extra sheet. Accept 70 % text on dense MC pages; avoid going below about 62 %.
- **Side reasons are plain text.** `m(tex, reason)` and `t(text, reason)` print the reason exactly as written: no `$…$`, no TeX command, and no maths-only token such as `u_x`. Write words — "horizontal speed is constant", not `x = u_x t`. A long `\therefore …` sentence is a `t()` line, never `m()`.
- **A `space` cut never crosses ink.** It falls on a measured blank row, and every region stays above the printed footer; see "Answer space and page cuts" in [02-book-format.md](02-book-format.md).
- **Before trying a new look**, back up the project folder so it can be reverted in one step.

## 2. Worked solutions

- **Follow the teacher's method exactly:** the same unknown, the same order of steps, and the same final sentence as the red-boxed working in the ANS.
- **Hong Kong conventions:**
  - "Let $x$ be …" when the key defines the unknown;
  - $\because$ … and $\therefore$ …;
  - integer reasoning written out: "$\because$ $k$ is an integer.", then "$\therefore$ The maximum possible value of $k$ is 7.";
  - final answers underlined where the key underlines them: `\\underline{26}`.
- **One step per line.** Each algebra step is its own `m()` line, so a tap reveals exactly one move.
- **Side reasons** are short and start with the operation: "+ 10", "÷ 2", "÷ (−6): reverse", "collect like terms", "set up from the question". Always flag a sign reversal.
- **Geometry reasons** use the bracket phrase a marker accepts, and a parallel-line reason names the lines. The reason stays on the same line as the step, at the same size as the working, immediately to its right. The phrases are: `given`; `SAS` / `SSS` / `ASA` / `AAS` / `RHS`; `common side`; `adj. ∠s on st. line`; `vert. opp. ∠s`; `corr. ∠s, AB // CD`; `alt. ∠s, AB // CD`; `int. ∠s, AB // CD`; `corr. ∠s equal` / `alt. ∠s equal` / `int. ∠s supp.`; `∠ sum of △`; `ext. ∠ of △`; `base ∠s, isos. △`; `corr. sides, ≅ △s` / `corr. ∠s, ≅ △s`; `opp. sides of //gram`; `opp. ∠s of //gram`; `diags. of //gram`; `diags. bisect each other`; `opp. sides equal`; `opp. ∠s equal`; `2 sides equal and //`; `mid-pt. theorem`; `Pyth. theorem`.
- **Parts** get `h("(a)")` headings, normally one box per part.
- **Teacher margin notes** (`note()`) are for the key's pink side remarks, such as "Number of pages must be an integer, so …".
- **MC questions:**
  - test each statement I, II, III in turn, by working or with a counterexample (the "LQ method" substitutes values);
  - end with "$\therefore$ The answer is D." only if the teacher wants the letter shown;
  - leave answer squares empty unless asked (JM26 (B) removed the letters for Q23–Q30).
- **Check every final answer** against the ANS before release.

## 3. Number lines (HKDSE style)

The same style is used in the answer boxes (`nl()`) and in the graphics (`ray()`):

1. The axis has arrowheads at both ends, ticks, and real minus signs (−12, not -12).
2. A **short vertical line** rises from the boundary value.
3. A **circle** sits on top: **hollow** for $<$ and $>$ (the value is not included), **filled** for $\le$ and $\ge$.
4. The **arrow** runs from the circle in the direction of the solutions.
5. Integer solutions are red dots on the axis. In graphics, the answer value gets an orange ring, and sample values are labelled pins stacked so they never overlap.

For **ranges of two related variables** (e.g. "given $x > 0$, find the range of $y = 3x - 24$"), use the x–y picture:
- the x number line along the bottom and the y line up the left side, both in the style above;
- the given range in green, the resulting range in blue, and their overlap shaded orange;
- the relation drawn as a line, thick red where it satisfies the condition;
- dashed guides from the boundary point to both axes;
- a legend such as "given: x > 0, so: y > −24", adding "negative coefficient: sign reversed" when the sign flips.

## 4. Review links

Review links connect the wording of a question to the part of the answer it becomes. On the question they show as faint dashed boxes; in the answer they show as coloured dotted underlines (so neighbouring pieces in a formula do not clash). Tapping one opens a solid box on the question and a solid underline (with a light tint) on the answer, with a remark tag and a short leader line. Nested answer links stack their underlines downwards.

- **Link every word problem.** Skip printed worked examples, and questions where no phrase maps to a step (e.g. pure-algebra MC).
- **What to link:**
  - the definition of each unknown ("BC = x cm" → $x$);
  - each quantity built from it ("longer than BC by 4 cm" → $(x + 4)$);
  - the relation words ("at least" → $\ge$, "is shorter than twice" → $< 2(\dots)$, "not more than" → $\le$);
  - conditions ("x is a positive integer");
  - what is asked ("greatest value of x").
- **Link only what matters.** Box the exact phrase that maps to an answer part, not the whole sentence. In JM26 (B) Q5, "two consecutive even numbers" was unlinked, and only "the smaller number is x − 2" was linked.
- **Colours:**
  - amber for the inequality condition ("at least 23", "greater than 61 cm");
  - pink, blue and green for the quantities;
  - purple for a fifth link, usually what is asked.

  Within a question, each colour means one thing on both sides.
- **Tags** are short notes: "$AB = x + 4$", "at least → $\ge$", "least integer with $n \ge 8$".
- On the answer side, mark the smallest piece that matches: `L()` inside maths, or `[[key|words]]` in a sentence. Use `lk()` only when the whole line is the match.

## 5. Interactive graphics

A graphic should make the reasoning visible, not just repeat the algebra.

- **If the question prints a figure, the graphic is that figure — redrawn to the pixel.**
  Measure it from `pages/pNN.jpg` at 3 px/pt before drawing: every circle's centre and
  radius from the ink itself (sample the rim at 360° and fit through the ink centre, never
  from a downscaled view or by eye — a wrong seed slides onto the neighbouring circle's
  arc), plus each letter badge, each leader and every measurement arrow the page prints.
  Then prove it: draw the measured geometry back over the page image and show that every
  element sits within **1.5 px** of the printed line (mean and p95, not one max). A figure
  that is only "similar" teaches a different picture from the question, and every check and
  review after it is then validating the wrong thing. When you draw it: one pt ? px map for
  every element (no "corner at 45 %" heuristics), non-target lines at the printed ink weight
  with a thin target ring and at most 5 % fill, and the explanatory marks (centre dots) drawn
  **last** and large enough ? the printed arrows run through the centres and will hide them.
- **It must match the question.** It opens with a question card (the question in brief, then the same "Let …" lines and inequality as the worked solution) and uses the solution's letters.
- **It must suit the form.** Use pictures, bar models, counters, number lines and shapes. Don't use graphs of functions unless the class has learned them. JM26 (B) Q11 replaced a cost/income graph with a picture of oranges and two money bars.
- **Standard parts:**
  - the picture, which redraws live;
  - a slider for the unknown, with − / + and ▶ play;
  - a readout with the substituted calculation and ✓ satisfies or ✗ fails;
  - a caption explaining the current value ("Exactly 300 pages is not MORE than 300");
  - quick buttons for the key values ("Least value: 101", "Too few: 60", "Just enough: 72").
- **Colours:**
  - green means satisfies, red means fails;
  - amber marks the answer or boundary;
  - blue is the unknown;
  - soft tints are for areas.
- **Good fits by question type:**

  | Question type | Graphic |
  | --- | --- |
  | Polygon perimeter and side counts | Polygon slider, with the sides unrolled onto a ruler |
  | Consecutive numbers | The pair on a number line, with the +2 jump |
  | Money and counts | Counters or items plus money bars |
  | Journeys | Bar models of distance |
  | Mixtures | A beaker filling in layers |
  | Angles | An n-gon with angle arcs |
  | Two related variables | The x–y range picture |
  | MC | Sliders for the variables, a live true/false for each statement, and a "find a counterexample" search |
  | Percentage change | Original bar vs new bar, with the change marked |
  | Successive changes, growth and decay | A bar per period with the factor between bars (JM27 (A) `timeline()`) |
  | Reverse percentage ("… ago", "original") | The same timeline, with a slider for the start until the given bar matches |
  | Threshold ("less than half", "double") | The timeline with an amber threshold line |
- **No overlaps.** Labels, pins and legends must never collide. Check every graphic's QA screenshot at the default value and at the extremes.

## 6. Ink and tools

Ink behaviour belongs to the engine and is the same in every book, so there is nothing to author per chapter. If the teacher asks for an ink feature, add it to `engine/ink/` for all books.

## 7. Measuring a printed figure (for panel animations)

The printed physics diagrams in this book are **not black ink**. The trajectory lines are
yellow-green at high saturation; only the labels (75°, 60°, …) are black. So a luminance
threshold (grey < 128) finds the labels and misses the curves, and a fit scored against that
mask converges on a label instead of a curve.

- Mask the curves by saturation, not brightness: max(r,g,b) - min(r,g,b) > 40 and max(r,g,b) > 90.
- Each trajectory is a parabola whose apex x is the midpoint of launch x and landing x (checked on
  p7: 414.4 / 444.8 / 456.0 against midpoints 414.4 / 444.8 / 456.0). So a curve is pinned by three
  numbers: launch point, landing point, apex height. Read the apex height from the saturated runs at
  the apex column; do not fit a free-form curve.
- p7 measured apex heights above the launch point y = 216.0: 15° 7.7, 30° 31.3, 45° 65.5,
  60° 95.3, 75° 120.0 pt. The family is drawn with a vertical stretch of about 1.5–1.6× against
  real physics, and the stretch is not uniform — do **not** rebuild them with a single factor.
- Animate the ball on the measured parabola and leave the printed curves untouched; the poster and
  the last frame must be a straight crop of pages/pNN.jpg (native 3 px/pt), so nothing shifts when
  the animation ends.
- The green landing discs are the shared endpoints: p7 has three, at x = 454.0 (15°/75°),
  514.8 (30°/60°) and 537.2 (45°), centre y = 216.3. Complementary angles share a range but **not**
  a flight time: t ∝ sin θ, so the shallow one lands first.

## 8. Panel overlays: measure them, then watch every frame

p1 `ResolvingVelocity` shipped broken for a whole release and no check caught it, because
`--still` compares only the opening frame (guides) or the closing frame (media) — both are the
printed figure, so overlays that are misplaced or out of shot still PASS.

What went wrong on p1 (2026-11-20):

- the overlay arrows used a second coordinate set: `v` ran from (406, 206) to (566, 82), so its tip
  sat 21 pt above the camera frame. Nothing of the triangle was in shot; only a stray `θ` and
  duplicated labels landed on the page.
- a white cover hid the printed "y (vertical) component of velocity" for the first seconds.
- the film re-drew labels the print already carries ("vx = v cos θ" twice, "vy = v sin θ", θ).

Rules from here on:

1. Measure every overlay point on pages/pNN.jpg (colour mask + line fit) and keep it as a named
   constant with a comment saying where it was measured. On p1 the printed figure gives: v from
   (403.0, 258.9) to (521.7, 164.4) at 38.6°, the green guide at y = 265.5 from x 403.7 to 522.3,
   the red guide at x = 402.2 from y 259.0 to 142.3.
2. `--still` proves only that the poster is the print. Before rendering the film, pull three or
   four frames from the middle of it (`ffmpeg -v error -y -ss <t> -i <mp4> -frames:v 1 f.png`) and
   check that every overlay sits on the line it explains.
3. Do not re-draw what the print already has. Fill its dashed guides with solid arrows in the
   printed colours (sample them: p1 green #19eb16, red #fe030a, blue #1404ff), or highlight and
   follow them; add new words only where the print has none.
4. A white cover is only for page text that bleeds into the figure's bounding box (for example the
   last lines of a question). Never cover the figure's own labels.
5. Vectors act at the centre: the tail of a velocity, weight or acceleration arrow is the object's
   centre, never the top of the ball. If the arrow needs room below the object, grow the canvas —
   the Q6 widget went from `HT 250` to `270` so the v_y arrow stays whole when the ball reaches
   the floor.


## 9. The rules in one place

[06-layout-controls-and-media.md](06-layout-controls-and-media.md) collects every layout, control
and media rule with the symptom, the cause, the rule and the check that enforces it. Read it before
starting a new book; §2 covers the cut line that `check_cuts.py` now guards in this repo too.

---

## Physics only (verbatim from the physics repo — NOT yet reconciled with the base above)

6. **The poster is what the student sees before pressing ▶.** It must be the **finished** figure
   (the same image the film ends on), never a blank grid or a mid-draw frame — otherwise the page
   hides the printed figure behind an empty panel. Frame 0 and the last frame must be the same
   drawing (`PSNR inf` on the poster, ≥50 dB between first and last decoded frames), and the film
   must never fade to blank at the end: hold the finished figure for at least 0.5–1 s.
7. **A tool must move with the line it draws.** On the compass film the body had to turn about the
   needle so the pencil stayed at the arc's leading end; a static tool with an arc appearing beside
   it reads as magic, not as drawing. Measure it: the tool's axis and the arc's end differ by
   ≤2°, the pencil sits ≤1 px from the arc, and the pivot does not move (<1 px).
