import tempfile
import unittest
from pathlib import Path

from sync_from_local import LEAK_PATTERNS, scan_leaks


class TestScanLeaks(unittest.TestCase):
    def test_blacklist_matches_spec(self):
        self.assertEqual(
            LEAK_PATTERNS,
            ["REDACTED", "REDACTED", "REDACTED", "REDACTED", "REDACTED-IP", "REDACTED-PATH"],
        )

    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins" / "demo").mkdir(parents=True)
            (repo / "plugins" / "demo" / "a.md").write_text("hello world", encoding="utf-8")
            (repo / "README.md").write_text("# store", encoding="utf-8")
            self.assertEqual(scan_leaks(repo), [])

    def test_leak_in_plugins_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins" / "demo").mkdir(parents=True)
            (repo / "plugins" / "demo" / "bad.md").write_text("pwd=REDACTED", encoding="utf-8")
            hits = scan_leaks(repo)
            self.assertEqual(len(hits), 1)
            self.assertIn("REDACTED", hits[0])
            self.assertIn("bad.md", hits[0])

    def test_leak_in_readme_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "README.md").write_text("contact REDACTED", encoding="utf-8")
            self.assertTrue(scan_leaks(repo))

    def test_scripts_dir_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "scripts").mkdir(parents=True)
            (repo / "scripts" / "sync_from_local.py").write_text('P = ["REDACTED"]', encoding="utf-8")
            self.assertEqual(scan_leaks(repo), [])

    def test_binary_file_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins").mkdir()
            (repo / "plugins" / "blob.bin").write_bytes(b"\x00\xff\xfe")
            self.assertEqual(scan_leaks(repo), [])


if __name__ == "__main__":
    unittest.main()
