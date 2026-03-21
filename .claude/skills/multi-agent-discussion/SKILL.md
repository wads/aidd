---
name: multi-agent-discussion
description: 複数Agentによる並行独立調査スキル。偏りのない多角的分析を行い、人間の意思決定を支援する。
user-invocable: true
---

# Multi-Agent Research

複数Agentによる並行独立調査スキル。偏りのない多角的分析を行い、人間の意思決定を支援する。

## Arguments

- topic: 調査テーマ（必須）
- perspectives: 分割軸のヒント（省略時: Claude Codeがテーマに応じて自動決定）
- goal: 期待するアウトプット（省略時: 選択肢の整理と推奨案の提示）

## Process

1. **Theme Analysis (テーマ分析)**
   - テーマの性質を分析し、適切な分割軸を決定する
   - 分割軸の例: バックエンド/フロントエンド、UI/アプリケーション/データ、技術A/技術B等
   - 各軸に対して2名以上のAgentを割り当てる（同じ調査を独立に実施させるため）
   - 分割軸とAgent構成を人間に提示して確認

2. **Parallel Research (並行調査)**
   - 各Agentが独立に並行して調査を実施
   - Agent間の情報共有は行わない（独立性の確保）
   - 各Agentは調査結果を構造化して報告

3. **Synthesis (統合)**
   - 各Agentの調査結果を突き合わせる
   - 共通点: 複数Agentが同じ結論に至った事項
   - 差分: Agentごとに異なる発見や見解
   - 選択肢を整理し、各選択肢のPros/Consを明示

4. **Present to Human (人間への提示)**
   - 整理された選択肢と推奨案を人間に提示
   - 最終判断は常に人間が行う

5. **Record (記録)**
   - 調査結果と人間の決定を `tasks/decisions-log.md` に記録
   - アーキテクチャに関わる決定は `docs/adr/` にADRを作成

## Output Format

```markdown
## Research: [topic]
- Date: [YYYY-MM-DD]
- Perspectives: [分割軸]
- Agents: [Agent数と割り当て]

### Findings
#### Common (全Agentで共通)
[共通の発見事項]

#### Divergent (Agentごとの差分)
[異なる発見や見解]

### Options
[選択肢の整理とPros/Cons]

### Recommendation
[推奨案と根拠]

### Human Decision
[人間の判断を記録]
```
