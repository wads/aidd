# Branch Review Workflow

## 使い方

- `branch`: main との差分をレビュー
- `branch staged`: ステージ済み変更をレビュー
- `branch file:<パス>`: 特定ファイルのみレビュー
- `branch quick`: 重要な問題のみ指摘

## 手順

### Step 1. 差分の取得

`--first-parent --no-merges` を使い、現在ブランチに直接コミットされた変更のみを対象にする。

```bash
git log --first-parent --no-merges main..HEAD --oneline | cat
git log --first-parent --no-merges main..HEAD -p | cat
git log --first-parent --no-merges main..HEAD --name-only --format="" | sort | uniq | cat
```

差分だけでなく変更ファイルの全体も読む。

### Step 2. コンテキストの把握

JIRA 番号をコミットメッセージから抽出し、以下があれば読む。

- `AI_KNOWLEDGE_BASE/active/ECS-xxxxx/CONTEXT.md`
- `AI_KNOWLEDGE_BASE/active/ECS-xxxxx/TODO.md`

### Step 3. アーキテクチャの把握

変更ファイルのディレクトリ構成、命名、import 関係を読んで採用アーキテクチャを推定する。

- レイヤー分割の有無
- 依存方向
- 責務の分担
- テストの配置

推定できなければ「アーキテクチャ不明」として汎用的にレビューする。

### Step 4. レビュー

共通観点は `checklist.md` を参照する。

重点観点:

- 規約違反
- ドメイン知識とシステム都合の混在
- 仕様未達、範囲逸脱、エッジケース不足

### Step 5. 報告

`output-format.md` のブランチレビュー形式に従って報告する。

## 注意事項

- 未変更コードに docstring や型注釈を要求しない
- 単一使用の処理に抽象化を要求しない
- 問題点だけでなく具体的な改善提案を添える
- 仕様不明な場合は推測せず要確認として扱う
