<!-- canon: ebook-starter-v2/docs/00-agent-team.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

<!-- canon: ebook-starter-v2/docs/00-agent-team.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# 用 AI Agent Team 製作數理 e-book

**角色分工、技能清單、品質閘門，以及一套可複製的生產線**

版本：2026-11-20
依據：一條已上線的生產線（15 本數學 / M2 書 + 1 本物理書，共 16 本），不是設計稿
對象：其他科組想開自己 AI agent team 的同事

---

## 0. 一頁摘要

一套 e-book 生產線由 **3 個核心 AI agent + 1 個人類決策者** 組成：

| 角色 | 負責 | 一句話 |
|---|---|---|
| **Chief**（統籌）| 共用引擎、部署、跨角色驗收 | 唯一有權改 `engine/` 與推上線的人 |
| **ebook**（課本）| 階段 0–4、6：由 PDF 到頁面、答案區、逐步解答、QA | 把老師的筆記變成可讀的書 |
| **visual**（圖解）| 階段 5：互動圖、概念面板動畫、解答動畫 | 讓看不見的推理看得見 |
| **人類**（科主任／作者）| 定義範圍、批准部署、最終驗收 | 唯一的批准權 |

相鄰但非必需：**Cine**（短片）、**粵配**（粵語配音）。

六支資料夾內的 skill 就是這條生產線的 SOP：`ebook-intake`、`ebook-extract`、`ebook-solutions`、`ebook-manim`、`ebook-widgets`、`ebook-qa`。

**實測規模**（一本 10 頁、20 題的物理書）：20 段逐步解答（204 個步驟）、13 個 review link、4 段面板動畫、2 個互動圖，`book.json` + `solutions.js` + `widgets.js` 合共約 40 KB 原始碼。

**配套文件**：`docs/00-onepager.md`（給第一次接觸的同事，一頁紙）與 **`https://github.com/Tai-sura/ebook-starter`**（private；可 clone 的最小 repo：引擎 + 模板書 + 工具 + QA，117 個檔案、2.4 MB，不含任何課本）。兩份文件都已放進該 repo 的 `docs/`。

---

## 1. 成品是什麼

一本 e-book 不是「重排的網頁教科書」，而是**把原始 PDF 頁當底圖**（3× 渲染）疊上互動層：

- **原始頁面當背景** —— 版面、字型、題號、圖與印刷完全一樣，學生認得
- **逐步解答** —— 寫在頁面原有的空白／答案區內，點一次揭示一步
- **review link** —— 題目關鍵字連到解答的對應位置，兩邊同時高亮
- **互動圖** —— 滑桿拖參數，圖即時變，附即時讀數與 ✓/✗ 判斷
- **概念面板動畫** —— 覆蓋頁面上的一塊總結圖，最後一格等於印刷圖
- **Pencil 墨跡層** —— 鋼筆、螢光筆、擦膠、雷射筆、選取、兩指 tap 復原、演示模式
- **離線可用** —— service worker 快取，iPad 裝到主畫面

網址形式：`https://<org>.github.io/<repo>/reader.html?book=<id>`，前端 `index.html` 是書庫。

---

## 2. 為什麼要一隊 agent，而不是一個

不是為了好看，是三個物理限制：

1. **上下文長度**：一本書 20 題的解答是 17 KB 程式碼 + 20 張老師筆跡裁圖 + 10 頁版面座標。一個 agent 同時做「量版面」與「寫 20 題解答」，會在中途忘記前面的座標決定。
2. **失敗模式不同**：版面錯誤是「像素級」的（切口切斷分數線），解答錯誤是「數學級」的（跟錯老師解法），動畫錯誤是「時間軸級」的（疊加元素飛出框）。同一雙眼睛看不出三種錯。
3. **寫入衝突**：`engine/` 一個檔案影響 16 本書。兩個 agent 同時改引擎，一次 regression 就會把 16 本書一起弄壞。

所以分工的界線不是「誰擅長什麼」，而是**誰可以寫哪個檔案**。

---

## 3. 團隊名冊

