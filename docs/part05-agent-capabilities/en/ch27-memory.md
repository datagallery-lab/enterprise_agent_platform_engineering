# Chapter 27: Memory Systems

---
Memory is the platform mechanism that controls what context an Agent can reuse, how long that context remains valid, who can see it, and when it must expire or be deleted. It is not a place to stuff all previous conversations back into the prompt, and it is not a renamed enterprise knowledge base. Its job is to restore context inside one Run, reuse confirmed user preferences safely, inject organizational standards consistently, and keep Memory separate from RAG.

Chapter 22 requires checkpoints to reconstruct the Planner's visible context. Otherwise, after a process restarts, the Planner may forget that the previous SQL query already returned results, reselect tables, call tools again, or produce an answer that differs from the one before the restart. Chapter 25 adds that each Planner decision depends on Tool Call history, errors, and Memory fragments. Memory is therefore part of Runtime recoverability, not an optional personalization feature.

Consider a DataAgent flow. The user first asks which SKUs declined in East China last week. The system queries and returns results. The user then asks, "How about North China?" Planner must remember the time range, metric definition, and comparison method from the previous turn, while replacing only the region. When the same user returns next week, the system may know that she prefers tables with year-over-year comparison. But which stores belong to East China is organizational context, not personal memory, and should come from master data or the semantic layer.

The chapter separates four layers: Working Memory for the current Run, Episodic Memory for past task fragments, Profile for confirmed long-term user preferences, and Org Context for enterprise definitions, permissions, and process standards. Mixing them into one vector store creates privacy, deletion, versioning, and permission problems. A production platform needs controlled memory layers between forgetting everything and remembering everything forever.

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

The reading order of these four types also differs. Org Context typically loads first into the system context. Working Memory ensures continuity of the current task. Episodic Memory is retrieved as needed, and Profile is injected only with preferences relevant to the current task. They must not be merged into one generic memory vector store.

These four types correspond to different responsible parties. Working Memory is primarily managed by the runtime. Episodic and Profile memories require joint governance by users, business units, and compliance to decide promotion rules. Org Context should come from master data systems, semantic layers, or organizational configuration. Distinguishing responsibility ensures deletion, auditing, and version updates have clear points of control.

### 27.1.2 Relationship Between Memory and Runtime

When a runtime checkpoint is written, at minimum a snapshot of Working Memory must be saved. Otherwise, upon recovery, the system only knows `state=executing` but not which tool results the planner has already seen. For long-running tasks and human-in-the-loop (HITL) scenarios, restoration after approval depends heavily on this snapshot.

Memory should not directly execute tools or trigger state transitions. Instead, it provides context assembly for the planner, recovery material for runtime, and evidence for auditing about what contexts were injected at that time. Writing, reading, deleting, and promotion must go through platform APIs. No agent should privately maintain a local memory.

In a normal run, the memory flow should be clear: user input enters Working Memory; the planner reads from Working and necessary Org Context; tool results are written back to Working Memory by the runtime; checkpoints save Working snapshots. After task completion, the system may extract candidates for Episodic Memory, but promotion depends on strategy. This separation avoids mixing short-term continuity with long-term learning within the same write operation.

This flow also benefits auditing: it enables restoring "what the model knew at that time." When a user questions an answer, the platform must present SQL queries and document references and also specify which Working entries, user preferences, and version of organizational context were injected during that run. If memory is scattered as private variables in agent code, such reconstruction is nearly impossible.

### 27.1.3 Misuse Risks in Memory

The first misconception is treating Memory as chat history. Chat history is only one input to Working Memory and cannot shoulder user profiles, organizational context, or long-term task experience.

The second misconception is equating Memory with Retrieval-Augmented Generation (RAG). RAG mainly handles corporate documents and knowledge bases, emphasizing citation sources; Memory handles user and task context, emphasizing permissions, deletions, and recovery. They can collaborate but should not mix indexing and permission models.

The third misconception is letting the model decide what to remember permanently. Promotion to long-term memory must pass policies for PII, permissions, and user confirmation. The model can suggest, but the platform decides what to write.

The fourth misconception is adding memory without deleting memory. Employee turnover, tenant offboarding, organizational changes, and compliance deletion requests all require the system to clear parts of memory. Without delete and export capabilities in the Memory API, launching long-term memory too early increases future migration costs.

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

