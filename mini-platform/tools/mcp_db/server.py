"""MCP 数据库工具 Server（Demo：进程内 JSON-RPC 形态，非真实网络）。

关联章节：Ch.24 · §2 Host/Client/Server
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class McpToolDefinition:
    """MCP ``tools/list`` 返回的一项工具定义。"""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class McpDbServer:
    """模拟只读数据库 MCP Server，暴露 ``query_sales`` 工具。"""

    _tools: list[McpToolDefinition] = field(default_factory=list)

    def __post_init__(self) -> None:
        """初始化工具目录。"""
        self._tools = [
            McpToolDefinition(
                name="query_sales",
                description="按区域查询销售额 Top SKU（只读 Demo）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "description": "销售区域，如华东"},
                        "tenant_id": {"type": "string", "description": "租户 ID"},
                    },
                    "required": ["region", "tenant_id"],
                    "additionalProperties": False,
                },
            )
        ]

    def list_tools(self) -> list[dict[str, Any]]:
        """对应 MCP ``tools/list``，返回工具元数据列表。"""
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.input_schema,
            }
            for t in self._tools
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """对应 MCP ``tools/call``，执行工具并返回结构化内容。

        Args:
            name: 工具名。
            arguments: 调用参数。

        Returns:
            MCP 风格的 ``content`` 列表包装结果。

        Raises:
            KeyError: 未知工具名。
            ValueError: 缺少必填参数。
        """
        if name != "query_sales":
            raise KeyError(f"unknown tool: {name}")
        region = arguments.get("region")
        tenant_id = arguments.get("tenant_id")
        if not region or not tenant_id:
            raise ValueError("region and tenant_id are required")
        rows = [
            {"sku": "SKU-A", "sales": 3200, "region": region},
            {"sku": "SKU-B", "sales": 2800, "region": region},
        ]
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"tenant={tenant_id} region={region} top_skus=2",
                }
            ],
            "structuredContent": {"rows": rows, "tenant_id": tenant_id},
        }

    def handle_jsonrpc(self, method: str, params: dict[str, Any]) -> Any:
        """处理简化 JSON-RPC 请求（Demo 传输层）。

        Args:
            method: 如 ``tools/list``、``tools/call``。
            params: 方法参数。

        Returns:
            方法结果对象。
        """
        if method == "tools/list":
            return {"tools": self.list_tools()}
        if method == "tools/call":
            return self.call_tool(params["name"], params.get("arguments", {}))
        raise ValueError(f"unsupported method: {method}")
