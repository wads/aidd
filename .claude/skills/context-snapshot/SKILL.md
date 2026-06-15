---
name: context-snapshot
description: 開発単位（Issue）の最新の意図と検証状態を、人間が読みやすい 1 枚の HTML スナップショットとして生成する skill。P7 の受入れ判断の材料として使うほか、「このIssueいまどうなってる？」を確認したい任意のタイミングで実行できる。生成ビューであり、真実の源ではない。
user-invocable: true
---

# Context Snapshot

## いつ使うか

- P7 検証・レビューで、受入れ判断の材料を人間へ提示するとき
- Issue の現在状態（意図・判断・検証）を素早く把握したいとき

## 入力

- GitHub Issue（Product Intent 本文 + Intent Delta コメント）
- 関連 ADR・設計書（Issue からのリンク）
- PR（実装方針、AC⇄テスト対応表、検証記録）

## 出力

- HTML スナップショット 1 ファイル（生成日付き） → GitHub Issueへ添付

## 扱う Intent

- 全 Intent の生成ビュー（新しい Intent は作らない）

## 原則

- スナップショットはビューであり、真実の源ではない。不変記録（ADR・設計書・テスト）と食い違った場合は記録側を正とする
- 保守しない。古くなったら捨てて再生成する
- スナップショットを直接編集して情報を足さない。足すべき情報は元の記録（GitHub Issue・ADR・設計書・PR）に書いてから再生成する

## 読むべき補助ファイル

- `workflow.md`
