---
type: adr
scope: all
status: accepted
updated: 2026-06-15
---

# [ADR-0002] aidd 汎用テンプレートへの適応

## ステータス

承認済み（ADR-0001 の `.agents/skills/` 配置をこのテンプレートの範囲で置き換える）

## 背景

本リポジトリは、別リポジトリの AIDD playbook バンドルを出発点に、特定組織・特定ツールに依存しない**汎用の AIDD テンプレート**として再構成したものである。出発点のバンドルは Jira 前提・`.agents/skills/`（Codex/Cursor 併用）配置・組織固有 skill を含んでいた。汎用テンプレートとして使うにあたり、以下の判断が必要になった。

- skill の配置機構（Claude Code ネイティブ vs `.agents/skills/` + command wrapper）
- Issue トラッカー（Jira vs GitHub Issue）
- 長期記録（ADR・設計書・要求）の置き場所・形式の決め方
- 取り込む skill の範囲

## 検討した選択肢

### 案1: バンドルを忠実踏襲（`.agents/skills/` + Jira + 固定 docs/）

- メリット: 出典との差分が最小
- デメリット: Claude Code がネイティブ skill として自動認識しない。Jira 非利用環境で動かない。コンテキストハブを持つプロジェクト（例 remosys-context）と二重管理になる

### 案2: Claude Code ネイティブ + GitHub Issue + ハブ追従 Binding（採用）

- 概要: skill 本文を `.claude/skills/` に集約しネイティブ起動。Issue は GitHub Issue。長期記録の置き場所はプロジェクト単位の単一 Binding で決める
- メリット: そのまま `/dev` 等で起動できる。Jira 不要。コンテキストハブの規約と整合し二重管理を避けられる。汎用
- デメリット: 出典の `.agents/skills/`・Jira 記述からの書き換えが必要

## 決定内容

案2 を採用する。

- **skill 配置**: `.claude/skills/<name>/SKILL.md`（`user-invocable: true`）を source of truth とする。`.agents/skills/` と `.claude/commands/` wrapper は使わない
- **Issue トラッカー**: GitHub Issue。タイプは GitHub ラベル `type-*`。ブランチは `feature/issue-{番号}-short-desc`
- **記録の Binding**: 長期記録と Issue の置き場所はプロジェクトの `CLAUDE.md` で一度だけ宣言（`records_root` / `issue_repo` / `service`）。全フェーズがこの宣言だけに従い、フェーズごとの規約混在を禁止する。宣言が無ければ standalone（`docs/`・自 repo）
- **記録形式**: ADR・設計書に frontmatter（`type` / `scope` / `status` / `updated`）を付与し、連番 4 桁 0 埋め。`service` 指定時は `services/{service}/`、横断は `system/` に分割（コンテキストハブ規約と整合）
- **取り込む skill の範囲**: コアプロセス（product-intent / dev / requirements / adr / design-docs / implementation-plan / tdd-cycle / review / context-snapshot / retrospective / multi-agent-discussion / workspace-hygiene）+ ui-prototyping。組織固有の daily-sentry-check・ui-migration は除外

## 設計意図

Claude Code 単体で即起動でき、かつ Jira 等の特定 SaaS に縛られない汎用テンプレートにする。コンテキストハブ（要求・設計・ADR・Issue を一元管理するリポジトリ）を持つプロジェクトでは、ハブの規約に records を流すことで「正本は 1 箇所・二重管理しない」を守る。承認ゲートは人間によるコンテンツ承認であり、記録の置き場所やトラッカー種別に依存しないため、standalone でもハブでも同一に機能する。

## トレードオフ

- 出典バンドルからの差分が大きくなる。出典の設計記録（ADR-0001・`docs/design/skills-restructure.md`）は歴史的経緯として残すが、`.agents/skills/` 配置という結論は本テンプレートでは本 ADR が置き換える
- Codex/Cursor 併用は当面 `AGENTS.md` から `.claude/skills/` を参照する形にとどめ、専用配置は持たない

## 影響範囲

- `.claude/skills/`（全 skill 本文）
- `shared/rules/common.md`（Binding 規約）・`CLAUDE.md`（Binding 宣言）
- `shared/templates/adr-template.md`（frontmatter 追加）
- `docs/`（設計・マニュアル・チュートリアルの記述）

## 議論ログ

- 2026-06-15 Human + AI: バンドル再現方針を協議。汎用性・全フェーズ一貫（規約混在禁止）・承認ゲート維持を条件にハブ追従 Binding を採用。ui-prototyping の React/Next preset は別 Issue で後追い。
