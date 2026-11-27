<!-- canon: ebook-starter-v2/docs/07-visuals-and-animations.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

<!-- canon: ebook-starter-v2/docs/07-visuals-and-animations.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# 視覺與動畫：給其他科組的入門指引

讀者：已有 e-book starter repo、但未接觸過我們視覺流程的同事。看完應該知道「有邊樣工具、擺喺邊、叫我們做要提供咩、我們用咩數字收貨」。

行號以完整版 `C:\Users\surat\.dsh\bot\workspace\ebook-engine\` 為準；starter 只帶部分 docs，`docs\06-layout-controls-and-media.md` 未收錄，要對規矩請打開完整版。

---

## 1. 一頁總表

| 技能／工具 | 放喺邊（絕對路徑） | 一句話用途 | 幾時用 |
|---|---|---|---|
| `ebook-panel-animation-pipeline` | team skill（本機副本 `…\workspace\.tmp-skillspector\ours\ebook-panel-animation-pipeline\SKILL.md`） | 重畫有版權的印刷面板＋配一支對版 MP4＋自動重貼 | 要換走印刷卡通，或要一段蓋住面板的教學片 |
| `ebook-widgets` | team skill（副本 `…\ours\ebook-widgets\SKILL.md`） | 寫 `books\<id>\widgets.js` 的互動 SVG | 題目要「拖一下即刻見結果」 |
| `ebook-manim` | team skill（副本 `…\ours\ebook-manim\SKILL.md`） | `GuideScene` 解答動畫、media 面板動畫的寫法與出片次序 | 要逐步推演 |
| `manimce` | `…\workspace\skills\manimce\` | ManimCE 的 API、rules 索引、常見錯誤（上游 MIT） | 寫／改 Manim 前查語法 |
| `explainer-default`／`engaging`／`high-energy` | `…\workspace\motion-graphics\skills\explainer-*\` | 產品示範片：45–90 s 平穩、一鏡到底、12–30 s 高能 | 對外宣傳，**不入** e-book |
| `sketch-to-3d` | `…\workspace\skills\sketch-to-3d\` | 3D 模型變手繪 marker 草圖，再擦開露 render | 要「手繪變真實」的轉場 |
| `print-figure-measurement` | team skill | 把印刷頁的圓、弧、箭咀量成 pt 座標 | 重畫任何印刷幾何之前 |
| `engine\widgets\kit.js` | `…\ebook-engine\engine\widgets\kit.js`（11,048 B） | 互動圖共用 API：`C S T scene question sector` | 寫 widget 時唯一要 import 的引擎檔 |
| `engine\infographic\` | `…\ebook-engine\engine\infographic\`（`kit.js` 25,206 B） | 白板式情境圖，板子在 `books\<id>\infographics.js` | 要情境圖而不是滑桿 |
| `engine\deck\` | `…\ebook-engine\engine\deck\`（`deck.js` 15,393 B） | 尾頁 flashcard deck（`endPages` 的 `"deck"`） | 要一頁溫習卡 |
| `ebook-qa` | team skill（副本 `…\ours\ebook-qa\SKILL.md`） | QA gate 與上線次序 | 每次交貨前 |

---

## 2. 每個技能一節

### 2.1 `ebook-panel-animation-pipeline`
- **解決什麼**：印刷圖是別人的卡通，要換成自畫面板並在上面播教學片。
- **輸入**：`pages\pNN.jpg`（1 pt = 3 px）、要換那塊的實際外框（連陰影）、答案區、步驟次序。
- **輸出**：`panels\pNN-*.png`（3×）＋`panels.json`＋`media\*.mp4`／`-poster.png`；`book.json` 的 `media`：`page`、`region`、`scene`、`src`、`poster`、`title`（`docs\02-book-format.md:46`）。
- **工時**：無記錄（見第 7 節）；流程是「面板對版 → `--still` → 出片」各一輪。
- **失敗會怎樣**：`extract_pages` 重出頁圖，手貼面板靜默消失（`…\ours\ebook-panel-animation-pipeline\SKILL.md:9-10`）；貼圖排在蓋章之後會被重新編碼而漂移（同檔 `:11-12`）。

### 2.2 `ebook-widgets`
- **解決什麼**：把推理變成可拖的圖，學生自己試出規律。
- **輸入**：題目文字、solution 的「Let …」措辭、量到的幾何。
- **輸出**：`books\<id>\widgets.js`＋`REGISTRY` 登記；API 見 `…\ours\ebook-widgets\SKILL.md:26-33`。
- **工時**：無記錄；一題首次一輪、修改一輪。
- **失敗會怎樣**：`check_book --shots` 出 `reference\qa\graphic-<qid>.png`，標籤重疊、出界、數字錯一眼看到（同檔 `:54`）；改過畫布高度要重跑 `measure_ctl`，否則按鈕壓答案（`:62`）。

### 2.3 `ebook-manim`
- **解決什麼**：把 `solutions.js` 每一步畫成動作；或把概念面板做成循環短片。
- **輸入**：`PAGE`、`REGION`（頁面點 595×842）、步驟。
- **輸出**：`tools\manim\<module>.py`；`book.json` 的 `guides`（`02-book-format.md:47`）或 `media`（`:46`）。guide 的 poster 是第一格，media 是最後一格（`…\ours\ebook-manim\SKILL.md:53-54`）。
- **工時**：無記錄；「still 對版 → 抽中間幀 → 出片」三輪。
- **失敗會怎樣**：`--still` 只證海報＝印刷圖，箭咀飛出框照樣 PASS（同檔 `:71-74`）；`PAGE` 錯就整段對錯頁（`:99`）。

### 2.4 `manimce`
- **解決什麼**：查 ManimCE 的類別與 best practice，避免誤用 ManimGL 語法。
- **輸入**：想畫的動作；**輸出**：可跑的 ManimCE code；本機實測 **0.22.1**（`python -c "import manim"`）。
- **工時**：無記錄（查語法，不計輪次）。
- **失敗會怎樣**：ManimGL 語法（`Tex` vs `MathTex`）直接跑不起。

### 2.5 `explainer-*`
- **解決什麼**：寫一個可由時間值 render 任何一格的 HTML 頁，再壓成帶音樂的 MP4。
- **輸入**：產品名、一句賣點、品牌色／字、比例、長度、音樂。
- **輸出**：1920×1080 或 1080×1920 MP4；default 60 s（45–90）、engaging 10–20 s、high-energy 12–30 s。
- **工時**：無記錄。
- **失敗會怎樣**：`explainer-default` 明禁編事實——虛構用戶數、評分、引言（`explainer-default\SKILL.md:26`）。

### 2.6 `sketch-to-3d`
- **解決什麼**：3D 模型畫成手繪 marker 草圖逐筆動畫，最後擦開露 render。
- **輸入**：模型（three.js 場景或 GLB／GLTF／OBJ／FBX／STL／PLY／USDZ 等）、最終尺寸。
- **輸出**：MP4 ＋ 一個 web player（上游預設兩樣）。**入 e-book 只取 MP4**，放 `media\` 並加 `media` 條目。
- **工時**：無記錄；先 stills 後出片（`…\skills\sketch-to-3d\SKILL.md:22`）。
- **失敗會怎樣**：把上游 web player 塞進 reader 等於書裡再開一套 3D 引擎——這是本組規矩，上游 `SKILL.md` 沒寫，所以 brief 要寫明「只要 MP4」。

### 2.7 `print-figure-measurement`
- **解決什麼**：把印刷圖的幾何量成可重畫的 pt 座標，並用疊圖證明量對。
- **輸入**：`pages\pNN.jpg`（3 px/pt）、要量的元素。
- **輸出**：pt 座標常數（docstring 註明量自邊度）＋疊回頁圖的對比圖。
- **工時**：無記錄。
- **失敗會怎樣**：由縮圖目測再擬合，重疊的圓會滑到鄰圓的弧上（`06-layout-controls-and-media.md:139-143`）。

---

## 3. 硬規矩（house rules）

`06:` ＝ `ebook-engine\docs\06-layout-controls-and-media.md`；`03:` ＝ `ebook-engine\docs\03-authoring-style.md`（starter 內 03 是 165 行版本，行號不同，用引號字眼搜）。

| # | 規矩 | 為什麼（症狀） | 出處 |
|---|---|---|---|
| 1 | **印刷頁永遠最上層**：淡填色 → 虛線 → 印刷圓周 → 顏色圈 → 印刷箭咀與讀數 → 徽章 → 圓心點 | 圓周在虛線之下時，虛線跨過別人圓周就把 1.2 px 印刷墨蓋成藍色，實測掉 114 個墨像素 | `06:184-190` |
| 2 | **虛線兩端要落在實墨**，末端離圓周 ≤0.5 pt；週期由線長解出 `round(len/(on+off) − 0.5) + 0.5` | 固定 `13 7` 令 307 px 直徑短 7 px；整數週期正是空隙起點，十二條有六條短 2.8–4.0 pt | `06:191-196` |
| 3 | **逐圓一個預設角**，與其他圓心點 ≥9 pt，並避開印刷箭咀、讀數、徽章 | 全局 62° 令最大圓直徑離別個圓心點 4.3 pt、離箭咀 3.7 pt，看起來「斷在點上」；F 改 288° 後最近點 18.8 pt | `06:197-202` |
| 4 | **工具要跟住它畫的線走**：圓規繞針尖轉，鉛筆永遠在弧前端 | 圓規不動、弧自己長出來，像魔術不像畫 | `06:212-223`；`03:170-173` |
| 5 | **不可用加粗或放大做高亮**：目標環 2.2、填色 ≤5% | 2.8 環 + 9% 填色令準確的 C 看起來變大，老師回報「C 應該細啲」 | `06:169-172` |
| 6 | **片頭先清場，後起筆** | 印刷標題與新畫的弧同時在，像重影 | 無書面出處（第 7 節） |
| 7 | **片尾不可淡到空白**；停完成圖並 hold ≥0.5 s；第 0 格＝最後一格 | 淡到 0.9% 墨再硬切回，停格的人見到近乎空白 | `06:123-128`；`03:165-169` |
| 8 | **poster 是學生按 ▶ 前見到的東西**，必須是完成圖 | 六格空白框的 poster 把印刷漫畫整個藏起來 | `06:116-121` |
| 9 | **量印刷圖用 ink band（1 pt = 3 px）**，不用眼、不用有色底 | 有色底邊 725 pt、印刷框線 750 pt，25 pt 誤差切掉第二行 | `06:30-34` |
| 10 | **`--still` 只證明海報**，出片前抽 3–4 個中間 frame 逐格看 | p1 `ResolvingVelocity` 壞了一整輪，箭咀飛出框 21 pt 仍 PASS | `03:136-138`、`:154-156` |
| 11 | **不重畫印刷已有的字、虛線、θ、90°**；只做填實、強調、跟隨 | p1 把 `vx = v cos θ` 畫了兩次 | `03:157-159` |
| 12 | **向量由物體正中心畫** | 用戶原話：「在物體的正中心垂直向下」 | `03:162-164`；`…\ebook-widgets\SKILL.md:58` |
| 13 | **白框只遮壓入圖 bbox 的題目文字**，不可遮圖本身註解 | p1 白框蓋掉「y (vertical) component of velocity」 | `03:160-161` |
| 14 | **量完用 cm／數值驗比例**：六圓全部 14.2 pt/cm | 第一次量到 C、F 用 80.7／80.3 pt，差一點寫出「印刷不按比例」 | `06:156-161` |
| 15 | **不可由縮圖目測起手**；疊回頁圖逐元素報偏差，>1.5 px 算錯 | A 偏細偏左、C 偏大、F 落到另一個圓，而且已上線 | `06:146-151` |
| 16 | **交付 = 0 FAIL 0 WARN**，WARN 要修或進 allow-list 寫原因日期 | 「no blocking problems」不是交付標準 | `06:234-235` |

---

## 4. 驗收數字

| 指標 | 數字 | 怎麼量 | 出處 |
|---|---|---|---|
| 面板影片畫布 | 690×582 px（1.1856，對 region 230×193.7 pt = 1.1875） | 量印刷框線墨帶，不量有色底 | `06:30-34` |
| 影片大小 | 每段約 900 KB 以下 | 逐個 `src` 計 bytes | `01-workflow.md:161`；`…\ebook-manim\SKILL.md:55` |
| poster | 影片第 0 格，SSIM 1.0；media 的 poster 是最後一格 | `-frames:v 1` 抽出與 poster 比 | `06:104-105` |
| 首尾一致 | poster PSNR inf；解碼後第 0 vs 最後 ≥50 dB | 兩格各抽 PNG 比 | `06:127-128`；`03:168` |
| 片尾停留 | ≥0.5 s 停在完成圖 | 逐 0.2 s 量墨覆蓋率 | `06:123-127` |
| 印刷墨保護 | **變亮 >20 的像素 = 0**（16 個狀態） | 同圖渲染兩次（顯示／隱藏虛線）；隱藏那版亮度 <100 當印刷墨，逐像素相減數變亮 >20 | `06:184-190` |
| 虛線端 | 兩端在實墨內，各 ≤0.5 pt 到圓周 | **只重繪虛線**（不畫色圈）再量末端；色圈會假裝有墨 | `06:191-196` |
| 虛線避讓 | 離其他圓心點 ≥9 pt | 360° 全掃逐角評分 | `06:197-200` |
| 圓規跟線 | 軸 vs 弧前端 ≤2°；鉛筆 ≤1 px；針尖 <1 px | 每格畫到一半時量 | `06:221-223`；`03:170-173` |
| 重畫對版 | ≤1.5 px；驗收跑 mean 0.36–0.41、p95 0.61、max 1.52 px | 把人畫幾何畫回 `pages\pNN.jpg` | `06:149-151`、`:179-181` |
| 實片規格 | `books\p5m07a\media\circles-compass.mp4`（2026-11-25 讀取）：690×582、30/1 fps、408 幀、13.6 s、269,292 B、只有 video stream（無音軌） | `ffprobe -show_entries stream=codec_type,width,height,r_frame_rate,nb_frames` | 檔案本身；900 KB 門檻見 `01-workflow.md:161` |
| widget 截圖 | 每個 widget 一張 `graphic-<qid>.png`，default 與 min／max 都看 | `check_book.mjs <id> --shots` | `…\ebook-widgets\SKILL.md:54`；`03:106` |
| 按鈕不壓答案 | 尾行 `PASS: no strip covers the working` | 四條版面路徑逐題量重疊 | `…\ebook-qa\SKILL.md:37-40` |

---

## 5. 怎樣叫我們做

複製整段填好就發。**PDF 一定要給**——我們所有座標都由頁圖量出來。

```
書名／科目：
PDF 檔（QUE 與 ANS 兩份，或一份含答案）：
要處理的頁碼（PDF 第幾頁，1-based）：
那一格是：□ 整頁下半的漫畫  □ 概念面板  □ 某一題的圖
  └ 只做局部時請圈範圍，或寫「標題 XXX 之下到頁腳之上」