### 3.1 五個角色

| Bot | 角色標籤 | 負責階段 | 手上 skill | 可以改 | 絕對不碰 |
|---|---|---|---|---|---|
| **Chief** | 統籌 | 跨階段、部署 | 診斷、寫作、handoff 等通用 | `engine/`、`tools/qa/`、`docs/0x`、sw.js 版本、`book.json` 的 `media` 條目 | 各書的 `solutions.js` 內容 |
| **ebook** | 課本 | 0–4、6 | `ebook-intake`、`ebook-extract`、`ebook-solutions`、`ebook-qa` | `books/<id>/`（除 widgets/media）、`docs/chapters/<id>.md`、`tools/` 的新工具 | `engine/`、`widgets.js`、部署 |
| **visual** | 圖解 | 5 | `ebook-widgets`、`ebook-manim`、`manimce`、`ebook-qa`、（`sketch-to-3d`）| `books/<id>/widgets.js`、`tools/manim/<module>.py`、`books/<id>/media/` | `engine/`、`solutions.js`、region、`book.json` 的 `media`/`guides`（要先問）|
| **Cine** | 短片 | 獨立線 | `sketch-to-3d`（+ 短片工具鏈）| `films/` | 書的任何檔案 |
| **粵配** | 配音 | 獨立線 | `cantonese-tts`、`cantonese-tts-lexicon` | `voice/` | 書的任何檔案 |

### 3.2 每個角色的實際職責

**Chief（統籌）**
- 維護共用引擎：`engine/` 19 個檔案、305 KB，被 16 本書共用
- 維護 QA 工具：`check_book`、`measure_ctl`、`check_media`、`check_boards`
- 每次改引擎都要做 regression（例：jm29c 18 WARN、jm30a 23 WARN，改前改後必須相同）
- 批 `book.json` 的 `media` 條目（region、title、`ctrl` 偏移）
- 部署：升 `sw.js` 快取版本、推 GitHub Pages、線上核實
- 跨角色仲裁：`widgets.js` 的外觀 vs 引擎的滑桿尺寸這類交界問題

**ebook（課本）**
- 由 QUE / ANS 兩份 PDF 開書、渲染頁面、定答案區
- 寫 `solutions.js`（最大的工程：一本 20 題 = 204 個步驟）
- 加 review link（字眼必須與印刷逐字相符）
- 跑兩支自動 QA、逐頁看截圖
- 交部署前的完整清單給 Chief

**visual（圖解）**
- `widgets.js`：互動圖（滑桿、即時讀數、✓/✗ 判斷）
- `tools/manim/`：概念面板動畫與解答動畫（Manim Community）
- 由 `pages/pNN.jpg` 量出所有座標，寫成常數
- 出 `_cmp.png` 對版，抽中間 frame 逐格看，合格才出片

### 3.3 為什麼「引擎只有一個人有鑰匙」

一條規則救過 16 本書：**`engine/` 只有 Chief 可以改**。

曾經有位 agent 為了修一題的排版，改了 `engine/viewer/answers.js` 的 `answerRight()`，結果 jm29c 由 18 WARN 變 19、jm30a 由 23 變 24。修一題，壞兩本。做法：`git checkout` 還原，改成在 `book.json` 加 `space`。

引擎改動的代價不是「改那一行」，是「驗 16 本書」。

---

## 4. 六支 ebook skill：功能與效果

### 4.1 對照表

| skill | 階段 | 輸入 | 輸出 | 它擋住什麼錯 |
|---|---|---|---|---|
| `ebook-intake` | 0–1 | QUE + ANS 兩份 PDF | `books/<id>/` 骨架、catalog 條目 | ANS 頁碼偏移錯，之後每題解答都對錯題 |
| `ebook-extract` | 2 | PDF、`book.json` | `pages/*.jpg`、`layout.json`、答案區 | 切口切斷印刷行、區域壓到頁腳 |
| `ebook-solutions` | 3–4 | 老師筆跡裁圖、題目 | `solutions.js` | 跟錯解法、一步塞兩步、側註顯示原樣 TeX |
| `ebook-manim` | 5a | 頁面座標 | 概念面板動畫 / 解答動畫 | 疊加元素飛出相機框、與印刷線不貼合 |
| `ebook-widgets` | 5b | 題目與物理 | `widgets.js` | 向量尾巴不在物體中心、標籤重疊、滑桿被切 |
| `ebook-qa` | 6–7 | 整本書 | QA 報告、截圖、上線 | 「自動全綠但人眼一看就錯」 |

