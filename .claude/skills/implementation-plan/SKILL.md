---
name: implementation-plan
description: P5 実装計画を行う skill。確定済みの要求・設計をもとに、実装順序・変更範囲・検証方針を Execution Intent として draft PR の説明文にまとめ、人間の承認を得てから実装（P6）へ進むときに使う。
---

# Implementation Plan

## いつ使うか

- 実装に入る前に、刻み方と人間確認ポイントを合意したいとき
- どの AC をどのステップ・どのテストで満たすかを計画したいとき

## 入力

- 確定版の受入れ条件・品質条件（P2、AC/QC ID）
- 設計書・ADR（あれば）
- P2.5 を実施した場合は `IMPLEMENTATION_PROMPT.md`

## 出力

- 実装方針 → draft PR の説明文（`template.md` 参照、使い捨ての短期コンテキスト）
  - 各ステップに AC-ID 対応と TDD / DIRECT 区分

## 扱う Intent

- Execution Intent（作成）/ Product・Design・Decision Intent（入力）

## exit 条件（ゲート）

- 各ステップが AC-ID・設計のどの項目に対応するか明示されている
- 全ステップに TDD / DIRECT 区分があり、DIRECT には実施手順と検証手順がある
- 人間が計画を承認している

## 読むべき補助ファイル

- `workflow.md`
- `template.md`
