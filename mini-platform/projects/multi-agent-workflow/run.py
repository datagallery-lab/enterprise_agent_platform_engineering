"""Part V 实战项目：一条 Run 链（Handoff + MCP + waiting_human）。

关联章节：Ch.22–Ch.30

用法（推荐在 ``mini-platform`` 根目录执行）：

    python3 projects/multi-agent-workflow/run.py start
    python3 projects/multi-agent-workflow/run.py approve

也可 ``cd projects/multi-agent-workflow`` 后执行 ``python3 run.py start`` / ``approve``。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_PROJECT_DIR = Path(__file__).resolve().parent
_MINI_PLATFORM = _PROJECT_DIR.parents[1]
sys.path.insert(0, str(_MINI_PLATFORM))
sys.path.insert(0, str(_PROJECT_DIR))

from lib import MultiAgentPlanner, build_workflow_registry  # noqa: E402
from core.runtime import CheckpointStore, RunLoop  # noqa: E402

RUN_ID_FILE = _PROJECT_DIR / ".last_run_id"


def _resolve_checkpoint_dir() -> Path:
    """解析检查点目录：优先 ``CHECKPOINT_DIR`` 环境变量，否则用项目内 ``.checkpoints/``。

    容器与宿主机可通过挂载同一卷并设置 ``CHECKPOINT_DIR`` 共享检查点。

    Returns:
        检查点持久化目录的绝对路径。
    """
    env_dir = os.environ.get("CHECKPOINT_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return _PROJECT_DIR / ".checkpoints"


CHECKPOINT_DIR = _resolve_checkpoint_dir()


def _script_cli_path() -> str:
    """返回从 ``mini-platform`` 根目录执行时 ``run.py`` 的相对路径。

    Returns:
        例如 ``projects/multi-agent-workflow/run.py``。
    """
    try:
        rel = _PROJECT_DIR.relative_to(_MINI_PLATFORM)
    except ValueError:
        return str(_PROJECT_DIR / "run.py")
    return f"{rel.as_posix()}/run.py"


def _approve_command_hint(run_id: str) -> str:
    """生成 ``approve`` 命令提示（与 README 一致，假定 cwd 为 ``mini-platform``）。

    Args:
        run_id: 当前 Run ID。

    Returns:
        可直接复制的 shell 命令行。
    """
    script = _script_cli_path()
    return (
        f"python3 {script} approve\n"
        f"  # 或显式指定 run_id：python3 {script} approve --run-id {run_id}"
    )


def _make_loop(event_sink=print) -> RunLoop:
    """构造带持久化检查点的 RunLoop。"""
    return RunLoop(
        registry=build_workflow_registry(),
        planner=MultiAgentPlanner(),
        checkpoint_store=CheckpointStore(persist_dir=CHECKPOINT_DIR),
        event_sink=event_sink,
    )


def cmd_start(interactive: bool) -> int:
    """启动 Run 直至 ``waiting_human`` 或终态。"""
    loop = _make_loop()
    ctx = loop.run(
        agent_id="workflow_agent",
        user_input="华东区 Q1 毛利为什么下滑？请给出简要报告",
        context={"tenant_id": "shanlan-retail", "scope": ["sales_region:华东"]},
    )
    RUN_ID_FILE.write_text(ctx.run_id, encoding="utf-8")
    state = loop.get_state(ctx.run_id)
    print(f"\n--- run_id={ctx.run_id} state={state} ---")
    print(f"handoffs={len(ctx.handoff_stack)} tool_calls={len(ctx.tool_calls)}")

    if state == "waiting_human":
        print("\nRun 已在 waiting_human 暂停。")
        print("手动批准并继续，请执行（在 mini-platform 根目录）：")
        print(f"  {_approve_command_hint(ctx.run_id)}")
        if interactive:
            input("\n按 Enter 在本进程内调用 approve()+resume() ...")
            loop.approve(ctx.run_id, approver_id="u-director-001", comment="口径已确认")
            ctx = loop.resume(ctx.run_id)
            print(f"\nfinal_state={loop.get_state(ctx.run_id)}")
            print(f"answer={ctx.answer}")
    elif state == "succeeded":
        print(f"\nanswer={ctx.answer}")
    return 0


def cmd_approve(run_id: str, approver_id: str, comment: str) -> int:
    """从检查点恢复，手动 ``approve`` 后 ``resume``。"""
    loop = _make_loop()
    state = loop.get_state(run_id)
    print(f"loaded run_id={run_id} state={state}")
    if state != "waiting_human":
        print(f"错误：当前状态为 {state}，仅 waiting_human 可 approve")
        return 1
    loop.approve(run_id, approver_id=approver_id, comment=comment)
    ctx = loop.resume(run_id)
    print(f"\nfinal_state={loop.get_state(run_id)}")
    print(f"answer={ctx.answer}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Part V Run 链 Demo")
    sub = parser.add_subparsers(dest="command", required=True)

    start_p = sub.add_parser("start", help="启动 Run，在 waiting_human 暂停")
    start_p.add_argument(
        "--interactive",
        action="store_true",
        help="暂停后在本进程内按 Enter 调用 approve()+resume()",
    )

    approve_p = sub.add_parser("approve", help="手动批准并继续 Run")
    approve_p.add_argument("--run-id", help="Run ID；省略则读 .last_run_id")
    approve_p.add_argument("--approver-id", default="u-director-001")
    approve_p.add_argument("--comment", default="口径已确认")

    args = parser.parse_args()
    if args.command == "start":
        raise SystemExit(cmd_start(args.interactive))
    if args.command == "approve":
        run_id = args.run_id or RUN_ID_FILE.read_text(encoding="utf-8").strip()
        raise SystemExit(cmd_approve(run_id, args.approver_id, args.comment))


if __name__ == "__main__":
    main()
