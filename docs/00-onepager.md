<!-- canon: ebook-starter-v2/docs/00-onepager.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

<!-- canon: ebook-starter-v2/docs/00-onepager.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# 一頁紙：開一個 e-book AI agent team

> 給第一次接觸的科組同事。完整版見 `docs/00-agent-team.md`，可跑的程式見 `ebook-starter` repo。

## 成品是什麼

原始 PDF 頁當底圖，疊上**逐步解答**（點一下揭一步）、**review link**（題目關鍵字連到解答）、**互動圖**、**概念面板動畫**、**Apple Pencil 墨跡層**，iPad 可離線閱讀。

## 誰做什麼

| 角色 | 負責 | 你不給它碰 |
|---|---|---|
| **Chief**（統籌）| 共用引擎 `engine/`、QA 工具、部署 | — |
| **ebook**（課本）| 由 PDF 到頁面、答案區、逐步解答、QA | `engine/`、`widgets.js` |
| **visual**（圖解，可後加）| 互動圖、面板動畫、解答動畫 | `engine/`、`solutions.js` |
| **你**（科主任／作者）| 定範圍、批部署、最終驗收 | — |

三個角色都由你開的 Bot 擔任；一個 agent 也可以先做完全部，但**引擎只有一個人有鑰匙**。

## 七步開一本書

```powershell
# 0) 一次性：裝 Python 套件、Node 依賴
pip install pymupdf pillow numpy
cd tools\qa; npm install; cd ..\..

# 1) 驗環境（會告訴你缺什麼、怎麼補）
python tools\check_env.py

# 2) 開書（換成你的兩份 PDF）
python tools\new_book.py mybook --form S4 --code "PHY CH11" --title "Projectile Motion" `
  --topic "Projectile Motion" --que "C:\path\QUE.pdf" --ans "C:\path\ANS.pdf"

# 3) 草擬題目清單 → 貼進 book.json 的 extract.questions
python tools\extract_pages.py mybook --scan

# 4) 渲染頁面 + 自動答案區域
python tools\extract_pages.py mybook

# 5) 裁老師筆跡（寫解答的唯一依據）
python tools\extract_ans_refs.py mybook

# 6) 寫 books\mybook\solutions.js（逐步解答）

# 7) QA（交付條件，不是可選）
cd tools\qa
node check_book.mjs mybook --shots
node measure_ctl.mjs mybook      # 尾行必須 PASS
```

預覽：`python -m http.server 8090` → `http://127.0.0.1:8090/reader.html?book=mybook`

## 五條鐵律（每一條都是真實錯誤換來的）

1. **`engine/` 只有一個人改。** 一個檔影響所有書；改完每本書都要重跑 QA。
2. **切口要落在量度出來的空白行。** 切錯會把一行的分子分母劈開 —— 掃頁圖找整行無墨跡的位置，不要靠肉眼。
3. **答案區不可伸入頁腳。** 頁腳在切口之上不會移動，區域一伸進去，答案就蓋住頁腳。
4. **動畫對版要抽中間格。** 只比首／尾格會漏掉「疊加元素飛出框」這類錯（我們壞過一整輪）。
5. **部署要先得批准，並升 `sw.js` 版本號。** 不升，iPad 會繼續用舊檔。

## 兩種 PDF，兩條路

| 你的 PDF | 額外要做什麼 |
|---|---|
| 老師**手寫紅框答案** | 用 `extract_ans_refs.py` 裁筆跡，`solutions.js` 逐行照老師寫法 |
| **Word / LaTeX 原稿** | 通常不需要 `make_que.py`；把原稿匯出成 PDF 當底圖，解答由原稿轉成 `m()`/`t()` 的行 |

兩種都可以用同一個引擎；分別只在第 1 與第 3 階段的人工。

## 第一週建議

1. 揀**一課 10–20 題**做 pilot，不要一次開一個科組
2. 先把「最密的一頁」（最多字、最多圖）跑一次階段 2 + 3 —— 看答案空間夠不夠
3. 不夠就用 `tools\relayout_pdf.py` 在 PDF 內開位（該頁會高過 A4，列印要縮放，要通知老師）
4. pilot 上線後，把踩到的坑寫回 skill，第二本開始就會快一倍

## 想深入

- 流程：`docs\01-workflow.md`
- 版面風格：`docs\03-authoring-style.md`
- QA 與上線：`docs\04-qa-and-release.md`
- 完整角色與 skill 說明：`docs/00-agent-team.md`
