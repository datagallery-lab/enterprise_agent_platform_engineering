# 《企业级 Agent 平台工程：从数据智能底座到 AI 原生业务系统》v3 完整策划

> 版本：v3（2026-05-28 全栈扩充）
> 状态：可直接开工的总策划，作为 v0.1 骨架阶段的源文档
> v3 变化：在 v2 基础上补齐业界全栈技术分类，从 30 章扩展为 **10 Part / 55 章 / 16 实战项目 / ~1150 页主体**

---

## 0. 卷首

### 一句话定位

面向企业真实落地场景，**百科式**讲解从数据底座、模型推理、知识工程到 Agent 平台、AI 原生业务系统的完整技术栈，以 **DataAgent 主线**深潜数据智能场景，配套自建开源参考实现 **mini-enterprise-agent-platform**。

### 封面副文案

数据智能与 Agent 平台的中文权威参考 · 全栈能力百科 · DataAgent 主线深潜 · AI 原生业务落地手册。

### 目标读者（5 角色）

- **AI 平台负责人 / CTO**：理解平台边界、ROI、3 年演进路线
- **架构师**：掌握模型/数据/检索/Agent/部署五层全栈接口契约与失败模式
- **数据智能工程师**：DataAgent / ChatBI 方向，关注数据底座、语义层、NL2SQL、可信回答
- **AI 应用开发者**：从 Demo 到生产，关注代码、配置、踩坑
- **安全 / 合规负责人**：OWASP LLM Top 10、NIST AI RMF、EU AI Act、中国合规

### 核心差异化

- **全栈覆盖**：模型推理 → 数据基础设施 → 向量与知识工程 → Agent 平台 → DataAgent → 部署 → 前端 → 安全合规，所有业界主流技术分类一站讲透
- **平台视角**：不是单 Agent 教程，不是框架教程，讲企业级平台基础设施
- **三层阅读法（L1/L2/L3）强制贯穿**，支持按角色跳读
- **DataAgent 主线深潜 + 5 类业务案例横向覆盖**
- **mini-platform 与书稿 monorepo 同源**，代码即文档

---

## 1. 三层阅读法（贯穿全书写作规范）

| 层 | 篇幅 | 内容 | 适用读者 |
|---|---|---|---|
| **L1 概念** | ~30% | 业务定义、边界、相邻概念对比、典型误区；无代码、有概念图 | CTO / 安全合规 / 跨职能读者 |
| **L2 架构** | ~40% | 组件划分、数据流、接口契约、状态机、失败模式；有架构图与时序图 | 架构师 / 平台负责人 |
| **L3 工程** | ~30% | 基于 mini-platform 的可运行代码、配置、生产化 checklist、踩坑记录 | 工程师 / 应用开发者 |

每章页眉标注 L1/L2/L3 的页码区间，页脚标注当前层级。

### 五条读者路径

| 角色 | 推荐路径 | 页数 |
|---|---|---|
| CTO / 平台负责人 | Part I + Part V/VI/X 各章 L1+L2 | ~350 页 |
| 架构师 | Part I + Part II/III/IV/V/VIII 全部 + Part VI L2 | ~800 页 |
| 数据智能工程师 | Part I L1 + Part III/IV 全部 + Part VI 全部 + Part VII | ~600 页 |
| AI 应用开发者 | Part I L1 + Part II/V 全部 L3 + Part IX + 附录 | ~650 页 |
| 安全 / 合规 | Part I + Part VII/X 全部 + Part III 元数据/血缘 | ~350 页 |

---

## 2. 全书结构（10 Part / 55 章 / ~1150 页）

### 卷前

- 推荐序
- 前言：从 Chatbot 到 AI 原生业务系统
- 导读：三层阅读法 + 五条读者路径 + 全栈技术地图
- 开源项目说明：代码、案例、数据集、贡献方式

---

### Part I 总论与平台观（4 章 / ~70 页）：骆阳

