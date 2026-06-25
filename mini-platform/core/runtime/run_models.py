"""Run / Step / Tool Call 上下文模型。

关联章节：Ch.22 Agent Runtime · §1 上下文模型
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from core.memory import MemoryMessage, MessageRole, WorkingMemory
from core.runtime.approval import ApprovalRequest


def new_run_id() -> str:
    """生成 Run 唯一标识。

    Returns:
        形如 ``run-<hex>`` 的字符串。
    """
    return f"run-{uuid4().hex[:12]}"


def new_tool_call_id() -> str:
    """生成 Tool Call 唯一标识。

    Returns:
        形如 ``tc-<hex>`` 的字符串。
    """
    return f"tc-{uuid4().hex[:8]}"


class ToolCallStatus(str, Enum):
    """单次工具调用的执行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class ToolCallRecord:
    """一次 Tool Call 的结构化记录，用于审计与检查点。"""

    tool_call_id: str
    tool: str
    version: str
    args: dict[str, Any]
    status: ToolCallStatus = ToolCallStatus.PENDING
    output: Any | None = None
    error: str | None = None


@dataclass
class RunContext:
    """一次 ``/run`` 的运行时上下文（实现 Planner 可见字段）。"""

    run_id: str
    agent_id: str
    input: str
    context: dict[str, Any]
    step_index: int = 0
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    answer: str | None = None
    active_agent_id: str = "workflow_agent"
    handoff_stack: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] = field(default_factory=dict)
    working_memory: WorkingMemory = field(default_factory=WorkingMemory)
    pending_approval: ApprovalRequest | None = None
    approval_granted: bool = False

    @property
    def tool_results(self) -> list[dict[str, Any]]:
        """Planner 可见的历史 Tool 成功输出列表。

        Returns:
            按调用顺序排列的结构化 output。
        """
        results: list[dict[str, Any]] = []
        for record in self.tool_calls:
            if record.status is ToolCallStatus.SUCCEEDED and record.output is not None:
                if isinstance(record.output, dict):
                    results.append(record.output)
                else:
                    results.append({"value": record.output})
        return results

    def pending_tool_calls(self) -> list[ToolCallRecord]:
        """返回尚未成功结束的 Tool Call 列表。

        Returns:
            状态为 pending 或 running 的记录。
        """
        return [
            tc
            for tc in self.tool_calls
            if tc.status in (ToolCallStatus.PENDING, ToolCallStatus.RUNNING)
        ]

    def append_user_message(self, content: str) -> None:
        """将用户输入写入 Working Memory。

        Args:
            content: 用户文本。
        """
        self.working_memory.append(
            MemoryMessage(
                role=MessageRole.USER,
                content=content,
                metadata={"source": "user_input"},
            )
        )

    def append_tool_result(self, tool: str, output: Any) -> None:
        """将 Tool 结果摘要写入 Working Memory。

        Args:
            tool: 工具名。
            output: 工具输出。
        """
        import json

        text = json.dumps(output, ensure_ascii=False) if isinstance(output, dict) else str(output)
        self.working_memory.append(
            MemoryMessage(
                role=MessageRole.TOOL,
                content=text,
                metadata={"source": "tool_result", "tool": tool},
            )
        )


@dataclass(frozen=True)
class PlannerDecision:
    """Planner 单步输出：调用工具或结束 Run（Ch.22 Stub 兼容）。"""

    finish: bool
    tool: str | None = None
    version: str = "v1"
    args: dict[str, Any] | None = None
    answer: str | None = None
