# 《企业级 Agent 平台工程：从数据智能底座到 AI 原生业务系统》

本书面向企业级 Agent 平台建设，讨论从数据智能底座、模型推理、知识工程、Agent Runtime、工具生态到评估、部署、前端、安全和组织治理的完整工程体系。中文第一版以“可读、可验证、可发布”为整理目标：已有正文按正式技术书标准修订，尚未形成可靠内容的案例和附录只保留后续版本说明，不编造事实。

## 版本入口

| 版本 | 入口 |
| --- | --- |
| 中文版 | [开始阅读 Part I](part01-overview/ch/index.md) |
| English Edition | [Start with Part I](part01-overview/en/index.md) |

## 卷前页面

| 页面 | 用途 |
| --- | --- |
| [缩写表](abbreviations.md) | 统一英文缩写、中文译名和本书采用的工程口径 |
| [序言](preface.md) | 说明本书的问题意识、平台工程视角和版本边界 |
| [致谢](acknowledgements.md) | 正式版本补齐，目前不预填未确认贡献 |
| [卷前导读](front_matter_guide.md) | 按角色、问题类型和全书层次给出阅读路径 |
| [贡献者](contributors.md) | 正式版本补齐，目前不预填姓名或机构 |

## 快速导航

| 部分 | 主题 |
| --- | --- |
| [Part I 总论与平台观](part01-overview/ch/index.md) | Agent 本质、平台边界、AI 原生业务系统和全书地图 |
| [Part II 模型与推理](part02-model-inference/ch/index.md) | 模型选型、本地推理、推理优化、结构化输出和能力定制 |
| [Part III 数据基础设施](part03-data-infra/ch/index.md) | 采集、湖仓、OLAP、实时、编排质量、元数据和指标 |
| [Part IV 向量、检索与知识工程](part04-vector-knowledge/ch/index.md) | Embedding、重排、向量库、文档解析、RAG 和知识工程 |
| [Part V Agent 能力百科](part05-agent-capabilities/ch/index.md) | Runtime、Tool Registry、MCP、Planner、Workflow、Memory、多 Agent 和协议 |
| [Part VI DataAgent 主线深潜](part06-dataagent/ch/index.md) | 语义层、NL2SQL、Python 分析、可视化报告和生态对标 |
| [Part VII 可观测性、评估与成本](part07-observability-eval/ch/index.md) | Trace、离线评估、在线评估、成本治理和 SLO |
| [Part VIII 部署与基础设施](part08-deployment/ch/index.md) | GPU 调度、模型部署、LLM 网关、GitOps 和边缘推理 |
| [Part IX 前端、交互与多模态](part09-frontend-multimodal/ch/index.md) | 对话 UI、Generative UI、多模态输入和语音 Agent |
| [Part X 安全、合规与组织](part10-security-org/ch/index.md) | 攻防、Guardrails、法规合规、组织和平台演进 |
| [Part XI 案例方法论与后续案例准入](part11-cases/ch/index.md) | 定义案例纳入、复审和平台化收束标准，不在第一版中编造案例 |
| [附录](appendix/index.md) | 安装、术语、API、评测、写作规范和延伸阅读的后续补充区 |

## 阅读路径

| 角色 | 建议路径 |
| --- | --- |
| AI 平台负责人 / CTO | Part I -> Part V -> Part VI -> Part X |
| 架构师 | Part I -> Part II -> Part III -> Part IV -> Part V -> Part VIII |
| 数据智能工程师 | Part III -> Part IV -> Part VI -> Part VII |
| AI 应用开发者 | Part II -> Part V -> Part IX -> mini-platform |
| 安全 / 合规负责人 | Part I -> Part VII -> Part X |

## 本地验证

```bash
bash scripts/check_all.sh
python -m mkdocs build --strict --clean --site-dir /tmp/enterprise-agent-book-site
```

第一条命令检查章节结构、术语、敏感信息和 mini-platform 测试；第二条命令检查电子书站点能否按严格模式构建。

[开始阅读 Part I](part01-overview/ch/index.md)

[Start with English Edition](part01-overview/en/index.md)

[阅读卷末说明](afterword.md)
