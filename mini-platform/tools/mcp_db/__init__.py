"""MCP 数据库工具服务（Demo 级进程内实现）。

关联章节：Ch.24 MCP 与企业工具生态
"""

from .client import McpDbClient
from .registry_bridge import register_mcp_tools
from .server import McpDbServer

__all__ = ["McpDbClient", "McpDbServer", "register_mcp_tools"]