### 4.2 逐支說明

**`ebook-intake`（第 0–1 階段）**
把兩份 PDF 變成書的骨架。三個工具：`new_book.py`（建目錄、寫 book.json、加入 catalog）、`make_que.py`（只有 ANS 時反推一份乾淨的 QUE：移除紅框答案、Answer 印章、MC 星號）、`extract_ans_refs.py`（裁出老師每題的紅框筆跡，寫解答時唯一的依據）。
**最易錯**：`source.ansPageOffset`。ANS 通常沒有封面，所以 ANS 頁 = QUE 頁 − 1。寫錯一個數字，之後每一題的解答都會對錯題。**book id 一旦定下永不可改**，它是每部 iPad 的筆跡儲存鍵。

**`ebook-extract`（第 2 階段）**
座標系是全條線最易錯的地方：單位是 PDF points，原點左上，一頁 595×842，頁面圖 3× 渲染，所以 **1 pt = 3 px**。
`region` 的四種 override：`region`（框住範圍）、`space`（加答題空間）、`square`（印刷答案格）、`ring`（要圈選的選項）。
**硬規則**（真實踩過）：`space` 的切口就是 `region[3]`，必須落在量度出來的空白行上。曾有一題切在 540，正好切斷選項 D 的分數線 —— 分子留在上一片、分母被推到下一片。實測 D 的墨跡止於 546.7、下一題文字由 558.7 起，切 550 才對。
另一條：所有 `region[3]` 必須在頁腳之上（本稿頁腳由 797.6 起，用 ≤ 790），否則答案會蓋住頁腳 —— 因為頁腳在切口之上、不會隨 `space` 移動。

**`ebook-solutions`（第 3–4 階段，最大的工程）**
`engine/authoring.js` 提供 `m()`（數學行 + 右邊理由）、`t()`（文字行）、`h()`（分段）、`note()`（旁註）、`align()`（模仿印刷 key 的等號對齊）、`L()` / `lk()`（把某段標為 link 的答案端）。
六條規矩：跟老師解法（依據是筆跡裁圖，不是自己覺得更好）、一步一行、最終答案加底線、該給理由就給、分段用 `h()`、印刷例題只給圖示。
**最易錯**：側註是純文字，不可有 `$…$`，也不可寫 `u_x` 這種只存在於數學的寫法（會原樣顯示）。
review link 的 `q` 字眼必須與印刷**逐字相符**（`ms-1` 不是 `ms−1`、`42o` 不是 42°），而且必須落在該題 anchor 行之下。

**`ebook-manim`（第 5 階段：動畫）**
兩個產物：**guides**（貼在印刷圖上的解答動畫）與 **media**（覆蓋一塊面板的概念動畫，最後一格 = 印刷圖）。
座標用頁面點重建印刷圖，`--still` 出 `_cmp.png`（印刷圖在上、最後一格在下）先對版。
**2026-11-20 新加的硬規則**：`_cmp.png` 只證明首／尾格 —— 兩者都是印刷圖。曾有一段動畫的疊加箭頭尖端飛出相機框 21 pt、畫面只剩一個浮著的 θ，`--still` 照樣 PASS，壞了一整輪。此後出片前必須抽 3–4 個中間 frame 逐格看。

**`ebook-widgets`（第 5 階段：互動圖）**
`engine/widgets/kit.js` 提供 `scene()`、`S()`、`T()`、`question()`、`sector()`、顏色常數。一個好 widget 有五個元素：題目卡、圖、滑桿、即時讀數、快捷按鈕。
**新加規則**：向量由物體**正中心**畫（用戶原話：「在物體的正中心垂直向下」）；不可為了避開版面而改物理 —— 要加高畫布（實測 250 → 270 px）。