| # | 章节 | 关键议题 |
|---|---|---|
| 1 | Agent 的本质：从对话助手到任务执行系统 | Agent vs Copilot vs Workflow vs RAG；感知-决策-行动；企业 vs 消费级 |
| 2 | 企业级 Agent 平台的边界 | 模型/数据/工具/流程/治理；平台 vs 应用分层；平台不是框架 |
| 3 | AI 原生业务系统：Agent 重塑企业软件 | SaaS → AI 原生迁移；Agent 作为业务新界面；组织协同变化 |
| 4 | 平台参考架构总览 | 全栈八大子系统全景图；55 章主题块导航地图 |

---

### Part II 模型与推理层（5 章 / ~120 页）⭐ 新增：张豪

| # | 章节 | 关键议题 |
|---|---|---|
| 5 | 大模型选型 | 闭源（GPT/Claude/Gemini）/ 开源（Llama/Mistral）/ 国产（Qwen/DeepSeek/GLM/文心/豆包）对比与场景适配 |
| 6 | 本地推理引擎 | vLLM、SGLang、LMDeploy、TGI、Ollama；吞吐 vs 延迟取舍 |
| 7 | 推理优化 | KV cache、prefix cache、speculative decoding、量化（GPTQ/AWQ/INT4） |
| 8 | 结构化输出与提示工程 | JSON Schema、Outlines、Instructor、Few-shot/CoT/ToT/Self-Consistency、Prompt 模板管理 |
| 9 | 模型微调与对齐 | LoRA、QLoRA、PEFT、SFT、DPO、KTO、领域微调；何时微调何时 RAG |

---

### Part III 数据基础设施层（6 章 / ~150 页）⭐ 新增：曹旭宏

| # | 章节 | 关键议题 |
|---|---|---|
| 10 | 数据采集与集成 | CDC、Debezium、Airbyte、Fivetran、Flink CDC；批 vs 流的取舍 |
| 11 | 数据湖与湖仓 | S3/OSS/HDFS、Iceberg、Hudi、Delta、Paimon；ACID、时间旅行、分区演化 |
| 12 | 湖仓引擎与 OLAP | Databricks、Snowflake、Doris、StarRocks、Trino、ClickHouse、DuckDB |
| 13 | 流式计算与实时数据 | Flink、Spark Streaming、Kafka；exactly-once、状态管理、watermark |
| 14 | 数据编排与质量 | Airflow、Dagster、Prefect、DolphinScheduler；Great Expectations、Soda、dbt tests |
| 15 | 元数据、血缘、契约与指标 | DataHub、Amundsen、OpenLineage、Marquez；Data Contract；Cube、MetricFlow、Feast |

---

### Part IV 向量、检索与知识工程（6 章 / ~140 页）⭐ 扩充：刘中一

| # | 章节 | 关键议题 |
|---|---|---|
| 16 | 嵌入模型 | BGE、E5、GTE、Conan、Qwen-Embedding、OpenAI Embedding；多模态嵌入（CLIP/SigLIP/Jina） |
| 17 | 嵌入微调与重排 | sentence-transformers、对比学习、hard negative mining；bge-reranker、Cohere Rerank、Cross-Encoder |
| 18 | 向量数据库与索引算法 | pgvector、Milvus、Qdrant、Weaviate、Chroma、Vespa；HNSW、IVF、PQ、ScaNN 取舍 |
| 19 | 文档解析与多模态 OCR | unstructured、LlamaParse、PyMuPDF、PaddleOCR、Nougat、Marker、Donut、Qwen-VL |
| 20 | RAG 工程与高级检索 | 分块策略、混合检索、RRF、SPLADE、ColBERT、Late Interaction、Parent-Child、Small-to-Big |
| 21 | 知识工程：本体、抽取与知识图谱 | NER/RE、LLM 抽取、实体链接消歧、OWL/RDF、Neo4j/NebulaGraph、Microsoft GraphRAG |

---

### Part V Agent 基础能力（10 章 / ~250 页）：子翔

