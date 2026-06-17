"""审批请求模型（Demo：内存级，无 HTTP）。

关联章节：Ch.30 Human-in-the-loop
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class ApprovalStatus(str, Enum):
    """审批工单状态。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def new_approval_id() -> str:
    """生成审批工单 ID。

    Returns:
        形如 ``ap-<hex>`` 的字符串。
    """
    return f"ap-{uuid4().hex[:8]}"


@dataclass
class ApprovalRequest:
    """一次 HITL 审批请求（生产建议模型；Demo 由 RunLoop 写入）。"""

    approval_id: str
    run_id: str
    step_index: int
    title: str
    artifact_ref: str
    requested_actions: list[str] = field(default_factory=list)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver_id: str | None = None
    comment: str | None = None
