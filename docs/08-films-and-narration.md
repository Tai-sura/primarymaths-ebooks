<!-- canon: ebook-starter-v2/docs/08-films-and-narration.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

<!-- canon: ebook-starter-v2/docs/08-films-and-narration.md · 由 CTO 於 2026-11-27 三路合併 · 改這份，唔好改副本 -->

# 教學短片與旁白：Cine 的技能與規矩

這份文件是給其他科組同事的：你手上有 e-book starter repo，想替自己的課題（化學、生物、數學也可以）做短片與旁白。以下全部是我們實際在做的方法，不是建議；每個數字後面都寫了出處檔案，找不到出處的會明講。

## 1. 一頁總表

| 技能／工具 | 絕對路徑 | 一句話用途 | 何時用 |
|---|---|---|---|
| cinecode | `C:\Users\surat\.dsh\bot\workspace\cinecode\SKILL.md` | Canvas/HTML 逐格 renderer（`scripts/capture.mjs`）出 MP4 | 要精準數值、公式同步的 2D 教學片 |
| motion-graphics `explainer-*` | `C:\Users\surat\.dsh\bot\workspace\motion-graphics\skills\explainer-default`（另有 `explainer-engaging`、`explainer-high-energy`） | 現成 kinetic 字卡／轉場 HTML | 片頭、轉場、字幕卡 |
| canto-narration-film | `C:\Users\surat\.dsh\bot\workspace\.tmp-skillspector\ours\canto-narration-film\SKILL.md` | 粵語旁白短片的總流程（先鎖片後配音） | 任何有旁白的片 |
| cantonese-tts | `C:\Users\surat\.dsh\bot\workspace\.tmp-skillspector\ours\cantonese-tts\SKILL.md` | Edge zh-HK 讀音驗收與修正 | 寫稿、試聽、驗音 |
| cantonese-tts-lexicon | `C:\Users\surat\.dsh\bot\workspace\.tmp-skillspector\ours\cantonese-tts-lexicon\SKILL.md` | 粵語詞庫、G2P 與單字首讀陷阱 | 多音字、專有名詞 |
| physics-film-revision-loop | `C:\Users\surat\.dsh\bot\workspace\.tmp-skillspector\ours\physics-film-revision-loop\SKILL.md` | 改物理片畫面、頁內動畫對齊印刷圖 | 每次改畫面、做面板動畫 |
| films\shorts-kit | `C:\Users\surat\.dsh\bot\workspace\films\shorts-kit\` | 15 秒 1080×1920 直式模板（episode JSON） | IG Reels／Shorts |

第 3–6 項的技能正文在 DSH 的 skill catalog；上面是本機的工作副本（複製自 skill gate 的檢查目錄），要搬去自己電腦就整份資料夾複製。e-book 的檔案格式出處是 `ebook-starter\docs\02-book-format.md`。

前置工具（`cinecode/SKILL.md` 開頭）：Node ≥ 22、Python 3、`ffmpeg`、Chrome。缺一樣不會令片子做不出來，但 renderer 會停，所以先跑一次 `node cinecode\scripts\capture.mjs --url … --probe` 看它認不認到 GPU。

## 2. 逐個技能

**工時一律未量測，本文件不給估算。** 真正固定的是「鎖片 → 等用戶確認」這一步（`canto-narration-film/SKILL.md`），其餘隨片長與畫面數變。

先分三條出片路線，選錯路線是最常見的浪費：

| 路線 | 適合 | 做法 | 限制 |
|---|---|---|---|
| 2D 逐格 | 公式、圖表、面板動畫 | 寫 HTML／Canvas，`capture.mjs` 逐格截圖 | 要自己寫 renderer 呼叫 |
| 3D 網頁 | 機械、線圈、剖面 | three.js／exploded-view 出網頁，再逐格截圖 | 沙盒內 Playwright 起不來，要完整權限（`canto-narration-film/SKILL.md`） |
| Manim 面板 | 與印刷圖逐像素對齊 | Manim class＋`render_media.py` | 只覆蓋 region，印刷字不可改（`02-book-format.md` ＋ `physics-film-revision-loop/SKILL.md`） |


### 2.1 cinecode（片）
- 輸入：一個 `film.html`（Canvas 或 DOM，動畫是 `t` 的函數）＋參數。
- 輸出：MP4；`capture.mjs --url … --out <frames> --video <mp4> --params "w=…&h=…"`，位元率上限 10M、草稿 4M（`cinecode/SKILL.md`）。
- 放 e-book：`books/<id>/media/`，再在 `book.json` 的 `media` 加一條 `{page, region, src, poster, title}`（`02-book-format.md`）。真實例子：`ebook-engine\books\jpfm08\media\p3-moments.mp4`（574,176 B）＋ `p3-moments-poster.png`（126,570 B）。
- 失敗：Chrome 起不來（沙盒）、幀數與預期不符、poster 用了截圖而非頁圖裁圖。

### 2.2 motion-graphics explainer-*
- 輸入：一份現成 HTML 模板；輸出：先出網頁，再交給 `capture.mjs` 抓格、ffmpeg 串成 MP4（`canto-narration-film/SKILL.md` 的 3D 選項表）。
- 放 e-book：同 2.1。
- 失敗：用 Playwright 在沙盒內起不來（`canto-narration-film/SKILL.md` 實測：`mojo platform_channel.cc:112`），要完整權限；或渲染時用 wall-clock 而掉格。

### 2.3 canto-narration-film（總流程）
- 輸入：分鏡腳本（一句旁白對一個畫面）＋畫面。
- 輸出：母片 `picture-vN.mp4`（無旁白）＋成品 `<片名>-Narrated-vN.mp4`；規格 `h264`、`yuv420p`、`1920×1080`、`30 fps`、AAC 192k；實測 4.5 s → 135 幀（`canto-narration-film/SKILL.md` 出片規格）。
- 放 e-book：`books/<id>/media/`，`book.json` 的 `media` 用 `src`／`poster`，`page`／`region` 指向要蓋住的印刷面板（`02-book-format.md`）。面板動畫另加 `scene`（Manim class），但我們多數是把 MP4 交回 ebook 負責人接線。
- 工時：未量測；卡點是第 3–4 步（鎖片＋用戶確認）。
- 失敗：先配音後做片 → 每次改畫面都要重錄（同檔「次序」一節）。

### 2.4 cantonese-tts（讀音）
- 輸入：句子（書面語，符號已改寫）；輸出：mp3/WAV＋驗收判斷。
- 聲音：`zh-HK-HiuGaaiNeural`、`zh-HK-HiuMaanNeural`、`zh-HK-WanLungNeural`（`cantonese-tts/SKILL.md`）。
- 失敗：θ 讀成 /f/、下標被讀成數字；ASR 回譯會有假警報（同檔）。

### 2.5 cantonese-tts-lexicon（詞庫）
- 輸入：稿與專有名詞；輸出：override／GATE 清單（例：`龜,gwai1`）。
- 失敗：自製 G2P 的單字首讀不一定對（同檔）。

### 2.6 physics-film-revision-loop（面板動畫）
- 輸入：頁圖的 region＋向量原稿；輸出：與印刷圖逐像素對齊的頁內動畫。
- 規格：首幀、末幀與 poster 在 PNG 層 `max 0`；poster 由頁圖裁，不用末幀截圖（`physics-film-revision-loop/SKILL.md`）。
- 失敗：拿 mp4 解碼層的色度差當失敗；或改一個數值卻沒重算旁白。

### 2.7 films\shorts-kit（直式短片）
- 輸入：`episodes/*.json`（hook／formula／bars／conclusion／cta）；輸出：1080×1920、30 fps、15 秒的直式片（`films\shorts-kit\README.md`；15 秒 × 30 fps = 450 幀是推算）。
- 位置：這是 IG 用，**不進 e-book**。
- 限制：render 仍需要一個 Remotion 專案；Remotion 對個人與 ≤3 人公司免費，超過要買 licence（`films\shorts-kit\README.md`）。

### 2.8 一個真實例子（jpfm08 p5）
- 目標：把印刷面板上「200 N 與 300 N 兩個載荷」的平衡做成 4.5 秒動畫。
- 做法：`p5-equilibrium-v3.html` 用 Canvas 逐格畫，底圖由 `p05.jpg` 裁 region，`capture.mjs` 出 864×276、135 幀、無音軌的 MP4。
- 交付：`ebook-engine\books\jpfm08\media\p5-equilibrium.mp4`（77,030 B）＋ `p5-equilibrium-poster.png`（51,584 B）；首末幀與 poster 在 PNG 層 `max 0`。
- 這條片沒有旁白：面板動畫由讀者按 ▶ 才播，加旁白反而要處理 autoplay 與字幕位置。


## 3. 硬規矩（附出處）

1. **整體 −14 LUFS ±1**（`canto-narration-film/SKILL.md` 第 7 步）。
2. **true peak 看音樂底**：平順底 loudnorm 設 −2.0；有鼓點／瞬態設 −2.5；**一律以 `ebur128` 量成品為準**。出處同檔；AAC 會令 TP 升約 0.2 dB（`cantonese-tts/SKILL.md`）。
3. **字幕由我們寫的句子＋TTS 回傳的時間生成 SRT**，不手打時間碼；cue 與音頻誤差 < 0.1 s（`canto-narration-film/SKILL.md` 第 6 步與驗收清單）。**不用語音識別做字幕**：ASR 只作旁證，且會自動「修正」成合理詞（`cantonese-tts/SKILL.md` 紀律一節）。
4. **逐格渲染要 seek 到第 i 格再截圖**，動畫必須是 `t` 的純函數，不可用 wall-clock（`canto-narration-film/SKILL.md` 第 2 步）。
5. **沒有實測數字就不要說合格**（`physics-film-revision-loop/SKILL.md`「交付前自驗」；`canto-narration-film/SKILL.md` 硬規矩 4）。
6. **新版本不覆蓋舊版**：v5 留著出 v6（`canto-narration-film/SKILL.md` 硬規矩 2）。
7. **先鎖片、後配音**；畫面未經用戶確認不出聲（同檔「次序」）。
8. **中英夾雜是已知限制**：Edge 讀英文詞會轉英文口音，不是 bug（同檔硬規矩 5）。

## 4. 粵語發音陷阱

| 寫法 | Edge 實際讀成 | 正確寫法 |
|---|---|---|
| `θ` / `theta` | /ˈfiːtə/（θ→f，香港口音） | 要真 /θ/ 就只換擦音：把 `theta` 開頭 50–70 ms 的 /f/ 換成 en-HK 聲線（如 Sam）的真 /θ/，12 ms 交叉淡化，不要整詞換聲（`cantonese-tts/SKILL.md`） |
| `sinθ` / `cosθ` | sin theta（theta 仍是 /f/） | 稿子寫全拼 `sine theta`／`cosine theta`（同檔，用戶指定） |
| `a₁` / `a₂` | 讀成數字（「a 四」） | 寫「加速度是…」，或不寫下標（同檔） |
| 龜 | 自製 G2P 首讀 `gau1`（「夠」） | 詞典 `gwai1`；override `龜,gwai1`（`cantonese-tts-lexicon/SKILL.md`） |
| 不 | 詞庫首讀 `fau2` | `bat1`（同檔） |
| 多音字（重、行、長、好） | 憑語感會錯 | 查詞典（粵典／中大審音配詞字庫／jyutjyu.com）（`cantonese-tts/SKILL.md`） |

## 5. 驗收清單

- `ffprobe`：`h264`、`yuv420p`、`1920×1080`、`30 fps`、幀數、音軌條數（`canto-narration-film/SKILL.md`）。
- `ebur128`：`I` −14 ±1、`TP` ≤ −1.5；**量成品**，不是量設定值（同檔）。
- 影像串流 MD5 與母片相同：`-c:v copy` 之後仍要比對，不符就攔截（同檔）。
- 首尾格與 poster：PNG 層 `max 0`（`physics-film-revision-loop/SKILL.md`）。
- 字框 diff：抽樣幀改動像素 0；另抽 3–4 個中間格人眼檢查（同檔）。
- 字幕 cue 與音頻誤差 < 0.1 s（`canto-narration-film/SKILL.md`）。
- 檔案不是 0 bytes；音量不是靜音（同檔：編碼默默失敗是常見事故）。
- 母片與成品都要留，各自版本號，舊版不刪（`canto-narration-film/SKILL.md` 硬規矩 2）。
- 原則：**拿不出實測數字就不要說合格**（出處同 §3 第 5 條）。

## 6. 怎樣叫我們做（可直接複製）

```
【片名】<片名>-Narrated-v1
【頁面】books/<id>/pages/pXX.jpg，region [x0, y0, x1, y1]；或「不需要頁圖」
【要講的 3–6 句】一句一行（書面語；符號先寫成 sine theta 這類全拼）
【長度】目標 __ 秒（可 ±__ 秒）
【旁白】要／不要；粵語（Edge zh-HK，指定 HiuGaai／HiuMaan／WanLung）／英文
【畫面】哪些元素要動、要標哪幾個數字（數字請先算好）
【交付】mp4＋poster＋SRT，放 books/<id>/media/
```

不確定的地方寧願問，不要自己在片裡補數字。
