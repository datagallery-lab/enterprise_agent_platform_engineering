"""Demo 内置工具 handler（Ch.23 起改由 Registry 解析）。

关联章节：Ch.22 Agent Runtime · §3 Tool Call 执行
"""
from __future__ import annotations

from typing import Any


def echo_handler(message: str) -> dict[str, Any]:
    """回显输入消息，模拟无副作用工具。

    Args:
        message: 来自 Planner 的参数。

    Returns:
        结构化工具输出。
    """
    return {"echo": message, "length": len(message)}


DEMO_HANDLERS: dict[tuple[str, str], object] = {
    ("echo", "v1"): echo_handler,
}
