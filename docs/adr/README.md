---
type: overview
scope: all
status: accepted
updated: 2026-09-04
---

# ADR topic 語彙表

ADR の frontmatter `topic` に使える値はこの表に限る。合う値が無ければ、その ADR と同じコミットでここに行を足す。有効 ADR の一覧は [INDEX.md](INDEX.md)（生成物。`python3 shared/scripts/adr_index.py docs/adr` で再生成）。規約は `shared/rules/common.md`「Project Binding」、経緯は [ADR-0003](0003-adr-index-and-links.md)。

機械可読なのはこの表の 1 列目（バッククォート）だけで、本文の箇条書きは語彙にならない。

| topic | 意味 |
|---|---|
| `records` | 記録・開発運用の決め方（ADR・設計書・Issue の置き場と書き方、skill の構成） |
| `tooling` | 開発ツール・ハーネスの選定と配置（Claude Code / Codex など実行環境に依存する判断） |
