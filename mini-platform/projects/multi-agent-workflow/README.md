# Part V 实战项目 · multi-agent-workflow

> 关联章节：Ch.22 RunLoop · Ch.23 Registry · Ch.24 MCP · Ch.25 Planner · Ch.28 Handoff · Ch.30 HITL  
> 难度：★★★

Part V 统一 Demo：**同一 `run_id`** 内走完 Workflow → Question → Data（MCP）→ Report → **waiting_human** → publish → succeeded。

## 运行环境

- Python ≥ 3.11
- 工作目录：可在 `mini-platform` 根目录或本目录运行

## 两步运行（手动 approve）

**步骤 1 — 启动 Run（在 `waiting_human` 暂停）：**

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py start
```

终端会输出 SSE（`state` / `action` / `result` / `approval_request`）及 `run_id`。

**步骤 2 — 另开终端，手动批准并继续：**

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py approve --run-id run-xxxxxxxxxxxx
```

`--run-id` 可省略（读取上次 `start` 写入的 `.last_run_id`）。

## 单终端交互（可选）

```bash
python3 projects/multi-agent-workflow/run.py start --interactive
```

在 `waiting_human` 处按 Enter，脚本会在 **同一进程** 内调用 `loop.approve()` 与 `loop.resume()`。

## 代码入口

| 模块 | 说明 |
|------|------|
| `lib/registry_setup.py` | Registry：handoff / sql / MCP / report |
| `lib/planner.py` | 多 Agent 规则 Planner |
| `core/runtime/run_loop.py` | RunLoop + waiting_human + approve/resume |
| `core/runtime/handoff_tool.py` | `handoff@v1` handler |

## 测试

```bash
cd mini-platform
pytest tests/test_multi_agent_workflow_run.py tests/test_runtime.py -q
```

检查点文件写入 `projects/multi-agent-workflow/.checkpoints/`（可删）。
