# Chapter 26 Agentic Workflow

---

Agentic Workflow enhancement mechanisms need explicit engineering constraints. Reflexion, Self-Refine, and Tree of Thoughts can improve complex-task quality, but they also amplify token cost and latency. Enterprises should make them scenario-specific, switchable, measurable local capabilities instead of enabling them by default. They sit on top of the Planner in Chapter 25, and their value must be validated through task quality, cost, and latency together.

Chapter 25 positioned Planner as the Runtime decision interface: in the `planning` state it calls `next_step()` and produces either FINISH or a Tool Call proposal, but it does not execute tools. ReAct and Plan-and-Execute answer how one step follows another. They do not answer a different production question: when the model chooses the wrong time window, a tool parameter fails, or the final report copy cannot pass brand review, should the platform allow extra reflection, report refinement, or branch search inside the same Run? Should these abilities be hardcoded in each Agent application, or should the platform control their switches, measurement, and audit? In this chapter, Agentic Workflow means decomposing Reflexion, Self-Refine, Tree of Thoughts, and similar methods into local enhancements that can be turned off, measured, and audited. They layer on top of Chapter 25 orchestration patterns. They do not replace the Runtime state machine.

A DataAgent in a multi-business-line enterprise already uses `planner.mode=react` by default: when a user asks why East China SKU sales declined, the Planner alternates reasoning and SQL calls. After launch, operations teams report two issues. First, the model occasionally chooses the wrong time window, and the team wants automatic reflection and retry after failure. Second, external reports often need several rounds of wording refinement before brand review passes. If every Agent application implements its own reflection loop, cost and audit standards will diverge quickly. A more controlled approach is to provide platform-level enhancement toggles: off by default, enabled per Agent configuration, and with all extra LLM turns counted in Step, Trace, `max_steps`, and Gateway quota controls.

The appeal of Agentic Workflow is that models can inspect themselves, rewrite output, and search branches. Production systems need a colder view. Each additional reflection or search round adds latency, cost, and uncertainty. Without switches, budgets, and audit records, these enhancements can turn a simple task into a long chain that is hard to explain. Reflexion, Self-Refine, and Tree of Thoughts suit different tasks. Report drafts can be polished. SQL generation failures can be retried under strict limits. Compliance approvals cannot let the model convince itself without new evidence. The platform should first decide whether the task allows multiple self-repair rounds, then decide which enhancement strategy is allowed.

---

## 26.1 Enhancement boundary above Planner

Agentic Workflow in this book refers to additional reasoning structures introduced inside or around the Planner decision loop to improve task quality: reflection trajectories, output self-revisions, and tree-of-thought searches. These structures are orthogonal to the orchestration patterns in Chapter 25. Orchestration patterns decide whether the system plans first and then executes, or reasons and acts step by step. Workflow enhancements decide whether a single-step decision may contain internal multi-round LLM calls or parallel candidates.

### 26.1.1 Division of responsibility between Planner and workflow enhancement

Table 26-1 compares Chapter 25 and this chapter from core question, configuration, and Runtime relationship. Orchestration patterns define step structure. Workflow enhancements decide whether extra LLM rounds are allowed inside or around a step.

*Table 26-1: Boundary comparison between Planner orchestration pattern (Chapter 25) and Agentic Workflow enhancement (Chapter 26). Source: This book.*

| Dimension | Chapter 25 Orchestration Pattern | Chapter 26 Agentic Workflow |
| --- | --- | --- |
| Core Question | What tool call to do next | Whether the current step/answer deserves further reasoning |
| Typical Configuration | `planner.mode`: `react` / `plan_and_execute` | Boolean toggles like `enhancement.reflexion` |
| Relationship with Runtime | One `next_step()` call per step | May call Gateway multiple times within one `planning` or insert refinement between steps |
| Default Strategy | Production agents must explicitly select mode | All enhancements are off by default |
| Auditing Unit | Step + Tool Call | Extra LLM calls must record Trace spans (Chapter 38) |

Agentic Workflow enhancements build on top of the Chapter 25 Planner and Chapter 22 Runtime. They do not change the six runtime states in Figure 22-1. Reflexion, Self-Refine, and ToT are encapsulated inside the Planner; Runtime only sees a longer current `next_step` and possibly a larger `llm_call_count`.

Although this boundary seems subtle, it is high-risk for system operation. If enhancements bypass the Runtime state machine, intermediate states disappear from SSE, checkpoints cannot detect how many planner rounds have run; task cancellations may not stop ongoing reflection or branch search; cost statistics only see one Step but not multiple Gateway calls behind it. Restricting enhancements inside the Planner and writing extra calls as Trace spans preserves a unified approach to cancellation, budgeting, replay, and charging.

### 26.1.2 Counting Standards (Three Counters)

The platform recommends distinguishing three counters to avoid ambiguity caused by whether Reflection advances the Step:

*Table 26-2: The three counters for measuring enhancement costs and their standards. Source: This book.*

| Counter | Typically Counts | Description |
| --- | --- | --- |
| `step_index` | Each completed Runtime `planning`->`executing` loop | Subject to hard constraint `max_steps` |
| `llm_call_count` | Extra Gateway calls for Reflection / Refine / ToT evaluation | Must be independently traced |
| `tool_call_count` | Successful paths of Registry `invoke` | Reflection LLM calls **do not count as Tool Calls** |

Reflection counts toward `llm_call_count` by default; whether it also advances `step_index` depends on platform policy (recommended to merge budget with Chapter 22 `max_steps`).

### 26.1.3 Applicability conditions for workflow enhancement

Enterprise deployments commonly fail around three boundary mistakes:

#### Treating Agentic Workflow as a more advanced Planner mode