Saving only the state machine is insufficient. Suppose a business analytics Run has executed SQL and the tool returned a sales drop for a specific SKU; then the Pod restarts before report generation. If the checkpoint lacks `working_snapshot`, the restored Planner might re-run the query or even see different results due to new data arriving. The user sees the same Run, but internally the system's factual chain has changed.

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

Working Memory should not store large tool results. Ten-thousand-line CSVs, lengthy PDFs, or full logs should be placed in object storage or result tables. Working Memory stores only samples, summaries, schema, row counts, hashes, and `result_ref`s. This allows Planner context restoration without overwhelming the model's context window.

Working Memory content should also distinguish model-visible context from audit evidence. The model only needs task-relevant summaries, examples, and errors; audit may need original result references, hashes, and execution times. Both can be linked from the same checkpoint, but they should not all be injected into the prompt.

## 27.3 Long-Term Memory, User Profiles, and Organizational Context

### 27.3.1 Episodic vs. Profile

Episodic Memory stores what happened during a specific task, while Profile stores a particular user's long-term preferences. The two are easily confused. For example, a user's last confirmation that East China is counted by store district is a fact from a specific task and may be stored in Episodic Memory; a user frequently requesting tables with year-over-year comparison is a preference likely stored in Profile.

Long-term memory cannot be written automatically from dialogue directly. A more reliable process is: candidate extraction, deduplication and merging, sensitive information review, user confirmation or policy approval, and version-controlled writing. Rejections, modifications, and deletions must all be logged. Otherwise, memory will become increasingly polluted, and the model may mistakenly treat temporary judgments as long-term facts.

For instance, when a user says that future answers should use tables, it can be a candidate for Profile; when a user says to temporarily use last month's criteria for this task, it should not be promoted to a long-term preference; when a user corrects an indicator definition during an error analysis, it may belong to Episodic Memory but should only be saved long-term after confirming it is not a one-time exception. Memory promotion is a governance process, not a simple text extraction task.

### 27.3.2 Org Context

Organizational Context belongs to enterprise context. It is not personal memory. Regional definitions, indicator criteria, approval chains, master data versions, and permission domains should be managed by organization and version. Its update frequency and permission boundaries differ entirely from user Profile.

For example, the list of stores that belong to East China should come from organizational master data or semantic layer versions, not from a particular user's historical queries. When the Planner assembles context, it should first inject organizational criteria, then stitch together the Working Window, and finally retrieve Episodic Memory as needed. This prevents a user's private memory from polluting enterprise definitions.

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

The two should work together. For example, DataAgent first obtains organizational metric definitions from Org Context, then uses RAG to retrieve metric specification documents, and finally uses Working Memory to retain the current round SQL results. When responding, document-based evidence comes from RAG, while current task continuity is maintained by Memory. Avoid letting RAG index users' private conversations, and do not let Memory take on document retrieval responsibilities.

Once the boundary is blurred, a common accident is public citation of private memory. For example, if a user uploads unpublished business data in conversation and that dialogue is indexed as RAG documents, another user may retrieve it by querying similar questions. Memory must first enforce isolation by user, tenant, and run before considering vector retrieval.

---
## 27.5 Context Overflow Management

The most common engineering challenge with memory is context bloat. Multi-turn conversations, tool outputs, retrieved snippets, user preferences, and organizational standards all stack together and quickly exceed the model's context window. Governance cannot rely solely on history summaries, because summaries might rewrite numbers, lose evidence, or confuse versions.

A stronger approach is hierarchical pruning. The Working memory retains the most recent user intents, the last successful tool results, key errors, and the current plan; large tool outputs are replaced with references; Episodic memory retrieval uses top-k and tenant filtering; Profile only injects task-relevant preferences; Org Context only injects standards required for the current task. Important numeric values, SQL, approval comments, and artifact hashes should never be rewritten by LLM-generated summaries.

mem0 emphasizes extracting, merging, and retrieving long-term memory from conversations (Chhikara et al. 2025). Letta inherits MemGPT's idea of main memory and external memory paging, explicitly differentiating storage inside and outside the model context (Packer et al. 2023). These concepts inspire platform design, but enterprise deployments must still wrap vendor SDKs with adapters. Deletion, export, tenant isolation, and audit cannot be entrusted to black-box long-term memory.