**`ebook-qa`（第 6–7 階段）**
四支腳本：`check_book`（8 類 fail：JS / console / request error、pencil 沒留墨、揭步不是剛好 +1、link 字眼找不到、link 沒有標記答案端、側註顯示原樣 TeX、end page 壞、catalog 沒列）、`measure_ctl`（四條版面路徑量揭步按鈕有沒有壓住答案文字，尾行必須 `PASS`）、`check_media`（每段動畫真的能播）、`check_boards`。
**最重要的一課**：兩支全綠仍然不夠，必須逐頁看 `sheet-*.png`：選項 A–D 與右側方格完整、頁腳完整、沒有印刷行被切成兩半、每行答案完整。

### 4.3 支撐 skill（可選）

| skill | 用途 | 何時需要 |
|---|---|---|
| `manimce` | Manim Community 最佳實踐（camera、updaters、timing、axes 的 rules 索引） | 寫或改 Manim 動畫 |
| `sketch-to-3d` | 把 3D 模型畫成手繪 marker 草圖逐筆動畫（MIT，dannystuart） | 短片轉場、3D 概念圖 |
| `writing-for-agents` | 寫 skill / AGENTS.md / Bot 指令的方法 | 建立或修改這個團隊本身 |

---

## 5. 引擎與工具地圖

```text
index.html            書庫（前端）：讀 books/catalog.json
reader.html           閱讀器：reader.html?book=<id>
sw.js                 離線快取（每次部署必須升版本號）
engine/               共用引擎，19 個檔案、305 KB，16 本書共用
  book.js             載入某本書
  authoring.js        solutions.js 用的 m/t/h/note/align/L/lk
  viewer/             app.js 頁面、answers.js 答案框與揭步、links.js、media.js、guide.js
  ink/                Pencil 墨跡、圖形、選取、擦膠、重播
  export/             匯出 PDF 與墨跡檔
  widgets/kit.js      互動圖的繪圖工具
  styles.css
books/
  catalog.json        書庫列出哪幾本
  _template/          新書骨架
  <id>/               book.json（章節、題目、region overrides）
                      layout.json（由 extract_pages.py 產生，永不手改）
                      pages/pNN.jpg（3×）
                      solutions.js / widgets.js
                      source/（兩份 PDF，不進 git）
                      reference/（老師筆跡裁圖、QA 截圖，不進 git）
tools/                38 支腳本（22 Python、14 Node、2 PowerShell）＋ 測試輸出
  new_book.py         建新書
  extract_pages.py    渲染頁面 + 自動答案區（--scan 草擬題目清單）
  extract_ans_refs.py 裁老師筆跡
  grow_regions.py     把區域擴到周圍空白
  relayout_pdf.py     在 PDF 內開位（會令該頁高過 A4）
  render_media.py     出 Manim 影片（--still 只出對版圖）
  qa/check_book.mjs   模擬 iPad 的全書檢查 + 截圖
  qa/measure_ctl.mjs  按鈕與答案文字的重疊量測
docs/                 5 份核心文件 + 16 份章節紀錄
```

---

## 6. 九個階段：誰做什麼

| 階段 | 做什麼 | 誰 | 完成條件 |
|---|---|---|---|
| 0 Intake | 收 QUE + ANS、決定 book id 與章節 | ebook | 兩份 PDF 放進 `source/`、章節紀錄已開 |
| 1 Create | 建書、寫 book.json、加入 catalog | ebook | 書庫看得到這本書 |
| 2 Extract | 渲染頁面、定答案區 | ebook | 沒有 `MISSING ANCHOR`、每題都有老師筆跡裁圖 |
| 3 Solutions | 寫逐步解答 | ebook | `check_book` 零 fail |
| 4 Links | review link | ebook | 每個 link 都有答案端、字眼找得到 |
| 5 Graphics | 互動圖 + 面板動畫 + 解答動畫 | visual | `_cmp.png` 吻合、中間 frame 逐格看過 |
| 6 QA | 四支腳本 + 逐頁人眼 | ebook 跑、Chief 核 | `check_book` 零 fail、`measure_ctl` PASS、截圖逐頁看 |
| 7 Release | 升 cache、推 Pages、線上核實 | Chief（或授權） | 線上檔案 hash 與大小對得上 |
| 8 Feedback | 老師試用後修改 | ebook + visual | 每項意見有紀錄與回覆 |