**Block A · 执行底座**

| # | 章节 | 关键议题 |
|---|---|---|
| 22 | Agent Runtime | 任务执行、状态机、检查点、失败恢复、超时重试 |
| 23 | Tool Registry & Function Calling | 能力注册、Schema、版本治理、调用契约 |
| 24 | MCP 与企业工具生态 | host-client-server、tools/resources/prompts、企业接入 |

**Block B · 智能与编排**

| # | 章节 | 关键议题 |
|---|---|---|
| 25 | Planner 与编排模式 | ReAct、Plan-and-Execute、状态机、工作流取舍 |
| 26 | Agentic Workflow | Reflexion、Self-Refine、Tree of Thoughts、AutoGPT 范式批判 |
| 27 | Memory 系统 | 短期/长期/用户画像/企业上下文；与 RAG 边界；mem0、Letta 对标 |
| 28 | 多 Agent 协作 | Planner/Router/Executor/Reviewer 分工；通信协议；冲突仲裁 |
| 29 | Agent 协议与标准 | MCP、A2A、Agent Card、ACP；跨平台协作 |

**Block C · 控制与对标**

| # | 章节 | 关键议题 |
|---|---|---|
| 30 | Human-in-the-loop 与长任务 | 审批、打断、回放、异步队列、检查点 |
| 31 | 框架横向对标 | LangGraph、AutoGen、CrewAI、Dify、Coze、Bisheng；何时自研何时用 |

---

### Part VI DataAgent 主线深潜（6 章 / ~150 页）⭐ 扩充：骆阳

| # | 章节 | 关键议题 |
|---|---|---|
| 32 | DataAgent 产品形态 | NL2SQL → 数据任务 OS；ChatBI 对标；四种产品形态 |
| 33 | 语义层工程 | 指标口径、维度关系、业务术语、Schema Linking、消歧策略 |
| 34 | NL2SQL 工程化 | DAIL-SQL、DIN-SQL、CHESS、CodeS；SQL 生成、纠错、安全执行 |
| 35 | Text-to-Pandas / Text-to-Python | PandasAI、Code Interpreter、Python 沙箱、数据分析 Agent |
| 36 | 数据分析、可视化与报告 | Auto-EDA、Lida、Chat2VIS；图表选型；洞察与行动建议；报告模板 |
| 37 | DataAgent 对标与生态 | DB-GPT、Vanna、WrenAI、Defog、Sherlock；商业产品对比 |

---

### Part VII 可观测性、评估与成本（5 章 / ~120 页）⭐ 扩充：韵洋

| # | 章节 | 关键议题 |
|---|---|---|
| 38 | 可观测性与 Trace | OpenTelemetry GenAI 语义约定、Langfuse、Phoenix、Helicone、会话回放 |
| 39 | 离线评估与基准 | Ragas、TruLens、DeepEval、Promptfoo；Spider/BIRD（NL2SQL）、MTEB、HELM |
| 40 | 在线评估与 LLM-as-Judge | 用户反馈、对比测试、LLM-as-Judge 偏差、可信度评估 |
| 41 | 成本治理与缓存 | 模型路由、prompt cache、semantic cache、GPTCache；token 成本核算 |
| 42 | SLO、限流与降级 | 延迟/质量 SLO、降级策略、熔断、配额 |

---

### Part VIII 部署与基础设施（4 章 / ~90 页）⭐ 新增：旭宏

| # | 章节 | 关键议题 |
|---|---|---|
| 43 | GPU 调度与 Kubernetes | Kubernetes + Volcano / Kueue、Slurm、Ray；GPU 共享、MIG |
| 44 | 模型部署 | KServe、BentoML、Triton、Ray Serve；A/B、灰度、版本管理 |
| 45 | LLM 网关与多租户 | LiteLLM、Portkey、Higress AI Gateway、Kong AI；rate limit、quota、租户隔离 |
| 46 | GitOps、IaC 与边缘推理 | ArgoCD、Terraform、Helm；ONNX Runtime、llama.cpp、MLC、端侧部署 |

