# AIDD Playbook

以下の共通ルールに従ってください。

@shared/rules/common.md

## Skills

必要に応じて `.claude/skills/` 配下の skill（各 `SKILL.md`）を参照してください。

## Branch / Workspace Hygiene

作業開始前に、必ず作業ツリーの差分を確認してください。

- 未コミット変更がある場合は、そのまま作業を開始してはいけません
- 必ず `git commit`、`git stash`、またはユーザー承認済みの削除で差分を解消してから進めてください
- 差分解消後、必ず topic branch を作成してから実装や調査を開始してください
- topic branch 作成前にコード変更を行ってはいけません
- 既存差分の扱いが不明な場合は、ユーザーに確認してください
