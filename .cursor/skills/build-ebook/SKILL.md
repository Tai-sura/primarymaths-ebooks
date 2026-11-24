---
name: build-ebook
description: >-
  Turn a teacher's question PDF and answer PDF into a book on this static ebook
  reader (books/<id>, solutions.js, layout, QA, release). Use when the user
  adds a chapter, booklet, or notes — mathematics, physics, chemistry, or
  biology — or mentions QUE/ANS PDFs, book.json, solutions.js, answer regions,
  or the ebook platform.
---

# Build an ebook chapter

The reader is a static site: `reader.html?book=<id>`, shared `engine/`, and one folder `books/<id>/`. Follow `docs/01-workflow.md`. This skill is the order of work and the rules that are easy to get wrong. Field lists live in `docs/02-book-format.md`, house style in `docs/03-authoring-style.md`, release in `docs/04-qa-and-release.md`. What the pipeline depends on (libraries, GitHub skill kits, local skills, and what we decided not to install) is in `docs/tools.md` - add to it when a tool enters or leaves the pipeline.

A chapter is the same shape in any subject. Only the notation changes (see Subjects).

## Rules that apply to every book

- The book id is the ink store on every iPad. Choose it once (`jm29c`) and never rename `id` or `storage`.
- The QUE page is the background. Nothing covers the printed question. Answers sit in the blank space, in the same order and with the same final sentence as the teacher's red working.
- Do not invent steps, values, reagents, or mechanisms the notes do not contain. If the answer PDF and the question disagree, stop and ask.
- `books/<id>/source/` (the PDFs) and `books/<id>/reference/` (crops, QA shots) are gitignored. Never commit a PDF. Never commit `reference/`.
- On PowerShell, run Python as `python -X utf8` with `$env:PYTHONIOENCODING="utf-8"`. Write a script file instead of a long `python -c`.
- Before a change that alters how answers look, copy the project folder aside so it can be reverted in one step.
- Decide how the answers show **before** writing solutions, from the notes' own layout (`tools/layout_triage.py`, stage 2b): a workbook keeps the in-page working; a worksheet's fill-in questions open a card from a `?` chip at their blank line, and MC/long questions stay inline. Record the choice in `docs/chapters/<id>.md`.
- Bump `CACHE` in `sw.js` on every release (`ebooks-v17` → `ebooks-v18`). Commit and push only when the user asks.

## 0. Intake