`react` and `plan_and_execute` are orchestration strategies. Reflexion can be enabled together with ReAct: after a failed call is reflected on, the next ReAct round starts. It should not replace the Planner mode with a fourth mode.

#### Enabling Reflexion and allowing unlimited retries

Production must bind `max_reflection_rounds`, `max_steps` (Chapter 22), and Gateway budget; otherwise, one SQL syntax error might trigger dozens of reflections, overwhelming shared Gateways.

#### Running full-depth ToT before every Tool Call

Tree of Thoughts multiplies cost by branching factor and depth. Enterprise scenarios should limit it to cases such as high-risk write operations or offline report generation. It should not become the default path for ordinary question answering.

---

## 26.2 Reflexion

**Reflexion** enables an Agent to review its own trajectory (Thought / Action / Observation) after task failure or receiving a tool error. It generates a **natural language reflection summary**, which is then injected into the subsequent Planner context to improve the next step (Shinn et al. 2023). Unlike merely feeding the error string back to the Planner, Reflexion explicitly requires the model to summarize *"what I did wrong and what to avoid next time"*. Empirically, this approach improves success rates on tasks such as AlfWorld and HotPotQA (Shinn et al. 2023).

### 26.2.1 Industry Scenario

DataAgent calls `sql_executor` and receives a `TOOL_ARGUMENT_INVALID` error because the model wrote `last_week()`, a nonexistent function, when trying to express "last week." The runtime logs a `result` event into the Run history; if only the original error JSON is fed back to the Planner, the model might hallucinate the same function again. When Reflexion is enabled, the Planner first triggers a **Reflection LLM call** at the **planning entry of the same or next step** (not counting as a Tool Call), producing something like:

> "Use the built-in date function `date_trunc('week', current_date - interval '7 days')` instead of inventing a UDF."

This reflection summary is appended to the Working Memory (see Chapter 27). When writing the implementation suggestion, set `metadata["source"]="reflection"` to distinguish it from Tool `result`. Currently, the demo does not integrate RunLoop enhancement, so Working Memory only grows with Tool Calls. The Planner then proceeds to call the normal model to generate the `next_step`. Reflexion hooks inside `next_step` without changing the Run's six states (in the same Run loop as **Figure 22-2**):

1. RunLoop calls `next_step(run_ctx)`.
2. If the previous Tool failed and `reflexion` is enabled -> Gateway calls `reflect(trajectory, error)` -> summary appended to Working Memory.
3. Gateway calls `plan(messages + tools)` -> either `tool_call` or `finish`.
4. Returns `PlannerDecision` -> RunLoop in `executing` state `invoke` Registry.

Reflexion **does not replace** Tool retry logic: the runtime still classifies `TOOL_ARGUMENT_INVALID` errors according to Chapter 22 and decides whether to feed back to the Planner. Reflexion only improves the **quality of Planner feedback content**. Reflexion is best suited for errors the model can fix itself, such as parameter formats, time expressions, tool choice, or missing query clauses. It is not suitable for errors like permission denials, downstream system failures, or business rule conflicts. Continuing reflection on permission denials just causes the model to attempt to bypass restrictions; reflecting on database unavailability will not restore the service. Platforms should set narrow trigger conditions: Reflexion should only intervene when the error type implies "changing parameters or approach might succeed."

### 26.2.2 Production Parameters

Recommended configuration for Reflexion is as follows; production environments should start with conservative defaults and enable Reflexion per Agent as needed:

*Table 26-3: Recommended default values and explanations for enhancement mechanism parameters. Source: compiled for this book.*

| Parameter                | Recommended Default | Description                                               |
|--------------------------|---------------------|-----------------------------------------------------------|
| `enhancement.reflexion`  | `false`             | Agent-level switch                                        |
| `max_reflection_rounds`  | `2`                 | Maximum Reflection LLM calls per single run (**production config**; not implemented in current demo) |
| `reflect_on`             | `tool_error`, `empty_result` | Trigger conditions; use `always` with caution            |
| `include_tool_output`    | `true`              | Whether to include full tool output in reflection prompt (beware of PII) |

### 26.2.3 Reflexion Applicability Boundaries

**Misconception: Reflexion = Human Reviewer Agent.**
Reflexion is still **self-criticism by the same Agent**, with no independent approval chain. Compliance rejection processes must go through `waiting_human` (Chapter 30), and cannot be bypassed via Reflexion.

---

## 26.3 Self-Refine

**Self-Refine** enables the model to **iteratively improve its own output**: generate a first draft -> have the same model (or a stronger model) provide critique -> revise -> repeat until a stopping condition is met (Madaan et al. 2023). It is typically used for **polishing answers after no tools are involved or tool usage has ended**, such as report summaries, email drafts, or JSON structure corrections.

### 26.3.1 Differences from Reflexion

The table below compares the inputs, goals, and typical timing of Reflexion and Self-Refine; the two can be combined, but their triggers and risks differ:

*Table 26-4: Comparison of Reflexion and Self-Refine. Source: Compiled by the book.*

| Comparison Dimension | Reflexion | Self-Refine |
| --- | --- | --- |
| Input | Failure trajectory + environmental feedback | Model's own previous output |
| Goal | Improve actions/tool parameters | Improve text or structured answers |
| Typical Timing | Tool `failed` or result is empty | Before or after `finish=true` |
| Risk | Repeated erroneous tool calls | Over-polishing causing fact drift |

In industry scenarios, SQL results may be correct but operations require "conclusions to include one sentence for year-on-year and one for month-on-month comparison." The Planner has already `finish`ed but the answer only contains a month-on-month comparison; with `enhancement.self_refine` enabled, the Planner runs a **Refine sub-loop** (up to `max_refine_iterations` times) before submitting the final `PlannerDecision(finish=True)`, sending the current answer along with a brand checklist to Gateway each round until the critic marks `pass` or the iteration limit is reached. **Self-Refine can only improve expression and must not rewrite factual numbers in the tool output** (e.g., sales, year-on-year or month-on-month figures). Self-Refine forms an internal **draft -> critic -> revise** closed loop in the Planner, only submitting FINISH to Runtime after passing the critic (or reaching `max_refine_iterations`).

