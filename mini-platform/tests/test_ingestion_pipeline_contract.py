from infra.ingestion import (
    IngestionMode,
    build_pipeline_contract,
    plan_ingestion_pipeline,
)


def test_database_with_primary_key_and_low_latency_uses_cdc():
    decision = plan_ingestion_pipeline(
        {
            "source_kind": "database",
            "freshness_slo_seconds": 60,
            "has_primary_key": True,
            "has_watermark": True,
        }
    )

    assert decision.mode is IngestionMode.CDC
    assert decision.tool == "Debezium"
    assert decision.requires_primary_key is True
    assert decision.freshness_slo_seconds == 60


def test_saas_api_uses_managed_elt_and_hour_floor():
    decision = plan_ingestion_pipeline(
        {
            "source_kind": "saas_api",
            "freshness_slo_seconds": 120,
            "has_primary_key": True,
            "has_watermark": True,
        }
    )

    assert decision.mode is IngestionMode.MANAGED_ELT
    assert decision.tool == "Airbyte or Fivetran"
    assert decision.freshness_slo_seconds == 3600


def test_contract_contains_agent_facing_quality_checks():
    contract = build_pipeline_contract(
        {
            "pipeline_id": "orders-postgres-to-iceberg",
            "source_kind": "database",
            "source": {"type": "postgres", "database": "oms", "table": "public.orders"},
            "destination": {"type": "iceberg", "table": "dwd.orders"},
            "freshness_slo_seconds": 60,
            "has_primary_key": True,
            "primary_key": ("order_id",),
            "expose_to_data_agent": True,
        }
    )

    assert contract.as_dict() == {
        "pipeline_id": "orders-postgres-to-iceberg",
        "source": {"type": "postgres", "database": "oms", "table": "public.orders"},
        "destination": {"type": "iceberg", "table": "dwd.orders"},
        "mode": "cdc",
        "primary_key": ["order_id"],
        "freshness_slo_seconds": 60,
        "expose_to_data_agent": True,
        "quality_checks": [
            "row_count_reconciliation",
            "primary_key_uniqueness",
            "freshness_slo",
            "schema_compatibility",
        ],
    }
