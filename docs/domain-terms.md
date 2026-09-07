---
type: overview
scope: all
status: accepted
updated: 2026-09-07
---

# 用語と判断領域（domain terms）

ADR の frontmatter `topic` に使える値は下の「判断領域」表に限る。合う値が無ければ、その ADR と同じコミットでここに行を足す。有効 ADR の一覧は [adr/INDEX.md](adr/INDEX.md)（生成物。リポジトリルートで `python3 shared/scripts/adr_index.py docs/adr` を実行して再生成）。規約は `shared/rules/common.md`「Project Binding」と `adr` skill、経緯は [ADR-0003](adr/0003-adr-index-and-links.md)。

機械可読なのは、見出し 1 列目が `topic` の表の 1 列目（バッククォート）だけ。本文の箇条書きや他の表は語彙にならない。

## 判断領域

| topic | 意味 |
|---|---|
| `records` | 記録・開発運用の決め方（ADR・設計書・Issue の置き場と書き方、skill の構成） |
| `tooling` | 開発ツール・ハーネスの選定と配置（Claude Code / Codex など実行環境に依存する判断） |
