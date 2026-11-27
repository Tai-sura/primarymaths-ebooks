<!-- canon: ebook-starter-v2/docs/06-layout-controls-and-media.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# Page layout, controls and media: the rules this book was built by

Every rule below is here for one of two reasons: a check fails when it is broken,
or a book shipped with the fault first and a teacher saw it. The symptom is what
the teacher saw; the rule is what to do next time; the gate is the command that
stops it coming back. They were all learned building *P5 Maths 07 Circles (A)*.

**Scope in this repo.** Physics books have no fill-in-the-blank answers: no
`book.json` here uses `answerStamps` and `engine/viewer/answers.js` has no stamp
code, so the stamp rules (§3 in part, §4, §6, §7, §8) apply only if a future
book adds them. What applies **today**: §1 and §2 (every physics book has
`region` cuts — 129 `space` keys across 19 books), §3 for `ctl`/chip placement,
§5, §9, §10, and every media rule. `tools/qa/check_cuts.py` now lives here and
runs over every book; see `docs/04` §2 for the sequence.

**Gates named in this file.** Run what exists in this repo: `check_book.mjs`,
`check_media.mjs`, `check_cuts.py`, `check_answer_chips.py`, `check_boards.mjs`,
`check_embed.mjs`, `check_folio.py`, `measure_ctl.mjs`. `check_play.mjs` and
`check_stamps.py` live in the maths repo; this repo has no fill-in stamps, so the
stamp rules below apply only when a book borrows that answer style.
## 1. Measure what the engine draws, not what the tool assumes

The engine works in whole-page terms: `growSheet()` opens a page by inserting a
band across the **full page width**; the step strip is placed at the **answer
card's right edge**; its height comes from the card, not the region; a media
panel is placed on a pocket of paper whose **height** must equal the video's
aspect ratio. A measurement that only looks at the answer column silently fails
every one of those cases.

For a media region, measure the printed frame with an ink band (1 pt = 3 px at
`extract.zoom = 3`), not by eye and not from a coloured background: a tinted
panel's bottom edge sat at 725 pt while the printed box line was at 750 pt, and
the 25 pt error clipped the second line of the panel. Check the ratio too —
`region` 230 × 193.7 pt = 1.1875 against 690 × 582 px = 1.1856.

Gate: `check_cuts.py`, `measure_ctl.mjs`, `check_media.mjs`.

## 2. A cut line must be blank across the whole page width

`region[3]` is where the page is opened. Choosing it from the answer column left
a cut through the bottom edge of a printed answer box (Q35) and through a circle's
lower arc (HW14), which shows as a broken shape, not as a moved answer.

Gate: `check_cuts.py` — every column of the line is tested against the page JPEG.

## 3. Every tappable is measured, and they clear each other

Three things can sit near an answer: the Play (`playAt`), the amber widget button
(`graphicAt`) and the red answer stamp. Any two of them on one pixel is a defect.
A stamp is cut *after* the layout, so nothing knows it is there unless it is
checked then.

Gate: `check_answer_chips.py` (ink, stamp, overlap), `check_play.mjs`.

## 4. Measured is not drawn

The stamp branch used to `continue` after placing the Play, so `graphicAt` was
measured for every question but the button was never created — q1 and q11 stayed
dormant for weeks. A position on paper proves nothing until the reader really
shows it.

Gate: `check_play.mjs` taps every `.ans-play[data-act="graphic"]` and fails when
the drawer does not open.

## 5. A new button type changes the QA selector in the same commit

`.ans-play` selected both buttons, so the amber widget button was judged against
the Play's fill and glyph and failed. When a control type is added, update the
selectors that describe the old one (`:not(.ans-graphic)`).

## 6. A stamp carries only ink the printed page does not

Two faults, one cause. An opaque white rectangle painted over the table rules and
figures under the answer; a faithful rectangle drew the printed words a second
time (`aand`, a doubled circle) because the ANS and QUE scans sit a few points
apart. The stamp is cut with alpha (only ink is opaque), aligned to the page
(±4 pt search), and black ink is dropped only where the page has ink at the same
pixel after that alignment. Red ink is never touched — it is the answer.

Gate: `check_stamps.py` — one red pixel short is a FAIL; black dropped on blank
paper is a WARN that must be allowed in `stamp_erase_allow.json` with a reason.

## 7. One stamp per answer mark

One rectangle round three answers also contains the printed words between them,
and those get drawn again. Red blobs are grouped per mark (letters of one word
and a box round a word stay together; a printed gap splits them). p5m07a went from
44 stamps to 63 that way.

