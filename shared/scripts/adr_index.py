#!/usr/bin/env python3
"""ADR ディレクトリから有効な ADR の索引 INDEX.md を生成し、frontmatter の整合を照合する。

Usage（リポジトリルートを cwd にして実行する）:
    python3 {aidd_root}/shared/scripts/adr_index.py ADR_DIR [--terms PATH] [--check]

ADR_DIR 直下の NNNN-*.md を読む。関係リンク（supersedes 等）は同じ ADR_DIR 内の番号のみを指す。
topic の語彙表は既定で ADR_DIR の親の domain-terms.md（--terms で別の場所を指定可）。語彙表の機械可読部分は、
見出し 1 列目が topic の表（各行 1 列目がバッククォートの topic 名）。
語彙表も INDEX.md も無いディレクトリを未移行とみなし、警告のみで照合と生成を省略する。
次は error（skip の抜け道にしない）: ADR_DIR が無い・ディレクトリでない・読めない、--terms のパスが無い・読めない、
語彙表が読めない、INDEX.md があるのに語彙表が無い、語彙表に topic 表が無い。
照合で誤りがあれば INDEX.md を書かず終了コード 1 を返す。--check は書かずに INDEX.md の陳腐化だけを検査する。
frontmatter は 1 行の `key: value`、行内リスト `[a, b]`、ブロックリスト（次行以降の `- item`）、行末の ` # コメント` に対応する。
先頭の BOM と空行、列 0 の `#` 行は無視する。引用符は値を保護しない（`"A # B"` も ` # ` 以降が落ちる）。
未知のキーは warning（スペルミスの検出。独自キーは無視してよい）。関係リンクの 4 フィールドと considered は関係があるときだけ書けばよい。
"""
import argparse
import difflib
import os
import re
import sys
from dataclasses import dataclass, field

STATUSES = ("proposed", "accepted", "superseded", "deprecated")
ACTIVE_STATUSES = ("proposed", "accepted")
RELATIONS = (("supersedes", "superseded_by"), ("amends", "amended_by"))
LINK_KEYS = ("supersedes", "superseded_by", "amends", "amended_by", "considered")
COVERAGE_KEYS = ("supersedes", "amends", "considered")
REQUIRED_TEXT = ("type", "scope", "updated", "summary")
KNOWN_KEYS = REQUIRED_TEXT + ("status", "topic", "issue") + LINK_KEYS
SKEW_HIGH = 10
INDEX_NAME = "INDEX.md"
TERMS_NAME = "domain-terms.md"
HUMAN_DOCS = ("README.md",)

