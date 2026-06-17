# 术语表

> 本术语表是全书的强约束词汇源。CI 会扫描 L1/L2 段落中的英文缩写，若未在此表中登记则报警。
> v0.1 收录 ≥50 条；目标 v1.0 收录 ≈120 条。

## 编辑规范

- 术语按英文字母 + 中文笔画混合排序，分类为：**A 基础概念**、**B 模型与推理**、**C 数据基础设施**、**D 向量与知识**、**E Agent 与编排**、**F 评估与观测**、**G 安全与合规**、**H 部署与运维**、**I 前端与交互**、**J 数据智能**。
- 每条包含：术语英文 / 中文 / 定义 / 与相邻概念边界。

---

## A. 基础概念

### Agent / 智能体
可感知-决策-行动的程序实体，依赖 LLM 进行决策、调用工具、维护状态。区别于 Workflow（固定流程）与 Copilot（嵌入式辅助）。

### Copilot / 助手
嵌入既有产品中的对话或建议组件，行动权小、依赖用户确认。区别于 Agent 可自主调用工具完成任务。

### Workflow / 工作流
预先编排的步骤序列，分支与条件由开发者写死。区别于 Agent 的步骤由 LLM 动态决定。

### RAG / Retrieval-Augmented Generation / 检索增强生成
让 LLM 在生成前先检索外部知识，再基于检索片段作答。本书 Part IV 系统讲解。

### LLM / Large Language Model / 大语言模型
基于 Transformer 的大规模自回归或编码-解码模型，本书默认指生成式 LLM。

### AI 原生业务系统 / AI-native System
以 Agent 作为主入口、以数据资产与工具能力作为业务原语的新一代企业系统。

### mini-platform
本书配套开源参考实现 `mini-enterprise-agent-platform` 的简称。

### L1 / L2 / L3
本书三层阅读法：L1 概念层 / L2 架构层 / L3 工程实现层。

### CPU / 中央处理器
计算机核心运算单元。在 OLAP 语境中常讨论向量化执行对 CPU 缓存的利用效率。

### CLI / 命令行界面
通过文本命令与程序交互的界面，区别于 GUI。DuckDB 等工具提供 CLI 入口。

### CSV / 逗号分隔值
以逗号分隔字段的纯文本数据格式，常用于数据交换与导入导出。

### CFO / 首席财务官
企业高管角色。书中用于示例场景，如 CFO 关注的财务报表对数据延迟和准确性的要求。

### OOM / 内存溢出
进程内存耗尽错误。单机 OLAP 引擎（如 DuckDB）在超过内存上限的 Join 或聚合中可能触发 OOM。

### SIMD / 单指令多数据
CPU 指令集特性，一条指令同时处理多个数据。列式 OLAP 引擎利用 SIMD 加速批量运算。

### URL / 统一资源定位符
网络资源地址。书中用于引用官方文档链接和数据源端点配置。

### UUID / 通用唯一标识符
全局唯一的 128 位标识符。在数据建模中常见，但作为排序键首位时高基数特性会使稀疏索引近乎失效。

### GMV / Gross Merchandise Volume / 商品交易总额
一定时间内订单交易总额，常用于零售和电商经营分析。区别于实收金额、净收入和扣除退款后的销售额。

---

## B. 模型与推理

### Function Calling / 函数调用
LLM 输出结构化函数调用请求，由宿主程序解析并执行。OpenAI、Anthropic、Qwen 等模型协议略有差异。

### Tool Use / 工具使用
Function Calling 的语义化称呼，强调"调用外部工具"。本书与 Function Calling 互换使用。

### JSON Schema
描述 JSON 数据结构的标准。本书用于工具参数声明、结构化输出约束。

### KV Cache / Key-Value 缓存
Transformer 推理时缓存历史 Key/Value，避免重复计算。是吞吐与延迟优化的核心。

### Prefix Cache / 前缀缓存
在 KV Cache 之上，对相同 Prompt 前缀复用 KV，对 RAG 与 Agent 重复调用收益巨大。

