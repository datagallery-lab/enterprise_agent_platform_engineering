"""Tool 注册中心最小可运行 stub。

关联章节：Ch.23 Tool Registry & Function Calling · L3

v0.1 仅支持内存级注册与按 (name, version) 检索。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    version: str
    description: str
    parameters_schema: dict[str, Any]
    handler: Callable[..., Any]


@dataclass
class ToolRegistry:
    _store: dict[tuple[str, str], ToolSpec] = field(default_factory=dict)

    def register(self, spec: ToolSpec) -> None:
        key = (spec.name, spec.version)
        if key in self._store:
            raise ValueError(f"Tool {spec.name}@{spec.version} already registered")
        self._store[key] = spec

    def get(self, name: str, version: str) -> ToolSpec:
        try:
            return self._store[(name, version)]
        except KeyError as exc:
            raise LookupError(f"Tool {name}@{version} not found") from exc

    def list_versions(self, name: str) -> list[str]:
        return sorted(v for (n, v) in self._store.keys() if n == name)

    def __len__(self) -> int:
        return len(self._store)
