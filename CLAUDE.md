# AIDD - AI Driven Development

Claude Codeで「要求の整理からTDD実装・振り返りまで」を複数AIエージェントと対話しながら一気通貫で進められる、AI駆動開発フレームワーク。

## Development Process

@docs/process/development-workflow.md

## Agent Team Guide

@docs/process/agent-team-guide.md

## TDD Guide

@docs/process/tdd-guide.md

## Human Checkpoints

@docs/process/human-checkpoints.md

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

- `/multi-agent-discussion` - 複数Agentで調査・議論・合意形成
- `/tdd-cycle` - TDDサイクル（Red-Green-Refactor）
- `/retrospective` - 振り返り（KPT）
- `/worktree-setup` - git worktreeセットアップ
