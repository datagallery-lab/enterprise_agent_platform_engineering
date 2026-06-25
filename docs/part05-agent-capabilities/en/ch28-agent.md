# Chapter 28 Multi-Agent Collaboration

---
## Chapter Summary

This chapter discusses multi-Agent collaboration within enterprise Agent platforms. The value of multiple Agents lies not in letting multiple models chat with each other, but in integrating different responsibilities, permissions, and deliverables into a single auditable Run. A single DataAgent can handle querying, explanation, and report drafting; however, when tasks involve clarification, data verification, report generation, compliance review, and external vendor capabilities, one Agent often bears excessive prompt complexity, tool permissions, and responsibility boundaries. This chapter explains the platform-based approach to multi-Agent systems from six perspectives: splitting conditions, role division, handoff, capability discovery, conflict arbitration, and mini-platform implementation.
## Key Terms

Multi-agent collaboration, Handoff, Agent Catalog, role division, routing, conflict arbitration
## Learning Objectives

- Be able to determine whether a task needs to be split into multiple agents and explain the splitting costs.
- Be able to design the boundaries among roles such as Workflow, Question, Data, Report, and Reviewer.
- Be able to explain why handoff must be completed within the same `run_id`, rather than letting sub-agents each start independent tasks.
- Be able to design conflict detection, authoritative source selection, and human arbitration strategies for parallel collaboration.

---
## Opening Scenario

Chapter 25 discusses orchestration within a single Agent, where a Planner can use ReAct, Plan-and-Execute, or state charts to decide the next tool to call. Chapter 26 covers how a single Agent can perform self-correction. These chapters address the question of “how one Agent completes a task.” The problem in this chapter is different: when a task naturally spans multiple specialized roles, how can the platform enable multiple Agents to collaborate while maintaining unified state, approval, and auditing?

Take an example of a business analysis request. The operations leader inputs: “Explain the Q1 gross margin decline in East China and provide actionable recommendations.” If this is handed off to one Agent alone, it must clarify metric definitions, execute SQL queries, generate reports, and determine which conclusions require compliance review. While this approach may work in a demo, the production environment faces several issues: SQL tool permissions get mixed in with report generation logic; the prompt becomes overloaded with multiple role responsibilities; it’s difficult to separate report drafts and data verification for auditing; and compliance review is hard to insert at the appropriate step.

A more reliable approach is to place the task in an outer Workflow Run. A Workflow Agent receives the user input and chooses the next role; a Question Agent clarifies definitions; a Data Agent calls the semantic layer or SQL tools; a Report Agent drafts the report; a Reviewer or Policy Agent decides if manual confirmation is needed. These are not five separate `/run` services started independently, but rather five sequential processing stages under the same `run_id`. The runtime still maintains six states, checkpoints, tool calls, and approvals. The handoff merely transfers control and context to the next participant.

Multi-Agent orchestration is therefore not the default architecture. It adds overhead in routing, communication, checkpoints, observability, and failure recovery. Only when these costs bring clear advantages like permission isolation, organizational role separation, or parallel expertise does decomposition make sense. This chapter’s focus is to transform “multiple Agents” into a platform contract, rather than a loose collection of model chats.
## 28.1 When Multiple Agents Are Needed

To decide whether to split Agents, first check if a single Agent is already overloaded. Overload is not just about the model answering slowly, but whether one Agent carries multiple distinct responsibilities: it needs to use unrelated tools, switch between different permission domains, produce different types of deliverables, or let different teams be responsible for intermediate results. As long as these boundaries can still be clearly expressed by a single Planner, a clear Tool Registry, and a state diagram, there is no rush to split.

*Table 28-1: Signals for Choosing Single Agent vs. Multiple Agents. Source: compiled by author.*