### Speculative Decoding / 投机解码
用小模型先生成草稿、大模型并行验证，降低延迟。

### Quantization / 量化
将模型权重精度从 FP16 降到 INT8 / INT4，常见方案 GPTQ、AWQ、SmoothQuant。

### LoRA / Low-Rank Adaptation
低秩适配微调方法，冻结底模、训练旁路低秩矩阵。本书默认微调方案。

### ML / Machine Learning / 机器学习
通过数据训练模型以完成预测、分类、排序或生成任务的技术体系。区别于纯规则系统。

### DPO / Direct Preference Optimization
直接偏好优化，无需独立奖励模型的对齐方法。

### CoT / Chain-of-Thought / 思维链
让 LLM 显式输出推理步骤再给出最终答案的提示方法。

### ToT / Tree-of-Thoughts / 思维树
在 CoT 基础上分支探索多条推理路径，再用启发式选优。

### vLLM
高吞吐 LLM 推理引擎，基于 PagedAttention。

### SGLang
LLM 服务框架，强调结构化生成与高效控制流。

### LMDeploy
国内常用本地推理框架，对 Qwen、InternLM 等模型有优化。

---

## C. 数据基础设施

### CDC / Change Data Capture / 变更数据捕获
捕获数据库增量变更并下发的技术，常见 Debezium、Flink CDC。

### OMS / Order Management System / 订单管理系统
管理订单创建、拆单、履约、取消和售后状态流转的业务系统。区别于 WMS 的仓内作业管理，也区别于 CRM 的客户关系管理。

### WMS / Warehouse Management System / 仓储管理系统
管理仓库入库、出库、拣货、库存和库位的业务系统。区别于 ERP 的企业资源计划范围，也区别于 OMS 的订单履约编排。

### ELT / Extract Load Transform / 抽取加载转换
先抽取并加载原始数据到目标平台，再在目标平台内转换的数据集成模式。区别于 ETL 先转换再加载的模式。

### WAL / Write-Ahead Log / 预写日志
数据库在提交数据页修改前先写入的事务日志，CDC 工具常通过 WAL 或 binlog 捕获增量变更。区别于业务事件日志，WAL 是数据库内部一致性机制。

### LSN / Log Sequence Number / 日志序列号
数据库日志中的位置标识，用于表示 CDC 读取进度或恢复位点。区别于 Kafka offset，LSN 属于源数据库日志坐标。

### Lakehouse / 湖仓
统一数据湖（廉价存储）与数仓（事务/查询）能力的架构，依赖 Iceberg/Hudi/Delta 等表格式。

### Iceberg
开放表格式，支持 ACID、Schema 演化、时间旅行。

### Hudi
开放表格式，强调流批一体与增量处理。

### Delta Lake
Databricks 主导的开放表格式。

### Paimon
Apache 项目，原生流式湖仓表格式。

### OLAP / 在线分析处理
面向分析的查询模型，本书涉及 Doris、StarRocks、ClickHouse、Trino、DuckDB 等。

### OLTP / Online Transaction Processing / 在线事务处理
面向短事务、点查、行级更新和高并发写入的数据库负载模型。区别于 OLAP 的大范围扫描和聚合分析。

### SQL / Structured Query Language / 结构化查询语言
关系型数据查询语言，本书在数仓、湖仓、DataAgent 与 NL2SQL 章节中使用。

### MPP / Massively Parallel Processing / 大规模并行处理
将查询或计算任务拆分到多个节点并行执行的架构。区别于单机执行或仅依赖远端存储的串行查询。

### FE / Frontend / 前端节点
OLAP 数据库中常见的接入、元数据、规划和调度节点名称，Doris 与 StarRocks 均使用该术语。

### BE / Backend / 后端节点
OLAP 数据库中常见的存储与执行节点名称，通常负责分片数据、扫描和计算。

### CN / Compute Node / 计算节点
存算分离或 shared-data 架构中的计算节点，通常只负责查询执行和缓存，不持久化主数据。

