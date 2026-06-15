---
name: ui-prototyping
description: UI プロトタイピングを支援する skill。要求テキストやユーザーストーリーから、対象プロジェクトのデザインシステムとコーディング規約に沿ったプロトタイプを生成し、PdM と早期に見た目・操作感をすり合わせるときに使う。現在は React + Storybook 系を対象とし、project-config で project ごとの詳細を切り替える。
user-invocable: true
---

# UI Prototyping

## いつ使うか

- 実装前に UI の見た目と操作感を試作したいとき
- PdM とエンジニアで「コレジャナイ」を早い段階で潰したいとき
- 要求からプロトタイプと実装向けハンドオフ文書を作りたいとき

## 入力

- GitHub Issueの Product Intent と受入れ条件（P2 の暫定版でよい）。Issue前の素の `request` も受け付ける
- `project-config.md`
- 参考資料（任意）

## 出力

- プロトタイプ一式 → マージしない proto branch（GitHub Issueからリンク、短期コンテキスト）
- プレビュー方法
- `IMPLEMENTATION_PROMPT.md`（P5 実装計画の入力になる）
- 合意した UI の振る舞い・状態 → 受入れ条件の Delta として GitHub Issueへコメント

## 扱う Intent

- Product Intent（Delta 追記）/ Design Intent（UI、短期）

## 読むべき補助ファイル

- `workflow.md`
- `project-config-contract.md`
- `implementation-prompt.md`
- `variants/react-storybook.md`
- `presets/`
- `assets/`
