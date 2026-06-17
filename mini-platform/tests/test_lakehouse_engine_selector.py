from infra.lakehouse import Workload, choose_engine, list_workloads, route_query


def test_choose_realtime_bi_engine():
    choice = choose_engine(Workload.REALTIME_BI)
    assert choice.primary == "StarRocks"
    assert "Apache Doris" in choice.alternatives
    assert "高并发" in choice.reason
    assert choice.latency_budget_ms == 3000
    assert choice.max_scan_gb == 200


def test_choose_accepts_string_workload():
    choice = choose_engine("federated_query")
    assert choice.primary == "Trino"


def test_route_query_tightens_latency_budget():
    decision = route_query(
        {"workload": "federated_query", "latency_budget_ms": 5000}
    )
    assert decision["engine"] == "Trino"
    assert decision["latency_budget_ms"] == 5000
    assert decision["latency_feasible"] is False


def test_route_query_uses_policy_budget_by_default():
    decision = route_query({"workload": "realtime_bi"})
    assert decision["engine"] == "StarRocks"
    assert decision["latency_budget_ms"] == 3000
    assert decision["max_scan_gb"] == 200
    assert decision["latency_feasible"] is True


def test_list_workloads_is_stable():
    assert list_workloads() == (
        "platform",
        "cloud_warehouse",
        "realtime_bi",
        "federated_query",
        "event_analytics",
        "local_analytics",
    )
