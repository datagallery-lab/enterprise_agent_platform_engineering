# Chapter 27: Memory Systems

---
## Chapter Summary

This chapter discusses the platform design of Agent Memory. Memory is not simply stuffing all historical conversations back into the prompt, nor is it just renaming the corporate knowledge base. The challenge it addresses is: how to restore context in a single run, how to securely reuse users’ long-term preferences, how to consistently inject corporate organizational standards, and which information should go into Retrieval-Augmented Generation (RAG) versus Memory. This chapter categorizes Memory into four types—Working, Episodic, Profile, and Org Context—explaining their lifecycles, permission boundaries, compression strategies, and current implementation status within a mini-platform.
## Key Terms

Memory, Working Memory, Episodic Memory, User Profile, Organizational Context, Context Governance
## Learning Objectives

- Be able to distinguish the four types of memory: Working, Episodic, Profile, and Org Context.
- Be able to explain the boundary between Memory and RAG, avoiding mixing private conversations with enterprise documents during retrieval.
- Be able to design the `working_snapshot` in checkpoints to ensure the Planner does not lose context after Runtime recovery.
- Be able to identify compliance risks of long-term memory, including PII, deletion, tenant isolation, and data expiration policies.

---
## Opening Scenario

Chapter 22 requires that checkpoints be able to reconstruct the Planner’s visible context. Otherwise, after a process restarts, the Planner might forget that the previous SQL query already returned results, causing it to re-select tables, call tools repeatedly, or even produce different answers than before the restart. Chapter 25 further explains that each round of Planner decision-making depends on the history of Tool Calls, errors, and Memory fragments. Therefore, Memory is not just an add-on feature but the foundation of Runtime recoverability.

Let’s consider a DataAgent scenario. The user first asks, “What are the main SKUs for sales decline in the East China region last week?” The system queries and returns results. Then the user follows up, “How about North China?” The Planner must remember the time range, metric definitions, and comparison method from the previous turn. When the same user returns next week, the system might already know her preference for “tables + year-over-year comparison.” However, “which stores belong to the East China region” is part of the enterprise organization context and should not be mixed with user preferences.

If all this information is stuffed into the Prompt, it will soon encounter context length and privacy issues. On the other hand, if everything is given to Retrieval-Augmented Generation (RAG), user-private conversations, organizational master data, and document knowledge would all be mixed in the same retrieval space. The goal of this chapter is to create memory layering.

The challenge with Memory is not just "remembering," but rather "what to remember, how long to keep it, who can see it, and when it expires." If a production Agent remembers every single thing a user said forever, it might seem smart but actually creates privacy risks, misuse, and issues with outdated information. Conversely, if it always starts from scratch each time, long tasks and multi-turn Q&A degrade into one-off chats. The platform needs to build controllable memory layers between these extremes.

We can break down a complete question flow into parts. In the first turn, the user specifies “last week East China,” and the Working memory records the time range and region condition. After the SQL tool returns results, Working stores a summary and the `result_ref`. In the second turn, the user only says, “How about North China?” The Planner recovers the last turn’s metric and time range from Working but just replaces the region condition. In the third turn, the user confirms, “From now on, use year-over-year tables for this type of question.” The system treats this sentence as a Profile candidate, not immediately permanently writing it. Several days later, the organizational master data updates the region definitions, causing version updates in Org Context, and the old regional criteria automatically expire. These four steps correspond to different memory layers and should not be mixed together.

---
## 27.1 Four-Layer Model of Memory

### 27.1.1 Four Types of Memory

Memory can be divided into at least four categories. Working Memory serves the current run or session, storing recent user inputs, planner decisions, and tool results. Episodic Memory retains fragments of past tasks, such as a successful analysis path or user-confirmed criteria. Profile stores long-term user preferences. Org Context preserves enterprise-specific organization, metric definitions, permissions, and process standards.

*Table 27-1: Boundaries of the Four Types of Memory. Source: Compiled by the author.*

| Type         | Lifecycle        | Typical Content                                | Main Risks                       |
|--------------|------------------|------------------------------------------------|----------------------------------|
| Working      | Run or session   | Recent messages, tool results, context visible to planner | Overlength, incomplete recovery  |
| Episodic     | Across runs      | Historic task fragments, successful paths, manual corrections      | Cross-user contamination, expiry |
| Profile      | Across sessions  | User preferences, commonly used formats, language style            | PII exposure, deletion requests   |
| Org Context  | Organization level | Regional definitions, metric standards, approval rules            | Version drift, permission mismatch |

