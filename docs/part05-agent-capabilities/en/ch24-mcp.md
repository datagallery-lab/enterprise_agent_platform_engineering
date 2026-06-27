# Chapter 24 MCP and the Enterprise Tool Ecosystem

---

MCP provides an open protocol for connecting models to external tools and data, but an enterprise cannot connect arbitrary MCP Servers directly into production. External capability still has to pass through the enterprise Registry for permission control, audit, versioning, and risk classification. Host, Client, Server, Tools, Resources, and the enterprise Registry belong to different boundaries. Collapsing them into one layer makes tool governance hard to control.

Chapter 23 converged tools into a Tool Registry: register by `(name, version)`, validate schema, and invoke through a unified `invoke` path. In practice, however, existing enterprise capabilities are scattered across team-owned HTTP services, script libraries, and vendor SaaS products. If every consuming Agent writes its own adapter, the platform quickly returns to the old pattern of one Agent and one integration.

The Registry governs unified naming, versioning, validation, permission policy, and audit inside the platform. MCP governs the protocol across process and service boundaries. The integration path should remain discover, register, invoke. MCP must not replace the Registry. Discovery can happen through L1 or the MCP Client's `tools/list`, but discovery does not enter the Run main loop. Execution and audit should still follow the Chapter 22 and Chapter 23 chain: `action` to `invoke` to `result`.

Model Context Protocol (MCP), promoted by Anthropic and others, uses JSON-RPC semantics to expose Tools, Resources, and Prompts so that a Client inside a Host can connect to multiple Servers in a consistent way (Anthropic 2024; Model Context Protocol 2024). In this book's platform layering, MCP belongs to the L3 integration standard: external Servers expose capabilities through MCP, the platform-side Client fetches `tools/list`, those capabilities are registered into Registry, and Runtime continues to use the unified invocation chain from Chapters 22 and 23. For Agent-to-Agent interoperability protocols such as A2A, read this chapter together with Chapter 29 (Google 2024).

This chapter uses the following terminology. MCP refers to Model Context Protocol, the JSON-RPC standard in the L3 protocol layer. Host is the application process that hosts the user session and orchestrates the LLM and Client; in this platform, it roughly maps to Runtime plus Planner. Client connects to Server on behalf of the Host and relays `tools/list` and `tools/call`. Server is an independent process or service that exposes Tools, Resources, and Prompts.

Consider a multi-business-line enterprise that encapsulates a read-only sales wide-table query as an MCP Server. DataAgent, Finance Agent, and operations scripts can share the same service, while audit and version governance stay in the Registry layer. The key boundaries are where MCP sits in L3, how Tools, Resources, and Prompts divide responsibilities, and how MCP tools enter Tool Registry. MCP makes tools and resources easier to expose through a standard protocol. It does not automatically solve enterprise governance. Production access still has to pass through existing controls for identity, network isolation, audit, data classification, and tool version management.

---

## 24.1 MCP's Position in the Platform Protocol Layering

Chapter 2 defines **L3 Protocol Interoperability** as the standard interface layer across systems and platforms. MCP's current most typical ecosystem niche is: **enabling LLM applications (Host) to use external data and tools (Server) in a standardized way**, instead of duplicating an HTTP client in every Agent project (Anthropic 2024).

### 24.1.1 Relationship with Registry and Runtime

The table below summarizes the division of responsibilities among MCP, Registry, and Runtime at L2 / L3:

*Table 24-1: Relationship between MCP components and Registry, Runtime. Source: Compiled by this book.*

| Layer       | Component      | MCP-Related Responsibilities                             |
|-------------|----------------|---------------------------------------------------------|
| L2 Runtime  | Runtime        | Unchanged: send `action`, call Registry `invoke`, write `result` |
| L2 Runtime  | Tool Registry  | Stores `ToolSpec` + handler after MCP tool registration  |
| L3 Protocol | MCP Client     | `tools/list`, `tools/call`, transport (stdio / Streamable HTTP) |
| L3 Protocol | MCP Server     | Exposes tool implementations; optional Resources/Prompts  |

The relationship among Runtime, Registry, and MCP Client inside the Host is shown in **Figure 23-1** (Registry architecture) and **Figure 24-1** (MCP bridging closed loop); a Client can connect to multiple MCP Servers (sidecar or shared service; deployment topologies are discussed below). When an enterprise integrates MCP, the key issue is whether it still respects the original runtime boundaries. Runtime should not bypass the Run state, Tool Call recording, and error categorization in Chapter 22 just because the tool originates from MCP; Registry should not abandon platform-side naming, versioning, and risk registration just because the MCP Server already has an `inputSchema`. MCP solves cross-process tool discovery and invocation; enterprise platforms still need to manage who can call the tool, which version, which logs results enter, and how failures replay.

### 24.1.2 Four hard constraints for MCP integration

Enterprise MCP integration usually fails around four judgments: whether MCP is placed in the wrong layer, whether Runtime bypasses Registry, whether Resources replace the retrieval system, and whether Server-side audit is missing. Clarifying these four constraints before discussing Host, Client, and Server deployment prevents integration from becoming a simple connectivity exercise.

#### MCP does not replace Tool Registry

Registry governs unified naming, versioning, validation, permission policy, risk classification, and audit inside the platform. MCP governs protocol behavior across process and service boundaries. The correct path is to register MCP tools into Registry first, then let Runtime invoke them through Registry.

#### The Run main loop does not connect directly to MCP Server

Creating a new MCP connection for every Tool Call causes latency and connection storms. MCP Client should be registered as a Registry handler, while connection pooling and circuit breaking are reused at the Client layer. Direct connection also breaks responsibility ownership. If Runtime holds an MCP Client and calls Server directly, the tool call no longer passes Registry version selection or schema validation. Trace also struggles to reconstruct which tool definition the model saw, which Server was actually called, and which recovery strategy was used after failure. This becomes especially dangerous when the same Server is shared by multiple Agents: one Agent may upgrade tool parameters while another still calls the old schema. The platform only sees a vague tool failure while the useful evidence stays in Server logs.

