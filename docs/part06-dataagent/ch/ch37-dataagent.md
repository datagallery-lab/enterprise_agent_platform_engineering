# 第37章 DataAgent 对标与生态

---

## 本章摘要

本章对 DataAgent 相关产品和开源生态做对标，说明 BI Copilot、Notebook Agent、语义层工具和分析工作台各自适合的边界。这个领域产品形态分化严重：有的强在问数，有的强在 Notebook 协作，有的更接近语义层工具。直接比较“谁更好”没有意义，应先看它覆盖 DataAgent 链路的哪一段。本章把 DB-GPT、ChatBI 等主流开源方案与商业产品按能力维度拉成对照，帮助团队判断该自建、采购还是组合。

## 关键词

DataAgent 对标、BI Copilot、Notebook Agent、语义层工具、开源方案、能力对照

## 学习目标

- 能说明 DataAgent 生态为什么分化，不同产品强在链路的哪一段。
- 能区分 BI Copilot、Notebook Agent、语义层工具、分析工作台的边界。
- 能用能力维度对照 DB-GPT、ChatBI 等开源方案与商业产品。
- 能据团队需求判断 DataAgent 该自建、采购还是组合。

---

## 场景引入

Part VI 前五章分别定义产品边界（第32章）、语义层（第33章）、NL2SQL（第34章）、Python 分析（第35章）与表达层评估（第36章）。读者若已跟随 [第32章 §4 华东下滑案例](ch32-dataagent.md) 走完一条 Run 链，会自然产生一个问题：业界已有大量 DataAgent / Text-to-SQL 产品，多业务线场景该自建、采购还是混合？

采购和自研通常需要拆开判断。较稳妥的路线，是把外部产品放回 Part V 的 Runtime、Registry、Trace 和 Policy 之下，再判断它覆盖 DataAgent 链路的哪一段。后面的内容先解释生态为什么分化，再对照主流方案的能力覆盖、ChatBI 与 DataAgent 的边界，以及评估集如何支撑选型后的持续改进。

---

## 37.1 DataAgent 生态的分化来源

市场上很难找到一个可直接采购上线的标准 DataAgent 产品。DataAgent 同时牵涉对话入口、Text-to-SQL 技术、企业部署合规和组织级数据治理。多数产品只从其中一条轴线起步，其余能力靠集成或外接补齐。四类分化轴如下：

*表37-1：DataAgent 生态各分化轴的典型产物与能力缺口。来源：本书整理。*

| 分化轴 | 典型产物 | 能力缺口 |
| --- | --- | --- |
| 入口 | ChatBI 对话框 | 缺平台治理（Runtime、Registry、Trace） |
| 技术路线 | Text-to-SQL 库（如 Vanna，见 §2 说明） | 缺语义层与 HITL |
| 部署 | SaaS Copilot | 缺私有化与多租户 |
| 组织 | 数据中台项目 | 缺 Agent Runtime 与 Run 六态 |

以零售经营分析场景为例：运营总监一句「上周华东 GMV 下滑 Top SKU」，背后至少需要 Question Frame 解析（第32章）、Metric 绑定与消歧（第33章）、只读 SQL 执行（第34章）、品类贡献度 Python（第35章）、图表与报告审批（第36章），还需要贯穿全程的 Run 审计与评估（第37章、第39章）。采购一个“对话查数”SaaS，通常只覆盖入口与 NL2SQL 演示；语义层口径、沙箱分析、人工审批仍须企业自建或二次集成。

产品比较不宜从功能清单开始。更可靠的顺序是先列出业务工作流：谁提问、用哪个指标口径、能否追问、是否要审批、报告发给谁、失败后谁修样本。只有这些约束明确后，Vanna、WrenAI、DB-GPT、Defog 或 BI Copilot 才能放到合适的位置。否则团队很容易买到一个演示效果很强的 NL2SQL 工具，却在上线时发现它没有 Metric 版本、没有 `tenant_id` 注入，也没有报告级证据。