### HDFS / Hadoop Distributed File System / Hadoop 分布式文件系统
Hadoop 生态中的分布式文件系统，早期数据湖常见底层存储。区别于云对象存储。

### JDBC / Java Database Connectivity / Java 数据库连接
Java 生态访问数据库的标准接口，常用于 BI 工具、数据集成和查询引擎连接。

### SSD / Solid-State Drive / 固态硬盘
常用于缓存、热数据和本地低延迟存储。区别于对象存储的低成本大容量属性。

### VLDB / Very Large Data Bases / 超大数据库会议
数据库领域重要学术会议，本书在引用 ClickHouse 等系统论文时可能出现。

### DuckDB
进程内分析数据库，本书默认本地 OLAP 引擎。

### BDB / Berkeley DB
嵌入式键值存储库。在 StarRocks 架构语境中，FE 节点间使用类 BDB 协议进行 Leader 选举和元数据同步。

### CBO / Cost-Based Optimizer / 基于代价的优化器
SQL 优化器的一种，根据统计信息估算不同执行计划的代价并选择最优。区别于基于规则的 RBO。

### DML / Data Manipulation Language / 数据操纵语言
SQL 中操作数据的语句子集，包括 INSERT、UPDATE、DELETE 等。区别于 DDL。

### ORC / Optimized Row Columnar
列式存储文件格式，Hive 生态常用。与 Parquet 类似，湖仓外表查询时可能出现。

### S3 / Amazon Simple Storage Service
亚马逊云对象存储服务。在湖仓语境中泛指云对象存储，许多 OLAP 引擎支持直接查询 S3 上的 Parquet/ORC 文件。

### Trino
分布式 SQL 查询引擎，前身 Presto。

### Metadata / 元数据
描述数据资产结构、语义、运行状态和治理属性的数据。区别于业务数据本身，元数据用于资产发现、语义解释、权限控制和影响分析。

### Data Catalog / 数据目录
集中登记数据资产、Owner、标签、质量状态、血缘和使用说明的平台能力。区别于单纯表名搜索，数据目录应服务资产发现、治理和 DataAgent 上下文选择。

### Data Quality / 数据质量
对数据完整性、唯一性、准确性、及时性、一致性和有效性的系统性度量。区别于任务成功状态，数据质量关注产出是否可信。

### Quality Gate / 质量门禁
数据进入下游消费前执行的阻断、降级或告警控制点。区别于普通监控，质量门禁必须绑定失败动作、Owner 和审计记录。

### Lineage / 数据血缘
描述数据从源系统到表、指标、查询和回答引用的流转关系。区别于静态目录，血缘强调上下游依赖、影响分析和溯源。

### DAG / Directed Acyclic Graph / 有向无环图
用有向且不成环的节点关系表达任务执行顺序或依赖关系。区别于资产依赖，DAG 更关注执行流程。

### SLA / Service Level Agreement / 服务等级协议
生产者与消费者之间对可用性、新鲜度、响应时间或支持责任的协议。区别于 SLO，SLA 通常带有组织承诺或违约处理。

### Airflow / Dagster / Prefect
主流数据编排框架。

### OpenLineage
开源数据血缘标准。

### Data Contract / 数据契约
数据生产者与消费者之间关于 Schema、语义、SLA、质量、权限和变更流程的契约化协议。区别于普通字段文档，数据契约应参与发布门禁和影响分析。

### Headless BI / 无头 BI
将指标定义层独立于具体 BI 工具，代表 Cube、MetricFlow。

### Feature Store / 特征平台
集中管理在线/离线特征的系统，代表 Feast、Tecton、Hopsworks。

### Kafka
分布式事件日志与消息系统，常用于实时链路的事件总线。区别于 Flink 等流式计算引擎，Kafka 负责保存和分发事件，不负责复杂状态计算。

