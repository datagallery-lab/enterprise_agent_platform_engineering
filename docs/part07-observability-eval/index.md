# Part VII 可观测性、评估与成本

## 本部分目标

本部分回答一个企业级 Agent 平台从“能跑”走向“可运营”的关键问题：如何知道 Agent 为什么成功、为什么失败、线上质量是否变好、成本是否可控、系统是否能承受真实业务流量。

可观测性、评测、成本治理与 SLO 不是上线后的附属功能，而是 Agent 平台的生产化底座。没有 trace，就无法复盘一次多步任务；没有评测，就无法判断模型、提示词、工具和数据的变化是否带来退化；没有成本与韧性治理，Agent 很容易在长任务、高并发和不确定推理中失控。

## 本部分章节

- [Ch.38 Agent 可观测性与运行诊断](ch38-trace.md)
  - Agent 运行时观测模型
  - Trace 数据结构与生命周期
  - 全链路日志、指标与链路追踪
  - 会话回放与执行过程还原
  - 失败归因与根因分析
  - AgentOps 质量闭环实践
- [Ch.39 企业级 DataAgent 评测体系设计与 Benchmark 构建](ch39-dataagent-eval-benchmark.md)
  - DataAgent 能力边界与评测维度
  - Benchmark 任务空间设计
  - 企业数据分析场景抽象
  - QA 与任务集自动生成
  - Ground Truth 与标注体系构建
  - 结果评测、过程评测与语义评测
  - 主流 DataAgent Benchmark 对比分析
  - 企业级持续评测平台建设
- [Ch.40 在线评测、LLM-as-Judge 与持续优化](ch40-llm-as-judge.md)
  - 线上反馈信号采集
  - 用户行为与业务指标建模
  - LLM-as-Judge 评测框架
  - 评测偏差与一致性控制
  - A/B 实验与能力验证
  - 评测驱动的持续优化闭环
- [Ch.41 成本治理与缓存优化](ch41-cost-governance-cache.md)
  - Agent 成本结构分析
  - 模型路由与动态选型
  - Prompt Cache 与 Prefix Cache
  - Semantic Cache 与结果复用
  - Token 成本核算与预算控制
  - 性能、成本与质量平衡策略
- [Ch.42 SLO 管理、限流与系统韧性](ch42-slo.md)
  - Agent 服务等级目标设计
  - 延迟、成功率与质量指标
  - 限流、熔断与降级策略
  - 长任务可靠执行机制
  - 容量规划与弹性伸缩
  - 企业级 Agent 平台稳定性建设

## 推荐阅读路径

- **平台负责人 / CTO**：重点读 Ch.38 的观测闭环、Ch.39-40 的评测体系、Ch.41-42 的成本与 SLO 取舍。
- **架构师**：全读本部分，重点关注 trace 数据模型、评测平台架构、在线实验、缓存层次和稳定性策略。
- **工程师**：全读本部分，并结合 `mini-platform/core/observability/`、`mini-platform/core/eval/`、`mini-platform/core/gateway/` 做 L3 实现。
- **数据智能团队**：重点读 Ch.39-40，建立 DataAgent 的离线 benchmark、线上反馈和持续回归机制。