The reading order of these four types also differs. Org Context typically loads first into the system context. Working Memory ensures continuity of the current task. Episodic Memory is retrieved as needed, and Profile is injected only with preferences relevant to the current task. They must not be merged into one “memory vector store.”

These four types correspond to different responsible parties. Working Memory is primarily managed by the runtime. Episodic and Profile memories require joint governance by users, business units, and compliance to decide promotion rules. Org Context should come from master data systems, semantic layers, or organizational configuration. Distinguishing responsibility ensures deletion, auditing, and version updates have clear points of control.

### 27.1.2 Relationship Between Memory and Runtime

When a runtime checkpoint is written, at minimum a snapshot of Working Memory must be saved. Otherwise, upon recovery, the system only knows `state=executing` but not which tool results the planner has already seen. For long-running tasks and human-in-the-loop (HITL) scenarios, restoration after approval depends heavily on this snapshot.

Memory should not directly execute tools or trigger state transitions. Instead, it provides context assembly for the planner, recovery material for runtime, and evidence for auditing about what contexts were injected at that time. Writing, reading, deleting, and promotion must go through platform APIs—no agent should privately maintain a local memory.

In a normal run, the memory flow should be clear: user input enters Working Memory; the planner reads from Working and necessary Org Context; tool results are written back to Working Memory by the runtime; checkpoints save Working snapshots. After task completion, the system may extract candidates for Episodic Memory, but promotion depends on strategy. This separation avoids mixing short-term continuity with long-term learning within the same write operation.

This flow also benefits auditing: it enables restoring "what the model knew at that time." When a user questions an answer, the platform must present SQL queries and document references and also specify which Working entries, user preferences, and version of organizational context were injected during that run. If memory is scattered as private variables in agent code, such reconstruction is nearly impossible.

### 27.1.3 Misuse Risks in Memory

The first misconception is treating Memory as chat history. Chat history is only one input to Working Memory and cannot shoulder user profiles, organizational context, or long-term task experience.

The second misconception is equating Memory with Retrieval-Augmented Generation (RAG). RAG mainly handles corporate documents and knowledge bases, emphasizing citation sources; Memory handles user and task context, emphasizing permissions, deletions, and recovery. They can collaborate but should not mix indexing and permission models.

The third misconception is letting the model decide what to remember permanently. Promotion to long-term memory must pass policies for PII, permissions, and user confirmation. The model can suggest, but the platform decides what to write.

The fourth misconception is only “adding memory” without “deleting memory.” Employee turnover, tenant offboarding, organizational changes, and compliance deletion requests all require the system to clear parts of memory. Without delete and export capabilities in the Memory API, launching long-term memory too early increases future migration costs.

---
## 27.2 Working Memory and Checkpoints

### 27.2.1 Saving the Visible Context of the Current Run

Working Memory stores the short-term context for the current Run or session. It does not need to persist everything permanently but must ensure that the Planner can continue operating. Typical fields include role, content, timestamp, source, tool call ID, and summaries.

```python
from core.memory import MemoryMessage, MessageRole, MemoryStore

store = MemoryStore()
wm = store.get_working("run-demo")
wm.append(MemoryMessage(
    role=MessageRole.USER,
    content="East China SKUs declining?",
    metadata={"source": "user_input"},
))
wm.append(MemoryMessage(
    role=MessageRole.TOOL,
    content='{"rows":[{"sku":"A001","delta":-0.12}]}',
    metadata={"source": "tool_result", "tool_call_id": "tc-1"},
))

snapshot = wm.snapshot()
restored = store.get_working("run-demo-restored")
restored.restore(snapshot)
```

The mini-platform currently implements a minimal Working Memory: `append`, `snapshot`, `restore`, and truncation by message count. Production systems also require token-level windows, summarization, result referencing, and filtering by source.

### 27.2.2 Why Checkpoints Must Contain Working Memory

Saving only the state machine is insufficient. Suppose a business analytics Run has executed SQL and the tool returned a sales drop for a specific SKU; then the Pod restarts before report generation. If the checkpoint lacks `working_snapshot`, the restored Planner might re-run the query or even see different results due to new data arriving. The user sees the same Run, but internally the system’s factual chain has changed.

