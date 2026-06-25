"""Planner 配置与增强模式开关。

关联章节：Ch.25 Planner · Ch.26 Agentic Workflow
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PlannerMode(str, Enum):
    """编排模式。"""

    REACT = "react"
    PLAN_AND_EXECUTE = "plan_and_execute"


@dataclass
class PlannerEnhancementFlags:
    """Agentic 增强环开关；生产默认全部关闭（Ch.26）。"""

    reflexion: bool = False
    self_refine: bool = False
    tree_of_thoughts: bool = False


@dataclass
class PlannerConfig:
    """Planner 运行时配置。"""

    mode: PlannerMode = PlannerMode.REACT
    max_steps: int = 12
    enhancements: PlannerEnhancementFlags = field(default_factory=PlannerEnhancementFlags)
    default_tool_version: str = "v1"
