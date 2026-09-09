---
type: adr
scope: [対象サービス、または system / all]
status: proposed | accepted | superseded | deprecated
updated: YYYY-MM-DD
topic: [判断領域タグ。records_root の domain-terms.md の表から選ぶ。複数可]
summary: [決定の要旨を一行。INDEX.md に出る。何を決めたかが索引だけで分かる文に。` # `（空白-#-空白）以降はコメントとして切られ、引用符でも保護されない]
# 関係があるときだけ書く（無いフィールドは省略する。行ごと消す）:
# considered: [同 topic の既存 ADR のうち、読んだうえで置き換えも補足もしない番号（無関係・依存して併存、どちらも）。同 topic で自分より若い有効 ADR があれば supersedes / amends / considered のどれかに必ず書く]
# issue: [任意。対象 Issue（例 owner/repo#123）。スクリプトは検証しない]
# supersedes: [置き換える旧 ADR の番号。旧 ADR 側には superseded_by と status: superseded を追記する]
# superseded_by: [この ADR を置き換えた新 ADR の番号]
# amends: [補足・部分修正する ADR の番号。補足先の決定は有効のまま残る。補足先には amended_by を追記する]
# amended_by: [この ADR を補足した ADR の番号]
---

# [ADR-NNNN] [タイトル]

## ステータス

[提案中 | 承認済み]（記録時点の状態。以後の失効・補足は frontmatter の status と関係リンクが正で、本文は書き換えない）

## 背景

[この決定が必要になった経緯・課題]

## 検討した選択肢

### 案1: [タイトル]

- 概要: [説明]
- メリット: [利点]
- デメリット: [欠点]

### 案2: [タイトル]

- 概要: [説明]
- メリット: [利点]
- デメリット: [欠点]

## 決定内容

[何を採用するか]

## 設計意図

[なぜこの案が最適と判断したか。何を実現しようとしているか]

## トレードオフ

[この決定で受け入れるデメリット・妥協点。将来のリスクや技術的負債になりうる点]

## 影響範囲

[この決定が影響するコンポーネント・画面・サービス・チーム]

## 議論ログ

- [YYYY-MM-DD] [Agent/Human]: [議論の要点]
