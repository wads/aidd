# Intent Driven Development 設計メモ

この文書は、AIDD playbook の各 skill を今後修正・拡張するときに参照する設計メモである。

GitHub Issue、ADR、設計書、実装方針、テストなどの各成果物に「なぜそうするのか」「何を満たせば正しいのか」を残し、それらを `Intent Context` で辿れるようにすることで、AI 駆動開発で発生しやすい認知負債を抑える。

本 playbook では、Intent は Why と What を表すイミュータブルな記録として扱う。Intent そのものは更新せず、状況や判断が変わった場合は `Intent Delta` として追記する。

## 背景

AI 駆動開発では、ハーネスエンジニアリングによって品質、技術的負債、セキュリティのガードレールをある程度敷くことができる。

一方で、以下のような情報はテスト、lint、型検査、CI だけでは十分に保持できない。

- なぜその機能を作るのか
- 誰にどのような価値を届けたいのか
- なぜその技術判断を採用したのか
- どの制約を重視し、何を対象外にしたのか
- 何を満たせば完了と見なすのか
- 途中で意図が変わった理由は何か

これらが失われると、AI も人間も後から判断基準を復元できなくなる。結果として、動くコードは残っていても「なぜこの形なのか」が分からない状態になり、認知負債として蓄積する。

## 基本方針

Intent Driven Development は、各工程の成果物を「意図のコンテキスト」で接続する開発運用である。

重要なのは、意図を 1 つの巨大な文書へ集約することではない。各工程で必要な意図を、その工程の成果物に小さく記録し、必要に応じて上位の `Intent Context` から辿れるようにする。

Intent は以下に限定する。

- Why: なぜ必要なのか。事業上の動機、ユーザーの課題、守りたい価値
- What: 外から見て何を満たすべきか。期待する振る舞い、成功・失敗条件、制約

Intent には How を含めない。使用するライブラリ、内部データ構造、処理順序、実装ステップは、設計書や実装方針に書いてよいが、Intent とは分けて扱う。

```text
Intent Context
  ├── GitHub Issue Ticket: Product Intent
  ├── ADR: Decision Intent
  ├── Design Doc: Design Intent
  ├── Implementation Plan: Execution Intent
  ├── Tests: Verification Intent
  └── Retrospective: Learning Intent
```

実際の関連は完全な tree ではなく、複数Issue が 1 つの ADR を参照したり、1 つのテストが複数の受入れ条件を検証したりする。そのため、実体は tree を基本にした traceability graph / DAG として扱う。

## Intent Context

`Intent Context` は、機能・開発単位ごとに作成する。

推奨粒度は以下とする。

- 1 つの GitHub Issue
- 1 つのユーザーストーリー
- 1 つの機能追加
- 1 つの仕様変更
- 同じ目的を持つ小さなエピック

避ける粒度は以下とする。

- リポジトリ全体で 1 つだけの `Intent Context`
- 1 コミットごとの `Intent Context`
- 1 ファイル変更ごとの `Intent Context`
- 小さな文言修正や明白なバグ修正に毎回作ること

`Intent Context` は本文の集約場所ではなく、分散した意図を古いものから新しいものへ辿るための索引である。

```md
# Intent Context: {開発単位名}

## Goal
{この開発単位で達成したいことを短く書く}

## Sources
- GitHub Issue: {Issue 番号または URL}
- ADR: {必要なら ADR へのリンク}
- Design: {必要なら設計書へのリンク}
- Implementation Plan: {必要なら実装方針へのリンク}
- Tests: {必要ならテストや検証結果へのリンク}

## Intent Read Order
1. {最初の Product Intent または GitHub Issue}
2. {追加の ADR / 設計書 / Intent Delta}
3. {最新の ADR / Intent Delta}

## Intent Delta
- {日付}: {変更内容、理由、影響する成果物}
```

## Intent の不変性と読み順

Intent は上書きしない。ある時点の Intent は、その時点の判断として残す。

状況が変わった場合は、元の Intent を修正するのではなく、新しい `Intent Delta` を追加する。最新の意図は、古い Intent から新しい `Intent Delta` までを順に読むことで復元する。

そのため、Intent を含むドキュメントには、古いものと新しいものの順序が分かる命名を使う。

推奨する命名は以下とする。

- ADR: `docs/adr/NNNN-short-title.md`
- 設計書: `docs/design/NNNN-short-title.md` または `{ticket}-short-title.md`
- Intent Context 配下のメモ: `NNNN-kind-short-title.md`

`NNNN` は 0 埋めの連番とする。日付で並べる必要がある場合は `YYYYMMDD-short-title.md` を使う。

新しい判断が古い判断を置き換える場合は、古い文書を修正せず、新しい文書側に以下を記録する。

- どの Intent / ADR / 設計書を置き換えるのか
- 何が変わったのか
- なぜ変わったのか
- 後続工程がどちらを最新として読むべきか

## 各成果物に残す意図

