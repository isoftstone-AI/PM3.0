#!/usr/bin/env python3
"""Sync personal Claude assets into the PM3.0 marketplace repo.

Real run (defaults):  python3 scripts/sync_from_local.py
Test-only module functions are unit-tested in test_sync_from_local.py.

泄漏扫描黑名单不入库：维护者在 scripts/leak_patterns.local（git 忽略）维护
真实值，仓库只提交 leak_patterns.example 示例。
"""
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PATTERNS_LOCAL = SCRIPT_DIR / "leak_patterns.local"
PATTERNS_EXAMPLE = SCRIPT_DIR / "leak_patterns.example"

# 全仓扫描（含 scripts/）：脚本与测试已不含真实值，examples 为示例值；
# 不设排除区，未来任何文件（含维护脚本）混入真实密钥都会被闸门拦下
SCAN_TARGETS = ["plugins", "README.md", "docs", ".claude-plugin", "scripts"]

HOME = Path.home()
DEFAULT_AI_ROOT = HOME / "work" / "个人积累" / "ai"
DEFAULT_GLOBAL_ROOT = HOME / ".claude"
DEFAULT_REPO = Path(__file__).resolve().parent.parent
PC_REPO_PATH = HOME / "work" / "pm" / "pm3.0_frontend"

# 内容清洗：仓库内相对路径 -> [(编译正则, 替换文本), ...]
# 涉及本机路径的正则一律由 HOME 运行时构造，不在代码里写明文
CONTENT_EDITS = {
    "plugins/pm3-frontend/templates/CLAUDE.md": [
        # graphify 列表项 + 其无前缀续行
        (re.compile(r"^- \*\*graphify\*\*[^\n]*\nWhen the user types `/graphify`[^\n]*\n", re.M), ""),
        (re.compile(r"^- \*\*gbrain\*\*[^\n]*\n", re.M), ""),
        # 登录章节保留结构，账密置空占位由入项用户自填；带跳过说明，避免用户侧
        # Claude 把占位符当真实值尝试登录。真实值若漏进产出由 scan_leaks 闸门报错兜底
        (re.compile(r"(## 登录禅道\n)地址 [^\n]*\n账号 [^\n]*\n密码 [^\n]*\n"),
         r"\1> 入项后请填写以下地址与账密；未填写前跳过本节，不得使用占位符尝试登录。\n"
         r"地址 <禅道地址>\n账号 <填写账号>\n密码 <填写密码>\n"),
        (re.compile(r"(## 登录系统测试\n)账号 [^\n]*\n密码 [^\n]*\n"),
         r"\1> 入项后请填写以下账密；未填写前跳过本节，不得使用占位符尝试登录。\n"
         r"账号 <填写账号>\n密码 <填写密码>\n"),
    ],
    "plugins/pm3-mobile/skills/pm-mobile-migration/SKILL.md": [
        (re.compile(rf"（PC 仓库默认：`{re.escape(str(PC_REPO_PATH))}`，页面文件由输入参数 `<pc-vue-path>` 指定）"),
         "（PC 仓库根目录由调用方工作目录或输入参数确定，页面文件由输入参数 `<pc-vue-path>` 指定）"),
    ],
    # evals.json 示例提示词中的个人绝对路径 → 中性占位
    "plugins/pm3-frontend/skills/generate-api/evals/evals.json": [
        (re.compile(re.escape(str(DEFAULT_AI_ROOT))), "<ai-workspace>"),
    ],
    "plugins/pm3-frontend/skills/generate-prd-guide/evals/evals.json": [
        (re.compile(re.escape(str(DEFAULT_AI_ROOT))), "<ai-workspace>"),
    ],
}


def load_leak_patterns(path: Path = PATTERNS_LOCAL) -> list[str]:
    """Load blacklist from git-ignored local file. Missing file is fatal (fail-closed):
    running sync without the real blacklist would let credential leaks through the gate."""
    if path.exists():
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
        return [ln for ln in lines if ln and not ln.startswith("#")]
    print(f"ERROR: {path} not found — refusing to run with a weak blacklist.\n"
          f"Copy {PATTERNS_EXAMPLE.name} to {path.name} and fill in the real values.", file=sys.stderr)
    sys.exit(2)


def _iter_content_files(repo: Path):
    for target in SCAN_TARGETS:
        base = repo / target
        if not base.exists():
            continue
        if base.is_file():
            yield base
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file():
                continue
            yield f


