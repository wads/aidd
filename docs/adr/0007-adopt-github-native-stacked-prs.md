---
type: adr
scope: all
status: accepted
updated: 2026-09-06
---

# [ADR-0007] stacked PR の機構を GitHub ネイティブ機能（gh stack）に委ねる

## ステータス

承認済み（2026-09-06）。**ADR-0003 を置き換える**（Replaces: ADR-0003）。ADR-0003 から派生した ADR-0004（superseded 済み）・ADR-0005 も、対象としていた問題が GitHub 側で解決されるため不要になる。ADR-0006（積み替え後は常に再ゲート）は**プロセスの規則**であり、引き続き有効。

## 背景

ADR-0003 では、stacked PR の運用を git 標準機能（`rebase --update-refs` ほか）と gh で自作すると決めた。当時 Graphite を棄却した理由は「外部サービスのアカウントと GitHub App 連携が必要」だった。

その後、**GitHub が stacked PR をネイティブ機能としてパブリックプレビューで提供している**ことが判明した。GitHub 公式であり外部サービスへの連携は不要なので、ADR-0003 が Graphite を棄却した理由は当てはまらない。提供物は 2 つある。

- `gh extension install github/gh-stack`: CLI 拡張（機能本体）
- `gh skill install github/gh-stack`: **AI コーディングエージェント向けの公式 skill**（操作手順・非対話フラグ・exit code 体系・コンフリクト復旧・トラブルシューティングを含む）

後者の存在は決定的である。aidd は AI 駆動開発の playbook であり、エージェントが読む手順書を自作するのではなく、GitHub 公式のものを参照すればよい。

自作路線には、この Issue の実装過程で明らかになった構造的な弱点がある。

- 手順書の記述に、**実測しないと分からない誤りが 3 回混入した**: 「マージ時の自動ブランチ削除が有効だと毎回復旧が必要」（実際は GitHub が自動で base を付け替えるため安全）、「GitHub の rename API を使えば PR の head が追随する」（実際は PR が CLOSED になる）、diff 不変判定の fail-open（実際はバイナリを原理的に判定できない）。いずれも GitHub の挙動に関する推測が原因
- 5 回の実地検証（うち検証条件を渡さないブラインドは 3 回）と 4 視点 × 3 巡の批判的レビューゲートを経てなお、未検証の経路が残った
- 手順書は約 400 行に達し、保守対象として重い

## 検討した選択肢

### 案 1: `gh stack` へ全面移行（採用）

- 概要: ブランチ管理・PR 作成・積み替え・base 付け替え・マージ順序の強制・スタック構成変更を `gh stack` に委ね、aidd の skill はプロセス（スタックにする条件・ステップ完了の定義・先行着手と中断・ゲートの適用単位と再ゲート・チェック依頼の形・P7 の分担）だけを持つ
- メリット:
  - **GitHub の挙動に関する推測が不要になる**。上記の誤りの種類自体が消える
  - サーバー側でカスケードリベースと base 自動付け替えが行われ、この Issue で最大の事故源だった「付け替えと削除の順序」が問題として消える
  - マージ順序がサーバー側で強制される（ミッドスタックの単独マージが不可）。ADR-0005 が draft に担わせていた**順序の強制**は不要になる
    - ただし **draft は別の用途で引き続き必要**である。マージ前に GitHub が見るのは PR の状態（open・非 draft）だけなので、draft は「未チェック・失効中」を表す**唯一の機械的な印**であり、`gh stack merge` が指定 PR の下を巻き込むことに対する防御にもなる。ADR-0005 が廃止されたのは順序強制の役割であって、draft の使用そのものではない
  - ブランチ保護・CODEOWNERS・必要なレビューがスタック内の全 PR に自動適用される
  - 手順書が大幅に短くなり、aidd が本来持つべきプロセスの記述に集中できる
  - **操作手順そのものを公式 skill に委譲できる**。aidd 側は手順を再掲せず、プロセス規則に集中できる（規則が特定コマンドの挙動に依存する箇所だけは最小限を書く。決定内容を参照）
  - GitHub 自身が「大量のコードを生成する場合（開発者または Copilot / AI エージェント利用時）」を向くケースとして挙げており、aidd の想定と一致する
