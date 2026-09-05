---
name: stacked-pr
description: stacked PR（積み上げ式 PR）運用の手順 skill。複数ステップの Issue で、ステップ = 1 PR のスタックを git 標準機能 + gh で作成・積み替え・マージ追随するときに使う。手順の単一の正であり、各フェーズ skill（implementation-plan、tdd-cycle、dev、critical-gate、review）はここを参照する。
user-invocable: true
---

# Stacked PR

## いつ使うか

- P5 実装計画で複数ステップのスタック構成が確定した Issue の、PR 作成・積み替え・base 付け替え・構成変更を行うとき
- ステップが 1 つの Issue では使わない（従来どおり 1 PR。この skill への参照も発生しない）

## 環境要件

- git 2.38 以上（`rebase --update-refs` を使うため。`git --version` で確認）
- 対象 repo で draft PR が使えること（GitHub の private repo では有料プランが必要。draft はマージ順序のガードに使う）
- gh CLI（`gh pr create` / `edit --base` / `ready` / `merge` / `view --json mergeCommit` / `comment` が使えること。**必要な最低バージョンは未確認** — 手順が動かない場合はまず `gh --version` の更新を試す）

## 入力

- スタック構成（P5 実装計画で合意したステップ = 1 PR の境界・順序。Issue コメントの計画全体が正）
- Issue 番号・既定ブランチ名

## 出力

- ステップごとの draft PR（base は前ステップのブランチ）
- 積み替え・base 付け替えの実行結果と、差分の変化の記録・再ゲートの結果 → PR コメント

## 扱う Intent

- Execution Intent（実行。計画の正は Issue コメント側）

## 原則

- 各 PR の差分は常に自ステップ分のみを示す（積み替え未完了の過渡期を除く。その間は人間チェックに出さない）
- マージできるのはスタック最下段（base が既定ブランチ）の PR のみ。チェック済みでも下位が未マージなら待つ
- **最下段以外は draft のまま保つ**（ready 化は最下段になったときだけ）。GitHub は base がトピックブランチの PR でもマージボタンを有効にするため、順序制約を文章で伝えるだけでは守られない。draft はマージがブロックされ、レビュー・コメントは可能なので、順序制約の機械的ガードになる（ADR-0005）
- 積み替え・base 付け替えを行った PR は「ゲート通過済み・チェック済み」が**常に失効**する（差分が変わったかによらない。ADR-0006）。再ゲートとそのステップの検証再実行を行う
- ブランチの削除は base 付け替えの**後**に行う。付け替え前に手動削除すると上位 PR が CLOSED になる（マージ時の自動削除は GitHub が付け替えるため安全）
- 積み替えは履歴の書き換えを伴う。`git push --force-with-lease` は**自分専用のステップブランチに限り**承認不要とする（共有ブランチへの force push 禁止は従来どおり）

## 読むべき補助ファイル

- `workflow.md`