---

### Part IX 前端、交互与多模态（3 章 / ~70 页）⭐ 新增：刘中一

| # | 章节 | 关键议题 |
|---|---|---|
| 47 | 对话 UI 与流式输出 | Vercel AI SDK、CopilotKit、assistant-ui；SSE、流式、增量渲染 |
| 48 | Generative UI 与富交互 | Tool Call 渲染、图表/表格嵌入、Artifacts 范式 |
| 49 | 多模态输入与语音 Agent | Whisper、TTS、Realtime API；语音/图像/文件上传 |

---

### Part X 安全、合规与组织（4 章 / ~90 页）⭐ 扩充：刘中一

| # | 章节 | 关键议题 |
|---|---|---|
| 50 | 安全与攻防 | Prompt Injection、Red Teaming（PyRIT、Garak）、工具越权、数据泄漏；OWASP LLM Top 10 落地 |
| 51 | Guardrails 与内容安全 | NeMo Guardrails、Llama Guard、Azure Content Safety、敏感词与脱敏 |
| 52 | 合规与法规 | NIST AI RMF（含 GenAI Profile）、EU AI Act、中国《生成式 AI 服务管理办法》、深度合成规定、模型水印 C2PA |
| 53 | 组织、人才与平台演进路线图 | 团队组成、与业务部门协作、ROI 度量、3 年演进路线 |

---

### Part XI AI 原生业务系统案例集（2 章 / ~50 页）⭐ 收敛：旭宏/骆阳

> 业务案例从 v2 的 6 章压缩为 2 章合集，避免与 Part VI（DataAgent）和 Part V（Agent 能力）重复。每个案例 8-10 页，聚焦"业务背景 → 数据与工具拓扑 → Agent 设计 → 上线复盘"。

| # | 章节 | 包含案例 |
|---|---|---|
| 54 | 业务 Agent 案例集（上） | 企业知识助手、工单/客服 Agent、研发 Agent、运维 Agent |
| 55 | 业务 Agent 案例集（下）+ 平台化收束 | 销售/财务/法务 Agent；从单点 Agent 到企业 AI 原生业务平台 |

---

### 附录（~80 页，不计入主体 1150 页）

- **A.** mini-enterprise-agent-platform 安装与速览
- **B.** 术语表（~120 条）
- **C.** API 速查（Runtime / Registry / Eval / Trace / Gateway）
- **D.** 评测集与数据集（DataAgent / RAG / 安全）
- **E.** 章节贡献模板与写作规范
- **F.** 参考资料与延伸阅读（论文、官方文档、对标产品）
- **G.** 全栈技术对标速查表（按 10 个 Part 分类）
- **H.** 法规与合规清单（OWASP / NIST / EU AI Act / 中国办法）

### 篇幅核算

| Part | 章数 | 页数 |
|---|---|---|
| I 总论 | 4 | 70 |
| II 模型与推理 | 5 | 120 |
| III 数据基础设施 | 6 | 150 |
| IV 向量与知识工程 | 6 | 140 |
| V Agent 能力百科 | 10 | 250 |
| VI DataAgent 主线 | 6 | 150 |
| VII 可观测性/评估/成本 | 5 | 120 |
| VIII 部署与基础设施 | 4 | 90 |
| IX 前端与多模态 | 3 | 70 |
| X 安全/合规/组织 | 4 | 90 |
| XI 业务案例集 | 2 | 50 |
| **合计** | **55** | **1300** |

> 注：1300 页是「足量假设」上限；实际写作会按需收敛到 **1100-1150 页**主体（含图与代码留白）。

---

## 3. mini-enterprise-agent-platform 参考实现（v3 扩充）

### 仓库结构

