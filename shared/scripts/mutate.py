#!/usr/bin/env python3
"""変異注入ハーネス（tdd-cycle §1 特性テスト / critical-gate の検出力確認）。

手作業の変異注入で繰り返した事故を、道具で起きなくする:
- 未コミットの差分がある状態で変異し、復元で実装を消した（git checkout が巻き込む）
- 置換対象が複数あり、別の箇所を書き換えて「生存」と誤報告した
- 構文エラーで実行不能になったのを「検出 0 件」と読み違えた
- 復元に失敗したまま次の変異を測った
- 実行中にプロセスが殺され、変異が作業ツリーに残った（退避がメモリにしか無かった）

保証すること:
- 作業ツリーが clean でなければ中止する（コミットできない状態では変異しない）
- 置換対象の出現数がちょうど 1 でなければ、その変異は「無効」
- 復元は注入前のバイト列を書き戻し、ハッシュ一致を検査する（git を使わない）
- 判定は「検出 / 生存 / 無効」の 3 値。テストの収集失敗・実行できなかったテスト（JUnit の <error>）・
  基準より増えた skipped・件数の減少は「無効」
- 変異を書くたびに更新時刻を使っていない秒へ進め、元に戻すときは更新時刻も戻す
  （更新時刻でキャッシュを判定するテストランナーに、古い結果を使わせないため）
- 注入前のバイト列は disk（一時ディレクトリ）にも退避し、殺されて残った変異は次の実行の冒頭で復元する
- 「無効」のときは結果ファイルとテストの出力をリポジトリの外へ退避し、備考にパスを書く（出所を後から追える）

テスト結果の形式:
  JUnit XML が標準（テストランナーの多くが出せる）。--test にはテストの実行コマンドを、
  --result-out にはそのコマンドが書く JUnit XML のパスを渡す。互換のため vitest の JSON
  （--reporter=json）も読める。形式は中身で見分ける。

使い方（1 件）:
  mutate.py --repo . --file src/a.ts --old 'x ?? y' --new 'x || y' \
            --test '<テストの実行コマンド。結果を JUnit XML で .mutate.xml に書かせる>' \
            --result-out .mutate.xml [--baseline-total 42] [--label M07]

テストランナー別の --test の例（実物で確認したもの）:
  vitest:  npx vitest run --reporter=junit --outputFile=.mutate.xml
  pytest:  pytest --junitxml=.mutate.xml
  ほかのランナーも、JUnit XML を書かせる設定があれば同じ形で使える

複数件は --spec で JSON 配列（各要素は file / old / new / label）。
出力は PR にそのまま貼れる Markdown の表の行。

終了コード:
  0  完走した（判定の内訳に依らない）
  3  作業ツリーに未コミットの差分がある（変異しない）
  4  復元後の内容が注入前と一致しない、または作業ツリーが clean でない（以後の測定を止めた）
  5  基準の実行（変異なし）が green でない（変異しない）
  6  前回の中断で残った退避コピーがあるが、今の内容が注入した変異と一致しない（戻さない）。
     今の内容を残すなら --discard-interrupted で退避コピーを捨てる
"""
from __future__ import annotations

import argparse
import hashlib
import math
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
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
        # ラベルや備考に | が入ると Markdown の表の列がずれる
        cell = lambda v: str(v).replace("|", "\\|")
        return f"| {cell(self.label)} | {self.verdict} | {self.failed} / {self.total} | {cell(self.note)} |"


class DirtyTree(Exception):
    pass


class UnsafeRecovery(Exception):
    """中断で残った退避コピーがあるが、今の内容が変異後と一致しない（人が編集した可能性がある）"""


def git_porcelain(repo: Path, ignore: Path | None = None) -> str:
    """未コミットの差分。テストランナーが書く結果ファイル（ignore）だけは差分と数えない。"""
    out = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, check=True,
    ).stdout
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if ignore is not None:
        # porcelain のパスはリポジトリのルート基準（--repo がサブディレクトリでも）
        top = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        try:
            rel = ignore.resolve().relative_to(Path(top).resolve()).as_posix()
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


def backup_path(repo: Path, rel: str) -> Path:
    """注入前のバイト列の退避先。リポジトリの外に置く（中に置くと clean 検査に引っかかる）"""
    key = sha256(f"{repo.resolve()}::{rel}".encode("utf-8"))[:16]
    d = Path(tempfile.gettempdir()) / "mutate-backup"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}.bak"


