#!/usr/bin/env python3
"""按 article-image-generator-atlas skill 批量生成 Part VIII 配图。

从章节 Markdown 的「配图 Prompt」块解析意图，合成 Atlas 友好 prompt，
调用 generate_article_image.py，支持断点续传与失败重试。
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/part08-deployment"
OUT = ROOT / "docs/assets/images"
ATLAS = Path.home() / ".codex/skills/article-image-generator-atlas/scripts/generate_article_image.py"

PROMPT_BLOCK = re.compile(
    r"> \*\*配图 Prompt\*\*｜模板：`[^`]+`(?:（[^）]+）)?\n>\n"
    r"((?:> .*\n)*)\n"
    r"!\[[^\]]*\]\(\.\./assets/images/(ch\d+-\d+\.png)\)",
    re.MULTILINE,
)


def block_to_atlas_prompt(lines: str) -> str:
    """将配图 Prompt 块转为 Atlas 单行 prompt（skill：构图清晰、标签可读、16:9）。"""
    parts: list[str] = []
    for line in lines.splitlines():
        line = line.removeprefix("> ").strip()
        if not line or line.startswith("**配图"):
            continue
        if line.startswith("主题："):
            parts.append(line.replace("主题：", "主题：", 1))
        elif line.startswith("构图："):
            parts.append(line)
        elif line.startswith("视觉："):
            parts.append(line)
        elif line.startswith("约束："):
            parts.append(line)
        elif line.startswith("模块标签") or line.startswith("五步标签") or line.startswith("阶段 "):
            parts.append(line)
        elif line.startswith("列标题") or line.startswith("每列") or line.startswith("底部"):
            parts.append(line)
        elif line.startswith("层 ") or line.startswith("左侧") or line.startswith("右侧"):
            parts.append(line)
        elif line.startswith("四列") or line.startswith("四象限") or line.startswith("三个"):
            parts.append(line)
        elif line.startswith("状态标签") or line.startswith("模块从左"):
            parts.append(line)
        elif line.startswith("上方红色"):
            parts.append(line)
        elif line.startswith("红色路径") or line.startswith("红色箭头"):
            parts.append(line)
        elif line.startswith("每个节点") or line.startswith("每个象限"):
            parts.append(line)
        elif line.startswith("边缘框") or line.startswith("连接线"):
            parts.append(line)
        elif line.startswith("每步下方") or line.startswith("红色门禁"):
            parts.append(line)
        else:
            parts.append(line)
    body = " ".join(parts)
    suffix = (
        " 扁平企业技术信息图，education-tech infographic style，"
        "aspect ratio 16:9，中文短标签清晰可读，留白充足，"
        "no watermark, no 3D decoration, no long paragraphs in image."
    )
    return body + suffix


def collect_jobs() -> list[tuple[str, str]]:
    jobs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for md in sorted(DOCS.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in PROMPT_BLOCK.finditer(text):
            body, filename = m.group(1), m.group(2)
            if filename in seen:
                continue
            seen.add(filename)
            jobs.append((filename, block_to_atlas_prompt(body)))
    return jobs


def generate_one(api_key: str, filename: str, prompt: str, attempts: int = 4) -> bool:
    out = OUT / filename
    if out.exists() and out.stat().st_size > 10_000:
        print(f"[skip] {filename} already exists")
        return True

    cmd = [
        sys.executable,
        str(ATLAS),
        prompt,
        "--api-key",
        api_key,
        "--provider",
        "gpt-image-2",
        "--size",
        "1536x1024",
        "--format",
        "png",
        "--poll-interval",
        "5",
        "--max-attempts",
        "240",
        "--output",
        str(out),
    ]

    for attempt in range(1, attempts + 1):
        print(f"\n=== {filename} attempt {attempt}/{attempts} ===")
        print(f"prompt[:120]= {prompt[:120]}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            if result.returncode == 0 and out.exists() and out.stat().st_size > 10_000:
                print(result.stdout)
                print(f"[ok] {out}")
                return True
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"[timeout] {filename}", file=sys.stderr)
        if out.exists() and out.stat().st_size <= 10_000:
            out.unlink(missing_ok=True)
        time.sleep(8 * attempt)
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <atlas-api-key>", file=sys.stderr)
        return 1
    api_key = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = collect_jobs()
    print(f"Found {len(jobs)} figures to generate")

    failed: list[str] = []
    for i, (filename, prompt) in enumerate(jobs, 1):
        print(f"\n--- [{i}/{len(jobs)}] {filename} ---")
        if not generate_one(api_key, filename, prompt):
            failed.append(filename)
        time.sleep(3)

    ok = len(jobs) - len(failed)
    print(f"\n=== Summary: {ok}/{len(jobs)} succeeded ===")
    if failed:
        print("Failed:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
