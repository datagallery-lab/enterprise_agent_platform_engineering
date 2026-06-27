# Chapter 25 Planner and Orchestration Patterns

---

Planner is the decision interface of the Agent Runtime. It reads the user task, tenant context, visible tool set, run history, tool results, and Memory fragments, then proposes what to do next. It does not execute tools. Runtime advances Run state, calls Registry, pushes events, writes checkpoints, and chooses recovery paths. This boundary looks simple, but it determines whether an Agent remains controllable.

Chapter 22 explained how Runtime drives a Run forward. Chapter 23 explained how tools are registered as ToolSpecs. One role is still missing: at each Step, who reads the current context and decides which tool to call next, or whether the task can end? In a DataAgent task, the user asks which SKUs declined in East China last week. Runtime manages state. Registry manages tool definitions and invocation. Planner decides whether to look up region codes first, directly query sales detail, adjust SQL after a failure, switch to semantic-layer tools, or finish with an answer.

If planning and execution are both hardcoded inside RunLoop, every business Agent duplicates prompts, tool selection, and error recovery logic. When one version upgrades, behavior drifts across applications. A more stable design lets Planner return structured decisions only, while Runtime decides whether to execute, how to execute, how to log, and how to recover.

This separation also improves troubleshooting. If SQL parameters are wrong, first inspect the Planner output. If a tool refuses execution, inspect Registry schema and Policy. If a task waits for approval, inspect Runtime state and callbacks. Without this boundary, all failures get blamed on model instability. Planner mode choices such as ReAct, Plan-and-Execute, and state graphs should serve these responsibility boundaries instead of act as an algorithm showcase.

---

## 25.1 Planner Responsibility Boundaries

### 25.1.1 Planner Decides the Next Step

The Planner receives input from three sources: the user task and tenant context, the tool view provided by the Registry, and history stored by the Runtime and Memory. Its output should be a small, explicit decision object, not a direct tool invocation.

*Table 25-1: Planner Inputs and Outputs. Source: Author compilation.*

| Category | Content | Description |
|---|---|---|
| Input | `input`, `context`, `step_index` | From `/run` request and RunContext |
| Input | tools schema, tool version | From Tool Registry |
| Input | Tool Call results, errors, Memory snippets | From Runtime checkpoints and Memory |
| Output | `finish`, `answer` | Planner believes the task can be completed |
| Output | `tool`, `version`, `args` | Planner proposes a Tool Call |

The tool view should not be imported directly by the Planner from handlers. The schema the Planner sees must be the same source as the schema validated by the Registry before execution; otherwise, the model might see one set of fields while the executor validates another, making errors difficult to reproduce.

Planner inputs should also be scoped carefully. Feeding the model the full set of tools, entire conversation history, and all document fragments may seem comprehensive but actually reduces the stability of tool selection. The Runtime and Memory should give the Planner only the minimal necessary context for the current Run. The tool list should be trimmed by tenant, permissions, and workflow state.

For example, a business analysis Agent may register tools for SQL, charting, email, tickets, and knowledge base. When the user simply asks why sales declined in East China, the Planner should not be shown email sending or ticket creation tools yet. Once a report draft is generated and enters the publishing workflow, the Runtime can open publishing tools based on state and Policy to decide if HITL applies. Changing the tools available with state changes is far more reliable than repeatedly telling the model in the prompt to avoid sending emails.

### 25.1.2 PlannerDecision as a Handshake Structure

The platform can represent a single-step decision with the `PlannerDecision` structure.

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class PlannerDecision:
    finish: bool
    answer: str | None = None
    tool: str | None = None
    version: str | None = None
    args: dict[str, Any] | None = None