```
mini-enterprise-agent-platform/
├── core/                       # 平台内核
│   ├── runtime/                # 状态机、检查点、重试
│   ├── registry/               # Tool/Agent 注册中心
│   ├── memory/                 # 短期/长期记忆
│   ├── planner/                # ReAct / Plan-and-Execute / Reflexion
│   ├── rag/                    # 检索、重排、引用、混合检索
│   ├── observability/          # OTel trace + 会话回放
│   ├── eval/                   # 评测框架 + 评分器
│   ├── policy/                 # 权限、脱敏、敏感操作拦截
│   ├── gateway/                # LLM 网关、路由、缓存、限流  ⭐新增
│   └── guardrails/             # 内容安全、注入检测       ⭐新增
├── infra/                      # 数据基础设施集成        ⭐新增
│   ├── lakehouse/              # Iceberg / Duck DB 适配器
│   ├── metadata/               # DataHub / OpenLineage 客户端
│   ├── semantic_layer/         # Cube / MetricFlow 适配
│   └── vectorstore/            # pgvector/Milvus/Qdrant 适配
├── tools/                      # 内置工具
│   ├── mcp_db/                 # MCP 数据库工具
│   ├── mcp_docs/               # MCP 文档工具
│   ├── sql_executor/           # SQL 安全执行 + 字段脱敏
│   ├── python_sandbox/         # Python 沙箱（Docker/WASM）
│   ├── chart_renderer/         # 图表生成
│   ├── doc_parser/             # 文档解析（unstructured/Marker）⭐新增
│   └── kg_builder/             # 知识图谱构建            ⭐新增
├── agents/                     # 参考 Agent
│   ├── data_agent/             # DataAgent（主线）
│   ├── knowledge_agent/        # 企业知识助手
│   ├── ticket_agent/
│   ├── devops_agent/
│   └── workflow_agent/
├── console/                    # 管理后台 + Generative UI 示例 ⭐扩充
├── datasets/                   # 脱敏样例 + 评测集
├── benchmarks/                 # Spider/BIRD/MTEB 跑通脚本   ⭐新增
└── projects/                   # 16 个实战项目
```

### 技术栈选型

- **语言**：Python 3.11+（主体），TypeScript（Console + Vercel AI SDK 示例）
- **LLM 抽象**：OpenAI Python SDK 兼容协议；网关层支持 vLLM / SGLang / 国产模型
- **协议**：MCP 主路径 + Function Calling 兼容路径 + A2A 实验性
- **数据**：SQLite/PostgreSQL/DuckDB；Iceberg via PyIceberg；Cube 语义层
- **向量库**：pgvector（默认）→ Milvus / Qdrant
- **可观测性**：OpenTelemetry + Langfuse / Phoenix 集成
- **网关**：LiteLLM（默认）；可换 Portkey / Higress AI
- **部署**：Docker Compose（本地）→ Kubernetes + KServe（生产示例）
- **不绑定**：所有 SaaS 与商业组件都给开源替代路径

### 16 个实战项目

| # | 项目 | 关联章节 | 难度 |
|---|---|---|---|
| 1 | 最小可用 Agent Runtime | Ch22 | ★ |
| 2 | Tool Registry + Function Calling Demo | Ch23 | ★ |
| 3 | MCP 数据库工具服务 | Ch24 | ★★ |
| 4 | 企业知识库 RAG Agent | Ch20 + Ch54 | ★★ |
| 5 | NL2SQL DataAgent v1 | Ch33 + Ch34 | ★★★ |
| 6 | SQL 安全执行与权限过滤 | Ch34 + Ch50 | ★★ |
| 7 | Python 分析沙箱与图表生成 | Ch35 + Ch36 | ★★ |
| 8 | Agent Trace 与会话回放 | Ch38 | ★★ |
| 9 | DataAgent Eval 评测平台 | Ch39 + Ch36 | ★★★ |
| 10 | 多 Agent 业务流程：问题→数据→报告→审批 | Ch28 + Ch30 + Ch55 | ★★★ |
| 11 | vLLM + LiteLLM 模型路由网关 ⭐ | Ch6 + Ch45 | ★★ |
| 12 | Iceberg + DuckDB 数据湖查询 ⭐ | Ch11 + Ch12 | ★★ |
| 13 | 嵌入模型微调 + 向量库 benchmark ⭐ | Ch17 + Ch18 | ★★★ |
| 14 | GraphRAG 知识图谱构建 ⭐ | Ch21 | ★★★ |
| 15 | Ragas + Spider 评测自动化流水线 ⭐ | Ch39 | ★★★ |
| 16 | Generative UI DataAgent 前端 ⭐ | Ch47 + Ch48 | ★★ |

