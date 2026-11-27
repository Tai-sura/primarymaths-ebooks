# ADR-0001 — 部署只由建在 `origin/main` 的乾淨 worktree 做

狀態：已接受 · 2026-11-27 · 相關：`docs/01-workflow.md` Stage 7、`REPO.md`、commit `c5d0ca7`／`893614f`

## 背景

`ebook-engine` 這條本地 clone 的 `main` 與 GitHub 上的 `origin/main` 是**兩條沒有共同祖先的歷史**。本地有大量未推送的工作（`docs/topics/`、`tools/import_topics.py`、各書的治療紀錄），而線上只認 `origin/main`。

結果是：在本地 clone 上 commit 的內容**永遠不會出現在網站**，而 `git status` 看起來一切正常。這件事至少浪費過一輪工作。

## 決定

1. 任何要上線的改動，都在**新建的 worktree** 上做，起點必須是 `origin/main`：
   `git worktree add <path> --detach origin/main`
2. 改動用「由已知 commit 取 blob」的方式帶入（`git show <commit>:<path>`），不要整棵樹倒過去，也不要 `git checkout` 本地的檔案。
3. 部署樹跑過閘（`check_book`／`measure_ctl`）才算數；跑之前按需要把 `tools/qa/node_modules` 以 junction 接上（它不入版控）。
4. 部署樹 commit、打 `pre-<book>-v<N>` tag，push `HEAD:main`。
5. 本地 clone 保持原狀，只做作者工作區，不是部署來源。

## 被否決的選擇

| 方案 | 為什麼不做 |
|---|---|
| 在本地 `ebook-engine` 上 commit 再 push | 兩條歷史無共同祖先，推上去會被拒或造成混亂的合併 |
| 直接把檔案覆蓋到 `deploy-*` clone | 沒有閘、沒有 commit 紀錄，出錯時回不去 |
| 用 GitHub 網頁上載檔案 | 做不到多檔同步、無 tag、無 diff |

## 後果

- 好處：部署有單一來源、有 tag 可回滾、本地工作不受影響。
- 代價：每次要多一步建 worktree、帶入檔案；`tools/qa/node_modules` 要手動接（已記在 `docs/tech-debt.md` TD-008）。

## 何時重看

- 本地 clone 與 `origin/main` 合併成一條歷史之後。
- 出現第二個需要部署的科目 repo 而流程不同時。
