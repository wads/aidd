---
type: design
scope: all
status: accepted
updated: 2026-09-05
---

# 設計書: stacked PR 運用の責務配置

- Status: Accepted（2026-09-04 人間承認。P5 軽量ゲート・P7 ゲートの指摘反映を随時追記）
- Updated: 2026-09-05
- Date: 2026-09-04
- 関連: [ADR-0007](../adr/0007-adopt-github-native-stacked-prs.md)（ADR-0003 を置き換え。機構を gh stack へ）、[ADR-0006](../adr/0006-always-regate-after-restack.md)（ADR-0004 を置き換え）、[ADR-0003](../adr/0003-stacked-pr-with-native-git.md)、[ADR-0004](../adr/0004-diff-unchanged-by-changed-lines.md)、[ADR-0005](../adr/0005-draft-guard-for-merge-order.md)、Issue #18（P2 確定版 AC/QC）

## 目的

stacked PR（積み上げ式 PR）運用の規則・手順を、どの skill がどの責務で持つかを契約として定義する。手順の本体を 1 箇所に集約し（単一の正）、各フェーズ skill には薄い参照だけを置く。

## 非目的

- 手順の本文（コマンド・判定基準の詳細）。それは P6 で書く新 skill `stacked-pr` の内容
- orchestrator への統合（従来どおり移行期間は `dev` が入口）

## 責務配置

機構（ブランチ管理・PR 作成・積み替え・base 付け替え・マージ順序の強制・構成変更）は **GitHub ネイティブ機能 `gh stack` が持つ**（ADR-0007）。aidd の skill はプロセスの規則だけを持つ。

| 担い手 | 責務 | 対応 AC |
|---|---|---|
| **`gh stack`（GitHub 公式）** | ブランチ管理、PR 作成・更新、積み替え（カスケードリベース）、マージ後の base 自動再ターゲット、マージ順序の強制（指定 PR とその下を all-or-nothing でマージ）、スタック構成の変更 | AC-2, 5, 8 の機構部分 |
| **stacked-pr（aidd）** | プロセスの規則: 適用条件、ステップ完了の定義と PR 作成タイミング、先行着手と中断、積み替え後の失効と再ゲート（ADR-0006）、コンフリクト境界（自明 = AI / 判断あり = 人間）、チェック依頼の形、環境要件（gh 2.90+ と拡張。満たせなければスタックを使わない） | AC-2, 3, 5, 6, 8, 9 / QC-1, 3 |
| implementation-plan | 複数ステップ計画の承認時にスタック構成（ステップ = 1 PR の境界・順序）を対話で確定。計画全体を Issue コメントへ、各 PR の説明は自ステップ分 | AC-1 |
| tdd-cycle / dev（自動進行） | ステップ完了（TDD = テスト green / DIRECT = 検証手順完了）で次の層を積む。下位 PR への指摘が設計判断（P3/P4 再入）を要するときは先行積みを中断 | AC-2, 3 |
| critical-gate | 適用単位 = PR の差分ごと。積み替えをした PR は常に再ゲート（免除の判定は持たない。ADR-0006） | AC-4, 9 |
| review | P7 各節の PR 単位への適用（下位 PR / 最終 PR の分担）、最終 PR マージ前の全 AC⇄テスト横断確認と前方修正の受け皿 | AC-4, 7, 10 |

### P7 レビュー一式のスタック時の分担

- **各 PR で実施（その PR のマージ前）**: critical-gate（PR 差分）+ 人間チェック（**自ステップ分の AC 受入れ検証**と**差分範囲の整合確認**を含む）+ マージ直前の契約チェック。PR 説明の AC⇄テスト対応表は自ステップ分のみを持ち、最終 PR 集約対象のセクションは「最終 PR で実施」と参照記載する
- **最終 PR で追加実施**: context-snapshot、短期コンテキストの昇格判定、全 AC⇄テスト対応表の集約と横断確認（AC-10）

## フロー（どのフェーズでどの操作が走るか)

1. **P5**: 計画承認 → スタック構成確定 → 計画全体を Issue コメント → `gh stack init` + `submit` で最初の PR
2. **P6（ステップごとの繰り返し）**: 実装 → ステップ完了 → `gh stack add` + `submit` → PR 差分の critical-gate → 人間チェック依頼 → 待たずに次ステップへ着手
3. **随時（下位に指摘対応）**: `gh stack down` → 修正 → `gh stack rebase --upstack` → `gh stack push` → 積み替えた全 PR のゲート・チェック済みを失効させ、そのステップの検証を再実行（再ゲートは次にチェックへ出す直前）
4. **随時（チェック済みのマージ）**: `gh pr ready` → `gh stack merge`（指定 PR とその下をアトミックにマージ）→ 上位 PR は自動で base へ再ターゲットされる
5. **最終 PR**: 全 PR の AC⇄テスト対応表を集約し、マージ前に Issue 全 AC⇄テストの横断確認。漏れはマージ済み分を含め追加修正 PR（前方修正）。context-snapshot・昇格判定もここで実施

## 例外・境界

- スタック運用の適用条件は「P5 実装計画を実施するルート（feature / refactoring）で、ステップが 2 つ以上あり、各ステップが独立にレビュー・マージできる」こと（`dev/routes.md`・`implementation-plan/workflow.md` §3）。P5 を通らないルート（chore / hotfix / spike）と bugfix の簡易計画は、ステップ数によらず従来どおり 1 PR
- スタックにしない Issue では `stacked-pr` への参照も発生しない
- 積み替え未完了の上位 PR は人間チェックに出さない（AC-5）
- コンフリクトの「自明 / 判断あり」境界と設計判断指摘の判定目安は `stacked-pr` 本文で具体化（P2 持ち越し事項）

## 守るべき振る舞い

- 既存の 1 PR フロー（bugfix / chore 等）の記述・動作を変えない（QC-2）
- 「ゲート通過後に人間チェック」の順序を PR 単位でも維持する（aidd 不変条件）