---

## 7. 品質閘門：三層

### 第一層：自動（必須全綠，不可跳）

```powershell
node tools\qa\check_book.mjs <id> --shots    # 全書檢查 + 每頁截圖
node tools\qa\measure_ctl.mjs <id>           # 尾行必須 PASS
node tools\qa\check_media.mjs <id>           # 每段動畫真的能播
```

### 第二層：數值與幾何核對（我們最常贏的地方）

不要「看圖覺得對」，要量：

- 版面：`layout.json` 的 `pages[n].text` 逐行 y、x，加上頁圖墨跡行掃描
- 切口：掃整行無墨跡的位置（1 pt = 3 px）
- 動畫：把 Manim 最後一格與印刷圖裁切逐點比，報最大偏差（我們的標準是 ≤ 1.5 pt）
- 物理：由像素反推參數，再與公式對（例：由落點 x 與頂點高度反推 u，檢查是否五條曲線一致）

### 第三層：人眼（不可取代）

逐頁看 `sheet-*.png`、逐格看動畫的中間 frame、在真 iPad 上試一次。

---

## 8. 我們踩過的八個坑（真實數字）

1. **切口切斷印刷行**：切 540 把選項 D 的分數切斷；墨跡止於 546.7、下一題由 558.7 起，切 550 才對。
2. **答案區伸入頁腳**：頁腳在切口之上不會移動，所以區域一伸進去，答案就蓋住頁腳。規則：`region[3]` ≤ 790。
3. **揭步按鈕壓住答案文字**：四條版面路徑（全部答案 / 放大重排 / 縮回 iPad / 逐格按）中任何一條壓住都算 fail。引擎已改成揭示後重排 + 兩次 rAF。
4. **`_cmp.png` 只看首尾格**：疊加動畫的箭頭飛出相機框 21 pt、只剩一個浮著的 θ，對版照樣 PASS。此後必須抽 3–4 個中間 frame。
5. **向量尾巴不是在球心**：用戶原話「在物體的正中心垂直向下」。要加高畫布（250 → 270）而不是把箭頭挪開。
6. **印刷圖本身物理不一致**：一條 Range 圖的五條軌跡，垂直方向被拉伸約 1.5–1.6 倍（頂高實測 7.7 / 31.3 / 65.5 / 95.3 / 120 pt，而同一個 u 的理論值只有一半左右）。正確做法是**沿印刷曲線動畫**，不要重畫成物理正確的曲線 —— 否則動畫與印刷圖會差 50 pt。
7. **量圖用錯門檻**：那五條軌跡是**黃綠色高飽和**，不是黑色。用亮度門檻（<128）只會量到黑色標籤，於是任何曲線擬合都會收斂到標籤上。正確做法：`max(r,g,b) − min(r,g,b) > 40` 的飽和遮罩。
8. **工具鏈環境坑**：某部機的 esbuild 完全讀不到檔案（改用 Rollup）；Playwright 的 Windows 動態 import 要 `pathToFileURL`；無頭 Chrome 落到 SwiftShader 軟件渲染時會**中途失去 WebGL context**，表現是「全黑圖 + `-Infinity` 邊界」，改用 `--use-angle=d3d11` 走真 GPU 就正常，而且快 10 倍。

> 這一節是整份文件最有價值的地方。每一項都是「已經通過所有自動檢查但仍然錯」的個案，也就是為什麼要三層閘門。

---

## 9. 開一個新科組團隊：步驟

### 9.0 先裝什麼（附原因）

