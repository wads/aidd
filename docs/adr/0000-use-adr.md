# [ADR-0000] Use Architecture Decision Records

## Status

Accepted

## Context

AI駆動IT開発において、技術的な意思決定の経緯と理由を記録・追跡する必要がある。
複数Agentが議論して決定を行うため、その過程を透明に保つことが重要。

## Decision Drivers

- 意思決定の透明性と追跡可能性
- 複数Agent間の議論結果の記録
- 将来の意思決定者（人間・AI）への知識伝達

## Considered Options

### Option 1: ADR (Architecture Decision Records)
- Description: MADR形式で技術決定を個別ファイルに記録
- Pros: 標準的、検索しやすい、差分管理可能
- Cons: ファイル数が増える

### Option 2: Decision log in single file
- Description: 1つのファイルに全決定を記録
- Pros: シンプル
- Cons: 大きくなると管理困難、並行編集しにくい

## Decision

ADR (Architecture Decision Records) を MADR 形式で採用する。

## Rationale

- 各決定が独立したファイルとして管理され、git diff で変更追跡が容易
- Agent間の議論ログをDiscussion Logセクションに記録できる
- 業界標準であり、人間開発者にも馴染みやすい

## Consequences

### Positive
- 意思決定の経緯が明確に記録される
- 後からの振り返りや再検討が容易

### Negative
- ADR作成のオーバーヘッドが発生する（ただしテンプレートで軽減）

## Discussion Log

- 2026-03-05 Initial: ADR採用を決定。MADR形式をベースとし、Discussion Logセクションを追加。
