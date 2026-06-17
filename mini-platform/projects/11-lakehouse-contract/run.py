from infra.lakehouse import build_lakehouse_table_contract, validate_agent_readiness


def main() -> None:
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
    readiness = validate_agent_readiness(contract)

    print(
        f"{contract.table} snapshot={contract.snapshot_id} "
        f"format={contract.table_format.value}"
    )
    print(
        f"agent_ready={readiness['ready']} "
        f"missing={readiness['missing_controls']}"
    )


if __name__ == "__main__":
    main()
