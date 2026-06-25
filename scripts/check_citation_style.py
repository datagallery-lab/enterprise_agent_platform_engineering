#!/usr/bin/env python3
"""Validate Chinese citation style against the published reference-book pattern.

The Chinese book should use author-year citations in running text, for example:
    RAG (Lewis et al. 2020)
    ... (Lewis et al. 2020; Gao et al. 2023)

Numeric literature citations such as [1] or [1][2] are not allowed in prose, and
reference lists must not use numbered entries.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
NUMERIC_CITATION_RE = re.compile(r"(?<![A-Za-z0-9_])(?:\[[0-9]+\]|［[0-9]+］)+")
NUMBERED_REFERENCE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\[[0-9]+\]|［[0-9]+］)\s+")
CHINESE_NUMBERED_CITATION_RE = re.compile(r"（[^）]*(?:\[[0-9]+\]|［[0-9]+］)[^）]*）")
REFERENCE_YEAR_RE = re.compile(r"\((?:19|20)\d{2}|n\.d\.\)")
REFERENCE_LIKE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 .,&\-]+\.?\s+")


def should_scan(path: Path) -> bool:
    return path.suffix == ".md" and "en" not in path.parts


def mask_inline_code(line: str) -> str:
    return INLINE_CODE_RE.sub("", line)


def is_reference_like(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("相关章节", "本章", "长期维护", "#")):
        return False
    return REFERENCE_LIKE_RE.match(stripped) is not None


def iter_visible_lines(path: Path) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        lines.append((lineno, mask_inline_code(line)))
    return lines


def main() -> int:
    failures: list[str] = []

    for path in sorted(DOCS.rglob("*.md")):
        if not should_scan(path):
            continue
        rel = path.relative_to(ROOT)
        in_references = False
        for lineno, line in iter_visible_lines(path):
            stripped = line.strip()
            if stripped.startswith("## ") and "参考文献" in stripped:
                in_references = True
                continue
            if stripped.startswith("## ") and in_references:
                in_references = False

            if NUMBERED_REFERENCE_RE.match(line):
                failures.append(f"{rel}:{lineno}: numbered reference entry is not allowed")
                continue
            if in_references and is_reference_like(line) and not REFERENCE_YEAR_RE.search(line):
                failures.append(f"{rel}:{lineno}: reference entry must include (year) or (n.d.)")
                continue
            if CHINESE_NUMBERED_CITATION_RE.search(line):
                failures.append(f"{rel}:{lineno}: numeric citation inside Chinese parentheses")
                continue
            if NUMERIC_CITATION_RE.search(line):
                failures.append(f"{rel}:{lineno}: numeric in-text citation is not allowed")

    if failures:
        print("Citation style check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("✓ citation style check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
