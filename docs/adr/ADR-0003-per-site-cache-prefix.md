# ADR-0003 — 快取名帶站前綴，activate 只刪自己的 cache

狀態：已接受 · 2026-11-28 · 部分取代 ADR-0002（第 4 點的驗收方法）
相關：ADR-0002、`REPO.md` §1、`docs/04-qa-and-release.md` §5、兩站的 `sw.js`
Commit：physics `167c5c4`（`physics-ebooks-v189`）、maths `1c54ae6`（`primarymaths-ebooks-v190`）

## 背景

`https://tai-sura.github.io/physics-ebooks/` 與 `https://tai-sura.github.io/primarymaths-ebooks/` 是**同一個 origin** 之下的兩條路徑（兩個 repo 都沒有 `CNAME`）。CacheStorage 是按 origin 分的，不是按路徑分：`caches` 對兩條路徑是同一個表。

而舊的 `sw.js` activate 是：

```js
caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
```

即「凡是唔係我自己名的 cache 一律刪」。兩個站的 cache 名不同（`ebooks-v188` 與 `ebooks-v174`），所以每一次任何一站 activate，都會把**另一站的離線快取整批刪掉**。

後果是學生層面可見的：同一部機看過物理又看過數學，兩本書會互相清走對方的離線副本；學校 Wi-Fi 差或者完全離線時，另一本開不到。

ADR-0002 的「一號一內容」只保證兩個名不會撞，**從來沒有阻止這個刪除**。撞名只是表面症狀，真正的病因是刪除條件寫成「非我即敵」。

實測（Chrome，本地把兩個站掛在同一個 origin，與線上拓樸一致）：

- 舊邏輯：開 A 之後有 `ebooks-oldA`；再開 B，A 的 cache 消失（故障重現）
- 新邏輯：兩個 prefixed cache 共存，第三次訪問仍在，無殘留無前綴名
- 線上覆核（乾淨 profile，先開 physics 再開 maths）：`[physics-ebooks-v189, primarymaths-ebooks-v190]` 同時存在；兩本書各讀一本，`jpfm08` 65 圖 30 canvas、`p5m07a` 98 圖 22 canvas，0 page error

## 決定

1. cache 名帶站前綴：`const PREFIX = "physics-ebooks-"; const CACHE = PREFIX + "v<N>";`（maths 用 `primarymaths-ebooks-`）。
2. activate 只刪自己前綴的：`k.startsWith(PREFIX) && k !== CACHE`；另外各站一次性刪自己最後一個無前綴名（`LEGACY`，physics `ebooks-v188`、maths `ebooks-v174`）。
3. `caches.match(request, { cacheName: CACHE })`，不再全域搜，避免一個站命中另一個站的條目。
4. 號碼仍然兩站共用一組（ADR-0002 第 1–3 點維持），今次接續 v189／v190。前綴已經保證分離，共用號碼由「正確性防線」降格為「團隊溝通約定」。
5. 驗收方法要改：在訪問過兩站的瀏覽器上，`caches.keys()` **應該見到兩個 prefixed 名**。ADR-0002 第 4 點寫的「只剩該號」在共用 origin 下本來就不可能成立。

## 被否決的選擇

| 方案 | 為什麼不做 |
|---|---|
| 只維持 ADR-0002（共用計數器） | 完全沒有修到故障：名字不同，activate 照樣刪對方 |
| 靠 service worker scope 隔離 | scope 本來已經是 `/physics-ebooks/` 與 `/primarymaths-ebooks/`，已經隔離；`caches` 不受 scope 限制 |
| 立刻用 `/^ebooks-v\d+$/` 清所有無前綴名 | 會刪到另一站**仍在用**的舊 cache（還跑舊 `sw.js` 的用戶），即再犯同一個錯。要等兩站上前綴滿一個版本週期後才做 |
| 兩站各自由 v1 數起（推翻 ADR-0002） | 前綴已令撞名無害，但號碼失去全團隊唯一意思，用戶報問題講「v12」會有兩個答案 |
| 用 IndexedDB／localStorage 記版本 | 問題在「刪除條件」而不是「點記版本」，換地方記只是多一處要同步的狀態 |

## 後果

- 好處：兩本書可以同時留在離線快取；任何一站 bump 都不會影響另一站；兩站終於可以有獨立的發佈節奏。
- 代價：升級用戶會短暫多一個孤兒 cache（只有一個，不會累積）；`LEGACY` 要記得在一兩個版本後移除。
- 已連帶修好：`tools/qa/check_live.mjs` 原本用 `/const CACHE = "([^"]+)"/` 讀版本，改成 `PREFIX + "vN"` 之後匹配不到，會**靜靜地跳過** CACHE 檢查（實測舊 regex 在部署版上取到空字串）。已改成同時讀兩種寫法，並用故意錯的 `--expect-cache` 驗過會 FAIL。

## 何時重看

- 兩站都上前綴滿一個版本週期之後：把 `LEGACY` 換成 `/^ebooks-v\d+$/` 清走孤兒。
- 加第三個站，或者任何一站搬到獨立 origin：前綴可以簡化，共用計數器可以拆開。
- ADR-0002 第 3 點「號碼只由 Chief 改」與現行分工（CTO 管 CACHE 號碼）不一致，待用戶與 Chief 確認後再處理 ADR-0002 的狀態。
