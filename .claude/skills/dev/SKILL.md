---
name: dev
description: AI 駆動開発の標準フローへの薄い入口。Jira チケットの type-* ラベルからルート（実施フェーズ構成）を特定し、各フェーズの skill（requirements、ui-prototyping、adr、design-docs、implementation-plan、tdd-cycle、review、retrospective）へ振り分ける。orchestrator 完成までの移行期間用。
---

# Dev

## いつ使うか

- Jira チケットに着手して開発を始めるとき（P1 着手）
- チケットのタイプに応じた進め方を確認したいとき

## 入力

- `ticket`: Jira チケット番号（`type-*` ラベルが付与されていること）

## 出力

- 合意済みのルート（実施フェーズ構成）と P2.5 実施要否
- 各フェーズ skill の実行結果

## 扱う Intent

- Product Intent（入力）。各フェーズの Intent はそれぞれの skill が扱う

## ルール

- タイプラベルのないチケットには着手しない。`product-intent` での整備へ差し戻す
- フェーズの実施有無はルート（`routes.md`）が決め、成果物の深さは判断駆動の原則が決める
- 各フェーズの exit 条件（人間承認）を飛ばさない

## 読むべき補助ファイル

- `workflow.md`
- `routes.md`
- `escalation.md`
- `examples.md`
