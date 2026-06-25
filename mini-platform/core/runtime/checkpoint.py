"""检查点存储（Demo 级内存实现，可选目录持久化）。

关联章节：Ch.22 Agent Runtime · §4 检查点与持久化
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CheckpointStore:
    """按 ``run_id`` 追加保存 Run 快照；可选写入目录供跨进程 ``approve``。"""

    _history: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    persist_dir: Path | None = None

    def save(self, run_id: str, snapshot: dict[str, Any]) -> None:
        """追加一次检查点快照。

        Args:
            run_id: Run 标识。
            snapshot: 可 JSON 序列化的状态快照。
        """
        self._history.setdefault(run_id, []).append(snapshot)
        if self.persist_dir is not None:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            path = self.persist_dir / f"{run_id}.json"
            path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, run_id: str) -> dict[str, Any] | None:
        """读取该 Run 最近一次检查点。

        Args:
            run_id: Run 标识。

        Returns:
            最新快照；不存在时返回 ``None``。
        """
        items = self._history.get(run_id)
        if items:
            return items[-1]
        if self.persist_dir is not None:
            path = self.persist_dir / f"{run_id}.json"
            if path.is_file():
                return json.loads(path.read_text(encoding="utf-8"))
        return None

    def list_for_run(self, run_id: str) -> list[dict[str, Any]]:
        """返回某 Run 的全部检查点序列（便于恢复与测试）。"""
        return list(self._history.get(run_id, []))

    def count(self) -> int:
        """返回所有 Run 累计写入的快照条数。"""
        return sum(len(items) for items in self._history.values())