LLM/Agent-as-Data-Analyst 综述将分析 Agent 所需能力归纳为语义感知、工具链编排、自主流水线等多维组合 (Tang et al. 2025)。极少有单一产品一次覆盖这些能力。企业落地更常见的形态是：Part V 平台（第22章至第30章）加语义层（第33章），再配合第34章至第36章的专用工具，通过 Registry 统一审计。单个 ChatBI 产品通常覆盖不了这条链路。

公开 benchmark 也在推动这一认知转变。Spider 2.0 (Lei et al. 2024) 与 BIRD-INTERACT (Huo et al. 2026) 把评测从“单句翻译 SQL”推向企业 workflow、多轮澄清与交互式纠错。这与第32章定义的诊断、对比、报告链路一致。产品若仍停留在“把自然语言变成一条 SELECT”，在华东下滑这类多步分析 Run 上很快会暴露边界。

### 37.1.1 产品选型与集成风险

部署一个 ChatBI 不等于部署 DataAgent 平台。ChatBI 往往是问数形态的子集（第32章 §2），缺少 `waiting_human` 审批链、Handoff 与跨 Agent 编排；经营月报 Run 链仍须 Part V Runtime。

引入 DB-GPT 也不能替代 Part V 的平台能力。DB-GPT (eosphoros-ai 2024) 是开源 Agent 应用框架，自带 Runtime 壳与数据插件；若企业已建设 `core/runtime/` 与 `core/registry/`，再整包引入会形成双 Runtime（见第31章“低代码平台的边界风险”）。更稳的方式是接组件，不接平台壳。

NL2SQL 演示准确率不足以支撑上线判断。华东案例在 Linking 阶段就存在 `gmv_tax_excluded` 与 `gmv_ops` 歧义（第33章 §4）；没有业务金标准集与口径脚注评估，上线后口径投诉率会掩盖 SQL 语法正确率。

---

## 37.2 开源框架与商业产品分类

Vanna、WrenAI、DB-GPT、Defog、Sherlock 和 Power BI Copilot 名字相近，但定位差异很大。Vanna 更像 Question-SQL 检索增强库，用向量库检索历史问题和 SQL，适合快速验证私有 schema 适配。WrenAI 把语义层和对话式 BI 放在一起，更接近 Metric 建模与问数一体化。DB-GPT 提供 Agent 应用框架和数据插件模板，适合从零搭建数据应用，但容易与 Part V 的企业 Runtime 形成双运行时。Defog 偏 Text-to-Python 和自动报告，适合分析与叙事链路。Sherlock 更像研究型深度分析 Agent 原型，可以参考推理链，但企业治理能力较弱。Power BI Copilot 是 BI 产品内置 Copilot，适合改图表和筛选，不应直接等同于平台化 DataAgent。

后续对比不以“谁更好”为主线，而看它们分别落在平台哪一层。能作为工具的进入 Registry，能作为语义层后端的进入第33章，能提供评测样例的进入第39章；只有承担 Run 状态、权限、审计和恢复责任的部分，才有资格进入平台内核。

### 37.2.1 生态地图

按“偏库/偏平台”与“偏 NL2SQL/偏完整任务”两个维度看，Vanna 更接近 Question-SQL 检索增强库，适合快速适配私有 schema；WrenAI 处在语义层与对话式 BI 的中间位置，更容易和第33章的 Metric 建模发生关系；Defog 更靠近 Python 分析和报告生成，和第35章、第36章重叠；DB-GPT 更像开源平台壳，提供 Agent 应用框架和数据插件模板；Power BI Copilot 则是嵌入 BI 产品内部的 Copilot，不应直接等同于企业级 DataAgent。

![图37-1：DataAgent 生态能力地图](../../images/part6/ch/ch37-dataagent-ecosystem-map.svg)

*图37-1：DataAgent 生态能力地图。来源：本书自绘。Alt text：图中以偏库到偏平台、偏 NL2SQL 到偏完整任务两个维度放置 Vanna、WrenAI、DB-GPT、Defog、BI Copilot 和本书 mini-platform，说明各方案覆盖的能力边界。*

