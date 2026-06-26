# Chapter 25 Planner and Orchestration Patterns

---
Planner is the decision interface of the Agent Runtime. It reads the user task, tenant context, visible tool set, run history, tool results, and Memory fragments, then proposes what to do next. It does not execute tools. Runtime advances Run state, calls Registry, pushes events, writes checkpoints, and chooses recovery paths. This boundary looks simple, but it determines whether an Agent remains controllable.

Chapter 22 explained how Runtime drives a Run forward. Chapter 23 explained how tools are registered as ToolSpecs. One role is still missing: at each Step, who reads the current context and decides which tool to call next, or whether the task can end? In a DataAgent task, the user asks which SKUs declined in East China last week. Runtime manages state. Registry manages tool definitions and invocation. Planner decides whether to look up region codes first, directly query sales detail, adjust SQL after a failure, switch to semantic-layer tools, or finish with an answer.

If planning and execution are both hardcoded inside RunLoop, every business Agent duplicates prompts, tool selection, and error recovery logic. When one version upgrades, behavior drifts across applications. A more stable design lets Planner return structured decisions only, while Runtime decides whether to execute, how to execute, how to log, and how to recover.

This separation also improves troubleshooting. If SQL parameters are wrong, first inspect the Planner output. If a tool refuses execution, inspect Registry schema and Policy. If a task waits for approval, inspect Runtime state and callbacks. Without this boundary, all failures get blamed on model instability. Planner mode choices such as ReAct, Plan-and-Execute, and state graphs should serve these responsibility boundaries rather than act as an algorithm showcase.

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

If the Registry returns `TOOL_ARGUMENT_INVALID`, the Runtime should not fail immediately. Instead, it can record the error in `result` and call the Planner again to generate new parameters. Conversely, if the Runtime detects the same tool call with identical parameters repeating, it should trigger loop protection rather than letting the Planner keep trying.

### 25.2.3 Advantages and Costs

*Table 25-2: ReAct advantages and costs. Source: Compiled by the book.*

| Dimension       | Advantages                                     | Costs                              |
|-----------------|-----------------------------------------------|-----------------------------------|
| Task Fit        | Suitable for exploratory, multi-hop, incomplete information tasks | Number of steps unpredictable      |
| Cost            | Each step solves a local subproblem           | Multi-step accumulates latency and token usage |
| Observability   | Tool Call trace explains task path             | Thought drafts should not be exposed directly |
| Recovery        | Single-step errors can be locally corrected    | Requires `max_steps` and loop detection           |

The key to ReAct is bounded freedom inside the Runtime. Tools come from the Registry, actions are executed by the Runtime, results are saved to checkpoints, and errors are classified by error code. Without these boundaries, ReAct quickly turns into uncontrollable loops.

In practice, the most common failure of ReAct is repeatedly fixing the same error. For example, the model generates the same SQL missing tenant filters three times, differing only in spacing or field order. The Runtime should normalize tool parameters and summarize them, stopping after hitting a repetition threshold rather than burning tokens endlessly. Another common failure is verbal completion: the model produces a summary before the last tool call has returned. The final state must still be decided by the Runtime.

Another failure source comes from incomplete observation information. The Planner might see that SQL returned an empty set and conclude that sales did not decline. The same empty set could also indicate a wrong table, incorrect date filter, or overly strict permission filter. The Runtime can feed back tool errors and data quality signals together to the Planner, for example: query succeeded, result is empty, and the filter includes newly launched channel fields. The more structured the Observation, the easier it is for the Planner to fix issues.


---
## 25.3 Plan-and-Execute: Plan First, Then Execute

### 25.3.1 Suitable for Tasks Requiring Pre-Audit

Plan-and-Execute generates a plan first, then executes it step by step. It is suitable for tasks with strong compliance requirements, relatively clear workflows, and that require pre-execution auditing. For example, a financial closing assistant must first specify which tables will be checked, what filters will be applied, and what reports will be generated before running queries; only after the approver approves the plan will the runtime allow execution.

