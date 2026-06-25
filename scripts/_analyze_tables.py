#!/usr/bin/env python3
"""分析章节中的机械表题与表内容，辅助修订。只读，不修改文件。

用法：
    python3 scripts/_analyze_tables.py docs/part01-overview/ch/ch02-agent.md
输出每张表：行号、当前表题、表头行、首行数据，便于据内容重命名。
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

TABLE_TITLE = re.compile(r"^\*表(\d+)-(\d+)：(.+?)。来源：(.+?)。?\*\s*$")
MECH_SUFFIX = ["结构化对照", "要点对照", "阶段拆解", "场景分层", "职责分工",
               "指标口径", "判断要点", "风险与控制点"]


def analyze(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    print(f"=== {path} ===")
    n = 0
    for i, line in enumerate(lines):
        m = TABLE_TITLE.match(line.strip())
        if not m:
            continue
        n += 1
        title = m.group(3)
        mech = any(title.endswith(s) for s in MECH_SUFFIX)
        # 找紧随其后的表头行（下一个以 | 开头的行）
        header = ""
        first = ""
        for j in range(i + 1, min(i + 8, len(lines))):
            if lines[j].strip().startswith("|"):
                if not header:
                    header = lines[j].strip()
                elif "---" not in lines[j] and not first:
                    first = lines[j].strip()
                    break
        flag = "  [机械]" if mech else ""
        print(f"\n表{m.group(1)}-{m.group(2)} (行{i+1}){flag}")
        print(f"  题: {title}")
        print(f"  头: {header}")
        if first:
            print(f"  例: {first}")
    print(f"\n共 {n} 张表")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        analyze(Path(arg))