这种定位比简单打分更重要。若企业缺的是语义层，WrenAI 或 Cube 类能力值得重点验证；若缺的是历史 Question-SQL 检索增强，Vanna 更像一个可包装进 `tools/sql_executor/` 的训练或检索组件；若缺的是 Text-to-Python 与报告模板，Defog 的思路可以参考，但沙箱、权限和报告审批仍应回到企业平台；若企业已经有第22章至第30章的 Runtime、Registry、Trace 和 Policy，则引入 DB-GPT 这类平台型项目要格外谨慎，避免形成第二套 Runtime。

mini-platform 在这张地图里的角色不是“又一个产品”，而是本书用来固定接口和责任边界的参照实现。外部组件可以进入体系，但进入方式应是 Registry Tool、语义层后端、NL2SQL 训练管线或报告模板，而不是绕过 Part V 平台直接接管任务状态。

---

## 37.3 主流开源方案对比（DB-GPT、Vanna、WrenAI、Defog、Sherlock）

§2 已说明各开源项目的基本定位。本节进一步回答它们分别覆盖 Part VI 哪几章的能力，以及与 mini-platform 模块如何对照。

*表37-2：DB-GPT、Vanna、WrenAI 等开源方案按能力维度的对照。来源：本书整理。*

| 能力 / 章节 | DB-GPT | Vanna | WrenAI | Defog | Sherlock | mini-platform（书中模块） |
| --- | --- | --- | --- | --- | --- | --- |
| Agent Runtime (第22章) | 自有 | 无 | 部分 | 部分 | 实验 | ✓ `core/runtime/` |
| Tool Registry (第23章) | 部分 | 无 | 部分 | 部分 | 无 | ✓ `core/registry/` |
| 语义层 (第33章) | 可接 | 弱 | 强 | 中 | 弱 | `infra/semantic_layer/` · `agents/data_agent/linker.py` |
| NL2SQL (第34章) | ✓ | 强 | ✓ | 中 | 中 | `tools/sql_executor/` |
| Python 沙箱 (第35章) | ✓ | 弱 | 弱 | 强 | 中 | `tools/python_sandbox/` |
| 报告/图表 (第36章) | 部分 | 弱 | 中 | 强 | 中 | `tools/chart_renderer/` · `agents/data_agent/templates/` |
| HITL / 多租户 | 弱 | 弱 | 中 | 中 | 弱 | ✓ Part V Run 链 · `core/policy/` |
| 企业 Eval (第36章至第39章) | 部分 | 弱 | 中 | 中 | 研究 | `core/eval/` · 第39章 |

!!! note "mini-platform 落地状态"
    表中 Part V 模块（`core/runtime/`、`core/registry/` 等）与 `mini-platform/projects/multi-agent-workflow/` 已在仓库中存在。
    Part VI 列（`tools/sql_executor/`、`tools/python_sandbox/`、`infra/semantic_layer/client.py` 等）为书中目标契约，随 Part VI 工程迭代合入；选型评估应以实际验证为准，不能假定仓库已包含全部目录。

*能力评分为方向性对照，非版本打分（2025-06 核对）。*

### 37.3.1 各方案选型要点

Vanna (vanna-ai 2024) 以向量检索历史 SQL 与库表 schema 片段见长，适合私有 schema 的快速适配。华东案例若只用 Vanna，可较快生成 Top SKU 查询，但 GMV 歧义消歧（`gmv_ops` vs `gmv_tax_excluded`）与 View 级权限须外接 `infra/semantic_layer/` 与 `core/policy/`，否则难进生产。

WrenAI (Canner 2024) 强调语义层与对话式 BI，与第33章路线最接近。`sales_ops` View 与 Metric 版本策略可直接类比。WrenAI 仍须接企业 `core/runtime/` 与第30章 HITL；多 Agent 治理不宜与 Part V 双轨并行。

DB-GPT (eosphoros-ai 2024) 提供 Agent 应用壳与数据插件。若企业已有第22章至第30章平台，更可靠的做法是让 NL2SQL 训练或插件逻辑经 Registry 注册为 Tool，不引入第二套 Runtime（与 [第31章](../../part05-agent-capabilities/ch/ch31.md) 框架对标结论一致）。

