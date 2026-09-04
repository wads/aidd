# ADR Workflow

## 1. 判断の特定

何を決めるのか、なぜ今決める必要があるのかを 1〜2 行で確認する。判断に選択の余地がない（既知のパターンの適用のみ）なら ADR は作らない。

- **同 topic の既存 ADR を読む**: ADR ディレクトリの `INDEX.md` から該当 topic の有効 ADR を引いて読み、この判断がそれらと「置き換え / 補足 / 無関係」のどれに当たるかを宣言する。既存の決定を変えるのに置き換え・補足を宣言しない ADR は、衝突を後から検知できない最大の経路である
- 語彙表（`README.md`）に合う topic が無ければ、この ADR と同じコミットで語彙表へ追加する

## 2. 選択肢の整理

- 現実的な選択肢を 2〜4 案に整理し、各案の概要・メリット・デメリットをまとめる
- 選択肢が割れる、または影響が大きい場合は `multi-agent-discussion` を呼び、独立視点での調査結果（各案・差分・トレードオフ）を ADR の材料にする。最初の思いつきや既存実装に引きずられている疑いがあるときも有効
- AI の推奨案と理由を、人間の意向を聞く前に提示する。トレードオフ（何を捨てるか）と残る懸念を曖昧にしない（`common.md` の出力契約）

## 3. escalation

明確な優位案がない場合、リスクの高い判断の場合は、作業を止めて人間へ判断を仰ぐ。AI が僅差の判断を勝手に確定しない。

## 4. 人間の採用判断

最終決定は人間が行う。採用されなかった懸念・反対意見も「検討した選択肢」として記録してよい。

- 提示は `common.md`「長期コンテキスト文書の承認」に従う: 決定・選択肢・帰結（保存パス・命名規約・データ形式など、実装に現れる決定事項）を、作業の流れから切り出した選択式の問いで確定する
- P6 実装の自動進行中に戻ってきた場合（critical-gate 指摘の解消として作る ADR を含む）は、自動進行を中断してこの判断を取り、承認後に再開する

## 5. ADR の記録

- `shared/templates/adr-template.md` に従って書く。1 ページ以内を目安にし、仕様の本文ではなく判断の理由を残す
- frontmatter（`type: adr` / `scope` / `status` / `updated` / `topic` / `supersedes` / `superseded_by` / `amends` / `amended_by`）を必ず付与する。関係リンクは同じ ADR ディレクトリ内の番号のみを指す
- ファイル名: `{records_root}/adr/{連番}-short-title.md`（連番は 4 桁 0 埋め、ADR ディレクトリ内で独立）。Binding に `service` がある場合、サービス固有判断は `{records_root}/services/{service}/adr/`、複数サービス横断は `{records_root}/system/adr/` に置く
- 対象 Issue 番号は frontmatter またはコメントで紐づける（ファイル名には含めない）
- 既存 ADR の判断を置き換える場合は、新 ADR の frontmatter に `supersedes: [旧番号]` を書き、旧 ADR の frontmatter に `superseded_by: [新番号]` と `status: superseded` を追記する。補足の場合は `amends` / `amended_by` を同様に双方向で書く。旧 ADR への編集はこの frontmatter 変更のみで、本文には触れない
- 記録後、および既存 ADR の status を変えた後に `python3 {aidd_root}/shared/scripts/adr_index.py {adr_dir}`（services 側は `--vocab {records_root}/system/adr/README.md` を付ける）を実行して `INDEX.md` を再生成し、error が無いことを確認する（warning は通過を妨げない）。`skipped` が出るのは語彙表も INDEX.md も無い未移行ディレクトリだけで、移行 Issue が open で実在することを確認して通過させる（system 側は語彙表 `README.md` を作った時点で移行が始まる）
- 対象の GitHub Issue へリンクをコメントする

### 着手前に判断が固まった場合（`proposed` で起こす）

`product-intent` 前後の相談で技術判断が確定することがある。**product-intent と dev の間はコンテキストが失われる境界**であり（Issue を書く人間と着手する人間が異なり、時間差もある）、渡るのは Issue 本文・コメントと `records_root` だけで、判断の根拠となった会話は渡らない。着手を待つと記録が再構成になるか、失われる。

- この場合は着手を待たずに ADR を起こし、**`status: proposed` に留める**。Issue の関連情報からリンクする（このリンクが申し送りの役割を果たす）
- `accepted` にはしない。Architecture の採用判断はコードに触れる P3 技術判断 でエンジニアが行う。実装で初めて分かる制約により覆る余地が残っている
- 確認の担保は状態遷移で行う。P7 検証・レビュー が PR の「技術判断」セクションで `proposed` の残存を確認する（`review` skill）。自由文の申し送りには状態が無く、確認されたのか黙殺されたのか後から判別できない

## PR 作成時の連携

当該ブランチで記録した ADR は、P7 検証・レビューで PR 説明の「技術判断」セクションに設計意図・トレードオフ・影響範囲として要約される（`review` skill の責務）。

## 注意事項

- ADR は判断履歴であり、現在仕様の説明書ではない
- 設計の構造は設計書（`design-docs`）の責務。重複させない
- 連番の重複は P7 検証・レビューのチェックで検出し、後にマージする側がリネームする
