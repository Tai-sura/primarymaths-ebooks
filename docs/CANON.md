<!-- canon: ebook-starter-v2/docs/CANON.md · 由 CTO 於 2026-11-27 三路合併記錄 · 改這份，唔好改副本 -->

# CANON.md — docs 三路合併記錄（2026-11-27）

合併人：CTO。範圍：`ebook-starter-v2/docs`（canon）／`ebook-engine/docs`（physics）／`ebook-maths/docs`（maths）三份頂層 .md。**只改 canon，冇改兩個 repo 嘅 docs，冇跑 sync_docs.ps1，冇 commit／push。**

## 合併原則

1. **底本** = 三份中「較新且較完整」的一份（按 bytes 與內容判斷；以程式／實測為準，唔靠 byte 大細一項）。
2. **另一邊獨有的段落**以 `## Physics only`／`## Maths only` 附錄原封補回，附錄標明 **「NOT yet reconciled」**——凡兩份係平行重寫（唔係純增量），我唔硬塞成一句，只保留另一邊原句等第二輪精修。
3. 只喺 canon 有嘅四檔（`00-agent-team`、`00-onepager`、`07-visuals-and-animations`、`08-films-and-narration`）＋ `chapters/_template.md`：只加標頭，內容不動。
4. `tech-debt.md` 與 `adr/` 納入 canon——兩科用同一套流程，屬團隊共用；ADR 係不可變記錄，照抄唔加標頭。
5. 每檔頂部加 HTML 註解標頭：`<!-- canon: … · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->`。

## 逐檔裁決表

| 檔 | 採用底本 | 由哪邊補了什麼 | 科目分節 | bytes | md5 |
|---|---|---|---|---|---|
| 00-agent-team.md | canon（唯此一份） | 無 | — | 28326 | 8dd4cde5 |
| 00-onepager.md | canon（唯此一份） | 無 | — | 3898 | edafbc95 |
| 01-workflow.md | **physics**（26675，最新） | 補 maths 獨有：book/chapter 詞彙表、Stage 2a＋路由圖、Intake acceptance、book.json 單一真相、make_que 90% 盒規＋3–5 回歸樣本、answerStamps、Stage 6 check_catalog／chips／play／cuts、Stage 7 tag＋check_live、Stage 8 路由＋Global change regression、JM26 Owner 欄 | Maths only 附錄（49 段，兩份係平行重寫，需精修） | 46972 | ce4b6a4c |
| 02-book-format.md | **maths**（25193，最新） | 補 physics 獨有：media/guides 的 scene class 要與 mp4 同 commit＋SOURCES.md、JPEG 抗鋸齒切線量度 | Physics only 附錄（5 段） | 29859 | 551d866b |
| 03-authoring-style.md | **maths**（14070） | 補 physics 獨有：§6 poster、§7 tool 跟線走（§9 已搬返正文） | Physics only 附錄（2 段） | 15308 | 20df82e9 |
| 04-qa-and-release.md | **physics**（18392，最新） | 補 maths 獨有：check_catalog／check_live／media 預算、check_play／check_stamps、2b 顯示故障登記表（13 行） | Maths only 附錄（22 段） | 26568 | daacded4 |
| 05-engine-notes.md | **physics**（15528） | 補 maths 獨有：card 的「? chip」描述（已統一 22 px／15×15） | Maths only 附錄（1 段） | 17857 | 81cf778d |
| 06-layout-controls-and-media.md | **physics**（21892，最新） | 補 maths 獨有：§2 Scope（出版書唔 re-cut）、§13 F/E/D 標記寫法、Known items 兩條已結案 | Maths only 附錄（10 段） | 24333 | 91b9744a |
| 07-visuals-and-animations.md | canon（唯此一份） | 無 | — | 14836 | 9da2a59a |
| 08-films-and-narration.md | canon（唯此一份） | 無 | — | 10849 | 3baeeda5 |
| chapters/_template.md | 三份相同 | 無（只加標頭） | — | 1580 | 42f065a8 |
| tech-debt.md | physics（新） | 無（團隊共用，由 physics 帶入） | — | 3938 | 72e88ad7 |
| tools.md | **maths**（7598，最新） | 無（physics 冇獨有內容） | — | 7633 | c0055cf8 |
| adr/README.md | physics（新） | 無 | — | 1022 | c44f2802 |
| adr/ADR-0001-deploy-from-origin-main-worktree.md | physics（新，照抄） | 無 | — | 2009 | 58ccdae8 |
| adr/ADR-0002-shared-cache-numbering.md | physics（新，照抄） | 無 | — | 1771 | 1cef5af2 |

## 未解決的差異（2026-11-27 已裁決 5 項，剩 1 項）

已裁決（本輪已改 canon）：1 卡片按鈕統一「control button 22 px tall（`engine/styles.css:408`）、icon 15×15（`engine/styles.css:423`）」；2 answerStamps 標 Maths only，加註 physics 現冇 stamp code；3 media 預算統一 900 KB；4 過時 repo 改返 `Tai-sura/primarymaths-ebooks`（physics 站 `Tai-sura/physics-ebooks`）；5 §9「The rules in one place」搬返共用正文。

**剩 1 項未解決：**

1. **01-workflow 附錄偏大**：physics 與 maths 係平行重寫（唔係純增量），line 級別補回出咗 49 段「Physics only／Maths only」附錄。**第二輪人工精修，未排期**——把真係共用嘅改寫合併、真係獨有嘅先留。

## 界限

- 冇改 `ebook-engine/docs`、冇改 `ebook-maths/docs`、冇改 `sync_docs.ps1`、冇 commit、冇 push。
- canon 嘅副本（兩個 repo docs）仍係舊版，要等 Chief 批先 sync 返去（今次只做 canon）。