Defog (Defog.ai 2024) 偏 Text-to-Python 与自动报告，与第35章至第36章的 `python_sandbox` + `chart_renderer` 组合高度重叠。华东经营下滑分析场景的品类贡献度步骤可对标 Defog 强项；取数仍应走 `sql_executor` 只读链路。

Sherlock 属研究型深度分析 Agent 原型，在复杂推理链设计上有参考价值，但通常缺少企业级 Runtime、行级权限与评估流水线。不建议整包替换 Part V 平台；Planner 多步推理策略可借鉴，实现仍应回到 `core/planner/`。

对标开源方案时，最容易低估的是集成后的运行责任。引入第二套 Runtime，Trace 会分裂；绕过企业语义层，指标口径会分裂；让供应商工具直接执行 SQL，Policy 责任会分裂。比较表只能说明能力覆盖，不能替代架构判断。进入生产链路的外部组件，应先被包装成 Registry Tool，再接受同一套审计、限权、成本和 Eval 规则。

!!! note "对标不等于采购建议"
    上表随社区版本变化；选型时须完成实际验证与安全审计，本章仅提供能力映射与 mini-platform 模块对照。

---

## 37.4 ChatBI、BI Copilot、DataAgent 的产品差异

三类产品名称相近，职责边界不同：

*表37-3：ChatBI、BI Copilot、DataAgent 三类产品的差异。来源：本书整理。*

| 维度 | ChatBI | BI Copilot (Microsoft 2024) | DataAgent（本书） |
| --- | --- | --- | --- |
| 定位 | 对话查数 | BI 内嵌助手 | 平台托管数据任务 Agent |
| 语义层 | 不定 | 依赖 BI 数据集 | 强制 第33章 · `infra/semantic_layer/` |
| 多步分析 | 弱 | 中 | Planner 链第34章至第36章 · `sql_executor` → `python_sandbox` → `chart_renderer` |
| 审批 | 通常不支持 | 通常不支持 | HITL 第30章 · 报告级 `waiting_human` |
| 与 ERP/Agent 编排 | 弱 | 弱 | Handoff 第28章 · `agents/data_agent/` |
| 评测 | 依厂商 | 依厂商 | Spider 2.0 / BIRD-INTERACT + 业务金标准集 · `core/eval/` |

ChatBI 适合“单轮问数、用户规模小、合规要求低”的场景；一旦需要多轮澄清、Python 分析、报告审批与 Run 审计，即进入 DataAgent 范畴（第32章 四种产品形态）。

BI Copilot 降低已有 BI 用户的操作门槛，但口径通常绑定在 BI 数据集内，难以成为集团级 Metric 权威源。更稳的行业策略是：Tableau Copilot 做分析师辅助，覆盖库存和固定看板；DataAgent 做经营问数与月报 Run 链，覆盖华东下滑诊断、Controller 审批发布。二者可以并存，但口径必须统一到语义层 `infra/semantic_layer/models/`（第33章 经营分析样例），避免 Copilot 与 Agent 各说各的 GMV。

---

## 37.5 自研、采购与混合路线

### 37.5.1 四条建设路线的适用条件

*表37-4：自建、采购等四条路线的适用场景与风险。来源：本书整理。*

| 路线 | 适用 | 风险 |
| --- | --- | --- |
| 采购 SaaS ChatBI | 要快、用户少、可接受数据出境 | 口径不可控、难接 HITL 与 Eval |
| 采购 + 自建语义层 | 有中台与 Cube/dbt 基础 | 两套平台集成成本高 |
| 混合：平台自研 + 组件 | 有 Part V 团队 | 需架构纪律，禁止双 Runtime |
| 全自研 | 强合规、长期 ROI、定制深 | 初期交付慢 |

与 [第31章](../../part05-agent-capabilities/ch/ch31.md) 框架对标结论一致，Runtime、Registry、Observability 宜自研或统一于 Part V；NL2SQL 可接 Vanna 训练管线，包装为 `tools/sql_executor/` 的后端能力；语义层可用 Cube 或 Wren 引擎，由 `infra/semantic_layer/client.py` 统一 `resolve_metric()` 与 `compile_query()` 接口。外部组件经 Registry 的 HTTP 代理调用，业务代码不直连第三方 SDK。

