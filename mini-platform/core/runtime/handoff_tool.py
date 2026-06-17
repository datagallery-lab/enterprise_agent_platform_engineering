"""Handoff 工具 handler：Registry ``handoff@v1`` 实现。

关联章节：Ch.28 · §3 Handoff 契约
"""
from __future__ import annotations

from typing import Any

from core.runtime.run_scope import get_current_run


def handoff_handler(
    to_agent_id: str,
    payload: dict[str, Any] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    """将控制权转移给目标 Agent（同一 ``run_id`` 内）。

    Args:
        to_agent_id: 目标 Agent 标识。
        payload: 结构化交接内容。
        reason: 路由原因，供 Trace 审计。

    Returns:
        Handoff 确认对象。

    Raises:
        RuntimeError: 无活跃 Run 或目标 Agent 非法。
    """
    ctx = get_current_run()
    allowed = {
        "workflow_agent",
        "question_agent",
        "data_agent",
        "report_agent",
    }
    if to_agent_id not in allowed:
        raise ValueError(f"HANDOFF_TARGET_NOT_FOUND: unknown agent {to_agent_id}")

    from_agent = ctx.active_agent_id
    record = {
        "from_agent_id": from_agent,
        "to_agent_id": to_agent_id,
        "payload": payload or {},
        "reason": reason,
        "run_id": ctx.run_id,
    }
    ctx.handoff_stack.append(record)
    ctx.active_agent_id = to_agent_id
    if payload:
        ctx.artifacts.update(payload)
    return {
        "handoff": "ok",
        "from_agent_id": from_agent,
        "to_agent_id": to_agent_id,
    }