### Flink
面向有状态流式计算的分布式计算引擎，支持事件时间、Watermark、Checkpoint 等机制。区别于 Kafka 的事件存储角色，也区别于偏微批模型的 Spark Structured Streaming。

### Spark Structured Streaming
Spark 生态中的结构化流处理框架，常以微批方式处理持续到达的数据。区别于 Flink 的原生连续流处理模型。

### Watermark / 水位线
流式计算中对事件时间进度的估计，用于决定窗口何时输出和如何处理迟到数据。区别于处理时间，也不是所有事件已到齐的证明。

### Checkpoint / 检查点
流式作业对状态和输入位置的一致性快照，用于故障恢复。区别于 Savepoint 的主动运维快照，也区别于业务审计快照。

### Savepoint / 保存点
运维人员主动触发的可迁移状态快照，常用于流式作业升级、迁移和回滚。区别于周期性自动生成的 Checkpoint。

### Exactly-once / 精确一次语义
在可重放输入、可恢复状态和事务或幂等下游共同配合下形成的一致性处理语义。区别于业务事实绝对只发生一次，业务层仍需要幂等键和对账。

### Backpressure / 背压
下游处理能力不足导致上游处理速度被迫下降的现象。区别于普通任务失败，背压通常表现为消费延迟、Watermark 延迟和端到端延迟共同上升。

### Stream-table Duality / 流表二象性
将事件流、变更日志和动态表视为同一业务事实的不同表示方式。区别于只把流看作消息队列的搬运模型。

---

## D. 向量与知识

### Embedding / 嵌入
将文本、图像等映射为稠密向量的模型或结果。本书涉及 BGE、E5、GTE、Conan 等。

### Dense Retrieval / 稠密检索
基于向量相似度的检索，区别于 BM25 等稀疏检索。

### Sparse Retrieval / 稀疏检索
基于词项的检索，代表 BM25、SPLADE。

### Hybrid Search / 混合检索
稠密 + 稀疏检索结果融合，常用 RRF（Reciprocal Rank Fusion）。

### HNSW / 分层可导航小世界图
近似最近邻索引算法，平衡召回与延迟。

### IVF / Inverted File
近似最近邻倒排索引算法。

### PQ / Product Quantization / 乘积量化
向量压缩方法，降低内存占用。

### Reranker / 重排器
对初步检索结果再次打分排序的模型，常用 Cross-Encoder。

### ColBERT / Late Interaction
延迟交互检索，对每个 token 维护向量并在查询时做细粒度匹配。

### SPLADE
基于 BERT 的稀疏向量检索方法。

### GraphRAG
微软提出的图谱增强 RAG，做社区发现 + 层次摘要。

### Knowledge Graph / 知识图谱
以实体-关系-实体三元组组织的知识结构，本书涉及 Neo4j、NebulaGraph 等存储。

### OCR / 光学字符识别
将图像中的字符识别为文本，本书涉及 PaddleOCR、TrOCR、Nougat 等。

---

## E. Agent 与编排

### Runtime / 运行时
负责 Agent 任务执行、状态管理、失败恢复的平台组件。

### Tool Registry / 工具注册中心
集中登记工具 Schema、版本、权限的服务。

### MCP / Model Context Protocol / 模型上下文协议
Anthropic 主导的开放协议，host-client-server 架构，统一暴露 tools / resources / prompts。

### A2A / Agent-to-Agent
Agent 间协作协议，用于跨平台 Agent 互通。

### Agent Card
A2A 协议中描述 Agent 能力、端点、鉴权的元数据文件。

### ReAct
Reason + Act 循环范式，让 LLM 交替"思考"与"调用工具"。

### Plan-and-Execute
先全局规划再逐步执行的 Agent 范式。

### Reflexion / 反思
Agent 在失败后回顾自身轨迹并改进的范式。

### Self-Refine / 自我改进
Agent 用自身输出作为输入，迭代改进结果。

### Human-in-the-Loop / HITL / 人在回路
关键节点引入人工审批或纠正的设计。

### Memory / 记忆
Agent 维护的上下文信息，分短期（会话）与长期（用户/企业）。

