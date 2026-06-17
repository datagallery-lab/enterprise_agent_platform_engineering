"""Agent Runtime — 任务执行、状态机、检查点、失败恢复。

关联章节：Ch.22 Agent Runtime
"""

from .approval import ApprovalRequest, ApprovalStatus
from .checkpoint import CheckpointStore
from .run_loop import RunLoop
from .run_models import RunContext, ToolCallRecord, ToolCallStatus
from .state_machine import AgentState, AgentStateMachine, Transition

__all__ = [
    "AgentState",
    "AgentStateMachine",
    "ApprovalRequest",
    "ApprovalStatus",
    "CheckpointStore",
    "RunContext",
    "RunLoop",
    "ToolCallRecord",
    "ToolCallStatus",
    "Transition",
]
