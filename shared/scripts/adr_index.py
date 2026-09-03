#!/usr/bin/env python3
"""ADR ディレクトリから有効な ADR の索引 INDEX.md を生成し、frontmatter の整合を照合する。

Usage:
    python3 shared/scripts/adr_index.py ADR_DIR [--vocab README.md] [--check]

ADR_DIR 直下の NNNN-*.md を読む。topic の語彙表は ADR_DIR/README.md（--vocab で別の場所を指定可）。
照合で誤りがあれば INDEX.md を書かず終了コード 1 を返す。--check は書かずに INDEX.md の陳腐化だけを検査する。
"""
import argparse
import os
import re
import sys
from dataclasses import dataclass, field

STATUSES = ("proposed", "accepted", "superseded", "deprecated")
ACTIVE_STATUSES = ("proposed", "accepted")
RELATIONS = (("supersedes", "superseded_by"), ("amends", "amended_by"))
SKEW_HIGH = 10
INDEX_NAME = "INDEX.md"
VOCAB_NAME = "README.md"

ADR_FILE = re.compile(r"^(\d{4})-.*\.md$")
NUMBER = re.compile(r"(\d+)")
VOCAB_LINE = re.compile(r"^(?:\||-)\s*`([^`]+)`\s*(?:\||:)?\s*(.*?)\s*\|?\s*$")
TITLE_PREFIX = re.compile(r"^\s*(?:\[ADR-\d+\]|ADR[- ]?\d+[:.]?|\d{4}\.)\s*")


@dataclass
class Adr:
    num: str
    filename: str
    title: str
    status: str
    topics: list
    links: dict


@dataclass
class Result:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    index: str = ""


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = _parse_value(value.strip())
    return data


def _parse_value(value):
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
    return value.strip("'\"")


def normalize_number(value):
    match = NUMBER.search(str(value))
    return f"{int(match.group(1)):04d}" if match else str(value)


def load_vocab(path):
    vocab = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            match = VOCAB_LINE.match(line.strip())
            if match and match.group(1) != "topic":
                vocab.append((match.group(1), match.group(2)))
    return vocab


def load_adrs(adr_dir):
    adrs = []
    for name in sorted(os.listdir(adr_dir)):
        match = ADR_FILE.match(name)
        if not match:
            continue
        with open(os.path.join(adr_dir, name), encoding="utf-8") as f:
            text = f.read()
        fm = parse_frontmatter(text)
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), name)
        links = {}
        for fwd, back in RELATIONS:
            for key in (fwd, back):
                raw = fm.get(key, [])
                links[key] = [normalize_number(v) for v in (raw if isinstance(raw, list) else [raw]) if v]
        topics = fm.get("topic", [])
        adrs.append(Adr(
            num=match.group(1),
            filename=name,
            title=TITLE_PREFIX.sub("", title),
            status=str(fm.get("status", "")),
            topics=topics if isinstance(topics, list) else [topics],
            links=links,
        ))
    return adrs