### LangGraph / AutoGen / CrewAI / Dify / Coze
主流 Agent 编排框架，本书在 Ch31 横向对标。

---

## F. 评估与观测

### OpenTelemetry / OTel
开源可观测性标准，含 trace / metrics / logs。本书使用其 GenAI 语义约定。

### GenAI Semantic Conventions
OpenTelemetry 针对生成式 AI 的属性约定，规范 LLM / Agent 的 span 字段。

### Langfuse / Phoenix / Helicone
LLM 应用可观测性产品。

### Ragas / TruLens / DeepEval / Promptfoo
RAG 与 LLM 应用评测框架。

### LLM-as-Judge
用 LLM 作为评分器评估其他 LLM 输出。需注意偏差与稳定性。

### Spider / BIRD / CoSQL / SParC
NL2SQL 评测基准。

### MTEB / Massive Text Embedding Benchmark
嵌入模型综合评测基准。

### Semantic Cache / 语义缓存
基于嵌入相似度命中的缓存，代表 GPTCache。

### Prompt Cache / 提示缓存
在 LLM 服务侧对相同前缀复用 KV Cache 的能力。

### SLO / Service Level Objective / 服务等级目标
对延迟、可用性、质量的可量化目标。

---

## G. 安全与合规

### Prompt Injection / 提示注入
攻击者在输入中嵌入指令，让 Agent 偏离原任务。

### Indirect Prompt Injection / 间接提示注入
攻击者污染外部数据（如网页、文档），Agent 读取时被劫持。

### Red Teaming / 红队
通过攻击性测试发现系统漏洞，常用工具 PyRIT、Garak。

### Guardrails / 护栏
对 LLM 输入输出施加规则约束的组件，代表 NeMo Guardrails、Llama Guard。

### OWASP LLM Top 10
OWASP 组织维护的 LLM 应用十大安全风险清单。

### NIST AI RMF
美国 NIST 的 AI 风险管理框架，含生成式 AI Profile。

### EU AI Act
欧盟人工智能法案。

### 中国《生成式 AI 服务管理办法》
中国针对生成式 AI 服务的合规要求。

### C2PA
内容溯源与水印标准（Content Provenance and Authenticity）。

### Tokenization / 标记化（数据脱敏语境）
将敏感数据替换为不可逆 token 的脱敏方式；与 LLM tokenization 同名不同义。

### PII / Personally Identifiable Information / 个人可识别信息
受隐私法规保护的敏感字段。

### RBAC / Role-Based Access Control / 基于角色的访问控制
按用户角色授予系统或数据访问权限的模型。区别于基于属性的访问控制，RBAC 更强调角色集合与权限集合的映射。

---

## H. 部署与运维

### Device Plugin / 设备插件
Kubernetes 扩展机制，向 kubelet 注册 GPU 等加速设备为可调度资源；NVIDIA Device Plugin 注册 `nvidia.com/gpu`。

### Gang Scheduling / 组调度
要求一组 Pod 同时调度成功或同时等待的调度语义；Volcano PodGroup 的 `minMember` 实现；多卡张量并行推理依赖此能力。

### InferenceService
KServe 自定义资源（CRD），声明模型服务的 Runtime、副本、扩缩与流量分割；企业 LLM 生产部署的主 CRD。

### TTFT / Time To First Token / 首 Token 时间
流式推理从请求到收到第一个 token 的延迟；Agent 交互体验的关键 SLO 指标之一。

### Canary Traffic / 金丝雀流量
新版本模型服务先接少量比例流量（如 5%），指标达标后再逐步扩量；KServe `canaryTrafficPercent` 实现。

### External Secrets Operator
从 Vault/KMS 等外部密钥系统同步 Secret 到 Kubernetes；GitOps 仓库禁止明文 Key 的配套组件。

### KPA / Knative Pod Autoscaler
基于并发而非 CPU 的 Pod 自动扩缩器；KServe 推理服务常用扩缩指标。

