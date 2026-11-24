# Tools and skills we depend on

What the e-book pipeline and the film line actually run, where each piece is used, and where it
comes from. Written 2026-11-22. When something is added, removed or upgraded, update the tables
here in the same commit.

How this list was made: scan `ebook-engine/tools/qa/package.json`, `ebook-engine/vendor/`,
`vendor-pdf/`, the imports in `ebook-engine/tools/*.py` and `tools/manim/*.py`, and the git remotes
of every skill folder in the workspace. Re-run those checks before trusting it a month from now.

## 1. Libraries and binaries (GitHub open source, running every day)

| Tool | Version | What it does | Where we use it | GitHub |
| --- | --- | --- | --- | --- |
| PyMuPDF (fitz) | 2.1 | Reads the PDF, extracts the text layer, renders page images at 3x, gives the pt coordinates of every word and mark | `tools/extract_pages.py` builds `layout.json`; `tools/qa/brief.py` prints a question's printed text; every ink measurement starts here | https://github.com/pymupdf/PyMuPDF |
| pymupdf4llm | ships with PyMuPDF | PDF to Markdown/plain text | turning answer pages into `reference/ans-text/qNN.md`, so a Bot reads 1 KB of text instead of a 3x page image | same repo |
| Pillow | 13.0.0 | image crops, per-pixel ink counts, pasting folio glyphs | `tools/qa/check_folio.py`, `tools/qa/stamp_folio.py`, every crop used in a visual check | https://github.com/python-pillow/Pillow |
| numpy | 2.5.5 | array maths, image diffs | measuring highlight-band edges, frame-to-frame diffs, ink statistics | https://github.com/numpy/numpy |
| Manim Community | 0.22.1 | programmatic maths animation | guide animations and some concept panels (`tools/manim/*.py`) | https://github.com/ManimCommunity/manim |
| Perfect Freehand | bundled (`vendor/freehand`) | Apple Pencil stroke rendering | the reader's handwriting and line tools | https://github.com/steveruizok/perfect-freehand |
| KaTeX | bundled (`vendor/katex`) | maths rendering in the browser | formulas in questions and solutions | https://github.com/KaTeX/KaTeX |
| pdf-lib | bundled (`vendor/pdf-lib`) | PDF generation in the browser | Export PDF (a student's ink and answers) | https://github.com/Hopding/pdf-lib |
| Puppeteer (core) | 23.11.1 | headless Chrome | `check_book`, `measure_ctl`, `check_media`, every widget DOM measurement (iPad 1180x820, Retina, pen events) | https://github.com/puppeteer/puppeteer |
| FFmpeg | 9.0.2 (gyan build) | video encoding, frame grabs, frame diffs | Cine's films; my acceptance checks (first/last frame, 3 pt border band, contact sheets) | https://github.com/FFmpeg/FFmpeg |
| Node.js | 24.22.1 | runs the QA scripts | every `.mjs` check and screenshot script | https://github.com/nodejs/node |
| Python | 3.12 | runs extract, QA and media scripts | the whole pipeline | https://github.com/python/cpython |

Indirect (pulled in by PyMuPDF's layout features; we do not call them directly): `networkx`,
`onnxruntime`, `psutil`, `PyYAML`, `tabulate`, `pymupdf_layout`.

The three bundled libraries carry no version stamp inside `vendor/`. If one is ever replaced, note
the upstream tag in this table at the same time.

## 2. Skill kits cloned from GitHub

Different kind of thing from section 1: a folder with `SKILL.md`, scripts and templates that an
agent reads and follows, rather than a library the code imports.

| Kit | Where | What it does | Who uses it | GitHub |
| --- | --- | --- | --- | --- |
| cinecode | `workspace/cinecode` (commit `c8a3e75`) | Makes a film from code alone. Quick mode: one HTML file with Web Audio, a low-res draft, two revisions, up to about 3 minutes. Film mode: six gated steps, style frame, animatic, three.js render, layered sound. Ends in an MP4 with a -14 LUFS master. | **Cine**, every day: the 20+ projects under `films/`, the nine spem02 concept panels, the jpfm08 q25/q30/q31 animations | https://github.com/sarpstar/cinecode |
| mp-skills | `workspace/mp-skills` (commit `5863806`) | A third-party collection of engineering, productivity and misc skills (architecture reviews, grilling, release notes) | cloned but **not attached** to any e-book Bot; reference only | https://github.com/mattpocock/skills |

## 3. Local skills (not from GitHub)

These are files in this workspace, so they are ours to edit and are not upstream projects.

| Where | Skill | What it covers |
| --- | --- | --- |
| `ebook-engine/.cursor/skills/` | `build-ebook` | the whole pipeline: intake, create, regions and `space`, solutions, QA (including `check_folio`), briefing a Bot, release |
| `ebook-engine/.cursor/skills/` | `animate-summary` | Manim concept animation: overlays, palette, nothing printed may be covered |
| `workspace/skills/` | `manimce` | Manim CE recipes (attached to visual) |
| `workspace/skills/` | `teach`, `sketch-to-3d`, `scaffold-exercises`, `improve-codebase-architecture` | teaching, hand-drawn 3D, exercise scaffolding, architecture scans - none of them part of the e-book line |
| `workspace/skills/` | `motion-graphics` | present but has no `SKILL.md` |

## 4. Our own repositories

| Repo | What it is |
| --- | --- |
| https://github.com/Tai-sura/physics-ebooks | The published site (GitHub Pages). Four books: phy11, phy06-force2, spem02, jpfm08. |
| (local only) `ebook-engine` | The engine, tools and the four book folders. Never pushed; only the built site is. |

## 5. Evaluated and not installed

| Project | Why not |
| --- | --- |
| Rive (https://github.com/rive-app/rive-docs) | The best fit if a rigged 2D character is ever needed (free editor, MIT runtime, vector line art). Not installed yet: no page currently has room for a moving figure (jpfm08 q30 needed 121 px and had 30). |
| DragonBones (https://github.com/DragonBones/DragonBonesJS) | Free and open, but a 2D sprite/bone system older than Rive; not worth adopting for one film. |
| Spine (https://github.com/EsotericSoftware/spine-runtimes) | Editor is paid; runtime alone does not help. |
| AnimatedDrawings (https://github.com/facebookresearch/AnimatedDrawings) | Rigs a drawing and drives it with mocap, but the motion set has no climbing, and it needs OpenCV plus PyTorch and a clean silhouette. |
| three.js + Mixamo | A real climbing clip exists, but 3D shading clashes with the printed line art on the page. |
| rtk (Rust Token Killer) | Hooks only work under Bash, we run pwsh, and it truncates the coordinates and checksums the QA depends on. |
| Graphify | Useful for "what touches this module"; not better than grep for finding the exact write site. Pilot only, no install. |

## 6. Keeping this file honest

- Versions: `python tools/qa/brief.py` style one-liners are not enough; check
  `tools/qa/package.json` (Node), `vendor-pdf/*.dist-info` (Python), `ffmpeg -version`,
  `node --version`, `python -V`.
- Skill kits: `git -C workspace/<kit> remote -v` and `git -C workspace/<kit> log --oneline -1`.
- Anything new that a Bot starts using belongs in a table here in the same turn it is introduced,
  including why it was chosen over the alternative.