```

`finish=True` only means the Planner believes the task can end. The Runtime must still confirm there are no unfinished Tool Calls before triggering `done` and entering the `succeeded` state. The `tool` and `args` are only proposals. Runtime must first perform Policy, schema, idempotency, and timeout checks, then execute via Registry.

### 25.1.3 Separation of Proposal and Execution

Separating proposal and execution offers three benefits. First, side effects occur only in the Runtime's `action` / `result` events, ensuring a complete audit trail. Second, tool errors can be returned as Observations back to the Planner so it can revise the next step instead of outright failing. Third, the Planner logic can be replaced without rewriting Runtime state machine, SSE, checkpoints, or tool governance.

Common mistakes include letting the Planner directly call SQL or HTTP tools. This bypasses Registry versioning, permission checks, and error classification, causing trace gaps where results appear without a matching `action` event. Another mistake is to treat the Planner as business application code with if/else conditions scattered across Agents. The Planner should provide reusable orchestration patterns; business differences should be expressed via Agent config, tool whitelists, and prompt templates.

An even subtler error occurs when the Planner describes tool constraints in prompts, but the Runtime lacks hard validation. Models tend to obey constraints until an edge case breaks them. Production systems should never rely on expected model behavior as a safety boundary. Constraints must be enforced in Registry, Policy, and Runtime execution paths.

---

## 25.2 ReAct: Acting While Observing

### 25.2.1 Suitable for Exploratory Tasks

ReAct interleaves reasoning and actions: the model first determines the next action, the Runtime executes the tool, then the tool's output is fed back as an observation to the Planner. The ReAct paradigm proposed by Yao et al. emphasizes a loop of Thought, Action, and Observation (Yao et al. 2023). In enterprise platforms, the Thought is not necessarily exposed to users, Action should materialize as a Tool Call, and Observation must come from real tool outputs or structured error messages.

Operational inquiry questions usually fit ReAct well. User questions are often not fully clear at the outset, so the Planner needs to check and adjust step-by-step: first confirm the regional scope, then query SKU rankings, then decide whether to query inventory or gross margin based on results. The path cannot be fully hardcoded in advance, so the iterative feedback of ReAct feels more natural than a fixed one-shot plan.

### 25.2.2 Single-Turn Mechanism

Each ReAct iteration's `next_step()` roughly involves five steps:

1. The Runtime passes the user query, historical Tool Calls, Memory fragments, and available tools to the Planner.
2. The Planner calls the model via Gateway, providing the tools schema.
3. The model returns either a tool call intent or a final answer.
4. The Planner parses the response into a `PlannerDecision`.
5. The Runtime follows the decision to execute tools, invoke human approval, continue to the next step, or finish.

If the Registry returns `TOOL_ARGUMENT_INVALID`, the Runtime should not fail immediately. Instead, it can record the error in `result` and call the Planner again to generate new parameters. Conversely, if the Runtime detects the same tool call with identical parameters repeating, it should trigger loop protection instead of letting the Planner keep trying.

### 25.2.3 Advantages and Costs

*Table 25-2: ReAct advantages and costs. Source: Compiled by the book.*

| Dimension       | Advantages                                     | Costs                              |
|-----------------|-----------------------------------------------|-----------------------------------|
| Task Fit        | Suitable for exploratory, multi-hop, incomplete information tasks | Number of steps unpredictable      |
| Cost            | Each step solves a local subproblem           | Multi-step accumulates latency and token usage |
| Observability   | Tool Call trace explains task path             | Thought drafts should not be exposed directly |
| Recovery        | Single-step errors can be locally corrected    | Requires `max_steps` and loop detection           |

The key to ReAct is bounded freedom inside the Runtime. Tools come from the Registry, actions are executed by the Runtime, results are saved to checkpoints, and errors are classified by error code. Without these boundaries, ReAct quickly turns into uncontrollable loops. In practice, the most common failure of ReAct is repeatedly fixing the same error. For example, the model generates the same SQL missing tenant filters three times, differing only in spacing or field order. The Runtime should normalize tool parameters and summarize them, stopping after hitting a repetition threshold instead of burning tokens endlessly. Another common failure is verbal completion: the model produces a summary before the last tool call has returned. The final state must still be decided by the Runtime.

Another failure source comes from incomplete observation information. The Planner might see that SQL returned an empty set and conclude that sales did not decline. The same empty set could also indicate a wrong table, incorrect date filter, or overly strict permission filter. The Runtime can feed back tool errors and data quality signals together to the Planner, for example: query succeeded, result is empty, and the filter includes newly launched channel fields. The more structured the Observation, the easier it is for the Planner to fix issues.

---

## 25.3 Plan-and-Execute: Plan First, Then Execute

### 25.3.1 Suitable for Tasks Requiring Pre-Audit

Plan-and-Execute generates a plan first, then executes it step by step. It is suitable for tasks with strong compliance requirements, relatively clear workflows, and that require pre-execution auditing. For example, a financial closing assistant must first specify which tables will be checked, what filters will be applied, and what reports will be generated before running queries; only after the approver approves the plan will the runtime allow execution. The plan itself is an artifact. It can enter checkpoints, approval workflows, and audit exports. After approval, the Planner outputs `PlannerDecision` step by step according to the `plan_cursor`. The runtime still executes tools according to the rules explained in Chapter 22.

### 25.3.2 Two-Stage Mechanism

The Plan stage should not execute any tools. The Planner only generates a structured plan based on the task, tool summaries, and policies.

```json
{
  "steps": [
    {"id": 1, "goal": "Parse East China region_code", "tool_hint": "sql_executor"},
    {"id": 2, "goal": "Query SKU sales ranking", "tool_hint": "sql_executor"},
    {"id": 3, "goal": "Summarize natural language answer", "tool_hint": null}
  ]
}
```

The Execute stage generates tool call proposals step by step based on the plan. If an Observation invalidates a planning assumption, e.g., the region code does not exist, the Planner can Replan, but the Replan must also be recorded in the `planner_output` for auditing purposes.

![Figure 25-1: Plan-and-Execute Flow](../../images/part5/en/p5-06-plan-and-execute.png)

*Figure 25-1: Plan-and-Execute flow. Source: drawn by the author. Alt text: The process starts with the Planner generating a multi-step plan, then executing step-by-step; if errors or invalid assumptions occur, it goes back to replanning. Arrows illustrate the difference between planning before execution and the ReAct approach that thinks and acts simultaneously.*

### 25.3.3 Trade-offs Between ReAct and Plan-and-Execute

*Table 25-3: Trade-offs between ReAct and Plan-and-Execute. Source: compiled by the author.*

| Dimension         | ReAct                        | Plan-and-Execute                           |
|-------------------|------------------------------|-------------------------------------------|
| Plan Visibility   | Scattered across each Step    | Generates full plan first                  |
| Human Approval   | Usually tool or artifact-based | Plan is approved upfront                   |
| Task Type          | Exploratory data queries, multi-hop unknowns | Clear paths, strong compliance, pre-audit needed |
| Risk                  | May detour or loop               | Planning errors affect subsequent steps    |
| Default Recommendation | Data exploration & general agents | Finance, legal, cross-system high-risk tasks |

Plan-and-Execute should not be treated as the default advanced option. For exploratory tasks, it may generate a seemingly complete but soon outdated plan and require frequent replanning, raising costs. For tasks requiring pre-execution auditing, it is highly valuable, since the plan can be reviewed by people and systems beforehand.

Plans also need versioning and schemas. Free-text plans are prone to misinterpretation during execution. For example, a request to query key SKUs could mean sorting by revenue, sales volume, or profit margin. Structured plans should at least specify each step's goal, tool hint, input dependencies, and completion criteria. When the plan is submitted for approval, approvers review an executable and accountable process artifact instead of the model's informal thoughts.

Financial scenarios especially benefit from this approach. A closing assistant can generate a plan first: which accounts to read, which dimensions to reconcile, which variance reports to generate, which steps need manual confirmation. Approvers approve the plan and permission boundary, not a natural language explanation from the model. If a step fails during execution, the Planner can replan only the remaining steps instead of canceling the entire run.

---

## 25.4 State Graphs and Workflow Boundaries

Frameworks like LangGraph use directed graphs to represent complex agent workflows: nodes correspond to function calls, model invocations, or tool wrappers, while edges represent conditional routing. State graphs are well suited for multi-branch processes, subgraph reuse, complex human-in-the-loop (HITL) gates, and node-level replay. However, the state graph remains an internal Planner implementation detail and cannot replace the six Run states.

The platform's external interface only needs to consistently expose the Run states such as `planning`, `executing`, `waiting_human`, `succeeded`, and `failed`. Internal node names like `fetch_schema`, `reflect_sql`, or `rerank_tools` should never be directly exposed to the Console or ticketing systems. Otherwise, whenever the framework or node implementation changes, the frontend and audit reports risk being tightly coupled to internal details.

A simple guideline for choosing whether to use state graphs is as follows: if the task involves just a single-agent ReAct or a linear Plan-and-Execute flow, a RunLoop with a `planner.mode` is sufficient; if the same Run involves multiple Planner roles, reusable subgraphs, multiple HITL gates, or node-level A/B tests, then explicit StateGraph use is warranted. If the workflow mainly consists of human and system tasks, external BPM systems should manage gates and SLAs while LLM inference remains embedded in Planner nodes.

### 25.4.1 Mapping Principles

The internal state graph can be complex, but the external mapping should be restrained.

- When the graph enters a model planning node, the external state can remain `planning` or `executing`.
- When the graph triggers a Tool Call, it maps externally to the Runtime state `action`.
- When the graph enters a human intervention state, externally it maps to `waiting_human`.
- Internal reflection or reranking usually remains `executing` externally, with detailed information recorded in the Trace.

This mapping layer is an engineering concern, not a documentation detail. Without it, framework states and product states will diverge, making SLA management, replay, and alerting difficult. Another risk with state graphs is over-modeling. Many teams initially convert every decision point into a graph node, resulting in beautiful but harder-to-debug graphs. To decide if a state graph is needed, use this criterion: if node states do not require reuse, replay, or separate evaluation, avoid lifting them into graph nodes. Simple Python branching with clear logging is usually better.

The value of state graphs lies in reusing complex paths. For example, in compliance review, routine reports follow one path, reports involving personal data enter a data-masking subgraph, and reports involving competitor claims enter a legal review subgraph. Such paths have clear reuse value and suit graph modeling. In contrast, picking between two tools based on a simple if statement is too small a problem to force into graph modeling for framework consistency.

---

## 25.5 Planner and Runtime Interface

### 25.5.1 Planner Implementation Entry Point

The mini-platform includes two paths. `projects/multi-agent-workflow/lib/planner.py` contains the practical project's `MultiAgentPlanner`, which outputs Handoff, Tool Call, or FINISH decisions based on `active_agent_id`. The `core/planner/` directory provides a generic Planner interface, rule-based demos for ReAct and Plan-and-Execute, and the `create_planner(config)` factory for potential integration with a real Gateway later.

```
mini-platform/core/planner/
+-- base.py
+-- config.py
+-- react_planner.py
+-- plan_execute.py
`-- planner.py

projects/multi-agent-workflow/lib/
`-- planner.py
```

The recommended reading order for the code is to start with `base.py` to understand `PlannerDecision`; then review `react_planner.py` and `plan_execute.py` to learn the two modes; finally look at how `run_loop.py` calls the Planner and passes decisions to the Registry for execution.

### 25.5.2 Configuration Examples

The Planner mode should be configured within the Agent setup, instead of hardcoded in the Prompt.

```yaml
agent_id: demo-data-agent
planner:
  mode: react
  model: gpt-4o
  tools:
    - name: sql_executor
      version: v2
