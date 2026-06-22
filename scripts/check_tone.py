#!/usr/bin/env python3
"""Scan Chinese documentation for phrases that violate the book voice guideline."""
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_ROOT = Path("docs")
CONTEXT_TRUNCATE = 100

BANNED_PHRASES = [
    "山岚集团",
    "本章聚焦",
    "章节以",
    "关键问题的分析框架",
    "工程落地、检查项或跨章节衔接",
    "能够把本章方法用于方案评审",
    "进入生产语境后",
    "生产化清单",
    "上线检查清单",
    "L1 概念",
    "L2 架构",
    "L3 工程实现",
    "阅读本章时，可以把",
    "从而理解本章与前后章节的衔接",
    "本节要回答的问题",
    "读图时",
    "沿着图",
    "这也是为什么",
    "换句话说",
    "本质上",
    "真正的关键",
    "本章讨论 Agent 平台的共享能力",
    "本章把模型能力放回企业平台的运行链路中讨论",
    "本章把向量、检索和知识工程放到同一条知识供给链路里看",
    "本章围绕 DataAgent 主线展开",
    "本章关注 Agent 平台运行后的证据体系",
    "本章讨论模型服务与 Agent 平台进入生产环境时的基础设施问题",
    "本章讨论用户能直接感知的交互层",
    "本章讨论平台能力增强以后必须同步建立的风险、合规和组织机制",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan Chinese markdown files for banned template and tone phrases.",
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--list-phrases", action="store_true")
    return parser.parse_args()


def should_scan(path: Path) -> bool:
    if path.suffix != ".md":
        return False
    return "en" not in path.parts


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return hits

    in_code = False
    for lineno, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for phrase in BANNED_PHRASES:
            if phrase in line:
                context = line.strip()
                if len(context) > CONTEXT_TRUNCATE:
                    context = context[:CONTEXT_TRUNCATE] + "..."
                hits.append((lineno, phrase, context))
    return hits


def main() -> int:
    args = parse_args()
    if args.list_phrases:
        print("Banned phrases:")
        for phrase in BANNED_PHRASES:
            print(f"- {phrase}")
        return 0

    total_hits = 0
    files_with_hits: set[Path] = set()
    for path in sorted(args.root.rglob("*.md")):
        if not should_scan(path):
            continue
        hits = scan_file(path)
        if not hits:
            continue
        files_with_hits.add(path)
        for lineno, phrase, context in hits:
            print(f"{path}:{lineno}: {phrase}: {context}")
            total_hits += 1

    if total_hits == 0:
        print("No tone violations found.")
        return 0

    print(f"Found {total_hits} tone-violation hit(s) across {len(files_with_hits)} file(s).")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