**Fact anchoring**: The critic prompt in Refine should require **not contradicting tool outputs**; otherwise the model might alter numbers just to improve fluency. The platform should inject **read-only** Tool Call summaries during the refine phase (see Chapter 27 Working Memory), instead of allowing the model to reissue SQL queries.

The product value of Self-Refine usually appears in reports, emails, and structured summaries instead of re-solving problems. It can make answers clearer and JSON output more schema-conformant, but it cannot change evidence. If the refine stage changes "month-on-month down 12%" to "significantly down about one-tenth" purely for fluency, it loses auditability in business or compliance analysis. Production systems should separate rewriteable sections from immutable facts, and when necessary have the critic only return issues lists, with final text composed deterministically by templates.

### 26.3.2 Configuration Points

- `enhancement.self_refine`: default `false`.
- `max_refine_iterations`: recommended `1-3`; report agents may go up to `5` and should be paired with evaluation (Chapter 39).
- `refine_target`: `answer` | `plan` (under Plan-and-Execute, can refine plan text before execution).
- Combine with **Structured Outputs** (Chapter 8): critic outputs JSON `{ "pass": bool, "issues": [...] }` for easier automation testing.

---

## 26.4 Tree of Thoughts

Tree of Thoughts (ToT) expands reasoning as a search tree: each node represents a partial solution or intermediate thought, with the model generating multiple candidates at each node. These candidates are then evaluated using heuristics or an LLM scoring function to select which branches to expand, continuing until an executable plan or final answer is found (Yao et al. 2023). Chapter 8 introduces ToT and Self-Consistency at the prompt layer as a structure for single completions; this chapter discusses ToT at the Agent layer, focusing on when ToT acts as an internal Planner search instead of ordinary Chain-of-Thought (CoT).

### 26.4.1 Division of Responsibilities with Chapter 8

ToT can operate at the prompt layer, Planner layer, and Runtime layer. The following table clarifies the scope and responsibilities at each layer:

*Table 26-5: Division of roles between Self-Consistency in Chapter 8 (structured output layer) and this chapter. Source: compiled by the authors.*

| Layer         | Responsibility                          | This Chapter / Chapter 8            |
|---------------|---------------------------------------|-----------------------------------|
| Prompt Layer  | `n` samples per request, plus voting  | Chapter 8 Self-Consistency         |
| Planner Layer | Maintain branches across multiple steps, backtracking, pruning | This Chapter ToT                 |
| Runtime Layer | Execute Tool Calls only on **selected branches** | Chapter 22 unchanged              |

Example: High-risk automatic price adjustment scenario. Before writing with the `price_update` tool, the Agent's Planner uses ToT to generate three pricing strategy branches. An **evaluation model** scores them (compliance, margin, competitive price). Only the highest scoring branch delivers its first Tool Call to Runtime. Branches not selected **must not** cause side effects. This contrasts with AutoGPT's "think-while-doing" pattern.

!!! warning "Branches not selected must not execute tools"
    ToT search happens entirely within the Planner; only the **final selected branch** can produce a `PlannerDecision` including a Tool Call. Non-selected branches must not invoke Registry `invoke`.

### 26.4.2 ToT Parameters and Cost

The token cost of ToT is determined by the product of its branching factor and depth. The following table provides recommended default values for production:

*Table 26-6: Meaning and cost-related production recommendations of Tree of Thoughts parameters. Source: compiled by the authors.*

| Parameter                  | Meaning                      | Production Recommendation            |
|----------------------------|------------------------------|------------------------------------|
| `enhancement.tree_of_thoughts` | Master toggle               | Default `false`                    |
| `tot_branching`            | Candidates per node           | Within `3`                         |
| `tot_depth`                | Maximum depth                | `2-3`                             |
| `tot_evaluator`            | `llm` or `rule`              | Use `rule` + policy double-check before write operations |
| `tot_budget_tokens`        | Max tokens per ToT run       | Aligned with Gateway quota         |

After ToT search completes, only the **selected branch** produces Tool Calls; non-selected branches are pruned inside the Planner's memory (`tot_branching` × `tot_depth` must be controlled by Gateway quotas, see Chapter 38). ToT's **parallel candidates** increase Gateway QPS; platforms should implement **tenant-level quotas** and alerting for `enhancement.tree_of_thoughts` (Chapter 38).

ToT should avoid presenting the search process as a definitive conclusion. Multiple candidate branches represent model exploration, not business-validated plans. Non-selected branches must not appear in final answers or be written into long-term Memory. For pricing, permissions, contracts, and compliance tasks, branch evaluation should combine rule-based and policy checks instead of relying solely on another LLM scoring pass. This makes ToT a controlled decision support tool instead of entrusting high-risk judgments to self-assessing models. Therefore, the default recommended place for ToT is offline analysis, draft reporting, or limited pre-evaluation before high-risk actions, not a fixed pre-step for every ordinary dialog. Leaving it off by default is the practical and manageable starting point.

---

## 26.5 AutoGPT-style autonomy and production thresholds

AutoGPT and similar open-source projects (BabyAGI, AgentGPT, etc.) have popularized an end-to-end narrative based on goal decomposition, autonomous loops, long-term memory, and toolchains: give the agent a high-level goal, and it breaks down tasks, searches the web, writes files, then sets new goals autonomously. The demos are intuitive, but if an enterprise DataAgent platform copies this approach directly, it often runs into the following structural issues (Significant Gravitas 2023; Wang et al. 2024):

