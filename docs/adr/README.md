<!-- canon: ebook-starter-v2/docs/adr/README.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# ADR（技術決策記錄）

每一份 ADR 一頁，寫「為什麼這樣做」與「為什麼不做其他選擇」。方法與格式見 skill `adr`。

## 命名

`ADR-<四位數>-<短 slug>.md`，四位數連續、不重用。新決策取代舊的時，不要改舊檔：開新一份，並在舊檔的狀態寫「已取代（由 ADR-NNNN）」。

## 索引

| 編號 | 標題 | 狀態 | 日期 |
|---|---|---|---|
| [ADR-0001](ADR-0001-deploy-from-origin-main-worktree.md) | 部署只由建在 `origin/main` 的乾淨 worktree 做 | 已接受 | 2026-11-27 |
| [ADR-0002](ADR-0002-shared-cache-numbering.md) | 兩個站的 CACHE 號碼共用一組，一號一內容 | 已接受 | 2026-11-27 |

## 規則

- 一頁為限，細節用連結。
- 必寫「被否決的選擇」與「何時重看」——半年後最常問的就是這兩個。
- 日期與 commit hash 要查，不要憑記憶寫。
