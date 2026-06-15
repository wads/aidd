# [ADR-0001] Claude Code と Codex 向けに skill 配置を `.agents/skills/` へ再編する

## Title

Claude Code と Codex 向けに skill 配置を `.agents/skills/` へ再編する

## Status

Proposed

## Context

このリポジトリの skill は現在 `skills/*.md` に平置きされており、各ファイルが skill 本文の source of truth になっている。
この構成は一覧性は高い一方で、以下の課題がある。

- skill 本文が長くなりやすく、エージェントが読む入口と詳細手順が混在している
- 関連する補助資料やテンプレートが `docs/` や `shared/templates/` に分散し、skill ごとの文脈が追いにくい
- `Claude Code` の slash command 前提で書かれた記述が多く、`Codex` の skill 構造と一致していない
- `Cursor` も含めた互換性を意識した説明が README に混在しており、実際の運用方針が曖昧になっている
- `mcp__claude_ai_...` や `browser_*` のようなツール固有名が skill 本文に現れ、再利用性を下げている

今回の整理では、対象を `Claude Code` と `Codex` に絞る。`Cursor` 対応は行わない。
また、これらの skill はまだ本格運用前であり、既存構成との後方互換性や段階移行は必須ではない。
そのため、Breaking change を許容して構成を整理できる。

## Decision

このリポジトリの skill の source of truth を `skills/` から `.agents/skills/` へ移す。

各 skill は 1 ファイルではなく 1 ディレクトリとして管理し、`SKILL.md` を薄い入口として扱う。
`SKILL.md` には以下のみを残す。

- skill の目的
- いつ使うか
- 想定入力
- 想定出力
- 必要に応じて読む補助ファイル

詳細手順、チェックリスト、例、補助資料、skill 専用テンプレートは同じディレクトリ配下にコロケートする。

再編時の設計方針は以下とする。

- `Codex` では `.agents/skills/` をそのまま利用する
- `Claude Code` では `.agents/skills/` の内容を実体とし、必要に応じて薄い command wrapper を別途用意する
- `Cursor` 向けの構成や説明は削除する
- 後方互換のための旧 `skills/*.md` 併存は行わない
- 複数の関連 skill は、人間が覚えやすい粒度に統合する

初回の再編対象は以下を優先する。

- `dev`
- `review` (`review-branch` と `review-pr-comments` を統合)
- `ui-migration`
- `product-intent`

`tdd-cycle`、`multi-agent-discussion`、`retrospective` も最終的には `.agents/skills/` 配下に置くが、構造は簡潔に保つ。

## Trade-offs

### Pros

- `Codex` の公式な skill 構造に沿った配置になり、運用方針が明確になる
- `Claude Code` と `Codex` の両方で、skill の実体を同じ場所に集約できる
- `SKILL.md` を薄くし、詳細を分離することで段階的開示と相性が良くなる
- 補助文書やテンプレートが skill ごとに集まり、人間にとっても探索しやすくなる
- `review` や `ui-migration` のような複雑な workflow を、覚えやすい単位で整理できる
- 後方互換を考慮しないため、中途半端な二重構成を避けられる

### Cons

- 既存の `skills/*.md` を参照している前提はすべて壊れる
- ファイルやディレクトリ構造が大きく変わるため、短期的な学習コストが発生する
- `Claude Code` では wrapper の作り方を別途整理する必要がある
- skill をディレクトリ化しすぎると、軽量な skill まで重く見えるリスクがある
- `SKILL.md` を薄くしすぎると、trigger 情報が不足する可能性があるため設計の節度が必要になる

## Impact

### 影響コンポーネント

- `skills/` 配下の全 skill 定義
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `shared/templates/` のうち skill 専用テンプレート
- `docs/` のうち skill 固有の手順説明

### API / インターフェース

- repo 内の skill 呼び出し単位が `skills/*.md` から `.agents/skills/<name>/SKILL.md` に変わる
- `review-branch` と `review-pr-comments` は `review` に統合される可能性がある
- 旧チケット作成 skill は `product-intent` など、役割に沿った skill 名に再編される可能性がある

### 運用

- `Codex` は `.agents/skills/` を前提とした運用へ切り替える
- `Claude Code` は `.agents/skills/` を実体として参照する wrapper 構成へ切り替える
- `Cursor` を対象外とするため、README や導入手順から Cursor 向けの説明を削除する

### 移行

- Breaking change を許容し、一括で新構成へ切り替える
- 旧 `skills/` との互換レイヤーは作らない
- skill 専用資料は新ディレクトリへ移し、`docs/` には横断文書を残す

### テスト観点

- `AGENTS.md` と `CLAUDE.md` から新しい skill 配置が参照しやすいこと
- `Codex` が `.agents/skills/` の skill を認識できること
- `Claude Code` の wrapper から想定 skill へ到達できること
- 各 `SKILL.md` が短い入口として成立し、補助ファイル参照で workflow を完結できること
- 既存の壊れた参照が残っていないこと

## Links

- 関連テンプレート: `shared/templates/adr-template.md`
- 関連実例: `shared/templates/adr-example-0000-use-adr.md`
- 関連文書: `docs/codex-research-results.md`
- 関連文書: `docs/claude-research-results.md`
- 関連文書: `README.md`
- 関連ルール: `shared/rules/common.md`

## 議論ログ

- 2026-04-07 Human + Codex: skill を `Claude Code` と `Codex` に最適化する方針を議論
- 2026-04-07 Human + Codex: `Cursor` 対応は不要、後方互換も不要、Breaking change 許容でよいと整理
- 2026-04-07 Human + Codex: `skills/` 平置きから `.agents/skills/` を source of truth にする案を ADR 化
