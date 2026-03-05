# AIDD - AI Driven Development

Claude Codeで「要求の整理からTDD実装・振り返りまで」を複数AIエージェントと対話しながら一気通貫で進められる、AI駆動開発のボイラープレートです。

## Directory Structure

```
aidd/
├── CLAUDE.md                  # エントリポイント（@importsでプロセス文書を参照）
├── .claude/
│   ├── agents/                # カスタムAgent定義
│   │   ├── researcher.md      #   調査・情報収集
│   │   ├── developer.md       #   TDD実装
│   │   └── reviewer.md        #   レビュー・品質
│   └── skills/                # カスタムSkill定義
│       ├── multi-agent-discussion/SKILL.md
│       ├── tdd-cycle/SKILL.md
│       ├── retrospective/SKILL.md
│       └── worktree-setup/SKILL.md
├── docs/
│   ├── process/               # プロセス定義
│   ├── templates/             # ドキュメントテンプレート
│   ├── adr/                   # Architecture Decision Records
│   ├── requirements/          # 要求定義
│   ├── specifications/        # 要件定義
│   └── designs/               # 詳細設計
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
# aidd/ は本ボイラープレートのクローン先パス

# .claude/ ディレクトリ（agents, skills）をコピー
cp -r /path/to/aidd/.claude/agents .claude/agents
cp -r /path/to/aidd/.claude/skills .claude/skills

# docs/ と tasks/ をコピー
cp -r /path/to/aidd/docs .
cp -r /path/to/aidd/tasks .
```

### 2. Create or update CLAUDE.md

既存の CLAUDE.md がある場合は、以下のセクションを追記:

```markdown
## Development Process
@docs/process/development-workflow.md

## Agent Team Guide
@docs/process/agent-team-guide.md

## TDD Guide
@docs/process/tdd-guide.md

## Human Checkpoints
@docs/process/human-checkpoints.md
```

既存の CLAUDE.md がない場合は、ボイラープレートのものをコピーして編集:

```bash
cp /path/to/aidd/CLAUDE.md .
```

### 3. Update Project Configuration

CLAUDE.md の Project Configuration をプロジェクトに合わせて更新。

#### Go project

```markdown
- **Test command**: `go test ./...`
- **Build command**: `go build ./cmd/server`
- **Lint command**: `golangci-lint run`
```

#### Next.js project

```markdown
- **Test command**: `npm test`
- **Build command**: `npm run build`
- **Lint command**: `npm run lint`
```

#### Python/uv project

```markdown
- **Test command**: `uv run pytest`
- **Build command**: `uv build`
- **Lint command**: `uv run ruff check .`
```

### 4. Adjust directory mapping

既存プロジェクトのディレクトリ構成に合わせて CLAUDE.md を調整:

```markdown
## Directory Structure
- `cmd/` - エントリポイント (Go)
- `internal/` - 内部パッケージ (Go)
- `app/` - Next.js App Router
- `src/` - ソースコード (Python)
- `tests/` or `test/` - テストコード
```

### 5. Commit

```bash
git add .claude/agents .claude/skills docs/ tasks/ CLAUDE.md
git commit -m "feat: adopt AIDD development framework"
```

## Development Process Flow

```
[1.要求確認] --> 人間承認 --> [2.要件定義] --> 人間承認 --> [3.ADR作成]
    --> 人間承認 --> [4.詳細設計] --> 人間承認 --> [5.worktree作成]
    --> [6.TDD実装] --> 人間確認 --> [7.振り返り]
```

詳細は [docs/process/development-workflow.md](docs/process/development-workflow.md) を参照。

## Customization

### Agent の追加

`.claude/agents/` に新しいAgent定義を追加:

```bash
# 例: architect agent
vim .claude/agents/architect.md
```

詳細は [docs/process/agent-team-guide.md](docs/process/agent-team-guide.md) を参照。

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
