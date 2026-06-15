# タイプ別ルート

チケットの `type-*` ラベルから実施フェーズを決める。詳細な契約は `docs/design/0001-dev-phase-decomposition.md` を正とする。

| フェーズ（skill） | feature | bugfix | refactoring | chore | spike |
|---|---|---|---|---|---|
| P1 着手（workspace-hygiene + 本 skill） | ✓ | ✓ | ✓ | ✓ | ✓ |
| P2 要求整理（requirements） | ✓ | ✓（再現条件・回帰範囲） | ✓（不変条件・対象範囲） | 簡易 | ✓（問いの定義） |
| P2.5 プロトタイピング（ui-prototyping） | UI 変更時 | − | − | − | − |
| P3 技術判断（adr） | 判断駆動 | 判断駆動（稀） | 判断駆動 | − | 結論を ADR 化しうる |
| P4 設計（design-docs） | 判断駆動 | − | 判断駆動 | − | − |
| P5 実装計画（implementation-plan） | ✓ | 簡易（PR 説明 1 段落） | ✓ | − | − |
| P6 実装（tdd-cycle） | ✓ | ✓（再現テスト先行） | ✓（既存テスト green 維持） | ✓ | 使い捨てコード可（マージしない） |
| P7 検証・レビュー（review + context-snapshot） | ✓ | ✓ | ✓ | 簡易 | 報告のレビュー |
| P8 振り返り（retrospective） | 推奨 | 任意 | 任意 | − | 必須 |

- hotfix は bugfix の緊急変形: P6・P7 の最小構成で先に直し、事後に P8 と記録（Intent Delta、必要なら ADR）を必須にする。チケットの事後作成を許容する
- 「判断駆動」= フェーズには入るが、成果物（ADR・設計書）は書くべき判断が生じたときだけ作る
- タイプが混在するチケットは分割を提案する。分割できなければ feature のルートに乗せる
