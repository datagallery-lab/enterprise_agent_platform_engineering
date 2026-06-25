"""Registry 结构化错误，与 Ch.22 Runtime 错误码对齐。

关联章节：Ch.23 Tool Registry · §5 调用链
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegistryError(Exception):
    """Registry 操作失败基类。"""

    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class ToolNotFoundError(RegistryError):
    """工具名或版本未注册。"""

    def __init__(self, name: str, version: str) -> None:
        super().__init__(
            code="TOOL_NOT_FOUND",
            message=f"Tool {name}@{version} not registered",
            details={"tool": name, "version": version},
        )


class ArgumentInvalidError(RegistryError):
    """参数未通过 JSON Schema 校验。"""

    def __init__(self, name: str, version: str, validation_errors: list[str]) -> None:
        super().__init__(
            code="TOOL_ARGUMENT_INVALID",
            message="Tool arguments failed schema validation",
            details={
                "tool": name,
                "version": version,
                "validation_errors": validation_errors,
            },
        )


class ToolUnavailableError(RegistryError):
    """MCP Server 或 transport 不可达时由 handler 抛出（生产路径）。"""

    def __init__(
        self,
        name: str,
        version: str,
        *,
        reason: str = "",
    ) -> None:
        super().__init__(
            code="TOOL_UNAVAILABLE",
            message=f"Tool {name}@{version} unavailable",
            details={"tool": name, "version": version, "reason": reason},
        )
