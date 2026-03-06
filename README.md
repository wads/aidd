# AIDD - AI Driven Development

タスクの規模に応じたプロセスで、品質を保ちながら開発を進めるAI駆動開発のボイラープレートです。

デフォルトは最小プロセス（Lite モード）。必要に応じて要件定義・設計・マルチAgent調査を追加できます。

## Directory Structure

```
aidd/
├── CLAUDE.md                  # エントリポイント（軽量）
├── .claude/
│   └── skills/                # カスタムSkill定義
│       ├── dev/SKILL.md                       # 開発メイン（Lite/Standard/Full）
│       ├── multi-agent-discussion/SKILL.md    # 並行独立調査
│       ├── tdd-cycle/SKILL.md                 # TDDサイクル
│       ├── retrospective/SKILL.md             # 振り返り（KPT）
│       └── worktree-setup/SKILL.md            # git worktreeセットアップ
├── docs/
│   ├── process/               # プロセス定義（Skillから参照）
│   ├── templates/             # ドキュメントテンプレート
│   ├── adr/                   # Architecture Decision Records
│   ├── requirements/          # 要求定義（Full モード）
│   ├── specifications/        # 要件定義（Standard・Full モード）
│   └── designs/               # 詳細設計（Full モード）
├── tasks/
│   ├── todo.md                # TODOリスト
│   ├── lessons.md             # 教訓・ベストプラクティス
│   ├── decisions-log.md       # 意思決定ログ
│   └── retrospectives/        # 振り返り記録
├── src/                       # ソースコード
└── tests/                     # テストコード
```

## Quick Start (New Project)

### Prerequisites

- [Claude Code](https://claude.com/claude-code) がインストール済みであること
- Git がインストール済みであること

### 1. Clone this boilerplate

```bash
git clone <this-repo-url> my-project
cd my-project
rm -rf .git
git init
```

### 2. Configure for your language/framework

#### Go

```bash
go mod init github.com/yourname/my-project
```

CLAUDE.md の Project Configuration を更新:

```markdown
- **Test command**: `go test ./...`
- **Build command**: `go build ./...`
- **Lint command**: `golangci-lint run`
```

.gitignore に追記:

```gitignore
# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
bin/
```

#### Next.js

```bash
npx create-next-app@latest . --use-npm  # or --use-pnpm, --use-yarn
```

CLAUDE.md の Project Configuration を更新:

```markdown
- **Test command**: `npm test`
- **Build command**: `npm run build`
- **Lint command**: `npm run lint`
```

.gitignore に追記:

```gitignore
# Node.js
node_modules/
.next/
out/
```

#### Python (uv)

```bash
uv init
# or with a specific Python version:
uv init --python 3.12
```

CLAUDE.md の Project Configuration を更新:

```markdown
- **Test command**: `uv run pytest`
- **Build command**: `uv build`
- **Lint command**: `uv run ruff check .`
```

.gitignore に追記:

```gitignore
# Python
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/
```

### 3. Initial commit

```bash
git add -A
git commit -m "feat: initialize project from AIDD boilerplate"
```

### 4. Start development

```bash
claude
```

初めての方は [Tutorial](docs/tutorial.md) に沿って進めてください。

## Adapting to an Existing Project

既存プロジェクトにAIDDフレームワークを導入する手順。

### 1. Copy AIDD files

```bash
# 既存プロジェクトのルートで実行

# .claude/skills をコピー
cp -r /path/to/aidd/.claude/skills .claude/skills

# docs/ と tasks/ をコピー
cp -r /path/to/aidd/docs .
cp -r /path/to/aidd/tasks .
```

### 2. Create or update CLAUDE.md

既存の CLAUDE.md がない場合は、ボイラープレートのものをコピーして編集:

```bash
cp /path/to/aidd/CLAUDE.md .
```

既存の CLAUDE.md がある場合は、以下のセクションを追記:

```markdown
## Default Process (Lite mode)

要求確認 → TDD実装 → (判断があればADR記録) → 完了 → 「振り返りしますか？」(任意)

開発を始めるときは `/dev` を使用する。

## Key Skills

- `/dev` - 開発メインスキル（Lite/Standard/Full モード選択）
- `/multi-agent-discussion` - 複数Agentによる並行独立調査
- `/tdd-cycle` - TDDサイクル（Red-Green-Refactor）
- `/retrospective` - 振り返り（KPT、任意）
- `/worktree-setup` - git worktreeセットアップ
```

### 3. Update Project Configuration

CLAUDE.md の Project Configuration をプロジェクトに合わせて更新。

### 4. Commit

```bash
git add .claude/skills docs/ tasks/ CLAUDE.md
git commit -m "feat: adopt AIDD development framework"
```

## Development Process

3つのモードからタスク規模に応じて選択:

| Mode | Use case | Process |
|------|----------|---------|
| Lite（default） | バグ修正、小機能追加 | 要求確認 → TDD → (ADR) → 完了 |
| Standard | 中規模機能、技術選定 | Lite + 要件定義 + Agent調査 + ADR |
| Full | 大規模変更、新アーキテクチャ | Standard + 詳細設計 + フルドキュメント |

詳細は [docs/process/development-workflow.md](docs/process/development-workflow.md) を参照。

## Customization

### Skill の追加

`.claude/skills/<skill-name>/SKILL.md` に新しいSkill定義を追加:

```bash
mkdir .claude/skills/my-skill
vim .claude/skills/my-skill/SKILL.md
```

### Process の変更

`docs/process/` 内のファイルを編集してプロセスをカスタマイズ。
振り返り（`/retrospective`）で得た改善提案を反映する運用を推奨。

## License

MIT
