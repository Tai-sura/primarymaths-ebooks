# QA and release

## 1. Preview locally

The reader loads its files as modules and JSON, so it must be served over HTTP; double-clicking `index.html` does not work.

```powershell
cd "<project folder>"
python -m http.server 8090
```

- This computer: <http://127.0.0.1:8090/>, then pick the book (or go straight to `reader.html?book=<id>`).
- iPad on the same Wi-Fi: start with `python -m http.server 8090 --bind 0.0.0.0`, then open `http://<this PC's IPv4 from ipconfig>:8090/`. Allow Python through Windows Firewall on private networks. Offline install needs https, so test that on the live site.

## 2. Automatic checks

```powershell
cd tools/qa
npm install                      # first time only
node check_book.mjs <id>         # checks only
node check_book.mjs <id> --shots # checks + screenshots in books/<id>/reference/qa/
```

The script serves the site itself, and opens the book in Chrome emulating an iPad: 1180 × 820, touch, Retina, with Pencil input sent as pen events. It reports:

| Result | Meaning | Fix |
| --- | --- | --- |
| FAIL no anchor found | A question in `book.json` is missing from `layout.json`. | Fix `extract.anchors` or `fixedAnchors`, then re-run `extract_pages.py`. |
| FAIL no entry in solutions.js | A question has no solution. | Add it, or remove it from `book.json`. |
| FAIL phrase not found | A link's `q` phrase doesn't match the printed words. | Copy the words exactly as printed; a phrase may wrap across lines. |
| FAIL no marked answer part | A link has nothing to point to. | Add `L()`, `lk()` or `[[key|…]]`. |
| FAIL underline does not sit under all of … | An answer underline is shorter than, or cuts through, the maths it marks (fractions, powers, roots). | A measuring bug in `inkRects()` in `engine/viewer/links.js`; the book content is fine. |
| FAIL graphic threw / drew nothing | A widget crashed. | Fix it in `widgets.js`. |
| FAIL page error / HTTP 404 | Broken code or a missing file. | Read the message. |
| FAIL Pencil stroke / finger tap | An input regression in the engine. | See [05-engine-notes.md](05-engine-notes.md). |
| WARN answer scrolls inside its region | The answer is taller than its region at the book's type size. | Acceptable for teaching; add `space` in `extract.overrides` when a short answer should show in full. |
| WARN shrunk to N % | The text was scaled down to fit. | Acceptable down to about 62 %. |

Exit code 0 means nothing blocks a release.

Two results are newer than the rest and protect against the fault that shipped in `p5m07a`:

| Result | Meaning | Fix |
| --- | --- | --- |
| FAIL answer region is inverted | `layout.json` has `region[3] < region[1]`: the reader would cut the page above the answer and the card would sit on the next question's text. | Re-run `extract_pages.py`; a page with no blank row needs `answerCards` (or `answers: "cards"`), not a hand-made region. |
| WARN answer region runs past the page | The region's bottom is below the page height (a footer, or a page grown by `relayout_pdf.py`). | Move the region up, or record the page's real height in `layout.json`. |

For a book with answer cards (`"answers": "cards"` or `answerCards`), also run:

```powershell
python -X utf8 tools/qa/check_answer_chips.py <id>
```

It maps every chip's `cardAt` back through the page JPEG and fails when a chip covers printed ink. `check_book` already opens every card once, so its fit and scroll warnings cover cards too.

For a book with stamped answers (`answerStamps`), the same check covers the Play button of every stamp — it maps each `playAt` back through the page JPEG, fails when a button covers ink, and fails when two buttons share a box — and then the browser check:

```powershell
python -X utf8 tools/qa/check_answer_chips.py <id>
node tools/qa/check_play.mjs <id> --shots $env:TEMP\<id>   # optional page shots
```

`check_play` fails when a stamped answer has no Play, when the button is not the same box, fill, corner and `▸` glyph as the LQ answer's Play, when the two buttons of one stamped answer (Play and the amber widget button) overlap or sit under the toolbar, when the amber button does not open the drawer, or when a tap does not open and close its answer. The Play must match the LQ Play by measurement, not by eye — and `.ans-play` must keep its `min-width/min-height: 0`, or the global 40 × 40 `button` rule turns it back into a big circle.

Every book, whatever its answer style, also gets the cut-line check:

```powershell
python -X utf8 tools/qa/check_cuts.py <id>
```

`extract_pages.py` opens a page by inserting blank space at each question's `region[3]` (`growSheet` in `engine/viewer/answers.js` cuts across the **whole page width**). `check_cuts.py` maps every cut line back to the page JPEG and fails when any column of that line still carries printed ink — a cut through the bottom edge of a printed answer box or through the lower arc of a figure shows up as a broken shape on screen, and no button check would catch it. Stamp questions are skipped (their answer is drawn over the page). A book that fails needs its `region[3]` moved to a row that is blank across the full width, not just under the answer column.

For a book with stamped answers, the stamps themselves are checked against the ANS page they came from:

```powershell
python -X utf8 tools/qa/check_stamps.py <id>
```

Every stamp is cut from the ANS scan and then trimmed so that printed ink the QUE page already shows is not drawn a second time. `check_stamps.py` re-reads the ANS page and compares: **one red pixel short is a FAIL**, because red is the answer and it is never trimmed. Black ink the trim dropped that landed on paper the page leaves blank is a WARN above 1 % of that stamp's black ink; those must be cleared one by one in `tools/qa/stamp_erase_allow.json` with a reason and a date (a boxed answer printed in black sits close to its box's rules, so an over-eager trim shaves a stroke and only the teacher would notice). The density constant is fixed at 0.35 — a looser value shaves the top off a boxed "2".

Then check the printed page numbers, because a clean text layer does not prove a folio is visible:

```powershell
python tools/qa/check_folio.py <id>      # --verbose lists every page
```

| Result | Meaning | Fix |
| --- | --- | --- |
| MISS pN | The folio's own box on `pages/pNN.jpg` is empty: the number was never drawn there, usually because a figure or a white box covers it. | Place the glyph by hand — [05-engine-notes.md](05-engine-notes.md) → Page numbers. |
| LOOK pN | Something else (a figure edge, a rule, a neighbour label) runs through the folio box, so the number may be unreadable. | Look at a 3× crop of the footer; if the number cannot be read, treat it as MISS. |

Run it on every book after any engine change, and on a book whenever its page images or `layout.json` are rebuilt. It is a standing part of the gate, not a one-off.

### Book list, live build and media budget

```powershell
node tools/qa/check_catalog.mjs                              # catalogue, folders and status agree
node tools/qa/check_live.mjs <id> --expect-cache ebooks-vN   # the published site serves this build
```

`check_catalog.mjs` fails a listed book with no folder, a live book that is not
listed, a book whose folder and `id` disagree, and a live book with no
`docs/chapters/<id>.md`. `check_live.mjs` reads the published `sw.js` CACHE, the
live `book.json` status and the reader/layout/solutions responses, so a missed
cache bump or a failed deploy is caught instead of assumed. `check_media.mjs`
warns when a panel video is over the 300 KB budget.

For a book with scenario boards (`"infographics": true`):

```powershell
node check_boards.mjs <id> [q1 q5 ...]
```

It draws every board with all its steps showing and reports handwriting that overlaps other handwriting, is crossed by a table rule, or runs off the board. Open the screenshots in `books/<id>/reference/boards/`: rings and braces must not cut through numbers, and labels must not sit on bar edges.

## 2b. Display faults: why they slipped through, and the gate for each

Every fault below reached a live book while `check_book` was green. They are not
random: each one broke an assumption that a tool and the engine did not share.
This table is the register — when a new display fault appears, add its row and
the gate that would have caught it, then add that gate to the list above.

| Symptom the teacher saw | Root cause | Assumption that broke | Gate now |
| --- | --- | --- | --- |
| Play button on top of the red answer | `answer_stamps.py` cut the stamps *after* `extract_pages.py` had placed the Play, so nothing knew the answer was there | "the answer is not on the page when the button is placed" | `nudge_plays()` + `check_answer_chips.py` |
| Play on printed text or a figure | `play_spot()` measured the answer column only | "blank under the answer column is blank on the page" | `play_spot()` pixel test + `check_answer_chips.py` |
| Step-button strip on a figure | the strip is placed at the answer card's right edge, so a region that runs over a figure drags the strip onto it | "a region never covers printed ink" | narrowed `region`, `ctlAt` for the hard cases, `measure_ctl.mjs` |
| A printed answer box or a circle cut into two | `growSheet()` inserts the band across the **whole page width**, while the cut line was chosen from the answer column only | "a row blank under the answer is blank across the page" | `check_cuts.py` (10 lines in p5m07a) |
| Printed table rule / figure hidden under a white rectangle | stamps were saved as RGB with an opaque white background | "a stamp is only its answer ink" | alpha cut-out (white → transparent) |
| Printed words or arcs drawn twice ("aand", double circle) | the crop is a rectangle round the answer, and the ANS scan sits a few points off the QUE scan | "the stamp holds only what the page lacks" | ANS↔QUE alignment + trim of dense print the page already has (`answer_stamps.py`) |
| A boxed answer lost a stroke | the trim window reached the printed box edge beside the digits | "ink near printed ink is print" | density test (9 px, ≥35%) + red ink never trimmed; the tool prints how much black it removed where the page is blank |
| Table row's Play in the header, other rows aligned | a stamp's right edge sat exactly on the measured spot, so the nudge pushed the button up and shrank it | "a pinned spot stays pinned" | `playAt` pinned in `book.json` + `check_play.mjs` |
| Stamped answers missing on the live site | `extract_pages.py` rewrites `layout.json` without stamps; a build ran in that window | "the layout always carries its stamps" | `build_deploy.ps1` throws when `answerStamps` is listed but the layout has none |
| A widget's labels cross its lines, or three labels stack on a tiny circle | the widget's own layout is not measured by any tool — the harness is eyeballed | "a widget is checked like a page" | none yet; proposed: measure each label box against the lines and the other labels, WARN under 3 px |
| A Play on blank paper that belongs to no line | the button was measured as "blank here" without asking which line it belongs to (hw7 sat between two lines) | "blank paper is enough" | `playAt` within 70 pt of `blankAt` and ≤18 pt off its own line, checked by `check_play` + `check_answer_chips` |
| A measured spot with no button on it | the stamp branch returned before drawing the graphic button, so `graphicAt` existed and q1/q11 stayed dormant | "measured means drawn" | `check_play` taps every `.ans-play[data-act="graphic"]` and fails when the drawer does not open |
| The gate itself is wrong | `check_play` selected `.ans-play`, so the amber widget button was judged against the Play's fill and glyph | "one selector covers the controls" | a new button type needs the QA selector updated in the same change (`:not(.ans-graphic)`) |

