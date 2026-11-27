<!-- canon: ebook-starter-v2/docs/02-book-format.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# Book format

A book is one folder, `books/<id>/`, containing the files below. The engine never contains chapter content: anything specific to one book goes in its folder.

| File | Who writes it | Purpose |
| --- | --- | --- |
| `book.json` | you, starting from `new_book.py` | chapter details, sections, question list, region overrides |
| `layout.json` | `tools/extract_pages.py` | page sizes, answer regions, printed text positions |
| `pages/pNN.jpg` | `tools/extract_pages.py` | page backgrounds (3× zoom) |
| `solutions.js` | you | the worked solutions and review links |
| `widgets.js` | you | the interactive graphics |
| `source/` | `new_book.py` | the QUE and ANS PDFs (not published) |
| `reference/` | tools | teacher crops and QA screenshots (not published) |

Coordinates are always in **PDF points**, measured from the top left of the page. An A4 page is 595.32 × 841.92. Page numbers start at 1, the same as the QUE PDF.

---

## book.json

```json
{
  "id": "jm26b",
  "form": "S3",
  "code": "JM26 (B)",
  "title": "Inequalities I",
  "topic": "Inequalities",
  "year": 2026,
  "status": "live",
  "storage": "jm26b",
  "source": { "que": "source/…(QUE).pdf", "ans": "source/…(ANS).pdf", "ansPageOffset": -1 },
  "sections": [{ "id": "practical", "label": "Practical" }],
  "extract": { "zoom": 3, "regionX": [66, 546], "footer": 822, "questions": [], "anchors": {}, "fixedAnchors": {}, "overrides": {} }
}
```

