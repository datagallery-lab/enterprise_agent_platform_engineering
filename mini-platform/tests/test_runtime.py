from core.runtime import AgentState, AgentStateMachine


def test_happy_path():
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
