<!-- canon: ebook-starter-v2/docs/tech-debt.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# 技術債台帳

一個決策：「發現了但今次唔修」的東西要有家，否則只會留在人的腦裡。方法與優先級見 skill `tech-debt-register`；本檔是資料。

**優先級次序**：錯 ＞ 誤導 ＞ 可讀性 ＞ 美觀。同一級才比成本與重犯機會。
**狀態**：`open`（未做）、`doing`、`done <commit>`、`accepted`（判為接受，寫理由）、`blocked`（等決定）。

| ID | 位置 | 症狀（可觀察） | 影響 | 修法 | 成本 | 狀態 |
|---|---|---|---|---|---|---|
| TD-001 | `books/jpfm08/widgets.js` `f.side` | 只寫不讀的死欄位，旁邊註解已過時 | 誤導下一個寫手 | 刪欄位與註解 | 10 分鐘 | open |
| TD-002 | 同上，`d ≤ 3 px` | 畫布印 `d₁ = 0 (line through P)`，右欄印 0.020 m | 同一圖兩個數 | 門檻改 `d < 0.5 px`，其餘印實數 | 20 分鐘 | open |
| TD-003 | 同上，三支力 sandbox | 1 個 `text×dot`（`F₂ 30 N` 壓 knob） | 可讀性 | 標籤避讓 | 1 小時 | open |
| TD-004 | 同上，q30 | x ≈ 0 時 500 N 箭咀整支在地面線下 | 幾何必然，已在註解寫明 | 保留 | — | accepted（與印刷對應的必然結果） |
| TD-005 | `books/p5m07a/book.json` | code 寫 `P5 Maths 07`，官方表為 `P508 Circles` | topics 對帳 | 待用戶決定改名 | — | blocked |
| TD-006 | `books/catalog.json` | 21 本中 17 本 code／title 對不上 topics list | 對帳、搜尋、分冊 | 分批重整 | 數日 | open |
| TD-007 | `tools/build_deploy.ps1:74` | explainers 由 `workspace\explainers` 抄，不是由 repo 抄；repo 內副本可以過時而無人知 | 部署出錯版本 | 改成由 repo 的 `explainers/` 抄，或加 md5 對照閘 | 半天 | open |
| TD-008 | 部署 worktree | `tools/qa/node_modules` 不入版控，乾淨 worktree 跑 `check_book` 會 `ERR_MODULE_NOT_FOUND` | 每次部署都要手動做 junction | 在 worktree 建 junction 並寫進 release-runbook | 10 分鐘（文件） | open |
| TD-009 | 共用 skill registry | 34 個 skill 只在 `state.json` 的 `capabilities.items`，其中 8 個技術 skill 冇 on-disk SKILL.md | 改不到、diff 不到、review 不到 | 匯出成 `skills/` 下的檔並版控 | 半天 | open |
| TD-010 | `workspace\skills\{ours,registry-export,registry}` | 三份源冇 sync 標記，同一 skill 可以三個版本 | drift | 每份加 `source:` 與 `synced-at:` 標頭 | 1 小時 | open |
| TD-013 | `books/jpfm08/widgets.js` q2 caption | 臂收起時 caption 仍寫「watch every arm change」，而畫布上已經冇臂 | 措辭與畫面不符（學生會找不存在的臂） | 收臂時把 caption 改成「watch d and τ in the column」或中性句 | 20 分鐘 | open（physics-lead 判為下次順手改） |
| TD-014 | `ebook-starter-v2/docs/01-workflow.md` | canon 有 49 段 `Physics only／Maths only` 附錄未精修（兩份平行重寫，唔係純增量） | 同一流程兩份寫法，維護要改兩處 | 人工逐段合併 | 半天 | open |

## 已修（保留紀錄，唔要刪）

| ID | 內容 | 何時 | 證據 |
|---|---|---|---|
| TD-011 | `ebook-qa` 把 `--shots` 當主閘，但真正印 FAIL／WARN 的是 `--verbose` | 2026-11-27 | skill 已改：`--verbose` 為閘、`--shots` 為證據 |
| TD-012 | `physics-lead` 一個 skill 都冇（`maths-lead` 有 `maths-content-review`） | 2026-11-27 | 已掛 `doc-review` ＋新 `physics-content-review` |

## 規矩

- 每項要有**可驗證的完成定義**（量到哪個數、哪張截圖、哪個閘 PASS），唔好寫「改善可讀性」。
- 已判 `accepted` 的一定要寫理由，否則三個月後有人重開。
- 修好標 `done <commit>`，唔要即刻刪——下次有人問「這個修過嗎」有得查。
- 排了優先級不等於有批准動手：上線、改 docs、改設定一樣要用戶批。