每项目强制包含：`README.md`、`requirements.txt`、`data/`、`evals/`、`run.sh`、`notebooks/`。

### 书稿与代码的双向引用

- 书中 L3 代码片段指向 mini-platform 真实文件路径
- mini-platform PR commit message 标注关联章节
- CI 校验代码行号一致性

---

## 4. 章节统一模板

```markdown
# Ch.NN 章节标题

> 本章目标：读者学完能做到 ……
> 前置阅读：Ch.X / Ch.Y    估计阅读：L1 15min / L1+L2 45min / 全章 90min
> mini-platform 关联：core/<module>/ 或 infra/<module>/    项目：projects/NN-name/

## L1 概念  〔约 30% 篇幅〕
### 1.1 业务场景：为什么企业需要这个能力
### 1.2 核心概念与边界（含对比表）
### 1.3 常见误区

## L2 架构  〔约 40% 篇幅〕
### 2.1 在平台中的位置（架构图 + 数据流）
### 2.2 组件划分与接口契约
### 2.3 状态机 / 时序 / 失败模式
### 2.4 设计取舍（≥2 个 trade-off 决策表）

## L3 工程实现  〔约 30% 篇幅〕
### 3.1 mini-platform 中的实现路径
### 3.2 可运行代码与配置
### 3.3 生产化 checklist
### 3.4 踩坑记录（≥3 条真实场景）

## 本章小结
- 关键结论 3-5 条
- 检查清单：能上线吗？能扩展吗？能治理吗？
- 延伸阅读：官方文档、论文、对标产品
```

---

## 5. 写作规范与质量门禁

### 配图标准
- 架构图、时序图、状态机：统一 Mermaid → SVG
- 配色三色制：蓝=组件 / 灰=外部系统 / 红=控制流
- 取舍表固定列：方案 / 优势 / 代价 / 适用场景 / mini-platform 选择
- 每章 5-12 张图，全书约 500 张

### 写作风格
- 第三人称客观叙述
- 所有 Python 代码块对应 `projects/` 测试，CI 跑通
- 每次出现框架 API 必须说明"为什么用"和"替代方案"
- 统一使用虚构公司「山岚集团」（零售/制造/金融/物流）作为案例背景
- 禁用 emoji 与营销腔

### 术语表
- v0.1 至少 50 条 → v0.5 100 条 → v1.0 120 条
- CI 校验：L1/L2 段落不得出现表外英文缩写未解释

### 质量门禁（CI/CD）
| 检查项 | 工具 | 时机 |
|---|---|---|
| Markdown 语法 | markdownlint | PR |
| 链接有效性 | lychee | PR + 每周 cron |
| 图片引用一致性 | 自定义脚本 | PR |
| 术语统一 | 自定义脚本 | PR |
| 代码可运行 | pytest（projects/ 全跑） | PR + nightly |
| 章节模板完整性 | 自定义脚本 | PR |
| 敏感信息扫描 | gitleaks + 关键词清单 | PR |
| 字数与篇幅 | 自定义脚本 | nightly |
| 图片大小与格式 | 自定义脚本 | PR |
| 引用版本一致性 | 自定义脚本 | nightly |
| **跨章节引用一致性** ⭐新增 | 自定义脚本 | nightly |

### 仓库目录

