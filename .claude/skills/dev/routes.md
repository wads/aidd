# タイプ別ルート

Issue の `type-*` ラベルから実施フェーズを決める。詳細な契約は `docs/design/0001-dev-phase-decomposition.md` を正とする。

| フェーズ（skill） | feature | bugfix | refactoring | chore | spike |
|---|---|---|---|---|---|
| P1 着手（workspace-hygiene + 本 skill） | ✓ | ✓ | ✓ | ✓ | ✓ |
| P2 要求整理（requirements） | ✓ | ✓（再現条件・回帰範囲） | ✓（不変条件・対象範囲） | 簡易 | ✓（問いの定義） |
| P2.5 プロトタイピング（ui-prototyping） | UI 変更時 | − | − | − | − |
| P3 技術判断（adr） | 判断駆動 | 判断駆動（稀） | 判断駆動 | − | 結論を ADR 化しうる |
| P4 設計（design-docs） | 判断駆動 | − | 判断駆動 | − | − |
| P5 実装計画（implementation-plan） | ✓ | 簡易（PR 説明 1 段落） | ✓ | − | − |
| P6 実装（tdd-cycle） | ✓ | ✓（再現テスト先行） | ✓（既存テスト green 維持） | ✓ | 使い捨てコード可（マージしない） |
| P7 批判的ゲート（critical-gate、人間レビュー前） | フル版（4視点） | 軽量版（2視点） | フル版（4視点） | 契約チェックのみ | 対象外 |
| P7 検証・レビュー（review + context-snapshot） | ✓ | ✓ | ✓ | 簡易（`context-snapshot` は任意） | 報告のレビュー |
| P8 振り返り（retrospective） | 推奨 | 任意 | 任意 | − | 必須 |

- `critical-gate` は P2 要求整理の確定前・P5 承認前にも軽量版を挟む（feature / refactoring は推奨、bugfix / spike は任意、chore / hotfix は実施しない）。深さの定義は `critical-gate/workflow.md` §0・§0.5 を正とする
- **ルート提示には `critical-gate` の行も含める**。表に無いゲートは合意された計画に入らず、そのまま実行されずに終わる
- hotfix は bugfix の緊急変形: P6・P7 の最小構成で先に直し、事後に P8 振り返りと記録（Intent Delta、必要なら ADR）を必須にする。Issue の事後作成を許容する
- 「判断駆動」= フェーズには入るが、成果物（ADR・設計書）は書くべき判断が生じたときだけ作る
- chore の `context-snapshot` は任意。設定 1 行の変更に 1 枚のビューを起こすのは、人間から見た読む量に見合わない。ただし **本番環境へ変更を加える chore** では、規模ではなく影響範囲を基準に生成を検討する
- draft PR は通常 P5 実装計画（implementation-plan）で作成するが、P5 実装計画を実施しない chore では `tdd-cycle` が P6 実装の開始時に作成する（`tdd-cycle/workflow.md` §4）
- **stacked PR（ステップ = 1 PR）は P5 実装計画を実施するルート（feature / refactoring）で、各ステップが独立にレビュー・マージできる場合に使う**。P5 を通らないルート（chore / hotfix / spike）と bugfix の簡易計画は、ステップ数によらず従来どおり 1 PR。P5 で作るのは最下段の PR だけで、step2 以降は P6 実装で各ステップ完了時に作成する。P7 のゲート・人間チェック・マージは PR 単位で回り、Issue 全体の受入れ確認は最終 PR のマージ前に行う（手順は `stacked-pr`、責務配置は `docs/design/0002-stacked-pr-responsibilities.md`）
- タイプが混在するIssue は分割を提案する。分割できなければ feature のルートに乗せる