Therefore, checkpoint payloads should minimally include:

```python
checkpoint_payload = {
    "run_id": run_ctx.run_id,
    "state": sm.state.value,
    "step_index": run_ctx.step_index,
    "tool_calls": [...],
    "working_snapshot": wm.snapshot(),
}
```

Working Memory should not store large tool results. Ten-thousand-line CSVs, lengthy PDFs, or full logs should be placed in object storage or result tables. Working Memory stores only samples, summaries, schema, row counts, hashes, and `result_ref`s. This allows Planner context restoration without overwhelming the model’s context window.

Working Memory content should also distinguish “for the model” versus “for auditing.” The model only needs summaries
## 27.3 Long-Term Memory, User Profiles, and Organizational Context

### 27.3.1 Episodic vs. Profile

Episodic Memory stores "what happened during a specific task," while Profile stores "a particular user’s long-term preferences." The two are easily confused. For example, a user’s last confirmation that “East China region is counted by store district” is a fact from a specific task and may be stored in Episodic Memory; a user frequently requesting “output tables with year-over-year comparison” is a preference likely stored in Profile.

Long-term memory cannot be written automatically from dialogue directly. A more reliable process is: candidate extraction, deduplication and merging, sensitive information review, user confirmation or policy approval, and version-controlled writing. Rejections, modifications, and deletions must all be logged. Otherwise, memory will become increasingly polluted, and the model may mistakenly treat temporary judgments as long-term facts.

For instance, when a user says “always give me tables going forward,” it can be a candidate for Profile; when a user says “temporarily use last month’s criteria this time,” it should not be promoted to a long-term preference; when a user corrects an indicator definition during an error analysis, it may belong to Episodic Memory but should only be saved long-term after confirming it is not a one-time exception. Memory promotion is not a simple text extraction task but a governance process.

### 27.3.2 Org Context

Organizational Context belongs to enterprise context—it is not personal memory. Regional definitions, indicator criteria, approval chains, master data versions, and permission domains should be managed by organization and version. Its update frequency and permission boundaries differ entirely from user Profile.

For example, “which stores belong to the East China region” should come from organizational master data or semantic layer versions—not from a particular user’s historical queries. When the Planner assembles context, it should first inject organizational criteria, then stitch together the Working Window, and finally retrieve Episodic Memory as needed. This prevents a user’s private memory from polluting the enterprise definitions.

Org Context also requires invalidation mechanisms. After organizational restructuring, indicator renaming, or region merging, old memories must not remain valid by default. The Memory API should return version and validity period so Trace can record the organizational criteria used in the current response.

Org Context is closely related to the semantic layer but has different focuses. The semantic layer defines indicators, dimensions, and SQL generation criteria; Org Context injects the current organization, permissions, approval chains, and business terminology into the Planner. When DataAgent generates SQL, it follows the semantic layer as the source of truth, but when generating explanations and approval paths, it simultaneously uses Org Context.

---
## 27.4 Boundaries Between Memory and RAG

RAG and Memory both incorporate external information into the context, but they are not the same thing. RAG targets documents, knowledge bases, table schemas, and policies, emphasizing citing sources and traceable facts. Memory targets users, tasks, and runtime context, emphasizing continuity, restoration, preferences, and organizational norms.

*Table 27-2: Differences Between Memory and RAG. Source: Compiled by the authors.*

| Dimension          | Memory                            | RAG                                   |
|--------------------|---------------------------------|-------------------------------------|
| Main Focus         | Users, runs, task experience, organizational norms | Documents, knowledge bases, table schemas, policies |
| Permission Boundaries | User, tenant, organization, run | Document permissions, knowledge domains, classification level |
| Citation Requirement | Requires recording source of injection, not necessarily displaying citation | Usually requires citation |
| Deletion Requirement | User deletion, tenant cleanup, expiration | Document removal, index updates |
| Typical Risks       | Cross-user contamination, long-term memory errors | Retrieval noise, permission mismatches |

The two should work together. For example, DataAgent first obtains organizational metric definitions from Org Context, then uses RAG to retrieve metric specification documents, and finally uses Working Memory to retain the current round SQL results. When responding, document-based evidence comes from RAG, while current task continuity is maintained by Memory. Avoid letting RAG index users’ private conversations, and don’t let Memory take on document retrieval responsibilities.