该类场景适合混合路线：Part V 与 DataAgent 应用（`agents/data_agent/`）自研；语义层基于 Cube 风格 YAML 托管在 `infra/semantic_layer/models/`；NL2SQL 可借鉴 Vanna 的 question-SQL 检索增强 `sql_executor` 生成阶段，但执行与 Policy 不外包。

组织分工也要写进选型方案。平台团队负责 Runtime、Registry、Trace、Policy 与 Eval 流水线；数据团队负责语义层、指标版本、样本集和血缘；业务团队负责金标准问法、报告验收和建议采纳反馈。采购组件可以减少某一段实现成本，但这些职责仍要留在企业内部。职责不清时，系统出了错会变成「模型问题」「数据问题」「供应商问题」之间来回转移。

### 37.5.2 自研、采购与混合路线的决策表

自研和采购不是两列互斥选项，而是几条责任边界的组合。NL2SQL 引擎可以自研 Planner、Gateway 和 `sql_executor`，也可以把 Vanna 式训练或检索能力包装成 Registry Tool；无论采用哪条路，执行、权限、审计和错误反馈都应留在平台内。语义层可以基于 Cube、Wren 等开源引擎，也可以从自研 YAML 起步，但 `resolve_metric()`、`compile_query()` 和 `trusted_context()` 的接口要由企业掌握。

前端同样可以分层处理。经营问数和报告 Run 适合走第48章的 Generative UI 与报告审批链；已有 BI 场景可以嵌入 Power BI Copilot 或 Tableau Copilot，但口径应回写语义层，不能让 BI 数据集和 DataAgent 各自维护 GMV。Python 分析可以参考 Defog 的报告思路，但沙箱、权限、artifact 和 EvidenceRef 仍应由 `tools/python_sandbox/` 与第36章的表达层契约承接。

采购决策的底线是：任何引入方案不得绕过 `tenant_id` 注入、只读执行、`metric_id@version` 审计三件套（第34章 §5）。否则华东案例可在演示环境跑通，生产环境却无法通过安全评审。选型文档里真正要写清楚的，不是“用不用某个产品”，而是哪些能力外采、哪些能力保留、外采能力怎样进入 Registry 和 Trace。

---

## 37.6 评估与持续改进

选型回答“买什么”；Eval 回答“买或建之后有没有变好”。DataAgent 的 Eval 须公开 benchmark 与业务金标准集双轨并行。前者保证技术回归，后者保证口径与叙事贴合业务真实问法。

### 37.6.1 离线 Eval

公开集 Spider 2.0、BIRD、BIRD-INTERACT 用于技术回归；含义见 [第32章 §1](ch32-dataagent.md)。业务金标准集 用于口径与叙事，二者不可互相替代。

*表37-5：DataAgent 离线评测各层级的数据集与对应模块。来源：本书整理。*

| 层级 | 数据集 | 章节 | mini-platform |
| --- | --- | --- | --- |
| SQL 正确性 | BIRD、Spider 2.0 (Lei et al. 2024) | 第39章 | `core/eval/` SQL 子集 |
| 多轮交互 | BIRD-INTERACT (Huo et al. 2026) | 第39章 | 澄清 / ASK 场景回放 |
| 洞察与报告 | 业务金标准集（≥50 条） | 第36章 §6 | 口径脚注、EvidenceRef 覆盖率 |

业务金标准集应包含华东下滑 变体问法（如「销售额」vs「GMV」、「华东」vs「苏皖大区」），每条标注期望 `metric_id@version` 与是否触发 HITL。Eval 失败样本直接回流 `infra/semantic_layer/` Glossary 与 Prompt 版本。

### 37.6.2 在线指标

在线指标要服务具体改进，而不是只做增长看板。首问解决率反映产品可用性，但需要结合 Trace 判断是否靠错误答案“解决”；口径投诉率直接指向语义层、Glossary 和 Metric 版本；审批通过率反映报告模板、EvidenceRef 和 HITL 质量；Run 成本则把模型选型、重试、Python 分析和图表生成拉回第41章的成本治理。四类指标要按 Agent、租户、版本和任务类型拆开，否则平均数会掩盖真实问题。

