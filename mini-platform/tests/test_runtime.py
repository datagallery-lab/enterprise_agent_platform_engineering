from core.registry import ToolRegistry, ToolSpec
from core.runtime import AgentState, AgentStateMachine, CheckpointStore, RunLoop
from core.runtime.demo_tools import echo_handler
from core.runtime.stub_planner import StubPlanner


def _minimal_registry() -> ToolRegistry:
    """构造仅含 echo 的 Registry，供 Stub Planner 单测。"""
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo",
            version="v1",
            description="echo",
            parameters_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "additionalProperties": False,
            },
            handler=echo_handler,
        )
    )
    return registry


def test_happy_path_state_machine_only():
    sm = AgentStateMachine()
    assert sm.state is AgentState.PENDING
    sm.fire("start")
    sm.fire("plan_ready")
    sm.fire("done")
    assert sm.state is AgentState.SUCCEEDED
    assert sm.is_terminal()


def test_invalid_transition():
    sm = AgentStateMachine()
    try:
        sm.fire("done")
    except ValueError:
        return
    raise AssertionError("expected ValueError on invalid transition")


def test_react_loop_transitions():
    sm = AgentStateMachine()
    sm.fire("start")
    sm.fire("plan_ready")
    assert sm.state is AgentState.EXECUTING
    sm.fire("next_step")
    assert sm.state is AgentState.EXECUTING
    sm.fire("done")
    assert sm.state is AgentState.SUCCEEDED


def test_waiting_human_flow():
    sm = AgentStateMachine()
    sm.fire("start")
    sm.fire("plan_ready")
    sm.fire("need_approval")
    assert sm.state is AgentState.WAITING_HUMAN
    sm.fire("approved")
    assert sm.state is AgentState.EXECUTING


def test_run_loop_happy_path():
    store = CheckpointStore()
    events: list[str] = []
    loop = RunLoop(
        registry=_minimal_registry(),
        planner=StubPlanner(),
        checkpoint_store=store,
        event_sink=events.append,
    )
    result = loop.run(agent_id="test-agent", user_input="hello")
    assert result.answer == "任务完成：hello"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].status.value == "succeeded"
    assert store.count() >= 3
    joined = "\n".join(events)
    assert "event: state" in joined
    assert "event: action" in joined
    assert "event: result" in joined