Once the boundary is blurred, a common accident is “private memory being publicly cited.” For example, if a user uploads unpublished business data in conversation and that dialogue is indexed as RAG documents, another user may retrieve it by querying similar questions. Memory must first enforce isolation by user, tenant, and run before considering vector retrieval.

---
## 27.5 Context Overflow Management

The most common engineering challenge with memory is context bloat. Multi-turn conversations, tool outputs, retrieved snippets, user preferences, and organizational standards all stack together and quickly exceed the model’s context window. Governance cannot rely solely on “summarizing history,” because summaries might rewrite numbers, lose evidence, or confuse versions.

A more robust approach is hierarchical pruning. The Working memory retains the most recent user intents, the last successful tool results, key errors, and the current plan; large tool outputs are replaced with references; Episodic memory retrieval uses top-k and tenant filtering; Profile only injects task-relevant preferences; Org Context only injects standards required for the current task. Critical numeric values, SQL, approval comments, and artifact hashes should never be rewritten by LLM-generated summaries.

mem0 emphasizes extracting, merging, and retrieving long-term memory from conversations (Chhikara et al. 2025). Letta inherits MemGPT’s idea of main memory and external memory paging, explicitly differentiating storage inside and outside the model context (Packer et al. 2023). These concepts inspire platform design, but enterprise deployments must still wrap vendor SDKs with adapters. Deletion, export, tenant isolation, and audit cannot be entrusted to black-box long-term memory.

Context governance must also be part of evaluation. The test set cannot focus only on final answers; it must verify whether expired memory was used, whether Profile was mistakenly treated as fact, whether RAG documents were confused for user preferences, and whether deleted snippets are still recalled. Memory-related bugs are often not syntax errors, but “using information that should not have been used.”

---
## 27.6 mini-platform Deployment Path

### 27.6.1 Current Implementation

The current `core/memory/` implements a minimal Working Memory. In the practical project Run chain, `RunContext.working_memory` appends messages after Tool Calls, and `RunLoop._save_checkpoint` writes the `working_snapshot`. Episodic, Profile, Org, promotion, and token-level sliding windows remain production extension goals.

```text
mini-platform/core/memory/
├── __init__.py
├── working.py
└── store.py

core/runtime/
├── run_models.py
└── run_loop.py
```

### 27.6.2 Run Verification

