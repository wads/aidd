# Tutorial: AIDD で開発を始める

Claude Code を起動した後の具体的な進め方を、ステップバイステップで説明します。

## 前提

- プロジェクトへの playbook 導入が完了していること（[README の導入手順](../README.md#導入) を参照）
- CLAUDE.md に Project Configuration（Test command 等）が設定済みであること
- 着手したい Jira チケットがあること（なければ `/product-intent` で作る）

## Step 0: チケットを作る — `/product-intent`

開発はチケットから始まります。`/product-intent` が要求をタイプ別テンプレートで構造化し、`type-*` ラベルつきの Jira チケットを作ります。

```
> /product-intent 検索画面で表示が崩れているのを直したい
```

タイプ（feature / bugfix / hotfix / refactoring / chore / spike）はここで確定します。bugfix や chore などエンジニア起点のチケットは軽量テンプレートで数分で作れます。

## Step 1: 着手する — `/dev`

```
> /dev ECS-12345
```

`/dev` はチケットの `type-*` ラベルからルート（実施フェーズ構成）を提示します。あなたがルートを承認すると、フェーズが順に進みます。

タイプごとのルートの目安:

| タイプ | 流れ |
|---|---|
| feature | 要求整理 →（UI 変更なら プロトタイピング）→ 必要なら ADR・設計 → 実装計画 → TDD 実装 → 検証・レビュー |
| bugfix | 再現条件の確定 → 再現テスト先行の TDD 実装 → 検証・レビュー |
| refactoring | 不変条件の確定 → 実装計画 → 既存テスト green を維持して実装 → 検証・レビュー |
| chore | 簡易確認 → 実施 → CI green 確認 |
| spike | 問いの定義 → 調査（コードはマージしない）→ 報告・ADR 化 → 振り返り |

## Step 2: 完了とは何かを決める（P2 要求整理）

`requirements` skill が受入れ条件（AC）と品質条件（QC）を ID つきで確定します。

**あなたがやること:**
- 曖昧な点への質問に答える
- 🟡・🔴（推定・要確認）マーカーの項目を確認して確定させる
- 確定版を承認する（Jira コメントに残ります）

## Step 3: TDD で実装（P6）

`tdd-cycle` skill が Red → Green → Refactor を繰り返し、各テストを AC-ID に対応付けます。

**あなたがやること:**
- 確認ポイントで結果を確認して次に進む
- 計画から外れる事態（スコープ変更・想定外）が起きたら AI が止まるので、判断する

## Step 4: 検証・レビューとマージ（P7）

`review` skill が self-review と AC ごとの受入れ検証を行い、`context-snapshot` がチケットの意図と検証状態を 1 枚の HTML にまとめて Jira に添付します。

**あなたがやること:**
- スナップショットと PR を見て受入れを判断する
- 短期コンテキストの昇格提案（ADR・設計書へ残すべき判断）を承認する
- マージする

## Step 5: 振り返り（P8）

```
> /retrospective
```

KPT で振り返り、playbook への改善提案が出ます。採用したものはこの playbook への PR になります。

## 技術的な議論が必要なとき

開発中に判断に迷ったら、いつでも `/multi-agent-discussion` で調査できます。

```
> /multi-agent-discussion エラーハンドリングの方針。独自エラー型を定義すべきか、標準のエラーで十分か。
```

複数のエージェントが独立に並行調査し、結果を突き合わせて選択肢を整理してくれます。最終判断はあなたが行います。

## 現行構成メモ

現在の source of truth は `skills/` ではなく `.agents/skills/` です。
Claude Code では `.claude/commands/` の command から `.agents/skills/<name>/SKILL.md` を参照します。

主な skill 名:

- `/product-intent`
- `/dev`
- `/requirements`
- `/adr`
- `/design-docs`
- `/implementation-plan`
- `/tdd-cycle`
- `/review`
- `/context-snapshot`
- `/retrospective`
- `/multi-agent-discussion`
- `/daily-sentry-check`
- `/ui-migration`

## Tips

### Skill を使わない自由な開発もOK

Skill はあくまでガイドです。慣れてきたら Skill を使わずに直接指示してもかまいません。

```
> この関数にバリデーションを追加して。テストも書いて。
```

### ドキュメントは「書くべき判断が生じたとき」だけ

ADR・設計書はフェーズに来たから書くものではありません。選択肢のある判断や「守るべき振る舞い」が生まれたときだけ書きます。書かない判断も正当です。

### プロセスの詳細

フェーズ・ゲート・コンテキストの置き場の全体像は [docs/design/0001-dev-phase-decomposition.md](design/0001-dev-phase-decomposition.md) を参照してください。
