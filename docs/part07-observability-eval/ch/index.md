# Part VII 可观测性、评估与成本

## 本部分目标

本部分回答一个企业级 Agent 平台从“能跑”走向“可运营”的关键问题：如何知道 Agent 为什么成功、为什么失败、线上质量是否变好、成本是否可控、系统是否能承受真实业务流量。

可观测性、评测、成本治理与 SLO 属于 Agent 平台的生产化底座。没有 trace，就无法复盘一次多步任务；没有评测，就无法判断模型、提示词、工具和数据的变化是否带来退化；没有成本与韧性治理，Agent 很容易在长任务、高并发和不确定推理中失控。

## 本部分章节

| 章 | 主题 | 读完应能回答的问题 |
|---|---|---|
| [第38章 Agent 可观测性与运行诊断](ch38-trace.md) | Trace、日志、指标、会话回放 | 一次 Run 为什么成功或失败，平台怎样复盘工具调用、状态迁移和产物 |
| [第39章 企业级 DataAgent 评测体系设计与 Benchmark 构建](ch39-dataagent-eval-benchmark.md) | 任务空间、Ground Truth、轨迹评测 | DataAgent 的能力边界怎样被样本、断言和 trace graph 评估出来 |
| [第40章 在线评测、LLM-as-Judge 与持续优化](ch40-llm-as-judge.md) | 线上反馈、Judge、A/B 实验 | 线上质量信号怎样进入评测集和回归流程 |
| [第41章 成本治理与缓存优化](ch41-cost-governance-cache.md) | 成本归因、路由、缓存、预算 | Agent 成本怎样拆解到模型、上下文、重试、工具和评测环节 |
| [第42章 SLO 管理、限流与系统韧性](ch42-slo.md) | SLO、限流、熔断、容量规划 | 不同类型 Agent 应怎样定义可靠性目标和降级策略 |

## 推荐阅读路径

平台负责人和 CTO 应重点关注第38章至第42章之间的取舍关系：观测能否定位问题，评测能否发现退化，成本和 SLO 是否能支撑真实流量。架构师建议完整阅读本部分，重点看 trace 数据模型、评测平台、在线实验、缓存层次和稳定性策略。工程师可以结合 `mini-platform/core/observability/`、`mini-platform/core/eval/` 和 `mini-platform/core/gateway/` 做实现对照。数据智能团队应重点读第39章和第40章，建立 DataAgent 的离线 benchmark、线上反馈和持续回归机制。