#### Resources do not replace RAG

MCP Resources provide readable URIs and snapshots. Enterprise retrieval, permissions, and indexing still belong to Chapter 20 RAG and vector stores. The two can coexist: RAG searches, while Resources read a known document version.

#### Server-side audit must remain

MCP standardizes protocol. It does not provide enterprise IAM by itself. The Server side must record caller identity, `tenant_id`, tool name, parameter summary, result summary, and `run_id`. Platform Trace should link to those records (Chapter 38). The question of who can call which tool still belongs to Chapter 50 Policy and network isolation.

---

## 24.2 Host / Client / Server architecture and deployment

The MCP specification defines three roles (Model Context Protocol 2024):

*Table 24-2: Meanings and example scenarios of MCP Host, Client, and Server roles. Source: Compiled by this book.*

| Role   | Description                                 | Industry Scenario Example      |
|--------|---------------------------------------------|-------------------------------|
| **Host**   | Hosts user sessions and orchestrates LLM with Client applications | DataAgent platform process      |
| **Client** | Represents Host to connect to Server, forwarding `tools/list`, `tools/call`   | Built-in platform `McpDbClient` |
| **Server** | Independent process or service exposing Tools/Resources/Prompts               | `mcp-db` read-only query service |

### 24.2.1 Transmission Methods

In MCP production deployment, "local process" and "remote service" are distinguished. Local Servers typically use **stdio**; remote Servers should prefer MCP's **Streamable HTTP** (mainstream remote transport since 2025-03-26). The legacy **HTTP+SSE** can be used for backward compatibility or understood as a server message stream mechanism within Streamable HTTP, but it should not be the primary name for production remote transport in new documentation.

*Table 24-3: Applicable scenarios and notes for different MCP transmission methods. Source: Compiled by this book.*

| Transmission      | Scenario                                    | Notes                                                      |
|-------------------|---------------------------------------------|------------------------------------------------------------|
| **stdio**         | Local subprocess, IDE plugins, developer tools | Container environments must clarify subprocess lifetime to avoid zombie processes |
| **Streamable HTTP**| Remote MCP Server, Kubernetes deployments, multi-Host sharing | Requires TLS, authentication, timeout, body size limit, and gateway routing configuration |
| **HTTP+SSE (compatibility)** | Integration with deprecated endpoints per 2024-11-05 spec | Only for compatibility; new deployments should prioritize Streamable HTTP |
| **In-process (Demo)** | Teaching and unit tests                      | Used by `tools/mcp_db/`; simulates only method/params dispatch, not production transport layer |

This chapter's demo reduces dependencies by using in-process `McpDbClient -> McpDbServer` calls. Production implementations should replace this with official SDK's stdio or Streamable HTTP transports while preserving the call boundaries Runtime -> Registry -> handler -> MCP Client. Transmission mode affects failure characteristics. stdio Server failures often stem from subprocess lifecycle, stdio blocking, or container restart issues; remote HTTP Server failures often result from authentication problems, gateway timeouts, oversized bodies, connection pool exhaustion, or regional network policies. Packaging all errors as ordinary tool failures leads the Planner to repeat the same call. A better approach separates transport timeouts, Server business errors, schema mismatches, and permission denials for recording, enabling Runtime to choose retry, circuit breaking, Planner feedback, or escalation to human intervention. A typical `tools/list` and `tools/call` interaction sequence is as follows:

*Table 24-4: Steps, directions, and descriptions of a single MCP communication. Source: Compiled by this book.*

| Step | Direction        | Description                          |
|-------|------------------|------------------------------------|
| 1     | Host -> Client    | Connect to Server (stdio / Streamable HTTP) |
| 2     | Client -> Server  | `tools/list` -> tool definitions array |
| 3     | Host -> Client    | `tools/call(name, args)`            |
| 4     | Client -> Server  | JSON-RPC request                   |
| 5     | Server -> Client  | `content` + optional `structuredContent` |
| 6     | Client -> Host    | Normalized result returned by Registry handler |

The Server should record `tenant_id`, caller identity, and parameter summary for every `tools/call` for traceability and compliance export described in Chapter 38. The protocol itself does not replace audit storage.

### 24.2.2 Deployment Topology

- **Sidecar**: Each Agent Pod sidecar connects to a dedicated MCP Server, suitable for strong tenant isolation.
- **Shared Service**: Platform operations deploy `mcp-db` centrally; multiple Hosts connect through Clients, requiring quotas and circuit breakers.
- **Container / Host**: The `mini-platform` demo uses `sys.path` to support both; production configuration specifies Server base URL or stdio command line.

### 24.2.3 JSON-RPC Message Semantics (Key Points for Reading Protocol Docs)

MCP is built on the **JSON-RPC 2.0** message model (Model Context Protocol 2024): complete messages include `jsonrpc: "2.0"`, an `id`, plus `method` / `params` or `result` / `error`. Beginners need not memorize all fields but should keep three main lines in mind:

1. **Discovery**: `tools/list` -> obtains tool array (names, descriptions, `inputSchema`).
2. **Execution**: `tools/call` -> passes `name` and `arguments` object.
3. **Lifecycle**: Protocol version and capability exchanged via `initialize` upon connection establishment. Production Client SDKs encapsulate this; this chapter references the (Model Context Protocol 2024) 2024-11-05 spec semantics, with remote transport based on Streamable HTTP (revision 2025-03-26).

`mini-platform`'s `McpDbServer.handle_jsonrpc()` **only simulates method/params dispatch**, returning business objects instead of the full JSON-RPC envelope and does not implement the `initialize` handshake. It is convenient for offline study against the official protocol, but not representative of production MCP message format.

### 24.2.4 Managing Multiple Clients Within a Host

A Host often connects to multiple Servers (databases, documents, ticketing). The platform should maintain a **Client pool** inside the Host. The table below lists four common points of attention:

*Table 24-5: Considerations and recommendations for managing multiple MCP Clients within a Host. Source: Compiled by this book.*