### 26.5.1 Key Critiques

1. **Goal Drift**
   Without external validation, the agent endlessly expands the scope to "complete sub-goals" (e.g., further competitor research, additional blog posts), often unrelated to the user's original query. Production requires **Run-level input controls plus max_steps** hard boundaries (Chapter 22), instead of an unlimited `while True` loop.

2. **Uncontrollable Side Effects**
   AutoGPT-style loops commonly assume **tool use is allowed at every iteration**. Enterprises demand **Policy enforcement upstream** (Chapter 50), **human-in-the-loop (HITL) for write operations** (Chapter 30), and **tool registry version pinning** (Chapter 23). Fully autonomous operation conflicts with all three requirements.

3. **Unpredictable Cost and Latency**
   Autonomous loops lack **step and token budget controls**, so a single "research-style" task might consume millions of tokens. Platforms must **meter Reflexion / Self-Refine / ToT steps** and fold them into FinOps governance (Chapter 46).

4. **Memory Pollution**
   Persistently writing unverified intermediate conclusions into long-term memory (Chapter 27) risks error amplification in later runs. The AutoGPT method of "remembering everything" violates enterprise requirements for **deletability and auditability**.

5. **Lack of Evaluation and Replay**
   Autonomous agents struggle to answer "Why was incorrect output given last week?" Run / Step / Tool Call + Trace logging (Chapters 22 and 38) are indispensable compliance basics, not optional.

### 26.5.2 Production Thresholds (Platform Checklist Summary)

When reducing the AutoGPT paradigm to a Planner-enhanced model, the table below lists the production thresholds the platform must satisfy:

*Table 26-7: Thresholds to meet before enhancement mechanisms enter production. Source: Compiled by this book.*

| Threshold        | Description                                                                                 |
|------------------|---------------------------------------------------------------------------------------------|
| Bounded Run      | `max_steps`, run timeout, cancellation APIs                                                |
| Enhancement Off by Default | `PlannerEnhancementFlags` all set to `false`                                       |
| Explicit Enable  | Agent YAML toggle switches per feature + approval records                                  |
| Side Effect Gateway | Registry + Policy enforcement; ToT executes only selected branches                        |
| Memory Governance | Long-term memory includes source and timestamp; supports deletion (Chapter 27)            |
| Observability    | Independent tracing spans per reflect / refine / tot_eval step                             |
| Human-in-the-Loop | High-risk operations remain `waiting_human`, no fully autonomous execution                 |

AutoGPT-style patterns are useful for personal experiments and prototypes. Enterprise platforms should reduce them to configurable, toggleable, and measurable Planner enhancements, such as Reflexion, Self-Refine, and ToT, while keeping the Runtime six-state model and audit path unchanged. Enterprises can still use autonomous loops, but they should not be the default execution model. Production-ready designs usually break "autonomy" into controlled segments: a plan may be revised once, a failure may trigger one reflection, a report may be refined once, and a high-risk write operation may go through limited branch evaluation. Each segment has trigger conditions, budgets, stop criteria, and audit records. This preserves quality gains for complex tasks without turning an ordinary query into an unpredictable long-running job.

---

## 26.6 Runtime boundary for Planner enhancement mode

The current `mini-platform/core/planner/config.py` defines `PlannerEnhancementFlags`, but it only contains three boolean switches. Subloops such as `reflect()`, `refine_answer()`, and `tot_search()` are not integrated into the demo RunLoop. This section separates what exists in the codebase from the production interface that the platform should eventually provide.

### 26.6.1 Implementation Entry for Planner Enhancement

```
mini-platform/core/planner/
├── __init__.py              # create_planner, PlannerEnhancementFlags, PlannerConfig
├── config.py                # PlannerEnhancementFlags (three boolean switches)
├── react_planner.py         # Chapter 25 ReAct rule Demo
├── plan_execute.py          # Chapter 25 Plan-and-Execute rule Demo
└── planner.py               # create_planner factory

# Production extension targets (not present yet):
# enhancements.py            # reflexion / self_refine / tot submodules
```

Enhancements are off by default. `RunLoop` does not need to know the internal details of Reflexion; it reads `PlannerDecision` and observes planning latency. The existing switch definition in `core/planner/config.py` is intentionally small:

```python
@dataclass
class PlannerEnhancementFlags:
    """Agentic Workflow enhancement switches; default all False in production."""

    reflexion: bool = False
    self_refine: bool = False
    tree_of_thoughts: bool = False
```

For production implementation, upper limits such as `max_reflection_rounds`, `max_refine_iterations`, `tot_branching`, `tot_depth`, and `tot_budget_tokens` should enter `PlannerConfig`. `next_step` also needs explicit accounting for `llm_call_count`, token budget, and Trace spans. Without that accounting, a failed enhancement loop is hard to attribute.

### 26.6.2 Release Gates for Enhancement Mechanisms

Agentic Workflow release gates cannot look only at whether the answer appears better. Enhancements change cost, latency, explainability, and cancellation semantics. A usable release gate should include four kinds of evidence: offline evaluation shows quality improvement for the target task; online canary keeps p95 latency and token cost within limits; Trace can expand every `reflect`, `refine`, and `tot_eval` span; failures exit cleanly instead of continuing self-correction.

Release should be staged. First, enable the enhancement on offline samples and compare it with the baseline Planner. Second, run shadow mode to record extra LLM calls without changing user-visible results. Third, canary on low-risk Agents and a small number of tenants. Fourth, allow business lines to enable the feature through configuration. Any stage with cost explosion, cancellation failure, factual drift, or approval bypass should roll back to the base Planner.

