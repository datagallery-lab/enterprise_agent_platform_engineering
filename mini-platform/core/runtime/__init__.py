"""Agent Runtime — 任务执行、状态机、检查点、失败恢复。

关联章节：Ch.22 Agent Runtime
"""

from .state_machine import AgentState, AgentStateMachine, Transition

__all__ = ["AgentState", "AgentStateMachine", "Transition"]