| Concern      | Recommendation                                  |
|--------------|-------------------------------------------------|
| Connection reuse | Cache Clients per Server instance to avoid handshake on every Tool Call |
| Tool name conflicts | Add prefixes when registering in Registry (e.g., `mcp_db_`, `mcp_docs_`) |
| Circuit breaking  | Temporarily remove from `tools/list` cache after continuous failures on a Server |
| Quotas           | Limit concurrent `tools/call` per tenant to avoid overloading shared Server |

---

## 24.3 Tools, Resources, and Prompts as capability categories

MCP defines Tools for execution, Resources for read-only data URIs, and Prompts for reusable prompt templates (Model Context Protocol 2024).

### 24.3.1 Tools

- Aligned with Chapter 23 Function Calling: have `name`, `description`, and `inputSchema`.
- Executed via `tools/call`, returning `content` (text/image, etc.) and optional `structuredContent` (Qu et al. 2025).
- **Enterprise default**: write-operation Tools require idempotency keys plus Policy approval (Chapter 30).

### 24.3.2 Resources

- Identified by URI pointing to read-only objects, e.g., `sales://report/2025Q1`.
- Client calls `resources/read` to pull snapshots, suitable for "known-path file read," but not for open semantic retrieval.
- Compared with Chapter 20 RAG: **RAG solves document search, Resource solves reading a specific version.**

### 24.3.3 Prompts

- Server exposes named prompt templates; Host can instantiate them with parameters.
- Platforms can integrate Prompts into **Prompt Template Management** (Chapter 8), binding them with Agent configurations to avoid conflicting maintenance between Server and Console.

Typical platform landing points for these three capabilities are as follows:

*Table 24-6: Purposes and platform landing points of Tools, Resources, and Prompts. Source: compiled by this book.*

| Capability | Typical Usage             | Platform Landing Point   |
|------------|--------------------------|-------------------------|
| Tools      | SQL, work orders, emails | Registry + Runtime      |
| Resources  | Policy PDFs, metric snapshots | Cache + permissioned URI |
| Prompts    | Standard analysis steps  | Prompt repository      |

This chapter's demo focuses on **Tools**; Resources/Prompts are marked as production extensions in the checklist ☐. **Key conclusion:** By default, only **Tools** are `register_mcp_tools`-ed into the Registry and invoked by the Runtime; **Resources** are better suited for Memory/RAG or permissioned URI reading; **Prompts** enter the Prompt template repository (Chapter 8) to avoid dual-source template maintenance with the Server.

Mixing these three capabilities later complicates governance. Treating Resources as Tools means even read-only document reads enter side effect audit chains, causing unnecessary approval; treating Tools as Resources risks bypassing action permissions and idempotency checks; leaving Prompts inside MCP Server makes it impossible for ops teams to view real template versions in the Console. Enterprises should assign each capability at onboarding: executable actions go to the Registry, read-only objects go to permissioned resource readers or RAG, prompt templates go to a unified Prompt repository.

### 24.3.4 Industry Scenario: How the Three Capabilities Cooperate to Answer a Query

When an Operations Director asks "Why did SKUs drop in East China?," the typical division of work is:

1. **Tools:** `query_sales` pulls structured sales data (this chapter's demo).
2. **Resources:** `policy://pricing/2025Q2` reads the current pricing policy PDF snapshot, letting the Planner check if "price drop caused it."
3. **Prompts:** Server exposes `monthly_sales_review` template to ensure the Reviewer Agent outputs fixed sections (summary, root cause, actions).

The typical platform landing points for the three capabilities are in the table above; the Planner aggregates results obtained via Tools / Resources / Prompts to answer. There is no need to put all three into the same MCP Server. The key is that the Host side unifies discovery and permission models, then merges into Registry or Memory (Prompts into the Prompt repository).

### 24.3.5 Trade-offs with "Direct HTTP Integration"

When integrating with existing systems, one can choose between direct HTTP or exposing via MCP Server. The following table compares four dimensions:

*Table 24-7: Multi-dimensional comparison between direct enterprise HTTP API and MCP Server exposure. Source: compiled by this book.*

| Dimension      | Direct Internal HTTP API    | Exposed via MCP Server       |
|----------------|----------------------------|------------------------------|
| Integration Cost | Each Agent writes client    | Single Server, reused by many Hosts |
| Contract        | OpenAPI / private            | MCP `inputSchema` + JSON-RPC (Hou et al. 2024) |
| Ecosystem       | No standard tool discovery  | `tools/list` auto-registration |
| Suitable for    | Highly customized, ultra-low latency internal calls | Cross-team, multi-tool, IDE/multi-Host reuse |

Enterprises should use MCP for **read-only data warehouse legacy** scenarios (broad reuse); retain gRPC direct calls for **millisecond trading risk control** scenarios that require ultra-low latency without MCP Server adaptation. This trade-off also applies to team boundaries. Cross-team sharing with standard discovery and IDE or multi-Host reuse suits MCP Server wrapped capabilities entered into Registry; only highly latency-sensitive internal calls with controlled interfaces should remain direct. Do not turn all HTTP APIs into MCP just because MCP is new, nor let each Agent maintain repeated clients just because direct is faster. Judgments should return to reuse scope, governance cost, latency budget, and audit requirements. A practical rule: first ask if this integration will be used by a second Host in the future. If no, MCP may not be worth it; if yes, standard discovery and unified registration typically quickly pay off the first version wrapping cost. This judgment should be recorded in the integration evaluation note to aid future retrospectives.

The review notes should also explain why direct integration is not used.

---

## 24.4 Enterprise integration for identity, networking, and auditing

When MCP enters enterprise production, the platform must answer who can connect, how traffic flows, and how the call can be audited afterward.

### 24.4.1 Identity and Tenancy

- The server must validate the caller's **tenant** and **scope** (passed exactly as in Chapter 22's `context`).
- It is not advisable to keep long-term keys as plaintext environment variables on the host; prioritize short-lived tokens with rotation (see Chapter 50).
- In multi-tenant scenarios, you can deploy isolated server instances per tenant or implement row-level isolation within one server, depending on data sensitivity.