Two habits keep the register short:

1. **Measure what the engine draws, not what the tool assumes.** If the engine
   works across the full page (band insert, card right edge, strip height), the
   measurement must too. When they disagree, the engine wins.
2. **Sweep the whole book after fixing one instance.** The same fault shows up
   on every question built the same way (the four homework rows, the six table
   rows). Fix one, re-render all pages, and look at every sheet before shipping.

## 3. Visual pass (screenshots)

Open every `sheet-*.png` and `graphic-*.png` in `books/<id>/reference/qa/` and check:

- [ ] every answer box sits inside its blank space with a margin, and covers no printed text;
- [ ] the controls don't overlap the boxes, the next question or the page edge;
- [ ] the maths renders properly: no raw LaTeX and no red KaTeX errors;
- [ ] review link boxes sit on their words, and the tags stay inside the page;
- [ ] graphics have no overlapping labels, and the question card matches the solution;
- [ ] a long answer scrolls inside its region with a visible bar; wheel and drag move the answer before the page.

## 4. iPad checklist (real device, Apple Pencil)

Run this on the live link after release, or on the local Wi-Fi preview.

- [ ] The library shows the book; tapping the card opens it; the top-left brand returns to the library.
- [ ] Every page shows its printed page number, and no figure line runs through it (`python tools/qa/check_folio.py <id>`).
- [ ] Pencil writing starts instantly, with no delay between strokes; a resting palm neither scrolls nor makes marks.
- [ ] One finger scrolls and two fingers pinch-zoom, in every tool.
- [ ] A tap in a box reveals one step; ▸ » ◂ ↺ work; Show all and Hide all work.
- [ ] Dashed review links open and close on tap (finger, or Pencil in Read mode).
- [ ] Every graphic opens, and its slider and buttons respond.
- [ ] Holding still at the end of a stroke snaps it to a line, circle, rectangle or triangle.
- [ ] Tapping ink opens the edit menu (colour, size, Shape, Copy, Delete, move, resize).
- [ ] A two-finger tap undoes and a three-finger tap redoes.
- [ ] Present mode works: swipe between pages, and only the Exit button leaves. On iPad it does not use Safari full screen (no "Swipe down to exit"), so a zoomed page scrolls up and down with one finger; desktop browsers go full screen, and Esc there only drops full screen. After a two-finger pinch, one-finger drags pan without leaving the zoom; a double tap returns to the whole page.
- [ ] Export PDF opens the share sheet.
- [ ] Rotate the iPad, then close and reopen the app: the ink is still there.

## 5. Release

1. Set `"status": "live"` in `books/<id>/book.json`, and make sure the id is in `books/catalog.json`.
2. Bump `CACHE` in `sw.js` (`ebooks-v5` → `ebooks-v6`). Without this, iPads that already opened the site keep serving the old files.
3. Commit and push:
   ```powershell
   git add -A
   git commit -m "Add <code> <title>"
   git push
   ```
4. Wait about a minute, then confirm the build and the live files:
   ```powershell
   gh api repos/uniplusmathsteam-bot/jm26b-inequalities-ebook/pages/builds/latest --jq .status
   ```
   Open `https://uniplusmathsteam-bot.github.io/jm26b-inequalities-ebook/books/<id>/book.json` to confirm that it's live.
5. On the iPad, close and reopen the app (or the tab) once, so it loads the new version.

**What is public.** The GitHub repo and Pages site are public. `.gitignore` keeps out the PDFs (`*.pdf`, `books/*/source/`) and the reference crops and screenshots (`books/*/reference/`). The page images, solutions and graphics are published.

## 6. Rolling back

- **One bad release:** `git revert <commit>`, then `git push`. Ink saved on iPads is untouched, because it lives in the browser, not in the repo.
- **An aesthetic experiment:** restore from the backup folder made before the change (e.g. `… (backup before review links)`), or `git checkout <commit> -- <files>`.
- **Never** change a live book's `id` or `storage`. The saved ink is keyed by `storage`.
