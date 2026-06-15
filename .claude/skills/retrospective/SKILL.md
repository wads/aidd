---
name: retrospective
description: KPT 形式で振り返りを行う skill。タスク完了後やフェーズ区切りで、Keep、Problem、Try を整理し、次の改善アクションを明確にしたいときに使う。
user-invocable: true
---

# Retrospective

## いつ使うか

- タスクやフェーズの振り返りをしたいとき
- 継続改善のために Keep / Problem / Try を整理したいとき

## 入力

- `topic`

## 出力

- KPT 形式の振り返り結果 → GitHub Issueへコメント
- 採用された改善 → playbook への PR またはIssue

## 扱う Intent

- Learning Intent（作成）

## 読むべき補助ファイル

- `workflow.md`
