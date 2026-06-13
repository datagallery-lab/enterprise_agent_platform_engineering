# Ch.39 企业级 DataAgent 评测体系设计与 Benchmark 构建

> **本章目标**：读者学完能为企业 DataAgent 设计一套覆盖能力边界、任务空间、Ground Truth、语义评测、轨迹评测和持续回归的评测体系，并能判断公开 benchmark 与企业内部 benchmark 的差异。
> **关键议题**：评测范式演进；DataAgent 能力边界；Benchmark 任务空间设计；Ground Truth 与评分口径；结果评测、语义评测与轨迹评测；轨迹半标准化与 source graph；公开 benchmark 对比；持续评测平台建设
> **前置阅读**：[Ch.32 DataAgent 产品形态](../part06-dataagent/ch32-dataagent.md)、[Ch.33 语义层工程](../part06-dataagent/ch33.md)、[Ch.34 NL2SQL 工程化](../part06-dataagent/ch34-nl2sql.md)、[Ch.38 Agent 可观测性与运行诊断](ch38-trace.md)
> **估计阅读**：L1 20 min / L1+L2 60 min / 全章 120 min
> **mini-platform 关联**：`core/eval/`、`core/observability/`、`infra/semantic_layer/`、`core/runtime/`
> **实战项目**：`projects/09-dataagent-eval/`、`projects/15-ragas-spider-eval/`
> **分层阅读**：
> L1 概念层（CTO / 安全合规 / 跨职能读者）建议读 1、2、7 与本章小结，重点理解 DataAgent benchmark 的边界、误区和公开评测的适用范围。
> L2 架构层（架构师 / 平台负责人）建议读 3、4、5、6、8，重点理解任务空间、评测对象、轨迹标准化和持续评测平台。
> L3 工程层（工程师 / 应用开发者）建议读 5、6、8、上线检查清单与实战项目，重点落到评分脚本、`eval_trace`、版本绑定和发布门禁。

---

## 1. 什么是 Benchmark，以及它如何演进到企业 DataAgent

Benchmark 直译是“基准测试”，但在 AI 系统里，它不只是一个题库。一个合格的 benchmark 至少包含四件事：明确的任务定义、可复现的数据集、统一的评测流程和可解释的指标。换句话说，它要回答“测什么、用什么测、怎么测、分数怎么解释”。如果只有一批问题和答案，却没有任务边界、数据版本、评测脚本和指标口径，那更像练习题，不是工程上可用于回归和上线决策的 benchmark。

在传统机器学习和早期 NLP（Natural Language Processing，自然语言处理）阶段，benchmark 多用于单点能力评测。例如分类任务看准确率，机器翻译看 BLEU（Bilingual Evaluation Understudy，一种用词语重合度衡量译文接近参考译文的指标），阅读理解看 EM（Exact Match，答案完全匹配率）和 F1（同时考虑答案词语命中率和覆盖率的指标），检索任务看 Recall（召回率，相关内容被找回的比例）、MRR（Mean Reciprocal Rank，正确结果排得越靠前分数越高）和 NDCG（Normalized Discounted Cumulative Gain，衡量排序结果质量的指标）。这些 benchmark 的共同特点是输入输出相对固定，评测流程容易复现。它们适合比较模型基础能力，但很难回答“模型能不能完成一个真实业务任务”。

LLM 出现后，benchmark 开始覆盖更广的通用能力。MMLU [1]、BIG-Bench [2]、HELM [3]、C-Eval [4]、CMMLU [5] 等代表性评测，把知识、推理、数学、代码、常识、安全等能力放进统一框架里。这个阶段解决了一个重要问题：同一个模型不能只在单一任务上看起来强，而要在多种能力上接受横向比较。但它仍然主要评估“模型本身”，而不是一个带工具、带数据、带权限、带运行轨迹的 Agent 系统。

很快，评测又向 Agent benchmark 延伸。SWE-bench [6] 是最有代表性的例子之一：它从真实 GitHub issue 出发，要求系统理解代码仓库、定位缺陷、修改文件并通过测试，因此比“写一道算法题”更接近开发者 Agent 的真实工作流。它的影响不只在代码领域，也在于把评测对象从“回答是否正确”推进到“能否在可执行环境中完成一个多步任务”。同类思路还包括 AgentBench [7] 对多环境工具使用的评测，WebArena [8] 对浏览器和网页任务的评测，OSWorld [9] 对桌面操作系统任务的评测。这些 benchmark 共同把问题从模型静态能力，推向了环境交互、工具调用、状态管理和结果可验证。

当 LLM 被用于数据分析，评测进一步演化到 Text-to-SQL。WikiSQL [10]、Spider [11] 等 benchmark 把自然语言问题、数据库 schema 和 SQL 生成连接起来。Spider [11] 的重要意义在于跨数据库泛化：模型不能只记住一套表结构，而要理解新的 schema。BIRD [12]、Spider 2.0 [13] 又把任务推向更真实的数据分析环境：数据库更大，schema 更复杂，执行结果更重要，模型要面对更接近生产的数据连接和查询难度。

但是，企业 DataAgent 不是单纯的 Text-to-SQL 模型。它面对的是私有数仓、语义层、BI 资产、权限策略、历史对话、工具调用和产物交付。用户问“本月经营性现金流为什么下降”，真正要评的不只是 SQL 是否生成正确，还包括指标口径是否理解、数据源是否选对、工具执行是否成功、分析结论是否可复核、图表和报告是否合规，以及整个过程是否能通过 trace 回放。

