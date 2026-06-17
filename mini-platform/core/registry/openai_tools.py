"""ToolSpec 与 OpenAI Function Calling 工具定义的互转。

关联章节：Ch.23 · §3 Function Calling Schema
"""
from __future__ import annotations

from typing import Any

from core.registry.tool_registry import ToolSpec


def to_openai_tool(spec: ToolSpec, *, strict: bool = False) -> dict[str, Any]:
    """将 ``ToolSpec`` 转为 OpenAI Chat Completions ``tools`` 数组的一项。

    Args:
        spec: 已注册或待注册的工具规格。
        strict: 是否在定义中启用 ``strict``（与 OpenAI Structured Outputs 对齐 [2]）。

    Returns:
        形如 ``{"type": "function", "function": {...}}`` 的字典。
    """
    parameters = dict(spec.parameters_schema)
    if strict and parameters.get("type") == "object":
        parameters.setdefault("additionalProperties", False)

    function_def: dict[str, Any] = {
        "name": spec.name,
        "description": spec.description,
        "parameters": parameters,
    }
    if strict:
        function_def["strict"] = True

    return {"type": "function", "function": function_def}
