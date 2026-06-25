"""MCP 数据库工具 Demo 单元测试。

关联章节：Ch.24 · §6 实战项目
"""
from __future__ import annotations

import pytest

from core.registry import ToolNotFoundError, ToolRegistry
from tools.mcp_db import McpDbClient, McpDbServer, register_mcp_tools


def test_list_tools():
    server = McpDbServer()
    tools = server.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "query_sales"
    assert "inputSchema" in tools[0]


def test_call_tool_success():
    server = McpDbServer()
    result = server.call_tool(
        "query_sales",
        {"region": "华东", "tenant_id": "t1"},
    )
    assert "structuredContent" in result
    rows = result["structuredContent"]["rows"]
    assert len(rows) == 2
    assert rows[0]["region"] == "华东"


def test_call_tool_unknown():
    server = McpDbServer()
    with pytest.raises(KeyError, match="unknown tool"):
        server.call_tool("missing", {"region": "华东", "tenant_id": "t1"})


def test_call_tool_missing_params():
    server = McpDbServer()
    with pytest.raises(ValueError, match="region and tenant_id"):
        server.call_tool("query_sales", {"region": "华东"})


def test_handle_jsonrpc_unsupported():
    server = McpDbServer()
    with pytest.raises(ValueError, match="unsupported method"):
        server.handle_jsonrpc("tools/ping", {})


def test_client_list_and_call():
    client = McpDbClient()
    tools = client.list_tools()
    assert tools[0]["name"] == "query_sales"
    raw = client.call_tool(
        "query_sales",
        {"region": "华北", "tenant_id": "t2"},
    )
    assert raw["structuredContent"]["tenant_id"] == "t2"


def test_register_mcp_tools_and_invoke():
    client = McpDbClient()
    registry = ToolRegistry()
    n = register_mcp_tools(registry, client)
    assert n == 1
    result = registry.invoke(
        "mcp_db_query_sales",
        "v1",
        {"region": "华东", "tenant_id": "shanlan-retail"},
    )
    assert result.output["tenant_id"] == "shanlan-retail"
    assert len(result.output["rows"]) == 2


def test_invoke_before_register():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        registry.invoke("mcp_db_query_sales", "v1", {"region": "华东", "tenant_id": "t1"})
