---
type: adr
scope: all
status: accepted
updated: 2026-09-07
topic: [records]
summary: ADR に topic・要旨・双方向リンクを持たせ、語彙表 domain-terms.md と生成索引 INDEX.md をスクリプトで照合する。ADR ディレクトリは records_root ごとに 1 つ
amends: [0002]
---

# [ADR-0003] ADR の検索性と置き換え関係の機械可読化

## ステータス

承認済み（2026-09-04。critical-gate の指摘を受けて同日に決定 4・5・7 を修正。2026-09-07 のレビューで決定 1・4・5 を修正し、決定 9 を追加）

## 背景

ADR は追記専用の判断履歴であり、本数が増えるほど「どの決定が今有効か」「この判断領域を扱う ADR はどれか」を引く手段が要る。現行の規約には次の欠落がある。

- 検索軸が無い: frontmatter は `type` / `scope` / `status` / `updated` のみで、判断領域で引けない。skill の参照は Issue 番号 grep に限られ、「この Issue が従うべき過去の ADR」は見つからない
- 衝突を検知しない: adr skill の手順は同領域の既存 ADR を読まない。既存の決定を置き換える ADR を、置き換えと認識せずに新規として書ける
- 置き換え関係が片方向で規約が揺れている: workflow は「旧 ADR を書き換えず新 ADR に Replaces を書く」とする一方、テンプレートは `status: superseded` を持ち、実際の ADR-0001 には本文冒頭に注記が前置きされている。旧 ADR に着地した読み手は失効を知る手段が無い。「置き換え」でなく「補足」の関係は未定義
- status の語彙が割れている: テンプレートは `accepted`、利用側ハブ（remosys-context）は `active` を使う

人間だけの運用では「書いたことを覚えている人」が索引を兼ねるため 30〜50 本まで顕在化しないが、AI が主担当だと記憶による索引が毎セッション消えるため閾値はもっと早い。逆に、有効な決定だけを領域別に並べ直す作業は AI・スクリプト向きである。

## 検討した選択肢

### 案1: frontmatter に検索軸と関係リンクを追加し、索引をスクリプトで生成する（採用）

- 概要: `topic`（判断領域、複数可）と関係リンク `supersedes` / `superseded_by` / `amends` / `amended_by` を frontmatter に追加。records_root に手書きの topic 語彙表（`domain-terms.md`）、ADR ディレクトリにスクリプト生成の有効 ADR 索引（`INDEX.md`）を置く。生成スクリプトが語彙表照合・双方向リンク・superseded の残存を検査し、マージ前契約チェック（`review/acceptance.md` §7）で実行する
- メリット: 検索・衝突検出・失効表示が機械可読になる。索引が生成物なので腐らない。照合が AI の読み落としに依存しない
- デメリット: aidd に初のコード資産（スクリプト）が入る。フィールドが 5 つ増える

### 案2: 規約のみ追加し、索引は AI が生成する

- 概要: 案1 と同じ frontmatter を導入するが、INDEX.md はレビュー時に AI が ADR を読んで書き直す
- メリット: コード資産が増えない
- デメリット: 照合の信頼性が AI の読み落としに依存する。「確認済み」の主張を機械照合で裏づける証拠つき報告の趣旨に反する

### 案3: 何もしない（Issue 番号 grep と人間の記憶で運用）

- 概要: 現状維持
- メリット: 変更コストゼロ
- デメリット: 本数が増えた時点で衝突・失効の見落としが起きる。AI 主担当では閾値が早い

### 案4: 旧 ADR を要約圧縮した digest を維持する

- 概要: 古い ADR をまとめて要約し、AI は digest だけを読む
- デメリット: 判断理由が失われる。digest 自体が手書きの二重管理になる。不採用

## 決定内容

