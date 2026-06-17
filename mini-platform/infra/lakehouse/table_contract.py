"""Minimal lakehouse table contract helpers for Ch.11."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TableFormat(str, Enum):
    ICEBERG = "iceberg"
    HUDI = "hudi"
    DELTA = "delta"
    PAIMON = "paimon"


@dataclass(frozen=True)
class LakehouseTableContract:
    table: str
    table_format: TableFormat
    catalog: str
    snapshot_id: str
    primary_key: tuple[str, ...]
    partition_fields: tuple[str, ...]
    schema_version: str
    data_freshness_seconds: int
    time_travel_enabled: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "table": self.table,
            "table_format": self.table_format.value,
            "catalog": self.catalog,
            "snapshot_id": self.snapshot_id,
            "primary_key": list(self.primary_key),
            "partition_fields": list(self.partition_fields),
            "schema_version": self.schema_version,
            "data_freshness_seconds": self.data_freshness_seconds,
            "time_travel_enabled": self.time_travel_enabled,
        }


def build_lakehouse_table_contract(request: dict[str, Any]) -> LakehouseTableContract:
    """Create the minimal table contract consumed by engine routing and Agent tools."""

    table_format = TableFormat(request.get("table_format", "iceberg"))
    snapshot_id = str(request["snapshot_id"])

    return LakehouseTableContract(
        table=request["table"],
        table_format=table_format,
        catalog=request.get("catalog", "local"),
        snapshot_id=snapshot_id,
        primary_key=tuple(request.get("primary_key", ())),
        partition_fields=tuple(request.get("partition_fields", ())),
        schema_version=request.get("schema_version", "v1"),
        data_freshness_seconds=int(request.get("data_freshness_seconds", 86_400)),
        time_travel_enabled=table_format
        in {TableFormat.ICEBERG, TableFormat.DELTA, TableFormat.HUDI},
    )


def validate_agent_readiness(contract: LakehouseTableContract) -> dict[str, Any]:
    """Return readiness signals before a table is exposed to DataAgent."""

    missing: list[str] = []
    if not contract.primary_key:
        missing.append("primary_key")
    if not contract.partition_fields:
        missing.append("partition_fields")
    if contract.data_freshness_seconds > 3600:
        missing.append("freshness_slo")
    if not contract.time_travel_enabled:
        missing.append("time_travel")

    return {
        "table": contract.table,
        "ready": not missing,
        "missing_controls": tuple(missing),
        "snapshot_id": contract.snapshot_id,
    }