答案（跟老師 ANS 的寫法與數字）：
時長：□ 10–14 s（面板動畫）  □ 逐步推演（guide，每步一拍）  □ 其他：___
要不要旁白：□ 不要（我們出無音軌片）  □ 要（另開配音工序）
要不要互動版：□ 不要  □ 要（同一塊面板加一個 widget 按鈕）
有沒有版權卡通要換走：□ 沒有  □ 有，範圍：___
驗收想看：□ 疊圖  □ 中間幀截圖  □ 首尾一致數字（可以全要）
```

分工：畫面與動畫由 visual 出；接 `book.json`、跑 `check_media`／`check_book`／`measure_ctl`、上線由 ebook 做；上線前一定問用戶。

---

## 6. 不要做什麼

- **不要重畫一個「同印刷圖不同」的圖**：先量、疊圖證明 ≤1.5 px 才准畫（`06:146-151`）。
- **不要加印刷沒有的元素、數值、標籤**：spem02 自創「混合網絡」被用戶抓出來（`…\ebook-manim\SKILL.md:68`）。
- **不要用未播種的 random、不要用 `Date.now()`**：每次 render 要能逐位元重現；改完要驗 sha256 真係變（同檔 `:93`）。
- **不要用白色 halo 保護線**，會把圈切斷（`…\ebook-widgets\SKILL.md:60`）。
- **不要 fade `self.mobjects`** 收尾，會連印刷圖一齊帶走（`…\ebook-manim\SKILL.md:95`）。
- **不要用 `Set-Content -Encoding utf8` 改 `sw.js`**（會加 BOM），用 `[IO.File]::WriteAllText` + `UTF8Encoding($false)`（`…\ebook-qa\SKILL.md:73`）。
- **不要未經同意 push／升 cache／覆蓋已上線檔案**（`06:237`）。

---

## 7. 出處與已知缺口

- 引用檔：`ebook-engine\docs\06-layout-controls-and-media.md`、`03-authoring-style.md`、`01-workflow.md`、`02-book-format.md`；team skills `ebook-manim`、`ebook-widgets`、`ebook-panel-animation-pipeline`、`ebook-qa`；`workspace\skills\manimce`、`sketch-to-3d`、`motion-graphics\skills\explainer-default`；實片 `books\p5m07a\media\circles-compass.mp4`；Manim 版本由實跑得出。
- **工時**：本組沒有工時紀錄，第 2 節只描述流程輪次，不是量測值。
- **無書面出處三條**：①「片頭先清場後起筆」在 `06`／`03`／各 skill 找不到原句，只在對話中由用戶提出；②「無音軌」無 docs 條文，只有實片 ffprobe 可證；③「sketch-to-3d 只准 MP4」是本組規矩，上游反而明寫會出 web 版。建議補進 `06`。
