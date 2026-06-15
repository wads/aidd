@shared/rules/common.md

# aidd テンプレート

AI 駆動開発（AIDD）の汎用 playbook テンプレート。skill 本文は `.claude/skills/` 配下にあり、Claude Code がネイティブ skill として認識する（`/dev` のように起動できる）。

## AIDD Binding

このリポジトリ自身は standalone（記録はこの repo の `docs/` に置く）。

```
records_root: docs/
issue_repo:   <このリポジトリ>
service:      （なし）
```

このテンプレートを各プロジェクトで使うときは、利用側プロジェクトの `CLAUDE.md` に Binding を宣言する。コンテキストハブを使う例:

```
records_root: ../remosys-context/contexts
issue_repo:   <owner>/remosys-context
service:      remosys-frontend
```

全フェーズの skill はこの Binding だけに従う（フェーズごとに規約を混在させない）。詳細は `shared/rules/common.md` と `docs/manual.md` を参照。

## Project Configuration

- **Test command**: `TODO: プロジェクトに応じて設定`（例: `npm test`, `uv run pytest`, `go test ./...`）
- **Build command**: `TODO: プロジェクトに応じて設定`
- **Lint command**: `TODO: プロジェクトに応じて設定`
