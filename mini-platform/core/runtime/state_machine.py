"""Agent 状态机最小可运行 stub。

关联章节：Ch.22 Agent Runtime · L3 工程实现段

v0.1 仅提供枚举与可推进的状态机骨架；后续章节会补充检查点、重试、超时。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class AgentState(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_HUMAN = "waiting_human"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class Transition:
    src: AgentState
    dst: AgentState
    label: str


DEFAULT_TRANSITIONS: tuple[Transition, ...] = (
    Transition(AgentState.PENDING, AgentState.PLANNING, "start"),
    Transition(AgentState.PLANNING, AgentState.EXECUTING, "plan_ready"),
    Transition(AgentState.EXECUTING, AgentState.WAITING_HUMAN, "need_approval"),
    Transition(AgentState.WAITING_HUMAN, AgentState.EXECUTING, "approved"),
    Transition(AgentState.EXECUTING, AgentState.SUCCEEDED, "done"),
    Transition(AgentState.PLANNING, AgentState.FAILED, "plan_error"),
    Transition(AgentState.EXECUTING, AgentState.FAILED, "exec_error"),
)


@dataclass
class AgentStateMachine:
    state: AgentState = AgentState.PENDING
    transitions: tuple[Transition, ...] = DEFAULT_TRANSITIONS
    history: list[tuple[AgentState, str]] = field(default_factory=list)

    def can(self, label: str) -> bool:
        return any(t.src == self.state and t.label == label for t in self.transitions)

    def fire(self, label: str) -> AgentState:
        for t in self.transitions:
            if t.src == self.state and t.label == label:
                self.history.append((self.state, label))
                self.state = t.dst
                return self.state
        raise ValueError(
            f"Invalid transition '{label}' from state '{self.state.value}'"
        )

    def is_terminal(self) -> bool:
        return self.state in (AgentState.SUCCEEDED, AgentState.FAILED)