持续改进的链路是：Eval 失败样本进入语义层、Glossary、Prompt 或 Tool 版本修订，再通过回归评测确认效果 (Liu et al. 2025)。与第31章的框架对标后迭代相同，DataAgent 迭代以业务样本为主、公开榜为辅。Spider 2.0 高分但华东案例口径脚注缺失，仍视为发布阻塞项。

失败样本要进入明确队列。口径绑定错，优先修 Glossary、Metric alias 或 View 权限；SQL 结构错，回到 schema linking、历史 Question-SQL 或 `sql_executor` 校验；图表字段不存在，修 `chart_renderer` spec 校验；报告话术夸大或缺 EvidenceRef，修模板和输出 Eval。这样做比笼统地「优化 prompt」慢一点，但每次改动都有归属，也能解释下一版为什么更好。

[第39章](../../part07-observability-eval/ch/ch39-dataagent-eval-benchmark.md) 与第50章提供平台级 Eval 与 Policy 自动化；Part VI 强调，业务样本不可只用公开 benchmark 替代。

---

## 37.7 企业选型最终要落到责任边界

### 37.7.1 选型结论最终要落到谁负责

CTO 和数据负责人做 DataAgent 选型时，最容易被演示效果牵着走。一个演示可以在固定 schema 上生成漂亮 SQL，也可以把图表和解释包装得很完整，但它未必回答了生产问题：谁拥有指标口径，谁限制 SQL 权限，谁在模型答错后修样本，谁能复现一个月前的报告。选型会议如果只比较功能截图，就会把这些责任问题推迟到上线前夕。

平台边界要先说清楚。企业是否强制语义层，禁止 Agent 长期直连物理表？是否已有 Agent Runtime、Registry 和 Trace，而不是停留在一个 Chat UI？NL2SQL 是否只读、是否注入 `tenant_id`、是否把 `metric_id@version` 写入审计？复杂分析是否进入沙箱 Python，还是把所有归因都塞进 SQL？对外报告是否经过 HITL 和 evidence 检查？这些问题决定外部产品能不能进入平台，采购选择只是后续动作。

运营证据也要进入评审。试点通过以后，团队至少要拿出三类样本：公开 benchmark 的回归结果、业务金标准问数集、线上用户反馈闭环。公开 benchmark 可以暴露技术能力下限，业务金标准集能暴露口径和叙事问题，线上反馈能暴露采纳率、投诉率和成本变化。三类证据缺一类，选型结论都会偏。Spider 2.0 或 BIRD-INTERACT 的抽测结果可以进入技术评审，但华东下滑、门店毛利、月末关账这类内部样本才决定系统是否可用 (Lei et al. 2024; Huo et al. 2026)。

接入方式决定后续能不能治理。外部组件如果以 Registry Tool 的形式接入，平台仍能统一审计、Trace、Policy 和成本归因；如果它自带 Runtime、权限系统和日志系统，企业就会得到第二套平台。第二套平台在试点时不明显，生产时会在事故复盘里暴露：Trace 断在外部服务，权限策略分散在两个地方，用户反馈不知道回到哪个样本库。第31章讨论框架选型时已经给出相同结论：可以借能力，不能让平台边界被组件拆散。

选型评审的输出不应只是一句“采用某产品”，还应包括一张责任分配表：哪些能力由外部产品提供，哪些能力由 `core/runtime/`、`core/registry/`、`infra/semantic_layer/`、`tools/sql_executor/`、`core/policy/` 和 `core/eval/` 保留；哪些数据会出域，哪些日志进入企业 Trace；失败样本由谁标注，下一版由谁回归。责任表说清楚后，采购、开源集成和自研才有共同语言。

### 37.7.2 走读：示例「华东下滑」案例贯穿 Part VI 六章

以下沿用 [第32章 §4](ch32-dataagent.md) 运营总监原话：「上周华东区销售相对前周明显下滑，主要 SKU 是哪些？和品类结构有没有关系？」

*表37-6：华东下滑案例贯穿 Part VI 六章各步骤与模块。来源：本书整理。*

