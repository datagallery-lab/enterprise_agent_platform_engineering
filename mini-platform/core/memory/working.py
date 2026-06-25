"""短期工作记忆（Working Memory）。

关联章节：Ch.27 Memory · §2 短期记忆
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    """消息角色。"""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


@dataclass
class MemoryMessage:
    """一条可写入检查点的记忆消息。"""

    role: MessageRole
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkingMemory:
    """单次 Run 或会话内的短期上下文。"""

    messages: list[MemoryMessage] = field(default_factory=list)
    max_messages: int = 50

    def append(self, message: MemoryMessage) -> None:
        """追加消息并在超限时丢弃最旧条目。

        Args:
            message: 新消息。
        """
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def snapshot(self) -> list[dict[str, Any]]:
        """导出可 JSON 序列化的检查点片段。"""
        return [
            {"role": m.role.value, "content": m.content, "metadata": m.metadata}
            for m in self.messages
        ]

    def restore(self, data: list[dict[str, Any]]) -> None:
        """从检查点片段恢复。"""
        self.messages = [
            MemoryMessage(
                role=MessageRole(item["role"]),
                content=item["content"],
                metadata=item.get("metadata", {}),
            )
            for item in data
        ]
