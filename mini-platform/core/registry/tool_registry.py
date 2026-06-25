"""Tool 注册中心：注册、检索、校验与调用。

关联章节：Ch.23 Tool Registry & Function Calling
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from core.registry.errors import ArgumentInvalidError, ToolNotFoundError
from core.registry.schema_validate import validate_parameters


@dataclass(frozen=True)
class ToolSpec:
    """平台侧工具能力规格。"""

    name: str
    version: str
    description: str
    parameters_schema: dict[str, Any]
    handler: Callable[..., Any]

    @property
    def key(self) -> tuple[str, str]:
        """返回 ``(name, version)`` 主键。"""
        return (self.name, self.version)


@dataclass
class InvokeResult:
    """一次成功调用的结构化结果。"""

    tool: str
    version: str
    output: Any


@dataclass
class ToolRegistry:
    """内存级 Tool Registry；生产可替换为持久化后端。"""

    _store: dict[tuple[str, str], ToolSpec] = field(default_factory=dict)

    def register(self, spec: ToolSpec) -> None:
        """注册工具；同 ``(name, version)`` 重复注册将失败。

        Args:
            spec: 工具规格。

        Raises:
            ValueError: 主键已存在。
        """
        key = spec.key
        if key in self._store:
            raise ValueError(f"Tool {spec.name}@{spec.version} already registered")
        self._store[key] = spec

    def get(self, name: str, version: str) -> ToolSpec:
        """按名与版本检索工具规格。

        Args:
            name: 工具名。
            version: 版本号。

        Returns:
            匹配的 ``ToolSpec``。

        Raises:
            ToolNotFoundError: 未注册。
        """
        try:
            return self._store[(name, version)]
        except KeyError as exc:
            raise ToolNotFoundError(name, version) from exc

    def list_versions(self, name: str) -> list[str]:
        """列出某工具名的全部已注册版本（升序）。

        Args:
            name: 工具名。

        Returns:
            版本字符串列表。
        """
        return sorted(v for (n, v) in self._store.keys() if n == name)

    def invoke(self, name: str, version: str, args: dict[str, Any]) -> InvokeResult:
        """校验参数并执行 handler。

        Args:
            name: 工具名。
            version: 版本号。
            args: 调用参数（通常来自模型 Function Calling 输出）。

        Returns:
            结构化调用结果。

        Raises:
            ToolNotFoundError: 工具未注册。
            ArgumentInvalidError: 参数未通过 schema 校验。
        """
        spec = self.get(name, version)
        errors = validate_parameters(spec.parameters_schema, args)
        if errors:
            raise ArgumentInvalidError(name, version, errors)
        output = spec.handler(**args)
        return InvokeResult(tool=name, version=version, output=output)

    def __len__(self) -> int:
        return len(self._store)
