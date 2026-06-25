"""多 Agent 规则 Planner：按 ``active_agent_id`` 驱动 Handoff 与工具调用。

关联章节：Ch.25 Planner · Ch.28 多 Agent · projects/multi-agent-workflow
"""
from __future__ import annotations

from core.planner.base import PlannerDecision
from core.runtime.run_models import RunContext, ToolCallStatus


class MultiAgentPlanner:
    """Part V Demo：Workflow → Question → Data → Report → Publish。"""

    def next_step(self, ctx: RunContext) -> PlannerDecision:
        """根据 ``active_agent_id`` 与 Run 历史产出下一步决策。

        Args:
            ctx: 含 handoff 栈、artifacts 与 tool 历史的 Run 上下文。

        Returns:
            Tool Call 提议或 FINISH。
        """
        agent = ctx.active_agent_id
        if agent == "workflow_agent":
            return self._workflow_step(ctx)
        if agent == "question_agent":
            return self._question_step(ctx)
        if agent == "data_agent":
            return self._data_step(ctx)
        if agent == "report_agent":
            return self._report_step(ctx)
        return PlannerDecision(finish=True, answer=f"未知 Agent：{agent}")

    def _workflow_step(self, ctx: RunContext) -> PlannerDecision:
        """入口 Workflow：审批后发布，否则 Handoff 到 Question。"""
        if ctx.approval_granted:
            if self._agent_finished_tool(ctx, "publish_report"):
                return PlannerDecision(
                    finish=True,
                    answer="报告已审批并发布至 Console",
                    thought="publish_report 已完成",
                )
            report = ctx.artifacts.get("report", {})
            report_md = report.get("report_md", "")
            tenant_id = ctx.context.get("tenant_id", "t-demo")
            return PlannerDecision(
                finish=False,
                tool="publish_report",
                version="v1",
                args={"report_md": report_md, "tenant_id": tenant_id},
                thought="审批已通过，发布报告",
            )
        if self._agent_finished_tool(ctx, "handoff", {"to_agent_id": "question_agent"}):
            return PlannerDecision(
                finish=True,
                answer="工作流异常：Question 阶段未完成",
            )
        return PlannerDecision(
            finish=False,
            tool="handoff",
            version="v1",
            args={
                "to_agent_id": "question_agent",
                "payload": {"intent": ctx.input},
                "reason": "用户问题需澄清",
            },
            thought="路由到 Question Agent 澄清意图",
        )

    def _question_step(self, ctx: RunContext) -> PlannerDecision:
        """Question Agent：产出 query_spec 并 Handoff 到 Data。"""
        if self._agent_finished_tool(ctx, "handoff", {"to_agent_id": "data_agent"}):
            return PlannerDecision(finish=True, answer="Question 阶段已完成")
        query_spec = {
            "region": "华东",
            "metric": "gross_margin",
            "period": "Q1",
            "intent": ctx.input,
        }
        ctx.artifacts["query_spec"] = query_spec
        return PlannerDecision(
            finish=False,
            tool="handoff",
            version="v1",
            args={
                "to_agent_id": "data_agent",
                "payload": {"query_spec": query_spec},
                "reason": "意图已澄清，交由 Data Agent",
            },
            thought="槽位已齐，Handoff 到 Data",
        )

    def _data_step(self, ctx: RunContext) -> PlannerDecision:
        """Data Agent：查 MCP 销售数据，再 Handoff 到 Report。"""
        if self._agent_finished_tool(ctx, "handoff", {"to_agent_id": "report_agent"}):
            return PlannerDecision(finish=True, answer="Data 阶段已完成")
        if not self._agent_finished_tool(ctx, "mcp_db_query_sales"):
            tenant_id = ctx.context.get("tenant_id", "shanlan-retail")
            return PlannerDecision(
                finish=False,
                tool="mcp_db_query_sales",
                version="v1",
                args={"region": "华东", "tenant_id": tenant_id},
                thought="按 query_spec 查询 MCP 只读库",
            )
        metrics = ctx.artifacts.get("metrics")
        if not metrics and ctx.tool_results:
            metrics = ctx.tool_results[-1]
            ctx.artifacts["metrics"] = metrics
        return PlannerDecision(
            finish=False,
            tool="handoff",
            version="v1",
            args={
                "to_agent_id": "report_agent",
                "payload": {"metrics": metrics},
                "reason": "数据就绪，生成报告",
            },
            thought="Handoff 到 Report Agent",
        )

    def _report_step(self, ctx: RunContext) -> PlannerDecision:
        """Report Agent：渲染报告草稿（RunLoop 将进入 waiting_human）。"""
        if self._agent_finished_tool(ctx, "render_report"):
            return PlannerDecision(
                finish=True,
                answer="报告已生成，等待人工审批",
            )
        metrics = ctx.artifacts.get("metrics", {})
        rows = metrics.get("rows", []) if isinstance(metrics, dict) else []
        summary = (
            f"华东 Q1 毛利下滑；Top SKU 样本 {len(rows)} 条。"
            "建议补货审查与竞品对照。"
        )
        return PlannerDecision(
            finish=False,
            tool="render_report",
            version="v1",
            args={"summary": summary, "format": "markdown"},
            thought="汇总指标生成 Markdown 草稿",
        )

    def _agent_finished_tool(
        self,
        ctx: RunContext,
        tool: str,
        args_match: dict | None = None,
    ) -> bool:
        """判断当前 Agent 是否已成功执行指定工具。

        Args:
            ctx: Run 上下文。
            tool: 工具名。
            args_match: 可选 args 子集匹配。

        Returns:
            若存在成功记录且 args 匹配则为 ``True``。
        """
        for record in ctx.tool_calls:
            if record.status is not ToolCallStatus.SUCCEEDED:
                continue
            if record.tool != tool:
                continue
            if args_match:
                if not all(record.args.get(k) == v for k, v in args_match.items()):
                    continue
            return True
        return False
