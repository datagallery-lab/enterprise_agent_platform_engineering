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

### DuckDB
进程内分析数据库，本书默认本地 OLAP 引擎。

### Trino
分布式 SQL 查询引擎，前身 Presto。

### Airflow / Dagster / Prefect
主流数据编排框架。

### OpenLineage
开源数据血缘标准。

### Data Contract / 数据契约
数据生产者与消费者之间关于 Schema、SLA、质量的契约化协议。

### Headless BI / 无头 BI
将指标定义层独立于具体 BI 工具，代表 Cube、MetricFlow。

### Feature Store / 特征平台
集中管理在线/离线特征的系统，代表 Feast、Tecton、Hopsworks。

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

---

## H. 部署与运维

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
