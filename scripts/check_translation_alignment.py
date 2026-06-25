#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def count_tables(text: str) -> int:
    lines = text.splitlines()
    count = 0
    for i in range(len(lines) - 1):
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}:?", lines[i + 1]):
            count += 1
    return count


def metrics(text: str) -> dict[str, int]:
    return {
        "h1": len(re.findall(r"^#\s+", text, re.M)),
        "h2": len(re.findall(r"^##\s+", text, re.M)),
        "h3": len(re.findall(r"^###\s+", text, re.M)),
        "h4": len(re.findall(r"^####\s+", text, re.M)),
        "images": len(IMAGE_RE.findall(text)),
        "code_fences": len(re.findall(r"^```", text, re.M)) // 2,
        "tables": count_tables(text),
        "table_caps": len(re.findall(r"^\s*\*(?:表|Table)\s*\d+", text, re.M)),
        "fig_caps": len(re.findall(r"^\s*\*(?:图|Figure)\s*\d+", text, re.M)),
        "zh_chars": len(re.findall(r"[\u4e00-\u9fff]", text)),
    }


def local_targets(path: Path, text: str) -> list[str]:
    targets: list[str] = []
    for regex in (IMAGE_RE, LINK_RE):
        for raw in regex.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            if target.endswith((".md", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif")):
                targets.append(target)
    return targets


def check_pair(ch_path: Path) -> list[str]:
    part_dir = ch_path.parents[1]
    en_path = part_dir / "en" / ch_path.name
    errors: list[str] = []
    if not en_path.exists():
        return [f"missing English file: {en_path.relative_to(ROOT)}"]
    ch = ch_path.read_text(encoding="utf-8")
    en = en_path.read_text(encoding="utf-8")
    cm, em = metrics(ch), metrics(en)
    for key in ["h1", "h2", "h3", "h4", "images", "code_fences", "tables"]:
        if cm[key] != em[key]:
            errors.append(f"{key} mismatch: ch={cm[key]} en={em[key]}")
    # Captions can be reflowed but should not disappear.
    for key in ["table_caps", "fig_caps"]:
        if em[key] < cm[key]:
            errors.append(f"{key} missing: ch={cm[key]} en={em[key]}")
    if em["zh_chars"] > 40:
        errors.append(f"too many Chinese characters remain in English: {em['zh_chars']}")
    for target in local_targets(en_path, en):
        resolved = (en_path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"missing local target: {target}")
        if "/images/" in str(resolved) and "/ch/" in str(resolved):
            errors.append(f"English file points to Chinese image: {target}")
    return errors


def main() -> int:
    args = sys.argv[1:]
    paths = [Path(a) for a in args] if args else sorted(DOCS.glob("part*/ch/*.md"))
    failures = 0
    for path in paths:
        if not path.is_absolute():
            path = ROOT / path
        errs = check_pair(path)
        if errs:
            failures += 1
            print(f"✗ {path.relative_to(ROOT)}")
            for err in errs:
                print(f"  - {err}")
    if failures:
        print(f"\n{failures} file(s) failed translation alignment checks.")
        return 1
    print(f"✓ translation alignment passed for {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
