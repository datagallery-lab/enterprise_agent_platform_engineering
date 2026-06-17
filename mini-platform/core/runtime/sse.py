"""SSE 事件格式化（Demo 打印用，非 HTTP 服务）。

关联章节：Ch.22 Agent Runtime · §1 SSE / §3 事件流
"""
from __future__ import annotations

import json
from typing import Any


def format_sse_event(event: str, data: dict[str, Any]) -> str:
    """将一条 SSE 事件格式化为可打印文本。

    Args:
        event: 事件名，如 ``state``、``action``、``result``。
        data: 事件 payload，将序列化为 JSON。

    Returns:
        符合 SSE 语法的两行文本（``event`` + ``data``）。
    """
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n"
