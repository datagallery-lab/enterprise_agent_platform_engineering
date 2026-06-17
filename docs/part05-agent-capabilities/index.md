# Part V Agent 能力百科

**统一实战项目**：`mini-platform/projects/multi-agent-workflow/` — Ch.22–Ch.30 共用 **同一 `run_id`** Run 链（`start` → Handoff / MCP / 报告 → `waiting_human` → `approve` → `succeeded`）。各章 Registry、MCP 等能力另见 `tests/test_registry.py`、`tests/test_mcp_db.py` 单测。

## 本部分章节

- [Ch.22 Agent Runtime](ch22-agent-runtime.md) — Run 六态、任务执行、检查点、失败恢复、超时重试
- [Ch.23 Tool Registry & Function Calling](ch23-tool-registry-function-calling.md) — 能力注册、Schema、版本治理、调用契约
- [Ch.24 MCP 与企业工具生态](ch24-mcp.md) — host-client-server 架构、tools/resources/prompts、企业接入
- [Ch.25 Planner 与编排模式](ch25-planner.md) — ReAct、Plan-and-Execute、状态机、工作流取舍
- [Ch.26 Agentic Workflow](ch26-agentic-workflow.md) — Reflexion、Self-Refine、Tree of Thoughts、AutoGPT 范式批判
- [Ch.27 Memory 系统](ch27-memory.md) — 短期/长期/用户画像/企业上下文；mem0、Letta 对标
- [Ch.28 多 Agent 协作](ch28-agent.md) — Planner/Router/Executor/Reviewer；通信协议；冲突仲裁
- [Ch.29 Agent 协议与标准](ch29-agent.md) — MCP、A2A、Agent Card、ACP；跨平台协作
- [Ch.30 Human-in-the-loop 与长任务](ch30-human-in-the-loop.md) — 审批、打断、回放、异步队列、检查点
- [Ch.31 框架横向对标](ch31.md) — LangGraph、AutoGen、CrewAI、Dify、Coze、Bisheng；自研 vs 用现成
