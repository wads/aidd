# Development Workflow

AI駆動IT開発の全体フロー定義。

## Process Flow

```
[1.要求確認] --> 人間承認 --> [2.要件定義] --> 人間承認 --> [3.ADR作成]
    --> 人間承認 --> [4.詳細設計] --> 人間承認 --> [5.worktree作成]
    --> [6.TDD実装] --> 人間確認 --> [7.振り返り]
```

## Phase Details

### 1. 要求確認 (Requirements Confirmation)
- ユーザーからの要求をresearcherが調査・整理
- `/multi-agent-discussion` で複数Agentが要求を分析
- `docs/requirements/` に要求定義を作成
- **人間チェックポイント**: 要求内容の承認

### 2. 要件定義 (Specification)
- 要求を具体的な要件に分解
- researcher + developer で実現可能性を議論
- `docs/specifications/` に要件定義を作成
- **人間チェックポイント**: 要件の承認

### 3. ADR作成 (Architecture Decision Record)
- 技術的な意思決定を記録
- `/multi-agent-discussion` で選択肢を議論
- `docs/adr/` にADRを作成
- **人間チェックポイント**: 技術決定の承認

### 4. 詳細設計 (Detailed Design)
- 実装方針をdeveloperが設計
- reviewerがレビュー
- `docs/designs/` に設計書を作成
- **人間チェックポイント**: 設計の承認

### 5. Worktree作成
- `/worktree-setup` でgit worktree + topic branchを作成
- 実装用の隔離された作業環境を準備

### 6. TDD実装
- `/tdd-cycle` でRed-Green-Refactorサイクルを実行
- developerが実装、reviewerがレビュー
- **人間チェックポイント**: 実装結果の確認

### 7. 振り返り
- `/retrospective` でKPT振り返りを実施
- `tasks/retrospectives/` に記録
- 教訓を `tasks/lessons.md` に蓄積

## Principles

- 各フェーズはplan modeで計画 -> 人間合意後に実施
- 調査・議論は常に複数Agent（researcher x2等）で実施
- 合意/多数決で結論、合意不可時は人間にエスカレーション
- 小さく・段階的に進める（30行以下の変更を基本単位とする）