Enhancements also need stop conditions. If Reflexion cannot fix the same tool-argument error after two rounds, it should stop and return an explainable failure. If Self-Refine cannot pass the critic after several rounds, it should return a marked draft or enter human review. If ToT branch scores are too close, the platform should degrade to a conservative plan instead of forcing a weak choice. Stop conditions matter more than the enhancement method itself because they decide whether the system can stop under uncertainty.

### 26.6.3 Failure Recovery and Human Takeover

Failure recovery must return to Runtime instead of staying inside Planner. If a user cancels a Run while reflection, refinement, or ToT evaluation is in progress, the inner loop should receive the cancellation signal, stop further Gateway calls, and mark the Run as `cancelled` or `failed`. If cancellation only stops the outer Runtime while the inner enhancement loop continues, the frontend will show a finished task while the backend keeps spending tokens and Trace contains unexplained tail calls.

For DataAgent-style analysis, recovery should follow risk tiers. A read-only query failure may allow Reflexion to adjust field names, time windows, or filters. A weak report draft may allow Self-Refine to improve structure and wording. A failed ToT evaluation before a high-risk write operation should not automatically choose another execution path; it should enter human confirmation. Enhancements should expand the system's ability to repair safe errors, not expand execution authority.

Human takeover should show compressed evidence, not raw model thoughts. Reviewers need to know how many rounds ran, which error types appeared, which tools were called, which branches were abandoned, and why the system stopped. Full intermediate reasoning can overload reviewers and expose strategy prompts; hiding everything makes review impossible. A stable pattern is to store full Trace, show a structured summary in the frontend, and let auditors inspect detailed spans when necessary.

### 26.6.4 Enhancement Switch Configuration Example

This chapter's code baseline has not implemented independent enhancement subloops. The commands below verify that Run boundaries remain stable when enhancements are off; they do not prove that Reflexion itself is wired into the Runtime.

```bash
cd mini-platform
pytest tests/test_multi_agent_workflow_run.py tests/test_runtime.py -q
python3 projects/multi-agent-workflow/run.py start   # Observe full Run without reflexion enabled
```

`PlannerEnhancementFlags` is defined in `core/planner/config.py`. The following YAML shows the target shape for Agent configuration:

```yaml
planner:
  mode: react
  enhancement:
    reflexion: true
    self_refine: false
    tree_of_thoughts: false
    max_reflection_rounds: 2
```

The following snippet illustrates the target wiring and should not be copied as runnable code. `RunLoop` construction still needs a `registry` (Chapter 23), and the Reflexion subloop is not integrated.

```python
from core.planner import PlannerConfig, PlannerEnhancementFlags, create_planner
from core.runtime import RunLoop

config = PlannerConfig(
    enhancements=PlannerEnhancementFlags(reflexion=True),
)
# Production requires: registry = build_workflow_registry() or equivalent ToolRegistry
loop = RunLoop(planner=create_planner(config))  # Missing registry -> TypeError
loop.run(agent_id="data-agent", user_input="...", context={"tenant_id": "retail-demo"})
```

### 26.6.5 Switch Boundary and Future Evolution

*Table 26-8: Coverage of enhancement capabilities in this chapter's Demo. Source: Compiled from this book.*

| Capability                           | Description               | This Chapter Demo |
|------------------------------------|---------------------------|-------------------|
| `PlannerEnhancementFlags` three boolean switches | Configuration entry defined | ✓                 |
| Reflexion / Self-Refine / ToT subloops             | `enhancements.py`           | ☐                 |
| Linkage with `max_steps` / `llm_call_count`         | Measurement and truncation  | ☐                 |
| Trace segmented spans                              | `planner.reflect` / `planner.refine` / `planner.tot` | ☐          |
| Gateway budget                                    | Tenant-level token / call limits | ☐                 |
| ToT executes only selected branches               | Non-selected branches have no Tool Call | To be implemented |
| Checkpoints include enhancement state              | Integration with Chapter 27 | ☐                 |

The current demo covers configuration entry points, not the full enhancement pipeline. A production version should add independent submodules for Reflexion, Self-Refine, and ToT, bind those modules to `max_steps` and `llm_call_count`, write separate Trace spans, and enforce Gateway budgets. ToT must evaluate branches inside Planner and only emit one selected Tool Call to Runtime. Checkpoint recovery also needs to preserve enhancement state together with Memory state from Chapter 27, otherwise recovery may repeat reflections or lose the reason a branch was rejected.

### 26.6.6 Failure Convergence for Enhancement Loops

#### Reflexion and Tool Retry Counters Explode

Symptom: `TOOL_ARGUMENT_INVALID` triggers Registry feedback to Planner and Reflexion, which triggers model retries, resulting in 6 Gateway calls within a single step.
Fix: Reflexion is constrained by `max_reflection_rounds`; merge configuration with feedback Planner limits from Chapter 22. This failure is usually caused by two recovery mechanisms that do not know about each other. Runtime feeds tool errors back to Planner, Reflexion modifies the plan, and Gateway only sees repeated model calls. The implementation should put recovery actions under the same budget object: one tool failure can trigger at most one reflection; if the reflected call still fails, Runtime should end, degrade, or enter human review according to policy.

#### Self-Refine Rewrites SQL Conclusions

Symptom: After polishing, numbers in the answer are inconsistent with the `sql_executor` results.
Fix: critic enforces "numbers must reference tool output"; Eval sampling inspection (Chapter 39). Do not rely only on a prompt sentence that says "do not change numbers." A safer design locks numeric facts, metric versions, and EvidenceRef values into structured fields, then allows refinement only on explanatory prose. The final renderer combines factual fields and expression fields. Even if the model tries to make the answer smoother, it cannot overwrite evidence fields.

#### ToT Executes Tools on All Parallel Branches

