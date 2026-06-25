# Chapter 26 Agentic Workflow

---
## Chapter Summary

This chapter discusses the engineering boundaries of Agentic Workflow, explaining how enhancement mechanisms such as Reflexion, Self-Refine, and ToT can be integrated into the platform as locally scoped capabilities that are switchable and measurable. These mechanisms improve the quality of complex tasks but multiply token consumption and latency, so enterprises should not enable them by default. Instead, they should be treated as scenario-specific toggles with measurable benefits. This chapter delineates their boundaries in relation to the Planner from Chapter 25, describes the types of tasks each mechanism is suited for, and explains how to evaluate whether the additional cost results in quality improvements.
## Key Terms

Agentic Workflow, Reflexion, Self-Refine, Tree of Thoughts, Cost Measurement, On-Demand Switching
## Learning Objectives

- Be able to distinguish the boundaries between Agentic Workflow enhancement mechanisms and Planner orchestration patterns.
- Be able to explain the suitable task types and costs for Reflexion, Self-Refine, and ToT.
- Be able to design switches and metrics for enhancement mechanisms to avoid default full activation that increases cost and latency.
- Be able to evaluate whether the quality improvement brought by an enhancement mechanism justifies the additional tokens and delay.

---
## Opening Scenario

Chapter 25 positions the **Planner** as the decision interface of the Runtime: in the `planning` state it calls `next_step()`, producing either a FINISH signal or a Tool Call proposal, but never executing tools directly. ReAct and Plan-and-Execute answer the question of **"how to orchestrate one step at a time."** However, Chapter 25 leaves another question unanswered:

When the model selects the wrong time window, a tool call returns a parameter error, or a final report draft fails brand review, does the platform allow the Planner to **perform additional reflection, polish a report, or explore alternative branches within the same Run**? Are these capabilities hardcoded into individual Agent applications, or does the platform provide centralized toggles, metering, and auditing?

The **Agentic Workflow** discussed in this chapter refers to decomposing capabilities such as Reflexion, Self-Refine, and Tree of Thoughts into **opt-in, metered local enhancements** layered on top of the orchestration patterns from Chapter 25—not replacing the Runtime state machine, and not granting Agents the freedom to loop indefinitely.

A multi-business-unit enterprise DataAgent already defaults to `planner.mode=react` following Chapter 25: when querying East China SKU decline, the Planner alternates between reasoning and SQL calls. After going live, operations teams reported two categories of problems: first, the model occasionally selects the wrong time window, and teams want **automatic reflection and retry on failure** (Reflexion); second, externally facing report copy requires **multiple rounds of polishing** before passing brand review (Self-Refine). If the platform hardcodes these capabilities inside individual Agent applications, each team ends up implementing its own "reflection loop," making cost tracking and audit standards impossible to unify. This chapter introduces **platform-level enhancement toggles**: disabled by default, enabled per-Agent via configuration, with all additional LLM turns counted toward Steps and subject to `max_steps` limits and Gateway quota constraints.

The chapter proceeds as follows: §1 defines the boundary with Chapter 25; §2 introduces Reflexion; §3 covers Self-Refine; §4 covers Tree of Thoughts; §5 critiques the AutoGPT-style paradigm and establishes production readiness thresholds; §6 closes with the `core/planner/` enhancement mode implementation.

---
## 26.1 The Boundary Between Agentic Workflow and Chapter 25

**Agentic Workflow** in this book refers to the **additional reasoning structures** introduced inside or outside the Planner decision loop to improve task quality—such as reflection trajectories, output self-revisions, and tree-of-thought searches. These are orthogonal to the **orchestration patterns** described in Chapter 25: orchestration patterns determine whether to "plan first, then execute" or to "think and act simultaneously"; workflow enhancements decide whether a single-step decision allows internal multi-round LLM calls or parallel candidates.

### 26.1.1 Comparison Table

The table below compares Chapter 25 and Chapter 26 from dimensions like core questions, configuration options, and relationship with runtime. When reading the table, remember: **orchestration patterns define step structure, while workflow enhancements determine whether extra LLM rounds are allowed**.

*Table 26-1: Boundary comparison between Planner orchestration pattern (Chapter 25) and Agentic Workflow enhancement (Chapter 26). Source: This book.*

