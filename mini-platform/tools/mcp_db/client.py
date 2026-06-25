"""MCP Client：调用 Server 的 ``tools/list`` 与 ``tools/call``。

关联章节：Ch.24 · §2
"""
from __future__ import annotations

from typing import Any

from tools.mcp_db.server import McpDbServer


class McpDbClient:
    """进程内 MCP Client，直连 ``McpDbServer``（生产为 stdio / Streamable HTTP 传输）。"""

    def __init__(self, server: McpDbServer | None = None) -> None:
        """初始化 Client。

        Args:
            server: MCP Server 实例；默认新建 ``McpDbServer``。
        """
        self._server = server or McpDbServer()

    def list_tools(self) -> list[dict[str, Any]]:
        """拉取 Server 工具列表。"""
        result = self._server.handle_jsonrpc("tools/list", {})
        return result["tools"]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """调用指定工具。"""
        return self._server.handle_jsonrpc(
            "tools/call",
            {"name": name, "arguments": arguments},
        )
