#!/usr/bin/env python3
"""変異注入ハーネス（tdd-cycle §1 特性テスト / critical-gate の検出力確認）。

手作業の変異注入で繰り返した事故を、道具で起きなくする:
- 未コミットの差分がある状態で変異し、復元で実装を消した（git checkout が巻き込む）
- 置換対象が複数あり、別の箇所を書き換えて「生存」と誤報告した
- 構文エラーで実行不能になったのを「検出 0 件」と読み違えた
- 復元に失敗したまま次の変異を測った

保証すること:
- 作業ツリーが clean でなければ中止する（コミットできない状態では変異しない）
- 置換対象の出現数がちょうど 1 でなければ、その変異は「無効」
- 復元は注入前のバイト列を書き戻し、ハッシュ一致を検査する（git を使わない）
- 判定は「検出 / 生存 / 無効」の 3 値。テストの収集失敗・skipped・件数の減少は「無効」

使い方（1 件）:
  mutate.py --repo . --file src/a.ts --old 'x ?? y' --new 'x || y' \
            --test 'npx vitest run --reporter=json --outputFile=/tmp/vitest.json src/a.test.ts' \
            --json-out /tmp/vitest.json [--baseline-total 42] [--label M07]

複数件は --spec で JSON 配列（各要素は file / old / new / label）。
出力は PR にそのまま貼れる Markdown の表の行。終了コードは 0（全件が検出または等価として扱う判定に依らず、実行が完走したこと）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DETECTED = "検出"
SURVIVED = "生存"
INVALID = "無効"


@dataclass
class Result:
    label: str
    verdict: str
    failed: int
    total: int
    note: str

    def row(self) -> str:
        return f"| {self.label} | {self.verdict} | {self.failed} / {self.total} | {self.note} |"


class DirtyTree(Exception):
    pass


def git_porcelain(repo: Path, ignore: Path | None = None) -> str:
    """未コミットの差分。テストランナーが書く結果ファイル（ignore）だけは差分と数えない。"""
    out = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=True,
    ).stdout
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if ignore is not None:
        try:
            rel = ignore.resolve().relative_to(repo.resolve()).as_posix()
        except ValueError:
            rel = None
        if rel:
            lines = [ln for ln in lines if ln[3:].strip() != rel]
    return "\n".join(lines).strip()


def require_clean(repo: Path, ignore: Path | None = None) -> None:
    dirty = git_porcelain(repo, ignore)
    if dirty:
        raise DirtyTree(f"作業ツリーに未コミットの差分がある。コミットしてから変異する:\n{dirty}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_vitest_json(path: Path) -> tuple[int, int, int] | None:
    """(failed, total, skipped) を返す。読めなければ None。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    total = int(data.get("numTotalTests", 0))
    failed = int(data.get("numFailedTests", 0))
    skipped = int(data.get("numPendingTests", 0)) + int(data.get("numTodoTests", 0))
    # 収集段階で落ちたファイルは numFailedTestSuites に出るが numTotalTests に乗らないことがある
    if int(data.get("numFailedTestSuites", 0)) > 0 and total == 0:
        return None
    return failed, total, skipped


def run_one(
    repo: Path,
    rel: str,
    old: str,
    new: str,
    test_cmd: str,
    json_out: Path,
    baseline_total: int | None,
    label: str,
) -> Result:
    require_clean(repo, json_out)
    target = repo / rel
    original = target.read_bytes()
    text = original.decode("utf-8")
    n = text.count(old)
    if n != 1:
        return Result(label, INVALID, 0, 0, f"置換対象の出現数が {n}（1 でなければ注入しない）")
    if old == new:
        return Result(label, INVALID, 0, 0, "old と new が同一")

    before_hash = sha256(original)
    try:
        target.write_bytes(text.replace(old, new, 1).encode("utf-8"))
        if json_out.exists():
            json_out.unlink()
        subprocess.run(test_cmd, shell=True, cwd=str(repo), capture_output=True, text=True)
        parsed = parse_vitest_json(json_out)
    finally:
        target.write_bytes(original)
        # 結果ファイルを残すと git status に出て、次の測定や人の目を惑わせる
        if json_out.exists():
            json_out.unlink()

    after_hash = sha256(target.read_bytes())
    if after_hash != before_hash:
        # ここに来たら復元が壊れている。以後の測定を続けてはいけない
        raise RuntimeError(f"復元後のハッシュが一致しない: {rel}")
    dirty = git_porcelain(repo, json_out)
    if dirty:
        raise RuntimeError(f"復元後に作業ツリーが clean でない:\n{dirty}")

    if parsed is None:
        return Result(label, INVALID, 0, 0, "テスト結果を読めない（収集失敗・構文エラー・出力ファイル無し）")
    failed, total, skipped = parsed
    if total == 0:
        return Result(label, INVALID, failed, total, "テストが 1 件も実行されていない")
    if skipped > 0:
        return Result(label, INVALID, failed, total, f"skipped が {skipped} 件（実行不能を含む）")
    if baseline_total is not None and total < baseline_total:
        return Result(label, INVALID, failed, total, f"件数が基準 {baseline_total} を下回る")
    if failed > 0:
        return Result(label, DETECTED, failed, total, "")
    return Result(label, SURVIVED, failed, total, "全件 green。等価変異か、検出力の欠落")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--test", required=True, help="テスト実行コマンド（vitest の --reporter=json --outputFile を含める）")
    ap.add_argument("--json-out", required=True, help="--test が書く vitest の JSON のパス")
    ap.add_argument("--baseline-total", type=int, default=None)
    ap.add_argument("--file")
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--label", default="M")
    ap.add_argument("--spec", help="JSON 配列のファイル。各要素: file / old / new / label")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    json_out = Path(args.json_out)
    if not json_out.is_absolute():
        json_out = repo / json_out

    specs: list[dict]
    if args.spec:
        specs = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    else:
        if not (args.file and args.old is not None and args.new is not None):
            ap.error("--file / --old / --new か --spec を指定する")
        specs = [{"file": args.file, "old": args.old, "new": args.new, "label": args.label}]

    try:
        require_clean(repo, json_out)
    except DirtyTree as e:
        print(str(e), file=sys.stderr)
        return 3

    print("| 変異 | 判定 | 失敗 / 全件 | 備考 |")
    print("|---|---|---|---|")
    for i, s in enumerate(specs, 1):
        label = s.get("label") or f"M{i:02d}"
        try:
            r = run_one(repo, s["file"], s["old"], s["new"], args.test, json_out, args.baseline_total, label)
        except DirtyTree as e:
            print(str(e), file=sys.stderr)
            return 3
        except RuntimeError as e:
            print(f"中止: {e}", file=sys.stderr)
            return 4
        print(r.row())
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