| 軟件 | 版本 | 用來做什麼 | 為什麼不能省 |
|---|---|---|---|
| **Python** | 3.10+ | 跑 `tools/*.py`：讀 PDF、渲染頁面、算答案區域、在 PDF 內開位 | 整條線的排版工作都在這裡 |
| **PyMuPDF**（`pip install pymupdf`）| 1.24+ | 開 PDF、抽每行文字的座標、產生新 PDF | 沒有它就沒有「第 3 行在 y=420pt」這種資料，答案區是靠這些數字定位 |
| **Pillow**（`pip install pillow`）| 10+ | 開頁面圖、掃墨跡行、裁老師筆跡 | 切口要落在「整行無墨跡」的位置，只能靠像素掃 |
| **numpy**（`pip install numpy`）| 1.26+ | 墨跡／像素批量分析 | 1786×2526 的圖逐行跑 Python 迴圈會極慢 |
| **Node.js** | 18+ | 跑 `tools/qa/*.mjs` | QA 是 JavaScript 寫的 |
| **Google Chrome** | 最新穩定版 | QA 用真瀏覽器模擬 iPad（1180×820、觸控、Retina 2×）| QA 要真的點選項、揭步、拖滑桿；`puppeteer-core` 只驅動、不內建瀏覽器 |
| **puppeteer-core**（`cd tools\qa && npm install`）| 見 `package.json` | 控制 Chrome | 同上 |
| **Git** | 任意 | 版本控制、部署 | 部署走 GitHub Pages，回滾要有 commit |
| *(數理科建議一開始就裝)* **Manim Community + ffmpeg** | Manim 0.19+ | 概念面板動畫、解答動畫 | 數理科的圖與動畫是主要賣點，建議一開始就裝（渲染在真 GPU 下是秒級）；中文科不需要 |

全部 **Windows 可用**，而且 reader 本身**不需要互聯網**（`vendor/` 已放好 KaTeX、perfect-freehand、pdf-lib 的離線副本）。

**數理科（數學／物理／化學／生物）建議一開始就裝 Manim**，因為面板動畫與解答動畫是這些科目的主要賣點；中文科不需要，跳過整個階段 5a。

一行檢查自己的機器：`python tools\check_env.py`（starter repo 內附），它會逐項報 OK / 缺什麼 / 補救指令。

### 9.1 兩種教材 PDF，兩條路

| 你的 PDF | 第 1 階段 | 第 3 階段 |
|---|---|---|
| **老師手寫紅框答案** | 有 QUE 就直接用；只有 ANS 時用 `make_que.py` 反推一份乾淨的 QUE | `extract_ans_refs.py` 裁筆跡，`solutions.js` 逐行照老師寫法 |
| **Word / LaTeX 原稿** | 匯出成 PDF 當底圖即可，不需要 `make_que.py` | 解答由原稿轉成 `m()` / `t()` 的行；重點變成「排版對齊印刷」而不是「還原筆跡」 |

兩種都適用同一個引擎。分別只在人工：紅框路線是「解讀筆跡」，原稿路線是「重排文字」。
若原稿已經有清楚的題號與答案，`extract_pages.py --scan` 通常可以直接抓到題目清單。

### 9.2 七個步驟

1. **拿一份 PDF 做 pilot**：選一課 10–20 題的筆記，同時要有老師答案。不要一開始開 16 本。
2. **建 repo 與環境**：直接 clone `ebook-starter`（引擎 + 模板書 + 工具 + QA，2.4 MB，不含任何教材），跑 `python tools\check_env.py` 確認 Python 套件、Node、Chrome 都齊；要做動畫才另外裝 Manim Community + ffmpeg。
3. **建立團隊**：
   - **Chief**（統籌）：管引擎、部署、驗收；只有一個
   - **ebook**（課本）：文字與版面
   - **visual**（圖解）：互動圖與動畫（可以後加）