Need the QUE PDF (blank working space) and the ANS PDF (the same pages with the teacher's working). Record form, code and title as printed, the book id, and the top-bar sections. Copy `docs/chapters/_template.md` to `docs/chapters/<id>.md` and keep decisions there.

**Only an answer PDF was supplied.** Build the question paper with `tools/make_que.py`, then treat its output as the QUE. It removes the pure-red answer frames (stroke redder than the notes' own frames, at least 28×16 pt), the text and drawings inside them, the "Answer" stamp, and the `*` on an MC option. A figure that merely touches a box is kept.

```powershell
python -X utf8 tools/make_que.py "<ANS>.pdf" "books/<id>/source/<QUE made>.pdf" --red-text list
```

`--red-text cover` removes red writing outside a box. `--red-text black` turns red text black, which is what a correct MC option printed in red needs. `--stamp WORD` when the stamp is not "Answer".

Check every page against the ANS before going on: every figure still there, no red working left. The first version of this blanking deleted whole images that touched a box and the live books lost their figures.

## 1. Create

```powershell
python tools/new_book.py <id> --form S3 --code "JM29 (C)" --title "Quadrilaterals" --topic Quadrilaterals --que "<QUE>.pdf" --ans "<ANS>.pdf"
```

This copies `books/_template/`, stores both PDFs, fills `book.json`, and adds a `draft` row to `books/catalog.json`. Set `sections` from the notes' own headings. Set `source.ansPageOffset` (0 when both PDFs have the same page count; -1 when the ANS has no cover).

`books/_template/widgets.js` ships an **empty `REGISTRY` on purpose**. Never leave a worked example in the template: whatever is registered there opens from a question's graphic button in every new book, and a mathematics example in a physics book reaches students (jpfm08 shipped the marble inequality that way). Register only the graphics you write for that book.

## 2. Pages and answer regions

```powershell
python tools/extract_pages.py <id> --scan
```

Copy the printed draft into `extract.questions`. Numbered questions use `q1`… and need no anchor. Examples and practices need `extract.anchors` (`{"ex1": "Example\\s*1"}`). `label` is what the jump list shows. Give each question a `section` id.

```powershell
python tools/extract_pages.py <id>
```

Writes `pages/pNN.jpg` (zoom 3, JPEG quality 86) and `layout.json`. A region runs from the bottom of the question to the next question, clipped at `extract.footer`.

When the working must sit on the teacher's own box (MC beside the options, a framed example), set `extract.overrides[id].region` to that box in PDF points, origin top-left, page 595×842. Add `square` for a printed MC answer box and `ring` for an option to circle. One point is 3 pixels on the page image.

Then grow those boxes into the blank space around them and rebuild:

```powershell
python tools/grow_regions.py <id> --write
python tools/extract_pages.py <id>
```

Read `books/<id>/reference/regions/`. The growth must not swallow the next question, a figure, or the footer.

```powershell
python tools/extract_ans_refs.py <id>
```

One crop per red box in `reference/ans/`. Solutions are transcribed from these crops, not from memory.

## 2b. Decide how the answers show

Run this before stage 3: the notes' own layout decides it, and changing it later means redoing regions, `space` and QA.

```powershell
python -X utf8 tools/layout_triage.py <id>
```

| The notes | Verdict | Set |
| --- | --- | --- |
| A workbook with a blank band under each question | inline (physics way) | `space` in `extract.overrides` where the working needs room |
| A worksheet: questions ~10 pt apart, figures/tables crossing every row, fill-in blanks | cards for the fill-in questions, inline for MC and long questions | `"answerCards": [...]` in `book.json` |
| Every page a worksheet with no answer space | cards for the whole book | `"answers": "cards"` |

A card's `?` chip sits at the top-right of the printed line that carries the blank (`layout.json` `cardAt`, from the row with the underscores), so a blank on the question's second line gets the chip on that line. Cards never cut or move the printed page; MC and long questions keep the page cut, so a book can mix both.

An inverted region (`region[3] < region[1]`) makes the reader cut above the answer and the card lands on the next question's text. `extract_pages.py` no longer writes one and `check_book.mjs` fails on it; never hand-edit `layout.json` to work around it.

Record the decision and the `answerCards` list in `docs/chapters/<id>.md` under **How the answers show**.

## 3. Solutions

`books/<id>/solutions.js`, one entry per question, in page order. Helpers from `engine/authoring.js`:

| Helper | Use |
| --- | --- |
| `m(tex, reason?)` | one algebra or equation step, display maths |
| `t(text, reason?)` | a sentence; `$inline$`, `**bold**`, `[[key\|words]]` |
| `h("(a)")` | part heading; always visible, not counted |
| `note(text)` | the teacher's pink margin remark |
| `nl({min, max, op, at})` | HKDSE number line |
| `L(key, tex)`, `lk(key, step)` | the answer side of a review link |

One box per part where the key has side-by-side boxes. `flow: "col"` stacks long working beside options. `printed: true` plus `ctlAt` when the working is already printed and only a graphic button belongs there. Leave `letter` off an MC question unless the teacher wants the letter filled in.

Every answer uses one type size. The engine tries the authored layout, then equations broken before "=", then side-by-side columns, then a flowing wrap; if the answer is still taller than its region it scrolls inside it (visible scroll bar). Parts printed as `(a)` `(b)` on one row get each box under its own label. Prefer `flow`, a box `w`, or `space` in `extract.overrides` (opens the page under the region) when a short answer should show in full without scrolling.

Side reasons (the second argument of `m()` / `t()`, and `note()`) are **plain text**: no `$...$`, no TeX command, and no maths-only symbol such as `u_x` — a reason renders literally, so write words ("horizontal speed is constant"). A long `\therefore` sentence belongs in `t()`, never `m()`: `m()` cannot wrap, and the engine shrinks the whole line to fit, down to 50 %.

## 4. Review links

On every word problem, `links` tie a short phrase of the question to the matching step. `q` phrases must match the printed words; matching ignores case and punctuation. Skip pure-algebra questions and printed examples. Link the phrase that maps to a step, not the whole sentence. The phrase must sit in a printed row **below** the question's anchor row: the matcher only searches the rows under the anchor, so wording in the anchor row itself (often the first printed line, such as "1.0 m away") is reported as `phrase not found` — take wording from the line after it. Copy the printed spelling exactly: `ms-1` with an ASCII hyphen, `42o` with the letter o when that is what the page prints.

## 5. Pictures

**Before you brief anyone on a question, read the question.** A brief written from memory of what "q36" or "the V–I one" says has produced three wrong briefs in one evening (an axis direction reversed, a question invented, a hinge put on the wrong side), each costing a wasted round trip. One command gives you the ground truth — printed lines, the solution entry, and a crop of the printed figure:

```powershell
python tools/qa/brief.py <book-id> <qid>
```

Quote the printed facts in the brief itself ("printed: O on the right, force at A on the left; solution: tau = 20 sin(theta) (2)"). A brief that quotes the page lets the person doing the work check it, and that check is what caught the invented q36. State the rule for them too: *if this brief contradicts the page, stop and report instead of building.*

A slider graphic goes in `books/<id>/widgets.js`, registered in `REGISTRY`, built with `engine/widgets/kit.js`. Copy the shape of `books/jm26b/widgets.js`: a question card in the solution's own letters, a picture of the situation, a slider, a live readout. Use pictures, bars, number lines and shapes. No function graph unless the class has learned graphs. No label may collide at the slider's ends.

A printed concept panel (a theorem box, a law, a family tree) is an animation instead. Follow [animate-summary](../animate-summary/SKILL.md).

A question marked with the green diamond gets a solution guide: its printed figure animated through the teacher's steps, opened from a film button (`guides` in `book.json`, scenes in `tools/manim/<id>_guides.py` built on `guide.py`). There are no written lines, because a narrator speaks over it. Colour equal parts alike, and show each reason as a motion (fold, half-turn, slide, angles gathering on a line). Answers appear in bold red with no box. Labels keep clear of wedges, arcs and lines, and words never grow (unknowns flash red in place): `python -X utf8 tools/audit_guides.py <id>` must report every scene clean. After re-rendering, bump `CACHE` in `sw.js`, because the service worker would keep serving the old video under the same name. Check every scene with `python -X utf8 tools/render_media.py <id> <Class> --still` (`reference/guides/<Class>_cmp.png` and `_sheet.png`), one render at a time. See `docs/01-workflow.md`.

## 6. QA

```powershell
cd tools/qa
npm install
node check_book.mjs <id> --shots
```

Fix every `FAIL`. Read every `WARN`. A `FAIL` includes a reason that still contains raw TeX (`\angle`, `$...$`); write the symbol. Run the strip check as well — `node measure_ctl.mjs <id>` must end `PASS` (the step strip never covers the working, in four layout paths). Then check that **every page really shows its printed page number**: `python tools/qa/check_folio.py <id>` must end `ok all N pages show their page number`. The PDF text layer can carry a folio the rendered page does not show ??a figure, a rule or a white box sits on it ??so the tool measures ink in the folio's own box on `pages/pNN.jpg` and flags any page where something else crosses that box (`LOOK`) or where the box is empty (`MISS`). Fix a `MISS` as in `docs/05-engine-notes.md` ??Page numbers??. Then open every `sheet-*.png` and check what no counter can: options and their answer squares whole, the footer intact, no printed row cut in two, every revealed line complete. A clean WARN count proves none of that. Open the screenshots in `books/<id>/reference/qa/` and the iPad list in `docs/04-qa-and-release.md`. After an engine change, run `check_book.mjs` for every book in `books/catalog.json`.

## 6b. Answer space on a page with no room left

What a region can hold is fixed by the printed page: the blank that is already there, plus what `space` opens. When the working still does not fit, fix the page — never the working, never a printed mark.

- **A region's bottom edge is the `space` cut.** The cut must land in a *measured blank row* of the page image (1 pt = 3 px at the 3x render; scan for rows with no dark pixel). A cut inside a row tears it: on phy11 the cut at 540 split option D's fraction and pushed its denominator to the next slice; the blank rows were 546.7–558.7, so 550 was correct.
- **Keep every region bottom above the printed footer** (the footer row starts near 797.6; use ≤ 790). A region that reaches into the footer draws the answer over it, because the cut sits at the region's bottom and everything above the cut — including the footer — stays put.
- **Two `space` regions on one page add their insertions.** Give a region an explicit `space` with a hand-chosen cut; an answer that overflows a region without one gets an implicit cut wherever `cutFor()` finds a clear row, which nobody chose.
- **No usable gap on the page?** (content runs straight into the footer, an answer square or option crosses every candidate line) Then do not cut at all: put the working beside the options, or open the page in the PDF:

  ```powershell
  python -X utf8 tools/relayout_pdf.py <in.pdf> <out.pdf> --page 7 --at 796.8 --add 150
  ```

  It keeps every printed mark where it is (only what lies below the cut moves down) and makes that page taller, so it is no longer A4 — say so in the hand-over, and remember the reader needs the per-page height (`layout.json` `pages[n].height`).
- **Measure, do not eyeball.** `layout.json` `pages[n].text` gives every printed row's y and x, and `pages/pNN.jpg` gives the ink runs; a phone screenshot is not a measurement.
- A page that mixes a taller page with a `space` cut is the fragile case: check the whole page in one screenshot (`sheet-*.png`), not just the question.

## 7. Release

Set `"status": "live"`. Bump `CACHE` in `sw.js`. Update the book table in `README.md` and `docs/chapters/<id>.md`. Commit and push only when asked. The live site is GitHub Pages on `main`: `https://uniplusmathsteam-bot.github.io/jm26b-inequalities-ebook/reader.html?book=<id>`.

## Subjects

The pipeline does not change. Notation and what a "good picture" is do change.

**Mathematics.** KaTeX through `m()` and `$...$`. Angles and triangles as `∠` `△` in text, never raw TeX in a reason. Number lines follow `docs/03-authoring-style.md`: stem, hollow or filled circle, arrow.

**Physics.** Quantities with units in the teacher's notation (`$F = ma$`, `$9.8\,\mathrm{m\,s^{-2}}$`). A graphic is the situation: a free-body sketch, a ray, a circuit, a motion bar. Do not add a graph of a function the form has not learned. Keep the teacher's symbol for a vector; do not switch notation mid-solution.

**Chemistry.** Equations as KaTeX. The vendored KaTeX has no mhchem. To get `\ce{H2O}`, copy `mhchem.min.js` from the **same** KaTeX release as `vendor/katex/` into `vendor/katex/contrib/` and load it in `reader.html` immediately after `katex.min.js`. State symbols and charges must match the notes `(s)`, `(aq)`, `^2+`. Do not balance an equation the teacher left unbalanced, and do not add conditions (heat, catalyst) they did not write. A graphic is a particle picture or apparatus sketch, not a lab procedure.

**Biology.** Prose plus short labels. Keep the notes' terms (do not rename a process). A graphic is a labelled drawing or a cycle with the notes' own arrows and names. Do not add stages, organs, or causes the page does not list.