runtime:
  max_steps: 20
  run_timeout_s: 900
```

Plan-and-Execute can add planning model, execution model, max replans, and a plan approval switch.

```yaml
planner:
  mode: plan_execute
  planning_model: gpt-4o-mini
  execution_model: gpt-4o
  max_replan: 2
  plan_requires_approval: true
  plan_schema: plans/finance_v1.json
```

Switching the `planner.mode` should be treated as a new Agent version requiring re-evaluation. Switching mid-run within the same `run_id` from ReAct to Plan-and-Execute is not allowed because checkpoints, evaluation, and audit become hard to interpret. Configurations should also record default tool versions. The Planner should not fetch the latest tools from the Registry each time because the same problem might then follow different schemas days later. Tool versions should be pinned into checkpoints at run startup, ensuring all steps use the same tool views unless the Run is recreated.

Evaluation should separate modes. ReAct focuses on step count, loop rate, tool argument fix success rate, and final answer quality; Plan-and-Execute examines plan readability, approval pass rate, replan frequency, and execution deviation; and state charts look at node mapping, branch coverage, and recovery consistency. Mixing all modes into a single average score masks real issues. Failed samples should be attributed by mode. ReAct failures often come from too many tools; Plan-and-Execute failures from overly loose plan schemas; state chart failures from node states not folding into the Run properly. Different causes require different fixes. Planner quality review should look beyond the final answer. It must also evaluate whether decision paths are short, tool selection is stable, failures are correctable, and the "Planner proposes, Runtime executes" boundary is always upheld. All evidence should be reconstructible from Trace and checkpoints.

If only the final answer is visible without seeing how the Planner arrived at it, the system remains at a chatbot interface level. A truly platform-grade Planner allows every decision step to be replayed, constrained, and replaced. Tool-view pruning should also be part of release review. The same Agent should see different tools in different states: during data inquiry, it usually needs semantic-layer, SQL, and chart tools; during report publication, notification, email, or ticketing tools may become visible; during approval wait, the Planner should not keep seeing publication tools until the Runtime receives a valid approval callback. If the tool view is too broad, prompt instructions become soft constraints. A stronger design lets Runtime build the tool view for the current turn from state, tenant, user role, and Policy, then records that tool-view version in the checkpoint.

Planner evaluation must include cases where the correct decision is to stop. Many evaluations count task completion and accidentally reward overactive Planners. Production samples should include insufficient permission, ambiguous metric definitions, weak evidence, repeated tool failure, and tasks that require human approval. Expected outcomes may be clarification, refusal, human handoff, or controlled failure. A good Planner calls tools when evidence supports action and stops when the platform boundary says it should stop.

### 25.5.3 Acceptance Criteria

Planner-related acceptance should verify task completion and boundary discipline.

*Table 25-4: Checklist Before Planner Launch. Source: Compiled by this book.*

| Checklist Item        | Judgment Criteria                                          |
|-----------------------|-----------------------------------------------------------|
| Planner does not execute tools | Code paths do not include Registry `invoke` or tool handler calls |
| Tool views have a common source | Planner sees schema from Registry                         |
| Failures provide feedback    | Errors like `TOOL_ARGUMENT_INVALID` feed into next Planner input |
| Loops are terminable         | Configured `max_steps`, parameter summaries, and repeat call thresholds |
| Mode is versioned            | `planner.mode`, model, and tool versions recorded in Agent manifest |
| States are mappable          | Internal graph states fold into Run's six states and SSE  |

Acceptance should deliberately include counterexamples. The first category is parameter error: missing `tenant_id`, invalid date ranges, or non-existent SQL fields. The review checks whether the Planner can use structured errors to fix parameters instead of repeating the same failed call. The second category is permission denial: if a user cannot view customer details, the Planner must stop or request human handling instead of trying to bypass Policy. The third category is empty result with data-quality warnings: the Planner needs to distinguish no business data from a likely table, filter, metric, or permission issue.

Trace must participate in acceptance. A qualified Run should show each `PlannerDecision`, the corresponding `action`, Registry `result`, error code, retry count, and final state. If Trace shows a tool execution without an `action` event, the Planner or business code bypassed Runtime. If the same normalized arguments repeat without loop protection, Runtime has not contained Planner failure. If `finish=True` appears while a tool is still unfinished, terminal-state control has leaked from Runtime into Planner.

The first acceptance version can select three tasks: an exploratory Q&A task using ReAct, a plan approval task using Plan-and-Execute, and a complex branching task using the state chart. All three tasks share the same Runtime and Registry. If all can produce consistent `state`, `action`, `result`, checkpoints, and error codes, the Planner layer is truly replaceable.

This is also a prerequisite for later introducing LangGraph or other frameworks. Frameworks can replace Planner internal implementations but must not alter the outer Run contract. With this stable boundary, the platform team can gradually experiment with more complex orchestration modes without impacting already deployed tool governance and audit chains.

The first version does not need to perfect all modes. A more realistic goal is: by default, ReAct can reliably handle Q&A; Plan-and-Execute covers scenarios requiring plan approval; and state charts are used only where complex flow reuse is clearly valuable. This ensures the designs in this chapter translate into code and evaluation, not remain mere conceptual comparisons.

---

### 25.5.4 Replay Requirements for Planner Decisions

The production value of a Planner is not that it generates a plausible plan, but that every choice can be reviewed later. After a Run finishes, the platform should be able to reconstruct the user goal, the context visible to the Planner, the candidate tool list, the selected tool, the alternatives rejected, and the reason the Planner ended the task. If the platform only sees the final Tool Call, operators cannot tell whether a failure came from planning, tools, permissions, or model interpretation.

Replay does not require permanently storing the full prompt. Production systems usually balance privacy, cost, and audit requirements. A practical approach is to store structured summaries: Planner input summary, candidate tool versions, key context references, decision JSON, error code, and trace span. Sensitive original text can stay in short-lived encrypted storage, while long-term audit records keep hashes, field names, data domains, and reference IDs.

Cost amplification also belongs in Planner review. ReAct can probe repeatedly when tools fail, and Plan-and-Execute can drive the entire execution down the wrong path when the initial plan is too broad. Before release, each Agent should define `max_steps`, maximum tool calls per Run, maximum Planner LLM calls, and degradation strategy. If the Planner selects the same failing tool twice in a row, Runtime should be able to stop the loop and return a clear reason.

## 25.6 Planner Cost and Retry Boundaries

Planner risk often comes from repeated wrong decisions instead of one bad decision. A ReAct loop that repeatedly selects similar tools, receives similar observations, and continues reasoning will quickly consume model budget and tool quota. Plan-and-Execute has a related problem: a large plan can make each subtask trigger more model calls, retrieval, and tool access. Planner design should treat cost as part of state, not as a number calculated only after the run ends.

Cost control enters in three places. Before generating a plan, the Planner should set maximum steps, tool calls, and retries according to task type, user permission, and business value. During execution, Runtime should feed consumed budget back into Planner context so later decisions know how much room remains. After failure, retry policy should distinguish recoverable and unrecoverable errors: network timeout can retry, permission denial should not, missing parameters should ask for clarification, and business-rule conflicts should move to human handling.

Retries must preserve meaning. If the user asks for last month's East China revenue and SQL execution fails because of resource limits, the system may change execution strategy or ask the user to narrow the query. It should not silently turn the task into "revenue for the last seven days." Planner retries should preserve the original intent and record the reason for each rewrite. That record becomes Trace evidence for Chapter 38 and evaluation material for Chapter 39.

## 25.7 Plan Freezing and Replayable Execution

High-risk tasks often need the plan to be frozen before execution. Freezing does not mean the plan can never change. It means the current version becomes the audit object: which capability each step will call, what inputs it needs, what output it expects, and how failures will be handled. If execution requires a change, the system creates a new plan version and records the reason. Approvers, developers, and incident reviewers can then distinguish "the original plan said this" from "execution adjusted the plan."

Replayable execution requires a stable mapping between Planner decisions and Runtime state. Each plan node should correspond to one or more Steps, and each Step should store tool calls, model calls, and observations. Replay does not have to execute external actions again, but it should show decisions, evidence, and state transitions in the original order. For write operations, replay also needs to mark which actions were committed, simulated, canceled, or compensated.

This design turns Planner from a clever prompt into an auditable control surface. The first implementation does not need a complex graph execution engine, but it should at least save plan versions, step mappings, and change records. Otherwise, the Planner chapter and Runtime chapter remain disconnected: one discusses reasoning patterns, the other discusses state machines, with no traceable execution chain connecting them.

## 25.8 Evaluation Sample Design for Planner

Planner evaluation cannot use final answer quality alone. A task may complete while taking a high-cost, low-control, or unauditable path. Evaluation samples should cover plan rationality, tool selection, step count, retry strategy, human intervention, and failure recovery. The same user question may allow several correct plans, but each plan must satisfy budget, permission, and evidence requirements.

Counterexamples are especially useful. A user asks for data and the Planner selects email sending; a question lacks required conditions and the Planner executes anyway; a tool returns permission denial and the Planner keeps retrying; a plan contains free-text steps that cannot be replayed. These cases reveal production risk better than success rate alone. They should enter the Chapter 39 evaluation set and run as regression checks whenever Planner changes.

Planner maturity is the ability to make stable decisions under constraints. The first version can combine fixed rules with a small number of model decisions, then gradually expand model autonomy after Trace, tool governance, and evaluation become stable. Planner explanations should also be evaluated. Users and approvers do not need the full reasoning chain, but they need to know why the plan selected these steps, which actions carry risk, and which steps can be canceled.

Planner should also know when to stop. Asking for clarification when evidence is missing, stopping when permission is insufficient, degrading when budget is exhausted, and handing off after repeated tool failures are all valid high-quality decisions. Evaluation should reward these stop decisions instead of scoring only task completion.

Orchestration-mode selection should return to task structure. ReAct fits tasks that need observation and adjustment. Plan-and-Execute fits tasks with relatively stable steps and pre-execution review. State graphs fit workflows with approval, recovery, and multi-role collaboration. No single mode is suitable for every Agent, and the choice itself should be governed once the platform supports multiple Planners.

Planner input must remain controlled. The context, Memory, tool history, and system policies visible to the Planner shape its next action. If unauthorized data enters the context package, the Planner may choose the wrong tool even when it does not directly reveal the data. Runtime should prepare a clean context package before calling Planner and record the source of each part. Planner output should also stay small and explicit. Returning a long reasoning paragraph and then parsing actions from it increases instability. A steadier interface returns a finite decision such as `FINISH`, `ASK_CLARIFICATION`, or `TOOL_CALL`, with structured tool name, arguments, confidence fields, and stop reason.

Plan changes during a Run need to be visible. User clarification, tool failure, permission denial, and data-quality warnings can all change the route. The platform should record the plan before and after the change, plus the event that triggered the change. Later review can then decide whether the Planner made a reasonable adjustment or was pulled off track by bad context.

Different Planner implementations also need governance. A rule-based Planner is cheap and stable, an LLM Planner is flexible but less predictable, and a state graph is useful for enumerable processes. Different tasks can use different Planners, but they should all obey the same Runtime interface and audit format. Evaluation can start from trajectory samples: given a user question, visible tools, context, and historical observations, the expected output is the next action or stop decision. Samples should include normal paths, insufficient permission, missing data, tool failure, and ambiguous user questions.

Plan freezing is appropriate for high-risk tasks such as contract review, external email sending, and batch data export. The Planner can generate a plan first, then wait for user or approver confirmation before Runtime executes it. If execution needs to deviate from the frozen plan, the system should request confirmation again or record the reason. Freezing reduces flexibility, but it gives teams a clearer audit object for actions with larger consequences.

Planner and Memory also need a boundary. Historical preferences may help choose report format, but they should not override the current task goal or permission policy. If a user often views East China data but the current question lacks a region, the Planner should ask for clarification instead of silently applying an old preference. Memory provides clues; it should not make business assumptions on behalf of the Planner.

Multi-model planning can be useful once Trace and evaluation are stable. Low-risk tasks may use a cheaper model for next-step selection, while high-risk or complex tasks can switch to a stronger reasoning model. Runtime or Gateway should control the model switch and record the reason. This keeps cost visible and gives complex tasks better planning capacity without making every Run expensive.

Planner failures often accumulate through small deviations. The first table choice is slightly wrong, the second correction follows the wrong direction, and the third attempt produces a vague answer. Trace needs to preserve these small deviations so evaluation and debugging have material to work with. Looking only at the final answer hides early planning failures.

The Planner context window also needs a budget. Tool descriptions, historical steps, user input, Memory, and retrieval results all compete for space. Long context increases cost and makes the model more likely to miss key constraints. Runtime can prepare structured summaries for Planner, keep necessary state, and move large objects into references that can be recovered outside the prompt.

Clarification needs product support. When Planner decides that information is insufficient, the frontend should show a specific question and keep the current Run state. After the user replies, the task continues under the same `run_id` instead of opening a new session. Clarification then becomes part of the workflow and audit chain.

Planner can also use tool-health information. If a tool is degraded or under maintenance, the Planner should choose an alternative path or ask the user to wait instead of repeatedly calling the same unhealthy tool. Tool health comes from Registry and observability systems; adding it to Planner context makes decisions closer to production reality.

In complex tasks, Planner may expose an intermediate plan for user confirmation. The user can correct a misunderstanding before the task consumes tools, and later execution becomes more predictable. This interaction costs one extra step, but it reduces the chance that a long task finishes in the wrong direction. Planner must also handle target changes during execution: the user may add a condition, revoke part of the request, or realize the original question was wrong. Runtime should let Planner receive the change event and decide whether to continue the current Run, create a child task, or cancel and restart. Treating every target change as a new chat message breaks the audit chain.

Plan reviews can reveal platform capability gaps. If Planner repeatedly takes long detours, the issue may be a missing tool or semantic-layer entry point instead of model weakness. Regularly reviewing failed plans and overly long plans can feed back into Registry and data-platform roadmap decisions. Planner traces are therefore also product evidence for platform evolution.

## 25.9 Planner Operating Ledger and Strategy Rollback

After a Planner goes live, it needs an operating ledger. The ledger should record Agent version, Planner mode, model version, tool-view version, step limit, budget ceiling, retry strategy, plan-freezing setting, evaluation-set version, and release owner. Whenever Planner behavior changes, the team should be able to tell whether the model changed, tool schema changed, Memory injection changed, policy thresholds changed, or evaluation samples changed. Without this ledger, an online question such as "why did this Run choose a different path" becomes hard to answer.

The ledger should also record high-risk decision samples. Examples include the Planner executing with insufficient evidence, retrying after permission denial, expanding the plan when budget is nearly exhausted, or failing to update the Frame after user clarification. Review should inspect the context visible to Planner, tool-health state, error code, consumed budget, and final Run state at the time. Final answer quality alone rarely reveals that the Planner had already drifted early in the task.

Strategy rollback should be more fine-grained than model rollback. Planner behavior can be shaped by prompts, tool-view pruning, retry thresholds, budget limits, plan-freezing rules, and Memory injection rules. If failure rate rises after a release, the platform does not always need to roll back the whole Agent. It can first disable a retry class, narrow the tool view, restore the previous plan-freezing policy, or move some tasks from an LLM Planner back to a rule-based Planner. The rollback action should enter the ledger and trigger the related evaluation samples to confirm whether the problem is contained.

The first version can make the Planner ledger part of release records. Before each release, store configuration, sample results, and expected behavior changes. After release, sample successful, failed, clarified, refused, and human-handoff Runs. When an incident occurs, add the incident sample to the regression set. Planner evolution then follows evidence instead of intuition about a smarter strategy. Over time, Planner trust comes from replayable decisions and rollbackable strategies, not from a plan that looks complete once.

## 25.10 Planner Review Samples And Strategy Migration

Planner quality review should start from task paths instead of final answers alone. A failure may come from over-decomposition that increases cost, skipped approval, early tool selection, continued reasoning with insufficient observations, or repeated retries after tool failure. Review samples should preserve the user goal, plan version, observation at each step, selected tools, skipped candidate tools, budget consumption, failure phase, and final disposition. With these materials, the team can decide whether to change decomposition, tool ordering, stop conditions, or Runtime state protection.

Strategy migration should proceed in stages. When the Planner moves from ReAct to Plan-and-Execute, or from a single prompt policy to a state-graph policy, the platform should not replace all traffic at once. It can start with read-only tasks, low-risk queries, and internal users, then compare plan steps, tool-call success rate, human-confirmation count, user waiting time, and cost. If the new strategy is slower on simple tasks, it may be planning too much. If it saves cost on complex tasks, it may be reducing wasted retries. Evaluation should consider both success rate and path quality so a correct answer with an unauditable path does not pass as ready.

Planner migration boundaries also need organizational ownership. Platform teams maintain the strategy framework and runtime parameters. Business teams provide task samples and approval rules that cannot be skipped. Security teams confirm planning constraints for high-risk actions. Evaluation teams maintain regression sets. If one team changes Planner strategy alone, tool permission, approval responsibility, and cost budget become unstable. Once review samples and migration cadence enter the operating ledger, the Planner can evolve as a platform capability.

## 25.11 Boundaries Between Planner And Business Policy

Planner should not replace business policy. It can choose the next tool, decide whether clarification is needed, and decide whether to keep trying, but it should not change pricing rules, approval rules, customer priority, or compliance requirements. Business policy should come from rules, configuration, semantic layer, or Policy Engine. Planner organizes tasks inside those boundaries. If business policy lives inside prompts, audit and change management become difficult.

Boundary material should enter Planner context in structured form. Available tools, approvals that cannot be skipped, budget limits, task risk level, data visibility, and current tool health should all be visible to Planner. Then the plan matches production state. If these facts live only in documents, the model can generate a plan that looks reasonable while violating platform rules.

After business policy changes, Planner samples should rerun. Pricing changes, approval-threshold changes, tool-permission changes, and data-domain changes can all alter the best plan. Evaluation should check whether the task completes and whether the plan obeys the new policy, avoids unnecessary steps, and keeps users on the correct path. Planner capability should serve business boundaries and platform evidence.

## 25.12 Canary and rollback for Planner policy

Planner policy releases need canary support. Task decomposition, tool selection, retry count, clarification timing, cost budget, and stop conditions all affect user experience and system cost. A new policy may improve completion for complex tasks while slowing simple tasks or increasing tool calls. Planner changes should not be judged by a few successful examples. They need observation across real task distribution.

During canary, the platform should keep difference records between old and new policies. It can replay historical samples offline, then enable the new policy on a small share of real tasks. Records should include plan step count, tool-call count, failure type, human intervention, token cost, execution time, and final user acceptance. If the new policy adds automatic actions in high-risk tasks, canary scope should be smaller and HITL and Guardrails records should be complete.

Rollback also needs execution rules. After a Planner policy changes, the platform should define whether running tasks continue with the old plan, replan, or ask for user confirmation. Otherwise rollback creates mixed behavior, with some tasks running old strategy and others recovering under the new one. Planner controls task direction, so its release discipline should look closer to business-process change than to an ordinary prompt edit.

## 25.13 Layered governance of Planner failure samples

Planner failures should not be classified only as wrong answers. A more useful classification separates where the failure happened: goal understanding, task decomposition, tool selection, parameter construction, observation interpretation, stopping condition, approval boundary, or budget control. Each layer has a different repair path. A goal-understanding failure may need a better clarification question. A tool-selection failure may require ToolSpec wording and candidate-set pruning. An observation-interpretation failure may require structured results and evidence tiers. A stopping-condition failure may require Runtime to give Planner a clearer failure state.

Layered samples should keep the material visible to Planner at the time: original user request, context summary, Memory hits, visible tool list, tool health, policy version, consumed budget, previous observation, and final state. Without those materials, teams tend to blame all failures on model capability and then only change the model or prompt. Planner governance should answer whether the model saw the wrong tool, lacked evidence, was misled by stale Memory, or lacked a recovery path after tool failure.

These samples should feed platform work. If many failures come from tool selection, Registry descriptions and candidate pruning need revision. If many failures come from excessive decomposition, Planner budget and plan-freeze rules should tighten. If many failures come from missed approvals, Policy and HITL information did not enter Planner context clearly enough. Planner is not an isolated algorithm; it reveals interface problems among platform capabilities. Layered failure governance moves Planner improvement from one-off tuning into continuous platform evolution.

## 25.14 Periodic calibration for Planner policy drift

Planner policy drifts as the platform environment changes. After more tools are added, a once stable candidate set may become crowded. After Memory covers more historical tasks, old preferences may affect new scenarios. After cost policy changes, Planner may prefer shorter paths with weaker evidence. After security policy tightens, steps that used to run automatically may require approval. If teams evaluate Planner only at launch, the same policy may no longer fit the platform boundary several months later.

Periodic calibration should inspect both offline samples and live runs. Offline samples compare plan differences across policy versions on fixed tasks, with attention to step count, tool selection, approval trigger, budget consumption, and stopping condition. Live runs reveal the real task distribution, with attention to clarification rate, human takeover, tool retry, plan interruption, abnormal cost, and final acceptance. Together, the evidence shows whether drift came from task mix, tool inventory, Memory behavior, or model routing.

Calibration should not optimize only for completion rate. A Planner can improve completion by adding more steps and tool calls, shifting cost and wait time to the user. It can reduce cost by exploring less and miss necessary evidence. It can overuse Memory and carry conclusions from old tasks into new contexts. The calibration result should become a concrete policy action: narrow candidate tools, ask for clarification earlier, adjust budget, freeze plans sooner, add approval, or move a task class to Plan-and-Execute.

A first version can calibrate high-frequency tasks monthly. The material includes fixed-sample replay, sampled online Trace, layered failure statistics, and cost distribution. If calibration shows that policy has moved away from expectation, the team should check Registry, Memory, Runtime state, and HITL information before changing the model. Planner governance then follows platform facts instead of recurring prompt edits.

## 25.15 User-commitment checks before plan execution

After Planner produces a plan, the platform still has to inspect what the plan commits to on behalf of the user. A request such as "generate an operating analysis report" may only imply a draft. A request such as "send the result to the team" involves export, recipients, permission, and approval. If Planner decomposes steps without checking user commitment, Runtime may discover missing authorization or missing fields only during execution. Before execution, actions should be classified as read-only analysis, draft generation, internal publication, external sending, or system write, with confirmation requirements attached.

Commitment checks need structured plans. Each Step should mark input source, tool, output form, side effect, permission requirement, human confirmation point, and failure handling. If the plan contains a high-risk action, Runtime should create a confirmation card or enter HITL before submitting the tool call. If the plan only creates a draft, the interface should show draft state so users do not assume it has been published. Planner intelligence then stays within the platform's responsibility boundary.

A first version can connect commitment checks to the human-intervention mechanism in Chapter 30. Planner outputs a plan, Policy Engine marks risk, and Runtime decides whether to continue, confirm, suspend, or refuse. Trace stores plan version, confirmation action, and execution result. This path tells users what the system is about to do and tells the platform which step changed business state.

## 25.16 Joint governance of Planner and execution budget

Planner decides task decomposition and therefore shapes execution budget. A plan with ten tool steps differs from a plan with three tool steps in cost, latency, failure surface, and user waiting time. A production platform should evaluate whether a plan is reasonable and whether it can finish within budget. Budget includes model tokens, tool-call count, data-scan volume, human-approval count, retry count, and user waiting time.

Budget governance should happen before execution. After Planner produces a plan, Runtime can estimate resources: which steps need a large model, which query data, which may trigger Python sandbox, and which require human confirmation. If budget exceeds the task tier, the system can ask the user to narrow scope, move to async execution, split the task, or request approval. High-cost plans then do not enter the execution queue directly or fail halfway because quota runs out.

Budget should also enter review. If one plan type often exceeds budget, the team should inspect whether Planner decomposes too finely, tools return too much data, retry policy is too broad, or the user entry point lacks scope control. A first version can add `estimated_cost`, `budget_class`, and `budget_decision` to Planner output. Cost governance, SLO, and user commitment can then align at the planning stage instead of only after execution.

## 25.17 Runtime audit for plan changes

After Planner reaches production, a successful demo is not enough evidence. The platform needs stable fields for initial plan, observation result, plan change, budget consumption, stop reason, and human confirmation, and those fields should connect to release records, Trace, evaluation samples, and incident notes. When a production issue appears, teams can follow one set of facts to understand scope, ownership, and repair order instead of stitching together model logs, business logs, and verbal explanations.

This evidence also connects the surrounding chapters. It links to Chapter 22 on Runtime, Chapter 26 on enhanced workflow, and Chapter 30 on HITL: upstream capabilities provide assumptions, downstream capabilities consume the result, and governance capabilities preserve evidence and review decisions. If these materials do not share identifiers and versions, the production system splits apart. Business owners see user complaints, platform owners see system errors, and security or compliance teams see explanations written after the fact. That separation makes it hard to decide whether the issue came from data, model behavior, tool contracts, workflow state, or organizational ownership.

Common production risks include plans being rewritten repeatedly without user awareness, retries consuming budget, and stop conditions existing only in prompts. These risks are less visible during demos because demos usually exercise the successful path. Production users bring boundary cases, repeated requests, permission changes, and long-running state. The platform team should turn such failures into release samples. Some samples should block launch, some can be handled by degradation, and some require the business owner to accept the remaining risk with a review date.

Planner audit should record how a plan changed and which changes require acknowledgement from the user or a human reviewer. The record can stay compact, but it should include time, version, owner, sample, action, and the next review condition. Without those fields, review remains informal experience. With them, one production issue can become material for later releases, evaluation suites, and training.

A first platform version can start with a small set of high-risk paths. Choose flows with high traffic, high business impact, or sensitive data, require an evidence package for each change, and then expand the practice to ordinary scenarios. This keeps the capability at the engineering level: runnable, explainable, and recoverable.
## Chapter Recap

Planner decides the next step, while Runtime executes and governs through the `PlannerDecision` handshake. ReAct fits exploratory, multi-hop, incomplete-information tasks, but it needs step limits, loop detection, and tool boundaries. Plan-and-Execute fits clearer paths and tasks requiring plan approval. State graphs can implement Planner internals, but they cannot replace Runtime's six states or platform checkpoints. Planner modes should be configurable, versioned, evaluated, and rollback-ready. Cost, retry boundaries, plan freezing, and replayable evidence determine whether a Planner can enter production.

## References

Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Yao, S., Zhao, J., Yu, D., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

Qu, C., Dai, S., Wei, X., Cai, H., Wang, S., Yin, D., Xu, J., & Wen, J.-R. (2025). Tool learning with large language models: A survey. *Frontiers of Computer Science*, 19(8), 198343. [https://doi.org/10.1007/s11704-024-40678-2](https://doi.org/10.1007/s11704-024-40678-2)

OpenAI. (n.d.). *Function calling*. OpenAI API documentation. [https://developers.openai.com/api/docs/guides/function-calling](https://developers.openai.com/api/docs/guides/function-calling)

LangChain. (n.d.). *LangGraph persistence*. [https://docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

Masterman, T., Besen, S., Sawtell, M., & Chao, A. (2024). The landscape of emerging AI agent architectures for reasoning, planning, and tool calling: A survey. [https://arxiv.org/abs/2404.11584](https://arxiv.org/abs/2404.11584)