| 章 | 本步做什么（白话） | mini-platform 模块 |
| --- | --- | --- |
| 第32章 | 把原话解析成 Question Frame：诊断任务、华东、上周 vs 前周、按 SKU 看 | `agents/data_agent/` |
| 第33章 | 把「GMV」绑定为 `gmv_ops@2025Q1`，「华东」展开为 `EAST`，输出可编译的 Linked Schema | `infra/semantic_layer/` · `linker.py` |
| 第34章 | 编译 Semantic SQL，服务端加 `tenant_id`，只读执行，取 Top SKU 宽表 | `tools/sql_executor/` |
| 第35章 | 读 SQL 结果文件，算各品类对下滑差额的贡献度 | `tools/python_sandbox/` |
| 第36章 | 画 SKU 贡献条形图，写经营会报告初稿，等人审批后发布 | `chart_renderer/` · `templates/` |
| 第37章 | 用业务金标准集与开源对标做 Eval，驱动下一版改 Glossary / Prompt | `core/eval/` |

六章串联的是同一条 Run（如 `run-8f3a`）：第32章至第33章在 Planner 启动前完成理解与 Linking；第34章至第36章在 Planner 循环内按序调用 Tool；第37章定义上线后如何用 Eval 证明较上季度改进，并约束下一版是否引入 Vanna / Wren 等组件。

上述问题把本章收束到一个判断：DataAgent 选型要确认业务链路中哪些环节可以外采，哪些环节必须受企业平台控制。Runtime、语义层、执行权限、Trace、HITL 和 Eval 的责任边界清楚时，外部组件可以进入体系；这些边界不清楚时，组件越多，故障归因越困难。

---

## 37.8 生态对标中的平台责任

DataAgent 生态对标不能停留在功能清单。开源框架、ChatBI 产品、BI Copilot 和企业内部平台都可能支持自然语言问数，但它们承担的责任不同。有些产品主要解决交互体验，有些框架主要提供生成 SQL 的链路，有些平台则要负责语义层、权限、执行、Trace、评测和发布治理。对标时如果只比较“能否问数”“是否支持图表”“是否支持多轮”，会低估生产化差异。

平台责任可以从三个问题判断。第一，系统是否知道自己基于什么口径回答。没有语义层和指标版本，回答正确也难以复核。第二，系统是否知道自己能执行什么。没有权限和工具治理，自然语言入口可能绕过原有数据边界。第三，系统是否知道自己错在哪里。没有 Trace 和评测，错误只能靠用户反馈和人工排查。一个 DataAgent 产品若无法回答这三个问题，就更适合作为试点工具，而不是核心数据入口。

生态对标还要考虑迁移成本。企业可能先采购一个 ChatBI 产品验证需求，再逐步把语义层、评测样本和运行日志迁回内部平台。也可能先自研核心 Runtime，再接入外部可视化或 BI Copilot。无论路线如何，关键是不要把核心证据资产锁在无法导出的系统里。问题样本、SQL、指标口径、Trace 和用户反馈，是 DataAgent 平台长期演进的资产。

## 37.9 选型后的持续评估

DataAgent 选型不是采购结束时完成，而是在运行中持续验证。上线初期应关注基本可用性：问题覆盖率、SQL 成功率、权限拒绝、响应时间和人工介入次数。进入稳定期后，更应关注业务信任：答案被采纳的比例、用户追问的类型、人工修订的原因、指标口径争议和事故复盘结果。只看调用量会误判系统价值，因为用户可能频繁调用一个并不可信的入口。

持续评估还要把产品体验和工程质量分开。界面顺畅、图表漂亮、回答自然，不能证明底层口径正确；SQL 准确、证据完整，也不代表用户愿意在业务流程中使用。平台团队需要同时观察两类指标：一类衡量用户是否愿意用，另一类衡量系统是否可治理。两类指标出现矛盾时，要优先保护可信边界，再改进体验。

本章放在 DataAgent 主体章节之后，目的不是给出某个产品排名，而是帮助读者形成判断框架。企业最终需要的不是一个会写 SQL 的模型，而是一套能把自然语言、指标口径、执行系统、证据链和组织责任连起来的平台能力。

## 37.10 生态能力的组合路线

