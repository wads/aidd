---
name: dev
description: AI 駆動開発の標準フローへの薄い入口。GitHub Issueの type-* ラベルからルート（実施フェーズ構成）を特定し、各フェーズの skill（requirements、ui-prototyping、adr、design-docs、implementation-plan、tdd-cycle、review、retrospective）へ振り分ける。orchestrator 完成までの移行期間用。
user-invocable: true
---

# Dev

## いつ使うか

- GitHub Issueに着手して開発を始めるとき（P1 着手）
- Issue のタイプに応じた進め方を確認したいとき

## 入力

- `ticket`: GitHub Issue 番号（`type-*` ラベルが付与されていること）

## 出力

- 合意済みのルート（実施フェーズ構成）と P2.5 プロトタイピング 実施要否
- 各フェーズ skill の実行結果

## 扱う Intent

- Product Intent（入力）。各フェーズの Intent はそれぞれの skill が扱う

## ルール

- タイプラベルのないIssue には着手しない。`product-intent` での整備へ差し戻す
- フェーズの実施有無はルート（`routes.md`）が決め、成果物の深さは判断駆動の原則が決める
- 各フェーズの exit 条件（人間承認）を飛ばさない

### P6 実装の自動進行（スタック時）

計画のステップが複数あり stacked PR で進める場合（`implementation-plan/workflow.md` §3 で合意）:

- ステップ完了ごとに PR を作成して人間チェックに出し、**チェック完了を待たずに次ステップへ着手する**（先行して積む）。先行分は下位への指摘次第で積み替え・手戻りが起きることを許容する
- **中断する場合**: 下位 PR への指摘が設計判断（P3/P4 再入）を要するとき。自動進行と先行積みを止め、人間の採用判断を経てから再開する（既存の自動進行例外と同じ扱い）。目安は指摘の解消に「どの案を採るか」の選択が生じること、共有 API・共有部品の設計変更に触れること
- 積み替え・マージの手順は `stacked-pr` を参照する（機構は GitHub ネイティブ機能 `gh stack` が持つ）。P6 中に計画が変わったときのスタック構成の更新は `stacked-pr/workflow.md` §7（並べ替え・改名・削除に非対話の手段は無く、対話型 TUI はエージェントが起動してはならない。スタックを組み直す）

## 読むべき補助ファイル

- `workflow.md`
- `routes.md`
- `escalation.md`
- `examples.md`
