from infra.ingestion import build_pipeline_contract, plan_ingestion_pipeline


def main() -> None:
    request = {
        "pipeline_id": "orders-postgres-to-iceberg",
        "source_kind": "database",
        "source": {"type": "postgres", "database": "oms", "table": "public.orders"},
        "destination": {"type": "iceberg", "table": "dwd.orders"},
        "freshness_slo_seconds": 60,
        "has_primary_key": True,
        "has_watermark": True,
        "primary_key": ("order_id",),
        "expose_to_data_agent": True,
    }

    decision = plan_ingestion_pipeline(request)
    contract = build_pipeline_contract(request)
    data = contract.as_dict()

    print(f"{data['pipeline_id']} -> {data['mode']}")
    print(f"tool={decision.tool} freshness={data['freshness_slo_seconds']}s")
    print(f"checks={','.join(data['quality_checks'])}")


if __name__ == "__main__":
    main()