4. **掛 skill**：`ebook-intake`、`ebook-extract`、`ebook-solutions`、`ebook-qa`（ebook）；`ebook-widgets`、`ebook-manim`、`manimce`（visual）。
5. **寫下三條界線**（貼進每個 Bot 的指令）：
   - `engine/` 只有 Chief 可以改
   - 部署要先得科主任同意
   - 每本書的 `solutions.js` 只有 ebook 寫
6. **跑 pilot 到上線**，把每個踩到的坑寫回 skill（我們就是這樣長出 `ebook-qa` 的「中間 frame」規則）。
7. **第二本開始模板化**：CH1 用過的 region 量法、QA 流程、動畫對版流程直接複製。

---

## 10. 不同科目的調整

| 科目 | 主要挑戰 | 建議 |
|---|---|---|
| **數學** | 排版密集（分數、根號、矩陣） | 現有 15 本數學／M2 書的基礎；重點是切口與答案空間 |
| **物理** | 圖多、單位多、要動畫 | phy11 模式：概念面板動畫（4 段）+ 互動圖（2 個）+ review link |
| **化學** | 化學式下標、狀態符號、方程式的等號對齊 | 先測試 KaTeX 對 `\ce{}` 的需求；每個方程式要當一條 math 行 |
| **生物** | 圖解為主、文字多、少公式 | 重心放在 review link 與標註式互動圖；動畫價值高於解答動畫 |
| **中文** | 沒有公式，但**段落長、答案區要大**；評分點、寫作題、閱讀理解 | **橫排**（已確認，不做直排）。兩點特別處理：① 寫作／長答題的答案區往往要開位（`relayout_pdf.py`），或改成「答案另開一頁」；② 佳句、手法、段落作用這類標註最適合做成 review link（字眼連到評語）。動畫幾乎不用，互動圖也用得少 —— 中文科的價值集中在解答排版與標註 |
| **綜合科學** | 一個課題跨科 | 用 section 分（`sections` 就是 top bar 的分段） |

**中文科的一個實務提醒**：數理科的答案是「一行一公式」，中文科的答案是「一段一段」。`solutions.js` 的 `t()` 支援長句與粗體，但**不要**用 `m()`（它不會換行）；長答案要給 box 明確寬度，或加大 `space`。另外中文的字距與標點不能用 LaTeX 處理，一律寫在 `t()` 內。

所有科目共用的硬道理：**版面座標一律由像素量出來**，不要用「大概在那裡」猜。

---

## 11. 成本與節奏（實測）

- 一本 10 頁 / 20 題：階段 0–2 約 1–2 小時（經驗值）；階段 3–4 是主體（204 個步驟）；階段 5 每段動畫的製作（量座標、寫場景、對版）約 20–40 分鐘。渲染本身在真 GPU 下是秒級；QA 與修正另計
- 模型：`deepseek-flash` + 高思考等級已足夠；難點在「量度紀律」，不在模型大小
- 最大的時間黑洞不是寫程式，是**找出錯在哪一格**。所以量度工具比寫作能力更值錢

---

## 12. 治理與版權（分享前必讀）

1. **部署必須先得批准**：上線是公開行為，改的是學生看到的東西。
2. **先用 private repo 或內網分享，不要一開始就開 GitHub Pages。** 教材 PDF 的版權狀態通常未清；私 repo + 同事互相 clone 已經足夠協作。要對外開放時再逐本確認授權。
3. **共用引擎只有一個維護者**：多人同時改引擎 = 16 本書一起回歸。
4. **每次部署升 cache 版本**（`sw.js` 的 `ebooks-vNN`），否則 iPad 會繼續用舊檔。
5. **第三方素材授權**：開源 skill 要保留 LICENSE 與出處；字庫類資源要看清授權（例如某些粵語詞表是 LGPL，不可隨成品分發）。
6. **學生資料**：書庫與筆跡都存在學生自己的 iPad 本機，不上傳伺服器 —— 這是設計上的優點，要守著。
7. **不同科組的微調放在 `books/<id>/`，不要改 `engine/`。** 章節分段（`sections`）、答案區（`extract.overrides`）、解答（`solutions.js`）、互動圖（`widgets.js`）、動畫（`media` + `book.json`）都在書的資料夾內；真的需要改引擎，就由引擎維護者改一次、所有書一起重跑 QA。