这也解释了 Deep Research benchmark 为什么会出现。DeepResearch Bench [14]、ResearchRubrics [15] 等强调多轮检索、证据整合、报告质量和引用可信度，补上了开放式研究任务的评测维度。这些工作共同说明：复杂 Agent 的质量不只藏在最终文本里，也藏在研究路径、证据使用、上下文整合和工具调用里。

最近值得企业 DataAgent 特别关注的两类 benchmark，一类是 BEAVER [16]，另一类是 Workspace-Bench [17]。BEAVER [16] 把 Text-to-SQL 拉回企业环境，关注私有企业数据仓库、真实查询日志、复杂 schema、领域知识和可诊断子任务。Workspace-Bench 1.0 [17] 则关注 Agent 在真实工作区中的文件依赖、跨文件检索、上下文推理和多步执行。它不是 DataAgent benchmark，但它提醒我们：企业 Agent 面对的常常不是孤立问题，而是有历史版本、隐式依赖和执行轨迹的工作空间。

所以，本章讨论的“企业级 DataAgent benchmark”不是公开排行榜意义上的分数游戏，而是一套生产质量系统。它吸收 LLM benchmark 的标准化思想，继承 Text-to-SQL benchmark 的执行评测，借鉴 Agent benchmark 的工具和环境交互评测，再结合 Ch.38 的 trace 回放，把结果、语义、轨迹、安全和持续回归放在同一个框架里。

![图 39-1 从 LLM Benchmark 到企业 DataAgent Benchmark 的演进时间线](image/ch39-1.png)

这条时间线的结论很直接：企业 DataAgent benchmark 应该吸收公开 benchmark 的方法，但最终必须回到自己的生产问题。它要像一张能力地图，而不是一根只显示总分的温度计。地图必须告诉团队系统在哪些任务上可靠、在哪些约束下会失真、在哪些路径上虽然能答对但无法审计。

## 2. 为什么 DataAgent 不能只测最终答案

DataAgent 的输出看起来是一句话、一个 SQL、一张图表或一份报告，但真实能力并不只发生在最后一步。一次企业数据分析任务通常要经历：理解业务问题、识别指标口径、定位表和字段、生成查询、执行与纠错、分析结果、选择图表、组织解释、处理权限和不确定性。最终答案正确，只能说明这条链路在这一次样本上走通；最终答案错误，也不一定说明模型本身不行，可能是上下文包漏了约束，语义层缺字段说明，工具返回超时，或者权限策略没有把拒绝原因讲清楚。

企业评测要同时关注“结果”“语义上下文”和“轨迹路径”。结果评测回答最后交付物是否正确；语义上下文评测回答模型拿到的指标口径、schema、source、Memory 和 policy 是否正确；轨迹评测回答系统是否通过可接受、可审计、可复现的动作链路得到结果。三者缺一不可：只看结果，会放过碰巧答对、越权取数、过度依赖旧记忆的风险；只看轨迹，又可能把合理的多解任务误判成失败。成熟的 DataAgent 评测应该承认“一题多解”，允许不同 Agent 采用搜索整合、代码验证、SQL 执行、图表复核等不同路线，只要最终结果成立，且关键证据、权限和推理路径能够被审计。

在给任务执行情况打分时，应先用确定性评测方法（脚本执行等）处理可以确定给分的维度，再进入模型裁判或专家评审。SQL 是否执行、数值是否一致、文件 diff 是否符合预期、API 状态是否正确，都应该由确定性程序判断；报告深度、解释完整性、引用可信度这类开放指标，可以使用 LLM-as-a-Judge；高风险样本、争议样本和上线门禁样本，则需要人工抽检或专家复核。

可以用一个简化公式概括企业 DataAgent 的综合评测思想：

$$
Score_{\text{agent}} = Score_{\text{quality}} - w_{\text{cost}} \cdot CostPenalty
$$

其中质量分由结果、语义上下文、轨迹和安全四部分组成：

$$
Score_{\text{quality}} =
w_{\text{result}} \cdot Score_{\text{result}}
+ w_{\text{semantic}} \cdot Score_{\text{semantic}}
+ w_{\text{trajectory}} \cdot Score_{\text{trajectory}}
+ w_{\text{safety}} \cdot Score_{\text{safety}}
$$

这里的权重不是固定常数，而应该由任务类型决定。财务报表生成更重视安全、口径和可复核；临时探索分析可以适当容忍格式不完美；权限敏感任务则应把“安全分”设为门禁项，只要越权就直接失败。

![图 39-2 DataAgent 评测对象分层图](image/ch39-2.png)

## 3. DataAgent 的能力边界与指标设计

设计 benchmark 前要先定义能力边界。否则题库很容易变成“SQL 考试”：模型只要把自然语言翻译成 SQL 就算完成，实际却漏掉企业分析最难的部分。

企业 DataAgent 的能力边界，首先不在“模型是否聪明”，而在系统是否能把任务所需的上下文、工具和反馈通道提供给模型。大模型只是决策内核，它不天然知道企业指标口径、数据版本、API 参数、权限边界和历史会话状态。Agent Runtime 必须先把这些信息整理成足够清晰的 Context Package，再让模型做规划；模型也必须把自己的下一步意图、需要的证据、工具选择、不确定性和校验结论反馈给 Agent。评测要看的，正是这个闭环有没有成立。