| Judgment Dimension | Single Agent More Suitable | Multiple Agents More Suitable |
|---|---|---|
| Tool Permissions | Tools belong to the same authentication domain | SQL, report, and external SaaS permissions differ |
| Prompt Roles | One system prompt covers the task | Clarification, data querying, writing, review require different prompts |
| Audit Responsibility | Tool Call replay suffices to explain process | Different teams responsible for different intermediate outputs |
| Parallel Needs | Steps are naturally sequential | Multiple data sources, regions, or external Agents can work in parallel |
| Deliverable Forms | Only one final answer needed | Reports, attachments, approval comments, or external artifacts required |

A typical scenario where a single Agent suffices is a one-off read query with a brief explanation. For example, when a user asks “What were the top 10 SKUs for East China sales last week?”, the Planner just selects tables, generates SQL, runs the query, and explains. Splitting into Question Agent, SQL Agent, Report Agent only lengthens the process.

Multiple Agents are better suited for cross-role tasks. For example, the same business analysis may require a Data Agent to access the warehouse, a Report Agent to access a document renderer, and a Reviewer who can only read drafts and evidence but cannot directly access PII tables. Here splitting is not to complicate architecture, but to separate tool whitelists, output formats, and responsibility boundaries.

![Figure 28-1: Single vs. Multiple Agent Decision Tree](../../images/part5/en/p5-07-multi-agent-decision-tree.png)

*Figure 28-1: Single vs. Multiple Agent Decision Tree. Source: drawn by author. Alt text: A decision tree branching on whether a single Agent is overloaded, whether specialization is needed, and whether parallelism is required, leading to the conclusion to keep a single Agent or split into multiple Agents.*

It is also important to distinguish multiple Agents from Agentic Workflows. Reflection, search, and self-correction discussed in Chapter 26 can happen within a single Agent. Multiple Agents imply multiple `agent_id`s in the platform, each with independent configuration, tool permissions, and input-output contracts. The former enhances single-task quality; the latter aligns organizational and permission boundaries.

A common misconception is that multiple Agents mean "multiple models freely discussing." Production platforms cannot allow Agents to bypass the Runtime and send arbitrary messages to each other. Every handoff must correlate the `run_id`, `step_index`, input payload, output result, and failure reasons. Without this, apparent flexibility actually breaks the audit trail.

Another misconception is using multiple Agents to cover up tool governance problems. If the SQL tool schema frequently drifts, metrics have no versioning, or report templates are unstable, splitting into more Agents only scatters the issues. Before multiple Agents, there must be a stable Tool Registry, semantic layer versioning, and tracing. Otherwise, each Agent patches holes with its own interpretation, resulting in a seemingly collaborative but actually non-reproducible task chain.

---
## 28.2 Role Assignment

The first step in multi-Agent design is defining roles. Roles are not just for naming—they help constrain each Agent’s inputs, outputs, tool permissions, and scope of responsibility. A well-designed role should enable the business side to clearly say “who is responsible for this step” and enable the platform to say “what tools are allowed to be called at this step.”

*Table 28-2: Common Agent Roles and Responsibility Boundaries. Source: Compiled by this book.*

| Role | Primary Responsibility | Typical Output | Tool Permissions |
|---|---|---|---|
| Workflow / Router | Receive tasks, select the next Agent | `handoff` target, routing reasons | Routing tables, Agent Catalog |
| Question / Clarifier | Clarify scope and fill missing slots | `query_spec` | Low-risk knowledge retrieval |
| Data / Executor | Execute queries and fact generation | SQL results, metrics JSON, evidence citations | Semantic layer, SQL, read-only data tools |
| Report / Synthesizer | Generate report drafts | Markdown, PPT outlines, summaries | Document rendering, templates |
| Reviewer / Policy | Quality and compliance checks | Approve, reject, manual approval requests | Rules, evaluators, approval interfaces |

Router and Planner roles are often confused. The Router selects “which Agent will handle it,” while the Planner chooses “which tool the current Agent invokes.” A Workflow Agent can embed a lightweight Router, while a Data Agent itself still maintains a Planner internally. This avoids a global Planner needing to understand all tools and all roles at once, while allowing the Data Agent’s planning logic to stay focused.

