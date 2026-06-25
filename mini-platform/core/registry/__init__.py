"""Tool / Agent Registry — 能力注册、Schema、版本治理。

关联章节：Ch.23 Tool Registry & Function Calling
"""

from .errors import (
    ArgumentInvalidError,
    RegistryError,
    ToolNotFoundError,
    ToolUnavailableError,
)
from .openai_tools import to_openai_tool
from .tool_registry import InvokeResult, ToolRegistry, ToolSpec

__all__ = [
    "ArgumentInvalidError",
    "InvokeResult",
    "RegistryError",
    "ToolNotFoundError",
    "ToolUnavailableError",
    "ToolRegistry",
    "ToolSpec",
    "to_openai_tool",
]