用户说“本月现金流为什么下降”，系统不能只把这句话交给模型。它至少要提供可用的指标字典、语义层版本、相关表和字段、时间口径、权限策略、历史对话摘要、数据新鲜度和可能的对比基线。如果问题里的“现金流”存在多个口径，正确行为不是先猜一个口径去算，而是先读取口径定义或向用户澄清。这里测的不是模型能不能蒙中答案，而是 Agent 是否把完成任务所需的上下文准备充分。

工具和 API 也不是简单挂在系统里就算可用。模型需要知道有哪些工具、每个工具适合什么场景、参数 schema 是什么、权限要求是什么、返回结构是什么、常见错误如何处理。计算类任务尤其不能依赖模型心算或凭文本推理完成。比如现金流归因应调用 SQL、Python、OLAP 或指标服务计算；汇率、库存、支付状态这类动态数据应走对应 API；图表和报表应由产物工具生成并保存引用。大模型可以负责选择工具、解释结果和组织报告，但关键计算应交给可复核的执行器。

上下文和工具准备好之后，还要看 Agent 是否沿着可审计的动作链路执行。这里的“链路”不是要求暴露模型内部隐式思维，而是要求 trace 中能看到外显动作：确认任务目标，确认指标口径，选择权威数据源，生成或调用计算方案，执行工具，校验返回结果，再生成解释和产物。反过来，如果系统每次都沿用上一轮 SQL、默认使用某张老报表，或者在缺少口径时直接输出结论，即使这次碰巧答对，也说明它形成了路径依赖，不具备可靠的企业分析能力。

反馈回路同样重要。模型向 Agent 返回的内容不应只有最终答案，还应包括结构化的下一步动作、工具参数、需要补充的证据、错误解释和是否需要澄清。Agent 执行工具后，也要把工具结果、错误码、空结果、权限拒绝和产物引用反馈给模型，让模型基于真实 observation 继续判断。评测时要检查这条回路是否闭合：模型是否提出了合理动作，Agent 是否真的执行，工具结果是否回灌，模型是否基于结果修正，而不是继续沿着旧假设输出。

能力边界最终要被翻译成可修复信号。Benchmark 不应该只告诉团队“这个 case 错了”，还要指出下次应该怎么做才对。例如失败标签如果是 `metric_definition_missing`，修复方向可能是补指标字典、改 Context Builder 或要求先查口径；如果是 `tool_affordance_missing`，修复方向可能是补工具描述、参数示例和返回契约；如果是 `llm_ignored_observation`，修复方向可能是改 Planner prompt、增加状态机约束，或把失败样本转成训练数据。评测结果只有能反哺 Agent 设计、工具注册、语义层建设和 LLM 训练，才真正有工程价值。

有了这条闭环，评分设计才有落点。结果维度可以用执行结果、数值容差和断言命中衡量；语义上下文维度可以检查指标口径、schema、source、Memory 和 policy 是否被正确提供；轨迹维度则依赖半结构化 trace、动作序列检查和 source graph。这样的指标不会停留在抽象名词上，而能直接落到评测脚本、Judge prompt、trace adapter 和失败标签。

## 4. Benchmark 不是题库堆砌，而是任务空间设计

企业 benchmark 的价值不在于题目数量最大，而在于覆盖真实任务分布和关键风险。一个 500 条高质量、可回放、可归因、版本冻结的企业 benchmark，通常比 5 万条自动生成但无业务约束的题库更有用。原因很简单：上线风险不是均匀分布的。低风险单表查询可以很多，但它们无法代表“多源冲突、指标改版、用户中途纠正、权限收敛、旧记忆失效”这些真正会让 DataAgent 失控的场景。

任务空间设计要先定义坐标系，再填样本。横向看任务意图：查询、对比、归因、预测、解释、报告。纵向看执行复杂度：单表、多表 Join、多事实表、跨域数据、历史快照、长上下文。第三个维度是企业约束：业务语义是否明确、权限是否敏感、数据源是否冲突、产物是否需要审计、用户是否可能追问或纠正。只有把这些维度交叉起来，benchmark 才能像能力地图一样展示系统边界。

从产品视角看，任务空间不只是“难度分级”，还承担着需求澄清功能。PM 关心的是哪些用户任务能稳定上线，哪些任务只能灰度，哪些任务必须有人审；开发关心的是错误能否定位到工具、语义层、模型还是权限策略；AI 研究人员关心的是模型到底缺哪类能力。一个好的 benchmark 需要同时服务这三类问题，因此它应该把样本切成不同集合：核心业务稳定集、线上失败回归集、压力集、安全集和开放式报告评审集。集合之间可以重叠，但更新节奏不应相同。

可以用覆盖率公式约束任务空间，而不是只统计样本数量：

$$
Coverage =
\frac{\sum_{d \in D} I(count(d) \ge min(d)) \cdot weight(d)}
{\sum_{d \in D} weight(d)}
$$

其中 `D` 是任务空间中的维度或分桶，比如财务归因、销售对比、多轮追问、安全拒答、报告生成。`min(d)` 表示这个分桶至少要有多少可用样本。这样可以避免 benchmark 被大量简单查询刷高数量。

更进一步，Agent 任务还要承认路径多样性。对同一个现金流下降问题，一个 Agent 可能先检索指标字典再写 SQL，另一个可能先读取财务看板再回查明细。只要二者都使用了合规数据源，解释了指标口径，执行结果可复核，最终结论被证据支持，就不应因为路径不完全相同而判负。评测的目标不是强迫所有系统按同一条脚本行动，而是判断路径是否合理、必要证据是否覆盖、危险动作是否被拦截。

