---
name: tdd-cycle
description: TDD サイクルを回す skill。実装する振る舞いを TODO リストに分解し、失敗するテストの確認（Red）、最小実装（Green）、重複除去（Refactor）を繰り返して進める。テストの出所を AC・設計書に固定することで、テストが実装と独立であることを保証し、ゲート 1（テスト green）の信頼性を支える。
---

# TDD Cycle

## いつ使うか

- 振る舞いベースで小さく実装を進めたいとき
- `dev` のタイプ別ルートから実装フェーズ（P6）へ入るとき

## 入力

- `feature`（実装する振る舞い）
- 確定版の受入れ条件（AC-ID、テストレベル割当）と実装計画（あれば）
- `test_command`（任意）

## 出力

- Red / Green / Refactor を経た実装結果
- 受入れ条件⇄テスト対応表 → PR 説明（各テストがどの AC-ID を検証するか）

## 扱う Intent

- Verification Intent（テストとして作成）/ Product・Design Intent（入力）

## 読むべき補助ファイル

- `workflow.md`
- `examples.md`