### 24.4.2 Networking

- Public network MCP endpoints without authentication are forbidden in production.
- In Kubernetes, use Service + NetworkPolicy to restrict access so that only the Runtime namespace can reach `mcp-db`.
- For outbound proxy scenarios, configure JSON-RPC timeouts and maximum body size limits to prevent large results from overloading Runs (see Chapter 22 `tool_timeout`).

### 24.4.3 Auditing

- Each `tools/call` must write a **Tool Call Record**: `tool_call_id`, parameter summary, server instance ID, latency.
- MCP server logs and platform traces should be correlated by the same `run_id` (see Chapter 38).
- Compliance exports must demonstrate clearly "which Run called which table through MCP."

### 24.4.4 Server Aggregation and Splitting

There are trade-offs between aggregated servers versus splitting by tool. The table below offers a reference for architectural review:

*Table 24-8: Design Trade-offs for Different Approaches. Source: Compiled in this book.*

| Approach                       | Advantages           | Cost                       |
|-------------------------------|---------------------|----------------------------|
| One MCP Server per tool        | Small blast radius   | More operational instances |
| Aggregated server (multiple tools) | Simple operations    | Single point of failure impact |
| Register Tools only; Resources accessed via RAG | Clear architecture       | Two types of access coexist |

The Business Intelligence DataAgent uses an aggregated read-only DB server and a RAG document store side by side. This split keeps executable database access in Registry while leaving document retrieval to the retrieval system.

### 24.4.5 Compliance and Data Residency

Cross-border operations must clarify **where MCP server processes and data reside**: do parameters and results of `tools/call` cross borders, does the log contain PII? Even if the Host is domestic, an MCP server running in an overseas SaaS may trigger compliance reviews. The platform should mark **data domains** (e.g., `cn-north` / `eu`) when registering tools at L1; policies should reject cross-region calls accordingly.

Data residency also includes debugging traces. Many teams only check if business results cross borders, neglecting MCP Client logs, server access logs, error stacks, and trace sampling. A failed `tools/call` may write full parameters into error logs, including customer IDs, SQL conditions, or document URIs. Production integration must specify which fields can store raw text, which must be hashed or summarized, and which logs must remain in the same region. Otherwise, compliance risks may come not from normal calls but from troubleshooting and monitoring systems.

---

## 24.5 Integration of MCP Server with Tool Registry

The integration goal is straightforward: Runtime recognizes the Registry as the capability entry point, while MCP is one handler implementation source behind that entry point.

!!! warning "MCP does not replace the Registry"
    Production Runtime should not directly call the MCP Server. MCP tools must first be registered as ToolSpecs, then invoked via the Registry; auditing and version governance continue to follow the unified model described in Chapter 22 and Chapter 23.

### 24.5.1 Integration Steps

1. **Discovery**: Client calls `tools/list` to fetch the Server's tool catalog.
2. **Mapping**: Generate a platform-unique `name` for each MCP tool (prefix `mcp_db_` is recommended to avoid conflicts).
3. **Registration**: Use MCP `inputSchema` as the `parameters_schema`; the handler internally calls `client.call_tool`.
4. **Health Check**: Level 1 periodically calls `tools/list` or ping; on failure, remove the tool from the Agent tool view and raise an alert.
5. **Execution**: Runtime calls `registry.invoke` -> handler -> MCP Client -> Server.

Reference implementation: `register_mcp_tools()` in `tools/mcp_db/registry_bridge.py`. The demo handler only returns MCP `structuredContent` for use by `invoke`; production should preserve the full mapping of `content` and `structuredContent` for tracing and frontend display.

![Figure 24-1: MCP -> Registry Bridge Closed Loop](../../images/part5/en/p5-05-mcp-registry-bridge.png)

*Figure 24-1: MCP -> Registry Bridge Closed Loop. Source: drawn by this book. Alt text: Tools exposed by the external MCP Server are first registered, risk-leveled, and access-controlled by the enterprise Registry before being available for Runtime invocation. The invocation results flow back for auditing, forming a closed governance loop.*

### 24.5.2 Error Handling

*Table 24-9: Platform-side handling of various MCP error scenarios. Source: compiled by this book.*

| Scenario                            | Platform-side Handling                                                                                      |
|-----------------------------------|------------------------------------------------------------------------------------------------------------|
| Server unreachable / transport timeout | Registry handler wraps error as `TOOL_UNAVAILABLE` (defined in `core/registry/errors.py`; demo in-process Server rarely triggers); Runtime handles retries using the strategy from Chapter 22 |
| MCP returns business error        | Write error details into Tool Call's `error.details`; Runtime decides whether to propagate the error to the Planner |
| `inputSchema` inconsistent with Server actual parameters | Detected during CI registration or health check; changes require Registry version upgrade                   |

The important point is to preserve error classes. `TOOL_ARGUMENT_INVALID` means Planner may still fix parameters. `TOOL_UNAVAILABLE` means a downstream service is temporarily unavailable and should follow retry or circuit-break behavior. Permission denial should not be fed back to the model as another chance to guess; it should end the action or enter human review. MCP Server business errors also need to keep their original classification so Runtime does not infer behavior from raw strings.

### 24.5.3 Version Migration and Canary Integration

Once an MCP Server enters the enterprise platform, it becomes a shared published capability instead of a private tool process. Server-side changes to `inputSchema`, return structure, authentication, or resource URI semantics may affect ToolSpecs already registered in Registry. The platform should not assume that every fresh `tools/list` response is backward compatible. A safer pattern snapshots discovered MCP tools into platform versions, tests them in shadow mode, and then makes them visible to production Agents.

Canary integration usually has four steps. First, the Client fetches `tools/list` and generates candidate ToolSpecs without exposing them to Planner. Second, static checks review name, description, input schema, return structure, risk level, tenant scope, and Server identity. Third, replay or synthetic samples call the new Server and compare results with the old version while only writing Trace. Fourth, the new version is published into Registry and gradually enabled by Agent, tenant, or business line.