Context governance must also be part of evaluation. The test set cannot focus only on final answers; it must verify whether expired memory was used, whether Profile was mistakenly treated as fact, whether RAG documents were confused for user preferences, and whether deleted snippets are still recalled. Memory-related bugs are often not syntax errors; the problem is usually using information that should not have been used.

Evaluation samples should cover multi-turn processes as well as single-turn Q&A. For example, the first turn asks for East China, the second turn says to switch to North China, the third turn deletes a personal preference, and the fourth turn runs after the organizational definition has changed. Such samples test whether Working, Profile, and Org Context each take effect under the right rules. Single-turn samples can make Memory look usable while hiding cross-turn contamination and stale definitions.

---
## 27.6 Memory and Runtime Read/Write Interfaces

### 27.6.1 Working Memory Implementation Entry Point

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

### 27.6.2 Memory Runtime Verification

You can run the practical project from the `mini-platform` root directory and inspect checkpoints.

```bash
cd mini-platform
python3 projects/multi-agent-workflow/run.py start
```

The checkpoint is located at `projects/multi-agent-workflow/.checkpoints/<run_id>.json`, where the `working_snapshot` contains user messages and tool messages. The production version should be extended to token-level windows, result references, delete APIs, promotion APIs, and organizational context versioning.

### 27.6.3 Design Questions Before Runtime Integration

Before Memory connects to Runtime, at least five questions must be answered. These questions decide whether Memory is a runtime capability or merely history appended to a prompt.

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

Beyond quotas, memory entries should retain source and confidence metadata. Preferences confirmed by users, policies from organizational configuration, candidates extracted by the model all have different trust levels that influence deletion and overwrite rules. A common practice is to tag Profile entries with `source=confirmed_by_user` or `source=model_suggested`, and Org Context with `source=semantic_layer` and version numbers. The Planner can prioritize high-confidence entries during reads; audit replay can explain why a certain memory was injected rather than showing only a seemingly relevant context snippet.

Changes to Memory should also enter the release process. Adding new memory types, changing Profile promotion strategies, and adjusting Org Context expiration times all affect the model's visible context. A stable approach is to record strategy versions in the Trace and use regression testing to check whether old issues change answers under new strategies. Memory is not static configuration; it continuously affects Agent behavior and thus should be version-managed alongside Prompts, tool schemas, and semantic layers.

Finally, the Memory user experience should be restrained. The system does not need to show all memories to users but should explain in key scenarios, "I am analyzing this based on previously confirmed policies," and provide interfaces for viewing and deleting. This way, users know why the system remembers something and how to correct it. Invisible, undeletable, unexplainable long-term memory is hard to adopt in enterprise production environments.

The first version should avoid making long-term memory enabled by default. It can initially enable Profile candidates only in internal or low-risk scenarios, requiring user confirmation before writing; Episodic only stores summaries and evidence references of successful tasks without saving original sensitive text; Org Context is loaded only from controlled configurations. This way, Memory first serves continuity and recovery, then gradually expands to personalization and organizational learning.

This sequence reduces rework. Once long-term memory stores many incorrect preferences, expired policies, or sensitive fragments, cleanup becomes harder than adding missing features. Stable Working Memory, checkpointing, deletion, and export should come first, followed by automated promotion.

---
### 27.6.4 Pollution Control and Evaluation Evidence for Memory

The hardest Memory problem after launch is not that the system fails to remember, but that it remembers the wrong thing and keeps using it. An incorrect preference, expired organizational rule, or prompt-injection-contaminated fact can enter long-term memory and affect later Runs repeatedly. Enterprise platforms should treat Memory writes as governed actions, not as ordinary context concatenation.

Write decisions should consider source, confidence, expiry time, tenant boundary, and deletion responsibility. After a Memory entry is written, Trace should be able to show which Run produced it. Different memory classes need different approval strength. Working Memory belongs to the current Run and can be checkpointed. Episodic Memory records task experience and should carry timestamp and source. Profile Memory affects user preference and is safer when confirmed by the user or administrator. Org Context represents business rules and should not be written from one conversation.

Memory evaluation should cover more than hit rate. The platform should check whether information that should be remembered is used correctly, whether information that should not be remembered is filtered, and whether expired or revoked information stops taking effect. For DataAgent, metric definitions, user filtering habits, and report preferences may enter memory, but they must still obey Chapter 33 semantic-layer definitions and Chapter 50 permission policy.

