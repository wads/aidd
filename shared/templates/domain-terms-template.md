---
type: overview
scope: all
status: accepted
updated: YYYY-MM-DD
---

# 用語と判断領域（domain terms）

ADR の frontmatter `topic` に使える値は下の「判断領域」表に限る。合う値が無ければ、その ADR と同じコミットでここに行を足す。有効 ADR の一覧は [adr/INDEX.md](adr/INDEX.md)（生成物。`adr_index.py` で再生成）。

機械可読なのは、見出し 1 列目が `topic` の表の 1 列目（バッククォート）だけ。他の表や箇条書きは語彙にならない。

## 判断領域

| topic | 意味 |
|---|---|
| `{topic-name}` | {何についての判断か、一行} |

## 用語

（任意。プロジェクト固有の用語と一行の定義。ADR・設計書・Issue で同じ言葉を使うための表）
