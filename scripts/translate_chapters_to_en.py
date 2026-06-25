#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

SYSTEM_PROMPT = """You are translating a technical book from Chinese into native, publication-quality English.

Hard rules:
- Return only Markdown. No explanation, no code fences around the whole output.
- Translate the entire input. Do not summarize, shorten, merge sections, omit examples, omit tables, omit code blocks, or omit captions.
- Preserve Markdown structure exactly: heading levels, table structure, lists, admonitions, code fences, Mermaid fences, footnotes, links, and image blocks.
- Preserve all code blocks. Translate Chinese comments and Chinese string literals only when they are explanatory examples, not executable identifiers.
- Translate table captions, figure captions, alt text, and source notes into natural English.
- Use native technical English. Avoid Chinglish, promotional language, and AI-ish phrasing.
- Keep product names, protocol names, API names, file paths, identifiers, and citations unchanged unless the path has already been changed in the input.
- Preserve chapter numbering and section numbering.
- Use "Figure" for 图 and "Table" for 表.
- Translate "本章摘要" as "Chapter Summary" and "本章小结" as "Chapter Recap"; do not use the same heading for both.
- Translate "场景引入" as "Opening Scenario", "关键词" as "Key Terms", "学习目标" as "Learning Objectives", and "参考文献" as "References".
- Keep all image paths exactly as they appear in the input.
"""


def part_number(path: Path) -> int:
    m = re.search(r"part(\d+)", str(path))
    if not m:
        raise ValueError(f"cannot infer part number from {path}")
    return int(m.group(1))


def rewrite_image_paths(text: str, ch_path: Path) -> str:
    n = part_number(ch_path)
    text = text.replace(f"../../images/part{n}/ch/", f"../../images/part{n}/en/")
    return text


def verify_image_targets(text: str, en_path: Path) -> list[str]:
    missing: list[str] = []
    for raw in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        target = raw.strip().split("#", 1)[0]
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        if not (en_path.parent / target).resolve().exists():
            missing.append(target)
    return missing


def run_claude(markdown: str, model: str, budget: float | None, timeout: int) -> str:
    prompt = SYSTEM_PROMPT + "\n\nTranslate this Markdown document:\n\n" + markdown
    cmd = ["claude", "--bare", "-p", "--model", model]
    if budget is not None:
        cmd.extend(["--max-budget-usd", str(budget)])
    proc = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude failed ({proc.returncode})\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    out = proc.stdout.strip()
    out = re.sub(r"^```(?:markdown)?\s*\n", "", out)
    out = re.sub(r"\n```\s*$", "", out)
    return out.rstrip() + "\n"


def split_by_h2(markdown: str) -> list[str]:
    lines = markdown.splitlines(keepends=True)
    chunks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("## ") and current:
            chunks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append(current)
    return ["".join(chunk) for chunk in chunks]


def translate_markdown(markdown: str, model: str, budget: float | None, timeout: int, chunk_by_h2: bool) -> str:
    if not chunk_by_h2:
        return run_claude(markdown, model=model, budget=budget, timeout=timeout)
    translated_chunks: list[str] = []
    chunks = split_by_h2(markdown)
    for idx, chunk in enumerate(chunks, start=1):
        print(f"  chunk {idx}/{len(chunks)}", flush=True)
        translated_chunks.append(run_claude(chunk, model=model, budget=budget, timeout=timeout))
    return "\n".join(part.rstrip() for part in translated_chunks).rstrip() + "\n"


def translate_file(ch_path: Path, model: str, budget: float | None, timeout: int, force: bool) -> None:
    en_path = ch_path.parents[1] / "en" / ch_path.name
    en_path.parent.mkdir(parents=True, exist_ok=True)
    source = ch_path.read_text(encoding="utf-8")
    prepared = rewrite_image_paths(source, ch_path)
    missing = verify_image_targets(prepared, en_path)
    if missing:
        print(f"WARN {ch_path.relative_to(ROOT)} missing English image targets before translation:")
        for m in missing:
            print(f"  - {m}")
    translated = translate_markdown(prepared, model=model, budget=budget, timeout=timeout, chunk_by_h2=translate_file.chunk_by_h2)
    previous = en_path.read_text(encoding="utf-8") if en_path.exists() else None
    en_path.write_text(translated, encoding="utf-8")
    check = subprocess.run(
        [sys.executable, "scripts/check_translation_alignment.py", str(ch_path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if check.returncode != 0:
        failed_path = en_path.with_suffix(en_path.suffix + ".failed")
        failed_path.write_text(translated, encoding="utf-8")
        if previous is None:
            en_path.unlink(missing_ok=True)
        else:
            en_path.write_text(previous, encoding="utf-8")
        raise RuntimeError(
            f"alignment failed for {ch_path.relative_to(ROOT)}; candidate saved to {failed_path.relative_to(ROOT)}\n"
            f"{check.stdout}\n{check.stderr}"
        )
    print(f"OK {ch_path.relative_to(ROOT)} -> {en_path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="Chinese markdown files to translate")
    parser.add_argument("--part", help="Only translate paths containing this part directory, e.g. part01-overview")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--budget", type=float, default=None)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--keep-going", action="store_true", help="Continue translating remaining files after a failure.")
    parser.add_argument("--chunk-by-h2", action="store_true", help="Translate each H2 section separately before validating the full file.")
    args = parser.parse_args()

    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = sorted(DOCS.glob("part*/ch/*.md"))
    if args.part:
        paths = [p for p in paths if args.part in str(p)]
    translate_file.chunk_by_h2 = args.chunk_by_h2  # type: ignore[attr-defined]
    failures: list[tuple[Path, str]] = []
    for p in paths:
        p = p if p.is_absolute() else ROOT / p
        try:
            translate_file(p, model=args.model, budget=args.budget, timeout=args.timeout, force=args.force)
        except Exception as exc:
            failures.append((p, str(exc)))
            print(f"FAIL {p.relative_to(ROOT)}: {exc}", file=sys.stderr)
            if not args.keep_going:
                break
    if failures:
        print("\nTranslation failures:", file=sys.stderr)
        for p, err in failures:
            print(f"- {p.relative_to(ROOT)}: {err.splitlines()[0] if err else err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