This process may look slower than directly connecting to an MCP Server, but it protects production stability. Many incidents are semantic instead of total outages: `customer_id` becomes `account_id`, amount units change from yuan to cents, error codes change from strings to objects, or the default query scope moves from tenant-only to global. If those changes reach Planner directly, the model may keep producing plausible actions while Trace can no longer explain why the same user question behaved differently across two days.

The integration review should record three versions. `server_version` describes what the capability provider released. `tool_spec_version` describes what the platform registered. `registry_version` describes what a specific Agent can actually see. They do not need to change at the same time, but they must be traceable to one another. Rollback should normally change Registry visibility instead of asking the Server team to revert code immediately.

### 24.5.4 Failure Recovery and Degradation Strategy

MCP failures should not all be handed to Planner as generic tool failures. At minimum, the platform should separate connection failures, protocol failures, business failures, and policy failures. Connection failures include unreachable Server, exhausted connection pool, and gateway timeout. Protocol failures include invalid JSON-RPC envelope, schema mismatch, and missing fields in the return structure. Business failures include downstream database errors, missing files, or empty query results. Policy failures include tenant mismatch, missing scope, or disallowed risk level.

These categories map to different actions. Connection failures can retry, switch replicas, or circuit-break the Server. Protocol failures usually should not retry; the new version should be removed and alerted. Business failures can be returned to Planner so it can adjust parameters or end the task. Policy failures must stop the action and may enter the Chapter 30 approval or rejection path. A single "tool failed" response invites Planner to retry permission denials and protocol incompatibilities, increasing both cost and risk.

User-visible degradation also needs a design. If a read-only query MCP Server is unavailable, the system can state that the data tool is temporarily unavailable and preserve the request for retry. If a document Resource cannot be read, the answer can degrade to cached evidence while clearly marking incomplete evidence. If a high-risk write tool fails, the platform should not silently switch to another write path. It should stop at a reviewable state. MCP provides a standard access protocol; production reliability comes from the deterministic behavior after access fails.

---

## 24.6 Practical Project: MCP Database Tool

The MCP implementation is located in `tools/mcp_db/`; `build_workflow_registry()` registers it as **`mcp_db_query_sales@v1`** via `register_mcp_tools()`. During the Data Agent stage, it is invoked through RunLoop -> Registry `invoke`. The **standalone unit tests** bridging the MCP protocol and Registry are in `tests/test_mcp_db.py`.

### 24.6.1 Runtime Environment

- **Python**: ≥ 3.11 (see `mini-platform/pyproject.toml`)
- **Run the practical project**: `python3 projects/multi-agent-workflow/run.py start` (SSE includes `"tool": "mcp_db_query_sales"`)
- **MCP unit tests**: `pytest tests/test_mcp_db.py -q` (covers `tools/list`, `tools/call`, Registry registration and `invoke`)

### 24.6.2 Implementation Path in mini-platform

```
mini-platform/tools/mcp_db/
├── __init__.py
├── server.py           # McpDbServer: tools/list, tools/call
├── client.py           # McpDbClient: in-process JSON-RPC
└── registry_bridge.py  # register_mcp_tools -> ToolRegistry

projects/multi-agent-workflow/lib/
└── registry_setup.py   # register_mcp_tools(...) inside build_workflow_registry()

projects/multi-agent-workflow/
├── run.py              # Data Agent stage triggers MCP Tool Call
└── README.md

tests/test_mcp_db.py    # MCP + Registry unit tests
```

`server.py` simulates the MCP read-only database tool `query_sales`; in the practical project, it is invoked uniformly via Registry during the Data Agent stage, consistent with the event model in Chapter 22.

### 24.6.3 Executable Code and Configuration

