---
type: overview
scope: all
status: accepted
updated: YYYY-MM-DD
---

# 判断領域（domain terms）

ADR の frontmatter `topic` に使える値は下の「判断領域」表に限る。合う値が無ければ、その ADR と同じコミットでここに行を足す。有効 ADR の一覧は [adr/INDEX.md](adr/INDEX.md)（生成物。`adr_index.py` で再生成）。

機械可読なのは、見出し 1 列目が `topic` の表の 1 列目（バッククォート）だけ。他の表や箇条書きは語彙にならない。

## 判断領域

| topic | 意味 |
|---|---|
| `{topic-name}` | {何についての判断か、一行} |

業務の言葉（ドメインの用語）は本書ではなく用語集 [glossary.md](glossary.md) が正本。本書は ADR を引くための判断領域タグだけを持ち、用語の定義は置かない（ADR-0011）。
