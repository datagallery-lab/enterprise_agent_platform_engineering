# 贡献指南

欢迎参与《企业级 Agent 平台工程》的写作与开源建设。本书采用 **主编 + Part Owner + 章节贡献者** 三级治理。

## 你可以贡献什么

| 类型 | 描述 |
|---|---|
| 章节主笔 | 认领单章的 L1/L2/L3 完整撰写 |
| Part Owner | 统筹一个 Part（4-10 章）的章节安排、风格一致性 |
| 案例提供 | 提供企业落地的脱敏踩坑案例 |
| 配图贡献 | 提供 Mermaid 架构图、时序图、状态机 |
| 术语修正 | 完善 `glossary/terms.md` |
| 校对 | PR 评审、文字润色、链接检查 |
| 代码贡献 | mini-platform 模块实现、实战项目 |

## 认领章节

1. 在 [Issues](https://github.com/your-org/agent_platform_book/issues) 查找 `label:chapter-claim` 的章节
2. 使用 [`templates/chapter-claim.md`](templates/chapter-claim.md) 提交认领申请
3. Part Owner 在 48 小时内确认

## 工作流

```
fork 仓库
└─ git checkout -b feature/partXX-chYY-<topic>
   └─ 撰写章节（使用 templates/chapter-template.md）
      └─ 本地跑 ./scripts/check_all.sh
         └─ 提 PR 到 main 分支
            └─ CI 自动跑全部质量门禁
               └─ Part Owner + 主编 + ≥1 reviewer 评审
                  └─ 合并 → 自动部署到 next 频道
                     └─ 每月 milestone 合并到 stable
```

## 写作规范

### 章节结构（强制）
每章必须包含且仅包含以下 4 个二级标题：
- `## L1 概念`
- `## L2 架构`
- `## L3 工程实现`
- `## 本章小结`

参考 [`templates/chapter-template.md`](templates/chapter-template.md)。

### 三层篇幅比例
L1 : L2 : L3 ≈ 3 : 4 : 3。L1 偏概念，无代码；L2 偏架构图与契约；L3 偏代码与 checklist。

### 配图
- 架构图、时序图、状态机统一 Mermaid 源（`assets/mermaid/chNN-*.mmd`），导出为 SVG
- 三色制：蓝=组件 / 灰=外部系统 / 红=控制流
- 每章 5-12 张图

### 写作风格
- 第三人称客观叙述
- 所有 Python 代码片段对应 `mini-platform/projects/` 测试，CI 跑通
- 每次出现框架 API（如 LangGraph、OpenAI SDK）必须说明"为什么用"和"替代方案"
- 统一使用虚构公司「山岚集团」（零售/制造/金融/物流）作为案例
- 禁用 emoji 与营销腔
- 禁止真实公司名、真实业务数据、真实凭证、真实内网地址

### 术语
- L1/L2 段落中出现的英文缩写必须在 `glossary/terms.md` 中登记
- 首次出现时给出中文释义
- CI 自动校验

## 本地预览

```bash
pip install mkdocs-material pymdown-extensions
mkdocs serve
# 访问 http://127.0.0.1:8000
```

## 本地运行质量门禁

```bash
./scripts/check_all.sh
```

包含：章节模板完整性、术语统一、敏感信息扫描、mini-platform 测试。

## mini-platform 开发

```bash
cd mini-platform
pip install -e .[dev]
pytest tests/ -q
```

每个章节的 L3 代码片段必须指向 mini-platform 真实文件路径（如 `core/runtime/state_machine.py`），并在 CI 中保证可运行。

## PR 要求

- 提交信息格式：`docs(chNN): <动作> <内容>` 或 `feat(core/<module>): <内容>`
- 每个 PR 不超过一个章节或一个模块
- PR 描述中说明：解决的 Issue、关联章节、关键设计取舍
- CI 全绿后才进入评审

## Code of Conduct

参与本项目即同意遵守 [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) v2.1。

## 联系方式

- Issues 用于功能讨论与章节认领
- Discussions 用于风格与决策讨论
- 紧急联系：（待主编上线后补充）
