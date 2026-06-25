"""工具参数 JSON Schema 子集校验（Demo 级，无第三方依赖）。

关联章节：Ch.23 · §3 Function Calling Schema
"""
from __future__ import annotations

from typing import Any

_SUPPORTED_TYPES = frozenset({"string", "integer", "number", "boolean", "object", "array"})


def validate_parameters(schema: dict[str, Any], args: dict[str, Any]) -> list[str]:
    """按 JSON Schema 子集校验工具调用参数。

    支持 ``type: object``、``properties``、``required`` 及常见标量类型。
    生产环境可替换为完整 JSON Schema 校验库。

    Args:
        schema: ``ToolSpec.parameters_schema``。
        args: Planner / 模型产出的参数字典。

    Returns:
        错误信息列表；空列表表示通过。
    """
    if schema.get("type", "object") != "object":
        return ["root schema must be type object"]
    if not isinstance(args, dict):
        return ["arguments must be a JSON object"]
    return _validate_object(schema, args, path="$")


def _validate_object(
    schema: dict[str, Any],
    value: dict[str, Any],
    path: str,
) -> list[str]:
    """校验 object 类型节点。"""
    errors: list[str] = []
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return [f"{path}: properties must be an object"]

    required = schema.get("required", [])
    if not isinstance(required, list):
        return [f"{path}: required must be an array"]

    for key in required:
        if key not in value:
            errors.append(f"{path}: missing required field '{key}'")

    for key, prop_schema in properties.items():
        if key not in value:
            continue
        if not isinstance(prop_schema, dict):
            errors.append(f"{path}.{key}: invalid property schema")
            continue
        errors.extend(_validate_value(prop_schema, value[key], f"{path}.{key}"))

    if schema.get("additionalProperties") is False:
        allowed = set(properties.keys())
        for key in value:
            if key not in allowed:
                errors.append(f"{path}: unexpected field '{key}'")

    return errors


def _validate_value(schema: dict[str, Any], value: Any, path: str) -> list[str]:
    """校验单个字段值。"""
    expected = schema.get("type")
    if expected not in _SUPPORTED_TYPES:
        return []

    if expected == "string" and not isinstance(value, str):
        return [f"{path}: expected string, got {type(value).__name__}"]
    if expected == "boolean" and not isinstance(value, bool):
        return [f"{path}: expected boolean, got {type(value).__name__}"]
    if expected == "integer" and not (isinstance(value, int) and not isinstance(value, bool)):
        return [f"{path}: expected integer, got {type(value).__name__}"]
    if expected == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return [f"{path}: expected number, got {type(value).__name__}"]
    if expected == "array":
        if not isinstance(value, list):
            return [f"{path}: expected array, got {type(value).__name__}"]
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            errors: list[str] = []
            for idx, item in enumerate(value):
                errors.extend(_validate_value(item_schema, item, f"{path}[{idx}]"))
            return errors
    if expected == "object":
        if not isinstance(value, dict):
            return [f"{path}: expected object, got {type(value).__name__}"]
        return _validate_object(schema, value, path)

    return []