- デメリット:
  - **パブリックプレビュー**であり仕様変更の可能性がある
  - gh 2.90.0 以降と拡張のインストールが前提になる（利用者側の環境要件が増える）
  - クロスフォークのスタックは非対応。GitHub Desktop は非対応
  - マージに新しい非同期 API を使うため、社内ボット・ダッシュボードがスタックを考慮する必要がある

### 案 2: 自作手順を維持（ADR-0003 のまま・棄却）

- メリット: プレビュー機能に依存しない
- デメリット: 約 400 行の手順を保守し続ける。未検証経路が残る。GitHub がサーバー側で行うこと（自動付け替え・順序強制）をクライアント側で再実装し続けることになり、GitHub 側の挙動が変わるたびに追随が必要

### 案 3: `gh stack` を主経路とし、自作手順をフォールバックとして残す（棄却）

- メリット: プレビューが使えない環境でも動く
- デメリット: 2 系統の手順を保守することになり、コストが倍になる。しかも自作側は検証頻度が下がって腐る。プレビューが使えない環境は「スタックを使わない（従来の 1 PR）」で足りる

## 決定内容

stacked PR の機構は `gh stack`（GitHub ネイティブ機能）に委ね、**操作手順は公式の `gh-stack` skill を単一の正とする**。生の git コマンドによる積み替え・base 付け替えは行わない。

aidd の `stacked-pr` skill は**操作手順を再掲しない**（重複させると、公式の更新に追随できず古い記述が残る）。ただし、**aidd の規則が特定のコマンドの挙動に依存する場合は、その規則を理解・実行するのに必要な最小限だけを書く**。たとえば「`submit --open` を使わない（既存 PR も含めてスタック全体が ready になるため）」は aidd 側の安全規則であり、コマンド名を挙げずには成立しない。判断基準は「これは手順の再掲か、aidd の規則の一部か」である。

導入は 2 つとも必要である。

```bash
gh extension install github/gh-stack     # CLI 拡張（機能本体）
gh skill install github/gh-stack         # エージェント向け skill（操作手順の正）
```

`stacked-pr` skill は次のプロセス規則だけを持つ。

- スタックにする条件（P5 実装計画での合意。適用ルートの境界）
- ステップ完了の定義（TDD = テスト green / DIRECT = 検証手順の完了）と PR 作成のタイミング
- 先行着手と中断の規則
- ゲートの適用単位（PR の差分ごと）と再ゲート規則（ADR-0006）
- チェック依頼の形、P7 各節の下位 PR / 最終 PR への分担

`gh stack` が使えない環境（gh のバージョンが古い、拡張を入れられない、クロスフォーク）では**スタックを使わず従来の 1 PR で進める**。フォールバックの手順は持たない。

## 設計意図

この Issue で繰り返した失敗の原因は、GitHub の挙動を推測で記述したことにある。機構を公式の実装に委ねれば、その誤りの種類は構造的に発生しなくなる。aidd が価値を持つのは「いつ・誰が・何を確認して次へ進むか」というプロセスの規律であり、git の操作手順ではない。責務をその線で切る。

## 運用上の前提（公式ドキュメント全 15 ページの確認で判明したもの）

これらは aidd の判断に影響するため、`stacked-pr` skill に記載する。

- **マージは非同期**で完了まで数分かかることがある。「コマンドが返った = マージ済み」ではないため、次へ進む前に完了を確認する
- **ブランチ保護・必須レビュー・状態チェック・CODEOWNERS・スキャンは「スタックベース」（トランク）に対して評価される**（直下の base ではない）。各 PR が独立にレビュー可能という aidd の前提と整合する
- **CI はスタック内の PR ごとに 1 回走る**。段数だけ使用量が増える。`github.event.pull_request.stack` で重いジョブを絞れる（利用先 repo の CI 設定の責務）
- **コミット署名が必須の repo では、サーバー側リベースが未署名コミットになる**。ローカルで積み替えれば署名設定に従う
- **スタックは厳密に線形**（1 親・最大 1 子）。並行作業は別スタックにする
- **非対話での並べ替え・削除は存在しない**（`gh stack modify` は TUI 専用）。回避策は `unstack` してから `init` で組み直す

