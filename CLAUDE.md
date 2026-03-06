# AIDD - AI Driven Development

タスクの規模に応じたプロセスで、品質を保ちながら開発を進めるAI駆動開発フレームワーク。

## Default Process (Lite mode)

```
要求確認 → TDD実装 → (判断があればADR記録) → 完了 → 「振り返りしますか？」(任意)
```

開発を始めるときは `/dev` を使用する。規模に応じて Standard・Full モードも選択可能。

## Project Configuration

- **Test command**: `TODO: プロジェクトに応じて設定` (e.g., `npm test`, `uv run pytest`, `go test ./...`)
- **Build command**: `TODO: プロジェクトに応じて設定`
- **Lint command**: `TODO: プロジェクトに応じて設定`

## Directory Structure

- `src/` - ソースコード
- `tests/` - テストコード
- `docs/` - ドキュメント（プロセス定義、テンプレート、ADR、要求/要件/設計）
- `tasks/` - タスク管理（TODO、教訓、意思決定ログ、振り返り）

## Key Skills

- `/dev` - 開発メインスキル（Lite/Standard/Full モード選択）
- `/multi-agent-discussion` - 複数Agentによる並行独立調査
- `/tdd-cycle` - TDDサイクル（Red-Green-Refactor）
- `/retrospective` - 振り返り（KPT、任意）
- `/worktree-setup` - git worktreeセットアップ