---

## 13. 已確認的前提與仍待補充的資訊

### 13.1 已確認（本文件已按此寫）

| 項目 | 已確認 |
|---|---|
| 對象科組 | 數學、物理、化學、生物、**中文**；全部是香港中學課程 |
| 教材 | 一定有 QUE 與 ANS 兩份 PDF，但**格式不一、不一定有紅框**，一定有答案 |
| 同事環境 | 以 **Windows** 為主 |
| 分享範圍 | **不公開**為先，科組同事之間互相分享 |
| 引擎 | **同一套主引擎**，各科組只在 `books/<id>/` 做執行上的微調 |
| pilot 選課 | 由**各科組自行決定**第一本做哪一課 |
| Manim | **數理科建議一開始就裝**；中文科不需要 |
| 統籌 | **暫時全科一個 Chief**（一份引擎、一位維護者）|
| repo | **一科一 repo** |
| 中文科排版 | **橫排**，不做直排 |
| starter | `Tai-sura/ebook-starter`（private，117 檔、2.4 MB）|

### 13.2 仍待補充（會改變具體建議）

1. **級別分布**：S1–S6 各科分布？同一課在不同級別的答案空間差很遠。
2. **每本書的規模與交期**：幾頁、幾題、希望多久完成一本（決定要不要拆成多個 agent）。
3. **最終驗收人**：科主任？出題老師？需不需要簽核紀錄？
4. **repo 與權限**：一科一 repo 已定，但 repo 要放哪個組織？同事要加到哪一層權限？
5. **是否需要離線 / PWA、匯出 PDF 與墨跡存檔**：引擎已有，但每科使用習慣不同。
6. **16 本舊書怎麼處理**：留在原 repo，還是搬進新的書庫？
7. **中文科的長答題處理**：開位（該頁會高過 A4）還是「答案另開一頁」？兩者教學體驗不同。

---

## 14. 我的建議

1. **先做一本 pilot，不要一次開一個科組 16 本。** 一本書會暴露 80% 的問題（切口、頁腳、字眼、答案空間），而且只用一個 agent 就能跑完。
2. **把「量度」變成腳本，不要靠眼睛。** 我們所有嚴重的錯，都是「自動檢查全綠、肉眼以為對」的個案。量度腳本是一次性投資、永久回報。
3. **`engine/` 只有一把鑰匙。** 這條規矩不值錢，但它救過 16 本書。多科並行時，建議全校只有一位引擎維護者，各科組只在自己的 `books/<id>/` 內工作。
4. **skill 就是 SOP，每次踩坑就寫回去。** 我們的 `ebook-qa` 之所以有用，是因為它記錄了「中間 frame 要抽」這種只有踩過才知道的規則。
5. **先 private repo、先內部分享。** 公開 Pages 是最後一步，不是第一步；教材版權通常要在那一步才有人認真處理。
6. **不同科目先做「密度測試」**：拿最密的一頁（最多字、最多圖）試階段 2 + 3，看答案空間夠不夠。不夠就要用 `relayout_pdf.py` 在 PDF 內開位（該頁會高過 A4，要告知列印需縮放）。中文科的長答題最可能撞到這一關。
7. **不要讓 agent 直接推上線。** 給人類一個批准關卡，成本只是幾分鐘，但避免「學生已經看到錯版」。
8. **用 `ebook-starter` 起手，不要從現有 16 本書 fork。** starter 只有引擎、模板與工具（2.4 MB），沒有任何教材；fork 16 本書會把不相關的內容與版權一起帶走。
8. **相鄰能力可以後加**：短片（Cine）與粵語配音（粵配）是獨立線，不影響 e-book；但如果你們要做翻轉課堂，這兩條線會很有用。

---

*這份文件由實際生產線的工作紀錄整理而成。若要修改，請同時更新對應 skill —— 文件與 skill 走散，就等於沒有 SOP。*