| Dimension | Chapter 25 Orchestration Pattern | Chapter 26 Agentic Workflow |
| --- | --- | --- |
| Core Question | What tool call to do next | Whether the current step/answer deserves further reasoning |
| Typical Configuration | `planner.mode`: `react` / `plan_and_execute` | Boolean toggles like `enhancement.reflexion` |
| Relationship with Runtime | One `next_step()` call per step | May call Gateway multiple times within one `planning` or insert refinement between steps |
| Default Strategy | Production agents must explicitly select mode | **All enhancements are off by default** |
| Auditing Unit | Step + Tool Call | Extra LLM calls must record Trace spans (Chapter 38) |

Agentic Workflow enhancements build on top of the Chapter 25 Planner and Chapter 22 Runtime, **without changing the six runtime states (Figure 22-1)**: Reflexion, Self-Refine, and ToT are encapsulated inside the Planner, with the Runtime only seeing increased latency in the current `next_step` and possibly more `llm_call_count`.

Although this boundary seems subtle, it is critical for system operation. If enhancements bypass the Runtime state machine, intermediate states disappear from SSE, checkpoints cannot detect how many planner rounds have run; task cancellations may not stop ongoing reflection or branch search; cost statistics only see one Step but not multiple Gateway calls behind it. Restricting enhancements inside the Planner and writing extra calls as Trace spans preserves a unified approach to cancellation, budgeting, replay, and charging.

### 26.1.2 Counting Standards (Three Counters)

The platform recommends distinguishing three counters to avoid ambiguity caused by whether Reflection advances the Step:

*Table 26-2: The three counters for measuring enhancement costs and their standards. Source: This book.*

| Counter | Typically Counts | Description |
| --- | --- | --- |
| `step_index` | Each completed Runtime `planning`→`executing` loop | Subject to hard constraint `max_steps` |
| `llm_call_count` | Extra Gateway calls for Reflection / Refine / ToT evaluation | Must be independently traced |
| `tool_call_count` | Successful paths of Registry `invoke` | Reflection LLM calls **do not count as Tool Calls** |

Reflection counts toward `llm_call_count` by default; whether it also advances `step_index` depends on platform policy (recommended to merge budget with Chapter 22 `max_steps`).

### 26.1.3 Workflow Boundaries and Misuse Risks

The following three misconceptions are most common in enterprise deployments:

**Misconception 1: Agentic Workflow is a more advanced Planner mode.**
`react` and `plan_and_execute` are mutually exclusive (or composable) **orchestration strategies**; Reflexion can be enabled simultaneously with ReAct—after failure reflection, a new ReAct round starts; it does not replace the mode with a fourth type.

**Misconception 2: Enabling Reflexion equals allowing infinite retries.**
Production must bind `max_reflection_rounds`, `max_steps` (Chapter 22), and Gateway budget; otherwise, one SQL syntax error might trigger dozens of reflections, overwhelming shared Gateways.

**Misconception 3: ToT must run full-depth search before every Tool Call.**
Tree of Thoughts’ branching factor multiplied by depth incurs **exponential cost**; enterprise scenarios should limit this to "before high-risk write operations" or "offline report generation," not default multi-path question answering.

---
## 26.2 Reflexion

**Reflexion** enables an Agent to review its own trajectory (Thought / Action / Observation) after task failure or receiving a tool error. It generates a **natural language reflection summary**, which is then injected into the subsequent Planner context to improve the next step (Shinn et al. 2023). Unlike merely feeding the error string back to the Planner, Reflexion explicitly requires the model to summarize *“what I did wrong and what to avoid next time”*. Empirically, this approach improves success rates on tasks such as AlfWorld and HotPotQA (Shinn et al. 2023).

### 26.2.1 Industry Scenario

DataAgent calls `sql_executor` and receives a `TOOL_ARGUMENT_INVALID` error because the model wrote `last_week()`—a nonexistent function—when trying to express “last week.” The runtime logs a `result` event into the Run history; if only the original error JSON is fed back to the Planner, the model might hallucinate the same function again. When Reflexion is enabled, the Planner first triggers a **Reflection LLM call** at the **planning entry of the same or next step** (not counting as a Tool Call), producing something like:

> “Use the built-in date function `date_trunc('week', current_date - interval '7 days')` instead of inventing a UDF.”

This reflection summary is appended to the Working Memory (see Chapter 27). When writing the implementation suggestion, set `metadata["source"]="reflection"` to distinguish it from Tool `result` — currently, the demo does not integrate RunLoop enhancement, so Working Memory only grows with Tool Calls. The Planner then proceeds to call the normal model to generate the `next_step`.

