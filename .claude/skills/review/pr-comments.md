# PR Comment Review Workflow

## 使い方

- `pr-comments`: 現在ブランチの PR を自動検索
- `pr-comments <PR番号>`: 指定 PR のコメントを取得

## 手順

### Step 1. PR の特定

```bash
gh pr list --head $(git branch --show-current | cat) --json number,title,url,state | cat
```

PR が見つからない場合は番号を確認する。

### Step 2. レビューコメントの取得

利用可能な GitHub PR コメント取得ツールを使い、以下を集める。

- 全レビューコメント
- レビュー全体のステータス
- コメントの投稿者、時刻、対象ファイル、URL

`gh` を使う場合の例:

```bash
gh api repos/<owner>/<repo>/pulls/<PR番号>/comments \
  --jq '.[] | "【\(.user.login)】\(.created_at)\nファイル: \(.path):\(.line // "全体")\n\(.body)\nURL: \(.html_url)\n---"' | cat

gh api repos/<owner>/<repo>/pulls/<PR番号>/reviews \
  --jq '.[] | {author: .user.login, state: .state, body: .body, submittedAt: .submitted_at}' | cat
```

### Step 3. コメントの整理

- 対応必須: Changes Requested / 明確な指摘
- 要確認: 質問形式のコメント
- 任意対応: 提案、nitpick
- 解決済み: 既にコードで対応済みと思われるもの

### Step 4. 報告

`output-format.md` の PR コメント形式に従って報告する。

### Step 5. 対応後の提案

- 対応内容をコミット
- コミットメッセージ案を提示
- 必要に応じて `AI_KNOWLEDGE_BASE/active/ECS-XXXXX/PR_BODY.md` を更新

## 注意事項

- Bot コメントは Bot であることを明記する
- コメントへの返信は行わない
- 仕様不明な指摘は推測で処理しない