The plan itself is an artifact. It can enter checkpoints, approval workflows, and audit exports. After approval, the Planner outputs `PlannerDecision` step by step according to the `plan_cursor`. The runtime still executes tools according to the rules explained in Chapter 22.

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

Plans also need versioning and schemas. Free-text plans are prone to misinterpretation during execution. For example, a request to query key SKUs could mean sorting by revenue, sales volume, or profit margin. Structured plans should at least specify each step's goal, tool hint, input dependencies, and completion criteria. When the plan is submitted for approval, approvers review an executable and accountable process artifact rather than the model's informal thoughts.

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

This mapping layer is an engineering concern, not a documentation detail. Without it, framework states and product states will diverge, making SLA management, replay, and alerting difficult.

Another risk with state graphs is over-modeling. Many teams initially convert every decision point into a graph node, resulting in beautiful but harder-to-debug graphs. To decide if a state graph is needed, use this criterion: if node states do not require reuse, replay, or separate evaluation, avoid lifting them into graph nodes. Simple Python branching with clear logging is usually better.

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

The Planner mode should be configured within the Agent setup, rather than hardcoded in the Prompt.

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

Switching the `planner.mode` should be treated as a new Agent version requiring re-evaluation. Switching mid-run within the same `run_id` from ReAct to Plan-and-Execute is not allowed because checkpoints, evaluation, and audit become hard to interpret.

Configurations should also record default tool versions. The Planner should not fetch the latest tools from the Registry each time because the same problem might then follow different schemas days later. Tool versions should be pinned into checkpoints at run startup, ensuring all steps use the same tool views unless the Run is recreated.

Evaluation should separate modes. ReAct focuses on step count, loop rate, tool argument fix success rate, and final answer quality; Plan-and-Execute examines plan readability, approval pass rate, replan frequency, and execution deviation; and state charts look at node mapping, branch coverage, and recovery consistency. Mixing all modes into a single average score masks real issues.

Failed samples should be attributed by mode. ReAct failures often come from too many tools; Plan-and-Execute failures from overly loose plan schemas; state chart failures from node states not folding into the Run properly. Different causes require different fixes.

Planner quality review should look beyond the final answer. It must also evaluate whether decision paths are short, tool selection is stable, failures are correctable, and the "Planner proposes, Runtime executes" boundary is always upheld. All evidence should be reconstructible from Trace and checkpoints.

If only the final answer is visible without seeing how the Planner arrived at it, the system remains at a chatbot interface level. A truly platform-grade Planner allows every decision step to be replayed, constrained, and replaced.

Tool-view pruning should also be part of release review. The same Agent should see different tools in different states: during data inquiry, it usually needs semantic-layer, SQL, and chart tools; during report publication, notification, email, or ticketing tools may become visible; during approval wait, the Planner should not keep seeing publication tools until the Runtime receives a valid approval callback. If the tool view is too broad, prompt instructions become soft constraints. A stronger design lets Runtime build the tool view for the current turn from state, tenant, user role, and Policy, then records that tool-view version in the checkpoint.

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

Acceptance should deliberately include counterexamples. The first category is parameter error: missing `tenant_id`, invalid date ranges, or non-existent SQL fields. The review checks whether the Planner can use structured errors to fix parameters instead of repeating the same failed call. The second category is permission denial: if a user cannot view customer details, the Planner must stop or request human handling rather than trying to bypass Policy. The third category is empty result with data-quality warnings: the Planner needs to distinguish no business data from a likely table, filter, metric, or permission issue.

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

Planner risk often comes from repeated wrong decisions rather than one bad decision. A ReAct loop that repeatedly selects similar tools, receives similar observations, and continues reasoning will quickly consume model budget and tool quota. Plan-and-Execute has a related problem: a large plan can make each subtask trigger more model calls, retrieval, and tool access. Planner design should treat cost as part of state, not as a number calculated only after the run ends.

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

