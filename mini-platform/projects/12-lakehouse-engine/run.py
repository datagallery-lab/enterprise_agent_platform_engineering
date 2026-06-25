from infra.lakehouse import choose_engine, route_query


def main() -> None:
    for workload in ("realtime_bi", "federated_query", "local_analytics"):
        choice = choose_engine(workload)
        print(f"{workload} -> {choice.primary}")

    decision = route_query(
        {
            "principal": "user:finance_analyst_01",
            "workload": "realtime_bi",
            "latency_budget_ms": 1500,
        }
    )
    print(
        "route realtime_bi@1500ms -> "
        f"{decision['engine']} "
        f"budget={decision['latency_budget_ms']}ms "
        f"feasible={decision['latency_feasible']}"
    )


if __name__ == "__main__":
    main()
