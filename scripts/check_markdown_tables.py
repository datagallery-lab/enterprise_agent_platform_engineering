#!/usr/bin/env python3
"""Validate Markdown table blocks render as tables in MkDocs."""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_SEPARATOR_RE = re.compile(
    r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$"
)


def strip_code_fences(lines: list[str]) -> list[str]:
    result: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append("")
            continue
        result.append("" if in_fence else line)
    return result


def should_scan(path: Path) -> bool:
    return path.suffix == ".md" and "en" not in path.parts


def is_table_separator(line: str) -> bool:
    return TABLE_SEPARATOR_RE.match(line.strip()) is not None


def is_table_header(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    line = lines[index].strip()
    if "|" not in line or line.startswith("!") or not is_table_separator(lines[index + 1]):
        return False
    return True


def main() -> int:
    failures: list[str] = []

    for path in sorted(DOCS.rglob("*.md")):
        if not should_scan(path):
            continue
        raw_lines = path.read_text(encoding="utf-8").splitlines()
        lines = strip_code_fences(raw_lines)
        for i, line in enumerate(lines):
            if not is_table_header(lines, i):
                continue
            if i > 0 and lines[i - 1].strip():
                failures.append(
                    f"{path.relative_to(ROOT)}:{i + 1}: table header must be preceded by a blank line"
                )

    if failures:
        print("Markdown table render check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("✓ markdown table render check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
