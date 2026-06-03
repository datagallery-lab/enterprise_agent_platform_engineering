"""Scan all chapter L1/L2 sections for uppercase acronyms not in the glossary whitelist.

Heuristic: extract all-caps tokens of length 2-6 (letters + optional digits)
that appear in L1 or L2 sections. Compare against the whitelist embedded in
glossary/terms.md (final "缩写速查" section).

Skip code blocks (lines inside ``` ... ```) and TODO/placeholder text.

Usage:
    python scripts/check_glossary.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GLOSSARY = ROOT / "glossary" / "terms.md"

ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")


def load_whitelist() -> set[str]:
    text = GLOSSARY.read_text(encoding="utf-8")
    # also accept terms with capital initials elsewhere
    whitelist: set[str] = set()
    # collect from headings and bullet entries
    for token in ACRONYM_RE.findall(text):
        whitelist.add(token)
    # always allow these structural tokens
    whitelist.update({"L1", "L2", "L3", "TODO", "PR", "CI", "CD"})
    return whitelist


def is_in_l1_l2(lines: list[str], idx: int) -> bool:
    """Return True if line idx is inside L1 or L2 section (before L3)."""
    section = None
    for i in range(idx, -1, -1):
        m = re.match(r"^##\s+L([123])\s+", lines[i])
        if m:
            section = m.group(1)
            break
    return section in ("1", "2")


def scan_file(path: Path, whitelist: set[str]) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    bad: list[tuple[int, str]] = []
    in_code = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not is_in_l1_l2(lines, i):
            continue
        for token in ACRONYM_RE.findall(line):
            if token not in whitelist:
                bad.append((i + 1, token))
    return bad


def main() -> int:
    whitelist = load_whitelist()
    failures = 0
    for path in sorted(DOCS.glob("part*/ch*.md")):
        bad = scan_file(path, whitelist)
        if bad:
            failures += 1
            rel = path.relative_to(ROOT)
            print(f"✗ {rel}")
            for line_no, tok in bad[:10]:
                print(f"   line {line_no}: undefined acronym '{tok}'")
            if len(bad) > 10:
                print(f"   ... and {len(bad) - 10} more")
    if failures:
        print(f"\n{failures} file(s) contain undefined acronyms.")
        return 1
    print("\n✓ glossary check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
