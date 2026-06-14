from infra.lakehouse import build_lakehouse_table_contract, validate_agent_readiness


def test_build_iceberg_contract_is_agent_ready():
    contract = build_lakehouse_table_contract(
        {
            "table": "dwd.orders",
            "table_format": "iceberg",
            "catalog": "demo",
            "snapshot_id": "742",
            "primary_key": ("order_id",),
            "partition_fields": ("order_date",),
            "schema_version": "orders.v7",
            "data_freshness_seconds": 60,
        }
    )

    assert contract.as_dict()["table_format"] == "iceberg"
    assert contract.time_travel_enabled is True
    assert validate_agent_readiness(contract) == {
        "table": "dwd.orders",
        "ready": True,
        "missing_controls": (),
        "snapshot_id": "742",
    }


def test_missing_controls_block_agent_readiness():
    contract = build_lakehouse_table_contract(
        {
            "table": "ods.raw_clicks",
            "table_format": "paimon",
            "snapshot_id": "latest",
            "data_freshness_seconds": 7200,
        }
    )

    readiness = validate_agent_readiness(contract)
    assert readiness["ready"] is False
    assert readiness["missing_controls"] == (
        "primary_key",
        "partition_fields",
        "freshness_slo",
        "time_travel",
    )