因此，企业 benchmark 中的“参考路径”更适合写成约束，而不是完整脚本。例如“必须在输出前检查权限”“必须读取最新指标定义”“遇到缺槽位必须先澄清”“不得引用未进入上下文的产物”。这些约束能保留多解空间，又能阻断不可接受的捷径。对需要精确流程的任务，例如资金支付审批或监管报送，可以把路径约束收紧；对探索分析和报告草拟，则应更多使用 source graph、证据覆盖和语义断言。

![图 39-3 企业 DataAgent Benchmark 任务空间矩阵](image/ch39-3.png)

一个可落地的设计流程是从真实业务资产出发，先抽取任务意图和约束，再决定样本落在哪个分桶。以“解释本月经营性现金流下降，并按区域拆解主要贡献因素”为例，它不是单纯的自然语言问答。样本至少要记录：指标口径、时间范围、对比基线、可用数据源、可查询字段、不可暴露字段、期望产物、可接受解释、必须引用的证据以及允许的工具。只有这些信息被结构化保存，后续才能自动运行、自动判分、失败归因和版本回放。

## 5. 结果评测、语义评测与轨迹评测

DataAgent 评测可以分成三层。第一层是结果评测，它回答“最后交付物对不对”。对于 SQL 查询，可以看执行成功率、结果准确率、SQL 等价率；对于图表，可以看图表类型、轴字段、筛选条件和数据一致性；对于报告，可以看关键事实是否覆盖、结论是否被证据支持。

第二层是语义评测，也可以叫上下文评测。它回答“Agent 检索并交给模型的上下文是否正确、充分、权威”。比如是否取到了正确指标口径，是否选对 schema、表、字段和 Join 路径，是否带上了必要的历史 Memory，是否识别了过期定义，是否把权限策略和可用 API 信息放进 Context Package。语义评测关心的是模型做决策前看到的材料是否对，而不是后续动作顺序是否漂亮。

第三层是轨迹评测，它回答“Agent 后续动作链路是否适合生产”。它看的是可观察的动作序列和状态流转：是否先确认口径再计算，是否调用了合理工具而不是让模型心算，是否把工具 observation 回灌给模型，是否在权限敏感任务里先查策略再输出，是否重复检索、无界重试或形成路径依赖。轨迹评测尤其适合发现“答案碰巧正确但路径不可接受”的样本。

具体评分不应该先从一个大而全的总分公式出发，而应该先看评测对象。结果、语义上下文、开放式报告和轨迹的 Ground Truth 形态不同，适合的评分方法也不同。简单查询优先用确定性程序；开放式报告再进入 LLM Judge；语义上下文可以检查证据来源、表字段、口径和权限上下文是否命中；轨迹类能力则把原始 trace 改造成半结构化动作链路，再评估依赖关系和执行顺序。

SQL 类任务至少要分开看“能不能执行”和“结果是否一致”。前者只判断 SQL 是否成功执行，不代表答案正确；后者再比较结果表。对于顺序无关的查询，比较前要先做归一化：列名映射、类型转换、行排序、空值处理和浮点格式统一。可以把严格结果比对写成：

$$
表结果命中 =
\mathbf{1}\left[
Normalize(R_{pred}) = Normalize(R_{ref})
\right]
$$

数值类答案不能简单用字符串完全匹配。收入、比例、增长率、汇率换算和聚合指标都需要容差。一个常用写法是同时设置绝对容差和相对容差：

$$
NumHit(x, x^*) =
\mathbf{1}\left[
|x - x^*| \leq \max(\epsilon_{abs}, \epsilon_{rel}\cdot |x^*|)
\right]
$$

如果一个 case 有多个关键数值，可以对每个数值断言求加权平均：

$$
数值结果分 =
\frac{\sum_i w_i \cdot NumHit(x_i, x_i^*)}{\sum_i w_i}
$$

开放式分析和报告更适合用断言加 rubric。断言用于检查不可缺少的事实，例如“必须说明下降主要来自应收账款回款延迟”“必须按区域给出贡献度”“不得暴露客户明细名称”。Rubric 用于评价表达质量和分析质量，但不应让 Judge 随意给 0 到 100 的连续分，而应使用离散档位，给每一档写清楚锚点。比如每个维度取 `0/1/2/3/4` 分：0 表示缺失或错误，2 表示部分满足，4 表示充分满足。一个多维 Judge 分可以写成：

$$
Judge 分 =
\frac{\sum_i w_i \cdot (d_i / 4)}{\sum_i w_i},
\quad d_i \in \{0,1,2,3,4\}
$$

这里的维度可以包括：关键事实是否覆盖、是否有合理归因而非堆数、是否遵循用户任务、结论是否绑定查询结果或文档证据、引用是否可信且可追溯，以及表达是否适合目标读者。DataAgent 还要额外设置门禁项：如果执行结果不一致、指标口径错误、引用了未读取证据，或者出现越权泄漏，即使文字表达很好，也不能给高分。

语义评测要看上下文是否捞对。可以把 benchmark 标注成一组必需材料：指标定义、表结构片段、权威文档、历史记忆、权限策略或 API 说明。评测时检查 Agent 实际放入上下文包的材料是否覆盖这些必需项，同时惩罚明显无关或过期的材料。一个简单的覆盖口径是：

$$
上下文召回率 =
\frac{|S_{pred} \cap S_{ref}|}{|S_{ref}|},
\quad
上下文准确率 =
\frac{|S_{pred} \cap S_{ref}|}{|S_{pred}|}
$$