Symptom: Three branches all triggered `price_update`, causing triple rewrites.
Fix: Runtime only executes **one** Tool Call actually submitted by the Planner; ToT search is done inside Planner, branches exist only as in-memory objects. ToT branches should be candidate plans, not candidate executions. The model or rules may score all branches, but only the selected branch can produce a `PlannerDecision`. If a team wants to compare multiple real execution outcomes, it should design an explicit experiment, sandbox, or approval flow instead of using ToT as a hidden execution fan-out.

#### AutoGPT-Style Autonomous Loops Enter RunLoop

Symptom: Planner internally performs a `while not done` loop without step boundaries, leading to no state updates for long periods in SSE.
Fix: Any enhancement subloop must **yield step boundaries** or be constrained to observable spans inside planning state, forbidding circumvention of `max_steps`. This also affects user experience. If the frontend only shows "thinking" for a long period, users cannot tell whether the system is retrieving, executing tools, waiting for approval, or stuck in a loop. Enhancement subloops should at least write Trace spans and expose stage status through events when needed. Otherwise, a sophisticated planning loop becomes an uninterruptible, unexplainable, and hard-to-bill task.

---

Enhancement strategies should prove value with task-level metrics before release. Accuracy, latency, cost, failure rate, and human-review reduction need to be evaluated together. A few successful examples can easily overstate the benefit of self-correction. Stop conditions are part of the release decision: when two revisions do not improve quality, tool errors repeat, evidence does not change, or the budget approaches the limit, Planner should stop self-correction and move to clarification, human review, or failure return.

Reflexion should distinguish error sources. Permission denial cannot be fixed by more reflection; failed data quality checks should not be papered over with model explanation; unclear report wording may benefit from revision. Self-Refine suits artifact-generation tasks, but it must preserve revision history so reviewers can see whether the model improved expression or changed facts. ToT amplifies cost and latency, so it should be limited to high-value reasoning tasks with visible branch summaries and evidence-based selection.

Enhancements also affect product experience and operations. Short interactions may allow one quick self-check; long reports, batch evaluation, and complex analysis can move into background execution with deeper refinement or search. The platform should offer independent switches by tenant, task, or Agent so a costly or faulty strategy can be disabled without rolling back the whole application. Strategy configuration, version, and hit records belong in Trace for later incident review.

## 26.7 Workflow Release Ledger and Failure Replay

The release unit for Agentic Workflow should be a replayable strategy bundle, not a prompt edit or a single Planner flag. The ledger should record task type, enabled enhancement strategies, maximum loop count, stop conditions, budget limit, model route, tool allowlist, evaluation-set version, and canary scope. This matters during incident review. A report task may degrade because the model changed, the Reflexion trigger became too broad, Self-Refine was allowed to rewrite a larger portion of the artifact, or tool error feedback changed shape. If the ledger only says that enhancement workflow was enabled, the team cannot locate the layer that introduced the risk.

Failure replay should cover both normal and abnormal paths. The normal path checks whether a strategy reduced human rework, improved evidence completeness, and stayed within the latency budget. The abnormal path checks whether tool failure caused repeated reflection, whether the reviser changed factual fields, whether branch search created multiple side effects, and whether budget exhaustion moved the task to clarification or human review. Replay material should preserve the original plan, the reason for each revision, rejected candidate branches, the final selection reason, and the user-visible artifact. Saving only the final answer cannot show whether the enhancement helped, and it cannot explain why cost increased.

The release process also needs local disablement. A contract-review task for one tenant may justify one evidence-checking pass, while a customer-service classifier should execute directly. A strategy may work for Chinese reports yet rewrite facts in English summaries. The platform should control strategy use by task, tenant, risk level, and artifact type, with hit records written into Trace. When cost, latency, or quality shifts, the team can disable the specific strategy bundle instead of rolling back the entire Agent application. Workflow enhancement is mature when every added layer has benefit evidence, stop conditions, and a rollback path.

## 26.8 Operating Review For Agentic Workflow

After Agentic Workflow goes live, review should focus on which steps should remain fixed and which can be left to model judgment. If every branch is hard-coded, the system returns to traditional workflow and cannot handle missing information or abnormal paths. If every decision is left to the model, approval, responsibility, and recovery become unstable. Operating review should inspect real Runs: which nodes are often skipped, which nodes often trigger human takeover, which model decisions cause rework, and which rules are so strict that users route around them.

Review material should include workflow version, Planner decision, node state, tool calls, human approval, exception recovery, and final artifact. If one node always follows the same path, it may be turned into a rule. If a rule is often overridden by humans, the model may need more context or the admission condition may need adjustment. If an exception class always goes to human takeover, the platform can add automatic recovery or clearer user copy. The value of Agentic Workflow comes from adjusting this boundary over time.

Operating review also serves organizational collaboration. Business owners confirm which nodes require human judgment. Platform teams maintain state machines and recovery policy. Security teams own high-risk gates. Evaluation teams turn failure paths into samples. Every change should enter version records and state its impact on SLO, cost, user waiting, and risk. Workflow can then absorb Agent flexibility while keeping governance intact.

## 26.9 Joint Acceptance Between Workflow And Runtime

Agentic Workflow should not be accepted only by the process design team or only by the Runtime team. Process designers care whether business nodes are complete. Runtime teams care whether state can recover. Security teams care whether high-risk actions are blocked. Frontend teams care whether users understand the current state. Joint acceptance should put these views into the same sample set.

Acceptance samples should cover normal completion, user-added information, tool failure, approval timeout, user cancellation, duplicate submission, state recovery, and final archiving. Each sample should state workflow node, Runtime state, visible UI, Trace record, and recovery action. If any layer cannot explain the current fact, the interface between Workflow and Runtime is not stable enough.