ADR_FILE = re.compile(r"^(\d{4})-.*\.md$")
NUMBER = re.compile(r"(\d+)")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TABLE_ROW = re.compile(r"^\|(.*)\|?\s*$")
VOCAB_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|?\s*$")
TITLE_PREFIX = re.compile(r"^\s*(?:\[ADR-\d+\]|ADR[- ]?\d+[:.]?|\d{4}\.)\s*")
COMMENT = re.compile(r"\s+#\s.*$")
BLOCK_ITEM = re.compile(r"^\s*-\s+(.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Adr:
    num: str
    filename: str
    title: str
    fm: dict
    status: str
    topics: list
    links: dict
    label: str = ""


@dataclass
class Result:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    index: str = ""
    skipped: bool = False


def split_frontmatter(text):
    """(frontmatter dict または None, 本文) を返す。BOM と先頭の空行は無視する。"""
    lines = text.lstrip("﻿").splitlines()
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or lines[start].strip() != "---":
        return None, lines
    data = {}
    key = None
    i = start + 1
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.strip() == "---":
            return data, lines[i:]
        if line.lstrip().startswith("#"):
            continue
        line = COMMENT.sub("", line.rstrip())
        if not line.strip():
            continue
        item = BLOCK_ITEM.match(line)
        if item and key is not None:
            if not isinstance(data[key], list):
                data[key] = [data[key]] if data[key] else []
            data[key].append(_unquote(item.group(1)))
            continue
        if ":" not in line:
            continue
        raw_key, value = line.split(":", 1)
        key = raw_key.strip()
        data[key] = _parse_value(value.strip())
    return None, lines


def parse_frontmatter(text):
    data, _ = split_frontmatter(text)
    return data or {}


def _unquote(value):
    return value.strip().strip("'\"")


def _parse_value(value):
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        return [_unquote(v) for v in value[1:-1].split(",") if v.strip()]
    return _unquote(value)


def _as_list(value):
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def _as_numbers(value):
    """リンク欄の値を番号のリストにする。角括弧なしのカンマ区切りも受け付ける。"""
    items = []
    for v in _as_list(value):
        items += [part.strip() for part in str(v).split(",") if part.strip()]
    return items


def normalize_number(value):
    match = NUMBER.search(str(value))
    return f"{int(match.group(1)):04d}" if match else str(value)


def find_title(body_lines, fallback):
    in_fence = False
    for line in body_lines:
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("# "):
            return TITLE_PREFIX.sub("", line[2:].strip())
    return fallback


def load_vocab(path):
    """語彙表の表のうち、見出し行の 1 列目が topic である表の行だけを語彙にする。"""
    vocab = []
    in_topic_table = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not TABLE_ROW.match(line):
                in_topic_table = False
                continue
            first_cell = line.strip("|").split("|", 1)[0].strip().strip("`")
            if first_cell == "topic":
                in_topic_table = True
                continue
            if not in_topic_table or set(first_cell) <= set("-: "):
                continue
            match = VOCAB_ROW.match(line)
            if match:
                vocab.append((match.group(1), match.group(2)))
    return vocab


def load_adrs(adr_dir):
    adrs, warnings = [], []
    for name in sorted(os.listdir(adr_dir)):
        match = ADR_FILE.match(name)
        if not match:
            if name.endswith(".md") and name not in (INDEX_NAME,) + HUMAN_DOCS:
                warnings.append(f"{name}: ファイル名が NNNN-*.md でないため索引の対象外")
            continue
        with open(os.path.join(adr_dir, name), encoding="utf-8") as f:
            text = f.read()
        fm, body = split_frontmatter(text)
        links = {key: [normalize_number(v) for v in _as_numbers((fm or {}).get(key))] for key in LINK_KEYS}
        adrs.append(Adr(
            num=match.group(1),
            filename=name,
            title=find_title(body, name),
            fm=fm,
            status=str((fm or {}).get("status", "")),
            topics=_as_list((fm or {}).get("topic")),
            links=links,
        ))
    return adrs, warnings


def validate(adrs, vocab_names):
    errors, warnings = [], []
    by_num = {}
    seen = {}
    for a in adrs:
        seen.setdefault(a.num, []).append(a)
    for a in adrs:
        a.label = f"ADR-{a.num} ({a.filename})" if len(seen[a.num]) > 1 else f"ADR-{a.num}"
        if a.num in by_num:
            errors.append(f"{a.label}: 連番が重複（{by_num[a.num].filename} と {a.filename}）")
        by_num[a.num] = a
    for a in adrs:
        if a.fm is None:
            errors.append(f"{a.label}: frontmatter が無い（先頭の `---` … `---` を置く）")
            continue
        for key in REQUIRED_TEXT:
            value = a.fm.get(key)
            if value in (None, "", []):
                errors.append(f"{a.label}: {key} が無い")
        if a.fm.get("type") not in (None, "", [], "adr"):
            errors.append(f"{a.label}: type '{a.fm.get('type')}' は不正（adr）")
        if isinstance(a.fm.get("updated"), str) and a.fm.get("updated") and not DATE.match(a.fm["updated"]):
            errors.append(f"{a.label}: updated '{a.fm['updated']}' は YYYY-MM-DD でない")
        if not a.status:
            errors.append(f"{a.label}: status が無い（{' / '.join(STATUSES)} のいずれか）")
        elif a.status not in STATUSES:
            errors.append(f"{a.label}: status '{a.status}' は不正（{' / '.join(STATUSES)} のいずれか）")
        for key in a.fm:
            if key not in KNOWN_KEYS:
                near = difflib.get_close_matches(key, KNOWN_KEYS, n=1, cutoff=0.8)
                hint = f"'{near[0]}' の誤り？" if near else "独自キーなら無視してよい"
                warnings.append(f"{a.label}: 未知のキー '{key}'（{hint}）")
        if not a.topics:
            errors.append(f"{a.label}: topic が無い")
        for t in a.topics:
            if t not in vocab_names:
                errors.append(f"{a.label}: topic '{t}' は語彙表（{TERMS_NAME}）に無い")
        for key in LINK_KEYS:
            if a.num in a.links[key]:
                errors.append(f"{a.label}: {key} が自分自身を指している")
        for fwd, back in RELATIONS:
            for target in a.links[fwd]:
                other = by_num.get(target)
                if other is None:
                    errors.append(f"{a.label}: {fwd} の ADR-{target} が存在しない")
                elif target != a.num and a.num not in other.links[back]:
                    errors.append(f"{other.label}: {back} に {a.num} が無い（{a.label} が {fwd} を宣言）")
            for target in a.links[back]:
                other = by_num.get(target)
                if other is None:
                    errors.append(f"{a.label}: {back} の ADR-{target} が存在しない")
                elif target != a.num and a.num not in other.links[fwd]:
                    errors.append(f"{other.label}: {fwd} に {a.num} が無い（{a.label} が {back} を宣言）")
        for target in a.links["considered"]:
            if target not in by_num:
                errors.append(f"{a.label}: considered の ADR-{target} が存在しない")
        if a.links["superseded_by"] and a.status != "superseded":
            errors.append(f"{a.label}: superseded_by があるが status が '{a.status}'（superseded にする）")
        if a.status == "superseded" and not a.links["superseded_by"]:
            errors.append(f"{a.label}: status が superseded だが superseded_by が空")

    active = [a for a in adrs if a.fm is not None and a.status in ACTIVE_STATUSES]
    for a in active:
        covered = {n for key in COVERAGE_KEYS for n in a.links[key]}
        for b in active:
            if b.num < a.num and b.num not in covered and set(a.topics) & set(b.topics):
                errors.append(f"{a.label}: 同 topic の ADR-{b.num} を読んだ宣言が無い（supersedes / amends / considered のいずれかに書く）")

    counts = {}
    for a in active:
        for t in a.topics:
            if t in vocab_names:
                counts[t] = counts.get(t, 0) + 1
    for t, n in counts.items():
        if n > SKEW_HIGH:
            warnings.append(f"topic '{t}' の有効 ADR が {n} 本（{SKEW_HIGH} 本超。分割を検討）")
    return errors, warnings


def _relations(a):
    return [f"{key} {', '.join(a.links[key])}" for key in ("supersedes", "amends", "amended_by") if a.links[key]]


def render(adrs, vocab, terms_rel):
    lines = [
        "<!-- generated by adr_index.py; do not edit. Regenerate: python3 <aidd_root>/shared/scripts/adr_index.py <adr_dir>（shared/rules/common.md 参照） -->",
        "# ADR 索引（有効な決定）",
        "",
        f"有効 = status が {' / '.join(ACTIVE_STATUSES)}。topic の意味は語彙表（{terms_rel}）を参照。失効した ADR は末尾に置く。",
    ]
    active = [a for a in adrs if a.status in ACTIVE_STATUSES]
    for name, desc in vocab:
        members = [a for a in active if name in a.topics]
        if not members:
            continue
        lines += ["", f"## {name} · {desc}" if desc else f"## {name}", ""]
        for a in members:
            summary = str(a.fm.get("summary", "")).strip()
            lines.append(
                f"- [ADR-{a.num} {a.title}]({a.filename}): {summary} · {a.status}"
                + "".join(f" · {p}" for p in _relations(a))
            )
    retired = [a for a in adrs if a.status not in ACTIVE_STATUSES]
    if retired:
        lines += ["", "## 失効", ""]
        for a in retired:
            tail = f"superseded by {', '.join(a.links['superseded_by'])}" if a.links["superseded_by"] else a.status
            lines.append(f"- [ADR-{a.num} {a.title}]({a.filename}) · {tail}")
    return "\n".join(lines) + "\n"


def run(adr_dir, terms=None, write=False):
    result = Result()
    if not os.path.isdir(adr_dir):
        what = "ディレクトリではない" if os.path.exists(adr_dir) else "存在しない"
        result.errors.append(f"ADR ディレクトリ {adr_dir} が{what}（リポジトリルートを cwd にしてパスを確認する）")
        return result
    try:
        entries = set(os.listdir(adr_dir))
    except OSError as e:
        result.errors.append(f"ADR ディレクトリ {adr_dir} を読めない（{e.strerror}）")
        return result
    terms_file = terms if terms is not None else os.path.join(os.path.dirname(os.path.abspath(adr_dir)), TERMS_NAME)
    if not os.path.isfile(terms_file):
        if terms is not None:
            result.errors.append(f"--terms の語彙表 '{terms_file}' が無いかファイルではない")
        elif INDEX_NAME in entries:
            result.errors.append(f"{INDEX_NAME} があるのに語彙表 {terms_file} が無い（移行済みなら語彙表を戻す）")
        elif os.path.exists(terms_file):
            result.errors.append(f"語彙表 {terms_file} がファイルではない")
        else:
            result.warnings.append(f"語彙表 {terms_file} も {INDEX_NAME} も無い。未移行として照合と索引生成を省略する")
            result.skipped = True
        return result
    try:
        vocab = load_vocab(terms_file)
    except OSError as e:
        result.errors.append(f"語彙表 {terms_file} を読めない（{e.strerror}）")
        return result
    if not vocab:
        result.errors.append(f"語彙表 {terms_file} に topic 表が無い（見出し 1 列目が `topic` の表を置く）")
        return result
    adrs, result.warnings = load_adrs(adr_dir)
    errors, warnings = validate(adrs, [name for name, _ in vocab])
    result.errors = errors
    result.warnings += warnings
    if errors:
        return result
    result.index = render(adrs, vocab, os.path.relpath(terms_file, adr_dir))
    if write:
        with open(os.path.join(adr_dir, INDEX_NAME), "w", encoding="utf-8", newline="") as f:
            f.write(result.index)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("adr_dir")
    parser.add_argument("--terms", help=f"topic 語彙表のパス（既定: ADR_DIR の親の {TERMS_NAME}）")
    parser.add_argument("--check", action="store_true", help="INDEX.md を書かず、最新かどうかだけ検査する")
    args = parser.parse_args(argv)

    result = run(args.adr_dir, terms=args.terms, write=not args.check)
    for w in result.warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in result.errors:
        print(f"error: {e}", file=sys.stderr)
    if result.skipped:
        print("skipped: 未移行ディレクトリ")
        return 0
    if result.errors:
        return 1
    index_path = os.path.join(args.adr_dir, INDEX_NAME)
    if args.check:
        current = ""
        if os.path.exists(index_path):
            with open(index_path, encoding="utf-8", newline="") as f:
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
