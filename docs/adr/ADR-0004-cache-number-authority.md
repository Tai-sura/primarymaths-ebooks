# ADR-0004 — CACHE 號碼：CTO 分配，Chief 執行

狀態：已接受 · 2026-11-29 · 相關：ADR-0002 第 3 點、ADR-0003、skill `release-runbook`、skill `sw-cache-version-gate`

## 背景

ADR-0002 第 3 點寫「號碼只由 Chief 改；其他 Bot 不改 `sw.js`、不 bump CACHE」。但 CTO 的職責定義包含「管 CACHE 號碼」，兩條規則直接對撞。

2026-11-28 就撞了一次：兩站改成 per-site cache 前綴（`physics-ebooks-v189`／`primarymaths-ebooks-v190`，見 ADR-0003），是 CTO 動的 `sw.js` 與 bump，靠用戶逐次批准才成立。每次都問用戶不可持續，所以要一條能長期執行的規則。

## 決定

把「管號碼」拆成兩件事，各歸一方：

1. **分配權屬 CTO**：取號（`git fetch` 後取較大者 +1）、撞號順延、跨站登記、出貨前的 gate、上線後的核對——號碼的所有判斷由 CTO 做。
2. **執行權屬 Chief**：改 `sw.js` 的 CACHE 字串、bump、commit、push 由 Chief 落手。其他 Bot 一律不改檔、不 bump、不自行 push，CTO 亦然。
3. 實際分工是一條交接：CTO 交「號碼 + 已驗的內容 + gate 結果」，Chief 落 bump 與 push，之後 CTO 做上線核對。中間任何一方發現號碼被別條線用掉，照 ADR-0002 順延。
4. 要下放執行權（例如交給 CI 或交回 CTO），必須另開 ADR 取代本份；不得靠對話批准長期生效。

## 被否決的選擇

| 方案 | 為什麼不做 |
|---|---|
| B：CTO 可 bump，配合主科主任簽核 + 用戶每次批准 | 用戶 2026-11 明定 CACHE 只由 Chief 改，那是撞號與倒退事故之後的決定；改成每次批准等於把長期規則換成一次性例外 |
| C：兩站各自管號碼 | 同號不同內容，除錯時無法憑號碼判斷新舊（ADR-0002 已否決） |
| D：完全自動化，push 時由 CI 取號 bump | 現時沒有 CI 跑兩站；且首次上線仍需人手核 `caches.keys()`，過早自動化會把 gate 繞過 |

## 後果

- 好處：兩條規則都成立——CTO 對號碼有完整判斷權，用戶「CACHE 只由 Chief 改」的原意不動；任何人問「為什麼不是 CTO 改」有檔可查。
- 代價：Chief 是出貨路徑上的單點。Chief 不在線時，bump 要等；我（Chief）要在收到號碼後盡快落手，不可積壓。

## 何時重看

- 用戶主動要把執行權下放（那時開新 ADR 取代本份）。
- 站數增加到需要獨立版本節奏。
- 兩站導入 CI 出貨，bump 應一併自動化。
