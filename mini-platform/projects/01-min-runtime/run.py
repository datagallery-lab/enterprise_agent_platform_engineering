"""Project 01 · 最小可用 Agent Runtime — 状态机驱动 ReAct 循环骨架。

关联章节：Ch.22 Agent Runtime
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.runtime import AgentStateMachine  # noqa: E402


def main() -> None:
    sm = AgentStateMachine()
    print(f"state={sm.state.value}")
    sm.fire("start")
    print(f"state={sm.state.value}")
    sm.fire("plan_ready")
    print(f"state={sm.state.value}")
    sm.fire("done")
    print(f"state={sm.state.value}")
    print(f"done={sm.is_terminal()}")


if __name__ == "__main__":
    main()
