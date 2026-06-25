# Project 12 · 湖仓引擎选型规则

> 关联章节：Ch.12 湖仓引擎与 OLAP
> 难度：★

## 目标

用一个最小规则模型演示如何把企业分析负载映射为湖仓或 OLAP 引擎候选项。该项目不连接真实引擎，重点是把选型依据固化为可测试代码：`choose_engine` 回答“哪个引擎”，`route_query` 在此基础上叠加延迟与扫描预算，对应正文 L2 的受控查询接口契约（仅产出路由决策，不执行 SQL）。

## 运行

```bash
PYTHONPATH=../.. python3 run.py
```

## 预期输出

```text
realtime_bi -> StarRocks
federated_query -> Trino
local_analytics -> DuckDB
route realtime_bi@1500ms -> StarRocks budget=1500ms feasible=False
```

最后一行说明：当调用方要求 1500ms 延迟、低于 realtime_bi 在 StarRocks 上的目标延迟 3000ms 时，路由器仍选定 StarRocks，但把生效预算收紧到 1500ms 并标记 `feasible=False`，提示上层改写查询、加过滤或更换引擎。

## 后续扩展

- 接入统一配置加载器，允许平台团队调整 workload 到 engine 的映射与预算。
- 增加真实执行适配器，提交 SQL 并返回 query_id。
- 接入权限、审计、成本预算和可观测性字段。