After role division, there should still be only one external entry point. Users see an operational analysis Agent or DataAgent, not manually selecting among five sub-Agents. Internal roles may be shown in debug interfaces, but the business entry must remain stable. For users, the platform delivers a single traceable task, not a collection of components they need to orchestrate themselves.

![Figure 28-2: Handoff Sequence](../../images/part5/en/p5-08-handoff-sequence.png)

*Figure 28-2: Handoff Sequence. Source: drawn by this book. Alt text: Sequence diagram showing the main Agent completing part of a task, packaging the task context and state to hand off to a specialized Agent, who processes it and returns it; arrows mark handoff points and context transfer.*

In the six states of Run, multi-Agent switching should not change the state model. `planning` indicates the currently active Agent is making decisions; `executing` indicates the Agent is calling tools or initiating Handoff; `waiting_human` means Reviewer or Policy requests manual approval; `succeeded` means the Workflow has completed aggregation. At checkpoints, `active_agent_id` and the Handoff stack need to be recorded to know which role currently holds control after recovery.

Role design must also control the boundaries of “shared knowledge.” The Report Agent needs to know the metrics and evidence output by the Data Agent but does not need database connection details; the Reviewer needs to see the report drafts, citations, and risk tags but should not have report writing permissions; the Workflow Agent must know each Agent’s capabilities and status but should not inherit all sub-Agents’ tool whitelists. Encoding these boundaries in the AgentSpec is far more reliable than repeatedly reminding in Prompts “do not access these tools.”

In organizational collaboration, roles correspond to responsible parties. Data Agent metric errors should be traceable back to the semantic layer or query tools maintained by the data team; Report Agent expression issues should be linked to report templates and generation strategies; Reviewer rejections must be traceable to rule versions or approval comments. A multi-Agent platform that cannot map technical roles to organizational responsibilities will struggle to truly enter operational business workflows.

---
## 28.3 Handoff Contract

Handoff is a structured transfer of control. It is neither forwarding the user's original input to another agent nor starting a new task with a different agent. The platform should implement Handoff as a special Tool Call: the Runtime records the call, the Policy can intercept it, checkpoints can restore it, and the Trace can replay it.

*Table 28-3: Minimum Fields for Handoff. Source: Compiled by this book.*

| Field | Description |
|---|---|
| `from_agent_id` | Originating agent |
| `to_agent_id` | Receiving agent |
| `handoff_id` | Unique ID, recorded in the Tool Call log |
| `payload` | Structured context visible to the next agent |
| `reason` | Routing reason, used for troubleshooting and auditing |
| `return_policy` | Whether returning to the previous agent after completion is allowed |

The granularity of the payload must be carefully controlled. The `query_spec` output by the Question Agent can be passed by value since it usually contains only metrics, time periods, regions, and filters. Large outputs from the Data Agent should not be fully embedded in the Handoff; instead, they should be stored in Memory, object storage, or result tables, passing only a `result_ref`, schema, sample, and hash to the Report Agent. This reduces checkpoint size and prevents intermediate agents from modifying the original result.

Complex workflows may require a Handoff stack. For example, when the Report Agent is drafting and finds the scope incomplete, it can return control to the Question Agent to fill the gaps, then resume at the Report Agent. Stack depth must have an upper limit and be linked with `max_steps`. Otherwise, looping between A and B can cause the Run to time out before failing.

Internal Handoff and external agent delegation must also be differentiated. Internal Handoff only requires locating platform configurations by `agent_id`; external delegation must go through the A2A, Agent Card, TLS, mTLS, and outbound Policy described in Chapter 29. Both appear as Tool Calls in Runtime, but have different adaptation layers and security requirements.

