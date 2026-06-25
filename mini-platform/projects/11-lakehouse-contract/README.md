# Project 11 · 湖仓表契约检查

> 关联章节：Ch.11 数据湖与湖仓
> 难度：★

## 目标

用一个最小表契约演示湖仓表在暴露给 DataAgent 前需要具备的控制点：开放表格式、Catalog、快照、主键、分区、新鲜度和时间旅行能力。该项目不连接真实 Iceberg、Hudi、Delta Lake 或 Paimon catalog，只验证平台侧应保留的契约字段。

## 运行

```bash
PYTHONPATH=../.. python3 run.py
```

## 预期输出

```text
dwd.orders snapshot=742 format=iceberg
agent_ready=True missing=()
```

## 常见失败

- 缺少 `primary_key`：DataAgent 无法稳定解释 upsert 或去重结果。
- 缺少 `partition_fields`：查询引擎难以做分区裁剪，成本不可控。
- `data_freshness_seconds` 超过一小时：默认不应暴露给需要新鲜度保障的 Agent 工具。
- 表格式不支持时间旅行或未暴露快照：无法稳定复现回答依据。