```
agent_platform_book/
├── docs/
│   ├── part01-overview/
│   ├── part02-model-inference/
│   ├── part03-data-infra/
│   ├── part04-vector-knowledge/
│   ├── part05-agent-capabilities/
│   ├── part06-dataagent/
│   ├── part07-observability-eval/
│   ├── part08-deployment/
│   ├── part09-frontend-multimodal/
│   ├── part10-security-org/
│   ├── part11-cases/
│   └── appendix/
├── mini-platform/              # monorepo 子目录
├── assets/                     # Mermaid 源 + SVG
├── glossary/                   # 术语表（CI 校验源）
├── templates/                  # 章节、贡献模板
├── scripts/                    # CI 校验脚本
├── .github/workflows/
└── mkdocs.yml
```

**采用 monorepo**：书 + 代码 + 评测同步演进。

---

## 6. 发布路线 v3

> v3 体量更大，路线相应延长；Part 间最大化并行。

| 版本 | 里程碑 | 内容 | 累计周期 |
|---|---|---|---|
| **v0.1** | 骨架就绪 | 书名、README、55 章空壳、术语表 v1（50 条）、章节模板、CI 流水线、mini-platform 初始化 | 3 周 |
| **v0.2** | 总论 + 模型推理 | Part I（4 章）+ Part II（5 章）+ Project 1/11 | +6 周 |
| **v0.3** | 数据基础设施 + 向量知识 | Part III（6 章）+ Part IV（6 章）+ Project 12/13/14 | +10 周 |
| **v0.4** | Agent 能力百科 | Part V（10 章）+ Project 2/3 | +10 周 |
| **v0.5** | DataAgent 主线 | Part VI（6 章）+ Project 5/6/7 + DataAgent 评测集 | +8 周 |
| **v0.6** | 可观测/评估/成本 + 部署 | Part VII（5 章）+ Part VIII（4 章）+ Project 8/9/15 | +8 周 |
| **v0.7** | 前端多模态 + 安全合规 | Part IX（3 章）+ Part X（4 章）+ Project 16 | +6 周 |
| **v0.8** | 业务案例集 | Part XI（2 章）+ Project 4/10 | +4 周 |
| **v0.9** | 内测对齐 | 交叉引用、术语统一、配图统一、外部 reviewer | +6 周 |
| **v1.0** | 正式发布 | 55 章 + 16 项目 + 8 附录 + 评测集 + 部署文档 | +3 周 |
| **v1.1+** | 持续运营 | 行业案例、PPT、视频脚本、纸质排版 | 持续 |

**并行策略**：
- Part II/III/IV 可由不同作者并行（v0.2-v0.3 阶段同步）
- Part V Block A/B/C 可并行（v0.4 阶段）
- Part VII/VIII/IX 可并行（v0.6-v0.7 阶段）

---

## 7. 贡献机制

### 四类贡献者

- **主编 / 总编**（1-2 人）：负责风格统一、跨 Part 一致性
- **Part Owner**（10 人，每 Part 一名）：负责本 Part 章节统筹与质量
- **章节贡献者**：认领单章
- **校对与案例提供者**：踩坑案例、术语修正、配图

### 流程

1. GitHub Issue 认领章节 → `templates/chapter-claim.md`
2. 在 `feature/partXX-chYY-<topic>` 分支撰写
3. PR 触发全部 CI 门禁
4. Part Owner + 主编 + ≥1 reviewer 评审
5. 合并后部署到 MkDocs `next` 频道
6. 每月 milestone 合并到 `main`，发布 `stable` 频道

### 激励
- 所有贡献者在 README + 章末 + 印刷版鸣谢中署名
- 企业案例提供方作为「案例合作伙伴」在附录 D 署名（脱敏）
- 重要贡献者邀请进入封面署名

---

## 8. 默认假设（v3 终稿）

