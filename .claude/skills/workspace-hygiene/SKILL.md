---
name: workspace-hygiene
description: 作業開始前のワークツリー整理と topic branch 作成を行う skill。実装や調査を始める前に、未コミット差分を `git commit`、`git stash`、または承認済み削除で解消し、差分がない状態で topic branch を切ってから着手するときに使う。
---

# Workspace Hygiene

## いつ使うか

- 実装、調査、リファクタリングなどの作業を始める前
- topic branch を切って作業を始めるとき
- 既存差分の扱いを明確にしてから安全に進めたいとき

## 入力

- `task`
- 必要なら branch 名

## 出力

- 差分整理方針
- 差分ゼロ確認
- 作成した topic branch 名

## 読むべき補助ファイル

- `workflow.md`
