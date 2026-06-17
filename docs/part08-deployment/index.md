# Part VIII 部署与基础设施

> Part Owner：旭宏 ｜ 状态：v0.6 初稿
> 四章形成 **调度 → 服务 → 网关 → 交付** 完整链路。

## 本部分章节

| 章 | 标题 | 核心职责 |
|---|---|---|
| [Ch.43](ch43-gpu-kubernetes.md) | GPU 调度与 Kubernetes | 算力从哪来 |
| [Ch.44](ch44.md) | 模型部署 | 模型怎么跑 |
| [Ch.45](ch45-llm.md) | LLM 网关与多租户 | 请求怎么进 |
| [Ch.46](ch46-gitops-iac.md) | GitOps、IaC 与边缘推理 | 整套怎么交付 |

## 阅读建议

- **架构师**：按 Ch.43 → Ch.46 顺序完整阅读 L1+L2。
- **AI 应用开发者**：重点 Ch.44、Ch.45 的 L3 工程示例。
- **CTO / 平台负责人**：每章 L1+L2，关注 ROI、合规边界与 3 年演进。

## 与全书关系

- 上游：Part II 推理引擎（Ch.6–7）提供 Runtime 选型依据
- 下游：Part IX 前端（Ch.47）依赖网关与模型服务的稳定 API
- 交叉：Part VII 成本/SLO（Ch.41–42）、Part X 安全隔离（Ch.50）