1. **frontmatter フィールドの追加**（テンプレート `shared/templates/adr-template.md`）
   - `topic`: 判断領域タグのリスト。複数可。値は語彙表 `domain-terms.md`（決定 4）に定義されたものに限る
   - `summary`: 決定の要旨一行。必須。INDEX.md の行に出し、索引だけでトリアージできるようにする（同 topic の ADR を全部読む側のコンテキストを抑える）
   - `considered`: 同 topic の既存 ADR のうち、読んで「無関係」と判断した番号。同 topic で自分より若い番号の有効 ADR は、`supersedes` / `amends` / `considered` のいずれかに必ず現れなければならない（スクリプトが検査する。内容の正しさは見ないが「読まずに飛ばした」は止まる）
   - `supersedes` / `superseded_by`: 置き換え（旧決定は全体が失効）。新 ADR が `supersedes`、旧 ADR が `superseded_by` を持ち、必ず双方向にする
   - `amends` / `amended_by`: 補足・部分修正（旧決定は有効のまま一部を追加・修正）。同じく双方向。**旧 ADR の一部だけを失効させる場合は `supersedes` でなく `amends`** を使う（`supersedes` は旧 ADR を丸ごと有効索引から外すため、生き残った決定が消える）
   - 関係リンク 4 つと `considered` は関係があるときだけ書く（空リストの行は不要）
   - `issue`: 任意。対象 Issue の参照（例 `owner/repo#123`）。スクリプトは検証しない。規約「Issue 番号は frontmatter または Issue コメントで紐づける」の frontmatter 側の受け皿
2. **status の語彙**: `proposed` / `accepted` / `superseded` / `deprecated`（置き換え先なしの失効）に統一。`active` は使わない
3. **旧 ADR の編集範囲**: `status` の変更と `superseded_by` / `amended_by` の追記（と `updated` の更新）のみ。本文には触れない。失効の表示は frontmatter と INDEX.md が担う。ADR-0001 冒頭の注記は残置し、以後は書かない
4. **語彙表と索引の置き場**: 語彙表は ADR ディレクトリの外、その親に `domain-terms.md` として置く（standalone は `{records_root}/domain-terms.md`、ハブは `{records_root}/system/domain-terms.md`。テンプレート `shared/templates/domain-terms-template.md`）。用語集としても使え、ADR の README.md は人間向け説明のために空けておく。機械可読なのは見出し 1 列目が `topic` の表の 1 列目のバッククォートだけ。`INDEX.md` は ADR ディレクトリ内の生成物（有効 ADR = `proposed` / `accepted` の topic 別一覧に要旨と置き換え・補足関係を併記。先頭に生成物・編集禁止を明記）。INDEX.md と関係リンクの解決範囲は **同一 ADR ディレクトリ内に限る**（連番はディレクトリごとに独立のため）。この制約が制約にならないよう、ADR ディレクトリは records_root ごとに 1 つだけ置く（決定 9）
5. **索引の生成と照合**: aidd 同梱のスクリプト `{aidd_root}/shared/scripts/adr_index.py`（python3、依存なし。`aidd_root` は Binding に追加する。リポジトリルートを cwd にして実行する）が ADR ディレクトリを引数に INDEX.md を生成する。語彙表は既定で ADR ディレクトリの親の `domain-terms.md`（`--terms` で変更可）。同時に次を誤りとして報告し、誤りがあれば INDEX.md を書かない: frontmatter の不在、必須項目（`type` / `scope` / `status` / `updated` / `topic` / `summary`）の欠落と不正値、語彙表に無い topic、片方向・自己参照・不在のリンク、失効なのに status が有効のままの ADR（と `superseded` なのに `superseded_by` が無い ADR）、連番重複、同 topic の若い番号の有効 ADR を読んだ宣言（決定 1 の `considered`）の欠落。topic の偏り（1 topic に 10 本超）は警告。語彙表も `INDEX.md` も無いディレクトリだけを未移行とみなし、警告のみで照合と生成を省略する（既存の利用側が移行を終えるまで壊さない。ADR ディレクトリが無い・ディレクトリでない・読めない、`--terms` のパスが無い、語彙表が読めない・ファイルでない、INDEX.md があるのに語彙表が無い、語彙表に topic 表が無い、の各場合は error にし、skip が抜け道にならないようにする）。マージ前契約チェック（`review/acceptance.md` §7）では `--check`（書かずに INDEX.md の陳腐化を検査。改行コードの変化も検出）で実行する。python3 が無い環境では §7 の第 3 の通過条件（手作業照合と確認範囲の明記）に従う
6. **skill の変更**: adr workflow 手順 1 に「同 topic の既存 ADR を読み、置換 / 補足 / 無関係のいずれかを宣言する」を追加。critical-gate のレンズに「既存 ADR と矛盾していないか」を追加。context-snapshot と implementation-plan の ADR 参照を Issue 番号 grep から Issue 番号 + topic へ広げる
7. **topic の見直し**: 定期見直しはしない。トリガーは (a) 新 ADR に合う topic が無い、(b) スクリプトの分割警告、(c) 振り返りで「引けなかった」が期待違反として出た、の 3 つ。見直しは frontmatter の一括書き換えと再生成で行い、本文には触れない。「1 本のみの topic」は警告しない（新 topic は必ず 1 本から始まり、統合の要否は (c) で拾う）
8. **適用範囲**: 本 ADR は ADR のみを対象とする。設計書の置き換え規約（`design-docs` skill の「Replaces」）は変えない。設計書へ広げる場合は別 ADR で決める
9. **ADR ディレクトリは分割しない**（ADR-0002 の記録形式の決定を、ADR について修正する）: Binding に `service` があっても ADR を `services/{service}/adr/` に分けず、records_root ごとに 1 つの ADR ディレクトリへ集約する（ハブ構成では `system/adr/`）。どのサービスの判断かは既存の `scope` フィールドで表す。設計書の `services/{service}/design/` 分割は維持する。スクリプトの `--vocab` は分割を前提とした機能なので削除する