def validate(adrs, vocab_names):
    errors, warnings = [], []
    by_num = {a.num: a for a in adrs}
    for a in adrs:
        if a.status not in STATUSES:
            errors.append(f"ADR-{a.num}: status '{a.status}' は不正（{' / '.join(STATUSES)} のいずれか）")
        if not a.topics:
            errors.append(f"ADR-{a.num}: topic が無い")
        for t in a.topics:
            if t not in vocab_names:
                errors.append(f"ADR-{a.num}: topic '{t}' は語彙表（{VOCAB_NAME}）に無い")
        for fwd, back in RELATIONS:
            for target in a.links[fwd]:
                other = by_num.get(target)
                if other is None:
                    errors.append(f"ADR-{a.num}: {fwd} の ADR-{target} が存在しない")
                elif a.num not in other.links[back]:
                    errors.append(f"ADR-{target}: {back} に {a.num} が無い（ADR-{a.num} が {fwd} を宣言）")
            for target in a.links[back]:
                other = by_num.get(target)
                if other is None:
                    errors.append(f"ADR-{a.num}: {back} の ADR-{target} が存在しない")
                elif a.num not in other.links[fwd]:
                    errors.append(f"ADR-{target}: {fwd} に {a.num} が無い（ADR-{a.num} が {back} を宣言）")
        if a.links["superseded_by"] and a.status != "superseded":
            errors.append(f"ADR-{a.num}: superseded_by があるが status が '{a.status}'（superseded にする）")
        if a.status == "superseded" and not a.links["superseded_by"]:
            errors.append(f"ADR-{a.num}: status が superseded だが superseded_by が空")

    counts = {}
    for a in adrs:
        if a.status in ACTIVE_STATUSES:
            for t in a.topics:
                if t in vocab_names:
                    counts[t] = counts.get(t, 0) + 1
    for t, n in counts.items():
        if n > SKEW_HIGH:
            warnings.append(f"topic '{t}' の有効 ADR が {n} 本（{SKEW_HIGH} 本超。分割を検討）")
        elif n == 1:
            warnings.append(f"topic '{t}' の有効 ADR が 1 本のみ（統合を検討）")
    return errors, warnings


def _relations(a):
    parts = []
    for key in ("supersedes", "amends", "amended_by"):
        if a.links[key]:
            parts.append(f"{key} {', '.join(a.links[key])}")
    return parts


def render(adrs, vocab):
    lines = [
        f"<!-- generated by shared/scripts/adr_index.py; do not edit. Regenerate: python3 shared/scripts/adr_index.py <adr_dir> -->",
        "# ADR 索引（有効な決定）",
        "",
        f"topic の意味は語彙表（{VOCAB_NAME}）を参照。失効した ADR は末尾に置く。",
    ]
    active = [a for a in adrs if a.status in ACTIVE_STATUSES]
    for name, desc in vocab:
        members = [a for a in active if name in a.topics]
        if not members:
            continue
        lines += ["", f"## {name} · {desc}" if desc else f"## {name}", ""]
        for a in members:
            lines.append(f"- [ADR-{a.num} {a.title}]({a.filename}) · {a.status}" + "".join(f" · {p}" for p in _relations(a)))
    retired = [a for a in adrs if a.status not in ACTIVE_STATUSES]
    if retired:
        lines += ["", "## 失効", ""]
        for a in retired:
            tail = f"superseded by {', '.join(a.links['superseded_by'])}" if a.links["superseded_by"] else a.status
            lines.append(f"- [ADR-{a.num} {a.title}]({a.filename}) · {tail}")
    return "\n".join(lines) + "\n"


def run(adr_dir, vocab_path=None, write=False):
    vocab = load_vocab(vocab_path or os.path.join(adr_dir, VOCAB_NAME))
    adrs = load_adrs(adr_dir)
    errors, warnings = validate(adrs, [name for name, _ in vocab])
    result = Result(errors=errors, warnings=warnings)
    if errors:
        return result
    result.index = render(adrs, vocab)
    if write:
        with open(os.path.join(adr_dir, INDEX_NAME), "w", encoding="utf-8") as f:
            f.write(result.index)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("adr_dir")
    parser.add_argument("--vocab", help=f"topic 語彙表のパス（既定: ADR_DIR/{VOCAB_NAME}）")
    parser.add_argument("--check", action="store_true", help="INDEX.md を書かず、最新かどうかだけ検査する")
    args = parser.parse_args(argv)

    result = run(args.adr_dir, vocab_path=args.vocab, write=not args.check)
    for w in result.warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in result.errors:
        print(f"error: {e}", file=sys.stderr)
    if result.errors:
        return 1
    index_path = os.path.join(args.adr_dir, INDEX_NAME)
    if args.check:
        current = ""
        if os.path.exists(index_path):
            with open(index_path, encoding="utf-8") as f:
                current = f.read()
        if current != result.index:
            print(f"error: {index_path} が最新ではない（--check なしで再生成する）", file=sys.stderr)
            return 1
        print(f"ok: {index_path} は最新")
        return 0
    print(f"wrote: {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
