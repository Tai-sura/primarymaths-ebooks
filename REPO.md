# This repository — primary maths e-books

**Subject: primary maths.**
Site: <https://tai-sura.github.io/primarymaths-ebooks/>

The physics books are in a different repository: `Tai-sura/physics-ebooks`
(<https://tai-sura.github.io/physics-ebooks/>). Nothing physics is authored here,
and nothing maths is authored there.

---

## 1. What is the truth

- The truth is **`origin/main` of this repository**. Nothing else is a base to build on.
- Deploy from a **clean worktree created from `origin/main`**. A local clone whose `main`
  has its own unrelated history can never be pushed (no common ancestor, so no merge);
  see section 5.
- Every deploy that changes a file the reader fetches bumps `CACHE` in `sw.js`; a docs-only
  or tools-only change does not, because bumping would send every iPad to re-download the
  page images for nothing. The number must be the **next free number across both
  repositories** — this site and the physics one share one counter. If the physics
  repository already shipped `v159`, the next maths deploy is `v160`.
- The cache **name carries this site's prefix**: `const PREFIX = "primarymaths-ebooks-"; const
  CACHE = PREFIX + "v<N>";`. Both sites are one origin, so they share one CacheStorage, and
  `activate` may delete only caches under this site's own prefix. See
  `docs/adr/ADR-0003-per-site-cache-prefix.md`.
- Tag every deploy, and record the commit, tag and CACHE in the report. Three naming lines,
  because a tag should say what kind of release it is:
  - `pre-<book>-v<number>` — a book release, e.g. `pre-p5m07a-v174`.
  - `pre-sw-v<number>` — a release that touches only `sw.js`, e.g. `pre-sw-v190`.
  - `pre-docs-<change>-v1` — docs or ADR only, named after the change: `pre-docs-canon-v1`,
    `pre-docs-fix-v1`, `pre-adr0004-v1`. No book and no cache number moved, so the number
    would say nothing about what is being rolled back.

## 2. What belongs in the catalogue

`books/catalog.json` decides what the site shows. Primary maths only:

| code | title | form |
|---|---|---|
| p5m07a | Circles (A) | P5 |

Physics codes (`phy*`, `spem*`, `jpfm*`, `jpwm*`) must **never** appear here.
**`node tools/qa/check_subject.mjs` fails on them.**

## 3. The older maths books are not here

The 15 books of the earlier junior-maths setup — `jm03b jm03c jm26b jm27a jm27b jm27c
jm29a jm29b jm29c jm29d jm29e jm30a jm30b jm30c m211-4` — live in the **physics** repository
as frozen folders outside its catalogue, purely so that the links students already hold
keep answering 200. They are not to be processed: no re-authoring, no new widgets, no
layout work, no re-extraction. Their files are not duplicated here.

If one of them ever has to be worked on again, that is a decision for the owner first.

## 4. Shared engine — each repository keeps its own copy

`engine/` is duplicated in the two repositories and the copies have drifted apart.
They are **not** re-synced wholesale. A fix is made in the repository that needs it; if
the other site needs the same fix, it is **ported as a patch** and then checked in both
places.

Current engine trees — update this table in **both** `REPO.md` files after any engine change:

| repository | engine tree | recorded at |
|---|---|---|
| physics-ebooks | `0139772a` | `44fde62` |
| primarymaths-ebooks | `7aa77ca4` | `f1450d9` |

If the two ids differ, that is expected and not a fault — but a fix that should be on both
sites must be ported, not assumed.

## 5. Local clones that must never be pushed

| folder | what it is |
|---|---|
| `workspace\ebook-maths` | a clone whose `main` is an unrelated history (66 commits, no common ancestor with `origin/main`), with a few unpushed edits in `books/p5m07a`, `tools/extract_ans_refs.py` and `docs/06-layout-controls-and-media.md`. It is **frozen**: never push it, never merge it. Salvage single files onto a clean worktree when they are needed. |

## 6. Docs and tools

`tools/` lives **here** and is the shared tooling; the physics repository carries only its
own `tools/qa`, added 2026-11-27.

`docs/01-workflow.md` … `06-layout-controls-and-media.md` are now carried by **both**
repositories. The physics repository committed its own copy on 2026-11-27, taken from its
local clone, which held the newer edits (the printed-figure rule, the physics-lead sign-off
at Stage 0 and Stage 7). Only `03-authoring-style.md` was newer here, and that one was
copied from this repository into that one.

From now on the documents drift the same way `engine/` does: edit the copy you are working
in, port as a patch only when the other site needs the change, and never overwrite a whole
file from the other repository.

`docs/chapters/` holds the notes for the maths books only (`jm*`, `m211-4`, `p5m07a`, plus
the template). The four physics chapter notes (`jpfm08`, `phy11`, `spem02`,
`phy06-force2`) were deleted from here on 2026-11-27; they live in the physics repository.

`docs/topics/` carries the **maths** topic registry — `maths.json`, 176 topics and 371
subtopics, imported from the official list on 2026-11-26 — with a `README.md` holding the
level-1 table. `tools/check_topic.py` checks a book's `code` and `title` against it and
loads only the registries present here, so the physics registry is never consulted.

`consistency.md` was not copied either: it is a generated report over the old combined tree.
Note that running the checker on `p5m07a` fails — its code is `P5 Maths 07`, and the
official list has no such code (the P5 circles topic is `P508 Circles`). That is a known
book-code issue in this repository, not a fault of the registry.

## 7. Checks

```
cd tools/qa && npm install          # once: puppeteer-core (needs a local Chrome)
node tools/qa/check_book.mjs p5m07a --verbose
node tools/qa/measure_ctl.mjs p5m07a
node tools/qa/check_subject.mjs     # catalogue vs subject
node tools/qa/check_live.mjs p5m07a # after a push: is the live site serving this build?
```

`tools/qa/check_book.mjs`, `measure_ctl.mjs` and `check_media.mjs` here differ in content
from the copies in the physics repository, which have moved on with the physics work.
That is the drift described in section 4: check a fix in the repository you are changing,
and port it only when it is actually needed on the other site.