def scan_leaks(repo: Path, patterns: list[str], skip: frozenset = frozenset()) -> list[str]:
    """Return leak reports for produced content. Empty list means clean.
    skip: resolved paths to exempt (the blacklist file itself carries the real values)."""
    hits = []
    for f in _iter_content_files(repo):
        if f.resolve() in skip:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue  # binary asset
        for pat in patterns:
            if pat in text:
                hits.append(f"{f.relative_to(repo)}: contains {pat!r}")
    return hits


def clean_file(path: Path, edits: list) -> int:
    """Apply regex edits in place. Returns number of replacements."""
    text = path.read_text(encoding="utf-8")
    count = 0
    for pat, repl in edits:
        text, n = pat.subn(repl, text)
        count += n
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return count


# (源相对路径, 仓库内目标相对路径, 源根, 目录级排除名)
COPY_PLAN = [
    (".claude/skills/generate-prd-guide", "plugins/pm3-frontend/skills/generate-prd-guide", "ai",
     frozenset({"temp", "OPTIMIZATION-PLAN.md", "OPTIMIZATION-REPORT.md", "REVISION-SUMMARY.md"})),
    (".claude/skills/generator-dev-plan", "plugins/pm3-frontend/skills/generator-dev-plan", "ai",
     frozenset({"tasks"})),
    (".claude/skills/generate-api", "plugins/pm3-frontend/skills/generate-api", "ai", frozenset()),
    (".claude/skills/scene-list", "plugins/pm3-frontend/skills/scene-list", "ai", frozenset()),
    (".claude/skills/scene-form", "plugins/pm3-frontend/skills/scene-form", "ai", frozenset()),
    (".claude/skills/scene-detail", "plugins/pm3-frontend/skills/scene-detail", "ai", frozenset()),
    (".claude/skills/scene-approval", "plugins/pm3-frontend/skills/scene-approval", "ai", frozenset()),
    (".claude/skills/pattern-upload", "plugins/pm3-frontend/skills/pattern-upload", "ai", frozenset()),
    (".claude/skills/skill-generator", "plugins/pm3-frontend/skills/skill-generator", "ai", frozenset()),
    (".claude/skills/create-develop-plan-skill", "plugins/pm3-frontend/skills/create-develop-plan-skill", "ai", frozenset()),
    (".claude/agents/workflow-agent", "plugins/pm3-frontend/skills/workflow-agent", "ai",
     frozenset({"logs", "skills"})),
    (".claude/rules", "plugins/pm3-frontend/templates/rules", "ai", frozenset()),
    ("CLAUDE.md", "plugins/pm3-frontend/templates/CLAUDE.md", "ai", frozenset()),
    ("skills/pm-mobile-migration", "plugins/pm3-mobile/skills/pm-mobile-migration", "global", frozenset()),
    ("skills/isoftstone-debug-recovery", "plugins/pm3-common/skills/isoftstone-debug-recovery", "global", frozenset()),
]


def copy_tree(src: Path, dst: Path, extra_excludes: frozenset = frozenset()) -> None:
    """Full rebuild: wipe dst, then copy ignoring .DS_Store and extra_excludes."""
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".DS_Store", "*.bak", *extra_excludes))


def sync(ai_root: Path, global_root: Path, repo: Path,
         plan=COPY_PLAN, edits=CONTENT_EDITS, leak_patterns=None) -> list[str]:
    if leak_patterns is None:
        leak_patterns = load_leak_patterns()
    roots = {"ai": ai_root, "global": global_root}
    copied = []
    for src_rel, dst_rel, root_name, excludes in plan:
        src = roots[root_name] / src_rel
        dst = repo / dst_rel
        if not src.exists():
            raise FileNotFoundError(f"missing source: {src}")
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            copy_tree(src, dst, excludes)
        copied.append(dst_rel)
    for rel, file_edits in edits.items():
        p = repo / rel
        if not p.exists():
            raise FileNotFoundError(f"expected file for cleaning missing: {p}")
        clean_file(p, file_edits)
    hits = scan_leaks(repo, leak_patterns, skip=frozenset({PATTERNS_LOCAL.resolve()}))
    if hits:
        print("LEAK SCAN FAILED — push is forbidden:", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        sys.exit(2)
    return copied


def main(argv=None) -> None:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ai-root", type=Path, default=DEFAULT_AI_ROOT)
    ap.add_argument("--global-root", type=Path, default=DEFAULT_GLOBAL_ROOT)
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    args = ap.parse_args(argv)
    copied = sync(args.ai_root, args.global_root, args.repo)
    print(f"synced {len(copied)} entries, leak scan clean:")
    for c in copied:
        print(f"  -> {c}")


if __name__ == "__main__":
    main()
