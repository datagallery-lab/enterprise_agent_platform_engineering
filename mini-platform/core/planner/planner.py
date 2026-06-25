"""Planner 工厂：按配置选择 ReAct 或 Plan-and-Execute。

关联章节：Ch.25 · §5 编排模式选型
"""
from __future__ import annotations

from core.planner.base import BasePlanner
from core.planner.config import PlannerConfig, PlannerMode
from core.planner.plan_execute import PlanAndExecutePlanner
from core.planner.react_planner import ReActPlanner


def create_planner(config: PlannerConfig | None = None) -> BasePlanner:
    """根据 ``PlannerConfig.mode`` 创建 Planner 实例。

    Args:
        config: 规划配置。

    Returns:
        具体 Planner 实现。
    """
    cfg = config or PlannerConfig()
    if cfg.mode is PlannerMode.PLAN_AND_EXECUTE:
        return PlanAndExecutePlanner(cfg)
    return ReActPlanner(cfg)