其中 `S_ref` 是完成任务必须看到的上下文集合，`S_pred` 是本次运行实际提供给模型的上下文集合。对 DataAgent 来说，语义评测还可以继续拆成几个中文口径：指标口径是否命中，表和字段是否选对，证据来源是否权威，权限上下文是否齐全，历史记忆是否新鲜。这些指标回答的是“模型有没有拿到正确材料”，不是“Agent 后续有没有按正确步骤执行”。

轨迹评测要看动作是否发生在正确位置，而不只是最终文本有没有提到。它可以由规则检查表达，例如“读取指标口径必须早于计算指标”“检查权限必须早于最终输出”“工具返回结果必须回灌给模型”。这类规则的输出最好带失败标签，例如“缺少指标定义”“工具说明不足”“模型忽略工具返回”“跳过权限检查”。这样评测报告不仅说明哪里错，还能说明下次应该补上下文、补工具描述、改 Planner 约束，还是加入训练样本。

轨迹评测还要把 Ch.38 中的原始 trace 进一步改造成 `eval_trace`：把不同 Agent 框架里的节点、消息、工具调用和产物写入统一的 `step_type`、`inputs`、`outputs`、`status`、`source_refs`。在此基础上，可以借鉴 Workspace-Bench [17] 的依赖图思想抽取 source graph：节点是 Turn、Memory、Schema、指标字典、SQL Result、BI Dashboard、Artifact；边表示 reads、generates、references、derives。这样就能判断 Agent 是否读取了必要 source，是否引用了未进入上下文的 source，是否因为路径依赖复用了旧 memory。

最后再把这些分数组合起来。组合时不应让一个总分掩盖风险：安全、权限和数据泄漏通常是门禁项；SQL 执行失败会让结果分归零；报告 Judge 分只有在关键事实和证据断言通过后才有意义。更稳妥的看板不是一列总分，而是同时展示 SQL 执行是否成功、结果表是否一致、关键数值是否命中、报告断言是否覆盖、Judge 多维分、上下文召回与准确率、轨迹规则通过率、source graph 分、安全通过率和成本延迟指标。

![图 39-4 结果评测、语义上下文评测与轨迹评测](image/ch39-4.png)

轨迹评测是企业 Agent benchmark 相比传统 DataAgent benchmark 最需要补上的部分。一个答案可能数值正确，但如果它通过越权字段、错误口径或不可复现的中间步骤得到，就不能算生产可接受。反过来，一个开放式报告和参考答案表达不同，只要核心断言命中、证据充分、路径合理，也应该被认可。

## 6. 不同 Agent 轨迹如何半标准化评测

在轨迹评测上，不同 Agent 框架的轨迹格式通常不一样：LangGraph 可能记录节点状态和边转移，AutoGen 可能记录多角色消息，OpenAI Agents SDK 可能记录 tool call 和 handoff，企业自研 Runtime 可能记录 Step、Span、Event、Artifact。即使都叫 trace，字段、粒度、命名和父子关系也可能不同。如果评测平台直接依赖某一种原始格式，benchmark 很快就会被框架锁死。

如果是在企业内部做定制化评测，可以只关注企业 Agent 的组件，通过定制化评测准确定位问题；而在通用轨迹评测上，更稳妥的做法是做“半标准化”。所谓半标准化，不是要求所有 Agent 都产生完全相同的 trace，而是在评测入口把不同轨迹归一到一组最小可比较对象：

```json
{
  "run_id": "run_fin_042",
  "trace_id": "trace_fin_042",
  "steps": [
    {
      "step_id": "s1",
      "type": "context_pack",
      "inputs": ["turn_001", "summary_003", "schema_finance_v12"],
      "outputs": ["ctxpkg_042"]
    },
    {
      "step_id": "s2",
      "type": "tool_call",
      "tool": "sql_executor",
      "inputs": ["ctxpkg_042", "schema_finance_v12"],
      "outputs": ["sql_result_042"],
      "status": "succeeded"
    },
    {
      "step_id": "s3",
      "type": "artifact_write",
      "inputs": ["sql_result_042"],
      "outputs": ["chart_042", "summary_042"]
    }
  ],
  "sources": [
    {"source_id": "schema_finance_v12", "kind": "schema"},
    {"source_id": "sql_result_042", "kind": "tool_result"},
    {"source_id": "chart_042", "kind": "artifact"}
  ]
}
```

这个格式只保留评测需要的公共骨架：步骤、类型、输入、输出、状态、工具、产物和 source 引用。原始 trace 仍然可以保留在 Ch.38 的观测存储里；评测平台读取的是归一化后的 `eval_trace`。

半标准化以后，可以从轨迹中抽取一个 source graph，也就是“这次答案到底依赖了哪些来源”。这点可以借鉴 Workspace-Bench [17] 的思路。Workspace-Bench [17] 关注工作区中文件之间的依赖关系：任务答案往往不是来自单个文件，而是来自多个文件、目录、历史版本和跨文件线索。DataAgent 里也有类似结构，只是 source 不一定是文件，而可能是原始 Turn、Context Summary、Memory、Schema、SQL、查询结果、BI 看板、指标字典、Artifact 和权限策略。

可以把一次 Run 抽象成有向图：

$$
G_{trace} = (V, E)
$$

其中 `V` 是轨迹中的 source 和 step，`E` 表示“读取、生成、引用、派生”的关系。比如 `schema_finance_v12 -> sql_generation` 表示 SQL 生成读取了财务 schema，`sql_result_042 -> chart_042` 表示图表由查询结果生成，`turn_001 -> ctxpkg_042` 表示用户原始问题进入了本次上下文包。