Errors in Handoff must be structured as well. Cases such as the target agent not existing, payload schema violations, target queue timeouts, tenant mismatches, or failures to parse return results should all have clear error codes and recovery strategies. The Workflow Agent can decide to clarify, retry, degrade, or fail depending on the error type. Writing errors only as natural language makes retries, alerts, and analytics difficult.

Idempotency is another fundamental requirement for Handoff. When Runtime retries a Handoff, it must not cause the target agent to write duplicate reports, create duplicate tickets, or initiate duplicate external calls. The `handoff_id`, `idempotency_key`, and payload hash should all be recorded in the Tool Call log. This way, if the process crashes after Handoff, recovery can determine whether the handoff has already been received by the target agent.

---
## 28.4 Routing and Capability Discovery

The routing of Workflow Agents should not rely on the model’s on-the-fly guessing. Production systems typically use hybrid routing: rules first filter out high-certainty paths, classification models handle natural language variants, the Agent Catalog provides candidate capabilities and permission filtering, and low-confidence cases are handed off to a Question Agent for clarification.

*Table 28-4: Applicable Boundaries for Routing Strategies. Source: Compiled for this book.*

| Strategy                 | Suitable Scenario                  | Main Risk                       |
|--------------------------|----------------------------------|--------------------------------|
| Rule-based Routing       | High-certainty keywords, fixed flow | Insufficient coverage           |
| Classification Model     | Diverse user expressions, stable labels | Requires evaluation and confidence thresholds |
| Agent Card / Catalog Match | Large number of Agents, frequent capability changes | Metadata drift                 |
| Hybrid Routing           | Typical enterprise production    | Higher implementation and testing cost |

The Agent Catalog is the infrastructure foundation for routing. Each Agent must at least declare `agent_id`, capability description, input/output schema, tool whitelist, SLA, tenant scope, and version. The Router first filters by tenant and permissions, then chooses candidates by task intent, and finally records `route_label`, candidate list, final `chosen_agent_id`, and routing reasons.

When routing fails, the platform must have clear fallback paths. If no candidate Agents exist, enter clarification; if the target Agent times out, retry using idempotency keys; if queues are too long, select backup Agents or return an explainable delay; if the model routing confidence is low, direct SQL access is prohibited. Directly routing low-confidence queries to data tools remains one of the easiest causes of permission incidents in multi-Agent systems.

Routing itself also requires evaluation. Historic user queries, expected Agents, rejected routing samples, and boundary cases can form a test set to run regression tests after each rule or AgentSpec change. Evaluation should consider not only accuracy but also high-risk misroutes. For example, “Help me write a sales review” may route to the Report Agent, but “Find sales details by customer phone number” should never bypass permissions to go directly to the Data Agent, even if it contains the keyword “sales.”

As the number of Agents increases, maintaining the Catalog becomes more costly than the routing algorithm itself. Expired Agents, duplicate capabilities, ownerless Agents, and chronically failing external Agents should be removed from candidates or downgraded. Otherwise, the Router may pick from a pool of seemingly available Agents but actually hit unmaintained legacy capabilities.

The Router must also treat “reject routing” as a first-class outcome. When user queries lack time ranges, have ambiguous metric definitions, cross tenant boundaries, or when the target Agent is not enabled in the current environment, the best action is often not to force selecting an Agent but to return a clarification or rejection. Many production incidents do not stem from the model failing to understand the question entirely but from the system choosing a seemingly close capability under low confidence. For Data Agents, such errors can directly lead to erroneous SQL or unauthorized queries.

Routing outputs should also be captured in Trace, not just printed in logs. The Trace should retain at least candidate Agents, filtering reasons, final selection, routing confidence, routing rule version, and Catalog version. This enables the platform to explain why a “report Agent” was not called—whether due to tool whitelist filtering, tenant permission filtering, or misclassification by the model. Routing is the entry decision for multi-Agent invocation; without visibility, troubleshooting downstream becomes extremely difficult.

---
## 28.5 Conflict Arbitration and Consistency

