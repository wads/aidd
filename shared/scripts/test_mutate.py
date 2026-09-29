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

    def test_recovers_mutation_left_by_interrupted_run(self):
        # 前回のプロセスが殺されて変異が残った状態を再現する: 退避コピーがあり、対象は書き換わっている
        target = self.repo / "a.ts"
        original = target.read_bytes()
        bak = mutate.backup_path(self.repo, "a.ts")
        bak.write_bytes(original)
        target.write_bytes(original.replace(b"// MARK", b"// gone"))

        r = self.run_one("// MARK", "// gone")

        self.assertEqual(r.verdict, mutate.DETECTED)
        self.assertEqual(target.read_bytes(), original)
        self.assertFalse(bak.exists())

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
