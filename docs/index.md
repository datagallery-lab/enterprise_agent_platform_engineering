# 《企业级 Agent 平台工程：从数据智能底座到 AI 原生业务系统》

> 当前版本：**v0.1 骨架** · 共 11 Part / 55 章 / 16 实战项目 / 主体 ~1150 页

数据智能与 Agent 平台的中文权威开源参考书。完整介绍见仓库根目录的 [README](https://github.com/your-org/agent_platform_book#readme) 和 [总策划 PLAN.md](https://github.com/your-org/agent_platform_book/blob/main/PLAN.md)。

---

## 快速导航

- [Part I 总论与平台观](part01-overview/zh/index.md)
- [Part II 模型与推理](part02-model-inference/index.md)
- [Part III 数据基础设施](part03-data-infra/index.md)
- [Part IV 向量、检索与知识工程](part04-vector-knowledge/index.md)
- [Part V Agent 能力百科](part05-agent-capabilities/index.md)
- [Part VI DataAgent 主线深潜](part06-dataagent/index.md)
- [Part VII 可观测性、评估与成本](part07-observability-eval/index.md)
- [Part VIII 部署与基础设施](part08-deployment/index.md)
- [Part IX 前端、交互与多模态](part09-frontend-multimodal/index.md)
- [Part X 安全、合规与组织](part10-security-org/index.md)
- [Part XI 业务案例集](part11-cases/index.md)
- [附录](appendix/index.md)

---

## 三层阅读法

每章固定 L1 概念 / L2 架构 / L3 工程实现三段：

- **L1 概念**（~30%）：业务定义、边界、相邻概念对比、典型误区
- **L2 架构**（~40%）：组件划分、数据流、接口契约、状态机、失败模式
- **L3 工程**（~30%）：mini-platform 可运行代码、生产化 checklist、踩坑记录

---

## 五条读者路径

| 角色 | 推荐路径 | 页数 |
|---|---|---|
| CTO / 平台负责人 | Part I + Part V/VI/X 各章 L1+L2 | ~350 |
| 架构师 | Part I + Part II/III/IV/V/VIII 全部 + Part VI L2 | ~800 |
| 数据智能工程师 | Part I L1 + Part III/IV 全部 + Part VI 全部 + Part VII | ~600 |
| AI 应用开发者 | Part I L1 + Part II/V 全部 L3 + Part IX + 附录 | ~650 |
| 安全 / 合规 | Part I + Part VII/X 全部 + Part III 元数据/血缘 | ~350 |

---

## 配套开源实现

本书所有 L3 工程代码都对应 `mini-enterprise-agent-platform` 仓库的真实文件。仓库与书稿采用 monorepo，单一真相源。

[开始阅读 →](part01-overview/zh/index.md)
