"""Part V Run 链集成测试。

关联章节：projects/multi-agent-workflow
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = _ROOT / "projects" / "multi-agent-workflow"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_PROJECT))

from lib import MultiAgentPlanner, build_workflow_registry  # noqa: E402
from core.runtime import CheckpointStore, RunLoop  # noqa: E402


def test_workflow_run_until_waiting_human():
    events: list[str] = []
    loop = RunLoop(
        registry=build_workflow_registry(),
        planner=MultiAgentPlanner(),
        checkpoint_store=CheckpointStore(),
        event_sink=events.append,
    )
    ctx = loop.run(
        agent_id="workflow_agent",
        user_input="华东区 Q1 毛利下滑？",
        context={"tenant_id": "shanlan-retail"},
    )
    assert loop.get_state(ctx.run_id) == "waiting_human"
    assert ctx.pending_approval is not None
    assert len(ctx.handoff_stack) >= 2
    joined = "\n".join(events)
    assert "event: handoff" not in joined  # handoff 走 action
    assert '"tool": "handoff"' in joined or "handoff" in joined
    assert "approval_request" in joined
    assert any(tc.tool == "render_report" for tc in ctx.tool_calls)


def test_workflow_approve_and_resume():
    store = CheckpointStore()
    loop = RunLoop(
        registry=build_workflow_registry(),
        planner=MultiAgentPlanner(),
        checkpoint_store=store,
        event_sink=lambda _: None,
    )
    ctx = loop.run(
        agent_id="workflow_agent",
        user_input="华东区 Q1 毛利下滑？",
        context={"tenant_id": "shanlan-retail"},
    )
    run_id = ctx.run_id
    loop.approve(run_id, approver_id="u-test", comment="ok")
    ctx = loop.resume(run_id)
    assert loop.get_state(run_id) == "succeeded"
    assert ctx.answer is not None
    assert "发布" in ctx.answer or "报告" in ctx.answer
    assert any(tc.tool == "publish_report" for tc in ctx.tool_calls)


def test_approve_rejects_wrong_state():
    store = CheckpointStore()
    loop = RunLoop(
        registry=build_workflow_registry(),
        planner=MultiAgentPlanner(),
        checkpoint_store=store,
        event_sink=lambda _: None,
    )
    ctx = loop.run(agent_id="workflow_agent", user_input="test", context={"tenant_id": "t1"})
    loop.approve(ctx.run_id, approver_id="u1")
    loop.resume(ctx.run_id)
    try:
        loop.approve(ctx.run_id)
    except ValueError as exc:
        assert "waiting_human" in str(exc)
        return
    raise AssertionError("expected ValueError on double approve")
