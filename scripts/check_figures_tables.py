"""Validate figure and table numbering in Chinese chapter markdown files.

The check is intentionally stricter than MkDocs:
- every image must have a descriptive alt text containing its chapter figure id;
- every image must be followed by an independent caption line;
- every markdown table must be preceded by an independent table caption line.
- every markdown table must have non-empty header cells and consistent row width.

Usage:
    python scripts/check_figures_tables.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FENCE_RE = re.compile(r"^\s*(```|~~~)")
H1_RE = re.compile(r"^#\s*第\s*(\d+)\s*章")
CHAPTER_FROM_NAME_RE = re.compile(r"ch(\d+)", re.IGNORECASE)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)|<img\b[^>]*>", re.IGNORECASE)
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
LEGACY_FIGURE_RE = re.compile(r"图\s+P\d+\s*[-－]\s*\d+|\bP5-\d+\b")
PSEUDO_CAPTION_RE = re.compile(r"^\s*\*\*图\s+(?:P5-\d+|\d+-\d+)\*\*.*images/ch/p5-", re.IGNORECASE)
LOW_QUALITY_TITLE_RE = re.compile(r"(?:图|表)\s*\d+\s*[-－]\s*\d+\s*[：:](?:的|是|的是)")
DUPLICATE_STANDALONE_TITLE_RE = re.compile(
    r"^\s*\*{0,2}\s*(?:图|表)\s*\d+\s*[-－]\s*\d+\s*[：:].+"
)


def strip_code_fences(lines: list[str]) -> list[str]:
    """Return lines with fenced code blocks replaced by empty lines."""
    result: list[str] = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            result.append("")
            continue
        result.append("" if in_fence else line)
    return result


def chapter_number(path: Path, lines: list[str]) -> int | None:
    for line in lines[:40]:
        m = H1_RE.match(line)
        if m:
            return int(m.group(1))
    m = CHAPTER_FROM_NAME_RE.search(path.name)
    if m:
        return int(m.group(1))
    return None


def expected_image_part(chapter: int) -> int | None:
    ranges = [
        (1, 4, 1),
        (5, 9, 2),
        (10, 15, 3),
        (16, 21, 4),
        (22, 31, 5),
        (32, 37, 6),
        (38, 42, 7),
        (43, 46, 8),
        (47, 49, 9),
        (50, 53, 10),
        (54, 55, 11),
    ]
    for start, end, part in ranges:
        if start <= chapter <= end:
            return part
    return None


def previous_nonblank(lines: list[str], index: int) -> tuple[int, str] | None:
    for i in range(index - 1, -1, -1):
        if lines[i].strip():
            return i, lines[i].strip()
    return None


def next_nonblank(lines: list[str], index: int) -> tuple[int, str] | None:
    for i in range(index + 1, len(lines)):
        if lines[i].strip():
            return i, lines[i].strip()
    return None


def has_numbered_text(text: str, kind: str, chapter: int, seq: int) -> bool:
    pattern = rf"{kind}\s*{chapter}\s*[-－]\s*{seq}\s*[：:].+"
    return re.search(pattern, text) is not None


def has_loose_number_and_title(text: str, kind: str, chapter: int, seq: int) -> bool:
    pattern = rf"{kind}\s*{chapter}\s*[-－]\s*{seq}\s*(?:[：:]\s*|\s+).{{4,}}"
    return re.search(pattern, text) is not None


def has_source(text: str) -> bool:
    return "来源：" in text or "来源:" in text


def has_alt_text_note(text: str) -> bool:
    return "Alt text：" in text or "Alt text:" in text


def is_table_header(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    line = lines[index].strip()
    if not line.startswith("|") or not line.endswith("|"):
        return False
    return TABLE_SEPARATOR_RE.match(lines[index + 1].strip()) is not None


def split_markdown_row(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    in_code = False
    for char in text:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if char == "`":
            current.append(char)
            in_code = not in_code
            continue
        if char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def iter_chinese_chapters() -> list[Path]:
    paths = []
    for path in DOCS.rglob("ch*.md"):
        parts = set(path.parts)
        if "en" in parts:
            continue
        paths.append(path)
    return sorted(paths)


def main() -> int:
    failures: list[str] = []

    for path in iter_chinese_chapters():
        raw_lines = path.read_text(encoding="utf-8").splitlines()
        lines = strip_code_fences(raw_lines)
        chapter = chapter_number(path, lines)
        if chapter is None:
            failures.append(f"{path.relative_to(ROOT)}: cannot determine chapter number")
            continue

        figure_seq = 0
        table_seq = 0
        for i, line in enumerate(lines):
            if LEGACY_FIGURE_RE.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{i + 1}: legacy Part V figure label remains"
                )
            if PSEUDO_CAPTION_RE.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{i + 1}: old pseudo-caption with image path remains"
                )
            if LOW_QUALITY_TITLE_RE.search(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{i + 1}: low-quality figure/table title starts with 的/是"
                )
            if DUPLICATE_STANDALONE_TITLE_RE.match(line) and not has_source(line):
                failures.append(
                    f"{path.relative_to(ROOT)}:{i + 1}: duplicate standalone figure/table title lacks 来源"
                )

            if IMAGE_RE.search(line):
                figure_seq += 1
                image_match = re.search(r"!\[([^\]]*)\]\(([^)]+)\)", line)
                alt_match = image_match
                alt = alt_match.group(1).strip() if alt_match else ""
                if image_match:
                    target = image_match.group(2).strip()
                    expected_part = expected_image_part(chapter)
                    if expected_part is not None and f"images/part{expected_part}/" not in target:
                        failures.append(
                            f"{path.relative_to(ROOT)}:{i + 1}: image path must use docs/images/part{expected_part}"
                        )
                if not has_loose_number_and_title(alt, "图", chapter, figure_seq):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{i + 1}: image alt lacks 图{chapter}-{figure_seq} number and title"
                    )
                nxt = next_nonblank(lines, i)
                caption = nxt[1].strip("*_ ") if nxt else ""
                if not nxt or not has_numbered_text(caption, "图", chapter, figure_seq):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{i + 1}: image lacks following caption 图{chapter}-{figure_seq}：标题"
                    )
                elif not has_source(caption) or not has_alt_text_note(caption):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{nxt[0] + 1}: image caption lacks 来源 or Alt text"
                    )

            if is_table_header(lines, i):
                table_seq += 1
                header = split_markdown_row(lines[i])
                separator = split_markdown_row(lines[i + 1])
                if any(not cell for cell in header):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{i + 1}: table header contains empty cell"
                    )
                if len(separator) != len(header):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{i + 2}: table separator has {len(separator)} cells, header has {len(header)}"
                    )
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    row = split_markdown_row(lines[j])
                    if len(row) != len(header):
                        failures.append(
                            f"{path.relative_to(ROOT)}:{j + 1}: table row has {len(row)} cells, header has {len(header)}"
                        )
                    j += 1
                prev = previous_nonblank(lines, i)
                caption = prev[1].strip("*_ ") if prev else ""
                if not prev or not has_numbered_text(caption, "表", chapter, table_seq):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{i + 1}: table lacks preceding caption 表{chapter}-{table_seq}：标题"
                    )
                elif not has_source(caption):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{prev[0] + 1}: table caption lacks 来源"
                    )

    if failures:
        print("Figure/table numbering check failed:\n")
        for failure in failures:
            print(f"- {failure}")
        print(f"\n{len(failures)} issue(s) found.")
        return 1

    print("✓ figure/table numbering check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