You can run the practical project from the `mini-platform` root directory and inspect checkpoints.

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py start
```

The checkpoint is located at `projects/multi-agent-workflow/.checkpoints/<run_id>.json`, where the `working_snapshot` contains user messages and tool messages. The production version should be extended to token-level windows, result references, delete APIs, promotion APIs, and organizational context versioning.

### 27.6.3 Release Gate

Before Memory goes live, at least five questions must be answered.

*Table 27-3: Memory Release Gate. Source: Compiled by this book.*

| Gate        | Check Question                                                      |
|-------------|-------------------------------------------------------------------|
| Restore     | Does the checkpoint include a Working Snapshot sufficient to rebuild the Planner context? |
| Isolation   | Are Episodic and Profile filtered by user, tenant, and organization? |
| Deletion    | Can user deletion and tenant cleanup cover long-term memory?     |
| Expiry      | Does Org Context have versioning and invalidation mechanisms?    |
| Context Budget | Is there a limit on total Tool results, RAG fragments, and Memory fragments? |

The first version can focus on solid Working Memory and checkpointing. If long-term memory and user profiles lack deletion, confirmation, and audit capabilities, it is better not to go live with them than to let the system quietly "permanently remember" user conversations.

Practical acceptance can design two scenarios: one where a Pod restarts and continues generating reports, verifying that `working_snapshot` can restore the Planner context; another where the user deletes preferences and then queries again, verifying that Profile is no longer injected. The former proves Memory supports runtime recovery, the latter that long-term memory is subject to governance constraints.

Production APIs can evolve in four capability groups. The first group is Working API, providing append, window, snapshot, and restore. The second group is long-term memory API, providing propose, approve, merge, and delete. The third group is organizational context API, providing get_org_context, version, and invalidate. The fourth group is audit API, reporting which memories were injected during the run, from which version, and whether they were deleted by the user. Clear API grouping makes it easier to integrate mem0, Letta, or self-developed vector stores later.

Memory must also have quotas. After long-term use by a user, Profile, Episodic, and Working snapshots will grow; without quotas, the system accumulates growing historical noise. Quotas can be set by user, tenant, memory type, and validity period. When exceeding quota, the system should prioritize evicting expired, low-confidence, and unreferenced entries rather than simply deleting the most recent records.

Beyond quotas, memory entries should retain source and confidence metadata. Preferences confirmed by users, policies from organizational configuration, candidates extracted by the model—all have different trust levels that influence deletion and overwrite rules. A common practice is to tag Profile entries with `source=confirmed_by_user` or `source=model_suggested`, and Org Context with `source=semantic_layer` and version numbers. The Planner can prioritize high-confidence entries during reads; audit replay can explain why a certain memory was injected rather than showing only a seemingly relevant context snippet.

Changes to Memory should also enter the release process. Adding new memory types, changing Profile promotion strategies, adjusting Org Context expiration times—all affect the model's visible context. A stable approach is to record strategy versions in the Trace and use regression testing to check whether old issues change answers under new strategies. Memory is not static configuration; it continuously affects Agent behavior and thus should be version-managed alongside Prompts, tool schemas, and semantic layers.

Finally, the Memory user experience should be restrained. The system does not need to show all memories to users but should explain in key scenarios, "I am analyzing this based on previously confirmed policies," and provide interfaces for viewing and deleting. This way, users know why the system remembers something and how to correct it. Invisible, undeletable, unexplainable long-term memory is hard to adopt in enterprise production environments.

The first version should avoid making long-term memory enabled by default. It can initially enable Profile candidates only in internal or low-risk scenarios, requiring user confirmation before writing; Episodic only stores summaries and evidence references of successful tasks without saving original sensitive text; Org Context is loaded only from controlled configurations. This way, Memory first serves continuity and recovery, then gradually expands to personalization and organizational learning.

This is not conservative but reduces rework. Once long-term memory writes大量错误偏好 (a large amount of incorrect preferences), expired policies, or sensitive fragments, subsequent cleanup will be harder than adding features. Stable Working Memory, checkpointing, deletion, and export should come first, then automated promotion, to follow the enterprise system evolution sequence.

---
## Chapter Recap

1. Memory is a platform subsystem; it is not the same as chat history, nor is it the same as RAG.
2. Working Memory must be checkpointed; otherwise, after Runtime recovery, the Planner will lose its memory.
3. Episodic, Profile, and Org Context have different scopes, permissions, and update frequencies, and cannot be stored together.
4. RAG handles document and knowledge referencing, while Memory is responsible for task continuity, user preferences, and organizational consistency.
5. For long-term memory, issues such as deletion, isolation, versioning, and auditing must be addressed before considering automatic promotion.
## Further Reading

- [Chapter 22 Agent Runtime](ch22-agent-runtime.md)
- [Chapter 20 Enterprise Knowledge Base RAG](../../part04-vector-knowledge/ch/ch20-rag.md)
- [Chapter 25 Planner and Orchestration Patterns](ch25-planner.md)
- [Chapter 33 Semantic Layer and Metric Definitions](../../part06-dataagent/ch/ch33.md)
- [Chapter 38 Agent Trace and Session Replay](../../part07-observability-eval/ch/ch38-trace.md)
- [Chapter 50 Policy and Permissions](../../part10-security-org/ch/ch50.md)
- `mini-platform/projects/multi-agent-workflow/README.md`
## References

Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Chhikara, P., Khant, P., Yadav, P., et al. (2025). mem0: Building production-ready AI agents with scalable long-term memory. [https://arxiv.org/abs/2504.19437](https://arxiv.org/abs/2504.19437)

Packer, C., Wooders, S., Lin, K., et al. (2023). MemGPT: Towards LLMs as operating systems. [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

Letta. (n.d.). *Letta documentation*. [https://docs.letta.com/](https://docs.letta.com/)

Zhang, Z., Wang, Y., Fang, C., et al. (2024). A survey on the memory mechanism of large language model-based agents. [https://arxiv.org/abs/2404.13501](https://arxiv.org/abs/2404.13501)

LangChain. (n.d.). *Persistence*. LangGraph. [https://docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
