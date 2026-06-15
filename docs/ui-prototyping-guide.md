# UI Prototyping Guide

`ui-prototyping` は、実装前に UI の見た目と操作感を試作し、PdM とエンジニアの認識ずれを減らすための skill である。現時点では React + Storybook 系を対象とする。

## 役割分担

- `workflow.md`: stack 非依存の進め方
- `variants/`: stack 依存の生成ルール
- `presets/`: project 固有設定
- `assets/`: 実装ハンドオフ template

## 使い分け

### preset で吸収するもの

- パス
- デザイントークン
- コーディング規約
- 起動コマンド
- 既存コンポーネント参照方法

## 同梱している preset

- `presets/react-storybook/ec-frontend/project-config.md`

これは React + Storybook 系 preset の具体例であり、project 固有例として扱う。

## 新しい project を追加する手順

1. `presets/react-storybook/_template.md` を元に `project-config.md` を作る
2. preview 方式や禁止パターンを project に合わせて補強する
3. 既存の React/Storybook ルールで吸収できない差分がある場合は guide を更新する

## 今後の拡張方針

- React + Storybook 系 project は preset を増やして対応する
- 別 stack が必要になった時点で variant を追加する
- 1 skill パッケージとしての入口は `ui-prototyping` のまま保つ
