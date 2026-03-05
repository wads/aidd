# TDD Guide (Kent Beck Style)

Kent Beck方式のテスト駆動開発ガイド。

## Red-Green-Refactor Cycle

### Red: 失敗するテストを書く
1. 実装したい振る舞いを1つ選ぶ
2. その振る舞いを検証するテストを書く
3. テストが失敗することを確認する（コンパイルエラーも含む）

### Green: テストを通す最小限の実装
1. テストを通すために最も単純なコードを書く
2. ハードコード、仮実装でもOK
3. テストが通ることを確認する

### Refactor: リファクタリング
1. 重複を除去する
2. コードの意図を明確にする
3. テストが引き続き通ることを確認する

## Testing Principles (Vladimir Khorikov)

### 4 Pillars of Good Tests
1. **Protection against regressions** - バグ検出能力
2. **Resistance to refactoring** - 実装変更で偽陽性を出さない
3. **Fast feedback** - 高速に実行できる
4. **Maintainability** - 理解・実行が容易

### Test Classification
- **Output-based testing** (preferred): 入力に対する出力を検証
- **State-based testing**: 操作後の状態を検証
- **Communication-based testing** (last resort): モックとの相互作用を検証

### Mock Usage
- 外部依存（DB, API, ファイルシステム）のみモック
- ドメインモデルはモックしない
- Classical派（実オブジェクト優先）をデフォルトとする

## Workflow with `/tdd-cycle`

```
/tdd-cycle を実行
  -> テスト対象の振る舞いを確認
  -> Red: テスト作成 -> 失敗確認
  -> Green: 最小実装 -> 成功確認
  -> Refactor: 改善 -> 成功維持
  -> 次の振る舞いへ（またはcommit）
```

## Test Command Configuration

テスト実行コマンドはプロジェクトごとに設定:
- CLAUDE.md の `Test command` を更新する
- 例: `npm test`, `uv run pytest`, `go test ./...`, `cargo test`
