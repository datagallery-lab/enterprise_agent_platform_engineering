"""Plan-and-Execute 模式 Planner（Demo：先产出计划再逐步执行）。

关联章节：Ch.25 · §3 Plan-and-Execute
"""
from __future__ import annotations

from core.planner.base import BasePlanner, PlannerContext, PlannerDecision
from core.planner.config import PlannerConfig


class PlanAndExecutePlanner(BasePlanner):
    """先规划步骤列表，再按步调用工具；适合可审计场景。"""

    def __init__(self, config: PlannerConfig | None = None) -> None:
        """初始化 P&E Planner。"""
        self._config = config or PlannerConfig()
        self._plan: list[dict[str, str]] | None = None
        self._plan_index = 0

    def next_step(self, ctx: PlannerContext) -> PlannerDecision:
        """生成或执行计划中的当前步。"""
        if self._plan is None:
            self._plan = [
                {"tool": "echo", "purpose": "确认任务描述"},
            ]
            self._plan_index = 0
            return PlannerDecision(
                finish=False,
                tool="echo",
                version=self._config.default_tool_version,
                args={"message": ctx.input},
                thought=f"计划共 {len(self._plan)} 步，执行第 1 步",
            )
        if ctx.tool_results and self._plan_index < len(self._plan):
            self._plan_index += 1
        if self._plan_index >= len(self._plan):
            summary = ctx.tool_results[-1] if ctx.tool_results else {}
            text = summary.get("echo", "")
            return PlannerDecision(
                finish=True,
                answer=f"计划执行完毕：{text}",
                thought="计划内步骤已完成",
            )
        step = self._plan[self._plan_index]
        return PlannerDecision(
            finish=False,
            tool=step["tool"],
            version=self._config.default_tool_version,
            args={"message": ctx.input},
            thought=step["purpose"],
        )
