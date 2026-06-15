---
name: review
description: 変更レビューを行う skill。現在のブランチ差分のコードレビュー、または PR レビューコメントの整理と対応提案が必要なときに使う。規約、設計、仕様適合、レビュー応答方針をまとめて扱う。
---

# Review

## いつ使うか

- 現在のブランチの変更をレビューしたいとき
- PR についたレビューコメントを整理したいとき
- 規約、設計、仕様適合の観点で問題点を洗い出したいとき
- マージ前の P7 検証・レビュー（受入れ検証・昇格判定・PR 説明の最終化）を行うとき

## 入力

- review target: `branch`、`pr-comments` または `acceptance`（P7）
- オプション: `staged`, `file:<path>`, `quick`, `PR番号`
- `acceptance` の場合: P2 の確定版 AC/QC（Jira コメント）

## 出力

- 優先度つきのレビュー結果、もしくは PR コメント一覧と推奨対応
- `acceptance` の場合: AC-ID つき検証記録 → PR コメント、昇格判定（あり/なし）、必須セクションをそろえた PR 説明、コンテキストスナップショット

## 扱う Intent

- Verification Intent（検証記録）/ Product・Decision・Design Intent（整合確認の入力）

## 読むべき補助ファイル

- `branch.md`
- `pr-comments.md`
- `acceptance.md`（P7 のとき）
- `checklist.md`
- `output-format.md`