## トレードオフ

- パブリックプレビューへの依存を受け入れる。仕様が変わったら追随する。プロセス層（この skill が持つ規則）は変わらないため、影響は手順の呼び出し方に限られる
- 公式 skill への依存を受け入れる。手順の正が aidd の外にあるため、その更新を aidd が制御できない。ただし自作して古くなるより、公式が更新される方が望ましい
- 利用者側に gh 2.90.0 以降・拡張・公式 skill の導入を要求する。**加えて、対象リポジトリで stacked PR が有効になっている必要がある**（無効だと `gh stack submit` が exit 9 で失敗する）。ADR-0003 が掲げた「利用先 repo に設定変更を要求しない」は**維持されない**。ただし要求するのは機能の有効化であり、ブランチ保護のような運用ルールの変更ではない
- 自作手順の実装・検証にかけた作業は破棄する。埋没費用を理由に劣った方式を維持しない

## 影響範囲

- `stacked-pr` skill（全面的な書き直し。コマンド手順を公式 skill へ委譲し、aidd はプロセス規則に集中）
- ADR-0005（draft ガード）: `gh stack` がサーバー側でマージ順序を強制するため不要になる
- Issue #18 の AC-2・AC-5・AC-6・AC-8（実現手段が変わる。Intent Delta を Issue へ記録）
- QC-1・QC-3（検証シナリオと環境要件が変わる）

## 関連

- ADR-0006 の影響範囲が指す `stacked-pr` の節番号は、本 ADR による書き直しで変わっている（旧 §4「判定手順の廃止」・§5「失効規則」は、現行では §5「再ゲートと失効」に統合された）
- Issue: wads/aidd#18
- 置き換える ADR: ADR-0003（および派生の ADR-0005）
- 公式 skill: `github/gh-stack`（`gh skill install github/gh-stack`。SKILL.md + references/{commands,stack-design,troubleshooting}.md）
- 公式ドキュメント（2026-09-06 時点で確認した全 15 ページ）:
  - get-started: [about-stacked-prs](https://docs.github.com/ja/pull-requests/get-started/about-stacked-prs)、[stacked-prs-quickstart](https://docs.github.com/ja/pull-requests/get-started/stacked-prs-quickstart)
  - reference: [stacked-pull-requests](https://docs.github.com/ja/pull-requests/reference/stacked-pull-requests)（仕様）、[stacked-prs-cli-commands](https://docs.github.com/ja/pull-requests/reference/stacked-prs-cli-commands)、[stacked-pull-requests-apis-and-webhooks](https://docs.github.com/ja/pull-requests/reference/stacked-pull-requests-apis-and-webhooks)、[use-other-tools-with-stacked-pull-requests](https://docs.github.com/ja/pull-requests/reference/use-other-tools-with-stacked-pull-requests)
  - how-tos: [index](https://docs.github.com/ja/pull-requests/how-tos/stacked-pull-requests)、[creating](https://docs.github.com/ja/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests)、[managing](https://docs.github.com/ja/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests)、[reviewing](https://docs.github.com/ja/pull-requests/how-tos/review-pull-requests/reviewing-stacked-pull-requests)、[merging](https://docs.github.com/ja/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests)、[troubleshooting](https://docs.github.com/ja/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests)、[optimizing-ci](https://docs.github.com/ja/pull-requests/how-tos/merge-and-close-pull-requests/optimizing-ci-for-stacked-pull-requests)
  - tutorials: [roll-out-stacked-prs](https://docs.github.com/ja/pull-requests/tutorials/roll-out-stacked-prs)、[stack-ai-generated-code-in-pull-requests](https://docs.github.com/ja/copilot/tutorials/stack-ai-generated-code-in-pull-requests)
  - 未読（CLI 経由で使うため）: REST 非同期マージ / GraphQL `PullRequestStack` / Webhook ペイロード