如果 benchmark 有参考轨迹图 `G_ref`，可以用一个简化的图覆盖率评估 source 依赖是否合理：

$$
SourceGraphScore =
\eta_v \cdot \frac{|V_{pred} \cap V_{ref}|}{|V_{ref}|}
+ \eta_e \cdot \frac{|E_{pred} \cap E_{ref}|}{|E_{ref}|}
- \eta_n \cdot Noise(G_{pred})
$$

这里 `V_pred` 和 `E_pred` 来自 Agent 的实际轨迹，`V_ref` 和 `E_ref` 来自标注或参考执行。`Noise(G_pred)` 用来惩罚明显无关的 source，例如为回答现金流问题读取了无关的人事表、重复检索无关文件、把未进入上下文的 Artifact 当作证据引用。

这种评测比“最终答案对不对”更有诊断价值。假设两个 Agent 都答对了现金流下降原因，但 A 的轨迹引用了正确指标字典、财务 schema 和 SQL 结果，B 的轨迹没有读取指标口径，只是根据字段名猜测。结果分可能相同，source graph 分应该不同。反过来，如果答案错了，source graph 能帮助定位是缺少了关键 source，还是读了 source 但没有正确使用。

半标准化轨迹还可以支持跨 Agent 对比。不同 Agent 的原始日志可能完全不同，但只要都能映射到 `context_pack`、`model_call`、`tool_call`、`artifact_write`、`policy_check`、`memory_read`、`memory_write` 等公共 step 类型，就可以比较关键 source 覆盖率、无关 source 比例、工具调用冗余、失败恢复路径、权限检查是否发生、产物是否可追溯。

需要注意，企业内部不一定能为每个样本标注完整参考轨迹图。可以分三档做：核心 Golden Set 标注完整 `G_ref`；普通 Regression Set 只标注关键 source 和禁止 source；线上失败样本先自动抽图，再由专家在复盘时补充关键边。这样既能借鉴 Workspace-Bench [17] 的依赖图思想，又不会把标注成本推到不可执行。

## 7. 公开 Benchmark 能告诉我们什么，不能告诉我们什么

公开 benchmark 的价值在于提供横向比较和方法论参考，但企业不能直接把公开分数当作上线依据。


| Benchmark 类型   | 代表                                 | 能评什么                        | 企业缺口                                |
| -------------- | ---------------------------------- | --------------------------- | ----------------------------------- |
| 经典 Text-to-SQL | WikiSQL [10]、Spider [11]                     | 基础 SQL 生成、跨 schema 泛化       | 企业表结构、隐式口径、权限、日志来源不足。               |
| 大规模数据分析 SQL    | BIRD [12]、Spider 2.0 [13]                    | 更复杂 schema、执行准确率、真实数据库连接    | 仍难覆盖私有数据仓库和企业语义层。                   |
| 企业 Text-to-SQL | BEAVER [16]                             | 私有企业数仓、复杂 schema、领域知识、子任务诊断 | 对多轮分析、产物生成和完整 Agent 轨迹覆盖有限。         |
| Deep Research  | DeepResearch Bench [14]、ResearchRubrics [15] | 多步检索、证据整合、报告质量、引用可信度        | 偏开放研究任务，不等同于企业数据分析。                 |
| 工作区任务          | Workspace-Bench 1.0 [17]                | 大规模文件依赖、跨文件检索、上下文推理、多步任务    | 更偏文件工作区，不直接评 SQL 和语义层，但适合借鉴轨迹与依赖评测。 |
| 通用 Agent       | AgentBench [7]、WebArena [8]、OSWorld [9]        | 工具使用、环境交互、长链路执行             | 企业数据、权限、指标口径和产物审计不足。                |


BEAVER [16] 特别值得企业 DataAgent 团队关注。相比 Spider [11] 这类公开数据库 benchmark，它的启发不是“拿 BEAVER 分数替代内部评测”，而是告诉我们：企业 SQL 的难点不只在模型生成 SQL，而在复杂 schema、隐式领域知识和多子任务组合。

Workspace-Bench 1.0 [17] 也值得关注。它评测 Agent 在真实工作区中处理大规模文件依赖的能力，包含多种工作者画像、大量文件类型、文件依赖图和多步任务。它与 DataAgent 的任务表面不同，但方法论很相似：企业 Agent 面对的不是孤立输入，而是带历史版本、隐式依赖、跨文件证据和多步执行的工作环境。对 DataAgent 来说，这对应 BI 看板、历史报表、SQL 文件、指标字典、数据血缘和用户对话之间的依赖关系。

Deep Research benchmark 的启发在于评测开放式产出。RACE、FACT、多维 rubric 等方法来自 DeepResearch Bench [14] 这类研究报告评测设计，可以迁移到 DataAgent 的报告评测：不仅看报告是否“写得好”，还要看全面性、深度、指令遵循、可读性、事实丰度和引用可信度。区别是 DataAgent 还要额外绑定数据执行结果、指标口径和权限边界。

结论是：公开 benchmark 用来校准方法，内部 benchmark 用来决定上线。企业最终要评的是自己的表、自己的指标、自己的权限、自己的用户任务和自己的运行轨迹。

## 8. 企业级持续评测平台建设

