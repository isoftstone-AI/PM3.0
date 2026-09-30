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
