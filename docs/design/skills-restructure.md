# Skill 再編設計

> **注（aidd テンプレート）**: この文書は出典 playbook の `.agents/skills/` 再編設計を歴史的経緯として残している。本テンプレートの実際の配置は `.claude/skills/`（Claude Code ネイティブ）であり、その判断は [ADR-0002](../adr/0002-adapt-as-aidd-template.md) を参照。

この文書は、`Claude Code` と `Codex` 向けの skill 再編を実装するための設計ドキュメントである。
意思決定の背景、採否、トレードオフは ADR を参照すること。

- ADR: [ADR-0001 Claude Code と Codex 向けに skill 配置を `.agents/skills/` へ再編する](../adr/0001-restructure-skills-for-codex-and-claude.md)

## この文書の目的

実装時に AI が迷わないよう、以下を明確にする。

- 新しいディレクトリ構成
- skill ごとの責務分割
- `SKILL.md` と補助文書の役割分担
- `Claude Code` と `Codex` の接続方法
- どの順で再編するか
- 実装時に守るべき設計ルール

## 非目的

以下はこの文書では扱わない。

- 再編方針の是非の再議論
  参照: [ADR-0001](../adr/0001-restructure-skills-for-codex-and-claude.md)
- `Cursor` 対応
  参照: [ADR-0001](../adr/0001-restructure-skills-for-codex-and-claude.md)
- 後方互換レイヤーの維持
  参照: [ADR-0001](../adr/0001-restructure-skills-for-codex-and-claude.md)

## 実装前提

- source of truth は `.agents/skills/` とする
- 既存 `skills/` は最終的に削除対象とする
- skill は「1ファイル」ではなく「1ディレクトリ」で管理する
- `SKILL.md` は薄い入口であり、詳細手順は同階層ファイルに分離する
- skill 固有テンプレートや補助資料は、可能な限り skill ディレクトリ配下に寄せる
- 共通ルールと truly shared なテンプレートのみ `shared/` に残す

## 目標状態

### ルート構成

```text
.agents/
  skills/
    dev/
      SKILL.md
      modes.md
      adr.md
      escalation.md
      examples.md

    review/
      SKILL.md
      branch.md
      pr-comments.md
      checklist.md
      output-format.md

    product-intent/
      SKILL.md
      workflow.md
      checklist.md
      examples.md

    ui-migration/
      SKILL.md
      workflow.md
      extract-rules.md
      extract-tracking.md
      transform.md
      verify.md
      assets/
        migration-config.template.md
        migration-rules.template.md
        tracking-map.template.md

    tdd-cycle/
      SKILL.md
      workflow.md
      examples.md

    multi-agent-discussion/
      SKILL.md
      workflow.md
      examples.md

    retrospective/
      SKILL.md
      workflow.md

.claude/
  commands/
    dev.md
    review.md
    product-intent.md
    ui-migration.md
    tdd-cycle.md
    multi-agent-discussion.md
    retrospective.md

shared/
  rules/
    common.md
  templates/
    adr-template.md
    adr-example-0000-use-adr.md

docs/
  adr/
  design/
  tutorial.md
  claude-research-results.md
  codex-research-results.md
  dlc-skill-expansion-plan.md
```

### skill 単位の考え方

- `dev`: AIDD の入口。モード分岐、ADR、エスカレーションを束ねる
- `review`: 変更レビュー系を集約する
- `product-intent`: PdM の要求を Product Intent として整理し、GitHub Issueへ落とす workflow を管理する
- `ui-migration`: UI 移行系の workflow 群を一つの skill パッケージにまとめる
- `tdd-cycle`: 軽量 skill。詳細は少数ファイルに分割する
- `multi-agent-discussion`: 軽量 skill。実行パターンと例を持つ
- `retrospective`: 最小構成で保持する

## skill 設計ルール

### 1. `SKILL.md` は薄い入口にする

各 `SKILL.md` に含める内容は原則として以下のみとする。

- `name`
- `description`
- 何をする skill か
- いつ使うか
- 想定入力
- 想定出力
- 読むべき補助ファイル一覧

`SKILL.md` に長大な手順、詳細なチェックリスト、長いサンプル、テンプレート本文を直接書かない。

### 2. 詳細はファイル名で役割が分かるように分離する

分離先のファイル名は人間にとって予測可能であることを優先する。

- `workflow.md`: 手順の本体
- `modes.md`: モード分岐や条件
- `checklist.md`: 確認項目
- `examples.md`: 入出力例、プロンプト例
- `output-format.md`: 出力構造
- `adr.md`: ADR の書き方、参照方針
- `escalation.md`: 人間に確認すべき条件
- `assets/`: skill 固有テンプレート

### 3. tool 固有名は core から抽象化する

`mcp__claude_ai_...`、`browser_*` のような実装固有名は、core の workflow からは外す。
必要な場合は以下のような抽象表現へ置き換える。

- GitHub Issue 作成ツール
- ブラウザ自動操作ツール
- 設計モック参照ツール
- GitHub PR コメント取得ツール

具体的なツール名が必要な場合は、`Claude Code` wrapper か実行環境依存文脈に寄せる。

