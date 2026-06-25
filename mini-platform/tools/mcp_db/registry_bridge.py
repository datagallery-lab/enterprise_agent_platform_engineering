"""将 MCP 工具注册进 Tool Registry。

关联章节：Ch.24 · §5 MCP Server 与 Registry 集成
"""
from __future__ import annotations

from typing import Any

from core.registry import ToolRegistry, ToolSpec
from tools.mcp_db.client import McpDbClient


def _make_handler(client: McpDbClient, mcp_tool_name: str):
    """为 MCP 工具生成 Registry handler 闭包。"""

    def handler(**kwargs: Any) -> dict[str, Any]:
        """调用 MCP 工具；Demo 仅返回 ``structuredContent`` 供 Registry invoke。"""
        result = client.call_tool(mcp_tool_name, kwargs)
        return result.get("structuredContent", result)

    return handler


def register_mcp_tools(
    registry: ToolRegistry,
    client: McpDbClient,
    *,
    name_prefix: str = "mcp_db",
    version: str = "v1",
) -> int:
    """把 MCP Server 工具批量注册为 ``{prefix}_{tool_name}``。

    Args:
        registry: 目标 Registry。
        client: 已连接的 MCP Client。
        name_prefix: 平台内工具名前缀，避免与内置工具冲突。
        version: 注册版本。

    Returns:
        成功注册的工具数量。
    """
    count = 0
    for tool in client.list_tools():
        platform_name = f"{name_prefix}_{tool['name']}"
        schema = dict(tool["inputSchema"])
        registry.register(
            ToolSpec(
                name=platform_name,
                version=version,
                description=f"[MCP] {tool['description']}",
                parameters_schema=schema,
                handler=_make_handler(client, tool["name"]),
            )
        )
        count += 1
    return count
