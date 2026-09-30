"""mutate.py の振る舞いを保証する。

保証すること（AAR 2026-09-29 の事故を道具で起きなくする）:
- 未コミットの差分があれば注入しない（コミットできない状態で変異して復元で実装を消した事故）
- 置換対象の出現数が 1 でなければ「無効」（別の箇所を書き換えて生存と誤報告した事故）
- 実行不能（収集失敗・skipped・件数減）は「無効」であって「検出」ではない（構文エラーを検出 0 件と読んだ事故）
- 復元は注入前のバイト列に戻り、作業ツリーが clean に戻る
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
import mutate  # noqa: E402

# 偽のテストランナー: 対象ファイルに MARK があれば pass、無ければ fail を vitest 風 JSON で書く。
# 環境変数で「収集失敗」「skipped」も再現できる。
FAKE_RUNNER = textwrap.dedent("""\
    import json, os, sys
    src = open(sys.argv[1], encoding="utf-8").read()
    out = sys.argv[2]
    mode = os.environ.get("FAKE_MODE", "")
    if mode == "crash":
        data = {"numTotalTests": 0, "numFailedTests": 0, "numFailedTestSuites": 1}
    elif mode == "skipped":
        data = {"numTotalTests": 3, "numFailedTests": 0, "numPendingTests": 3}
    elif mode.startswith("junit"):
        ok = "MARK" in src
        cases = ['<testcase name="t1"/>', '<testcase name="t2"/>']
        if mode == "junit-skipped":
            cases.append('<testcase name="t3"><skipped/></testcase>')
        elif mode == "junit-base-skip":
            # 基準から skip が 1 件ある。変異では別のテストが落ちる
            cases = ['<testcase name="t1"/>' if ok else '<testcase name="t1"><failure/></testcase>',
                     '<testcase name="t2"/>', '<testcase name="t3"><skipped/></testcase>']
        elif mode == "junit-error":
            cases.append('<testcase name="t3"><error message="boom"/></testcase>')
        else:
            cases.append('<testcase name="t3"/>' if ok else '<testcase name="t3"><failure message="x"/></testcase>')
        open(out, "w").write('<?xml version="1.0"?><testsuites><testsuite name="s">' + "".join(cases) + "</testsuite></testsuites>")
        sys.exit(0)
    elif mode == "exit1":
        open(out, "w").write(json.dumps({"numTotalTests": 3, "numFailedTests": 0}))
        sys.exit(1)
    else:
        ok = "MARK" in src
        data = {"numTotalTests": 3, "numFailedTests": 0 if ok else 1}
    open(out, "w").write(json.dumps(data))
    """)


class MutateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = Path(self.tmp)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "t"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "commit.gpgsign", "false"], check=True)
        (self.repo / "a.ts").write_text("const v = x ?? y; // MARK\n", encoding="utf-8")
        (self.repo / "runner.py").write_text(FAKE_RUNNER, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-q", "-m", "init"], check=True)
        self.json_out = self.repo / "out.json"
        self.test_cmd = f"{sys.executable} runner.py a.ts {self.json_out}"

    def run_one(self, old, new, **kw):
        return mutate.run_one(self.repo, "a.ts", old, new, self.test_cmd, self.json_out, kw.get("baseline"), "M1")

    def test_detects_when_tests_fail(self):
        r = self.run_one("// MARK", "// gone")
        self.assertEqual(r.verdict, mutate.DETECTED)
        self.assertEqual((r.failed, r.total), (1, 3))

    def test_survives_when_tests_stay_green(self):
        r = self.run_one("x ?? y", "x || y")  # MARK は残るので偽ランナーは pass
        self.assertEqual(r.verdict, mutate.SURVIVED)

    def test_invalid_when_occurrence_count_is_not_one(self):
        (self.repo / "a.ts").write_text("x ?? y\nx ?? y // MARK\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qam", "two"], check=True)
        r = self.run_one("x ?? y", "x || y")
        self.assertEqual(r.verdict, mutate.INVALID)
        self.assertIn("出現数が 2", r.note)

    def test_refuses_dirty_tree(self):
        (self.repo / "a.ts").write_text("uncommitted\n", encoding="utf-8")
        with self.assertRaises(mutate.DirtyTree):
            self.run_one("uncommitted", "x")

    def test_restores_bytes_and_clean_tree(self):
        before = (self.repo / "a.ts").read_bytes()
        self.run_one("// MARK", "// gone")
        self.assertEqual((self.repo / "a.ts").read_bytes(), before)
        # 結果ファイルも残さない（除外なしの git status が空）
        self.assertFalse(self.json_out.exists())
        self.assertEqual(mutate.git_porcelain(self.repo), "")

    def test_collection_failure_is_invalid_not_detected(self):
        os.environ["FAKE_MODE"] = "crash"
        try:
            r = self.run_one("// MARK", "// gone")
        finally:
            del os.environ["FAKE_MODE"]
        self.assertEqual(r.verdict, mutate.INVALID)

    def test_skipped_is_invalid(self):
        os.environ["FAKE_MODE"] = "skipped"
        try:
            r = self.run_one("// MARK", "// gone")
        finally:
            del os.environ["FAKE_MODE"]
        self.assertEqual(r.verdict, mutate.INVALID)

    def test_invalid_keeps_the_result_outside_the_repo(self):
        # 「無効」の出所を後から追えるよう、消す前の結果を退避して備考にパスを書く
        os.environ["FAKE_MODE"] = "skipped"
        try:
            r = self.run_one("// MARK", "// gone")
        finally:
            del os.environ["FAKE_MODE"]
        kept = Path(r.note.split("結果: ")[1].strip())
        self.assertTrue(kept.exists())
        self.assertFalse(str(kept).startswith(str(self.repo)))
        self.assertEqual(json.loads(kept.read_text())["numPendingTests"], 3)
        self.assertFalse(self.json_out.exists())

    def test_total_below_baseline_is_invalid(self):
        r = self.run_one("// MARK", "// gone", baseline=10)
        self.assertEqual(r.verdict, mutate.INVALID)
        self.assertIn("基準 10", r.note)

    def cli(self, *extra, test_cmd=None, spec=None):
        spec = spec or [{"file": "a.ts", "old": "// MARK", "new": "// gone", "label": "M-A"}]
        path = Path(tempfile.mkdtemp()) / "spec.json"
        path.write_text(json.dumps(spec), encoding="utf-8")
        return subprocess.run(
            [sys.executable, mutate.__file__, "--repo", str(self.repo), "--test", test_cmd or self.test_cmd,
             "--json-out", str(self.json_out), "--spec", str(path), *extra],
            capture_output=True, text=True,
        )

    def interrupt(self):
        # 変異を入れたテストの実行中にハーネス自身を SIGKILL する（finally も走らない本物の中断）。
        # 変異の前の基準の実行では止めない
        self.cli(test_cmd=f'grep -q "// gone" a.ts && kill -9 $PPID; {self.test_cmd}')
        self.assertIn("// gone", (self.repo / "a.ts").read_text())

    def test_cli_recovers_a_mutation_left_by_a_killed_run(self):
        original = (self.repo / "a.ts").read_bytes()
        self.interrupt()

        proc = self.cli()

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| M-A | 検出 | 1 / 3 |", proc.stdout)
        self.assertEqual((self.repo / "a.ts").read_bytes(), original)

    def test_cli_does_not_overwrite_edits_made_after_a_killed_run(self):
        self.interrupt()
        edited = "const v = 2; // MARK edited by hand\n"
        (self.repo / "a.ts").write_text(edited, encoding="utf-8")

        proc = self.cli()

        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((self.repo / "a.ts").read_text(encoding="utf-8"), edited)
        self.assertIn("戻さない", proc.stderr)

    def test_cli_refuses_when_the_baseline_is_not_green(self):
        (self.repo / "a.ts").write_text("const v = 1; // no marker\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qam", "red"], check=True)

        proc = self.cli(spec=[{"file": "a.ts", "old": "const v = 1", "new": "const v = 2", "label": "M-A"}])

        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("| M-A |", proc.stdout)
        self.assertIn("基準", proc.stderr)

    def test_nonzero_exit_without_failures_is_invalid(self):
        os.environ["FAKE_MODE"] = "exit1"
        try:
            r = self.run_one("// MARK", "// gone")
        finally:
            del os.environ["FAKE_MODE"]
        self.assertEqual(r.verdict, mutate.INVALID)

    def test_backup_is_on_disk_while_mutated(self):
        # 実行中に殺されても復元できるよう、退避は disk に置く
        seen = Path(tempfile.mkdtemp()) / "seen.txt"
        runner = self.repo / "runner.py"
        runner.write_text(
            FAKE_RUNNER + textwrap.dedent(f"""\
                import pathlib
                p = pathlib.Path({str(mutate.backup_path(self.repo, "a.ts"))!r})
                open({str(seen)!r}, "w").write("yes" if p.exists() else "no")
                """),
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qam", "runner"], check=True)

        self.run_one("// MARK", "// gone")

        self.assertEqual(seen.read_text(), "yes")

    def test_label_with_a_pipe_does_not_break_the_table(self):
        proc = self.cli(spec=[{"file": "a.ts", "old": "// MARK", "new": "// gone", "label": "a ?? b | c"}])

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| a ?? b \\| c | 検出 |", proc.stdout)

    def test_repo_given_as_a_subdirectory_still_ignores_the_result_file(self):
        (self.repo / "sub").mkdir()
        (self.repo / "sub" / "b.ts").write_text("const w = 1; // MARK\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "sub"], check=True)
        out = self.repo / "sub" / "out.json"
        path = Path(tempfile.mkdtemp()) / "spec.json"
        path.write_text(json.dumps([{"file": "b.ts", "old": "// MARK", "new": "// gone", "label": "S"}]), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, mutate.__file__, "--repo", str(self.repo / "sub"),
             "--test", f"{sys.executable} ../runner.py b.ts {out}", "--json-out", str(out), "--spec", str(path)],
            capture_output=True, text=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| S | 検出 |", proc.stdout)

    def junit(self, mode, old="// MARK", new="// gone"):
        os.environ["FAKE_MODE"] = mode
        try:
            return self.run_one(old, new)
        finally:
            del os.environ["FAKE_MODE"]

    def test_junit_xml_detects_a_failing_testcase(self):
        r = self.junit("junit")
        self.assertEqual((r.verdict, r.failed, r.total), (mutate.DETECTED, 1, 3))

    def test_junit_xml_survives_when_all_testcases_pass(self):
        r = self.junit("junit", old="x ?? y", new="x || y")
        self.assertEqual((r.verdict, r.failed, r.total), (mutate.SURVIVED, 0, 3))

    def test_junit_xml_skipped_testcase_is_invalid(self):
        self.assertEqual(self.junit("junit-skipped", old="x ?? y", new="x || y").verdict, mutate.INVALID)

    def test_junit_xml_error_is_invalid_not_detected(self):
        # pytest は収集の失敗（構文エラーの変異など）を <error> で出す。テストの失敗と区別する
        r = self.junit("junit-error", old="x ?? y", new="x || y")
        self.assertEqual(r.verdict, mutate.INVALID)

    def test_skipped_tests_in_the_baseline_do_not_block(self):
        # 基準から skip があるプロジェクトでも使える。無効になるのは skip が基準より増えたときだけ
        os.environ["FAKE_MODE"] = "junit-base-skip"
        try:
            proc = self.cli()
        finally:
            del os.environ["FAKE_MODE"]
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| M-A | 検出 | 1 / 3 |", proc.stdout)

    def test_a_runner_that_caches_by_mtime_and_size_does_not_mislead_the_verdict(self):
        # 更新時刻（秒）とサイズで結果をキャッシュするランナーは言語を問わずある（Python の .pyc など）。
        # 長さが同じ変異を 1 秒以内に書き戻すと、古いキャッシュが使われて判定を誤る
        (self.repo / ".gitignore").write_text(".cache.json\n", encoding="utf-8")
        (self.repo / "calc.txt").write_text("a + b\n", encoding="utf-8")
        (self.repo / "cacherunner.py").write_text(textwrap.dedent("""\
            import json, os, sys
            st = os.stat("calc.txt")
            key = f"{int(st.st_mtime)}:{st.st_size}"
            cache = json.load(open(".cache.json")) if os.path.exists(".cache.json") else {}
            if key not in cache:
                cache[key] = open("calc.txt").read().strip() == "a + b"
                json.dump(cache, open(".cache.json", "w"))
            ok = cache[key]
            case = '<testcase name="t"/>' if ok else '<testcase name="t"><failure/></testcase>'
            open(sys.argv[1], "w").write("<testsuites><testsuite>" + case + "</testsuite></testsuites>")
            """), encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "cache"], check=True)
        spec = [{"file": "calc.txt", "old": "a + b", "new": new, "label": f"K{i}"}
                for i, new in enumerate(["a - b", "a * b", "a - b"])]
        out = self.repo / "r.xml"
        before = (self.repo / "calc.txt").stat().st_mtime_ns

        for _ in range(3):
            path = Path(tempfile.mkdtemp()) / "spec.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, mutate.__file__, "--repo", str(self.repo),
                 "--test", f"{sys.executable} cacherunner.py {out}", "--result-out", str(out), "--spec", str(path)],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.count("| 検出 |"), 3, proc.stdout)

        # 元に戻したファイルは中身だけでなく更新時刻も注入前のまま
        self.assertEqual((self.repo / "calc.txt").stat().st_mtime_ns, before)

    def test_python_bytecode_cache_does_not_mislead_the_verdict(self):
        # 長さが同じ変異を 1 秒以内に書き戻すと、Python は更新時刻とサイズで有効と見なした
        # 古い .pyc を使い、変異の判定と次の基準の実行を誤らせる
        (self.repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        (self.repo / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
        (self.repo / "pyrunner.py").write_text(textwrap.dedent("""\
            import sys
            sys.path.insert(0, ".")
            from calc import add
            ok = add(2, 3) == 5
            case = '<testcase name="t"/>' if ok else '<testcase name="t"><failure/></testcase>'
            open(sys.argv[1], "w").write("<testsuites><testsuite>" + case + "</testsuite></testsuites>")
            """), encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "py"], check=True)
        spec = [{"file": "calc.py", "old": "a + b", "new": new, "label": f"P{i}"}
                for i, new in enumerate(["a - b", "a * b", "a - b"])]
        out = self.repo / "r.xml"

        for _ in range(3):
            path = Path(tempfile.mkdtemp()) / "spec.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, mutate.__file__, "--repo", str(self.repo),
                 "--test", f"{sys.executable} pyrunner.py {out}", "--result-out", str(out), "--spec", str(path)],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.count("| 検出 |"), 3, proc.stdout)

    def test_discard_interrupted_keeps_the_edit_and_removes_the_backup(self):
        self.interrupt()
        edited = "const v = 3; // MARK kept\n"
        (self.repo / "a.ts").write_text(edited, encoding="utf-8")

        proc = self.cli("--discard-interrupted")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((self.repo / "a.ts").read_text(encoding="utf-8"), edited)
        self.assertFalse(mutate.backup_path(self.repo, "a.ts").exists())

    def test_a_leftover_result_file_in_a_subdirectory_repo_is_not_a_diff(self):
        (self.repo / "sub").mkdir()
        (self.repo / "sub" / "b.ts").write_text("const w = 1; // MARK\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "sub"], check=True)
        out = self.repo / "sub" / "out.json"
        out.write_text("{}", encoding="utf-8")  # 前回の実行の残り
        path = Path(tempfile.mkdtemp()) / "spec.json"
        path.write_text(json.dumps([{"file": "b.ts", "old": "// MARK", "new": "// gone", "label": "S"}]), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, mutate.__file__, "--repo", str(self.repo / "sub"),
             "--test", f"{sys.executable} ../runner.py b.ts {out}", "--result-out", str(out), "--spec", str(path)],
            capture_output=True, text=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| S | 検出 |", proc.stdout)

    def test_cli_prints_markdown_rows(self):
        # spec はリポジトリの外に置く（中に置くとハーネスが「未コミットの差分」として正しく拒否する）
        spec = Path(tempfile.mkdtemp()) / "spec.json"
        spec.write_text(json.dumps([
            {"file": "a.ts", "old": "// MARK", "new": "// gone", "label": "M-A"},
            {"file": "a.ts", "old": "x ?? y", "new": "x || y", "label": "M-B"},
        ]), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, mutate.__file__, "--repo", str(self.repo), "--test", self.test_cmd,
             "--json-out", str(self.json_out), "--spec", str(spec)],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| M-A | 検出 | 1 / 3 |", proc.stdout)
        self.assertIn("| M-B | 生存 | 0 / 3 |", proc.stdout)


if __name__ == "__main__":
    unittest.main()
