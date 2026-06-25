"""协议适配层 — MCP / A2A / Agent Card 统一入口。

关联章节：Ch.29 Agent 协议与标准
"""

from .adapter import ProtocolAdapter, ProtocolKind

__all__ = ["ProtocolAdapter", "ProtocolKind"]