**Run the practical project** (observe the MCP tool called within the full Handoff chain):

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py start
```

The SSE output includes Data Agent `action` / `result` events for `mcp_db_query_sales`. **MCP Protocol and Registry Unit Tests**:

```bash
pytest tests/test_mcp_db.py -q
```

After registration, the platform tool is named **`mcp_db_query_sales@v1`**, coexisting with the built-in `sql_executor` for versioning and audit differentiation.

### 24.6.4 MCP Bridge Demo Scope and Future Evolution

*Table 24-10: Coverage of MCP Capabilities in this chapter's Demo. Source: Compiled by the author.*

| Capability                        | Description             | This Chapter's Demo |
|---------------------------------|-------------------------|--------------------|
| MCP Server tools/list & call     | `server.py`             | ✓ (in-process)      |
| MCP Client                      | `client.py`             | ✓                  |
| Registry Bridge Registration     | `registry_bridge.py`    | ✓                  |
| MCP invoke in Practical Project  | `multi-agent-workflow/run.py` | ✓            |
| MCP + Registry Unit Tests        | `tests/test_mcp_db.py`  | ✓                  |
| `TOOL_UNAVAILABLE` end-to-end (transport timeout) | Remote MCP + circuit breaker | ☐           |
| In-process MCP + Practical Run chain | `test_mcp_db.py` + `multi-agent-workflow/run.py` | ✓ |
| stdio / Streamable HTTP Remote Transport | Official SDK transport layer | ☐           |
| Resources / Prompts              | Full MCP capabilities   | ☐                  |
| Health Check and Removal        | L1 liveness probe       | ☐                  |
| Tenant Authentication and Network Policy | §4               | ☐                  |
| Second Server for mcp_docs      | `tools/mcp_docs/`       | ☐                  |

The demo is intentionally a minimal bridge. It proves that a protocol tool can be discovered, registered into Tool Registry, invoked through Runtime, and tested independently. It does not implement remote stdio or Streamable HTTP transport, full `TOOL_UNAVAILABLE` circuit breaking after transport timeout, Resources and Prompts, automatic health removal, tenant authentication, network policy, or a second `mcp_docs` Server. Production expansion should add remote transport, health checks, circuit breaking, and tenant isolation before adding more MCP capabilities. Otherwise the problem shifts from "can the Server be called" to "can the failure be located, can permission be explained, and can cost be attributed."

### 24.6.5 Four Failure Points After MCP Integration

#### Bypassing Registry and Connecting Directly to MCP

Symptom: Runtime directly JSON-RPC in the Run main loop, causing tool version and audit divergence.
Fix: Always `register_mcp_tools` first and only `invoke` thereafter.

#### MCP Tool Name Conflicts with Built-in Tools

Symptom: `query_sales` conflicts with an old handler of the same name, overwriting registration.
Fix: Prefix platform tool names with `mcp_db_` or use tenant namespaces.

#### inputSchema and Server Validation Mismatch

Symptom: Registry validation passes but Server rejects the request.
Fix: Use CI to compare both schemas; bump version on changes.

#### Stale stdio Server Processes Inside Containers

Symptom: Pod restart leaves old subprocess occupying port.
Fix: Host manages subprocess lifecycle or switch to Streamable HTTP remote Server.

### 24.6.6 Runtime Troubleshooting

*Table 24-11: MCP Runtime Failure Phenomena, Possible Causes, and Diagnosis Methods. Source: Compiled by the author.*

| Phenomenon                         | Possible Cause                  | Diagnosis                              |
|-----------------------------------|-------------------------------|---------------------------------------|
| `ValueError: region and tenant_id are required` | Mandatory MCP call parameters missing | Compare `inputSchema` and Registry schema |
| `KeyError: unknown tool`           | Tool name incorrect or Server not exposed | Run `tools/list` to verify names     |
| `ValueError: unsupported method`  | Client called unimplemented JSON-RPC method | Check `handle_jsonrpc` against spec  |
| Registry `TOOL_NOT_FOUND`           | Not registered or version/agent config mistake | Confirm `register_mcp_tools` execution |
| Production Server timeout (`TOOL_UNAVAILABLE`) | Network issues, circuit breaker, Server down | Check MCP Client logs + Chapter 22 retry policy |

---

Enterprise MCP integration starts by keeping Host, Client, and Server responsibilities separate. Host owns the user session and model orchestration, Client owns protocol communication, and Server exposes tools or resources. Identity, permission, and audit cannot be scattered across those roles; the platform needs one policy path that every MCP-backed tool follows.

The Server lifecycle also needs ownership. Who publishes it, who upgrades it, who removes it, how compatibility is tested, and how failures degrade should be written into the Registry or delivery process. If an external Server changes interface behavior, the model may still generate a valid call, but the execution result may have changed. MCP reduces integration cost. The enterprise platform still has to provide the control plane.

Deployment location changes the security model. A Server running on a developer laptop, inside a business network, in the platform cluster, or in a vendor environment has different identity, network, and audit requirements. Production Agents should not connect directly to personal MCP Servers, and external Servers should not hold long-lived high-privilege credentials. The same standard applies to Resources. A Resource may look like context, but once sent to a model it affects reasoning and can leak sensitive information. Platform integration should record which Resources entered context and apply the same data-classification rules used by retrieval and evidence systems.

MCP integration also needs naming, credentials, audit, and isolation rules. Different teams may all expose `query_database`, `search_docs`, or `send_message`; Registry should assign enterprise tool names and versions so Planner selection remains stable. Server credentials should come from enterprise secret management, short-lived tokens, service identity, and rotation policies, not from long-lived local configuration. Audit logs need to cross the protocol boundary: Host should record `run_id` and `tool_call_id`, Client should record request and transport status, Server should record backend execution result. None of the three views is enough on its own.

Production deployment should separate development, staging, and production. Developers can use simulated data and low-permission accounts. Staging should use masked data and restricted tools. Production connects to real systems under managed network policy. Resource responses need size and type limits as well. A Resource that returns a full schema, a large log file, or an unbounded document can expand context quickly and bypass data classification. The adapter layer should limit fields, media types, and payload size, and convert large objects into artifact references.

## 24.7 MCP Server Admission Review

After an MCP Server enters the production catalog, it needs periodic review. The review checks whether the tool still has an owner, whether schema stays aligned with Registry, whether credentials rotate on schedule, whether health checks are stable, whether error codes still map to Runtime recovery, and whether Resource responses follow size and permission limits. External Servers also need dependency review, supply-chain review, and network-scope review. If a Server has no active users, it can be frozen and then retired. If several Agents depend on it, the platform should add release windows and rollback plans. MCP makes tool onboarding fast; review keeps that speed from turning into unmanaged production risk.

## 24.8 Failure-Recovery Boundaries For Protocol Interoperability

After MCP enters an enterprise platform, failure recovery needs to cover the protocol layer, tool layer, and governance layer. The protocol layer can face disconnection, incompatible Server versions, schema parsing failure, or expired resource URIs. The tool layer can face timeout, permission denial, downstream rate limits, or changed return structures. The governance layer can face expired credentials, unapproved Server versions, or missing audit fields. If all of these cases are reduced to "tool call failed," the Runtime cannot decide whether to retry, degrade, switch Server, or suspend the task for human handling.

The platform should define standard error classes for MCP Servers. Connection errors may allow short retry. Schema errors should block execution and notify the Server owner. Permission errors should guide the user toward access request or another path. Downstream rate limits should go through gateway and queue policy. Missing audit fields should stop high-risk actions. Error classes also belong in Trace. After an Agent Run fails on an MCP tool, the review material should show whether the failure happened in Host, Client, Server, network, credential, tool implementation, or downstream system. Without that breakdown, MCP pushes ecosystem complexity into the Agent dialogue.

Protocol interoperability also needs platform boundaries. MCP can lower integration cost, while the enterprise platform still owns identity, permission, audit, admission, and rollback. A Server should not decide which tenants can see it, which fields can be returned, or which write operations can execute. These decisions should come from Tool Registry, Policy Engine, and Runtime. MCP Server owners are responsible for capability implementation and version notes. Platform teams are responsible for admission, routing, credentials, and audit. With these boundaries, MCP becomes an integration mechanism for a tool ecosystem without bypassing enterprise Agent governance.

## 24.9 Vendor And Community Risk In The MCP Ecosystem

MCP speeds up tool integration and also brings vendor and community risk into the platform. A community Server may move quickly but lack maintenance commitment. A vendor Server may be feature complete but fail enterprise audit requirements for logs, credentials, or network access. An internal team may write a Server that solves the current problem but lacks versioning, tests, and an owner. The platform should check whether a Server can remain in the production catalog after the first successful run.

Admission material should include code source, dependency list, maintenance team, version strategy, network egress, credential method, log fields, error codes, and rollback method. External Servers should be checked for uncontrolled data transfer, sensitive-field logging, and whether the enterprise can pin a version. Internal Servers should have test samples, release records, and on-call ownership. If these materials are missing, the Server may enter experimentation but should not enter production Agents.

Ecosystem governance should also support replacement. When a Server retires, a vendor changes terms, or a community project stops maintenance, the platform should know which Agents are affected, which ToolSpecs can switch to another implementation, and which tasks need degradation. MCP opens the tool ecosystem. The enterprise platform makes that ecosystem auditable, replaceable, and rollbackable.

## 24.10 Runtime review of MCP tool catalogs

After MCP Servers are connected, the tool catalog needs periodic review. Tool names, parameter schemas, resource URIs, authentication methods, permission scope, and returned fields all change as external systems change. If the catalog is not reviewed, an Agent may keep calling an interface that has changed, or send old parameters to a new service. MCP is useful because it unifies protocol access, but that same entry point exposes several external systems to the model.

Review should use real call records. The platform should inspect which MCP tools are called often, which time out, which return oversized fields, which are rejected by policy, and which create permission disputes. A rarely used high-permission tool may no longer deserve exposure. A frequently used tool with a high failure rate may need schema, error-code, or retry fixes. A tool returning sensitive fields may need references or controlled views. The review is not a count of tools; it is a judgment about whether each tool remains suitable for Agent use.

A first version can produce a monthly MCP runtime summary: call volume, failure reason, permission denial, average latency, return size, owner, and last change time. The summary should enter Tool Registry review and connect to tool governance in Chapter 23, human approval in Chapter 30, and Trace in Chapter 38. MCP integration then moves from connectivity to platform governance.

## 24.11 Canary release and withdrawal for MCP integration

MCP Server integration should support canary and withdrawal. A Server that passes `tools/list` and one `tools/call` has not yet proved that it belongs in production Agents. Before canary, the platform should confirm Server owner, version, authentication method, network location, log fields, error classes, and data domain. The tool can then be registered as a production candidate and exposed only to internal tenants, low-risk tasks, or read-only scenarios. During canary, the platform should watch connection failures, schema mismatch, oversized returns, permission denial, unmapped error codes, and user disputes about results. If these problems cluster, Registry visibility should be withdrawn; the Planner should not be asked to avoid the tool through dialogue alone.

Withdrawal should preserve task evidence. Runtime decides whether already started Runs continue, move to human handling, or return a retryable state. Registry only closes the entry point for new calls. Trace should record withdrawal reason, affected tool version, affected Agents, and replacement path. If the MCP Server provides read-only query, the system may degrade to cache or ask the user to retry later. If it provides a write operation, withdrawal should not switch to an unapproved backup path. With clear canary and withdrawal rules, MCP can be released as a platform capability instead of a temporary external connection.

This release discipline also helps ecosystem governance. External Servers, vendor Servers, and internal team Servers change at different speeds, and the platform cannot assume they follow the same release standard. Registry-level canary, freeze, withdrawal, and replacement paths translate external changes into manageable platform states. MCP keeps its standard access advantage without passing external release risk directly into user tasks.

## 24.12 Replacement paths for MCP tool degradation

After an MCP tool enters production, degradation does not always come from protocol errors. The Server may still respond and the schema may remain unchanged, while downstream rate limits, narrower credentials, vendor API changes, or reduced resource fields lower result quality. Planner still sees the same tool name, and users see a weaker task result. If the platform monitors only connection success, it misses this type of degradation.

Replacement paths should be designed during integration. A read-only query tool can degrade to cache, static reports, or manual lookup. A write tool can move to HITL or pause execution. A resource reader can return an artifact reference and delayed-refresh state. An external vendor tool can switch to an internal Server or be limited to low-risk tenants. The model should not invent these paths during a dialogue. They should live in Registry capability metadata and Runtime recovery policy, so the system knows whether to continue, degrade, suspend, or refuse.

Degradation review should inspect business impact. A low-frequency tool failure may affect only a few tasks. A high-permission write tool can create wrong actions or approval backlog. The platform should record degradation window, affected Agents, replacement path, unfinished Runs, user-visible message, and repair action. If degradation comes from a vendor or community Server, review should decide whether to pin a version, replace the implementation, or tighten admission.

A first version can add two fields to each production MCP tool: `degradation_mode` and `replacement_path`. The first describes allowed degradation. The second describes replacement capability, manual handling, or pause policy. These fields are small, but they move MCP tools from callable integrations to recoverable platform capabilities, aligned with Runtime in Chapter 22, HITL in Chapter 30, and Trace in Chapter 38.

## 24.13 Tenant-level admission policy for MCP servers

After an MCP Server enters the enterprise platform, admission should not be judged only at the Server level. One Server may expose several tools, resources, and prompts. Some capabilities fit all tenants, some fit only certain business domains, and some require approval. If the platform adds the whole Server to the default candidate set, Planner may select it for the wrong tenant or task, creating permission, cost, or data-egress risk.

Tenant-level admission should inspect Server capabilities separately. Each capability should state applicable tenants, identity mapping, accessible resources, network boundary, call budget, audit fields, and disable condition. Read-only resources can be opened more broadly. Write actions, external APIs, and data export should be limited by tenant, role, and approval policy. MCP Client should fetch tenant-visible capabilities from Registry before invocation, instead of trusting the Server declaration directly.

Admission policy also needs fast withdrawal. If one tenant finds that a Server returns fields outside authorization, the platform should withdraw that tool for the tenant without shutting down the whole Server. If a vendor endpoint becomes unstable, the platform should reduce weight or remove the capability from candidates. Withdrawal should write to Trace and the tool catalog, so Planner knows why the capability is unavailable.

A first version can maintain tenant-level allowlists for MCP capabilities. The allowlist can stay simple, but it should include tenant, capability, permission, budget, owner, and review time. MCP integration then fits enterprise multi-tenancy and stays consistent with Chapter 45 gateway governance and Chapter 23 Tool Registry.

## 24.14 Tenant-level admission for MCP servers

MCP exposes external tools, resources, and prompt templates to the Agent platform, and it also brings external-system risk into the runtime path. When an enterprise connects an MCP Server, it should verify more than protocol connectivity. Admission should happen at tenant level. Different tenants can have different data boundaries, tool permissions, audit requirements, and network policies. The same MCP Server may expose read-only resources to one tenant, be blocked for another, or allow only approved tool calls.

Admission material should include capability list, data domain, authentication method, callable tools, resource types, returned-content structure, audit fields, error semantics, and owner. The platform turns this material into ToolSpec, Policy Engine rules, and Trace fields. If an MCP Server can return only unstructured text or cannot explain tool side effects, it is not suitable for high-risk production tools. Protocol compatibility is only the first step. Platform admission asks whether the server can be governed.

A first version can classify MCP Servers into three groups: development and debugging, internal read-only, and production write. Development servers stay in sandboxes. Internal read-only servers need identity, audit, and resource scope. Production write servers need idempotency, compensation, approval, and sample replay. MCP can then enter the enterprise ecosystem without bypassing the tool registry in Chapter 23 or the security boundary in Chapter 50.

## 24.15 Operating responsibility after MCP integration

After MCP integration reaches production, a successful demo is not enough evidence. The platform needs stable fields for server owner, tool permission, call log, version change, failure receipt, and replacement path, and those fields should connect to release records, Trace, evaluation samples, and incident notes. When a production issue appears, teams can follow one set of facts to understand scope, ownership, and repair order instead of stitching together model logs, business logs, and verbal explanations.

This evidence also connects the surrounding chapters. It links to Chapter 23 on tool registration, Chapter 29 on protocol interoperability, and Chapter 50 on security: upstream capabilities provide assumptions, downstream capabilities consume the result, and governance capabilities preserve evidence and review decisions. If these materials do not share identifiers and versions, the production system splits apart. Business owners see user complaints, platform owners see system errors, and security or compliance teams see explanations written after the fact. That separation makes it hard to decide whether the issue came from data, model behavior, tool contracts, workflow state, or organizational ownership.

Common production risks include servers having no maintainer after integration, tool schema changes not notifying the platform, and external tool failures lacking degradation paths. These risks are less visible during demos because demos usually exercise the successful path. Production users bring boundary cases, repeated requests, permission changes, and long-running state. The platform team should turn such failures into release samples. Some samples should block launch, some can be handled by degradation, and some require the business owner to accept the remaining risk with a review date.

After MCP capability enters the platform, it should be managed as a production tool with a real owner, version policy, and fallback path. The record can stay compact, but it should include time, version, owner, sample, action, and the next review condition. Without those fields, review remains informal experience. With them, one production issue can become material for later releases, evaluation suites, and training.

A first platform version can start with a small set of high-risk paths. Choose flows with high traffic, high business impact, or sensitive data, require an evidence package for each change, and then expand the practice to ordinary scenarios. This keeps the capability at the engineering level: runnable, explainable, and recoverable.
## Chapter Recap

1. **MCP is an L3 protocol**, with the Registry serving as the L2 capability hub; the integration flow is **discover -> register -> invoke**.
2. **Tools / Resources / Prompts** have distinct roles; in enterprise Q&A scenarios, Tools are primarily used while Resources supplement by reading known URIs.
3. **Production integration** requires completing identity, network, and auditing aspects, as the protocol itself does not include enterprise IAM.
4. The **demo** uses in-process Server/Client to clarify semantics; production replaces this with stdio / Streamable HTTP and a read-only real database account.

- Are all MCP tools registered via the Registry with version numbers?
- Does the Server enforce isolation parameters like `tenant_id`?
- Is there health checking and a `TOOL_UNAVAILABLE` retry strategy?
- Can tracing correlate `run_id` with MCP Server instances?

- [Chapter 23 Tool Registry](ch23-tool-registry-function-calling.md)
- [Chapter 29 Agent Protocols and Standards](ch29-agent.md)
- [Chapter 20 RAG Engineering](../../part04-vector-knowledge/en/ch20-rag.md)
- `mini-platform/projects/multi-agent-workflow/README.md`
- `mini-platform/tests/test_mcp_db.py`

---

## References

Anthropic. (2024). *Introducing the Model Context Protocol*. [https://www.anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol) Model Context Protocol. (2024). *Specification* (2024-11-05). [https://modelcontextprotocol.io/specification/2024-11-05](https://modelcontextprotocol.io/specification/2024-11-05) Model Context Protocol. (n.d.). *Architecture overview*. [https://modelcontextprotocol.io/docs/concepts/architecture](https://modelcontextprotocol.io/docs/concepts/architecture) Qu, C., et al. (2025). Tool learning with large language models: A survey. *Frontiers of Computer Science*, 19(8), 198343. [https://doi.org/10.1007/s11704-024-40678-2](https://doi.org/10.1007/s11704-024-40678-2) Hou, X., et al. (2024). Large language models for software engineering: A systematic literature review. arXiv:2404.06393. [https://arxiv.org/abs/2404.06393](https://arxiv.org/abs/2404.06393) (Discussion on tool integration and enterprise boundaries) Google. (2024). *Agent2Agent (A2A) protocol* (Preview of interoperability direction, to be read in comparison with MCP). [https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
