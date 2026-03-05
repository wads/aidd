# Multi-Agent Discussion

複数Agentによる調査・議論・合意形成スキル。

## Usage

User-invocable: `/multi-agent-discussion`

## Arguments

- topic: 議論のテーマ（必須）
- agents: 参加Agent名のリスト（省略時: researcher x2）
- goal: 期待するアウトプット（省略時: 合意された結論）

## Process

1. **Preparation (準備)**
   - 議論テーマと目標を確認
   - 参加Agentを決定

2. **Research (調査)**
   - 各researcherが独立して調査を実施
   - 調査結果をSendMessageで共有

3. **Discussion (議論)**
   - 各Agentが意見を表明
   - 相違点を明確化
   - 代替案を検討

4. **Consensus (合意形成)**
   - 合意できた場合: 結論をまとめる
   - 合意できない場合: 対立点を整理して人間にエスカレーション

5. **Record (記録)**
   - 議論結果を `tasks/decisions-log.md` に記録
   - 必要に応じてADRを作成

## Output Format

```markdown
## Discussion: [topic]
- Date: [YYYY-MM-DD]
- Participants: [agent list]
- Result: [Consensus | Escalated]

### Summary
[議論の要約]

### Decision
[合意された結論、またはエスカレーション理由]

### Action Items
- [action 1]
```
