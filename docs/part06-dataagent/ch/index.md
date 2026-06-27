# Part VI DataAgent 主线深潜

## 本部分目标

Part VI 以 DataAgent 为主线，把前面讨论的模型、数据、知识和 Runtime 能力串成一个企业分析产品。读者在这一部分需要看到：自然语言问题怎样变成可信查询，查询结果怎样进入 Python 分析、图表和报告，最终产物怎样带着证据链交付给业务用户。

## 本部分章节

| 章 | 主题 | 读完应能回答的问题 |
|---|---|---|
| [第32章 DataAgent 产品形态](ch32-dataagent.md) | 产品边界、四种形态、任务分型 | DataAgent 与 NL2SQL、BI Copilot、报表助手的边界在哪里 |
| [第33章 语义层工程](ch33.md) | 指标口径、Schema Linking、可信上下文 | 系统怎样把用户语言绑定到正确指标、字段和权限 |
| [第34章 NL2SQL 工程化](ch34-nl2sql.md) | 分步生成、大库剪枝、安全执行 | SQL 怎样生成、校验、执行和解释，错误怎样回到 Planner |
| [第35章 Text-to-Pandas / Text-to-Python](ch35-text-to-pandas-text-to-python.md) | Python 沙箱、SQL 与 Python 协同 | 哪些分析应交给 Python，怎样隔离代码执行风险 |
| [第36章 数据分析、可视化与报告](ch36.md) | 洞察、图表、报告与证据链 | DataAgent 怎样把计算结果变成可审计的业务产物 |
| [第37章 DataAgent 对标与生态](ch37-dataagent.md) | 开源/商业对标与选型 | 企业应怎样评估 DataAgent 产品和生态方案 |

统一案例是一条“华东区 GMV 下滑”的问数、分析和报告 Run 链，从第32章开始贯穿六章。这里不虚构公司背景，案例只保留任务、数据、工具和证据链。以下模块为 mini-platform 中 DataAgent 能力在 Part VI 各章的展开顺序。

## Part VI mini-platform 模块地图

| 模块路径 | 职责 | 主要章节 |
| --- | --- | --- |
| `agents/data_agent/` | AgentSpec、Question Frame | 第32章至第33章 |
| `infra/semantic_layer/` | 指标、View、口径解析 | 第33章 |
| `tools/sql_executor/` | 只读 SQL、校验与执行 | 第34章 |
| `tools/python_sandbox/` | 分析沙箱 | 第35章 |
| `tools/chart_renderer/` | 图表 spec | 第36章 |
| `agents/data_agent/templates/` | 报告模板 | 第36章 |

本部分不会重复展开平台底座，Run、Registry 和 HITL 的基础设计集中放在 Part V。需要回看实现边界时，优先参考 [第22章 Agent Runtime](../../part05-agent-capabilities/ch/ch22-agent-runtime.md) 到第30章。

## Part VI 能力体系（一览）

| 章 | 一句话 |
| --- | --- |
| 第32章 | DataAgent 不等于 NL2SQL，产品形态取决于任务边界 |
| 第33章 | 语义层决定问题能否绑定到正确口径 |
| 第34章 | 安全 SQL 需要生成、校验、执行和解释共同约束 |
| 第35章 | Python 沙箱负责 SQL 之后的受控分析 |
| 第36章 | 图表和报告必须保留证据链 |
| 第37章 | 选型应回到数据、工具、治理和评测能力 |