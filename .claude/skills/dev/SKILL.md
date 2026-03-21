---
name: dev
description: AI駆動開発のメインスキル。タスク規模に応じたモード（Lite/Standard/Full）で開発プロセスを実行する。
user-invocable: true
---

# Dev

AI駆動開発のメインスキル。タスク規模に応じたモード（Lite/Standard/Full）で開発プロセスを実行する。

## Arguments

- request: 実装する内容（必須）
- mode: プロセスモード（省略時: lite）
  - lite: デフォルト。要求確認 + TDD実装
  - standard: lite + 要件定義 + マルチAgent調査
  - full: standard + 詳細設計 + フルドキュメント化

## Process

### Lite モード（デフォルト）

1. **Confirm (要求確認)**
   - 要求内容を整理して人間に提示
   - 実装スコープと受け入れ基準を確認
   - 人間の承認を得てから次へ進む

2. **TDD Implementation (TDD実装)**
   - `/tdd-cycle` を実行してRed-Green-Refactorサイクルで実装
   - テスト実行コマンドは CLAUDE.md の Test command を使用

3. **ADR (判断の記録、該当時のみ)**
   - 実装中に技術的な判断があった場合、`docs/adr/` に軽量ADRを記録
   - テンプレート: `docs/templates/adr-template.md`

4. **Complete (完了)**
   - 実装結果を報告
   - 「振り返りしますか？」と確認
   - 希望すれば `/retrospective` を実行

### Standard モード

Lite モードの Step 1 と Step 2 の間に以下を追加:

- **Specification (要件定義)**: 要求を具体的な要件に分解。`docs/specifications/` に作成。人間の承認を得る
- **Multi-Agent Research (マルチAgent調査)**: `/multi-agent-discussion` で技術選択肢を調査。人間が技術決定
- **ADR (技術決定の記録)**: 調査結果と決定を `docs/adr/` に記録。人間の承認を得る

### Full モード

Standard モードに以下を追加:

- **Requirements (要求定義)**: `docs/requirements/` にフォーマルな要求定義を作成
- **Detailed Design (詳細設計)**: 実装方針を設計し `docs/designs/` に設計書を作成。レビューを実施。人間の承認を得る

## Git & PR ワークフロー

- **Draft PR作成**: 最初の TODO 完了後に Draft PR を作成する
- **TODO完了時**: 各TODOが完了したらコミットして Draft PR へ push し、今後の進め方を確認する
- **コミットメッセージ**: Conventional Commits 形式で記述する
- **PR本文**: 完了済み・残作業のチェックリストを含め、進捗を反映する

## Mode Selection Guide

迷った場合の目安:
- **Lite**: 1-2ファイルの変更、既知パターンの適用
- **Standard**: 複数ファイルの変更、技術選定が必要
- **Full**: モジュール横断の変更、新アーキテクチャ導入

## Reference

- プロセス詳細: `docs/process/development-workflow.md`
- チェックポイント: `docs/process/human-checkpoints.md`
- マルチAgent調査: `docs/process/agent-team-guide.md`