### 4. skill 固有資料は skill 配下へ寄せる

以下は原則として `.agents/skills/<skill>/` に移す。

- skill 専用のテンプレート
- skill 専用の手順書
- skill 専用の例
- skill 専用の補助文書

以下のみ `shared/` に残す。

- 全 skill 共通ルール
- 汎用 ADR テンプレート
- 汎用テンプレート

### 5. 人間が覚えやすい単位で統合する

統合方針は以下とする。

- `review-branch` と `review-pr-comments` は `review/` に統合
- 旧Issue 作成 skill は `product-intent/` に再編
- `ui-migration-*` は `ui-migration/` に統合

単一責務だが複雑性の低い skill は、ディレクトリ化してもファイル数を増やしすぎない。

## `Claude Code` と `Codex` の接続設計

### Codex

`Codex` では `.agents/skills/` をそのまま利用する。
そのため、`SKILL.md` の frontmatter と description は trigger 品質に直結する。

各 `SKILL.md` の description では以下を明示する。

- 何をするか
- いつ使うか
- どんな依頼に反応すべきか
- どんな依頼には反応しないか

### Claude Code

`Claude Code` では `.claude/commands/` に薄い wrapper を置く。
wrapper の役割は command 名と skill 入口をつなぐことだけに限定する。

wrapper に workflow 本文を重複記載しない。
実体は常に `.agents/skills/` 側とする。

想定例:

```text
@/path/to/repo/.agents/skills/dev/SKILL.md
```

必要に応じて wrapper 名は skill 名とそろえる。

## skill ごとのファイル責務

### `dev/`

`SKILL.md`
- skill の要約
- Lite / Standard / Full があること
- 補助ファイルの案内

`modes.md`
- モード選択基準
- モードごとの手順差分

`adr.md`
- ADR をいつ作るか
- どのテンプレートを参照するか

`escalation.md`
- 人間承認が必要な条件

`examples.md`
- プロンプト例
- モード指定例

### `review/`

`SKILL.md`
- 変更レビュー skill の入口
- branch review と PR comment review の両方があること

`branch.md`
- 旧 `review-branch` のレビュー観点

`pr-comments.md`
- 旧 `review-pr-comments` の取得・整理・出力方針

`checklist.md`
- 共通レビュー観点

`output-format.md`
- 報告フォーマット

### `product-intent/`

`SKILL.md`
- Product Intent 整理と GitHub Issue化 skill の入口

`workflow.md`
- ヒアリング、品質チェック、確認ループ、作成確認までの流れ

`checklist.md`
- Product Intent とIssue品質のチェック

`examples.md`
- ヒアリング、不足確認、Issue本文の例

### `ui-migration/`

`SKILL.md`
- UI 移行 skill 群の入口
- workflow / extract / transform / verify へ誘導

`workflow.md`
- 全体オーケストレーション

`extract-rules.md`
- UI 変換ルール抽出

`extract-tracking.md`
- 計測マッピング抽出

`transform.md`
- 変換と計測移植

`verify.md`
- UI 比較と計測検証

`assets/`
- config / rules / tracking map テンプレート

### 軽量 skill

`tdd-cycle/`
- `SKILL.md`, `workflow.md`, `examples.md`

`multi-agent-discussion/`
- `SKILL.md`, `workflow.md`, `examples.md`

`retrospective/`
- `SKILL.md`, `workflow.md`

## 文書の移設ルール

### `docs/` に残すもの

- チュートリアル
- 調査メモ
- ADR
- 横断的な設計文書

### `.agents/skills/` に移すもの

- skill 専用の詳細手順
- skill 専用テンプレート
- skill 専用の具体例
- skill 専用の補助ガイド

### `shared/` に残すもの

- どの skill からも参照される共通ルール
- skill 非依存のテンプレート

## 実装順序

### Phase 1

- `.agents/skills/` を作成
- `dev/` を新設
- `review/` を新設
- `.claude/commands/` の wrapper 方針を整える

### Phase 2

- `product-intent/` を新設
- `ui-migration/` を新設
- `shared/templates/` から skill 専用テンプレートを移す

### Phase 3

- `tdd-cycle/`
- `multi-agent-discussion/`
- `retrospective/`

### Phase 4

- `README.md` を全面更新
- `AGENTS.md` を新構成前提に更新
- `CLAUDE.md` を新構成前提に更新
- 旧 `skills/` を削除

## 実装時チェックリスト

- `.agents/skills/` が source of truth になっているか
- 各 `SKILL.md` が薄い入口として成立しているか
- 詳細が補助ファイルへ分離されているか
- `Claude Code` wrapper に本文重複がないか
- `Codex` が反応しやすい description になっているか
- skill 固有テンプレートが適切にコロケートされているか
- `docs/` に skill 固有手順が残りすぎていないか
- tool 固有名が core workflow に残っていないか

## Open Questions

- `Claude Code` wrapper をどこまで自動生成するか
- `ui-migration-guide.md` を横断ガイドとして残すか、skill 配下へ完全移設するか
- `review` skill の入口を単一 command に寄せるか、branch と PR comments を別 command に分けるか
