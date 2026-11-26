# Topic registry — maths

`book.json` 的 `code` 必須等於 Uni+ 官方 maths topics list 的 Topic Code，`title` 必須等於表裡的英文名。

這個 repo 只帶**數學**那一份；物理那份在 `Tai-sura/physics-ebooks` 的 `docs/topics/physics.json`。

- 176 個 topic、371 個 subtopic、6 個 level-1 章、6 項 Maths Ability
- 來源 `Maths Topics List(Update 6) (1).xlsx`，匯入 2026-11-26

## level-1

| code | name | strand | topics |
| --- | --- | --- | --- |
| CH1 | Number & Estimation | Number and Algebra | 52 |
| CH2 | Algebra & Functions | Number and Algebra | 26 |
| CH3 | Mensuration & Geometry | Measures, Shape and Space | 51 |
| CH4 | Coordinates & Trigonometry | Measures, Shape and Space | 14 |
| CH5 | Statistics & Probability | Data Handling | 22 |
| CH6 | Calculus | Calculus (M1/M2 only) | 11 |

## 檢查

```
python tools/check_topic.py p5m07a
python tools/check_topic.py --code P5M07 --title "Circles (A)"
```

`check_topic.py` 只讀這個 repo 有的 registry，所以它檢查的是數學書，不會去問物理那份。

## 不要手改 JSON

`maths.json` 是由官方 xlsx 匯入產生的。官方表更新時，在產生 registry 的機器上跑 `tools/import_topics.py --maths <xlsx>`（該匯入器留在那台機，不在這個 repo），再把新的 `maths.json` 連同這份 README 一起提交到這裡。
