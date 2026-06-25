#!/usr/bin/env python3
"""Report chapter length and density outliers for the Chinese edition.

This is an editorial audit, not a hard gate. It helps revising agents find
chapters that read too thin, too table-heavy, or too long compared with the
reference book.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def count_tables(lines: list[str]) -> int:
    total = 0
    for i, line in enumerate(lines[:-1]):
        if line.lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            total += 1
    return total


def metrics(path: Path) -> dict[str, int | float | str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    tables = count_tables(lines)
    code_blocks = len(re.findall(r"^```", text, re.M)) // 2
    figures = len(re.findall(r"^!\[", text, re.M))
    density = zh_chars / max(1, len(lines))
    return {
        "path": str(path.relative_to(ROOT)),
        "lines": len(lines),
        "zh_chars": zh_chars,
        "tables": tables,
        "code_blocks": code_blocks,
        "figures": figures,
        "zh_per_line": round(density, 1),
    }


def classify(row: dict[str, int | float | str]) -> list[str]:
    flags: list[str] = []
    zh_chars = int(row["zh_chars"])
    lines = int(row["lines"])
    tables = int(row["tables"])
    code_blocks = int(row["code_blocks"])
    structure_blocks = tables + code_blocks

    if zh_chars < 4500:
        flags.append("thin-prose")
    if zh_chars > 15000:
        flags.append("very-long")
    if lines > 750:
        flags.append("long-structure")
    if structure_blocks >= 16 and zh_chars < 7000:
        flags.append("table/code-heavy")
    if tables >= 18:
        flags.append("table-heavy")
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Chinese chapter length and density.")
    parser.add_argument("--fail", action="store_true", help="Exit non-zero when outliers are found.")
    args = parser.parse_args()

    rows = [metrics(p) for p in sorted(DOCS.glob("part*/ch/ch*.md"))]
    flagged: list[tuple[dict[str, int | float | str], list[str]]] = []
    for row in rows:
        flags = classify(row)
        if flags:
            flagged.append((row, flags))

    print(f"Checked {len(rows)} Chinese chapters.")
    print("Guideline: 4500-15000 Chinese characters, with tables/code supporting rather than replacing prose.")
    if not flagged:
        print("No density outliers found.")
        return 0

    print("\nDensity outliers:")
    print("path\tlines\tzh_chars\ttables\tcode\tfigures\tzh/line\tflags")
    for row, flags in flagged:
        print(
            f"{row['path']}\t{row['lines']}\t{row['zh_chars']}\t{row['tables']}\t"
            f"{row['code_blocks']}\t{row['figures']}\t{row['zh_per_line']}\t{','.join(flags)}"
        )
    return 1 if args.fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