Benchmark 不是一次性项目，而是一套持续运行的平台。每次模型、Prompt、工具、语义层、权限策略、数据版本变化，都可能让 DataAgent 的行为发生变化。持续评测平台要把这些变化纳入回归。

可以先看长期维护的公开 leaderboard。Spider [11] 的公开页长期保留数据切分、评测脚本、提交记录和榜单，并在后续把注意力引向更真实的 Spider 2.0 [13]；BIRD [12] 以执行准确率、数据规模、专业领域和持续更新的提交记录，展示了 Text-to-SQL 榜单如何跟随研究范式演进；HELM [3] 和 MTEB [18] 的价值在于把多任务、多指标和模型元数据放在同一套评测协议下；SWE-bench [6] 则说明，真实工程任务需要同时维护数据集、执行环境、提交入口、verified/lite/full 等不同轨道和可追溯排行榜。这些例子不等同于企业 DataAgent 评测，但它们都在证明一件事：榜单之所以能长期有效，不是因为有一个神奇总分，而是因为协议稳定、提交可复现、数据版本清楚、结果可追溯。

但公开榜单也有边界。Spider [11] 和 BIRD [12] 适合比较 Text-to-SQL 能力，却不知道企业内部的语义层版本、权限策略、BI 看板、历史 trace 和用户反馈。企业持续评测平台要借鉴它们的“固定协议 + 统一执行 + 可追溯榜单”，但评测对象要换成自己的生产系统。也就是说，企业内部也应该有一个私有 leaderboard：每个模型版本、Prompt 版本、工具版本、语义层版本都要在同一批 Golden Set、Regression Set、Safety Set 上留下可追溯结果。

企业级产品的做法会更接近“评测控制塔”。它不会只提供一个离线分数，而是把数据集管理、实验运行、Judge、线上监控、回归门禁、风险告警和审计记录连在一起。放到 DataAgent 平台里，对应的能力就是：从线上 trace 和用户反馈自动沉淀样本；在私有数据快照上重放 Agent；同时记录模型、Prompt、工具、语义层和权限版本；把结果分、语义上下文分、轨迹分、安全分和成本指标放进同一个看板；当核心指标退化或安全样本失败时，阻断发布。

持续评测平台还可以多做一步：不只是保存失败样本，还要把失败轨迹转成可复用资产。比如一次现金流分析失败，不只记录“答案错了”，还要保存当时的 Context Package、source graph、错误 SQL、修复后的 SQL、专家解释和最终正确报告。下一次类似任务回归时，这个 Case 既是评测样本，也是改进 Planner、工具描述和语义层的训练材料。

平台需要有样本库、执行器、Judge、Trace 采集、指标看板、回归门禁和样本沉淀。样本库管理 benchmark 版本、难度、任务类型、来源和标签；执行器调用 Agent Runtime，并固定模型、Prompt、工具、数据和权限版本；Judge 运行规则评测、执行评测、LLM-as-a-Judge 和人工评审；Trace 采集保存每次评测 Run 的 Context Package、Step、Tool Call、Artifact 和成本；指标看板展示准确率、语义上下文指标、安全指标、成本和延迟；回归门禁在 CI/CD、Prompt 发布、模型路由、语义层发布前阻断明显退化；样本沉淀则把线上失败、用户反馈和事故复盘转成新的回归样本。

持续评测的关键是版本绑定：

```text
eval_run_id
  benchmark_version
  model_version
  prompt_version
  tool_version
  semantic_layer_version
  policy_version
  data_snapshot_version
  runtime_version
  trace_id
```

没有这些版本，回归分数无法解释。比如准确率下降，到底是模型变了、Prompt 变了、语义层字段描述变了，还是数据快照变了？持续评测平台必须能回答。

一个推荐闭环是：线上 DataAgent 每次运行都写入 Trace 和用户反馈；失败、点踩、高成本、人工接管样本进入候选池；评测团队按任务类型和失败类型聚类；高价值样本补充 Ground Truth、语义上下文标签和轨迹标签；样本进入 Regression Set 或 Safety Set；团队修复 Context、工具描述、语义层、模型路由或权限策略；回归通过后灰度上线；Ch.40 的在线评测继续观察真实用户分布。

举一个内部榜单例子。假设团队同时维护 `gpt-4.1 + prompt:v12`、`gpt-5-mini + prompt:v3` 和一个本地模型路由方案。每晚评测平台在同一份 `benchmark:v2026_06` 上运行三套配置，生成一张私有榜单：结果准确率、表字段匹配分、source graph 分、安全通过率、P95 延迟、平均 token 成本。如果新方案结果分高 2%，但 Safety Set 有越权失败，发布门禁应直接失败；如果结果分持平但成本下降 40%，可以进入灰度；如果 Regression Set 中现金流场景下降，就把失败 trace 加入复盘队列，而不是只看总分。

评测平台也要控制成本。不是所有样本都要每天全量跑。小改动先跑 Smoke Eval，模型或语义层发布跑 Regression Eval，权限策略变更必须跑 Safety Eval，每天固定跑 Nightly Eval，重大版本上线前再跑全量 Release Eval。这样做的目标不是追求一个漂亮总分，而是让每次系统变化都有可解释、可回放、可修复的质量信号。

---

## 本章小结

DataAgent 评测已经从静态结果评测，演进到结果、语义上下文、轨迹、安全和持续回归并重。最终答案仍然重要，但它只是第一层证据；真正决定系统能否进入生产的，是答案背后的指标口径、上下文 source、工具调用、权限检查、状态更新和产物可追溯性。企业评测体系应优先使用可执行校验和规则校验，再用 LLM-as-a-Judge 或人工专家处理开放式报告与复杂解释。