## 8. Answer cards and step strips stay off the printed figure

A region that runs over a figure drags the card's right-edge strip onto it. Narrow
the `region` to stop before the figure, or pin the strip with `ctlAt` when the
answer text fills the width. A pinned `playAt` also stops the nudge pass from
pushing a button into the table header.

Gate: `measure_ctl.mjs`.

## 9. Build guards: stamps, and media files paired with their poster

`extract_pages.py` rewrites `layout.json` **without** the stamps; a build that ran
in that window shipped a book whose answers were invisible. `build_deploy.ps1`
now throws when `answerStamps` is listed and the layout has none. The same idea
covers media: `src` and `poster` must both exist, and the poster must equal the
video's first frame (SSIM 1.0). Scratch harnesses (`_*.py`, `_*.mjs`, `_*.html`)
never reach the published copy.

## 10. Release discipline

Bump `CACHE`, build, tag the rollback (`pre-<book>-vNNN`) and push the tag with
`git push origin refs/tags/…` (never `--tags`), paste the `ls-remote` line,
then `check_live --expect-cache`. A media change replaces the `mp4` **and** the
`poster` in the same commit. Push only from the deploy clone; the source clone is
committed but never pushed. Publishing needs the user's approval.

## 11. The poster is what the student sees before pressing ▶

It must be the finished drawing, not an empty frame and not a blank first frame —
a poster of six empty boxes hides the printed comic until someone taps play. The
video's first and last frames are the same picture, so the loop does not jump and
the page does not swap the print for a frame of nothing.

## 12. A teaching animation must not fade out to nothing

`CircleBasics` fades to 0.9 % ink cover at 13.5 s and hard-cuts back at 13.8 s, so
a student who stops on the last frame sees an almost empty panel. End on the
finished picture and hold it for at least 0.5–1 s; frame 0 and the last frame must
be the same picture (≥ 50 dB after decoding, pixel-identical for the poster).

## 13. One redrawn figure per printed figure, and it is the printed figure