### GitHub Issue Ticket: Product Intent

GitHub Issueは、PdM が「何を作るか」を AIDD で扱える形にする入口である。

主に以下を記録する。

- 背景・意図
- ユーザーストーリー
- 作るもの
- 対象範囲
- 対象外
- 受入れ条件
- 前提・制約
- 関連情報

GitHub Issueの目的は、技術的な影響範囲を網羅することではない。ユーザーに見える振る舞い、プロダクト上のスコープ、完了判断を明確にすることである。

### ADR: Decision Intent

ADR は、重要な技術判断の意図をイミュータブルに残す。

主に以下を記録する。

- 判断が必要になった背景
- 採用した選択肢
- 採用しなかった選択肢
- 判断理由
- トレードオフ
- 影響するIssue、設計書、実装

ADR は仕様の本文ではなく、判断の理由を残す場所である。
ADR-0001 の判断が後から変わった場合、ADR-0001 を書き換えない。ADR-0002 として「ADR-0001 を置き換える判断」を追加する。

### Design Doc: Design Intent

設計書は、要求や判断を実装可能な構造へ落とすときの意図を残す。

主に以下を記録する。

- 目的
- 非目的
- 責務分割
- データや状態の扱い
- 主要フロー
- 例外ケース
- 守るべき振る舞い
- 未確定事項

設計書は ADR と重複させない。技術選定や大きな判断理由は ADR へ寄せ、設計書から参照する。
設計書には How が含まれうるが、How と Intent を混ぜない。設計上の選択理由や守りたい振る舞いを Intent として分離して書く。

### Implementation Plan: Execution Intent

実装方針は、Intent を実装に移すための How を扱う成果物である。
ここで残す Execution Intent は、どの Intent を守るためにその実装順序、変更対象、検証方針を選ぶのかという判断理由である。

主に以下を記録する。

- 参照する Product Intent / Design Intent
- 実装順序とその理由
- 変更対象とその理由
- 触らない範囲とその理由
- リスク
- 検証方針
- 人間承認が必要なポイント

実装方針に How を書く場合も、Intent とは分けて扱う。作業者が変わっても同じ意図で進められるよう、How の背景にある Why / What を明示する。

### Tests: Verification Intent

テストは、何を保証するためのテストなのかを明確にする。

主に以下を記録する。

- 対応する受入れ条件
- 保証したい振る舞い
- 代表ケース
- 境界ケース
- 対象外のケース

テスト名やテストケースは、可能な限り Product Intent や Design Intent と対応付ける。テストコードに過剰な説明を埋め込むのではなく、必要に応じて設計書、Issue、検証メモへリンクする。

### Retrospective: Learning Intent

振り返りは、次に同じ種類の開発をするときに活かす意図を残す。

主に以下を記録する。

- 意図が十分に伝わった点
- 意図が不足していた点
- 後工程で認知負債になった点
- skill やテンプレートへ反映すべき改善

## Intent Delta

`Intent Delta` は、イミュータブルな Intent に対して、新しく分かったこと、変わった判断、追加された制約を追記する差分記録である。

元の Intent は修正しない。なぜ変わったのか、どの成果物へ影響するのかを残さないと、古いものから順に読んでも最新の意図を復元できなくなる。

記録する観点は以下とする。

- 変更内容
- 変更理由
- 影響する成果物
- 新しく追加した成果物
- 後工程で確認すべきこと

例:

```md
## Intent Delta
- 2026-05-14: 未ログインユーザーは検索条件保存の対象外に変更。
  理由: 保存先がユーザーアカウントに紐づくため。
  影響: Issue の受入れ条件、設計書、テストケースを読むときはこの Delta を適用する。
```

`Intent Delta` は独立した巨大ログにしない。基本は `Intent Context` に短く残し、詳細が必要な場合は新しい ADR、設計書、実装方針、検証メモへリンクする。

## skill 改修への反映方針

今後 skill を修正するときは、各 skill がどの Intent を入力し、どの Intent または Intent Delta を追記するかを明確にする。

| skill | 主な責務 | 扱う Intent |
|---|---|---|
| `product-intent` | PdM の要求を Product Intent として整理し、GitHub Issueへ落とす | Product Intent |
| `dev` | 実装プロセスを選び、実装へ進める | Product / Design / Execution Intent |
| `tdd-cycle` | 受入れ条件や設計意図をテストへ落とす | Verification Intent |
| `review` | diff が意図、設計、テストと整合しているか確認する | Product / Decision / Design / Verification Intent |
| `retrospective` | 開発後の学びを次の改善へつなげる | Learning Intent |
| `multi-agent-discussion` | 複数視点で判断材料を整理する | Decision Intent |
| `ui-migration` | UI 移行の設計、変換、検証をつなぐ | Design / Execution / Verification Intent |
| `ui-prototyping` | PdM との見た目・操作感のすり合わせを行う | Product / Design Intent |

skill の出力では、必要に応じて以下を明示する。

