import json
import re
import tempfile
import unittest
from pathlib import Path

from sync_from_local import (CONTENT_EDITS, DEFAULT_AI_ROOT, PC_REPO_PATH,
                             clean_file, copy_tree, load_leak_patterns, scan_leaks, sync)

# 测试一律用假密值，真实账密不得出现在任何入库文件（含本测试）
FAKE_PATTERNS = ["FAKE-PWD-1", "FAKE-USER-2", "/Users/fakehome"]

SKIP_NOTE = "未填写前跳过本节，不得使用占位符尝试登录"

SAMPLE_CLAUDE_MD = f"""# PM 3.0 前端开发规范

## 工作流规则（重要）
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, invoke the Skill tool with `skill: "graphify"` before doing anything else.
- **gbrain** 遇到组件问题先查询 gbrain 中有没有要求和实现可以参考，然后比对是否可以参考复用

## 快速开始（必读）
- 技术栈 Vue 3

## 登录禅道
地址 http://zentao.example.internal
账号 fake-user-1
密码 FAKE-PWD-1
使用工具 playwright

## 登录系统测试
账号 fake-user-2
密码 FAKE-PWD-2
使用工具 playwright
"""

SAMPLE_PM_MOBILE = f"""## 铁律

2. **PC 端代码必须读真实文件**（PC 仓库默认：`{PC_REPO_PATH}`，页面文件由输入参数 `<pc-vue-path>` 指定），不得凭记忆或描述推断字段与流程。
"""


class TestLoadPatterns(unittest.TestCase):
    def test_loads_lines_skipping_comments_and_blank(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "patterns"
            p.write_text("# comment\n\nSECRET-A\n  SECRET-B  \n", encoding="utf-8")
            self.assertEqual(load_leak_patterns(p), ["SECRET-A", "SECRET-B"])

    def test_missing_file_falls_back_to_home(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "nope"
            self.assertEqual(load_leak_patterns(p), [str(Path.home())])


class TestScanLeaks(unittest.TestCase):
    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins" / "demo").mkdir(parents=True)
            (repo / "plugins" / "demo" / "a.md").write_text("hello world", encoding="utf-8")
            (repo / "README.md").write_text("# store", encoding="utf-8")
            self.assertEqual(scan_leaks(repo, FAKE_PATTERNS), [])

    def test_leak_in_plugins_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins" / "demo").mkdir(parents=True)
            (repo / "plugins" / "demo" / "bad.md").write_text("pwd=FAKE-PWD-1", encoding="utf-8")
            hits = scan_leaks(repo, FAKE_PATTERNS)
            self.assertEqual(len(hits), 1)
            self.assertIn("FAKE-PWD-1", hits[0])
            self.assertIn("bad.md", hits[0])

    def test_leak_in_readme_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "README.md").write_text("contact FAKE-USER-2", encoding="utf-8")
            self.assertTrue(scan_leaks(repo, FAKE_PATTERNS))

    def test_scripts_dir_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "scripts").mkdir(parents=True)
            (repo / "scripts" / "sync_from_local.py").write_text('P = ["FAKE-PWD-1"]', encoding="utf-8")
            self.assertEqual(scan_leaks(repo, FAKE_PATTERNS), [])

    def test_binary_file_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "plugins").mkdir()
            (repo / "plugins" / "blob.bin").write_bytes(b"\x00\xff\xfe")
            self.assertEqual(scan_leaks(repo, FAKE_PATTERNS), [])


class TestCleanContent(unittest.TestCase):
    def _clean(self, sample: str, rel: str) -> str:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.md"
            p.write_text(sample, encoding="utf-8")
            clean_file(p, CONTENT_EDITS[rel])
            return p.read_text(encoding="utf-8")

    def test_claude_md_credentials_blanked_for_user_fill(self):
        out = self._clean(SAMPLE_CLAUDE_MD, "plugins/pm3-frontend/templates/CLAUDE.md")
        for forbidden in ("FAKE-PWD-1", "FAKE-PWD-2", "fake-user-1", "fake-user-2",
                          "zentao.example.internal"):
            self.assertNotIn(forbidden, out)
        # 章节结构保留，账密置为占位符，由入项用户自行填写；带跳过说明防误用
        for placeholder in ("## 登录禅道", "## 登录系统测试", SKIP_NOTE,
                            "地址 <禅道地址>", "账号 <填写账号>", "密码 <填写密码>"):
            self.assertIn(placeholder, out)
        self.assertIn("使用工具 playwright", out)

    def test_claude_md_personal_refs_removed(self):
        out = self._clean(SAMPLE_CLAUDE_MD, "plugins/pm3-frontend/templates/CLAUDE.md")
        for forbidden in ("gbrain", "graphify"):
            self.assertNotIn(forbidden, out)
        self.assertIn("## 快速开始（必读）", out)  # 其余章节不受影响

    def test_pm_mobile_local_path_parameterized(self):
        out = self._clean(SAMPLE_PM_MOBILE,
                          "plugins/pm3-mobile/skills/pm-mobile-migration/SKILL.md")
        self.assertNotIn(str(PC_REPO_PATH), out)
        self.assertIn("PC 仓库根目录由调用方工作目录或输入参数确定", out)
        self.assertIn("<pc-vue-path>", out)

    def test_clean_file_returns_replacement_count(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.md"
            p.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")
            n = clean_file(p, CONTENT_EDITS["plugins/pm3-frontend/templates/CLAUDE.md"])
            self.assertGreaterEqual(n, 4)  # graphify + gbrain + 两个登录节

    def test_evals_json_paths_parameterized(self):
        sample = json.dumps(
            {"prompt": f"根据 @{DEFAULT_AI_ROOT}/工程管理/api/openapi.yaml 生成"},
            ensure_ascii=False)
        for rel in ("plugins/pm3-frontend/skills/generate-api/evals/evals.json",
                    "plugins/pm3-frontend/skills/generate-prd-guide/evals/evals.json"):
            with tempfile.TemporaryDirectory() as td:
                p = Path(td) / "evals.json"
                p.write_text(sample, encoding="utf-8")
                clean_file(p, CONTENT_EDITS[rel])
                out = p.read_text(encoding="utf-8")
                self.assertNotIn(str(DEFAULT_AI_ROOT), out, rel)
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
        defaults = dict(plan=FAKE_PLAN, edits={}, leak_patterns=FAKE_PATTERNS)
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
        (self.ai_root / "CLAUDE.md").write_text("x FAKE-PWD-1 y\n", encoding="utf-8")
        edits = {"plugins/pf/templates/CLAUDE.md": [(re.compile(r"FAKE-PWD-1"), "REDACTED")]}
        self._sync(edits=edits)
        self.assertIn("REDACTED", (self.repo / "plugins/pf/templates/CLAUDE.md").read_text(encoding="utf-8"))

    def test_exits_2_when_leak_not_editable(self):
        (self.global_root / "skills/mobile/SKILL.md").write_text("pwd=FAKE-PWD-1", encoding="utf-8")
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
