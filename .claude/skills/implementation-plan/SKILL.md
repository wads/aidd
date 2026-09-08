---
name: implementation-plan
description: P5 実装計画を行う skill。確定済みの要求・設計をもとに、実装順序・変更範囲・検証方針を Execution Intent としてまとめ（ステップが複数なら stacked PR の構成もあわせて確定し）、人間の承認を得てから実装（P6 実装）へ進むときに使う。
user-invocable: true
---

# Implementation Plan

## いつ使うか

- 実装に入る前に、刻み方と人間確認ポイントを合意したいとき
- どの AC をどのステップ・どのテストで満たすかを計画したいとき

## 入力

- 確定版の受入れ条件・品質条件（P2 要求整理、AC/QC ID）
- 設計書・ADR（あれば）
- P2.5 プロトタイピングを実施した場合は `IMPLEMENTATION_PROMPT.md`

## 出力

- 実装方針（`template.md` 参照、使い捨ての短期コンテキスト）
  - 各ステップに AC-ID 対応と TDD / DIRECT 区分
  - スタックにしない計画: draft PR の説明文に書く
  - スタック構成に合意した計画（`workflow.md` §3）: 計画全体（スタック構成を含む）を Issue コメントに書き、最下段 draft PR の説明は自ステップ分にする（手順は `stacked-pr`）

## 扱う Intent

- Execution Intent（作成）/ Product・Design・Decision Intent（入力）

## exit 条件（ゲート）

- 各ステップが AC-ID・設計のどの項目に対応するか明示されている
- 全ステップに TDD / DIRECT 区分があり、DIRECT には実施手順と検証手順がある
- スタックにする計画では、スタック構成（各 PR の内容・積む順序・base 関係）が合意されている（適用条件は `workflow.md` §3・`dev/routes.md`）
- 人間が計画を承認している

## 読むべき補助ファイル

- `workflow.md`
- `template.md`
