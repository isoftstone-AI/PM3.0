import re
import tempfile
import unittest
from pathlib import Path

from sync_from_local import CONTENT_EDITS, LEAK_PATTERNS, clean_file, copy_tree, scan_leaks, sync


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

    def test_evals_json_paths_parameterized(self):
        sample = '{"prompt": "根据 @REDACTED-PATH/work/个人积累/ai/工程管理/api/openapi.yaml 生成"}'
        for rel in ("plugins/pm3-frontend/skills/generate-api/evals/evals.json",
                    "plugins/pm3-frontend/skills/generate-prd-guide/evals/evals.json"):
            with tempfile.TemporaryDirectory() as td:
                p = Path(td) / "evals.json"
                p.write_text(sample, encoding="utf-8")
                clean_file(p, CONTENT_EDITS[rel])
                out = p.read_text(encoding="utf-8")
                self.assertNotIn("REDACTED-PATH", out, rel)
                self.assertIn("<ai-workspace>", out, rel)


def make_fake_source(ai_root: Path, global_root: Path):
    (ai_root / "skills" / "demo").mkdir(parents=True)
    (ai_root / "skills" / "demo" / "SKILL.md").write_text("v1", encoding="utf-8")
    (ai_root / "skills" / "demo" / "temp").mkdir()
    (ai_root / "skills" / "demo" / "temp" / "junk.md").write_text("junk", encoding="utf-8")
    (ai_root / "skills" / "demo" / ".DS_Store").write_bytes(b"\x00")
    (ai_root / "skills" / "demo" / "SKILL.md.bak").write_text("old", encoding="utf-8")
    (ai_root / "CLAUDE.md").write_text("# rules\n", encoding="utf-8")
    (global_root / "skills" / "mobile").mkdir(parents=True)
    (global_root / "skills" / "mobile" / "SKILL.md").write_text("mobile", encoding="utf-8")


FAKE_PLAN = [
    ("skills/demo", "plugins/pf/skills/demo", "ai", frozenset({"temp"})),
    ("CLAUDE.md", "plugins/pf/templates/CLAUDE.md", "ai", frozenset()),
    ("skills/mobile", "plugins/pm/skills/mobile", "global", frozenset()),
]


class TestSync(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        base = Path(self._td.name)
        self.ai_root = base / "ai"
        self.global_root = base / "global"
        self.repo = base / "repo"
        make_fake_source(self.ai_root, self.global_root)

    def tearDown(self):
        self._td.cleanup()

    def _sync(self, **kw):
        defaults = dict(plan=FAKE_PLAN, edits={})
        defaults.update(kw)
        return sync(self.ai_root, self.global_root, self.repo, **defaults)

    def test_copies_plan_and_excludes(self):
        self._sync()
        demo = self.repo / "plugins/pf/skills/demo"
        self.assertTrue((demo / "SKILL.md").exists())
        self.assertFalse((demo / "temp").exists())
        self.assertFalse((demo / ".DS_Store").exists())
        self.assertFalse((demo / "SKILL.md.bak").exists())
        self.assertTrue((self.repo / "plugins/pf/templates/CLAUDE.md").exists())
        self.assertTrue((self.repo / "plugins/pm/skills/mobile/SKILL.md").exists())

    def test_full_rebuild_removes_stale(self):
        self._sync()
        stale = self.repo / "plugins/pf/skills/demo/stale.md"
        stale.write_text("old", encoding="utf-8")
        (self.ai_root / "skills/demo/SKILL.md").write_text("v2", encoding="utf-8")
        self._sync()
        self.assertFalse(stale.exists())
        self.assertIn("v2", (self.repo / "plugins/pf/skills/demo/SKILL.md").read_text(encoding="utf-8"))

    def test_applies_content_edits(self):
        (self.ai_root / "CLAUDE.md").write_text("x REDACTED y\n", encoding="utf-8")
        edits = {"plugins/pf/templates/CLAUDE.md": [(re.compile(r"REDACTED"), "REDACTED")]}
        self._sync(edits=edits)
        self.assertIn("REDACTED", (self.repo / "plugins/pf/templates/CLAUDE.md").read_text(encoding="utf-8"))

    def test_exits_2_when_leak_not_editable(self):
        (self.global_root / "skills/mobile/SKILL.md").write_text("pwd=REDACTED", encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            self._sync()
        self.assertEqual(cm.exception.code, 2)

    def test_missing_source_raises(self):
        (self.ai_root / "skills/demo").rename(self.ai_root / "skills/demo-bak")
        with self.assertRaises(FileNotFoundError):
            self._sync()

    def test_copy_tree_removes_existing_dst(self):
        dst = self.repo / "dst"
        dst.mkdir(parents=True)
        (dst / "old.txt").write_text("old", encoding="utf-8")
        src = self.ai_root / "skills/demo"
        copy_tree(src, dst, frozenset())
        self.assertFalse((dst / "old.txt").exists())
        self.assertTrue((dst / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
