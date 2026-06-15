# AIDD Common Rules

## Purpose

この playbook は、AI 駆動開発（AIDD）を安全かつ継続的に改善するための共通運用ルールを提供する。

## Default Process

開発プロセスはチケットのタイプ（Jira ラベル `type-*`）で決まる。詳細は `docs/design/0001-dev-phase-decomposition.md` を正とする。

- チケットは `product-intent` でタイプを確定して作成する（feature / bugfix / hotfix / refactoring / chore / spike）
- 着手は `dev` から。タイプ別ルートに従い各フェーズ skill を実行する
- 成果物の深さは判断駆動: ADR・設計書は書くべき判断が生じたときだけ作る
- 短期コンテキストは PR / Jira へ、長期記録（ADR・設計書・テスト）はプロダクト repo へ。マージ前に短期コンテキストの昇格を判定する

## Core Skills

- `product-intent`（チケット作成）
- `dev`（P1 着手・ルート振り分け）
- `requirements`（P2 要求整理）
- `adr`（P3 技術判断）
- `design-docs`（P4 設計）
- `implementation-plan`（P5 実装計画）
- `tdd-cycle`（P6 実装）
- `review`（P7 検証・レビュー）
- `context-snapshot`（P7 スナップショット）
- `retrospective`（P8 振り返り）
- `multi-agent-discussion`

## Operational Skills

- `daily-sentry-check`

## Migration Skills

- `ui-migration`

## Prototyping Skills

- `ui-prototyping`

## Principles

- 要求確認なしに大きい実装を始めない
- 人間承認ポイントを明示する。最終決定は常に人間が行う
- AI は議論で率直な意見・懸念・反論を提示し、人間の意向への同調を品質より優先しない
- 技術判断は必要に応じて ADR に記録する
- TDD を優先する
- 変更を小さく刻む
- 推測をマーカーなしで埋め込まない（信頼性マーカー 🔵/🟡/🔴。ゲート通過時に 🟡・🔴 を残さない）
- skill 本文は `.agents/skills/` を source of truth として扱う
- stack が同じ差分は preset、stack 自体の差分は variant で扱う
- PR 説明には必須セクション（受入れ条件⇄テスト対応表、技術判断、短期コンテキストの昇格判定、未検証項目）をそろえる。該当がなくても「なし」と明記する