Reflexion hooks inside `next_step` without changing the Run’s six states (in the same Run loop as **Figure 22-2**):

1. RunLoop calls `next_step(run_ctx)`.
2. If the previous Tool failed and `reflexion` is enabled → Gateway calls `reflect(trajectory, error)` → summary appended to Working Memory.
3. Gateway calls `plan(messages + tools)` → either `tool_call` or `finish`.
4. Returns `PlannerDecision` → RunLoop in `executing` state `invoke` Registry.

Reflexion **does not replace** Tool retry logic: the runtime still classifies `TOOL_ARGUMENT_INVALID` errors according to Chapter 22 and decides whether to feed back to the Planner. Reflexion only improves the **quality of Planner feedback content**.

Reflexion is best suited for errors the model can fix itself—such as parameter formats, time expressions, tool choice, or missing query clauses. It is not suitable for errors like permission denials, downstream system failures, or business rule conflicts. Continuing reflection on permission denials just causes the model to attempt to bypass restrictions; reflecting on database unavailability will not restore the service. Platforms should set narrow trigger conditions: Reflexion should only intervene when the error type implies “changing parameters or approach might succeed.”

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

**Self-Refine** enables the model to **iteratively improve its own output**: generate a first draft → have the same model (or a stronger model) provide critique → revise → repeat until a stopping condition is met (Madaan et al. 2023). It is typically used for **polishing answers after no tools are involved or tool usage has ended**, such as report summaries, email drafts, or JSON structure corrections.

### 26.3.1 Differences from Reflexion

The table below compares the inputs, goals, and typical timing of Reflexion and Self-Refine; the two can be combined, but their triggers and risks differ:

*Table 26-4: Comparison of Reflexion and Self-Refine. Source: Compiled by the book.*

| Comparison Dimension | Reflexion | Self-Refine |
| --- | --- | --- |
| Input | Failure trajectory + environmental feedback | Model’s own previous output |
| Goal | Improve actions/tool parameters | Improve text or structured answers |
| Typical Timing | Tool `failed` or result is empty | Before or after `finish=true` |
| Risk | Repeated erroneous tool calls | Over-polishing causing fact drift |

In industry scenarios, SQL results may be correct but operations require “conclusions to include one sentence for year-on-year and one for month-on-month comparison.” The Planner has already `finish`ed but the answer only contains a month-on-month comparison; with `enhancement.self_refine` enabled, the Planner runs a **Refine sub-loop** (up to `max_refine_iterations` times) before submitting the final `PlannerDecision(finish=True)`, sending the current answer along with a brand checklist to Gateway each round until the critic marks `pass` or the iteration limit is reached. **Self-Refine can only improve expression and must not rewrite factual numbers in the tool output** (e.g., sales, year-on-year or month-on-month figures).

Self-Refine forms an internal **draft → critic → revise** closed loop in the Planner, only submitting FINISH to Runtime after passing the critic (or reaching `max_refine_iterations`).

**Fact anchoring**: The critic prompt in Refine should require **not contradicting tool outputs**; otherwise the model might alter numbers just to improve fluency. The platform should inject **read-only** Tool Call summaries during the refine phase (see Chapter 27 Working Memory), rather than allowing the model to reissue SQL queries.

The product value of Self-Refine usually appears in reports, emails, and structured summaries rather than re-solving problems. It can make answers clearer and JSON output more schema-conformant, but it cannot change evidence. If the refine stage changes “month-on-month down 12%” to “significantly down about one-tenth” purely for fluency, it loses auditability in business or compliance analysis. Production systems should separate rewriteable sections from immutable facts, and when necessary have the critic only return issues lists, with final text composed deterministically by templates.

### 26.3.2 Configuration Points

- `enhancement.self_refine`: default `false`.
- `max_refine_iterations`: recommended `1–3`; report agents may go up to `5` and should be paired with evaluation (Chapter 39).
- `refine_target`: `answer` | `plan` (under Plan-and-Execute, can refine plan text before execution).
- Combine with **Structured Outputs** (Chapter 8): critic outputs JSON `{ "pass": bool, "issues": [...] }` for easier automation testing.

---
## 26.4 Tree of Thoughts