Deletion should exist in the first version. Enterprise users may request removal of personal preferences, administrators may revoke incorrect organization context, and compliance teams may delete records tied to specific data subjects. A minimal implementation should retain `memory_id`, source Run, write time, scope, and expiry policy so later governance can locate, invalidate, and delete records.

## 27.7 Memory Write Admission and Lifecycle

The model should not freely decide what enters Memory. It can propose a candidate worth remembering, but the platform must decide whether to persist it. Admission rules should inspect source, user authorization, sensitivity level, verifiability, and validity period. A user saying "use East China for this task" does not mean the platform should create a long-term profile saying the user only cares about East China. A one-time approval for exceptional access also should not become permission context for later Runs.

Long-term memory needs a lifecycle. Preference entries may have longer validity, but users should still be able to view and delete them. Task experience should bind to scenario and version so an old workflow does not pollute a new one. Organization context should follow changes in policy, permission, and data domain. Expiry should depend on time and dependency. If a semantic-layer metric is retired, historical task experience referring to that metric should no longer guide new work.

Deletion must cover storage, vector indexes, caches, summaries, evaluation samples, and Trace visibility rules where applicable. Content that has become immutable audit evidence may be retained for compliance, but it should no longer be used as active Memory. Production value comes from controlled reuse, not from indiscriminate accumulation.

## 27.8 Memory Pollution Detection and Repair

Memory pollution usually accumulates gradually. A model turns one-time context into a long-term preference, summarizes an incorrect answer into experience, writes an unverified assumption into a profile, or retrieves another tenant's similar question into the current task. The answer can still sound fluent, so user complaints are a late signal.

Detection should combine Trace and evaluation. The platform can sample answers under three conditions: no Memory, candidate Memory, and production Memory. If Memory pushes the answer away from permission, metric definition, or user intent, the entry becomes a pollution candidate. For high-value tasks, the model can output `MemoryRef` when using long-term memory, showing which entry affected which decision.

Repair should happen by layer. Wrong text can be deleted or down-weighted. Wrong summaries should be regenerated. Wrong profiles should be confirmed by the user or an administrator. Retrieval rules may need recall or filtering changes. After repair, affected samples should be replayed to confirm the issue has not returned in another form. Without this governance, Memory makes the Agent seem more familiar while preserving wrong experience inside the platform.

## 27.9 Memory and the User Control Plane

If Memory runs only in the background, users cannot build trust. Users should be able to see which long-term preferences the system remembers, which items came from previous tasks, and which organization context is maintained by administrators. Not every memory needs full display, but the product needs an explanation and control entry so users can correct, delete, or limit use.

The control plane should distinguish personal memory from organizational memory. Personal preferences can be modified by users. Organization context should be maintained by business or data owners. Task experience may need platform review before it is promoted. If these categories are mixed, a user deleting a personal preference may accidentally remove a shared rule, or an administrator updating organization context may overwrite personal settings.

The first version can provide a simple view-and-disable capability: which Runs used Memory, which type of Memory was referenced, and whether the user can mark a Memory entry as "do not use again." This small interface turns Memory from a black box into a governable capability.

User control also reduces the cost of misuse. If a user finds a wrong memory and can only restate the correction in chat, the system may continue retrieving the old entry. If the user can mark the entry as wrong, the platform can remove it from retrieval, summaries, and evaluation samples. The more controllable Memory becomes, the more willing users are to let the system reuse historical context.

Memory review should always answer four questions: who writes it, who can read it, how long it is stored, and how it is corrected. Without admission, noise accumulates. Without read permissions, sensitive information spreads. Without expiry, old context misleads the model. Without repair, wrong memory repeats.

Context compression also needs traceability. Compressing a long conversation into a summary saves tokens, but the summary can lose information or add interpretation. Important tasks should preserve both the original event references and the summary version so reviewers can return to the source record when something goes wrong. The boundary between Memory and RAG remains important here: RAG manages enterprise knowledge and evidence, while Memory manages task context, preferences, and organization usage patterns. They complement each other, but one should not replace the other.

Working Memory should follow the Run lifecycle. After a task ends, the platform must decide which content is retained only for audit, which content can become a user-preference candidate, and which content must be discarded immediately. If every context item is saved long term by default, the system accumulates sensitive and stale information. Long-term memory is safer with a suggest-confirm pattern: the model may identify a candidate preference, but before writing it, the system explains the source and intended use and requests confirmation when needed. Automatic writes may look intelligent, but they can turn accidental behavior into long-term preference.

