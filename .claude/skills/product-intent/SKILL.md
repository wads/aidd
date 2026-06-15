---
name: product-intent
description: 要求を Product Intent として整理し、AIDD で実装・テスト・レビューに使える Jira チケットへ整える skill。タイプ（feature / bugfix / hotfix / refactoring / chore / spike）を必須入力として確定し、タイプ別テンプレートで構造化、品質チェックを経て type-* ラベルつきでチケット化するときに使う。
---

# Product Intent

## いつ使うか

- 実装前に Jira チケットを整備したいとき
- PdM が「何を作るか」を AIDD 向けに整理したいとき
- エンジニアが bugfix / refactoring / chore / spike のチケットを素早く作りたいとき
- チケット内容が必要十分か、不備や過剰な記述がないか確認したいとき

## 入力

- メモまたはチケットのたたき台
- タイプ（不明な場合は対話で確定する。AI が推測で確定しない）

## 出力

- タイプ確定済み・品質チェック済みのチケット案
- 必要なら Jira 作成ツールを用いたチケット作成結果（課題タイプと `type-*` ラベルを設定）

## 扱う Intent

- Product Intent（作成）

## 読むべき補助ファイル

- `workflow.md`
- `type-templates.md`
- `checklist.md`
- `examples.md`
