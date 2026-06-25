"""协议适配层（Demo：路由到 Registry 或 Handoff）。

关联章节：Ch.29 · §6 协议适配层
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from core.registry import ToolRegistry


class ProtocolKind(str, Enum):
    """支持的互操作协议类型。"""

    MCP = "mcp"
    A2A = "a2a"
    INTERNAL = "internal"


@dataclass
class ProtocolAdapter:
    """将外部协议调用归一化为 Registry ``invoke``。"""

    registry: ToolRegistry
    default_version: str = "v1"

    def invoke_tool(
        self,
        protocol: ProtocolKind,
        tool_name: str,
        args: dict[str, Any],
        *,
        version: str | None = None,
    ) -> Any:
        """按协议类型解析工具名并调用 Registry。

        Args:
            protocol: 协议种类；MCP 工具名通常已带 ``mcp_`` 前缀。
            tool_name: 逻辑工具名。
            args: 调用参数。
            version: 可选版本覆盖。

        Returns:
            Registry ``invoke`` 的 output。
        """
        ver = version or self.default_version
        resolved = tool_name
        if protocol is ProtocolKind.MCP and not tool_name.startswith("mcp_"):
            resolved = f"mcp_db_{tool_name}"
        result = self.registry.invoke(resolved, ver, args)
        return result.output