Organization context should be maintained by the organization rather than growing out of personal conversations. Company metrics, approval rules, brand language, and security policies should come from formal assets. A user correcting the model in one dialogue may produce a feedback sample, but it should not directly overwrite shared organization rules. Pollution signals should also be observable: repeated user correction of the same preference, sudden use of old information in a task class, or contradictory organization definitions across users can all indicate write or read errors in Memory.

High-risk scenarios should use Memory conservatively. Contract review, financial analysis, permission decisions, and compliance advice should rely on current evidence and formal rules rather than historical preference. Memory can improve continuity, but it should not replace evidence or policy. Memory reads should also be explainable. The debug view should show which preferences, historical tasks, or Org Context entries were used. Users do not need to see this detail every time, but the platform needs to explain source influence when an answer depends on history.

Compression should be structured by layer. Short-term task summaries can keep the user question, executed tools, key results, and unfinished items. Long-term preference summaries should keep stable choices only. Org Context should reference formal rules. Collapsing everything into one natural-language summary loses permission, time, and evidence boundaries. A stable Memory schema is more useful than a beautiful paragraph: preferences, task summaries, organization-rule references, user profile entries, and historical artifacts should not all be stored as free text.

Deletion must truly take effect. When a user asks to remove a preference or sensitive item, the platform needs to clean primary storage, indexes, caches, and downstream copies, and record the deletion result. If Memory has entered training data or evaluation samples, additional handling is required. Enterprise users care whether deletion can be proven, not whether the item disappears from the interface alone. Cross-device and cross-channel use also needs identity boundaries: the same user may use the Agent from web, chat, mobile, and API channels, and the platform must decide which memories can be shared across channels and which belong only to one organization space.

Memory evaluation should include pollution tests. Inject wrong preferences, expired rules, malicious context, or conflicting memory entries, then check whether the system uses them blindly. Without pollution tests, Memory risk becomes harder to detect the longer the system runs. Evaluation environments should also isolate Memory from production history. If the model reads historical answers or user preferences during evaluation, scores become hard to compare across versions.

Long-term memory needs conflict handling. User preferences change, organization rules update, and memories from different sources may disagree. The platform should choose by source trust, update time, and scope, and ask for confirmation or defer to formal rules when conflicts cannot be resolved. Explicit memory and inferred memory should also be separated. A preference actively saved by the user carries more trust than a preference inferred from behavior; inferred memory should be treated as a hint and confirmed before it affects important outcomes.

Memory should be measured by impact, not volume. The platform can compare task completion, user corrections, and complaints with and without Memory. If a memory type often leads to user correction, it should be down-weighted or its write rule should change. More memory is not automatically better; useful, controlled memory is what should remain.

## Chapter Recap

Memory is a platform subsystem, not chat history and not RAG. Working Memory must enter checkpoints so Runtime recovery preserves Planner context. Episodic, Profile, and Org Context have different scopes, permissions, and update frequency and should not be mixed into one generic store. RAG handles documents and evidence; Memory handles task continuity, user preference, and organization context. Long-term memory should solve deletion, isolation, versioning, audit, write admission, pollution repair, and user control before automated promotion becomes default.

## References

Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6), 186345. [https://doi.org/10.1007/s11704-024-40231-1](https://doi.org/10.1007/s11704-024-40231-1)

Chhikara, P., Khant, P., Yadav, P., et al. (2025). mem0: Building production-ready AI agents with scalable long-term memory. [https://arxiv.org/abs/2504.19437](https://arxiv.org/abs/2504.19437)

Packer, C., Wooders, S., Lin, K., et al. (2023). MemGPT: Towards LLMs as operating systems. [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)

Letta. (n.d.). *Letta documentation*. [https://docs.letta.com/](https://docs.letta.com/)

Zhang, Z., Wang, Y., Fang, C., et al. (2024). A survey on the memory mechanism of large language model-based agents. [https://arxiv.org/abs/2404.13501](https://arxiv.org/abs/2404.13501)

LangChain. (n.d.). *Persistence*. LangGraph. [https://docs.langchain.com/oss/python/langgraph/persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