**Tree of Thoughts (ToT)** expands reasoning as a **search tree**: each node represents a “partial solution or intermediate thought,” with the model generating multiple candidates at each node. These candidates are then evaluated using heuristics or an LLM scoring function to select which branches to expand, continuing until an executable plan or final answer is found (Yao et al. 2023). Chapter 8 introduces ToT and Self-Consistency at the **prompt layer** as a structure for **single completions**; this chapter discusses ToT at the **Agent layer**, focusing on when ToT acts as an internal Planner search rather than ordinary Chain-of-Thought (CoT).

### 26.4.1 Division of Responsibilities with Chapter 8

ToT can operate at the prompt layer, Planner layer, and Runtime layer. The following table clarifies the scope and responsibilities at each layer:

*Table 26-5: Division of roles between Self-Consistency in Chapter 8 (structured output layer) and this chapter. Source: compiled by the authors.*

| Layer         | Responsibility                          | This Chapter / Chapter 8            |
|---------------|---------------------------------------|-----------------------------------|
| Prompt Layer  | `n` samples per request, plus voting  | Chapter 8 Self-Consistency         |
| Planner Layer | Maintain branches across multiple steps, backtracking, pruning | This Chapter ToT                 |
| Runtime Layer | Execute Tool Calls only on **selected branches** | Chapter 22 unchanged              |

Example: High-risk automatic price adjustment scenario. Before writing with the `price_update` tool, the Agent’s Planner uses ToT to generate three pricing strategy branches. An **evaluation model** scores them (compliance, margin, competitive price). Only the highest scoring branch delivers its first Tool Call to Runtime. Branches not selected **must not** cause side effects—this contrasts with AutoGPT’s “think-while-doing” pattern.

!!! warning "Branches not selected must not execute tools"
    ToT search happens entirely within the Planner; only the **final selected branch** can produce a `PlannerDecision` including a Tool Call. Non-selected branches must not invoke Registry `invoke`.

### 26.4.2 ToT Parameters and Cost

The token cost of ToT is determined by the product of its branching factor and depth. The following table provides recommended default values for production:

*Table 26-6: Meaning and cost-related production recommendations of Tree of Thoughts parameters. Source: compiled by the authors.*

| Parameter                  | Meaning                      | Production Recommendation            |
|----------------------------|------------------------------|------------------------------------|
| `enhancement.tree_of_thoughts` | Master toggle               | Default `false`                    |
| `tot_branching`            | Candidates per node           | Within `3`                         |
| `tot_depth`                | Maximum depth                | `2–3`                             |
| `tot_evaluator`            | `llm` or `rule`              | Use `rule` + policy double-check before write operations |
| `tot_budget_tokens`        | Max tokens per ToT run       | Aligned with Gateway quota         |

After ToT search completes, only the **selected branch** produces Tool Calls; non-selected branches are pruned inside the Planner’s memory (`tot_branching` × `tot_depth` must be controlled by Gateway quotas, see Chapter 38).

ToT’s **parallel candidates** increase Gateway QPS; platforms should implement **tenant-level quotas** and alerting for `enhancement.tree_of_thoughts` (Chapter 38).

ToT should avoid presenting the search process as a definitive conclusion. Multiple candidate branches represent model exploration, not business-validated plans. Non-selected branches must not appear in final answers or be written into long-term Memory. For pricing, permissions, contracts, and compliance tasks, branch evaluation should combine rule-based and policy checks rather than relying solely on another LLM scoring pass. This makes ToT a controlled decision support tool instead of entrusting high-risk judgments to self-assessing models.

Therefore, the default recommended place for ToT is offline analysis, draft reporting, or limited pre-evaluation before high-risk actions—not a fixed pre-step for every ordinary dialog.

Leaving it off by default is the practical and manageable starting point.

---
## 26.5 Critique of the AutoGPT Paradigm and Production Thresholds

**AutoGPT** and similar open-source projects (BabyAGI, AgentGPT, etc.) have popularized an end-to-end narrative based on **goal decomposition + autonomous loop + long-term memory + toolchain**: give the agent a high-level goal, and it breaks down tasks, searches the web, writes files, then sets new goals autonomously. The demos are impressive and intuitive, but if an **enterprise DataAgent platform** simply copies this approach, it often runs into the following structural issues (Significant Gravitas 2023; Wang et al. 2024):

### 26.5.1 Key Critiques

