# Page layout, controls and media: the rules this book was built by

Every rule below is here for one of two reasons: a check fails when it is broken,
or a book shipped with the fault first and a teacher saw it. The symptom is what
the teacher saw; the rule is what to do next time; the gate is the command that
stops it coming back. They were all learned building *P5 Maths 07 Circles (A)*.

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

## 13. One redrawn figure per printed figure, measured from the print

Several sub-questions on one printed figure (Q18–Q23's six circles) get **one**
redrawn figure, not six generic sliders. Measure its geometry from the page JPEG:
centre, radius, badge positions, elbow leaders, the arrows and values the print
already shows (1 pt = 3 px). Colour only the circle the question asks about. If
the printed arrows already mark a length, draw only the dashed line that is asked
(Q21's circle D draws the radius, not the diameter).

And the print is not always to scale: circles C and F measure 80.7 and 80.3 pt for
answers of 5 and 6 cm. Draw like the print; keep the reading from the answer key.

## 14. Style by measurement, never by eye

The global `button { min-width: 40px }` beat `.ans-play`'s 13 px and turned the
Play into a 40 × 40 circle; the fix is `min-width/min-height: 0`. Every tappable
is compared with the LQ Play item by item — box, radius, fill, glyph, font size —
not "looks about right".

Gate: `check_play.mjs`.

## How we work

- **Fix one, sweep the book.** The same fault appears on every question built the
  same way: four homework rows, six table rows. Re-render every page and look
  before shipping.
- **When a problem survives a few rounds, list the symptoms and the root cause
  before touching anything.** Blind fixes move the fault instead of ending it.
- **Delivery means 0 FAIL and 0 WARN**, not "no blocking problems". A WARN needs
  a fix or an allow-list entry with a reason and a date.
- **Bring evidence**: screenshots and measured numbers, not "done".
- **Publishing is a separate, approved step**, and only from the deploy clone.

## Known open items

`CircleBasics` still fades out at 13.5 s, and its mid-section uses flat bilingual
labels while the first and last frames use the printed colour boxes — a style
switch when it returns to the print. Both are recorded for the next animation
round.
