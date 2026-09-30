import re
import tempfile
import unittest
from pathlib import Path

from sync_from_local import CONTENT_EDITS, LEAK_PATTERNS, clean_file, scan_leaks


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


SAMPLE_CLAUDE_MD = """# PM 3.0 前端开发规范

## 工作流规则（重要）
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.
- **gbrain** 遇到组件问题先查询 gbrain 中有没有要求和实现可以参考，然后比对是否可以参考复用

## 快速开始（必读）
- 技术栈 Vue 3

## 登录禅道
地址 http://REDACTED-IP152.128
账号 REDACTED
密码 REDACTED
使用工具 playwright

## 登录系统测试
账号 REDACTED
密码 REDACTED
使用工具 playwright
"""

SAMPLE_PM_MOBILE = """## 铁律

2. **PC 端代码必须读真实文件**（PC 仓库默认：`REDACTED-PATH/work/pm/pm3.0_frontend`，页面文件由输入参数 `<pc-vue-path>` 指定），不得凭记忆或描述推断字段与流程。
"""


class TestCleanContent(unittest.TestCase):
    def _clean(self, sample: str, rel: str) -> str:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.md"
            p.write_text(sample, encoding="utf-8")
            clean_file(p, CONTENT_EDITS[rel])
            return p.read_text(encoding="utf-8")

    def test_claude_md_credentials_sections_removed(self):
        out = self._clean(SAMPLE_CLAUDE_MD, "plugins/pm3-frontend/templates/CLAUDE.md")
        for forbidden in ("登录禅道", "登录系统测试", "REDACTED", "REDACTED",
                          "REDACTED", "REDACTED", "REDACTED-IP152.128", "playwright"):
            self.assertNotIn(forbidden, out)

    def test_claude_md_personal_refs_removed(self):
        out = self._clean(SAMPLE_CLAUDE_MD, "plugins/pm3-frontend/templates/CLAUDE.md")
        for forbidden in ("gbrain", "graphify"):
            self.assertNotIn(forbidden, out)
        self.assertIn("## 快速开始（必读）", out)  # 其余章节不受影响

    def test_pm_mobile_local_path_parameterized(self):
        out = self._clean(SAMPLE_PM_MOBILE,
                          "plugins/pm3-mobile/skills/pm-mobile-migration/SKILL.md")
        self.assertNotIn("REDACTED-PATH", out)
        self.assertIn("PC 仓库根目录由调用方工作目录或输入参数确定", out)
        self.assertIn("<pc-vue-path>", out)

    def test_clean_file_returns_replacement_count(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.md"
            p.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")
            n = clean_file(p, CONTENT_EDITS["plugins/pm3-frontend/templates/CLAUDE.md"])
            self.assertGreaterEqual(n, 4)


if __name__ == "__main__":
    unittest.main()
