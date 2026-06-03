from core.registry import ToolRegistry, ToolSpec


def _echo(x):
    return x


def test_register_and_get():
    reg = ToolRegistry()
    spec = ToolSpec(
        name="echo",
        version="1.0.0",
        description="echo input",
        parameters_schema={"type": "object", "properties": {"x": {"type": "string"}}},
        handler=_echo,
    )
    reg.register(spec)
    got = reg.get("echo", "1.0.0")
    assert got.handler("hi") == "hi"
    assert reg.list_versions("echo") == ["1.0.0"]
    assert len(reg) == 1


def test_duplicate_register():
    reg = ToolRegistry()
    spec = ToolSpec("a", "1", "", {}, _echo)
    reg.register(spec)
    try:
        reg.register(spec)
    except ValueError:
        return
    raise AssertionError("expected ValueError on duplicate registration")