- 参照した Intent
- 新しく追加した Intent
- 新しく追加した Intent Delta
- 未確定の Intent
- 後工程へ渡すべき Intent

## Product Intent skill の方向性

`product-intent` skill は、Intent Driven Development の入口として扱う。

目的は、GitHub Issue作成そのものではなく、PdM の要求を AI が実装、テスト、レビューで扱える Product Intent に整えることである。

Issue本文の基本構成は以下を想定する。

```md
## 背景・意図
{なぜ作るのか、どんな課題や機会に対応するのか}

## ユーザーストーリー
{対象ユーザー} として、
{やりたいこと} したい。
なぜなら {得たい価値・解決したい課題} だから。

## 作るもの
{ユーザーに見える振る舞いとして何を作るのか}

## 対象範囲
- 対象画面・導線:
- 対象ユーザー・ケース:
- 対象外:

## 受入れ条件
- {条件または操作} のとき、{期待結果} になる
- {確認観点} を {確認方法} で確認できる

## 前提・制約
{なければ「特になし」}

## 関連情報
{なければ「特になし」}
```

Product Intent skill の品質チェックでは、少なくとも以下を見る。

- 背景・意図が第三者に伝わるか
- ユーザーストーリーが価値と対象ユーザーを表しているか
- 作るものがユーザーに見える振る舞いとして説明されているか
- 対象範囲と対象外が区別されているか
- 受入れ条件が確認可能な粒度になっているか
- 不明点を AI が推測で補っていないか

技術的な影響範囲、実装方式、詳細なテスト範囲、Lite / Standard / Full の判断は、原則として Product Intent skill の必須責務にしない。

## 運用上の注意

- 意図を長文化しない
- 同じ意図を複数箇所に重複記載しない
- 古い Intent を上書きしない
- AI が不明な意図を推測で補わない
- 各工程の意図は、その工程で判断可能な粒度に限定する
- 重要な意図変更は `Intent Delta` として残す
- 古いものから新しいものへ読める命名とリンクを保つ

この設計の成功条件は、「意図を大事にする」という方針を掲げることではない。各 skill が、自分の工程でどの Intent を受け取り、何を追記し、次工程へ何を渡すのかを具体的な出力契約として持つことである。

## Intent Delta

本文書はイミュータブルな設計メモとして残し、以後の変更はこの Delta で表す。最新の運用は [0001-dev-phase-decomposition.md](0001-dev-phase-decomposition.md) を正とする。

- 2026-06-12: `Intent Context` は repo 内のファイルとして作らない。索引の役割は GitHub Issueが担う（Issue 番号を全成果物に埋め込み、Issue に ADR・設計書・PR へのリンクを貼る）。本文書の「Intent Context」章はファイル前提で書かれているため、運用ではIssue を索引として読み替える。
  理由: 短期コンテキストは PR/Issue に残すだけでよいという方針と、索引ファイルの維持コスト回避。
  影響: Intent Context テンプレート（本文書内）は使用しない。
- 2026-06-12: 命名規則を `NNNN-short-title.md` から `{連番}-{Issue 番号}-short-title.md`（例: `00042-#123-cache-strategy.md`、連番は 5 桁 0 埋めで `docs/adr/` と `docs/design/` 各々独立）へ変更する。文書の新旧・置き換え関係の正は、ファイル名順序ではなく置き換える側の文書に明記する「Replaces: {旧文書}」とする。
  理由: GitHub Issueへのトレーサビリティと、ディレクトリ内の時系列の両立。
  影響: 本文書「Intent の不変性と読み順」の命名節は、上記の形式で読み替える。
- 2026-06-12: 「いまの設計がどうなっているか」の把握は、人間が維持する living doc ではなく、コード・テスト・不変記録からその場で生成するビュー（`context-snapshot` skill）で行う。生成ビューは使い捨てで、不変記録と食い違った場合は記録側を正とする。
  理由: Intent + Delta の順読みは判断履歴の保全には優れるが、現在状態の把握には不向き。維持される文書は陳腐化と維持コストの問題を持つ。
  影響: 各成果物のイミュータブル原則は変更なし。読み手向けのビュー層が追加される。
- 2026-06-12: `dev` skill の Lite / Standard / Full（規模ベースの mode）を廃止し、Issueタイプ別ルート（feature / bugfix / hotfix / refactoring / chore / spike、GitHub ラベル `type-*` で管理）へ置き換える。フェーズ構成・各 skill の Intent 入出力契約は 0001-dev-phase-decomposition.md に定義する。
  理由: フェーズの形は規模ではなくタイプで決まり、タイプはIssue 作成時に機械的に確定できるため。
  影響: 本文書「skill 改修への反映方針」の表は、0001 の skill 分解案を最新として読む。

## 参考

- [仕様駆動開発(SDD)から、意図駆動開発(IDD)へ](https://zenn.dev/yamaken0107/articles/2b3d2a0b059aa0)