1. 书名固定：《企业级 Agent 平台工程：从数据智能底座到 AI 原生业务系统》
2. 结构：10 Part + 55 章 + 16 项目 + 8 附录，主体 ~1150 页
3. 三层阅读法 L1/L2/L3 强制贯穿
4. DataAgent 作为主线案例贯穿 Part III-VI；Part VI 集中深潜（6 章 150 页）
5. mini-platform 自建参考实现，monorepo 与书稿同源
6. 虚构公司「山岚集团」作为统一业务背景
7. 不追求纸质出版排版（v1.0 之前）；不绑定单一框架与厂商
8. 全栈覆盖：模型/数据/向量/Agent/DataAgent/评估/部署/前端/安全九大技术分类
9. 读者门槛：Python、Web API、数据库、大模型应用基本经验
10. 开源协议：书稿 CC BY-SA 4.0；mini-platform Apache 2.0

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解策略 |
|---|---|---|
| 55 章体量巨大，单人难维护 | 进度慢、风格漂移 | 主编 + 10 Part Owner 分布式治理；强制章节模板 + CI 门禁 |
| 技术栈快速演进，案例过时 | 1 年后陈旧 | mini-platform 抽象优先；每季度 nightly 重跑全部 projects；半年补录新模型/新框架 |
| 真实企业案例难脱敏 | Part XI 稀薄 | 「山岚集团」虚构背景统一覆盖；3-5 家企业合作方提供脱敏案例 |
| 与同类书重复 | 差异化不足 | 强调"全栈 + 平台视角 + 工程取舍"，非框架教程；中文权威定位 |
| mini-platform 工作量过大 | v0.5 延期 | core/ 按章节优先级分批；infra/ 用现成开源工具集成而非自研 |
| 安全/合规法规变化 | Part X 过时 | Part X 设计为"框架 + checklist"，非具体法规条款 |
| 跨 Part 内容重复或矛盾 | 阅读体验差 | CI 跨章节引用一致性脚本；每季度交叉评审；术语表强约束 |
| 写作节奏失控 | v1.0 大幅延期 | 按 Part 解耦发布；v0.1-v0.8 每个里程碑独立可用 |

---

## 10. v0.1 开工清单

| # | 工作项 | 关键产出 |
|---|---|---|
| 1 | 创建 `docs/` 11 Part 目录及 55 章空壳 | 每章一个 .md 文件，套用 7 Section 模板 |
| 2 | 编写 README.md | 含五条读者路径、三层阅读法、贡献入口、全栈技术地图 |
| 3 | 编写 `templates/chapter-template.md` | 完整章节模板，L1/L2/L3 骨架 |
| 4 | 编写 `glossary/terms.md` | 至少 50 条术语（v0.1）→ 120 条（v1.0） |
| 5 | 初始化 `mini-platform/` | `core/{runtime,registry}` + `infra/{lakehouse,vectorstore}` 最小 stub |
| 6 | 配置 `mkdocs.yml` | Material 主题、按 11 Part 分组导航 |
| 7 | 编写 `.github/workflows/ci.yml` | 全部 11 项质量门禁 |
| 8 | 编写 `scripts/` 校验脚本 | 术语 / 链接 / 模板 / 敏感信息 / 跨章节一致性 |
| 9 | 招募 Part Owner（10 人）+ 主编 | Issue 公开招募；锁定 Part II/III/IV/VI Owner |
| 10 | 启动外部反馈渠道 | Issue 模板、Discussion、贡献者入门指南、全栈技术地图海报 |

### v0.1 验证标准

- [ ] `mkdocs serve` 本地起站，55 章空壳页面可访问
- [ ] CI 流水线在 PR 上跑通全部 11 项检查
- [ ] `templates/chapter-template.md` 被任一空壳章节使用，模板完整性脚本通过
- [ ] `glossary/terms.md` 至少 50 条核心术语
- [ ] `mini-platform/core/` 含 runtime / registry 最小可运行 stub；`infra/` 含 lakehouse / vectorstore 适配器骨架
- [ ] README 五条读者路径 + 全栈技术地图清晰可读
- [ ] 至少 4 名 Part Owner 已认领（Part II 模型、Part III 数据、Part IV 知识、Part VI DataAgent）
