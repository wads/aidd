---
name: adr
description: P3 技術判断を行う skill。選択肢のある技術判断を整理し、人間の採用判断を経て ADR として Binding の records_root（既定 docs/adr/）にイミュータブルに残すときに使う。判断が生じたときだけ実行し、フェーズに来たからという理由では書かない。
user-invocable: true
---

# ADR

## いつ使うか

- 選択肢のある技術判断が生じたとき（ライブラリ選定、方式選択、アーキテクチャ変更）
- 既存 ADR の判断を置き換える必要が出たとき
- P7 の短期コンテキストの昇格で、捨てた選択肢の判断を記録化するとき

## 入力

- 確定済みの要求（P2 の AC/QC）
- 判断が必要になった背景

## 出力

- ADR → `{records_root}/adr/{連番}-short-title.md`（service/system 分割は Binding に従う。テンプレート: `shared/templates/adr-template.md`）
- 対象の GitHub Issue へ ADR のリンクをコメント

## 扱う Intent

- Decision Intent（作成）

## exit 条件（ゲート）

- 採用しなかった選択肢とその理由が書かれている
- 人間が採用を判断している（AI は推奨を提示するが決定しない）

## 読むべき補助ファイル

- `workflow.md`
- `shared/templates/adr-template.md`
- `shared/templates/adr-example-0000-use-adr.md`
