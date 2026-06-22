# Part III 数据基础设施层

## 本部分目标

Agent 能否进入企业生产，取决于它拿到的数据是否及时、可信、可追溯。Part III 讨论数据底座从采集、湖仓、OLAP、实时计算到元数据治理的主链路。这里不把数据平台当成背景设施，而把它看作 Agent 平台的事实来源和责任边界。

## 本部分章节

| 章 | 主题 | 读完应能回答的问题 |
|---|---|---|
| [第10章 数据采集与集成](ch10.md) | CDC、批同步、文件与 API 接入 | 源系统数据怎样进入 Agent 平台，哪些接入方式会影响新鲜度和一致性 |
| [第11章 数据湖与湖仓](ch11.md) | Iceberg、Hudi、Delta、Paimon | 湖仓怎样保存可回放的数据版本，为什么快照和 Catalog 会影响回答可追溯性 |
| [第12章 湖仓引擎与 OLAP](ch12-olap.md) | Doris、StarRocks、Trino、ClickHouse、DuckDB | 不同分析负载应落在哪类引擎上，DataAgent 查询怎样避免拖垮生产看板 |
| [第13章 流式计算与实时数据](ch13.md) | Kafka、Flink、watermark、exactly-once | 实时指标怎样进入 Agent 决策，迟到数据和状态恢复怎样解释给业务用户 |
| [第14章 数据编排与质量](ch14.md) | Airflow、Dagster、质量门禁 | 数据产品怎样发布、回填和阻断，DataAgent 何时应该回答“数据不可用” |
| [第15章 元数据、血缘、契约与指标](ch15.md) | DataHub、OpenLineage、Data Contract、指标层 | Agent 怎样知道口径、权限、血缘和字段变更，而不是临场猜测 |

## 阅读路径

第10章至第13章解决“数据怎么来、怎么存、怎么查、怎么实时更新”。第14章和第15章再把这条链路收进质量、血缘、契约和指标治理。后续 DataAgent 章节中的 Schema Linking、NL2SQL、报告证据链，都依赖这里建立的数据边界。
