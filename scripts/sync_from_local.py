#!/usr/bin/env python3
"""Sync personal Claude assets into the PM3.0 marketplace repo.

Real run (defaults):  python3 scripts/sync_from_local.py
Test-only module functions are unit-tested in test_sync_from_local.py.
"""
import re
import shutil
import sys
from pathlib import Path

LEAK_PATTERNS = [
    "REDACTED",
    "REDACTED",
    "REDACTED",
    "REDACTED",
    "REDACTED-IP",
    "REDACTED-PATH",
]

# scan_leaks 只扫产出内容；scripts/ 自身含黑名单字符串，必须排除
SCAN_TARGETS = ["plugins", "README.md"]


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


def scan_leaks(repo: Path) -> list[str]:
    """Return leak reports for produced content. Empty list means clean."""
    hits = []
    for f in _iter_content_files(repo):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue  # binary asset
        for pat in LEAK_PATTERNS:
            if pat in text:
                hits.append(f"{f.relative_to(repo)}: contains {pat!r}")
    return hits


# 内容清洗：仓库内相对路径 -> [(编译正则, 替换文本), ...]
CONTENT_EDITS = {
    "plugins/pm3-frontend/templates/CLAUDE.md": [
        # graphify 列表项 + 其无前缀续行
        (re.compile(r"^- \*\*graphify\*\*[^\n]*\nWhen the user types `/graphify`[^\n]*\n", re.M), ""),
        (re.compile(r"^- \*\*gbrain\*\*[^\n]*\n", re.M), ""),
        (re.compile(r"## 登录禅道\n.*?(?=\n## |\Z)", re.S), ""),
        (re.compile(r"## 登录系统测试\n.*?(?=\n## |\Z)", re.S), ""),
    ],
    "plugins/pm3-mobile/skills/pm-mobile-migration/SKILL.md": [
        (re.compile(r"（PC 仓库默认：`REDACTED-PATH/work/pm/pm3\.0_frontend`，页面文件由输入参数 `<pc-vue-path>` 指定）"),
         "（PC 仓库根目录由调用方工作目录或输入参数确定，页面文件由输入参数 `<pc-vue-path>` 指定）"),
    ],
}


def clean_file(path: Path, edits: list) -> int:
    """Apply regex edits in place. Returns number of replacements."""
    text = path.read_text(encoding="utf-8")
    count = 0
    for pat, repl in edits:
        text, n = pat.subn(repl, text)
        count += n
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return count
