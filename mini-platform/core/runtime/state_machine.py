"""Agent 状态机：Run 六态枚举、迁移表与 ``fire`` 推进。

六个引擎态（``pending`` / ``planning`` / ``executing`` / ``waiting_human`` /
``succeeded`` / ``failed``）与 Ch.01 §2.3、Ch.22 §2 一致。

关联章节：Ch.22 Agent Runtime · §2 状态机
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
    Transition(AgentState.EXECUTING, AgentState.EXECUTING, "next_step"),
    Transition(AgentState.EXECUTING, AgentState.WAITING_HUMAN, "need_approval"),
    Transition(AgentState.WAITING_HUMAN, AgentState.EXECUTING, "approved"),
    Transition(AgentState.WAITING_HUMAN, AgentState.FAILED, "rejected"),
    Transition(AgentState.EXECUTING, AgentState.SUCCEEDED, "done"),
    Transition(AgentState.PLANNING, AgentState.FAILED, "plan_error"),
    Transition(AgentState.EXECUTING, AgentState.FAILED, "exec_error"),
)


@dataclass
class AgentStateMachine:
    state: AgentState = AgentState.PENDING
    transitions: tuple[Transition, ...] = DEFAULT_TRANSITIONS
    history: list[tuple[AgentState, str]] = field(default_factory=list)

    @classmethod
    def from_state(cls, state: AgentState) -> AgentStateMachine:
        """从给定状态构造状态机（用于检查点恢复）。

        Args:
            state: 恢复后的 Run 状态。

        Returns:
            处于 ``state`` 的状态机实例。
        """
        return cls(state=state)

    def can(self, label: str) -> bool:
        """判断当前状态是否允许触发给定迁移标签。

        Args:
            label: 迁移标签，如 ``start``、``plan_ready``。

        Returns:
            若存在 ``(state, label)`` 合法迁移则为 ``True``。
        """
        return any(t.src == self.state and t.label == label for t in self.transitions)

    def fire(self, label: str) -> AgentState:
        """触发迁移并更新 ``state``。

        Args:
            label: 迁移标签。

        Returns:
            迁移后的新状态。

        Raises:
            ValueError: 当前状态下该标签非法。
        """
        for t in self.transitions:
            if t.src == self.state and t.label == label:
                self.history.append((self.state, label))
                self.state = t.dst
                return self.state
        raise ValueError(
            f"Invalid transition '{label}' from state '{self.state.value}'"
        )

    def is_terminal(self) -> bool:
        """判断 Run 是否已处于终态。

        Returns:
            状态为 ``succeeded`` 或 ``failed`` 时为 ``True``。
        """
        return self.state in (AgentState.SUCCEEDED, AgentState.FAILED)