| Field | Meaning |
| --- | --- |
| `id` | Folder name and URL key (`reader.html?book=jm26b`): lower case letters, digits and hyphens. |
| `form`, `code`, `title`, `topic`, `year` | Shown in the library and the reader's top bar; searched by the library filter. The library groups books by `form`. |
| `status` | `draft` or `live`. Any value other than `live` is shown on the library card. |
| `storage` | Prefix of the saved-ink database (`<storage>-ebook`) and UI settings (`<storage>-ui`) on the device. **Never change it for a book in use**, or the teacher's ink disappears. It defaults to `id`. |
| `source.que`, `source.ans` | PDF paths relative to the book folder. |
| `source.ansPageOffset` | ANS page minus QUE page. It is −1 when the ANS has no cover page. |
| `sections` | Top-bar buttons, in order. Each jumps to the first question with that `section`. |
| `media` | Optional animations laid over printed panels: `[{ "page", "region": [x0, y0, x1, y1], "scene": "module:Class", "src": "media/x.mp4", "poster": "media/x.jpg", "title" }]`. The scene is a Manim class in `tools/manim/<module>.py`; `python tools/render_media.py <id>` renders `src` and `poster` (its last frame), and `--still` saves layout previews to `reference/media/`. The poster covers the panel until the round ▶ button on its corner is tapped. An entry may also carry `"widget": "<id>"` (and `"widgetTitle"`): a widgets.js graphic that belongs to the same printed panel, opened from one more round button beside ▶ — the panel's interactive version. |
| `guides` | Optional figure animations that walk through a question's solution: `[{ "q": "q5", "scene": "module:Class", "src": "media/guide-q5.mp4", "poster": "media/guide-q5.jpg" }]`. The question's control strip (or, for a printed answer, its corner chip) gets a film button that opens the video in a dialog. The scene (a `GuideScene` from `tools/manim/guide.py`) sets its own `PAGE` and `REGION`; the poster is the first frame, the plain figure. `python tools/render_media.py <id> --still` saves `reference/guides/<Class>_cmp.png` (print above the first frame) and `<Class>_sheet.png` (a frame every 2 s). `python tools/audit_guides.py <id>` lists every label that touches a mark, another label or the frame edge. |
| `embeds` | Optional interactive explainers (the published pages under `/explainers/`) opened from a tab in the page margin: `[{ "page": 3, "at": [1.5, 410.75], "title": "力矩平衡：蹺蹺板（q3、q5）", "sub": "Moment balance", "src": "explainers/moment-balance/moment-balance.html" }]`. `at` is the tab's top-left corner in page points and **must sit on measured blank margin** — the tab is 20 × 22 pt, so measure the page JPEG first (see `check_embed.mjs`, which fails a tab that leaves the sheet). Tapping it opens a full-screen panel with the page in an iframe, so the explainer keeps its own layout and its own no-scroll rules; closing drops the iframe and its sketch. `src` is relative to the site root, so one path works from `books/<id>/` and from a local server. `node tools/qa/check_embed.mjs <id> [site-root]` opens every tab and checks the explainer draws with no scroll inside its frame; `python tools/qa/check_embed_tabs.py <id>` maps each tab back through the page cuts and reports the darkest page pixel under it (must be ≥ 245, so no tab sits on printed ink). More than one entry may point at the same `src`, e.g. a tab beside the question and a second one on the figure's top-right corner. |
| `endPages` | Optional pages after the printed ones, in order: `[{ "key": "summary", "label": "Summary", "image": "pages/summary.png", "source": "tools/sheets/<id>-summary.html" }, { "key": "cards", "label": "Flashcards", "deck": "flashcards.js" }]`. The sheet key is `end-<key>` and ink is saved under it, so **never rename a key** once the book is in use. `image` is an A4 picture (render an HTML page with `node tools/qa/render_sheet.mjs <page.html> <out.png>`, which also warns about overlapping or spilling blocks); `source` only records where it came from. `deck` is a module in the book folder exporting `DECK` for `engine/deck/deck.js` (see the comment at its top for the card and figure format). A deck page is a landscape slide at the notes' width (`DECK_H` = 380 pt, or `"height"` on the entry) so presentation mode shows the whole card, including the score. It takes the laser pointer but no ink, and is left out of the PDF export and print. The page label reads "Summary · 9 / 10". |
| `widgets` | Set to `false` if the book has no `widgets.js`. |
| `answerScale` | Optional book-wide type size at reader 100% (default 1). Every answer uses this size; a long answer scrolls inside its region. |
| `answerCards` | `["q1", …]`: these questions' working opens in a card from a `?` chip at the top-right of their fill-in line; every other question keeps the in-page working, page cuts and `space` (see "Answers in a card"). Use it for fill-in questions on worksheet pages; leave MC and long questions out. |
| `answerStamps` | `["q1", …]`: these questions show the teacher's own red answer, cut from the ANS page, pasted back at the same spot (see "Answers stamped from the ANS page"). The tightest match to the printed key: no working, no card, and the page never moves. For a fill-in worksheet this is usually what the teacher wants. |
| `answers` | `"cards"`: the whole book uses cards (no page is ever cut). Only for a book where every page is a worksheet with no blank space; otherwise use `answerCards` or `answerStamps`. |
| `extract.zoom` | Render scale for the page images. Keep 3: sharp on a Retina iPad at about 200 KB per page. |
| `extract.regionX` | Left and right edges of a default answer region. |
| `extract.footer` | y where the page footer starts; the last region on a page stops 4 pt above it. |
| `extract.questions` | `[{ "id", "page", "label", "section" }]` in reading order. `--scan` drafts this. |
| `extract.anchors` | `{ id: regex }` for headings such as "Example 1". Numbered questions are found automatically from "12." at the left margin. |
| `extract.fixedAnchors` | `{ id: [y0, y1] }` when there is no searchable text (e.g. a second method under one example). |
| `extract.overrides` | `{ id: { "region": [x0, y0, x1, y1], "square": [...], "ring": [...], "space": N } }`, merged into the generated item. `square` is an MC answer box, filled with `letter` once all steps show. `ring` circles a printed option when the answer is complete. `space` opens N points of blank page under the region (cut at the region's own bottom) so a short answer can show in full without scrolling. |

### A `media` entry's mp4 and poster are one pair

The poster covers the printed panel until ▶ is tapped, so it must look like the
video's **first** frame: a poster left over from an older render makes the panel
jump the moment playback starts. Replace both files in the same change, and pull
the poster from the new mp4 rather than reusing the page crop:

```powershell
ffmpeg -y -i books/<id>/media/<name>.mp4 -vf "select=eq(n\,0)" -frames:v 1 books/<id>/media/<name>-poster.png
```

The poster must equal frame 0 pixel for pixel (SSIM 1.0). `render_media.py` writes
the *last* frame by default, which only fits a scene that ends on the printed page
— for a panel that starts from it, take frame 0 as above. `check_media.mjs` counts
the 900 KB budget per `src` file, so a light poster beside a 130 KB clip is fine.


---

### Answer space and page cuts

`space` opens blank page under the region by cutting the page at `region[3]` and moving everything below that line down. Two rules follow, and both are checked by eye, not by a counter:

- the cut must fall in a blank row of the page image (scan `pages/pNN.jpg`; 1 pt = 3 px at zoom 3). A cut inside a printed row tears that row in two — on phy11 a cut at 540 split an MC option's fraction, and the denominator moved to the next slice;
- every `region[3]` stays above the printed footer (where the footer row sits near 797.6, use `region[3] ≤ 790`). A region reaching into the footer draws the answer over it, because the footer lies above the cut and does not move.

`extract_pages.py` picks the band itself: the largest ink-free rectangle under the question. When a page has no such band it records a 2 pt band on a blank row just under the question's own text (`blank_row_below()`), never an inverted region — an inverted band (`region[3] < region[1]`) makes the reader cut the page *above* the answer card, so the card then sits on the next question's text.

When a page has no usable gap — content runs straight into the footer, or an option square crosses every candidate line — do not cut at all. Either put the working beside the options, or open the page inside the PDF:
```powershell
python -X utf8 tools/relayout_pdf.py <in.pdf> <out.pdf> --page 7 --at 796.8 --add 150
```

That keeps every printed mark where it is (only what lies below the cut moves down) and makes the page taller than A4, which is why `layout.json` records a height per page and the reader honours it.

### Answers stamped from the ANS page (`answerStamps`) — Maths only

> **Maths only.** Physics has no stamp code today (`engine/viewer/answers.js` has none); if a physics book wants stamps later, go back to Stage 2 and re-do extraction plus `answerStamps`.

For a fill-in worksheet the answer *is* the red mark on the ANS page: a word in a red box, a number, a circle round the choice. Copying that mark is a closer match to the printed key than any re-typesetting, and it answers "show me the answer, not an explanation".

`python -X utf8 tools/answer_stamps.py <id>` (also run by `extract_pages.py` when the list exists) finds the red ink on each ANS page, groups it per question — by the band between a question's own line and the next one, clipping a mark that crosses a band edge — cuts each group with a 2 pt white margin into `books/<id>/answers/pNN_<qid>.png`, and records it:

```json
"stamps": [{ "img": "answers/p03_q01.png", "rect": [135.8, 150.0, 199.5, 179.2] }]
```

The reader draws that PNG over the page at `rect` (page points, so it lands exactly where it was on the key) and lays nothing else out: no card, no `space`, no page cut. Each stamp has a small Play button at the top-right of its line: press it and the answer appears in its blank, press it again and it hides. Show all / Hide all drive every stamp. the page reads exactly as printed until the answer is asked for. MC and long questions keep the in-page working.

That Play is **the same button as an inline answer's** (`.ctl button[data-act="next"]` in `engine/styles.css`): 24 × 22 pt, 6 pt corner, `--ink` fill, white `▸` at 14 pt. One book shows one Play. Two things keep it that way:

- `engine/styles.css` `.ans-play` resets `min-width` / `min-height`. The reader's global `button` rule sets a 40 × 40 touch target, and a `width: 13px` on the button does not beat it — without the reset the button renders as a big circle.
- `layout.json` records where each button goes as `playAt`, measured by `play_spot()` in `tools/extract_pages.py`: flush with the text column's right edge on the line that carries the blank, nudged a few pt and then walked left along that line until the rendered page is blank there, and never out into the page margin — the reader's docked toolbar sits over the last ~18 pt. A mark's bounding box counts as occupied (white inside a printed circle is still the circle), so a figure reaching the column edge pushes the button into the free strip beside it; a scanned page, whose one page-sized image covers the whole sheet, puts its buttons in the left margin. `book.json` can override `playAt` per question.

Run `check_book.mjs` afterwards: it fails when a stamp falls outside the page or has no image, and a missing PNG shows up as an HTTP 404. Re-running `extract_pages.py` re-cuts every stamp, so a page change cannot leave a stale answer behind.

### Answers in a card (`answerCards`)

A worksheet page such as `p5m07a` has no blank paper under a question — the next question starts 10 pt below — and several questions sit beside one big figure or inside a printed table, so there is no blank row to cut at without tearing the figure or the table. Those **fill-in questions** get their working in a card; MC and long questions keep the usual in-page working:

```json
"answerCards": ["q1", "q2", "q3", "q4"]
```

A whole book like that can use `"answers": "cards"` instead, which makes every answer a card. For a question in the list:

- the printed page never moves and is never cut (`space` is ignored for it);
- a control button 22 px tall (`engine/styles.css:408` `.ctl button`) whose 15×15 `?` icon (`engine/styles.css:423` `.ctl button svg`) sits at the **top-right of the printed line that carries the blank**: `layout.json` records that spot as `cardAt` (the extractor finds the row with the underscores, so a blank on the question's second line still gets its chip on that line, not beside the question number). The chip steps right, then above or out into the margin, if printed ink is there;
- tapping it opens a card over the page with that question's worked solution at the book's type size, wrapped to the card's width, with the usual step buttons (▸ » ◂ ↺) and a ✕; Escape or a tap outside closes it. The card opens with the whole working shown — a `?` tap is a lookup — and ↺ hides the steps again;
- the card is as tall as the working needs (up to almost the page height) and scrolls only if the working is taller than that.

MC and long questions are **not** in the list: they keep the region, the page cut and `space`, exactly as in the physics books.

`py -3.12 tools/qa/check_answer_chips.py <id>` reads `layout.json` and the page images and fails when a chip or a Play button covers printed ink, or when two Play buttons share a box. `node tools/qa/check_play.mjs <id>` proves it in a real browser: one Play per stamped answer, measured and painted exactly like the LQ Play, none under the toolbar, and a tap that opens and closes the answer. `node tools/qa/check_book.mjs <id>` opens every card once, so its fit and scroll warnings cover cards too.

`python -X utf8 tools/layout_triage.py <id>` says which questions need a card (see Stage 2a of [01-workflow.md](01-workflow.md)).


## layout.json (generated)

Re-run `python tools/extract_pages.py <id>` after any `book.json → extract` change. Never edit layout.json by hand. It contains:

- `pages[n].width`, `height`;
- `questions[]`: `{ id, label, section, anchor: [y0, y1], region: [x0, y0, x1, y1], square?, ring?, space? }`;
- `text[]`: printed rows `[y0, y1, [[x0, x1, "word"], …]]`. The highlighter snaps to these, and review links search them for `q` phrases.

### What the reader draws, and when each piece is made

Display faults on this site have almost all come from one part being measured
while another part was not yet known. Keep this order in mind:

| Piece | Made by | Drawn by | What it must clear |
| --- | --- | --- | --- |
| `region` | `extract_pages.py` | `answers.js` | printed ink at the cut line **across the whole page width** |
| `playAt` / `playSize` | `play_spot()` in `extract_pages.py` | `.ans-play` | printed ink, and the red answer stamp |
| `graphicAt` / `graphicSize` | second `play_spot()` call, Play box in `taken` | `.ans-play.ans-graphic` | printed ink, the stamp, and the Play |
| the step strip | `placeCtl()` in `answers.js`, from the card's right edge | `.ctl` | printed ink beside the region |
| stamps | `answer_stamps.py`, **after** the layout | `.ans-stamp` | nothing: they carry only ink the printed page lacks |

Two rules follow:

1. `extract_pages.py` rewrites `layout.json` **without** the stamps; always run
   `tools/answer_stamps.py <id>` after it, and never build in between (the build
   refuses a book whose `answerStamps` list has no stamps in the layout).
2. A stamp is cut from the ANS scan and pasted on the QUE scan. The two scans are
   a few points apart, so the stamp keeps only ink the QUE page does not already
   print; red ink is never trimmed because that is the answer.

---

## solutions.js

```js
import { m, t, h, note, nl, tree, table, grow, align, L, lk } from "../../engine/authoring.js";

export const SOLUTIONS = [
  {
    id: "q1",
    links: [
      { key: "al", color: "amber", note: "at least → $\\ge$", q: ["is at least 23"] },
    ],
    boxes: [{
      steps: [
        m(`11 - 2(x + 2) ${L("al", "{} \\ge 23")}`),
        m("-2(x + 2) \\ge 12", "− 11"),
        m("x \\le -8", "÷ (−2): reverse the sign"),
        t("$\\therefore$ The greatest value of $x$ is $-8$."),
        nl({ min: -12, max: -4, op: "le", at: -8 }),
      ],
    }],
  },
];
```

### Question fields

| Field | Meaning |
| --- | --- |
| `id` | Must match an `id` in `book.json → extract.questions`. |
| `boxes` | One red answer box per item, laid out left to right and wrapping, like the ANS key. |
| `boxes[].steps` | The lines of that box, in reveal order. |
| `boxes[].w` | Fixed box width in points (otherwise the box fits its content). |
| `boxes[].left` | Page x where this box should start, to line it up under a part of the question. |
| `boxes[].bare` | No padding or fill, only the red outline: for a `table` with `at` that fills a grid printed on the page. |
| `flow: "col"` | Stack the boxes in columns instead of rows. Good for long MC working beside the options. |
| `nowrap: true` | Keep the boxes in one row instead of wrapping. A long answer scrolls inside its region at the book's type size. |
| `letter` | MC answer letter shown in the `square` override once all steps show. Leave it out to keep the square empty. |
| `printed: true` | The worked solution is already printed on the page: no answer boxes, only a graphic button at `ctlAt: [x, y]`. |
| `links` | Review links (below). |

### Step kinds

| Helper | Shows | Notes |
| --- | --- | --- |
| `m(tex, reason?)` | display maths (KaTeX) | e.g. `m("x > 14", "÷ 4")` |
| `t(text, reason?)` | a sentence | `$inline maths$`, `\\$` for a dollar sign, `**bold**`, `[[key|words]]` to link plain words |
| `h(label)` | part heading such as "(a)" | not a step: never hidden, not counted |
| `note(text)` | a teacher's margin note | same syntax as `t` |
| `nl({ min, max, op, at, dots?, mark? })` | HKDSE number line | `op`: `lt`, `le`, `gt`, `ge`. `dots`: integers marked in red. `mark`: one highlighted value. It is optional: dropped first when space is short. |
| `tree({ label?, cols?, kids, out?, sep?, mark? })` | tree diagram with a dashed line to each outcome | `kids`: nested `[label, kids]` pairs; `grow(["H", "T"], ["1", "2", "3"])` builds a tree where every stage has the same choices. `label`: part label at the top left. `cols`: bold column headers, one per stage plus one for the outcomes (pushed right so they never overlap). Outcomes are the labels on the path joined by `sep` (default ""), or `out[i]`. `mark`: outcome indexes or texts shown in red. |
| `table({ rows, top?, left?, head?, side?, strike?, hl?, u?, at? })` | table of outcomes | `rows`: arrays of cell text (`$maths$` allowed). The first `head` rows and `side` columns (default 1 each) are bold headers; `top` / `left` are captions above and beside the table. `strike` and `hl`: `[[r, c], …]` cells crossed out "╱" or highlighted. `u: true` underlines the body cells. `at: { xs, ys }`: page points of a grid already printed on the page; only the cells are drawn, there are no headers, and the text scales to the row height. |
| `align(steps)` | wraps a step list | Each "= …", "≈ …" or "> …" display line hangs under the first relation of the line that starts its chain, as printed keys do. |
| `lk(key, step)` | marks a whole step as the answer side of link `key` | |
| `L(key, tex)` | marks part of the maths as link `key` | Start with `{}` when the part begins with an operator, e.g. `L("lt", "{} < 4")`, so KaTeX keeps the spacing. Links can be nested. |

The reason (`r`) appears in small blue handwriting beside the line. Keep it to a few words.

### Review links

```js
links: [
  { key: "bc", color: "pink", note: "$BC = x$", q: ["BC = x cm"], at: 1 },
]
```

| Field | Meaning |
| --- | --- |
| `key` | Short id, unique within the question. The answer side uses it via `L()`, `lk()` or `[[key|…]]`. |
| `color` | `pink`, `blue`, `green`, `amber` or `purple`. |
| `note` | The remark tag text (inline `$maths$` allowed). Keep it short: "at least → $\\ge$". |
| `q` | Phrases in the printed question. They are matched word by word, ignoring case and punctuation; a phrase may wrap across lines. One link may have several phrases. |
| `at` | Which marked answer part the tag points to (0-based, default 0). |

---

## widgets.js

```js
import { C, S, T, scene, clear, slider, readout, question, buttonRow } from "../../engine/widgets/kit.js";

function q2(root) { /* append a question card, an SVG scene, a slider and a readout to root */ }

const REGISTRY = { q2 };
export function hasGraphic(id) { return Boolean(REGISTRY[id]); }
export function mountGraphic(id, root) { REGISTRY[id]?.(root); }
```

The engine calls `mountGraphic(id, root)` with an empty drawer body each time the graphic button is pressed. A question gets a graphic button only if `hasGraphic(id)` is true.

### Kit (`engine/widgets/kit.js`)

| Export | Use |
| --- | --- |
| `C` | Palette: `ink`, `red`, `green`, `amber`, `blue`, `pink`, `grey`, `line`, `paper`, `soft`, plus `*Soft` tints. |
| `S(tag, attrs, parent)`, `T(svg, x, y, text, attrs)`, `H(tag, attrs, kids)` | Create SVG elements, SVG text and HTML elements. |
| `scene(w, h)` | An SVG canvas with arrow markers; `clear(svg)` empties it but keeps the markers. |
| `marker(svg, "arr" / "arrInk" / "arrGreen" / "arrRed" / "arrAmber")` | Arrowhead reference for `marker-end`. |
| `axis(svg, { x, y, w, min, max, step, label, every })` | A number line; returns `X(value)` → pixel. |
| `ray(svg, X, y, at, "left"/"right", closed, color, { min, max })` | An HKDSE solution set on that axis. |
| `pin(svg, x, y, color, text, { up, level })` | A labelled marker on an axis; `level` stacks labels. |
| `bar`, `dashed`, `sector`, `regular(n, cx, cy, R)` | Bars, dashed guides, angle sectors, regular polygon points. |
| `slider({ label, min, max, step, value })` | Slider with − / + / ▶. Methods: `.el`, `.get()`, `.set(v)`, `.on(fn)`. |
| `readout()` | Live check. `.set(latex, ok, caption, labels)` shows ✓ satisfies or ✗ fails; `ok` null hides the chip, and `labels: { yes, no }` changes its words. |
| `question(text, lets)`, `intro(text)` | Question card with "Let …" lines; an intro paragraph. |
| `tabs(names, onChange)`, `buttonRow([[label, fn], …])` | Part tabs and quick-value buttons. |
| `tex(latex, display)`, `fmt(n, dp)`, `P(n)`, `niceStep(span)` | KaTeX span, number formatting, brackets for negatives, tick spacing. |

For a full example of each kind of graphic, see `books/jm26b/widgets.js`:
- slider pictures: Q2, Q4;
- number lines with pins: Example 1, Q5–Q8;
- x–y range pictures: Q19–Q22;
- MC statement checkers: the `MC` table.

For percentages, growth and decay, see `books/jm27a/widgets.js`: `timeline()` (bars per period, unknown slider, target or threshold line), `change()` (original vs new bar), and the area pictures in Q9 and Q10.

### `playAt` / `playSize` / `blankAt`

`playAt` 是填充題 Play 按鈕的左上角（pt），放在該題填充位的右上角；`playSize` 是它的大小（預設 `[24,22]`，
窄位可縮到 `[14,12]`，`engine/viewer/answers.js` 按此畫）；`blankAt` 是量到的填充位中心（第三個數字是該行文字右端），
供 QA 證明按鈕貼住自己嗰格。量唔到（掃描頁冇文字層）時 `blankAt` 為 `null`。


---

## Physics only (verbatim from the physics repo — NOT yet reconciled with the base above)

| `media` | Optional animations laid over printed panels: `[{ "page", "region": [x0, y0, x1, y1], "scene": "module:Class", "src": "media/x.mp4", "poster": "media/x.jpg", "title" }]`. The scene is a Manim class in `tools/manim/<module>.py`; `python tools/render_media.py <id>` renders `src` and `poster` (its last frame), and `--still` saves layout previews to `reference/media/`. The poster covers the panel until the round ▶ button on its corner is tapped. An entry may also carry `"widget": "<id>"` (and `"widgetTitle"`): a widgets.js graphic that belongs to the same printed panel, opened from one more round button beside ▶ — the panel's interactive version. The scene class is part of the delivery: commit `tools/manim/<module>.py` in the same commit as the `mp4` and the poster, and add its row to `books/<id>/media/SOURCES.md` (source, rebuild command, duration, size, md5) — a film the repo cannot rebuild is not delivered, see [06-layout-controls-and-media.md § 17](06-layout-controls-and-media.md). |
| `guides` | Optional figure animations that walk through a question's solution: `[{ "q": "q5", "scene": "module:Class", "src": "media/guide-q5.mp4", "poster": "media/guide-q5.jpg" }]`. The question's control strip (or, for a printed answer, its corner chip) gets a film button that opens the video in a dialog. The scene (a `GuideScene` from `tools/manim/guide.py`) sets its own `PAGE` and `REGION`; the poster is the first frame, the plain figure. `python tools/render_media.py <id> --still` saves `reference/guides/<Class>_cmp.png` (print above the first frame) and `<Class>_sheet.png` (a frame every 2 s). `python tools/audit_guides.py <id>` lists every label that touches a mark, another label or the frame edge. A guide's scene class is committed with its video in the same commit, and listed in `books/<id>/media/SOURCES.md`, as for `media`. |

| `answerCards` | `["q1", …]`: these questions' working opens in a card from a labelled **Answer** control button (22 px tall `engine/styles.css:408` `.ctl button`, 15×15 `?` icon `engine/styles.css:423` `.ctl button svg`) at the top-right of their fill-in line; every other question keeps the in-page working, page cuts and `space` (see "Answers in a card"). Use it for fill-in questions on worksheet pages; leave MC and long questions out. |
| `answers` | `"cards"`: the whole book uses cards (no page is ever cut). Only for a book where every page is a worksheet with no blank space; otherwise use `answerCards`. |

**Measure the cut on the image the reader actually serves.** The reader displays `pages/pNN.jpg` (`engine/book.js:53`), which `extract_pages.py` writes with `jpg_quality=86` (`tools/extract_pages.py:299`). JPEG puts 1–2 pt of anti-aliasing around every printed edge, so a row that is white in a fresh PDF render can carry grey pixels in the JPG that gets cut; measuring the PDF hides exactly those rows. Measure the saved `pages/pNN.jpg` (1 pt = 3 px at zoom 3) and require the cut row to be clear **across the whole page width**, not just across the region's x range, with 0 px below 245; inside the region itself require 0 px below 170. On jpwm01 a cut at 782.0 passed a PDF-render check and still carried 7 px below 245 in the JPG (the anti-aliased top of an option's glyphs), while 780.5 was clear.

- a control button 22 px tall (`engine/styles.css:408` `.ctl button`) with a 15×15 `?` icon (`engine/styles.css:423` `.ctl button svg`) sits at the **top-right of the printed line that carries the blank**: `layout.json` records that spot as `cardAt` (the extractor finds the row with the underscores, so a blank on the question's second line still gets its button on that line, not beside the question number). The button moves right, then above or out into the margin, if printed ink is there, and it is kept inside the page edge;
- tapping it opens a card over the page with that question's worked solution at the book's type size, wrapped to the card's width, with the usual step buttons (▸ » ◂ ↺) and a ✕; Escape or a tap outside closes it. The card opens with the whole working shown — the button is a lookup, not a puzzle — and ↺ hides the steps again;

`py -3.12 tools/qa/check_answer_chips.py <id>` reads `layout.json` and the page images and fails when a chip covers printed ink. `node tools/qa/check_book.mjs <id>` opens every card once, so its fit and scroll warnings cover cards too.