## 設計意図

手書きは各 ADR と語彙表だけに限定し、索引は常に再生成できる従属物にする。「引く」「衝突に気づく」「失効を知る」の 3 つを、人間の記憶でなく frontmatter とスクリプトに持たせる。語彙表と索引を別ファイルにするのは、生成時の照合相手を作るため（単一ファイルにすると、語彙表に無い topic を検出できない）。

## トレードオフ

- aidd が言語非依存のテンプレートである中に python3 スクリプトが入る。python3 が無い環境では照合が動かない（退避経路は `review/acceptance.md` §7 の第 3 の通過条件: 手作業で語彙表・リンクを照合し、確認した範囲を PR に明記する。INDEX.md は手書き可）
- topic の粒度は事前に決めない。最初の 10 本程度を書きながら決める。細かすぎれば付与がぶれ、粗すぎれば検索の意味が無い
- 移行（既存 ADR への topic / summary / considered の遡及付与）と topic の統合時は、網羅規則により同 topic の先行 ADR を遡って `considered` に書くことになり、「読んだ宣言」は一括記入になる（ハブ 9 本で 13〜36 エントリの試算）。移行では全 ADR を読むので実質の追加負荷は小さいと見て受容する
- 必須フィールドが 2 つ（`topic` / `summary`）増え、関係があるときだけ書くフィールドが 5 つ増える。ADR 1 本あたりの人間判断の純増は「topic を選ぶ」「要旨を一行書く」「同 topic の既存 ADR を読んで置換 / 補足 / 無関係を宣言する」の 3 つ

## 影響範囲