1. **Goal Drift**
   Without external validation, the agent endlessly expands the scope to "complete sub-goals" (e.g., further competitor research, additional blog posts), often unrelated to the user's original query. Production requires **Run-level input controls plus max_steps** hard boundaries (Chapter 22), rather than an unlimited `while True` loop.

2. **Uncontrollable Side Effects**
   AutoGPT-style loops commonly assume **tool use is allowed at every iteration**. Enterprises demand **Policy enforcement upstream** (Chapter 50), **human-in-the-loop (HITL) for write operations** (Chapter 30), and **tool registry version pinning** (Chapter 23). Fully autonomous operation conflicts with all three requirements.

3. **Unpredictable Cost and Latency**
   Autonomous loops lack **step and token budget controls**, so a single “research-style” task might consume millions of tokens. Platforms must **meter Reflexion / Self-Refine / ToT steps** and fold them into FinOps governance (Chapter 46).

4. **Memory Pollution**
   Persistently writing unverified intermediate conclusions into long-term memory (Chapter 27) risks error amplification in later runs. The AutoGPT method of “remembering everything” violates enterprise requirements for **deletability and auditability**.

5. **Lack of Evaluation and Replay**
   Autonomous agents struggle to answer “Why was incorrect output given last week?” Run / Step / Tool Call + Trace logging (Chapters 22 and 38) are indispensable compliance basics, not optional.

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

**Conclusion:** The AutoGPT paradigm is suitable for **personal experimentation and prototyping**. Enterprise platforms should **reduce it to a configurable, toggleable, and measurable Planner enhancement** (splitting into partial capabilities like Reflexion, Self-Refine, ToT, rather than default autonomous looping), with the runtime maintaining **six-state and audit models** unchanged.

This does not mean enterprises cannot use autonomous loops; rather, autonomous loops cannot be the default operational mode. Production-ready approaches usually break down “autonomy” into controlled segments: plans may be iterated once more, failures can trigger one reflection, reports can be polished once, high-risk write operations can undergo limited branch evaluation. Each segment has trigger conditions, budgets, stop criteria, and audit logs. This enables the system to still gain quality improvements in complex tasks without turning an ordinary query into an unpredictable long-running job.

---
## 26.6 mini-platform Engineering Implementation: Planner Enhancement Mode

The current `mini-platform/core/planner/config.py` defines `PlannerEnhancementFlags`, but it **only contains three boolean switches**; subloops such as `reflect()`, `refine_answer()`, and `tot_search()` are **not yet** integrated into the Demo execution logic. This section distinguishes between the "current Demo" and the "production interface draft."

### 26.6.1 Implementation Path in mini-platform

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

**Design Principle:** Enhancement capabilities are **off by default**; `RunLoop` does not perceive internal details of Reflexion, only reading `PlannerDecision` and variable-length planning latency.

Currently implemented switches in the Demo (`core/planner/config.py`):

```python
@dataclass
class PlannerEnhancementFlags:
    """Agentic Workflow enhancement switches; default all False in production."""

    reflexion: bool = False
    self_refine: bool = False
    tree_of_thoughts: bool = False
```

For production implementation, it is advisable to add upper limits such as `max_reflection_rounds`, `max_refine_iterations`, `tot_branching`, `tot_depth`, `tot_budget_tokens` to `PlannerConfig`, and explicitly account for `llm_call_count`, token budget, and Trace spans inside `next_step`.

### 26.6.2 Executable Code and Configuration

**Runtime Environment:** This chapter does not implement standalone enhancement subloops. It verifies stability of Run boundaries when enhancements are off:

```bash
cd mini-platform
pytest tests/test_multi_agent_workflow_run.py tests/test_runtime.py -q
python3 projects/multi-agent-workflow/run.py start   # Observe full Run without reflexion enabled
```

`PlannerEnhancementFlags` is defined in `core/planner/config.py`.

Agent configuration example (Control Plane YAML, **production target**):

```yaml
planner:
  mode: react
  enhancement:
    reflexion: true
    self_refine: false
    tree_of_thoughts: false
    max_reflection_rounds: 2
```

Conceptual wiring (enhancement subloops **not implemented yet**). The following snippet **cannot be copied to run directly**: `RunLoop` construction **must** inject `registry` (Chapter 23), and Reflexion subloop is not yet integrated; this only illustrates configuration and calling relations:

