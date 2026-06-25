"""ReAct 模式 Planner（Demo：规则驱动，无真实 LLM）。

关联章节：Ch.25 · §2 ReAct
"""
from __future__ import annotations

from core.planner.base import BasePlanner, PlannerContext, PlannerDecision
from core.planner.config import PlannerConfig


class ReActPlanner(BasePlanner):
    """边推理边行动：先调数据工具，再汇总结束。"""

    def __init__(self, config: PlannerConfig | None = None) -> None:
        """初始化 ReAct Planner。

        Args:
            config: 规划配置；默认 ``PlannerConfig()``。
        """
        self._config = config or PlannerConfig()

    def next_step(self, ctx: PlannerContext) -> PlannerDecision:
        """两步 happy path：query → finish。"""
        if ctx.step_index == 0:
            return PlannerDecision(
                finish=False,
                tool="echo",
                version=self._config.default_tool_version,
                args={"message": ctx.input},
                thought="需要先获取用户问题文本作为下游查询输入",
            )
        if ctx.tool_results:
            last = ctx.tool_results[-1]
            text = last.get("echo", str(last))
            return PlannerDecision(
                finish=True,
                answer=f"分析完成：{text}",
                thought="工具已返回，可以结束 Run",
            )
        return PlannerDecision(finish=True, answer="分析完成（无工具输出）")