Once multiple agents operate in parallel, conflicts inevitably arise. Two Data Agents might return different figures for the same SKU; a Report Agent might confuse gross profit with GMV; a Reviewer might reject conclusions in a report; two agents might even write to the same work order simultaneously. The platform cannot simply delegate resolving these issues to a final LLM to "integrate everything."

Conflict resolution first requires defining an authoritative source. Financial figures should be based on the semantic layer and versioned datasets; document conclusions must retain source references and timestamps; the final report should have only one author; Reviewers can tag and return reports but should not silently overwrite the main text. Before merging parallel results, the Workflow Agent must verify metric IDs, semantic layer versions, time ranges, filter criteria, and artifact hashes.

*Table 28-5: Types of Conflicts and Resolution Approaches. Source: Compiled by this book.*

| Conflict Type       | Detection Signal                          | Resolution Method                        |
|---------------------|------------------------------------------|----------------------------------------|
| Factual Conflict    | Different metrics returned for same `query_spec` | Use authoritative source or escalate to human arbitration |
| Definition Conflict | Inconsistent metric, time, or filter conditions | Return to Data Agent for regeneration   |
| Narrative Conflict  | Reviewer opposes Report conclusions       | Log annotations and request revision    |
| Resource Conflict   | Same artifact written by multiple Agents  | Single-author rule and optimistic locking |
| Handoff Loop       | Same payload circulating repeatedly among Agents | Detect via stack depth and payload hash |

Consistency contracts must be encoded into the platform itself rather than embedded in prompts. Handoff payloads should carry `semantic_layer_version`; Registry tools should support `idempotency_key`; events within a Run should be ordered by `step_index`; external Agent responses should record `external_task_id` and artifact hash. This enables the Trace playback in Chapter 38 to clearly show what each Agent received, did, and returned at each step.

Parallel collaboration especially needs to avoid producing an “average answer.” If two Data Agents return differing numbers, the Report Agent should not simply merge them into an apparently neutral conclusion; if the Reviewer identifies compliance risks, the Workflow Agent should not proceed just because the report wording is fluent. The platform must allow outputs like “Inconsistent, cannot auto-complete,” which better align with enterprise requirements than confidently producing an incorrect report.

Conflict data can also be leveraged to improve the system. Frequent definition conflicts indicate unclear semantic layer definitions; frequent Reviewer rejections show instability in report templates or prompts; frequent Handoff loops reveal unclear routing boundaries. One key value of multiple Agents is to make these issues explicit in Traces and metrics, rather than hiding all errors inside a black-box Agent's final response.

---
## 28.6 Mini-Platform Implementation Path

The practical project for this chapter is located at `projects/multi-agent-workflow/`. It completes the Workflow, Data, Report, and approval chain using the same `run_id`. Handoff is executed as a `handoff@v1` Tool Call, and checkpoints save the `active_agent_id` and `handoff_stack`. This is not a full production Router, nor does it integrate external A2A Agents, but it is sufficient to demonstrate the minimal closed loop of multiple Agents within the platform.

```text
mini-platform/
├── projects/multi-agent-workflow/lib/
│   ├── registry_setup.py
│   └── planner.py
├── core/runtime/
│   ├── run_loop.py
│   └── handoff_tool.py
└── projects/multi-agent-workflow/
    ├── run.py
    └── README.md
```