```python
from core.planner import PlannerConfig, PlannerEnhancementFlags, create_planner
from core.runtime import RunLoop

config = PlannerConfig(
    enhancements=PlannerEnhancementFlags(reflexion=True),
)
# Production requires: registry = build_workflow_registry() or equivalent ToolRegistry
loop = RunLoop(planner=create_planner(config))  # Missing registry → TypeError
loop.run(agent_id="data-agent", user_input="...", context={"tenant_id": "shanlan-retail"})
```

### 26.6.3 Release Gates and Runtime Constraints

*Table 26-8: Coverage of enhancement capabilities in this chapter’s Demo. Source: Compiled from this book.*

| Capability                           | Description               | This Chapter Demo |
|------------------------------------|---------------------------|-------------------|
| `PlannerEnhancementFlags` three boolean switches | Configuration entry defined | ✓                 |
| Reflexion / Self-Refine / ToT subloops             | `enhancements.py`           | ☐                 |
| Linkage with `max_steps` / `llm_call_count`         | Measurement and truncation  | ☐                 |
| Trace segmented spans                              | `planner.reflect` / `planner.refine` / `planner.tot` | ☐          |
| Gateway budget                                    | Tenant-level token / call limits | ☐                 |
| ToT executes only selected branches               | Non-selected branches have no Tool Call | To be implemented |
| Checkpoints include enhancement state              | Integration with Chapter 27 | ☐                 |

### 26.6.4 Common Issues

**Issue 1: Explosive double counting of Reflexion and Tool retries**
Symptom: `TOOL_ARGUMENT_INVALID` triggers Registry feedback to Planner and Reflexion, which triggers model retries, resulting in 6 Gateway calls within a single step.
Fix: Reflexion is constrained by `max_reflection_rounds`; merge configuration with feedback Planner limits from Chapter 22.

**Issue 2: Self-Refine rewriting SQL conclusion**
Symptom: After polishing, numbers in the answer are inconsistent with the `sql_executor` results.
Fix: critic enforces "numbers must reference tool output"; Eval sampling inspection (Chapter 39).

**Issue 3: ToT executes tools on all parallel branches**
Symptom: Three branches all triggered `price_update`, causing triple rewrites.
Fix: Runtime only executes **one** Tool Call actually submitted by the Planner; ToT search is done inside Planner, branches exist only as in-memory objects.

**Issue 4: Connecting AutoGPT-style autonomous loops into RunLoop**
Symptom: Planner internally performs a `while not done` loop without step boundaries, leading to no state updates for long periods in SSE.
Fix: Any enhancement subloop must **yield step boundaries** or be constrained to observable spans inside planning state, forbidding circumvention of `max_steps`.
## Chapter Recap

1. **Chapter 25 – Orchestration Patterns** and **Chapter 26 – Agentic Workflow** are orthogonal: the former defines step structure; the latter defines whether reflection, refinement, or branch search is applied.
2. **Reflexion** improves Planner output quality after failures; **Self-Refine** improves final-draft quality; **ToT** selects strategies under controlled search — all three are **disabled by default**.
3. **AutoGPT-style full autonomy** conflicts with Run boundaries, Policy, HITL, and auditing; enterprises should **downscope it to measurable augmentation** rather than treating it as default behavior.
4. **`PlannerEnhancementFlags`** is the platform-wide unified toggle; the six Runtime states remain unchanged, and checkpoints must include enhancement and Memory state.
5. All augmentation LLM calls must be **independently observable** and subject to dual constraints from the Gateway and `max_steps`.

---

- Should new Agents default to `enhancement.* = false`?
- Does enabling Reflexion or ToT require **tenant quotas and approval**?
- Does Self-Refine anchor to tool output to prevent factual drift?
- Does ToT guarantee that **exactly one** Tool Call enters `executing`?
- After checkpoint recovery, does the Planner avoid "amnesia" or "repeated reflection"?

---

- [Chapter 25 – Planner and Orchestration Patterns](ch25-planner.md)
- [Chapter 27 – Memory System](ch27-memory.md)
- [Chapter 30 – Human-in-the-Loop and Long-Running Tasks](ch30-human-in-the-loop.md)
- [Chapter 38 – Agent Trace and Session Replay](../../part07-observability-eval/ch/ch38-trace.md)
- [Chapter 8 – Structured Output and Prompt Engineering](../../part02-model-inference/ch/ch08.md)
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
