# React Storybook Variant

`stack: react-storybook` の project で使う variant。

## 想定 stack

- React
- TypeScript
- Storybook
- CSS Modules / SCSS などのコンポーネント単位スタイル

## 生成ファイル

```text
{prototypes-dir}/
└── Proto{Name}/
    ├── Proto{Name}.tsx
    ├── Proto{Name}.module.scss
    └── Proto{Name}.stories.tsx
```

プロジェクト規約で別拡張子や別配置が指定されている場合は preset を優先する。

## 生成ルール

- **Presentational のみ**: Container、データ取得、API 連携は含めない
- **ローカル状態は OK**: フォーム入力→プレビュー反映、タブ切替、開閉トグル等、PdM とのすり合わせに必要な UI の動きは `useState` で実装してよい
- **Storybook の主要状態を必ず作る**: Default、各バリエーション、エラー、ローディング、空状態など、PdM が確認する状態を網羅する
- **argTypes ルール**: Props が Union 型リテラル（例: `'Primary' | 'Secondary'`）の場合は `argTypes` で `control: { type: 'select' }` を設定し、Storybook UI から切り替え可能にする
- **既存コンポーネントは実物を読んで合わせる**: 型定義（`.tsx`）から Props を直接確認し、正しい import パス・正しい Props 名で渡す
- **デザイントークンを優先**: ハードコード値（hex、px、rem 直書き）を避け、project-config のトークンを `@use` で参照する
- **Proto prefix**: コンポーネント名・ディレクトリ名に必ず付ける

## プレビュー

- project-config の Storybook コマンドに従う
- title 規約、stories パス、argTypes のルールを合わせる

## 実装ハンドオフで含めるもの

- コンポーネント概要
- ファイル構成
- Props interface
- デザイントークン参照
- クラス設計
- デバイス差分
- 既存コンポーネント利用
- 状態管理
- Analytics / E2E
- Story 一覧
- テスト要件
- 制約事項