Joint acceptance also reduces responsibility disputes. Business owners fix wrong process nodes. Runtime fixes failed state recovery. Security and platform teams fix missed review on dangerous actions. Frontend and copy teams fix user misunderstanding. Once responsibility is written into acceptance samples, Agentic Workflow becomes a production chain maintained by several teams.

## 26.10 Stop conditions for enhanced workflows

Agentic Workflow needs stop conditions. Reflection, rewriting, branch search, and self-repair all add model calls and task time. Without stop conditions, the system may keep revising low-value tasks or produce more explanation when evidence is missing. The design should state maximum iteration count, which errors can retry, which errors require human review, and which tasks should fail directly.

Stop conditions should enter Runtime and Trace. Each iteration records reason, input difference, output difference, cost, and final state. If repeated revision does not improve the result, the platform should be able to see whether the problem comes from prompt, tool, evidence, or task definition. Enhanced workflows then serve quality improvement instead of hiding failure in a longer execution chain.

## 26.11 Release and rollback boundary for workflow strategies

Enhanced workflow strategies should be released as versioned runtime policy, not as scattered prompt edits. A release should state which tasks can use reflection, which artifacts can be refined, which branches can be searched, and which tool calls remain outside model discretion. The same record should include budget limits, stop conditions, model route, evaluation set, owner, and rollback target. Without this record, a later quality issue can look like a model problem even when the actual change was a wider refinement scope or a different ToT evaluator.

Rollback also needs a smaller unit than the whole Agent application. If Self-Refine starts altering report facts, the platform should be able to disable that strategy for report artifacts while leaving ordinary planning unchanged. If ToT increases cost for one tenant, the platform should restrict branch search for that tenant without rolling back Runtime. If Reflexion improves tool recovery but causes repeated retries on permission failures, the fix may be a narrower trigger condition instead of removing all reflection. Strategy-level rollback keeps useful capability available while containing the failure surface.

Release review should compare enabled and disabled runs on the same sample set. The review should inspect task completion, evidence preservation, latency, cost, human review, and final artifact acceptance. A strategy that improves wording but loses EvidenceRef should fail. A strategy that reduces manual rework but doubles latency may be accepted for asynchronous reports and rejected for interactive chat. The decision should be tied to task type and user expectation, not to a generic quality score.

The workflow ledger should remain connected to Chapter 38 Trace and Chapter 39 Eval. Every enhanced run should record the strategy version and the reason it fired. Failed runs should feed samples back into the evaluation set with labels such as repeated reflection, factual rewrite, branch side effect, budget exhaustion, or unclear stop condition. Over time, the platform can decide which strategies are worth keeping for which tasks. This prevents enhancement mechanisms from becoming hidden complexity that survives only because nobody remembers why it was enabled.

## 26.12 User expectation management for enhanced paths

Enhanced workflows change how users perceive task progress. In ordinary chat, users usually expect an immediate answer. After Reflexion, Self-Refine, or ToT enters the path, the system may call tools, inspect evidence, revise artifacts, and compare branches before answering. If the frontend still shows only "generating", users cannot tell whether the system is collecting evidence or stuck in repeated calls. Enhanced paths need to translate internal steps into understandable progress states.

Expectation management should follow task risk. Low-risk writing tasks can show lightweight states such as draft refinement. Report generation should expose evidence collection, chart generation, fact review, and pending human confirmation. High-risk operations should identify approval, execution, and rollback windows. The message does not need to expose full Planner internals, but it should tell users why the task has not ended and whether they can cancel, add information, or move to human handling.

Expectation management also affects stop conditions. If users see the system "reflecting" three times in a row, they may suspect it is stuck. If retries happen silently, users may submit the same task again. Runtime should map enhancement steps to stable events, and the frontend should present progress from those events. Trace fields for strategy version, trigger reason, and stop reason should align with the user-visible state. During incident review, the team can then distinguish strategy design problems, runtime delay, and interaction wording.

A first version can define a small set of common states for enhanced paths: collecting evidence, revising artifact, comparing candidates, waiting for approval, completed with degradation, and needs human handling. Each state maps to a Runtime event and cancellation rule. Agentic Workflow then remains explainable in the user experience while the backend grows more capable. Much of enterprise Agent usability comes from users knowing what the system is doing and when they should intervene.

## 26.13 Responsibility review for enhanced workflows

After Agentic Workflow introduces Reflexion, Self-Refine, or Tree of Thoughts, the system creates more intermediate judgments. Each reflection, correction, branch choice, and self-evaluation affects the final execution path. The platform should keep more than the final answer. It should record which intermediate judgments were accepted, which were discarded, why execution continued, and why it stopped. Otherwise, when users challenge a result, the team can only say that the model chose it, without assigning the issue to strategy, samples, or human ruling.

Responsibility review should distinguish three judgment types. The first is model self-evaluation, such as deciding that an answer is incomplete. The second is strategy judgment, such as stopping after the maximum retry count. The third is business judgment, such as whether a solution matches an approval policy. The model can participate in the first two categories, but the third should be handled by business rules, human reviewers, or explicit policy. If business judgment is left to model self-evaluation, the workflow becomes flexible while responsibility becomes unclear.

A first version can maintain a review package for enhanced workflows: user goal, candidate paths, accepted path, stop condition, tool results, human intervention points, and final output. Once this package enters Trace, teams can tell whether a problem came from planning, reflection, tools, business policy, or user input. Enhanced workflows then become explainable and replayable operating mechanisms instead of longer automatic chains.

## 26.14 Production evidence for enhanced workflows

After enhanced workflow reaches production, a successful demo is not enough evidence. The platform needs stable fields for plan versions, stop conditions, reflection records, tool calls, and human takeover events, and those fields should connect to release records, Trace, evaluation samples, and incident notes. When a production issue appears, teams can follow one set of facts to understand scope, ownership, and repair order instead of stitching together model logs, business logs, and verbal explanations.