企业 benchmark 的价值在于刻画能力边界，而不是制造题目数量。任务空间要覆盖真实业务约束：指标口径、跨源冲突、定义改版、旧记忆失效、用户纠正、权限限制和多产物交付。一个好的 benchmark 不会强行规定所有 Agent 走同一条路径，而是判断路径是否合理、关键证据是否覆盖、危险动作是否被拦截。

持续评测平台则把 benchmark 变成日常质量基础设施。它要绑定模型、Prompt、工具、语义层、权限策略、数据快照、Runtime 和 trace 版本，把线上失败沉淀为回归样本，把每次发布都放到私有 leaderboard 上比较。公开 leaderboard 可以提供协议设计的参照，但企业上线判断必须回到自己的数据、自己的权限、自己的用户任务和自己的运行轨迹。

### 上线检查清单

- 是否为 DataAgent 定义了能力边界和分层评测指标？
- 是否有覆盖核心业务场景、难度分级和版本管理的 benchmark？
- 是否把结果评测、语义上下文评测和轨迹评测分开统计？
- 是否把不同 Agent 的原始轨迹归一成可比较的 `eval_trace`？
- 是否能从轨迹中抽取 source graph，并检查关键 source 覆盖和无关 source 噪声？
- 是否为 SQL、图表、报告、安全拒答等不同产物设计了不同 Ground Truth？
- 每次模型、Prompt、工具或语义层变更是否触发回归评测？
- 线上失败样本是否能从 Trace 沉淀到 Regression Set？
- 评测结果是否能定位到 Prompt、模型、工具、语义层、权限或数据版本？

### 参考文献与延伸阅读

相关章节：[Ch.33 语义层工程](../part06-dataagent/ch33.md)、[Ch.34 NL2SQL 工程化](../part06-dataagent/ch34-nl2sql.md)、[Ch.38 Agent 可观测性与运行诊断](ch38-trace.md)、[Ch.40 在线评测、LLM-as-Judge 与持续优化](ch40-llm-as-judge.md)。

本章公开 benchmark 的参考文献按正文首次出现顺序排列。

[1] Hendrycks, D. et al. [*Measuring Massive Multitask Language Understanding*](https://arxiv.org/abs/2009.03300). ICLR, 2021.

[2] Srivastava, A. et al. [*Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models*](https://arxiv.org/abs/2206.04615). TMLR, 2023.

[3] Liang, P. et al. [*Holistic Evaluation of Language Models*](https://arxiv.org/abs/2211.09110). TMLR, 2023.

[4] Huang, Y. et al. [*C-Eval: A Multi-Level Multi-Discipline Chinese Evaluation Suite for Foundation Models*](https://arxiv.org/abs/2305.08322). arXiv, 2023.

[5] Li, H. et al. [*CMMLU: Measuring Massive Multitask Language Understanding in Chinese*](https://arxiv.org/abs/2306.09212). arXiv, 2023.

[6] Jimenez, C. E. et al. [*SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*](https://arxiv.org/abs/2310.06770). ICLR, 2024.

[7] Liu, X. et al. [*AgentBench: Evaluating LLMs as Agents*](https://arxiv.org/abs/2308.03688). ICLR, 2024.

[8] Zhou, S. et al. [*WebArena: A Realistic Web Environment for Building Autonomous Agents*](https://arxiv.org/abs/2307.13854). ICLR, 2024.

[9] Xie, T. et al. [*OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments*](https://arxiv.org/abs/2404.07972). arXiv, 2024.

[10] Zhong, V., Xiong, C., & Socher, R. [*Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning*](https://arxiv.org/abs/1709.00103). arXiv, 2017.

[11] Yu, T. et al. [*Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task*](https://arxiv.org/abs/1809.08887). EMNLP, 2018.

[12] Li, J. et al. [*Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs*](https://arxiv.org/abs/2305.03111). NeurIPS Datasets and Benchmarks, 2023.

[13] Lei, F. et al. [*Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows*](https://arxiv.org/abs/2411.07763). arXiv, 2024.

[14] Du, M. et al. [*DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents*](https://arxiv.org/abs/2506.11763). arXiv, 2025.

[15] Sharma, T. et al. [*ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents*](https://arxiv.org/abs/2511.07685). arXiv, 2025.

[16] Chen, P. B. et al. [*BEAVER: An Enterprise Benchmark for Text-to-SQL*](https://arxiv.org/abs/2409.02038). arXiv, 2024.

[17] Tang, Z. et al. [*Workspace-Bench 1.0: Benchmarking AI Agents on Workspace Tasks with Large-Scale File Dependencies*](https://arxiv.org/abs/2605.03596). arXiv, 2026.

[18] Muennighoff, N. et al. [*MTEB: Massive Text Embedding Benchmark*](https://arxiv.org/abs/2210.07316). EACL, 2023.

长期维护的 leaderboard 可参考：[Spider](https://yale-lily.github.io/spider) [11]、[BIRD](https://bird-bench.github.io/) [12]、[BEAVER](https://beaverbench.github.io/) [16]、[HELM](https://crfm.stanford.edu/helm/) [3]、[MTEB](https://huggingface.co/spaces/mteb/leaderboard) [18]、[SWE-bench](https://www.swebench.com/) [6]。评测工具可参考 Ragas、TruLens、DeepEval、Promptfoo、OpenTelemetry、Langfuse 和 Phoenix。
