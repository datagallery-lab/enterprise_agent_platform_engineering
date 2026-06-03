"""Check that each chapter stub conforms to the 7-section template.

Usage:
    python scripts/check_chapter_template.py
Exit code 0 if all chapters pass, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

REQUIRED_HEADINGS = [
    re.compile(r"^##\s+L1\s+概念"),
    re.compile(r"^##\s+L2\s+架构"),
    re.compile(r"^##\s+L3\s+"),
    re.compile(r"^##\s+本章小结"),
]


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    for pat in REQUIRED_HEADINGS:
        if not any(pat.search(line) for line in lines):
            errors.append(f"missing section matching {pat.pattern}")
    return errors


def main() -> int:
    bad = 0
    for path in sorted(DOCS.glob("part*/ch*.md")):
        errs = check_file(path)
        if errs:
            bad += 1
            rel = path.relative_to(ROOT)
            print(f"✗ {rel}")
            for e in errs:
                print(f"   - {e}")
    total = len(list(DOCS.glob("part*/ch*.md")))
    if bad:
        print(f"\n{bad}/{total} chapter(s) failed template check.")
        return 1
    print(f"\n✓ all {total} chapters conform to template.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
