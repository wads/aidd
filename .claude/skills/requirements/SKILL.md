---
name: requirements
description: P2 要求整理を行う skill。Jira チケットの Product Intent を開発で使える粒度へ具体化し、受入れ条件（AC）と品質条件（QC）を ID・信頼性マーカー・検証手段タグつきで確定して Jira コメントへ残すときに使う。
---

# Requirements

## いつ使うか

- チケットに着手し、ルート合意（P1）後に「完了とは何か」を確定したいとき
- 受入れ条件の曖昧・矛盾・漏れを洗い出したいとき
- 技術品質条件（テスト範囲・性能・互換性・セキュリティ・観測性）を確定したいとき

## 入力

- Jira チケット（Product Intent）とタイプ（`type-*` ラベル）
- P2.5 を実施した場合は UI 合意の Delta

## 出力

- 確定版の受入れ条件・品質条件 → Jira コメント（Intent Delta として追記）
  - 各項目に ID（`AC-n` / `QC-n`）、信頼性マーカー（🔵/🟡/🔴）、テストレベル（unit / integration / E2E）、検証手段タグ（CI / テスト / 手動）

## 扱う Intent

- Product Intent（入力）/ Intent Delta（追記）

## exit 条件（ゲート）

- 全受入れ条件が「検証手順を書ける」粒度になっている
- 🟡・🔴 マーカーが残っていない（人間が確認して 🔵 にするか、対象外として畳む）
- 人間が品質条件を承認している

## 読むべき補助ファイル

- `workflow.md`
- `checklist.md`
- `output-format.md`