### SSOT / Single Source of Truth / 单一事实源
GitOps 中 Git 仓库作为集群期望状态的唯一权威来源。

### OTA / Over-The-Air / 空中升级
边缘节点通过网络远程更新模型或软件；需 checksum 校验与原子切换避免半更新。

### KServe / BentoML / Triton / Ray Serve
模型部署框架。

### LiteLLM / Portkey / Higress AI Gateway / Kong AI
LLM 网关产品，提供统一 API、路由、限流、计费。

### Volcano / Kueue
Kubernetes 上的批/AI 作业调度器。

### MIG / Multi-Instance GPU
NVIDIA GPU 切分技术，多实例共享单卡。

### GitOps
通过 Git 仓库声明并同步基础设施状态的方式，代表 ArgoCD、Flux。

### IaC / Infrastructure as Code / 基础设施即代码
用代码（Terraform、Helm）管理基础设施。

### ONNX Runtime / llama.cpp / MLC
端侧/边缘推理引擎。

---

## I. 前端与交互

### SSE / Server-Sent Events
单向流式 HTTP 协议，常用于 LLM 流式输出。

### Generative UI / 生成式 UI
LLM 输出驱动 UI 组件渲染（图表、表单、表格），代表 Vercel AI SDK 的 useChat + tool 渲染。

### Artifacts
Claude.ai 等产品中独立画布展示长内容的范式。

### Realtime API
OpenAI 等厂商提供的低延迟语音/多模态接口。

---

## J. 数据智能

### DataAgent
本书核心案例：面向自然语言查数、分析、报告的 Agent，ChatBI 是其子集。

### ChatBI
以对话方式驱动商业智能的产品形态，DataAgent 的早期形态。

### NL2SQL / Text-to-SQL
将自然语言问题翻译为 SQL 的任务。

### Schema Linking / 模式链接
将自然语言提及的实体/字段映射到具体表/列的过程。

### Semantic Layer / 语义层
连接业务术语与物理数据的抽象层，定义指标口径与维度关系。

### Auto-EDA / 自动探索性数据分析
自动生成数据概览、分布、相关性等分析结果。

### Lida / Chat2VIS / PandasAI
Text-to-Chart / Text-to-Pandas 代表工具。

### DB-GPT / Vanna / WrenAI / Defog
开源 DataAgent / Text-to-SQL 平台与库。

---

## 缩写速查（CI 白名单）

A2A / ACP / AGI / AI / API / AWQ / BGE / BI / BM25 / CDC / CLIP / CoT / CRM / DAG / DDL / DPO / E5 / ERP / ETL / FP16 / GET / GMV / GPT / GPTQ / GTE / GUI / GraphRAG / HA / HITL / HNSW / HTTP / IaC / INT4 / INT8 / IVF / JSON / KPI / KV / LLM / LoRA / MCP / MIG / MTEB / MVP / NER / NL2SQL / OCR / OLAP / ONNX / OPA / OWASP / NIST / PEFT / PII / POS / POST / PQ / PR / RAG / RBAC / RE / ReAct / RDF / RLHF / ROI / RPC / RRF / SaaS / SDK / SKU / SLA / SLO / SOAP / SOC / SQL / SRE / SFT / SPLADE / SSE / SSO / TTS / ToT / UI / WASM / XSS / YAML / OWL / OSS / GPU / KTO / IAM / REST

Roman numerals used as Part numbers in this book are also exempt:
II / III / IV / V / VI / VII / VIII / IX / X / XI / L1 / L2 / L3 / L4

SQL keywords and code identifiers that may appear inline in narrative:
SELECT / FROM / WHERE / DROP / TABLE / INSERT / UPDATE / DELETE / JOIN / GROUP / ORDER / BY / NULL / NOT / AND / OR / TRUE / FALSE / ID

State machine state names used in Ch.22 and beyond:
PENDING / PLANNING / EXECUTING / WAITING / HUMAN / SUCCEEDED / FAILED
