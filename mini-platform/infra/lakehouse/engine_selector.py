"""Simple lakehouse engine selection rules for Ch.12.

The implementation is intentionally small: it models how a platform team can
turn workload intent into a shortlist of OLAP engines before doing a benchmark.
``choose_engine`` answers "哪个引擎"，``route_query`` 在此基础上叠加延迟与扫描
预算，对应 L2 的受控查询接口契约——只产出路由决策，不真正执行 SQL。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Workload(str, Enum):
    PLATFORM = "platform"
    CLOUD_WAREHOUSE = "cloud_warehouse"
    REALTIME_BI = "realtime_bi"
    FEDERATED_QUERY = "federated_query"
    EVENT_ANALYTICS = "event_analytics"
    LOCAL_ANALYTICS = "local_analytics"


@dataclass(frozen=True)
class EngineChoice:
    primary: str
    alternatives: tuple[str, ...]
    reason: str
    latency_budget_ms: int
    max_scan_gb: int


_RULES: dict[Workload, EngineChoice] = {
    Workload.PLATFORM: EngineChoice(
        primary="Databricks",
        alternatives=("Snowflake", "Trino"),
        reason="统一数据工程、湖仓治理、SQL 分析与 AI/ML 工作负载。",
        latency_budget_ms=60000,
        max_scan_gb=4096,
    ),
    Workload.CLOUD_WAREHOUSE: EngineChoice(
        primary="Snowflake",
        alternatives=("Databricks SQL",),
        reason="托管 SQL 数仓、弹性计算隔离、数据共享与低运维。",
        latency_budget_ms=15000,
        max_scan_gb=2048,
    ),
    Workload.REALTIME_BI: EngineChoice(
        primary="StarRocks",
        alternatives=("Apache Doris", "ClickHouse"),
        reason="高并发看板、低延迟聚合、物化视图和 MySQL 协议生态。",
        latency_budget_ms=3000,
        max_scan_gb=200,
    ),
    Workload.FEDERATED_QUERY: EngineChoice(
        primary="Trino",
        alternatives=("Apache Doris", "Databricks Lakehouse Federation"),
        reason="以连接器访问多源数据，适合作为开放湖仓 SQL 入口。",
        latency_budget_ms=30000,
        max_scan_gb=1024,
    ),
    Workload.EVENT_ANALYTICS: EngineChoice(
        primary="ClickHouse",
        alternatives=("StarRocks", "Apache Doris"),
        reason="日志、事件、时序和大宽表扫描聚合更依赖列存、排序键与数据跳过。",
        latency_budget_ms=5000,
        max_scan_gb=1024,
    ),
    Workload.LOCAL_ANALYTICS: EngineChoice(
        primary="DuckDB",
        alternatives=("ClickHouse local",),
        reason="进程内分析、直接读 Parquet/CSV/JSON，适合 Notebook 与轻量 ETL。",
        latency_budget_ms=10000,
        max_scan_gb=50,
    ),
}


def choose_engine(workload: Workload | str) -> EngineChoice:
    """Return a first-pass engine recommendation for a workload."""

    normalized = Workload(workload)
    return _RULES[normalized]


def route_query(request: dict) -> dict:
    """将一次受控查询请求映射为路由决策（仅决策，不执行 SQL）。

    request 至少包含 ``workload``，可选 ``latency_budget_ms``。当调用方给出的
    延迟预算比平台策略更严格时取更严格者；若调用方预算低于该负载的目标延迟，
    则标记为不可行，提示上层改写查询、加过滤或更换引擎。
    """

    choice = choose_engine(request["workload"])
    requested = request.get("latency_budget_ms")
    effective_budget = choice.latency_budget_ms
    latency_feasible = True
    if requested is not None:
        effective_budget = min(effective_budget, requested)
        latency_feasible = requested >= choice.latency_budget_ms

    return {
        "engine": choice.primary,
        "alternatives": choice.alternatives,
        "latency_budget_ms": effective_budget,
        "max_scan_gb": choice.max_scan_gb,
        "latency_feasible": latency_feasible,
        "reason": choice.reason,
    }


def list_workloads() -> tuple[str, ...]:
    """Expose supported workload names for demos and tests."""

    return tuple(item.value for item in Workload)
