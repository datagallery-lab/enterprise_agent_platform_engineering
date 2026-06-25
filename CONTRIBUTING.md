# 贡献指南

欢迎参与《企业级 Agent 平台工程》的写作与开源建设。本书采用 **主编 + Part Owner + 章节贡献者** 三级治理。

## 你可以贡献什么

| 类型 | 描述 |
|---|---|
| 章节主笔 | 认领单章正文，按正式章节结构完成摘要、关键词、学习目标、场景引入、编号小节、小结和参考文献 |
| Part Owner | 统筹一个 Part（4-10 章）的章节安排、风格一致性 |
| 案例提供 | 提供可复核、可脱敏的企业落地材料 |
| 配图贡献 | 提供架构图、时序图、状态机、数据流图或界面截图 |
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
每章必须采用正式技术书结构：

- `# 第N章 章节标题`
- `## 本章摘要`
- `## 关键词`
- `## 学习目标`
- `## 场景引入`
- `## N.1 ...`、`## N.2 ...` 等编号正文小节
- `## 本章小结`
- `## 参考文献`

参考 [`templates/chapter-template.md`](templates/chapter-template.md)。

旧版 `L1/L2/L3` 只是早期规划方法，不得作为正式标题、固定篇幅比例或每章必备骨架。概念章、工程章、治理章和案例章应按本章对象组织内容；没有明确上线对象的章节，不得硬写上线清单、踩坑记录或项目闭环。

### 配图
- 图片统一放在 `docs/images/partN/ch/` 或 `docs/images/partN/en/`，正文按当前语言引用对应目录。
- 图片文件名使用章节号和英文短名，例如 `ch22-run-state-machine.svg`。
- 正文图片必须同时具备 Markdown alt、独立图题、来源和 Alt text。
- 架构图、时序图、状态机和数据流图优先使用可维护的 SVG 或 Mermaid 源；截图必须说明来源。
- 每章图片数量服从内容需要，不为凑数量添加装饰图。

### 写作风格
- 第三人称客观叙述
- 所有 Python 代码片段对应 `mini-platform/projects/` 测试，CI 跑通
- 每次出现框架 API（如 LangGraph、OpenAI SDK）必须说明"为什么用"和"替代方案"
- 不使用固定虚构公司作为统一背景；如需场景，应使用读者能理解的匿名化复合场景，并写清角色、系统、任务和约束
- 禁用 emoji 与营销腔
- 禁止真实公司名、真实业务数据、真实凭证、真实内网地址

### 术语
- 正文中反复出现的英文缩写必须在 `glossary/terms.md` 中登记
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

章节中的代码片段必须指向 mini-platform 真实文件路径（如 `core/runtime/state_machine.py`），并在 CI 中保证可运行。接口示意代码必须显式标注为示意，不得写成已经实现的能力。

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