This evidence also connects the surrounding chapters. It links to Chapter 25 on Planner, Chapter 38 on Trace, and Chapter 39 on Eval: upstream capabilities provide assumptions, downstream capabilities consume the result, and governance capabilities preserve evidence and review decisions. If these materials do not share identifiers and versions, the production system splits apart. Business owners see user complaints, platform owners see system errors, and security or compliance teams see explanations written after the fact. That separation makes it hard to decide whether the issue came from data, model behavior, tool contracts, workflow state, or organizational ownership.

Common production risks include self-revision without a stop condition, reflection text that cannot explain the decision, tool retries that inflate cost, and users assuming approval has already happened. These risks are less visible during demos because demos usually exercise the successful path. Production users bring boundary cases, repeated requests, permission changes, and long-running state. The platform team should turn such failures into release samples. Some samples should block launch, some can be handled by degradation, and some require the business owner to accept the remaining risk with a review date.

The scenario owner should sample failed Runs every month and write strategy changes, new samples, and degradation conditions back to the release ledger. The record can stay compact, but it should include time, version, owner, sample, action, and the next review condition. Without those fields, review remains informal experience. With them, one production issue can become material for later releases, evaluation suites, and training.

A first platform version can start with a small set of high-risk paths. Choose flows with high traffic, high business impact, or sensitive data, require an evidence package for each change, and then expand the practice to ordinary scenarios. This keeps the capability at the engineering level: runnable, explainable, and recoverable.
## 26.15 Withdrawable release for enhancement strategies

Enhancement strategies need withdrawal support. Reflexion, Self-Refine, and Tree of Thoughts change the number of model turns, the order of tool calls, and user waiting time. A strategy upgrade can improve average success while making some high-risk tasks slower, more expensive, or harder to explain. Release should state scope, kill switch, rollback version, and known unsuitable samples.

Withdrawal also matters for user experience. When an enhancement strategy runs for a long time, the frontend should show whether the system is planning, reflecting, searching candidates, or executing. After user cancellation, Runtime should stop later tool calls. After strategy withdrawal, historical Runs should still preserve the version used at the time. Otherwise review sees only the result, not why the system chose a longer reasoning path.

A first version can manage enhancement strategy as a releaseable asset. Each strategy has version, samples, cost ceiling, stop condition, applicable task, and withdrawal condition. Chapter 26 then moves beyond algorithm description and explains how these methods are controlled inside an enterprise platform.

## Chapter Recap

1. Chapter 25, Orchestration Patterns, and Chapter 26, Agentic Workflow, are orthogonal: the former defines step structure; the latter defines whether reflection, refinement, or branch search is applied.
2. **Reflexion** improves Planner output quality after failures; **Self-Refine** improves final-draft quality; **ToT** selects strategies under controlled search. All three are disabled by default.
3. **AutoGPT-style full autonomy** conflicts with Run boundaries, Policy, HITL, and auditing; enterprises should **downscope it to measurable augmentation** instead of treating it as default behavior.
4. **`PlannerEnhancementFlags`** is the platform-wide unified toggle; the six Runtime states remain unchanged, and checkpoints must include enhancement and Memory state.
5. All augmentation LLM calls must be **independently observable** and subject to dual constraints from the Gateway and `max_steps`.

---

- Should new Agents default to `enhancement.* = false`?
- Does enabling Reflexion or ToT require **tenant quotas and approval**?
- Does Self-Refine anchor to tool output to prevent factual drift?
- Does ToT guarantee that **exactly one** Tool Call enters `executing`?
- After checkpoint recovery, does the Planner avoid "amnesia" or "repeated reflection"?

---

- [Chapter 25: Planner and Orchestration Patterns](ch25-planner.md)
- [Chapter 27: Memory System](ch27-memory.md)
- [Chapter 30: Human-in-the-Loop and Long-Running Tasks](ch30-human-in-the-loop.md)
- [Chapter 38: Agent Trace and Session Replay](../../part07-observability-eval/en/ch38-trace.md)
- [Chapter 8: Structured Output and Prompt Engineering](../../part02-model-inference/en/ch08.md)
- `mini-platform/projects/multi-agent-workflow/README.md`
- `mini-platform/core/planner/config.py`

---

## References

Shinn, N., Cassano, F., Gopinath, R., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS*. arXiv:2303.11366. [https://arxiv.org/abs/2303.11366](https://arxiv.org/abs/2303.11366)

Madaan, A., Tandon, N., Gupta, P., et al. (2023). Self-Refine: Iterative refinement with self-feedback. *NeurIPS*. arXiv:2303.17651. [https://arxiv.org/abs/2303.17651](https://arxiv.org/abs/2303.17651)

Yao, S., Yu, D., Zhao, J., et al. (2023). Tree of Thoughts: Deliberate problem solving with large language models. *NeurIPS*. arXiv:2305.10601. [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601)

Significant Gravitas. (2023). *AutoGPT*. GitHub. [https://github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)

Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Yao, S., Zhao, J., Yu, D., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*. arXiv:2210.03629. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

Li, X. (2025). A review of prominent paradigms for LLM-based agents: Tool use, planning (including RAG), and feedback learning. In *Proceedings of COLING 2025*. arXiv:2406.05804. [https://arxiv.org/abs/2406.05804](https://arxiv.org/abs/2406.05804)

Masterman, T., Besen, S., Sawtell, M., & Chao, A. (2024). The landscape of emerging AI agent architectures for reasoning, planning, and tool calling: A survey. arXiv:2404.11584. [https://arxiv.org/abs/2404.11584](https://arxiv.org/abs/2404.11584)