企业不必在自研和采购之间做绝对选择。比较常见的路线是用商业产品验证交互和业务需求，用开源框架验证技术可行性，再把语义层、权限、Trace、Eval 和工具治理逐步沉淀到内部平台。也可以反过来，先建设内部 Runtime 和治理能力，再接入外部 BI、可视化或数据目录产品。路线不同，但核心原则相同：共享证据资产要留在企业可控范围内。

组合路线要避免重复建设。若商业产品已经提供成熟图表和报告体验，内部平台可以先聚焦语义层和运行治理；若内部已有强大的数据目录和权限系统，DataAgent 应优先复用它们，而不是另建一套轻量目录。生态对标的意义，是帮助团队决定哪些能力买、哪些能力接、哪些能力必须自己掌握。

这种组合思路也适合第一版书稿。读者不需要一开始就实现所有模块，但需要理解每个模块的责任和替换边界。只要边界清楚，后续引入新产品或替换旧框架时，平台主线不会被打断。

## 37.11 对标结论的复审方式

对标结论也需要复审。产品能力、开源项目活跃度、协议支持和商业条款都会变化，书稿不能把某个时间点的判断写成永久结论。更稳妥的写法是说明判断维度和适用条件，而不是给出绝对排名。比如某产品适合快速验证 ChatBI 场景，某框架适合研究型链路，某内部平台适合承接权限和审计，这些结论比“谁更好”更有生命力。

复审时要检查每个对标项是否服务本书主线。与平台责任、语义层、工具治理、Trace、Eval 无关的功能比较，可以删减；能帮助读者做工程取舍的差异，应保留并补充理由。这样第37章才不会像产品清单，而能成为 DataAgent 平台路线的收束章节。

## 本章小结

DataAgent 生态可以从入口形态、技术路线、部署方式和组织治理四个维度观察。Vanna、WrenAI、DB-GPT、Defog、Sherlock 等项目各有长处，但更适合作为 Registry 中的组件或参考实现，而不是直接替代企业平台。ChatBI 可以作为 DataAgent 的早期子集存在，BI Copilot 也可以并行服务报表开发，但指标口径必须回到 `infra/semantic_layer/` 统一。

选型时要看架构边界、语义层接入、Eval、HITL 和 Trace，不能只看 NL2SQL 演示是否顺滑。采购或自研的底线是 tenant 注入、只读执行、`metric_id@version` 审计和可复现 Run。生态对标的价值，也在于帮助团队发现真实业务链路里的缺口，而不是把产品清单写成能力覆盖表。


## 参考文献

Liu, X., et al. (2025). NL2SQL survey. *IEEE TKDE*. [https://doi.org/10.1109/TKDE.2025.3592032](https://doi.org/10.1109/TKDE.2025.3592032)

Tang, Z., et al. (2025). LLM/Agent-as-Data-Analyst: A survey. arXiv:2509.23988. [https://arxiv.org/abs/2509.23988](https://arxiv.org/abs/2509.23988)

Lei, F., et al. (2024). Spider 2.0. *ICLR 2025*. arXiv:2411.07763. [https://arxiv.org/abs/2411.07763](https://arxiv.org/abs/2411.07763)

Huo, N., et al. (2026). BIRD-INTERACT. *ICLR 2026*. arXiv:2510.05318. [https://arxiv.org/abs/2510.05318](https://arxiv.org/abs/2510.05318)

eosphoros-ai. (2024). *DB-GPT*. GitHub. [https://github.com/eosphoros-ai/DB-GPT](https://github.com/eosphoros-ai/DB-GPT)

Canner. (2024). *WrenAI*. GitHub. [https://github.com/Canner/WrenAI](https://github.com/Canner/WrenAI)

vanna-ai. (2024). *Vanna*. GitHub. [https://github.com/vanna-ai/vanna](https://github.com/vanna-ai/vanna)

Defog.ai. (2024). *Defog*. [https://github.com/defog-ai/defog](https://github.com/defog-ai/defog)

Microsoft. (2024). *Copilot in Power BI*. [https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)

Cube. (2025). Semantic layer docs. [https://cube.dev/docs/product/introduction](https://cube.dev/docs/product/introduction)