- aidd: `shared/templates/adr-template.md`、`shared/rules/common.md`、`.claude/skills/adr/workflow.md`、`critical-gate/lenses.md`、`review/acceptance.md`、`context-snapshot/workflow.md`、`implementation-plan/template.md`、`shared/scripts/`（新設）、`docs/domain-terms.md`・`docs/adr/INDEX.md`（新設）、既存 ADR-0001 / 0002 の frontmatter
- aidd（決定 9）: `shared/rules/common.md` の記録の配置、`.claude/skills/adr/workflow.md`、`review/acceptance.md`、`shared/scripts/adr_index.py`（`--vocab` の削除）と対応するテスト、ADR-0002 の `amended_by`
- aidd（2026-09-07 レビュー反映）: `docs/domain-terms.md`（`docs/adr/README.md` から移動）、`shared/templates/domain-terms-template.md`（新設）、テンプレートの `summary` / `considered` と関係リンクの任意化、スクリプトの BOM・自己参照・CRLF・見出し抽出・必須項目・網羅検査、`CLAUDE.md` の Test command を `TODO:` に戻し aidd 自身のコマンドは `README.md` へ
- aidd（追加）: `docs/design/0001-dev-phase-decomposition.md` と `docs/design/intent-driven-development.md` の置き換え規約の記述（ADR に限定）、`README.md` の構成表、`docs/manual.md`、`.claude/skills/retrospective/workflow.md`（見直しトリガー (c) の受け皿）、`CLAUDE.md` の Test command、`.gitignore`
- 利用側（remosys-context ハブ）: `conventions/context-format.md` の ADR 向け status 語彙の分離と、`services/<name>/adr/` を許す記述の削除（いずれもハブ側の P3 判断）、`system/adr/` の既存 9 本への topic・summary・considered の付与と見出し・status の統一、`system/domain-terms.md` / `system/adr/INDEX.md` の新設。[clachic/remosys-context#79](https://github.com/clachic/remosys-context/issues/79) で行う。移行完了までは決定 5 の未移行扱いで照合が省略される

## 議論ログ

- [2026-09-04] Human: 通し番号で全読みすると飽和しないか、上書き・追加で引きにくくならないか、という懸念を提示
- [2026-09-04] AI: 飽和は skill が Issue 番号 grep で参照するため起きにくい。実在するのは「引けない・衝突に気づけない・置き換えが片方向」の 3 点と評価
- [2026-09-04] Human: 用語（supersedes / superseded_by / amends）、jrc での topic 例、README と INDEX の使い分け、見直しのタイミングを確認。INDEX.md は ADR ディレクトリ内に置く想定と明示
- [2026-09-04] Human: 選択式の問いで、索引はスクリプト生成、status は accepted 系、旧 ADR の編集は frontmatter のみ、を採用
- [2026-09-04] AI: critical-gate（4 視点）で不通過。Critical 4 件（topic 所属・有効判定・誤警告のテスト欠落、`__pycache__` のコミット）と、設計判断を要する指摘 4 件（1 本警告の扱い、設計書への適用範囲、ハブ横断参照、ハブへの即時影響）
- [2026-09-04] Human: 1 本警告は廃止、適用は ADR 限定、関係リンクは同一ディレクトリ内に限定、ハブは移行 Issue（#79）を作成し未移行ディレクトリは照合を省略、を採用
- [2026-09-05] AI: 再ゲートで Critical 1 件（services 側は語彙表を持たないため、`--vocab` を付け忘れると移行後も恒久的に skip される）
- [2026-09-05] Human: skip は「語彙表も INDEX.md も無く `--vocab` 未指定」に限定し、`aidd_root` を Binding に追加、を採用
- [2026-09-05] AI: 3 回目のゲートで Critical 1 件（存在しないディレクトリを未移行と誤診）。ディレクトリ存在判定と topic 表不在の error を追加
- [2026-09-05] AI: 4 回目のゲート通過（Critical なし）。同じ故障クラスの Warning（読めないディレクトリ・非ディレクトリ・`--vocab` がディレクトリ）を error にして閉じた
- [2026-09-07] AI: レビュー（4 視点）で、`services/{service}/adr/` は利用側ハブで 3 か月・ADR 9 本の運用中に 1 本も使われておらず、サービス軸は既存の `scope` が担っていると報告。分割は決定 4 の「解決範囲は同一ディレクトリ内」と組み合わさると、サービス側から system の決定が引けず、境界をまたぐ置き換えも表現できないため有害と評価
- [2026-09-07] Human: 選択式の問いで、ADR ディレクトリの統合（決定 9）と本 ADR への取り込みを採用
- [2026-09-07] AI（レビュー担当）: 4 観点レビューで条件付き差し戻し。スクリプトの BOM・自己参照・CRLF・見出し抽出、python3 不在時の退避経路の不在、新規プロジェクトが無検証で通る、`docs/adr/README.md` の慣習との衝突、索引に要旨が無く同 topic を全読みする側で 1 判断 45K トークンになりうる、衝突検出が指示のみで検出力ゼロ、空リンク 4 行の死んだ記述、common.md の箇条書きが 1000 字超、を指摘
- [2026-09-07] Human: 選択式の問いで、語彙表は ADR ディレクトリの外の `domain-terms.md`、`summary` は必須、`considered` による網羅検査、を採用。残りは指摘どおり修正
- [2026-09-07] AI: 再ゲート（5 回目）で Critical 1 件（PR 本文のハブ実行記録が失敗出力のまま skip の証拠として引かれていた。jrc の symlink 先が main の aidd でスクリプトが無かった）。ブランチのスクリプトで採取し直して差し替え。Warning として決定 3 と移行・本 PR の frontmatter 追記の矛盾、移行時の considered 一括記入の負荷、を報告
- [2026-09-08] Human: 決定 3 は狭いまま残し、既存 ADR への topic / summary / considered の遡及付与（本 PR の ADR-0001 / 0002 と #79 のハブ 9 本）は今回限りの移行として例外扱いにする。規約に例外は書かない。移行時の considered 一括記入は受容しトレードオフに明記。テンプレートに任意の `issue` 欄を追加
