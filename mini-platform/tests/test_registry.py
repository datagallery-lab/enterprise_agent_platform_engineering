from core.registry import (
    ArgumentInvalidError,
    ToolNotFoundError,
    ToolRegistry,
    ToolSpec,
    to_openai_tool,
)


def _echo(message: str):
    return {"echo": message}


def test_register_and_get():
    reg = ToolRegistry()
    spec = ToolSpec(
        name="echo",
        version="v1",
        description="echo input",
        parameters_schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
        handler=_echo,
    )
    reg.register(spec)
    got = reg.get("echo", "v1")
    assert got.handler(message="hi") == {"echo": "hi"}
    assert reg.list_versions("echo") == ["v1"]
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


def test_invoke_success():
    reg = ToolRegistry()
    reg.register(
        ToolSpec(
            name="echo",
            version="v1",
            description="",
            parameters_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
            handler=_echo,
        )
    )
    result = reg.invoke("echo", "v1", {"message": "ok"})
    assert result.output == {"echo": "ok"}


def test_invoke_not_found():
    reg = ToolRegistry()
    try:
        reg.invoke("missing", "v1", {})
    except ToolNotFoundError as exc:
        assert exc.code == "TOOL_NOT_FOUND"
        return
    raise AssertionError("expected ToolNotFoundError")


def test_invoke_invalid_args():
    reg = ToolRegistry()
    reg.register(
        ToolSpec(
            name="echo",
            version="v1",
            description="",
            parameters_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
            handler=_echo,
        )
    )
    try:
        reg.invoke("echo", "v1", {})
    except ArgumentInvalidError as exc:
        assert exc.code == "TOOL_ARGUMENT_INVALID"
        return
    raise AssertionError("expected ArgumentInvalidError")


def test_to_openai_tool():
    spec = ToolSpec(
        name="echo",
        version="v1",
        description="echo",
        parameters_schema={"type": "object", "properties": {"message": {"type": "string"}}},
        handler=_echo,
    )
    tool = to_openai_tool(spec, strict=True)
    assert tool["type"] == "function"
    assert tool["function"]["name"] == "echo"
    assert tool["function"]["strict"] is True
