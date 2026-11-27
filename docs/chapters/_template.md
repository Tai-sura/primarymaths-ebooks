<!-- canon: ebook-starter-v2/docs/chapters/_template.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

<!-- canon: ebook-starter-v2/docs/chapters/_template.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# <code> <title> (`<id>`)

| | |
| --- | --- |
| Form | |
| Book id / storage | `<id>` (never rename) |
| Source | `books/<id>/source/` QUE (… pages), ANS (… pages, offset …) |
| Status | draft |
| Live | `reader.html?book=<id>` |

## Source facts

- Page structure (cover, sections and the pages they span):
- Fonts or design notes that matter for layout:
- MC answers from the ANS:

## Question map

| Section | Questions | Pages | Notes |
| --- | --- | --- | --- |
| | | | |

## How the answers show

Decision from `tools/layout_triage.py`, recorded before the solutions were written (see Stage 2a of [01-workflow.md](../01-workflow.md)):

| | |
| --- | --- |
| Mode | inline / `answerCards` / `answers: "cards"` |
| Why the notes need it | |
| `answerCards` list (card books) | |
| `space` overrides (inline questions) | |

## Special cases

Regions overridden, printed examples, fixed anchors, layout options (`flow`, `minScale`, `nowrap`, box `w` / `left`) and why each was needed.

## Graphics

| Question | Graphic | Notes |
| --- | --- | --- |
| | | |

## Review links

Coverage, and any questions skipped (with the reason).

## Feedback log

| Date | Request | What changed |
| --- | --- | --- |
| | | |

## Known warnings

Output of `node tools/qa/check_book.mjs <id>` that was reviewed and accepted.
