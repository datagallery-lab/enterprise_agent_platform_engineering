"""Planner 抽象接口。

关联章节：Ch.25 · §1 职责与边界
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class PlannerDecision:
    """Planner 单步输出。"""

    finish: bool
    tool: str | None = None
    version: str = "v1"
    args: dict[str, Any] | None = None
    answer: str | None = None
    thought: str | None = None


class PlannerContext(Protocol):
    """Planner 可见上下文（Run 输入 + 工具历史）。"""

    @property
    def input(self) -> str: ...

    @property
    def step_index(self) -> int: ...

    @property
    def tool_results(self) -> list[dict[str, Any]]: ...


class BasePlanner(ABC):
    """Planner 基类：只产出决策，不执行工具。"""

    @abstractmethod
    def next_step(self, ctx: PlannerContext) -> PlannerDecision:
        """根据上下文产出下一步决策。

        Args:
            ctx: 含用户输入与历史 Tool 结果的上下文。

        Returns:
            工具调用或结束信号。
        """
