"""Demo 用 Planner：固定两步 happy path，不调用真实 LLM。

关联章节：Ch.22 Agent Runtime · §3 执行循环（Ch.25 替换为真实 Planner）
"""
from __future__ import annotations

from core.runtime.run_models import PlannerDecision, RunContext, ToolCallStatus


class StubPlanner:
    """两步规划：先调工具，再根据工具结果结束。"""

    def next_step(self, run_ctx: RunContext) -> PlannerDecision:
        """根据当前 Run 上下文产出下一步决策。

        Args:
            run_ctx: 含历史 Tool Call 的 Run 上下文。

        Returns:
            第一步返回工具调用；第二步在已有工具结果后返回 FINISH。
        """
        if run_ctx.step_index == 0:
            return PlannerDecision(
                finish=False,
                tool="echo",
                version="v1",
                args={"message": run_ctx.input},
            )
        last = run_ctx.tool_calls[-1] if run_ctx.tool_calls else None
        if last and last.status is ToolCallStatus.SUCCEEDED:
            text = last.output.get("echo", "") if isinstance(last.output, dict) else str(last.output)
            return PlannerDecision(
                finish=True,
                answer=f"任务完成：{text}",
            )
        return PlannerDecision(finish=True, answer="任务完成（无工具输出）")
