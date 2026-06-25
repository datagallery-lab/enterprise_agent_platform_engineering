# Project 10 · 数据采集契约规则

> 关联章节：Ch.10 数据采集与集成
> 难度：★

## 目标

用一个最小规则模型演示如何把源系统特征转换成接入模式和 DataAgent 可读的数据契约。该项目不连接真实数据库、SaaS API 或 Kafka，重点是把批同步、增量批、CDC、托管 ELT 和事件流的选择依据固化为可测试代码。

## 运行

```bash
PYTHONPATH=../.. python3 run.py
```

## 预期输出

```text
orders-postgres-to-iceberg -> cdc
tool=Debezium freshness=60s
checks=row_count_reconciliation,primary_key_uniqueness,freshness_slo,schema_compatibility
```

## 常见失败

- 请求缺少 `pipeline_id`、`source` 或 `destination`：补齐契约必填字段。
- 数据库表没有稳定主键：规则不会选择 CDC，应先定义业务键或采用批同步加对账。
- SaaS API 要求秒级新鲜度：规则会把 SLO 放宽到小时级，提示不要把 API 限流误当成实时链路。
