"""Run 执行循环：状态机 + Planner + Registry + SSE + 检查点 + HITL。

关联章节：Ch.22 Agent Runtime · §3；Ch.28 Handoff；Ch.30 waiting_human
"""
from __future__ import annotations

from typing import Any, Callable, Protocol

from core.registry import ToolRegistry
from core.registry.errors import RegistryError
from core.runtime.approval import ApprovalRequest, ApprovalStatus, new_approval_id
from core.runtime.checkpoint import CheckpointStore
from core.runtime.run_models import (
    RunContext,
    ToolCallRecord,
    ToolCallStatus,
    new_run_id,
    new_tool_call_id,
)
from core.runtime.run_scope import set_current_run
from core.runtime.sse import format_sse_event
from core.runtime.state_machine import AgentState, AgentStateMachine

EventSink = Callable[[str], None]


class PlannerProtocol(Protocol):
    """Planner 最小接口（Stub / ReAct / MultiAgent 共用）。"""

    def next_step(self, ctx: RunContext) -> Any:
        """产出下一步决策。"""
        ...


class RunLoop:
    """驱动一次 Run：经 Registry 执行工具，支持 Handoff 与 ``waiting_human`` 暂停。"""

    def __init__(
        self,
        registry: ToolRegistry,
        planner: PlannerProtocol,
        checkpoint_store: CheckpointStore | None = None,
        max_steps: int = 20,
        event_sink: EventSink | None = None,
    ) -> None:
        """初始化 Run 循环。

        Args:
            registry: Ch.23 Tool Registry；所有副作用经 ``invoke``。
            planner: 编排决策模块（Ch.25+）。
            checkpoint_store: 检查点存储；默认内存实现。
            max_steps: 最大 Step 数，防止死循环。
            event_sink: SSE 行输出回调；默认 ``print``。
        """
        self._registry = registry
        self._planner = planner
        self._checkpoint_store = checkpoint_store or CheckpointStore()
        self._max_steps = max_steps
        self._event_sink = event_sink or print
        self._sm: AgentStateMachine | None = None
        self._run_ctx: RunContext | None = None

    def run(
        self,
        agent_id: str,
        user_input: str,
        context: dict[str, Any] | None = None,
    ) -> RunContext:
        """启动新 Run，执行至终态或 ``waiting_human`` 暂停。

        Args:
            agent_id: 入口 Agent 标识。
            user_input: 用户任务描述。
            context: 租户 / 权限等透传字段。

        Returns:
            当前 Run 上下文（可能处于 ``waiting_human``）。
        """
        run_ctx = RunContext(
            run_id=new_run_id(),
            agent_id=agent_id,
            input=user_input,
            context=context or {},
            active_agent_id=agent_id,
        )
        run_ctx.append_user_message(user_input)
        sm = AgentStateMachine()
        self._bind(sm, run_ctx)
        self._emit_state(note="run_started")
        sm.fire("start")
        self._save_checkpoint()
        self._emit_state()
        self._drive_loop(from_step=0)
        return run_ctx

    def get_state(self, run_id: str) -> str:
        """读取 Run 当前状态值。

        Args:
            run_id: Run 标识。

        Returns:
            状态字符串，如 ``waiting_human``。
        """
        snapshot = self._checkpoint_store.load(run_id)
        if snapshot is None:
            raise KeyError(f"run not found: {run_id}")
        return snapshot["state"]

    def approve(
        self,
        run_id: str,
        *,
        approver_id: str = "demo-approver",
        comment: str = "",
    ) -> RunContext:
        """人工批准：仅当 Run 处于 ``waiting_human`` 时有效。

        Args:
            run_id: Run 标识。
            approver_id: 审批人 ID。
            comment: 审批意见。

        Returns:
            更新后的 Run 上下文。

        Raises:
            KeyError: Run 不存在。
            ValueError: 当前状态不是 ``waiting_human``。
        """
        self._restore(run_id)
        assert self._sm is not None and self._run_ctx is not None
        if self._sm.state is not AgentState.WAITING_HUMAN:
            raise ValueError(
                f"Run {run_id} is not waiting_human (state={self._sm.state.value})"
            )
        if self._run_ctx.pending_approval is not None:
            self._run_ctx.pending_approval.status = ApprovalStatus.APPROVED
            self._run_ctx.pending_approval.approver_id = approver_id
            self._run_ctx.pending_approval.comment = comment
        self._run_ctx.approval_granted = True
        self._run_ctx.active_agent_id = "workflow_agent"
        self._sm.fire("approved")
        self._save_checkpoint()
        self._emit(
            "approval_result",
            {
                "run_id": run_id,
                "decision": "approved",
                "approver_id": approver_id,
                "comment": comment,
            },
        )
        self._emit_state(note="approved")
        return self._run_ctx

    def reject(
        self,
        run_id: str,
        *,
        approver_id: str = "demo-approver",
        comment: str = "",
    ) -> RunContext:
        """人工驳回：迁移至 ``failed``。

        Args:
            run_id: Run 标识。
            approver_id: 审批人 ID。
            comment: 驳回原因。

        Returns:
            终态 Run 上下文。
        """
        self._restore(run_id)
        assert self._sm is not None and self._run_ctx is not None
        if self._sm.state is not AgentState.WAITING_HUMAN:
            raise ValueError(
                f"Run {run_id} is not waiting_human (state={self._sm.state.value})"
            )
        if self._run_ctx.pending_approval is not None:
            self._run_ctx.pending_approval.status = ApprovalStatus.REJECTED
            self._run_ctx.pending_approval.approver_id = approver_id
            self._run_ctx.pending_approval.comment = comment
        self._sm.fire("rejected")
        self._save_checkpoint()
        self._emit(
            "approval_result",
            {
                "run_id": run_id,
                "decision": "rejected",
                "approver_id": approver_id,
                "comment": comment,
            },
        )
        self._emit_state(note="rejected")
        return self._run_ctx

    def resume(self, run_id: str) -> RunContext:
        """从检查点继续 Run（通常在 ``approve`` 之后调用）。

        Args:
            run_id: Run 标识。

        Returns:
            继续执行后的 Run 上下文。
        """
        self._restore(run_id)
        assert self._run_ctx is not None
        start_step = self._run_ctx.step_index
        self._drive_loop(from_step=start_step)
        return self._run_ctx

    def _bind(self, sm: AgentStateMachine, run_ctx: RunContext) -> None:
        """绑定当前状态机与 Run 上下文。"""
        self._sm = sm
        self._run_ctx = run_ctx

    def _restore(self, run_id: str) -> None:
        """从检查点恢复状态机与 Run 上下文。"""
        snapshot = self._checkpoint_store.load(run_id)
        if snapshot is None:
            raise KeyError(f"run not found: {run_id}")
        run_ctx = RunContext(
            run_id=snapshot["run_id"],
            agent_id=snapshot["agent_id"],
            input=snapshot["input"],
            context=snapshot["context"],
            step_index=snapshot["step_index"],
            answer=snapshot.get("answer"),
            active_agent_id=snapshot.get("active_agent_id", snapshot["agent_id"]),
            handoff_stack=list(snapshot.get("handoff_stack", [])),
            artifacts=dict(snapshot.get("artifacts", {})),
            approval_granted=bool(snapshot.get("approval_granted", False)),
        )
        wm_data = snapshot.get("working_snapshot", [])
        if wm_data:
            run_ctx.working_memory.restore(wm_data)
        pending = snapshot.get("pending_approval")
        if pending:
            run_ctx.pending_approval = ApprovalRequest(
                approval_id=pending["approval_id"],
                run_id=pending["run_id"],
                step_index=pending["step_index"],
                title=pending["title"],
                artifact_ref=pending["artifact_ref"],
                requested_actions=list(pending.get("requested_actions", [])),
                status=ApprovalStatus(pending["status"]),
                approver_id=pending.get("approver_id"),
                comment=pending.get("comment"),
            )
        for item in snapshot.get("tool_calls", []):
            run_ctx.tool_calls.append(
                ToolCallRecord(
                    tool_call_id=item["tool_call_id"],
                    tool=item["tool"],
                    version=item["version"],
                    args=item["args"],
                    status=ToolCallStatus(item["status"]),
                    output=item.get("output"),
                    error=item.get("error"),
                )
            )
        sm = AgentStateMachine.from_state(AgentState(snapshot["state"]))
        sm.history = list(snapshot.get("history", []))
        self._bind(sm, run_ctx)

    def _drive_loop(self, from_step: int) -> None:
        """主循环：直至终态、``waiting_human`` 或 Step 上限。"""
        assert self._sm is not None and self._run_ctx is not None
        steps = from_step
        while not self._sm.is_terminal() and steps < self._max_steps:
            if self._sm.state is AgentState.WAITING_HUMAN:
                break
            if self._sm.state is AgentState.PLANNING:
                self._plan_from_planning()
            elif self._sm.state is AgentState.EXECUTING:
                if self._has_runnable_tool():
                    self._execute_pending_tool()
                    steps += 1
                else:
                    self._plan_from_executing()
            else:
                break

        if (
            not self._sm.is_terminal()
            and self._sm.state is not AgentState.WAITING_HUMAN
            and steps >= self._max_steps
        ):
            self._sm.fire("exec_error")
            self._save_checkpoint()
            self._emit_state(note="max_steps_exceeded")

    def _plan_from_planning(self) -> None:
        """在 ``planning`` 态接收 Planner 的工具调用并进入 ``executing``。"""
        assert self._sm is not None and self._run_ctx is not None
        decision = self._planner.next_step(self._run_ctx)
        if decision.finish:
            self._sm.fire("plan_error")
            self._save_checkpoint()
            self._emit_state()
            return
        record = self._new_tool_call(decision)
        self._run_ctx.tool_calls.append(record)
        self._sm.fire("plan_ready")
        self._save_checkpoint()
        self._emit_action(record)
        self._emit_state()

    def _plan_from_executing(self) -> None:
        """在 ``executing`` 态调用 Planner：结束 Run 或排队下一 Tool Call。"""
        assert self._sm is not None and self._run_ctx is not None
        self._run_ctx.step_index += 1
        decision = self._planner.next_step(self._run_ctx)
        if decision.finish:
            if self._run_ctx.pending_tool_calls():
                raise RuntimeError("Planner FINISH but tool calls still pending")
            self._run_ctx.answer = decision.answer
            self._sm.fire("done")
            self._save_checkpoint()
            self._emit_state(note="finished")
            return
        record = self._new_tool_call(decision)
        self._run_ctx.tool_calls.append(record)
        self._save_checkpoint()
        self._emit_action(record)
        self._emit_state()

    def _execute_pending_tool(self) -> None:
        """执行队首待运行 Tool Call。"""
        assert self._sm is not None and self._run_ctx is not None
        record = self._first_runnable_tool()
        if record is None:
            self._sm.fire("exec_error")
            self._save_checkpoint()
            self._emit_state()
            return

        record.status = ToolCallStatus.RUNNING
        try:
            set_current_run(self._run_ctx)
            output = self._invoke_tool(record)
            record.status = ToolCallStatus.SUCCEEDED
            record.output = output
            self._run_ctx.append_tool_result(record.tool, output)
            if record.tool == "render_report":
                self._run_ctx.artifacts["report"] = output
                self._enter_waiting_human(record)
                return
        except RegistryError as exc:
            record.status = ToolCallStatus.FAILED
            record.error = exc.code
            record.output = {"code": exc.code, "message": exc.message, "details": exc.details}
        finally:
            set_current_run(None)

        self._emit_result(record)
        if record.status is ToolCallStatus.FAILED:
            self._sm.fire("exec_error")
            self._save_checkpoint()
            self._emit_state()
            return
        self._sm.fire("next_step")
        self._save_checkpoint()
        self._emit_state()

    def _enter_waiting_human(self, record: ToolCallRecord) -> None:
        """报告生成后进入人工审批。"""
        assert self._sm is not None and self._run_ctx is not None
        self._emit_result(record)
        approval = ApprovalRequest(
            approval_id=new_approval_id(),
            run_id=self._run_ctx.run_id,
            step_index=self._run_ctx.step_index,
            title="Q1 华东毛利报告发布",
            artifact_ref=f"mem://{self._run_ctx.run_id}/report_md",
            requested_actions=["publish_report"],
        )
        self._run_ctx.pending_approval = approval
        self._sm.fire("need_approval")
        self._save_checkpoint()
        self._emit_state(note="waiting_human")
        self._emit(
            "approval_request",
            {
                "approval_id": approval.approval_id,
                "run_id": approval.run_id,
                "title": approval.title,
                "artifact_ref": approval.artifact_ref,
                "requested_actions": approval.requested_actions,
            },
        )

    def _has_runnable_tool(self) -> bool:
        """是否存在状态为 ``pending`` 的 Tool Call。"""
        return self._first_runnable_tool() is not None

    def _first_runnable_tool(self) -> ToolCallRecord | None:
        """返回第一个待执行的 Tool Call 记录。"""
        assert self._run_ctx is not None
        for record in self._run_ctx.tool_calls:
            if record.status is ToolCallStatus.PENDING:
                return record
        return None

    def _new_tool_call(self, decision) -> ToolCallRecord:
        """由 Planner 决策构造 Tool Call 记录。"""
        return ToolCallRecord(
            tool_call_id=new_tool_call_id(),
            tool=decision.tool or "unknown",
            version=getattr(decision, "version", "v1") or "v1",
            args=decision.args or {},
        )

    def _invoke_tool(self, record: ToolCallRecord) -> Any:
        """经 Registry 调用工具 handler。

        Args:
            record: 待执行的 Tool Call 记录。

        Returns:
            工具结构化输出。

        Raises:
            RegistryError: Registry 校验或调用失败。
        """
        result = self._registry.invoke(record.tool, record.version, record.args)
        return result.output

    def _save_checkpoint(self) -> None:
        """在状态迁移或 Tool 结果后写入检查点。"""
        assert self._sm is not None and self._run_ctx is not None
        ctx = self._run_ctx
        pending = None
        if ctx.pending_approval is not None:
            pa = ctx.pending_approval
            pending = {
                "approval_id": pa.approval_id,
                "run_id": pa.run_id,
                "step_index": pa.step_index,
                "title": pa.title,
                "artifact_ref": pa.artifact_ref,
                "requested_actions": pa.requested_actions,
                "status": pa.status.value,
                "approver_id": pa.approver_id,
                "comment": pa.comment,
            }
        snapshot = {
            "run_id": ctx.run_id,
            "agent_id": ctx.agent_id,
            "state": self._sm.state.value,
            "history": list(self._sm.history),
            "step_index": ctx.step_index,
            "input": ctx.input,
            "context": ctx.context,
            "active_agent_id": ctx.active_agent_id,
            "handoff_stack": list(ctx.handoff_stack),
            "artifacts": dict(ctx.artifacts),
            "approval_granted": ctx.approval_granted,
            "pending_approval": pending,
            "working_snapshot": ctx.working_memory.snapshot(),
            "tool_calls": [
                {
                    "tool_call_id": tc.tool_call_id,
                    "tool": tc.tool,
                    "version": tc.version,
                    "args": tc.args,
                    "status": tc.status.value,
                    "output": tc.output,
                    "error": tc.error,
                }
                for tc in ctx.tool_calls
            ],
            "answer": ctx.answer,
        }
        self._checkpoint_store.save(ctx.run_id, snapshot)

    def _emit_state(
        self,
        note: str | None = None,
    ) -> None:
        """输出 ``state`` SSE 事件。"""
        assert self._sm is not None and self._run_ctx is not None
        data: dict[str, Any] = {
            "run_id": self._run_ctx.run_id,
            "state": self._sm.state.value,
            "step_index": self._run_ctx.step_index,
            "active_agent_id": self._run_ctx.active_agent_id,
        }
        if note:
            data["note"] = note
        self._emit("state", data)

    def _emit_action(self, record: ToolCallRecord) -> None:
        """输出 ``action`` SSE 事件。"""
        assert self._sm is not None and self._run_ctx is not None
        self._emit(
            "action",
            {
                "run_id": self._run_ctx.run_id,
                "state": self._sm.state.value,
                "active_agent_id": self._run_ctx.active_agent_id,
                "tool_call_id": record.tool_call_id,
                "tool": record.tool,
                "version": record.version,
                "args": record.args,
            },
        )

    def _emit_result(self, record: ToolCallRecord) -> None:
        """输出 ``result`` SSE 事件。"""
        assert self._sm is not None and self._run_ctx is not None
        self._emit(
            "result",
            {
                "run_id": self._run_ctx.run_id,
                "state": self._sm.state.value,
                "active_agent_id": self._run_ctx.active_agent_id,
                "tool_call_id": record.tool_call_id,
                "status": record.status.value,
                "output": record.output,
                "error": record.error,
            },
        )

    def _emit(self, event: str, data: dict[str, Any]) -> None:
        """将格式化 SSE 行写入 ``event_sink``。"""
        self._event_sink(format_sse_event(event, data))