def keep_evidence(label: str, raw_json: bytes | None, proc) -> Path:
    """「無効」の出所を後から追えるよう、消す前の結果と出力をリポジトリの外へ退避する"""
    d = Path(tempfile.mkdtemp(prefix="mutate-invalid-"))
    safe = "".join(c if c.isalnum() else "_" for c in label)[:40] or "M"
    ext = "xml" if raw_json is not None and raw_json.lstrip().startswith(b"<") else "json"
    if raw_json is not None:
        (d / f"{safe}.{ext}").write_bytes(raw_json)
    if proc is not None:
        (d / f"{safe}.stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
        (d / f"{safe}.stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    return d / f"{safe}.{ext}" if raw_json is not None else d


def last_mtime_path(repo: Path, rel: str) -> Path:
    """このファイルに最後に付けた更新時刻（秒）。別の実行とも重ならないよう、実行をまたいで残す"""
    return backup_path(repo, rel).with_suffix(".lastmtime")


def bump_mtime(repo: Path, rel: str) -> None:
    """ファイルの更新時刻を、まだ使っていない新しい秒へ進める。

    更新時刻（秒）とサイズでキャッシュの有効性を判定するテストランナーは言語を問わずある
    （例: Python の .pyc）。長さが同じ変異を 1 秒以内に書き戻すと、古いキャッシュがそのまま
    使われ、変異の判定と次の基準の実行を誤らせる（ハッシュ検査・clean 検査では気づけない）。
    書き込みのたびに一度も使っていない秒を付ければ、どのキャッシュも作り直される。
    """
    state = last_mtime_path(repo, rel)
    try:
        last = int(state.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        last = 0
    t = max(math.ceil(time.time()) + 1, last + 1)
    os.utime(repo / rel, (t, t))
    state.write_text(str(t), encoding="utf-8")


def mutated_marker_path(repo: Path, rel: str) -> Path:
    """注入した変異後の内容のハッシュ。中断後の復元で、人の編集を上書きしないために使う"""
    return backup_path(repo, rel).with_suffix(".mutated")


def recover_interrupted(repo: Path, rel: str) -> bool:
    """前回の実行が殺されて残った変異を、退避コピーから戻す。戻したら True。

    今の内容が注入した変異と一致するときだけ戻す。一致しなければ、中断のあとに人が
    編集した可能性があるので戻さずに止める（その編集を古い内容で上書きしない）。
    """
    bak = backup_path(repo, rel)
    marker = mutated_marker_path(repo, rel)
    if not bak.exists():
        return False
    current = sha256((repo / rel).read_bytes())
    original = bak.read_bytes()
    if current == sha256(original):
        # 復元は済んでいて、退避の片づけの前に止まっていた
        pass
    elif marker.exists() and current == marker.read_text(encoding="utf-8").strip():
        (repo / rel).write_bytes(original)
        # 注入前の更新時刻は分からないので、使っていない秒へ進める（変異後の時刻と重ねない）
        bump_mtime(repo, rel)
    else:
        raise UnsafeRecovery(
            f"{rel}: 前回の中断で残った退避コピーがあるが、今の内容は注入した変異と一致しない。"
            f"中断のあとに編集された可能性があるので戻さない。退避コピー: {bak}。"
            f"今の内容を残すなら --discard-interrupted を付けて実行する"
        )
    bak.unlink()
    if marker.exists():
        marker.unlink()
    return True


def parse_results(path: Path) -> tuple[int, int, int, int] | None:
    """テスト結果から (failed, total, skipped, errors) を返す。読めなければ None。

    errors は「テストの失敗」でなく「実行できなかった」もの（JUnit XML の <error>。
    pytest は収集の失敗をこれで出す）。

    vitest の JSON（--reporter=json）と JUnit XML（vitest --reporter=junit・pytest --junitxml）を読む。
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if text.lstrip().startswith("<"):
        return parse_junit_xml(text)
    return parse_vitest_json(text)


def parse_junit_xml(text: str) -> tuple[int, int, int, int] | None:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    cases = list(root.iter("testcase"))
    failed = sum(1 for c in cases if c.find("failure") is not None)
    errors = sum(1 for c in cases if c.find("error") is not None)
    skipped = sum(1 for c in cases if c.find("skipped") is not None)
    # 収集段階で落ちたスイートは testcase を持たず、testsuite の errors 属性にだけ出ることがある
    suite_errors = sum(int(s.get("errors", "0") or 0) for s in root.iter("testsuite"))
    if not cases and suite_errors > 0:
        return None
    return failed, len(cases), skipped, errors


def parse_vitest_json(text: str) -> tuple[int, int, int, int] | None:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    total = int(data.get("numTotalTests", 0))
    failed = int(data.get("numFailedTests", 0))
    skipped = int(data.get("numPendingTests", 0)) + int(data.get("numTodoTests", 0))
    # 収集段階で落ちたファイルは numFailedTestSuites に出るが numTotalTests に乗らないことがある
    if int(data.get("numFailedTestSuites", 0)) > 0 and total == 0:
        return None
    return failed, total, skipped, 0


def run_one(
    repo: Path,
    rel: str,
    old: str,
    new: str,
    test_cmd: str,
    json_out: Path,
    baseline_total: int | None,
    label: str,
    baseline_skipped: int = 0,
) -> Result:
    if recover_interrupted(repo, rel):
        print(f"前回の中断で残っていた変異を復元した: {rel}", file=sys.stderr)
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
    bak = backup_path(repo, rel)
    marker = mutated_marker_path(repo, rel)
    mutated = text.replace(old, new, 1).encode("utf-8")
    original_times = (target.stat().st_atime_ns, target.stat().st_mtime_ns)
    raw_json: bytes | None = None
    proc = None
    try:
        bak.write_bytes(original)
        marker.write_text(sha256(mutated), encoding="utf-8")
        target.write_bytes(mutated)
        bump_mtime(repo, rel)
        if json_out.exists():
            json_out.unlink()
        proc = subprocess.run(test_cmd, shell=True, cwd=str(repo), capture_output=True, text=True)
        parsed = parse_results(json_out)
        if json_out.exists():
            raw_json = json_out.read_bytes()
    finally:
        target.write_bytes(original)
        # 中身と一緒に更新時刻も注入前に戻す（注入前の内容のキャッシュはそのまま正しい）
        os.utime(target, ns=original_times)
        if bak.exists():
            bak.unlink()
        if marker.exists():
            marker.unlink()
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

    def invalid(failed: int, total: int, reason: str) -> Result:
        return Result(label, INVALID, failed, total, f"{reason}。結果: {keep_evidence(label, raw_json, proc)}")

    if parsed is None:
        return invalid(0, 0, "テスト結果を読めない（収集失敗・構文エラー・出力ファイル無し）")
    failed, total, skipped, errors = parsed
    if total == 0:
        return invalid(failed, total, "テストが 1 件も実行されていない")
    if errors > 0:
        return invalid(failed, total, f"実行できなかったテストが {errors} 件（収集の失敗・構文エラーを含む）")
    if skipped > baseline_skipped:
        return invalid(failed, total, f"skipped が {skipped} 件（基準は {baseline_skipped} 件。実行不能を含む）")
    if baseline_total is not None and total < baseline_total:
        return invalid(failed, total, f"件数が基準 {baseline_total} を下回る")
    if failed == 0 and proc is not None and proc.returncode != 0:
        return invalid(failed, total, f"失敗 0 件だが終了コードが {proc.returncode}")
    if failed > 0:
        return Result(label, DETECTED, failed, total, "")
    return Result(label, SURVIVED, failed, total, "全件 green。等価変異か、検出力の欠落")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--test", required=True, help="テストの実行コマンド（結果を --result-out のパスへ JUnit XML で書かせる）")
    ap.add_argument("--result-out", "--json-out", dest="json_out", metavar="RESULT_OUT", required=True,
                    help="--test が書く結果ファイルのパス（JUnit XML。vitest の JSON も可）。--json-out は旧名")
    ap.add_argument("--baseline-total", type=int, default=None)
    ap.add_argument("--file")
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--label", default="M")
    ap.add_argument("--spec", help="JSON 配列のファイル。各要素: file / old / new / label")
    ap.add_argument("--discard-interrupted", action="store_true",
                    help="前回の中断で残った退避コピーを捨てて終わる（今の内容は変えない。exit 6 の後、手で直した内容を残すとき）")
    args = ap.parse_args(argv)

    # SIGTERM でも finally の復元を通す（SIGKILL は防げないので disk の退避で次回に戻す）
    def _interrupt(signum, frame):  # noqa: ARG001
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, _interrupt)

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

    if args.discard_interrupted:
        for rel in dict.fromkeys(s["file"] for s in specs):
            for p in (backup_path(repo, rel), mutated_marker_path(repo, rel)):
                if p.exists():
                    p.unlink()
                    print(f"退避コピーを捨てた（今の内容は変えていない）: {rel} {p}", file=sys.stderr)
        return 0

    # 中断で残った変異は clean 検査より先に戻す（先に検査すると、残った変異を差分と見て止まる）
    try:
        for rel in dict.fromkeys(s["file"] for s in specs):
            if recover_interrupted(repo, rel):
                print(f"前回の中断で残っていた変異を復元した: {rel}", file=sys.stderr)
    except UnsafeRecovery as e:
        print(f"中止: {e}", file=sys.stderr)
        return 6

    try:
        require_clean(repo, json_out)
    except DirtyTree as e:
        print(str(e), file=sys.stderr)
        return 3

    # 変異の前に、何も変えない状態で green かを確かめる。落ちているテストがあると、
    # どの変異も「検出」と判定されてしまう
    if json_out.exists():
        json_out.unlink()
    base = subprocess.run(args.test, shell=True, cwd=str(repo), capture_output=True, text=True)
    parsed = parse_results(json_out)
    if json_out.exists():
        json_out.unlink()
    if parsed is None or parsed[0] > 0 or parsed[3] > 0 or parsed[1] == 0 or base.returncode != 0:
        print(f"中止: 基準の実行（変異なし）が green でない: 結果={parsed} 終了コード={base.returncode}", file=sys.stderr)
        return 5
    baseline_total = args.baseline_total if args.baseline_total is not None else parsed[1]
    baseline_skipped = parsed[2]

    print("| 変異 | 判定 | 失敗 / 全件 | 備考 |")
    print("|---|---|---|---|")
    for i, s in enumerate(specs, 1):
        label = s.get("label") or f"M{i:02d}"
        try:
            r = run_one(repo, s["file"], s["old"], s["new"], args.test, json_out, baseline_total, label,
                        baseline_skipped)
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
