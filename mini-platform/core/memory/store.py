"""Memory 存储：按 run_id / user_id 索引。

关联章节：Ch.27 Memory
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.memory.working import WorkingMemory


@dataclass
class MemoryStore:
    """内存级 Memory 存储（生产可换 Redis / PG）。"""

    _working: dict[str, WorkingMemory] = field(default_factory=dict)

    def get_working(self, key: str) -> WorkingMemory:
        """获取或创建某 Run/会话的 Working Memory。

        Args:
            key: 通常为 ``run_id`` 或 ``session_id``。

        Returns:
            对应的 ``WorkingMemory`` 实例。
        """
        if key not in self._working:
            self._working[key] = WorkingMemory()
        return self._working[key]

    def save_working(self, key: str, memory: WorkingMemory) -> None:
        """持久化 Working Memory 引用。"""
        self._working[key] = memory

    def delete(self, key: str) -> None:
        """删除某 key 的记忆。"""
        self._working.pop(key, None)