Several sub-questions on one printed figure (Q18–Q23's six circles) get **one**
redrawn figure, not six generic sliders. Measure its geometry from the page JPEG:
centre, radius, badge positions, elbow leaders, the arrows and values the print
already shows (1 pt = 3 px). Colour only the circle the question asks about. If
the printed arrows already mark a length, draw only the dashed line that is asked
(Q21's circle D draws the radius, not the diameter).

**The first attempt at this was wrong.** The six circles were seeded from a
downscaled view and fitted with least squares; because the circles overlap, the
fit slid onto a neighbour's arc. A came out too small and too far left, C too
large, D shifted, and F landed on a different circle entirely — and the widget had
already been reviewed and shipped before anyone overlaid it. The rule that came
out of it:

- sample each rim at 360° and fit **through the ink centre**, one circle at a time,
  reporting how much of the circumference is visible (an occluded arc biases a fit);
- never seed from a thumbnail, and never accept "it looks like the print";
- prove it by drawing the measured geometry **back over `pages/pNN.jpg`** — circles,
  badges, leaders and printed arrows — and listing the deviation per element;
  anything above **1.5 px** is wrong;
- do this **before** placing buttons, cards or colours. A figure that does not match
  the question makes every later step worthless: the checks, the layout, the review
  and the student's work all validate a picture the question never showed.

**Check the fit against the printed centimetres.** Every circle must land on the
same scale: A 42.7 pt for 3 cm, B 28.4 for 2, C 71.1 for 5, D 21.4 for 1.5, E 42.7
for 3, F 85.3 for 6, so all six sit on 14.2 pt/cm. If one circle only fits at a
different scale factor, the fit has slid onto a neighbour's arc; that is not the
print being out of scale. A first pass reported C and F at 80.7 and 80.3 pt and
nearly produced a rule saying "the print is not to scale" — the print was fine.

**Drawing it is its own set of traps**, and each one cost a round of review:

- **One map, no heuristics.** Every element goes through the same pt → scene
  conversion. The first version computed each badge leader as "a corner at 45 %
  across, then drop to the rim"; the printed leaders have their own measured
  corners, so all six were wrong. Store the measured points and draw them.
- **Weight changes apparent size.** Non-target circles at the printed ink weight
  (dark, 1.2–1.5 stroke); the target ring thin (≈2.2) with a fill of at most 5 %.
  A 2.8 ring over a 9 % fill made the highlighted circle read bigger than the
  printed one, and the teacher reported "C should be smaller" when C was exact.
- **Explanatory marks go on top, and large enough.** The printed cm arrows run
  through the centres, so centre dots drawn before the arrows simply vanished —
  only the highlighted circle's dot was visible. Draw them last, at r ≈ 5–6 scene
  px with a white halo. Concentric circles (B and C) share one centre.
- **Prove the finished widget, not just the numbers.** Draw the widget's own
  coordinates back over the page and measure how far each drawn circle sits from
  the printed ink: mean and p95, not a single max. The accepted run was mean
  0.36–0.41 px, p95 0.61 px, max 1.52 px. Two people measured independently and
  agreed to 0.28 pt; that is the standard to aim for before anyone is asked to
  judge a picture by eye.

- **The printed page stays on top.** Draw in this order: wash, dashes, printed
  rims, colour rings, printed arrows and their readings, badges, centre marks. With
  the rims underneath, a widget lost 114 printed-ink pixels where the dash crossed a
  rim and repainted it. Prove it by rendering twice, dashes shown and hidden: take
  the hidden frame's dark pixels as the printed ink and require every one of them
  back unchanged (0 pixels lighter by more than 20; the accepted run was 0 across 16
  states). A dash that passes over the print is the fault, not a detail.
- **A dashed length ends on ink, not in a gap.** A fixed `13 7` left a 307 px
  diameter about 7 px short of the rim, because the length was not a whole number of
  periods. Solve the period from the length instead: `periods = round(len/(on+off) -
  0.5) + 0.5`, then scale `(on, off)` to that. A whole number of periods is the trap
  (L mod period = 0 is where a gap begins): it left six of twelve dashed lengths
  2.8-4.0 pt short. Verify both ends inside ink, each within 0.5 pt of the rim.
- **Every circle opens on its own angle.** One global 62 deg put the largest
  circle's diameter 4.3 pt from another centre dot and 3.7 pt from a printed
  arrow, so the line read as ending at the dot. Score all 360 angles per circle
  against the other centre dots (at least 9 pt), the printed arrows, their readings
  and the badges; the fix moved it to 288 deg, nearest dot 18.8 pt. Recompute
  whenever the printed figure changes.
## 14. Style by measurement, never by eye

The global `button { min-width: 40px }` beat `.ans-play`'s 13 px and turned the
Play into a 40 × 40 circle; the fix is `min-width/min-height: 0`. Every tappable
is compared with the LQ Play item by item — box, radius, fill, glyph, font size —
not "looks about right".

**Never take a coordinate from a review, either.** A verdict that says "put the label
at (x, y), that area is blank" is still a claim about the page and has to be measured.
On spem05 p1 the subject lead offered `x 390–540, y 148–158` as a blank band for the
finger line; it carries **615 px below luma 170** (darkest 23) because the printed
left-hand drawing's leader lines run through it. The band that was actually blank was
the 68 pt column to its left (`x 268–336`), where the same probe reads 0 px below 200
and a minimum of 255. A reviewer's blank is worth exactly what its measurement is worth.

Gate: `check_play.mjs`.

## 15. A tool has to move with the line it draws

The compass film first drew the arc while the compass stayed upright, and the
pencil foot was nowhere near the arc - it read as the arc appearing by itself, not
as the compass drawing it. Two fixes were needed together: the pivots rotate as a
rigid body (the old code flipped the compass upright so it never crossed 90 deg,
which is why it had stopped turning), and one tracker drives **both** the arc and
the compass, so the pencil is always at the arc's leading end.

Gate: measure it per cell - the tool's axis against the arc's end within 2 deg, the
pencil within 1 px of the arc, the pivot fixed within 1 px - and keep frame 0 = last
frame.

## 16. Motion is measured, not assumed

An animation can be correct and still show nothing. spem05 p07 shipped and the user's
verdict was "沒有動態效果"; measuring the shipped `mp4` proved him right — 10.5 s of
13.8 s (76 %) had no visible change at all, in six dead stretches of 1.0–2.5 s, and the
only real motion was a 1.9 pt arc at r = 19 pt (about 40 pt², i.e. 100–170 pt² changed
per 0.25 s, a 1–2 px line at reading size). A wash at `fill_opacity` 0.15 over a printed
panel that is already light green is not a highlight either.

Before a film is delivered, sample the encoded `mp4` itself (not the source) every
0.25 s, and count a pixel as changed when its luma moves by more than 30. The thresholds
are **a share of the region's area**, not absolute, because a strip is not a page:
spem05 p07 covers 552 × 665 pt (367,080 pt²) while spem02 p14 covers 480 × 104.7 pt
(50,256 pt²), 7.3 times smaller, and fixed numbers would make a small panel impossible to
pass. On a full page the shares come to the numbers in brackets:

- no 0.40 s **inside the film** with less than 0.08 % of the region changing (300 pt²);
  the closing hold that § 12 requires (0.5–1 s on the finished picture) is exempt — it is
  the printed page, not dead air, and the encoder needs those frames to settle;
- every 1.0 s window with at least 0.41 % changing (1,500 pt²);
- at least three 0.25 s windows with 3.3 % or more (12,000 pt²), and each of those beats
  must be a visible element, not a faint wash;
- **no single frame may change more than 10 % of the region.** A 0.25 s window can show a
  big change that is either a smooth fade or a hard cut, and a cut reads as a flash, not
  as motion. Sample the film again at its own frame rate and look at one-frame steps:
  spem05 p07 (re-cut) peaks at 0.8 % per frame and p1 at 2.5 %, both smooth, while a
  panel that snaps on would show 30–60 % in one frame;
- every overlay element either at least 3 pt thick or shifting the luma of the print
  under it by 25 or more;
- frame 0 and the last frame still equal to the printed page (mean abs difference ≤ 5
  against the page crop), poster unchanged. **Decode the last frame from the `mp4`; the
  poster is not a substitute.** They are the same picture but not the same pixels: on
  p07 the poster JPEG reads 4.94 while the decoded frame reads 5.13, because a JPEG
  re-encode of that frame lands about 0.5 luma brighter. Measure the frame the reader
  actually plays;
- a page that only becomes clean a few frames before the end cannot be encoded to that
  gate at any crf that fits the budget: the encoder never converges. p07's closing fade
  cleared at 10.87 s, leaving 4 clean frames, and crf 30 then lost 1.1 luma on the last
  frame. Hold the finished page 0.6 s (§ 12) and the same crf 30 lands at 4.79 with
  `-x264-params aq-mode=3` (781 KB instead of 896 KB, because the bits go where the
  change is);
- file still ≤ 900 KB, no audio, `+faststart`.

Sample the delivered `mp4` with a resampler (`ffmpeg -vf fps=4`), not with a seek per
timestamp: a per-timestamp `-ss` agrees with an accurate seek here, but a resampled
stream is what the reader actually plays and it removes the doubt.

For scale: the spem02 p14 rheostat film changes 50.5 % of its strip over 10 s, with peaks
of 5,501 and 3,504 pt² (11.0 % and 7.0 %). The spem05 p07 version that the user rejected
changed 14.3 % of its page in six jumps, with 10.5 s of its 13.8 s showing nothing.

"Draw, then hold" is not an animation: a student who presses ▶ must see something move
in every second of it. Fill the waits (ticks appearing one by one, a marker breathing)
rather than padding them with `self.wait()`.

## 17. A film is rebuilt from the repo, never from someone's desktop

spem05 p07's Manim scene, `tools/manim/spem05.py`, was never committed: only the `mp4`
and its poster went in, so nobody could rebuild the film or fix it from the repo. The
spem02 scenes are in the same state — `tools/manim/spem02.py` is untracked too, so the
p14 rheostat film (`scene` = `spem02:Rheostat`) cannot be rebuilt either. Both files are
to be committed before their next re-cut. Any film — `media`, `guides`, an `endPages`
video — is delivered only when the repo alone reproduces it.

- Commit the scene source (`tools/manim/<module>.py`) **in the same commit** as the
  `mp4` and the poster. `git ls-files tools/manim` must list it before the commit is
  called done.
- `book.json` names it as `"module:Class"`, so the rebuild command is always
  `python tools/render_media.py <id> <Class>` (add `--still` to check the frame under
  the print first). SCALE 2.5, 30 fps and `+faststart` live in `tools/render_media.py` and
  are not passed ad hoc. The crf **is** an option (`--crf`, default 26) because the size
  budget sometimes forces another value: on spem05 p07 the re-cut had to fit 900 KB at
  crf 26, which moved the encoded last frame to meanAbs 6.02 against the printed page
  (crf 26 on the longer first version measured 3.93), so the crf used must be written in
  `media/SOURCES.md` — the file is only reproducible with it. `--max-kb` stops a run that
  would ship an oversized film instead of letting it through.
- **One render at a time in a checkout.** `render_media.py` holds
  `tools/_manim/render.lock` (an OS file lock) and refuses a second render, because two
  sessions rendering at once shared Manim's text cache and overwrote the same
  `media/*.mp4` four times in one night on spem05. A lock left by a dead process is taken
  over after 90 minutes.
- A film made outside Manim (a `cinecode` shoot, a film from a 1080p master) has no
  scene class: keep its project folder or its build script in `films/`, and record in
  the manifest where it is and how it is re-rendered.
- Every book keeps `books/<id>/media/SOURCES.md`: one row per media file with the file,
  its source (scene class or project folder), the exact rebuild command, duration,
  frame size, byte size and md5. A media file with no row there is not delivered.
- A re-rendered film keeps its file name, so bump `CACHE` or readers keep the old one.

## How we work

- **The figure before the furniture.** Measure the printed figure, prove the redraw
  with an overlay, and only then place buttons, cards and colours. If the picture is
  not the question's picture, every hour spent after it is wasted.
- **Fix one, sweep the book.** The same fault appears on every question built the
  same way: four homework rows, six table rows. Re-render every page and look
  before shipping.
- **When a problem survives a few rounds, list the symptoms and the root cause
  before touching anything.** Blind fixes move the fault instead of ending it.
- **Delivery means 0 FAIL and 0 WARN**, not "no blocking problems". A WARN needs
  a fix or an allow-list entry with a reason and a date.
- **Bring evidence**: screenshots and measured numbers, not "done".
- **One task per Bot at a time.** Sending a second brief to a Bot that is still working
  starts a second, parallel session in the same folder. On spem05 it cost real work:
  two of visual's sessions overwrote each other's renders four times (10:47–10:51) and
  the file that reached the commit was the last writer's, not the checked one; 3Dwork's
  two sessions rewrote the same explainer and its capture harness, and one of them broke
  the harness with a quoted `${PORT}` that the other then had to repair. Either wait for
  the reply before the next brief, or name the single writer in the brief and say what
  the other may not touch.
- **Publishing is a separate, approved step**, and only from the deploy clone.

## Known open items

None open in this repo's layout, controls or media.

Recorded but deliberately not fixed: the 18 cut lines that cross printed ink in the
secondary books (`jpfm08` 12, `spem02` 5, `jm29c` 1), listed in
`04-qa-and-release.md`. Those books are finished, approved copies, and re-cutting
moves every answer below the line. Check a cut before reusing its region in a new
book; never re-cut a published one.


---

## Maths only (verbatim from the maths repo — NOT yet reconciled with the base above)

**Scope.** This is a rule for a book whose printed figures run across the page, which is
the case in the primary maths book. A published secondary book keeps its cuts: re-cutting
moves every answer below the line and changes a layout the teacher has already approved.
Check a cut before reusing its region in a new book; never re-cut a finished one on the
strength of this rule alone.

  the rims underneath, q18 lost 114 printed-ink pixels where the dash crossed a rim
  and repainted it. Prove it by rendering twice, dashes shown and hidden: take the
  hidden frame's dark pixels as the printed ink and require every one of them back
  unchanged (0 pixels lighter by more than 20; the accepted run was 0 across 16

- **A dashed length ends on ink, not in a gap.** A fixed `13 7` left F's 307 px

  (L mod period = 0 is where a gap begins): it left A's radius, B's and C's diameters
  and F's radius 2.8-4.0 pt short. Verify both ends inside ink, each within 0.5 pt of
  the rim.
- **Every circle opens on its own angle.** One global 62 deg put F's diameter 4.3 pt
  from E's centre dot and 3.7 pt from D's printed 3 cm arrow, so the line read as
  ending at the dot. Score all 360 angles per circle against the other circles'
  centre dots (at least 9 pt), the printed arrows, their readings and the badges; F
  moved to 288 deg, nearest dot 18.8 pt. Recompute whenever the printed figure
  changes: the numbers come from the measured geometry, not from taste.

pencil foot was nowhere near the arc — it read as the arc appearing by itself, not

rigid body (the old code flipped the compass upright so it never crossed 90°, which
is why it had stopped turning), and one tracker drives **both** the arc and the
compass, so the pencil is always at the arc's leading end.

Gate: measure it per cell — the tool's axis against the arc's end ≤ 2°, the pencil
≤ 1 px from the arc, the pivot fixed within 1 px — and keep frame 0 = last frame.

  not the question's picture, every hour spent after it is wasted — this is the one
  order that must never be reversed.

None in this book's layout, controls or media. Two things that were open are now closed:

- `CircleBasics` no longer fades to blank; it clears the printed page to white before it
  draws, and crossfades back at the end (v171).
- Its mid-section labels stay as flat coloured text, while the first and last frames use
  the printed colour boxes. **The teacher looked at both and chose to keep the flat
  labels** — do not "fix" this without asking; it is a decision, not a defect.
