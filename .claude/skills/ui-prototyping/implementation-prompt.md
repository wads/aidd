# Implementation Prompt

`IMPLEMENTATION_PROMPT.md` は、確定したプロトタイプを実装工程へ引き継ぐための構造化文書である。

## 目的

- プロトタイプ段階の合意内容を失わない
- AI または人間実装者に必要な制約を明文化する
- variant ごとの差分を template に閉じ込める

## 生成手順

1. プロトタイプ本体（`.tsx`）を読み、Props / import / JSX 構造 / 状態管理を抽出する
2. スタイルファイル（`.module.scss` 等）を読み、デザイントークン参照 / クラス名 / BEM 構造を抽出する
3. プレビュー用ファイル（`.stories.tsx`）を読み、Story 一覧 / argTypes / テスト要件のヒントを抽出する
4. 対話履歴から PdM の要求・制約・配置先の合意・未確定事項を抽出する
5. プロトタイプに含まれない事項（Analytics 計測、E2E テスト属性、Container 分離方針、テスト方式）を project-config と慣習から推定して補う
6. stack に対応する template を選ぶ
7. プロトタイプディレクトリ配下に `IMPLEMENTATION_PROMPT.md` として出力する。末尾に **「AI 向け生成指示」** セクションを必ず含めること（後続の実装 AI に渡す前提）

## Template の選択

- `react-storybook`: `assets/implementation-prompt-react.template.md`

## 注意事項

- 生成していない情報を断定しない
- 未確定事項は TODO や open question として残す
- Analytics、E2E、Container 分離はプロジェクトルールに沿って補う
