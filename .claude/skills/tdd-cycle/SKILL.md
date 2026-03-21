---
name: tdd-cycle
description: TDDサイクル（Red-Green-Refactor）実行スキル。
user-invocable: true
---

# TDD Cycle

TDDサイクル（Red-Green-Refactor）実行スキル。

## Arguments

- feature: 実装する機能の説明（必須）
- test_command: テスト実行コマンド（省略時: CLAUDE.mdのTest commandを使用）

## Process

1. **Confirm (確認)**
   - 実装する振る舞いの一覧を提示
   - 人間に実装順序を確認

2. **Red (失敗するテスト)**
   - テストファイルに失敗するテストを追加
   - テスト実行 -> 失敗を確認
   - 人間に確認: "Red phase complete. Proceed to Green?"

3. **Green (最小実装)**
   - テストを通す最小限のコードを実装
   - テスト実行 -> 成功を確認
   - 人間に確認: "Green phase complete. Proceed to Refactor?"

4. **Refactor (リファクタリング)**
   - コードの改善（重複除去、命名改善等）
   - テスト実行 -> 成功を維持
   - 人間に確認: "Refactor complete. Commit?"

5. **Repeat or Commit**
   - 次の振る舞いがあれば Step 2 に戻る
   - なければcommit

## Guidelines

- 1サイクルの変更は30行以下を目標
- テストは振る舞いを検証する（実装の詳細ではなく）
- Green phaseでは「動く最小のコード」を書く
- Refactor phaseでのみコード改善を行う

## Testing Principles

- **テストの4つの柱**: 退行保護、リファクタリング耐性、迅速なフィードバック、保守性
- **テスト優先順位**: 出力ベース > 状態ベース > 通信ベース（モック）
- **モック方針**: 外部依存（DB, API, ファイルシステム）のみモック。ドメインモデルはモックしない
- **Classical派を優先**: 可能な限り実オブジェクトを使用

## Reference

詳細は `docs/process/tdd-guide.md` を参照。
