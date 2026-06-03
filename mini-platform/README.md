# mini-enterprise-agent-platform

本仓库是《企业级 Agent 平台工程》一书的配套参考实现。当前为 **v0.1 骨架阶段**，仅含最小可运行 stub。

## 目录结构

```
mini-platform/
├── core/                       # 平台内核
│   ├── runtime/                # Agent Runtime (Ch.22)
│   ├── registry/               # Tool/Agent 注册中心 (Ch.23)
│   ├── memory/                 # 记忆系统 (Ch.27)
│   ├── planner/                # 编排 (Ch.25-26)
│   ├── rag/                    # 检索 (Ch.20)
│   ├── observability/          # Trace (Ch.38)
│   ├── eval/                   # 评测 (Ch.39-40)
│   ├── policy/                 # 权限脱敏 (Ch.50)
│   ├── gateway/                # LLM 网关 (Ch.45)
│   └── guardrails/             # 内容安全 (Ch.51)
├── infra/                      # 数据基础设施适配
│   ├── lakehouse/              # Iceberg / DuckDB (Ch.11-12)
│   ├── metadata/               # DataHub / OpenLineage (Ch.15)
│   ├── semantic_layer/         # Cube / MetricFlow (Ch.33)
│   └── vectorstore/            # 向量库适配 (Ch.18)
├── tools/                      # 内置工具
├── agents/                     # 参考 Agent
├── console/                    # 管理后台
├── configs/                    # 配置文件
├── datasets/                   # 脱敏样例
├── benchmarks/                 # 评测脚本
├── projects/                   # 16 个实战项目
└── tests/                      # 测试
```

## 开发

```bash
pip install -e .
pytest tests/
```

## 与书稿的对应关系

每个模块顶部注释标注关联章节号（如 `# Related: Ch.22 Agent Runtime`）。书稿 L3 段落引用本仓库的真实文件路径。
