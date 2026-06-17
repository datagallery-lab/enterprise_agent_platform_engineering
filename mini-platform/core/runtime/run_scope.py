"""Run 调用作用域：供 Registry handler（如 handoff）访问当前 RunContext。

关联章节：Ch.28 · Handoff Tool Call
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.runtime.run_models import RunContext

_current_run: RunContext | None = None


def set_current_run(ctx: RunContext | None) -> None:
    """绑定当前 Run 上下文（RunLoop 在 invoke 前后调用）。

    Args:
        ctx: 活跃 ``RunContext``；``None`` 表示清除。
    """
    global _current_run
    _current_run = ctx


def get_current_run() -> RunContext:
    """返回当前 Run 上下文。

    Returns:
        活跃 ``RunContext``。

    Raises:
        RuntimeError: 无活跃 Run。
    """
    if _current_run is None:
        raise RuntimeError("No active RunContext in run_scope")
    return _current_run
