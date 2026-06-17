"""Part V Registry：Ch.23 工具 + Ch.24 MCP + Ch.28 Handoff + 报告工具。

关联章节：Ch.28–Ch.30 · projects/multi-agent-workflow
"""
from __future__ import annotations

from typing import Any

from core.registry import ToolRegistry, ToolSpec
from core.runtime.handoff_tool import handoff_handler
from tools.mcp_db import McpDbClient, register_mcp_tools


def echo_handler(message: str) -> dict[str, str]:
    """回显消息（连通性测试）。"""
    return {"echo": message}


def sql_executor_handler(query: str, tenant_id: str) -> dict[str, object]:
    """模拟只读 SQL 查询。"""
    return {
        "rows": [{"sku": "SKU-A", "sales": 3200, "delta": -12}],
        "query": query,
        "tenant_id": tenant_id,
    }


def render_report_handler(summary: str, format: str = "markdown") -> dict[str, Any]:
    """生成报告草稿 artifact（无副作用）。"""
    body = f"# 华东区 Q1 毛利分析\n\n{summary}\n"
    return {
        "format": format,
        "summary": summary,
        "report_md": body,
        "status": "draft",
    }


def publish_report_handler(report_md: str, tenant_id: str) -> dict[str, Any]:
    """发布报告（Demo：打印级副作用）。"""
    return {
        "published": True,
        "tenant_id": tenant_id,
        "bytes": len(report_md),
        "channel": "internal_console",
    }


def build_workflow_registry() -> ToolRegistry:
    """构造 Part V 实战项目使用的 Tool Registry。

    Returns:
        已注册 handoff、sql、MCP、报告类工具的 Registry。
    """
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="handoff",
            version="v1",
            description="将控制权转移给另一 Agent（同一 run_id）",
            parameters_schema={
                "type": "object",
                "properties": {
                    "to_agent_id": {
                        "type": "string",
                        "description": "目标 Agent：question_agent/data_agent/report_agent",
                    },
                    "payload": {"type": "object", "description": "结构化交接内容"},
                    "reason": {"type": "string", "description": "路由原因"},
                },
                "required": ["to_agent_id"],
                "additionalProperties": False,
            },
            handler=handoff_handler,
        )
    )
    registry.register(
        ToolSpec(
            name="echo",
            version="v1",
            description="回显输入文本",
            parameters_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "additionalProperties": False,
            },
            handler=echo_handler,
        )
    )
    registry.register(
        ToolSpec(
            name="sql_executor",
            version="v1",
            description="执行只读 SQL（Demo 固定行）",
            parameters_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "tenant_id": {"type": "string"},
                },
                "required": ["query", "tenant_id"],
                "additionalProperties": False,
            },
            handler=sql_executor_handler,
        )
    )
    registry.register(
        ToolSpec(
            name="render_report",
            version="v1",
            description="生成报告草稿；成功后 Run 进入 waiting_human",
            parameters_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "format": {"type": "string", "default": "markdown"},
                },
                "required": ["summary"],
                "additionalProperties": False,
            },
            handler=render_report_handler,
        )
    )
    registry.register(
        ToolSpec(
            name="publish_report",
            version="v1",
            description="发布已审批报告（须 approval_granted）",
            parameters_schema={
                "type": "object",
                "properties": {
                    "report_md": {"type": "string"},
                    "tenant_id": {"type": "string"},
                },
                "required": ["report_md", "tenant_id"],
                "additionalProperties": False,
            },
            handler=publish_report_handler,
        )
    )
    register_mcp_tools(registry, McpDbClient())
    return registry