Run the program as follows:

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py start
python3 projects/multi-agent-workflow/run.py approve
```

The expected event flow should show `handoff`, switching of `active_agent_id`, the Data phase calling `mcp_db_query_sales`, the `waiting_human` status after report generation, and `approval_result` after approval passes. If each sub-Agent starts its own `/run` process separately, approval, recovery, and replay will break, which contradicts the design of this chapter.

The first production-grade version can be advanced in four steps. First, convert internal Handoff into a Tool Call, and enable checkpoints to recover the `active_agent_id`. Next, establish an Agent Catalog and a tool whitelist so the Router has an auditable candidate set. Then, complete routing evaluation, conflict detection, and Handoff loop detection. Finally, integrate external A2A Agents, since external protocols introduce authentication, outbound desensitization, timeout nesting, and vendor version management.

This order is critical. Many teams integrate external Agents first, and then try to patch internal state and auditing later. As a result, external tasks run but cannot be explained, canceled, or recovered. Building an internally testable minimum closed loop with Handoff first allows all subsequent protocol integrations to remain within the same Runtime model.

Acceptance testing can be designed with three types of cases. The first type covers the normal flow: from Workflow to Data to Report to approval, confirming that `run_id` remains consistent. The second type covers recovery flow: killing the process after Handoff and confirming the checkpoint restores the correct `active_agent_id`. The third type covers failure flows: constructing cases such as target Agent not existing, payload schema errors, and Handoff loops, confirming the system outputs structured errors rather than waiting indefinitely.

Post-launch, watch operational metrics, not just single demo runs. An abnormal rise in Handoff count indicates the Router may be oscillating between multiple Agents; a sudden increase in Question Agent hit rate might indicate upstream input getting ambiguous or routing rules expiring; an increase in Reviewer rejection rate may be due to Report Agent template drift; a large cross-agent payload per run might mean the Data Agent is stuffing large results directly into the Handoff. Incorporating these metrics into the observability system from Chapter 38 is essential for evolving multi-Agent systems from merely “runnable” to fully “operational.”

---
## Chapter Recap

1. The value of multiple agents lies in defined responsibilities, permissions, and organizational division of labor, not merely in increasing the number of models.
2. The Router selects the agent, while the Planner selects the tools—these operate at different hierarchical levels.
3. Handoff should be implemented as a structured Tool Call within the same `run_id`; child agents must not independently initiate separate tasks.
4. An Agent Catalog, a tool whitelist, and routing traceability are prerequisites for governable multi-agent systems.
5. Parallel collaboration requires conflict detection and authoritative source policies; models must not merge contradictory facts based solely on tone.
## Further Reading

- [Chapter 29 Agent Protocols and Standards](ch29-agent.md)
- [Chapter 30 Human-in-the-loop and Long-running Tasks](ch30-human-in-the-loop.md)
- [Chapter 27 Memory Systems](ch27-memory.md)
- [Chapter 33 Semantic Layer and Metric Definitions](../../part06-dataagent/ch/ch33.md)
- `mini-platform/projects/multi-agent-workflow/README.md`
## References

Li, G., et al. (2024). CAMEL: Communicative agents for "mind" exploration of large language model society. *NeurIPS*. arXiv:2303.17760. [https://arxiv.org/abs/2303.17760](https://arxiv.org/abs/2303.17760)

Qian, C., et al. (2024). ChatDev: Communicative agents for software development. arXiv:2307.07924. [https://arxiv.org/abs/2307.07924](https://arxiv.org/abs/2307.07924)

Google. (2025). *Agent2Agent (A2A) Protocol*. [https://google.github.io/A2A/](https://google.github.io/A2A/)

Microsoft. (n.d.). *AutoGen*. [https://microsoft.github.io/autogen/](https://microsoft.github.io/autogen/)

Wu, Q., et al. (2024). AutoGen: Enabling next-gen LLM applications via multi-agent conversation. arXiv:2308.08155. [https://arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155)

OpenAI. (2024). *Swarm*. [https://github.com/openai/swarm](https://github.com/openai/swarm)

Hong, S., et al. (2024). MetaGPT: Meta programming for a multi-agent collaborative framework. *ICLR*. arXiv:2308.00352. [https://arxiv.org/abs/2308.00352](https://arxiv.org/abs/2308.00352)

Wang, L., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Model Context Protocol. (2024). *Specification* (2024-11-05). [https://modelcontextprotocol.io/specification/2024-11-05](https://modelcontextprotocol.io/specification/2024-11-05)

Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. arXiv:2210.03629. [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
