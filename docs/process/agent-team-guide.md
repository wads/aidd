# Agent Team Guide

カスタムAgentの運用ガイド。

## Agent Roster

| Agent | Role | Description |
|-------|------|-------------|
| researcher | 調査・情報収集 | コードベース調査、技術調査、設計支援 |
| developer | TDD実装 | テスト作成、実装、設計書作成 |
| reviewer | レビュー・品質 | コードレビュー、品質チェック、議論進行 |

## Usage Patterns

### Investigation (調査)
researcher x2 で並行調査 -> 結果をSendMessageで共有 -> 合意形成

### Implementation (実装)
developer が TDD で実装 -> reviewer がレビュー -> フィードバック反映

### Discussion (議論)
researcher + reviewer が議論 -> 合意またはエスカレーション

## Communication Protocol

- Agent間のコミュニケーションは `SendMessage` を使用
- メッセージには必ず「目的」「調査結果/意見」「提案」を含める
- 合意できない場合は理由を明示して人間にエスカレーション

## Adding New Agents

必要に応じて以下のAgentを追加可能:
- **architect**: システム全体のアーキテクチャ設計
- **facilitator**: 議論のファシリテーション、合意形成の支援

追加手順:
1. `.claude/agents/<agent-name>.md` にAgent定義を作成
2. このガイドのAgent Rosterに追記
3. CLAUDE.mdの参照を更新
