"""Minimal ingestion contract and planning rules for Ch.10.

The module intentionally avoids external services. It captures the stable
contract a platform exposes after choosing batch, incremental batch, CDC, or
managed ELT for a dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SourceKind(str, Enum):
    DATABASE = "database"
    SAAS_API = "saas_api"
    FILE = "file"
    EVENT_STREAM = "event_stream"


class IngestionMode(str, Enum):
    BATCH = "batch"
    INCREMENTAL_BATCH = "incremental_batch"
    CDC = "cdc"
    MANAGED_ELT = "managed_elt"
    EVENT_STREAM = "event_stream"


@dataclass(frozen=True)
class PipelineDecision:
    mode: IngestionMode
    tool: str
    reason: str
    freshness_slo_seconds: int
    requires_primary_key: bool
    requires_watermark: bool


@dataclass(frozen=True)
class PipelineContract:
    pipeline_id: str
    source: dict[str, str]
    destination: dict[str, str]
    mode: IngestionMode
    primary_key: tuple[str, ...]
    freshness_slo_seconds: int
    expose_to_data_agent: bool
    quality_checks: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "source": self.source,
            "destination": self.destination,
            "mode": self.mode.value,
            "primary_key": list(self.primary_key),
            "freshness_slo_seconds": self.freshness_slo_seconds,
            "expose_to_data_agent": self.expose_to_data_agent,
            "quality_checks": list(self.quality_checks),
        }


def plan_ingestion_pipeline(request: dict[str, Any]) -> PipelineDecision:
    """Return a first-pass ingestion mode for a source dataset."""

    source_kind = SourceKind(request["source_kind"])
    freshness = int(request.get("freshness_slo_seconds", 86_400))
    has_primary_key = bool(request.get("has_primary_key", False))
    has_watermark = bool(request.get("has_watermark", False))

    if source_kind is SourceKind.DATABASE and freshness <= 300 and has_primary_key:
        return PipelineDecision(
            mode=IngestionMode.CDC,
            tool="Debezium",
            reason="数据库关键事实表需要分钟级新鲜度，且具备稳定主键。",
            freshness_slo_seconds=freshness,
            requires_primary_key=True,
            requires_watermark=False,
        )

    if source_kind is SourceKind.SAAS_API:
        return PipelineDecision(
            mode=IngestionMode.MANAGED_ELT,
            tool="Airbyte or Fivetran",
            reason="SaaS API 更受限于分页、限流和连接器质量，托管或连接器平台更自然。",
            freshness_slo_seconds=max(freshness, 3600),
            requires_primary_key=has_primary_key,
            requires_watermark=True,
        )

    if source_kind is SourceKind.EVENT_STREAM:
        return PipelineDecision(
            mode=IngestionMode.EVENT_STREAM,
            tool="Kafka plus stream processor",
            reason="业务事件已经以事件流产生，应保留可重放日志并交给 Ch.13 实时链路处理。",
            freshness_slo_seconds=freshness,
            requires_primary_key=False,
            requires_watermark=False,
        )

    if has_watermark:
        return PipelineDecision(
            mode=IngestionMode.INCREMENTAL_BATCH,
            tool="batch extractor",
            reason="源数据有稳定水印字段，适合用增量批同步控制成本和复杂度。",
            freshness_slo_seconds=max(freshness, 1800),
            requires_primary_key=has_primary_key,
            requires_watermark=True,
        )

    return PipelineDecision(
        mode=IngestionMode.BATCH,
        tool="batch extractor",
        reason="缺少稳定水印或主键时，先用可审计批同步和对账保证完整性。",
        freshness_slo_seconds=max(freshness, 86_400),
        requires_primary_key=False,
        requires_watermark=False,
    )


def build_pipeline_contract(request: dict[str, Any]) -> PipelineContract:
    """Build a DataAgent-facing ingestion contract from a planning request."""

    decision = plan_ingestion_pipeline(request)
    primary_key = tuple(request.get("primary_key", ()))
    quality_checks = (
        "row_count_reconciliation",
        "primary_key_uniqueness" if primary_key else "source_file_completeness",
        "freshness_slo",
        "schema_compatibility",
    )

    return PipelineContract(
        pipeline_id=request["pipeline_id"],
        source=request["source"],
        destination=request["destination"],
        mode=decision.mode,
        primary_key=primary_key,
        freshness_slo_seconds=decision.freshness_slo_seconds,
        expose_to_data_agent=bool(request.get("expose_to_data_agent", False)),
        quality_checks=quality_checks,
    )