Planner and Memory also need a boundary. Historical preferences may help choose report format, but they should not override the current task goal or permission policy. If a user often views East China data but the current question lacks a region, the Planner should ask for clarification rather than silently applying an old preference. Memory provides clues; it should not make business assumptions on behalf of the Planner.

Multi-model planning can be useful once Trace and evaluation are stable. Low-risk tasks may use a cheaper model for next-step selection, while high-risk or complex tasks can switch to a stronger reasoning model. Runtime or Gateway should control the model switch and record the reason. This keeps cost visible and gives complex tasks better planning capacity without making every Run expensive.

Planner failures often accumulate through small deviations. The first table choice is slightly wrong, the second correction follows the wrong direction, and the third attempt produces a vague answer. Trace needs to preserve these small deviations so evaluation and debugging have material to work with. Looking only at the final answer hides early planning failures.

The Planner context window also needs a budget. Tool descriptions, historical steps, user input, Memory, and retrieval results all compete for space. Long context increases cost and makes the model more likely to miss key constraints. Runtime can prepare structured summaries for Planner, keep necessary state, and move large objects into references that can be recovered outside the prompt.

Clarification needs product support. When Planner decides that information is insufficient, the frontend should show a specific question and keep the current Run state. After the user replies, the task continues under the same `run_id` instead of opening a new session. Clarification then becomes part of the workflow and audit chain.

Planner can also use tool-health information. If a tool is degraded or under maintenance, the Planner should choose an alternative path or ask the user to wait rather than repeatedly calling the same unhealthy tool. Tool health comes from Registry and observability systems; adding it to Planner context makes decisions closer to production reality.

In complex tasks, Planner may expose an intermediate plan for user confirmation. The user can correct a misunderstanding before the task consumes tools, and later execution becomes more predictable. This interaction costs one extra step, but it reduces the chance that a long task finishes in the wrong direction. Planner must also handle target changes during execution: the user may add a condition, revoke part of the request, or realize the original question was wrong. Runtime should let Planner receive the change event and decide whether to continue the current Run, create a child task, or cancel and restart. Treating every target change as a new chat message breaks the audit chain.

Plan reviews can reveal platform capability gaps. If Planner repeatedly takes long detours, the issue may be a missing tool or semantic-layer entry point rather than model weakness. Regularly reviewing failed plans and overly long plans can feed back into Registry and data-platform roadmap decisions. Planner traces are therefore also product evidence for platform evolution.

## Chapter Recap

Planner decides the next step, while Runtime executes and governs through the `PlannerDecision` handshake. ReAct fits exploratory, multi-hop, incomplete-information tasks, but it needs step limits, loop detection, and tool boundaries. Plan-and-Execute fits clearer paths and tasks requiring plan approval. State graphs can implement Planner internals, but they cannot replace Runtime's six states or platform checkpoints. Planner modes should be configurable, versioned, evaluated, and rollback-ready. Cost, retry boundaries, plan freezing, and replayable evidence determine whether a Planner can enter production.

## References

Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Yao, S., Zhao, J., Yu, D., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

Qu, C., Dai, S., Wei, X., Cai, H., Wang, S., Yin, D., Xu, J., & Wen, J.-R. (2025). Tool learning with large language models: A survey. *Frontiers of Computer Science*, 19(8), 198343. [https://doi.org/10.1007/s11704-024-40678-2](https://doi.org/10.1007/s11704-024-40678-2)

OpenAI. (n.d.). *Function calling*. OpenAI API documentation. [https://developers.openai.com/api/docs/guides/function-calling](https://developers.openai.com/api/docs/guides/function-calling)

LangChain. (n.d.). *LangGraph persistence*. [https://docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

Masterman, T., Besen, S., Sawtell, M., & Chao, A. (2024). The landscape of emerging AI agent architectures for reasoning, planning, and tool calling: A survey. [https://arxiv.org/abs/2404.11584](https://arxiv.org/abs/2404.11584)
