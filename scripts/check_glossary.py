"""Scan Chinese chapter text for uppercase acronyms not in the glossary whitelist.

Heuristic: extract all-caps tokens of length 2-6 (letters + optional digits)
from non-code text. Compare against the whitelist embedded in glossary/terms.md
(final "缩写速查" section).

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
    whitelist.update({
        "ACL",
        "CPU",
        "CSV",
        "HTML",
        "LLMO",
        "PDF",
        "PR",
        "TODO",
        "URL",
        "UTF",
        "VLM",
        "WHATWG",
        "XML",
    })
    return whitelist


def scan_file(path: Path, whitelist: set[str]) -> list[tuple[int, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    bad: list[tuple[int, str]] = []
    in_code = False
    in_references = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## ") and "参考文献" in stripped:
            in_references = True
            continue
        if stripped.startswith("## ") and in_references:
            in_references = False
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or in_references:
            continue
        if line.startswith("http") or line.startswith("["):
            continue
        for token in ACRONYM_RE.findall(line):
            if token not in whitelist:
                bad.append((i + 1, token))
    return bad


def main() -> int:
    whitelist = load_whitelist()
    failures = 0
    for path in sorted(DOCS.rglob("ch*.md")):
        if "en" in path.parts:
            continue
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
