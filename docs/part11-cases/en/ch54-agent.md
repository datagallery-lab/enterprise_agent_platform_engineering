# Chapter 54 Business case admission and writing method

---

Enterprise Agent cases are easy to turn into feature demos with outcome claims. A team builds a knowledge assistant that answers policy questions in a demo environment, and the draft becomes "enterprise knowledge management efficiency improvement." A ticket Agent produces a fluent complaint summary, and the draft becomes "customer service automation." A development Agent runs one code-change path in a repository, and the draft becomes "developer productivity improvement." These statements look complete, but they do not survive review. Readers need to know where the task sits in the business process, which data and tools the system used, which actions were actually automated, where the system stopped for human confirmation, and whether failures can be replayed.

The difficult part of case writing is evidence, not dramatic storytelling. An offline experiment can show model behavior on one sample set, but it cannot prove that production permissions, audit, cost, and human takeover are ready. A screenshot can show the interaction shape, but it cannot prove that tool calls are governed. User feedback can show that a direction has value, but it cannot replace evaluation sets, Trace records, or review logs. If a case skips these limits, readers may assume that connecting a model and a knowledge base is enough to create trustworthy automation.

The first edition therefore starts with case admission rules instead of fabricated company stories. An enterprise Agent case must meet a stricter editorial bar than an ordinary product case. It must explain what happened and why the reader should trust the evidence. Before material enters the main text, the author should describe the real task, provide evidence for data, tools, permissions, evaluation, and human confirmation, and connect the case back to the platform capabilities discussed earlier. If that evidence is missing, the material can remain in the internal backlog, but fictional companies, synthetic screenshots, or unverified benefit numbers cannot be used to fill the gap.

Enterprise knowledge assistants, ticketing or customer service Agents, development Agents, and operations Agents can all demonstrate platform capability. They are also the easiest scenarios to flatten into generic feature stories. A knowledge assistant must prove evidence citation, permission filtering, and knowledge updates. A ticketing Agent must prove governed tool calls, human takeover, and content safety. A development Agent must prove code-tool permissions, long-running execution, and evaluation. An operations Agent must prove Trace, SLO, and change boundaries. Each direction can become a case only when the task, chain, evidence, and boundary can be reconstructed. This chapter sets that evidence line for later case writing.

---

## 54.1 Case Inclusion Criteria

Before a case enters the main text, a straightforward question must be answered: can readers reconstruct how this was done from the material? If the draft only says "used Agent to improve efficiency," "integrated a knowledge base," or "automatically generated a report," but omits task input, system boundary, failure handling, and evaluation evidence, it is still promotional material rather than a case.

A qualified case must meet at least four conditions. These conditions are not editorial formatting rules. They correspond to the four places where enterprise Agent cases most often become disputed: unclear task definition, disconnected platform capability, missing chain evidence, and overstated effect. During review, the author should be able to answer why the system made a suggestion, whether unauthorized data entered the model, where an efficiency claim came from, and which record supports each statement. If those answers only exist orally, the material is not ready.

*Table 54-1: Four conditions and acceptance criteria for cases included in the main text. Source: Compiled by this book.*

| Condition | Acceptance criteria |
| --- | --- |
| Clear business task | Clearly specify user roles, inputs, outputs, decision actions, and risk boundaries |
| Corresponding platform capability | Map to Runtime, Tool Registry, MCP, Planner, Memory, RAG, Eval, Trace, or Guardrails |
| Clear data and tool topology | Describe involved systems, data objects, permissions, audits, and failure recovery actions |
| No exaggerated outcomes | Avoid reporting unverified cost reduction, efficiency improvement, accuracy, or deployment scale |

These four conditions block four common problems: unclear task, detached capability, missing evidence, and exaggerated result. Case authors should self-check with Table 54-1, and reviewers should use the same standard. If any condition cannot be confirmed, the material can enter the material repository, but it should not appear in the main text.

### 54.1.1 Tasks must be reproducible

A clear task is more than a sentence such as "sales needs automatic quoting" or "operations needs decline analysis." A reproducible task contains at least five elements: who initiates it, what input they bring, what output they expect, which actions the system may take, and which actions must stop for human confirmation.

In a quoting scenario, "generate pricing recommendations" is still too vague. A stronger description is: the salesperson selects the customer and product package in CRM; the system reads historical contracts, inventory status, and discount policies; it generates a quote draft and risk note; formal quotation, discount exceptions, and customer commitments require sales-manager confirmation. Only then can readers judge whether the design is Copilot, Workflow, or a task-execution system with an Agent loop.

### 54.1.2 Full-chain evidence coverage

Many cases show a polished result screenshot but skip how the system arrived there. For this book, screenshots only prove that the interface appeared. They do not prove that the workflow is trustworthy. Case evidence must cover input, retrieval, tool calls, permission checks, output, review, and feedback. Trace records, Tool Call logs, evaluation samples, sanitized logs, and human review sheets are often more important than final screenshots.

*Table 54-2: Case evidence materials and the conclusions they can support. Source: Compiled by this book.*

| Evidence material | Supported conclusions | Unsupported conclusions |
| --- | --- | --- |
| Sanitized task samples | Task type, input complexity, user roles | Deployment scale, business benefits |
| Tool Call records | Which systems were called, whether side effects were involved | Tool results are definitely correct |
| Trace and state machines | How the task progresses, where human confirmation occurs | Model capability is better than alternatives |
| Evaluation sets and human reviews | Quality boundary, common failure types | ROI, organizational efficiency gains |
| Sanitized screenshots | How users see results and evidence | Production workflow is stable |

Writers should control the extrapolation of evidence. One offline evaluation can indicate quality trends, but it cannot prove deployment benefits. A segment of sanitized logs can illustrate the workflow shape, but it cannot prove that the system meets production SLOs.

### 54.1.3 Sanitization scope and causal relationship preservation

Case sanitization cannot stop at changing a company name to "a certain enterprise." It must cover business identities, customer information, system domain names, field definitions, approval roles, ticket numbers, log timestamps, and metadata embedded in screenshots. Agent cases require extra care around tool-call parameters and retrieval snippets, because they often reveal internal system structure.

Sanitized material still has to preserve causal relationships. A contract number can be replaced, an approver can become a role, and a field name can be generalized, but the case must retain which input triggered which tool, which evidence supported which judgment, and which risk action required human confirmation. If sanitization leaves only a generic description, the case loses engineering value. If it preserves real system details, it creates a security risk. Editors need to calibrate between those two constraints.

*Table 54-3: Agent case sanitization checklist. Source: Compiled by this book.*

| Object | Common leakage points | Writing treatment |
| --- | --- | --- |
| Business entity | Customer names, supplier names, stores, contract numbers | Replace with roles or categories while preserving task relationships |
| Data fields | Internal field names, metric definitions, permission tags | Keep semantics, replace implementation details |
| Tool calls | Internal domain names, real APIs, account IDs | Write as interface types and necessary parameters |
| Logs and traces | Timestamps, request IDs, user IDs | Use synthetic IDs and preserve state transitions |
| Screenshots | Watermarks, navigation bars, org charts, avatars | Redraw or crop, keeping only areas needed for explanation |

If sanitization destroys the case's key causal relationships, do not force publication. Keep the material for internal review and release a public version only after enough anonymized samples are available.

## 54.2 Recommended Case Structure

Each case should follow a consistent structure so that it can cross-reference the capability chapters earlier in the book. The goal is not to impose a rigid template. It is to let readers compare different scenarios and see which capabilities come from business differences and which should be consolidated into the platform.

A case should start from the business task: who initiates it, in what context, and why fixed workflows or ordinary Q&A are insufficient. It should then describe the data and tools involved, including systems, documents, tables, APIs, and approval nodes. The Agent design should explain how Planner, tool calls, memory, retrieval, human confirmation, and result delivery divide responsibility. The execution chain should describe state transitions from input to output and show where Trace and audit evidence are recorded. Risk control and evaluation should come later: the former explains which actions are refused, downgraded, reviewed, or handed over to people; the latter explains how offline samples, manual review, online feedback, and business metrics support a limited conclusion.

This order matters. If technical terms come first, the case becomes a repeated architecture catalog. If evaluation appears too early, the case starts to sound like metric promotion. Starting from the task, then moving through data, tools, execution, and risk control, lets readers judge what problem the system solved, which platform capabilities it used, which conclusions have evidence, and where humans still make the decision.

Each part should survive editorial questioning. The business task should explain why users cannot solve it with a fixed process. Data and tools should explain which fields are read-only and which actions create side effects. Agent design should explain why planning is needed instead of a single answer. The execution chain should explain how Trace reconstructs what happened. Risk control should explain where the system stops. Evaluation should explain whether the sample and review criteria support the conclusion. If these questions cannot be answered, the case should not enter the main text.

### 54.2.1 Task-first narrative order

Weak cases often start like this: "This case uses RAG, Planner, Tool Registry, and Guardrails to build an intelligent customer service Agent." The sentence sounds complete, but it does not tell the reader why the system is needed. A better opening starts from task friction: customer service needs to handle refund disputes within minutes, while the order system, logistics system, and policy knowledge base sit in different systems; fixed workflows cover standard refunds, but they fail when promotions overlap, partial shipments occur, or a human promise has already been made.

Once the task is clear, platform capabilities have a place. RAG finds policies, Tool Registry constrains order queries and refund calculation, Human-in-the-loop handles exceptional refunds, and Trace preserves evidence. This order matches the reference book's style: show the problem first, then give the engineering structure.

### 54.2.2 Clearly specify the parts that are not automated

Agent cases often overstate automation. Mature enterprise cases clearly mark where the system stops. In sales quoting, the Agent can summarize information, generate drafts, and check discount policies, while customer commitments remain with sales. In legal review, the Agent can extract clauses and flag risks, while final legal opinions remain with legal owners. In finance analysis, the Agent can explain metric changes, while disclosure definitions remain with responsible staff.

These boundaries are prerequisites for trustworthy production systems. When writing, separate actions that are automatically completed, require confirmation, must be rejected, or should degrade to a fallback path. Readers can then judge whether the case is feasible in production.

*Table 54-4: Expressions of automation boundaries in case writing. Source: Compiled by this book.*

| Action category | What to state when writing | Example |
| --- | --- | --- |
| Automatically completed | Inputs, outputs, success conditions, and audit logs | Query historical orders and generate a refund-reason summary |
| Require confirmation | Who confirms, what is confirmed, how timeout is handled | Manager confirms an excessive discount before formal quote issuance |
| Must reject | Rejection conditions, user prompts, and logging method | User asks to bypass approval or access unauthorized contracts |
| Degraded handling | Degradation trigger and fallback path | Switch to a human knowledge-base ticket when retrieval evidence is insufficient |

### 54.2.3 Write evaluation as evidence, not slogans

Phrases such as "accuracy improvement" or "efficiency gain" only mean something when the evaluation criteria are clear. A case should state where samples come from, who annotated or reviewed them, how failures are classified, and which metrics are process indicators. For Agent cases, final-answer accuracy is only one item. Reviewers also need to know whether tool calls were correct, permissions were respected, human confirmation triggered as expected, and failures left replayable evidence.

*Table 54-5: Case evaluation metrics and their applicable boundaries. Source: Compiled by this book.*

| Metric | Suitable question | Risk |
| --- | --- | --- |
| Task completion rate | Can the system complete the whole task chain? | May hide high-risk actions corrected by humans |
| Evidence hit rate | Does the answer cite correct documents or data? | Does not prove reasoning correctness |
| Tool invocation success rate | Are tool parameters and returns contract-compliant? | Does not prove the business outcome was accepted |
| Human takeover rate | Does the system know where to pause? | Too low may imply overreach, too high may imply unusability |
| Review pass rate | Can business staff approve the result? | Depends on consistency of review standards |

Evaluation sections should also avoid treating every metric as "higher is better." Human takeover rate is the typical example. For high-risk quoting, legal review, or financial disclosure, a very low takeover rate may mean the system crossed boundaries it should have respected. For low-risk FAQ, a high takeover rate may mean the system cannot handle common requests. Task completion rate has the same issue: if the system counts requests it should have refused as completed, the metric looks good while risk rises. Case writing should state the boundary of each metric instead of turning it into a universal score.

Evaluation results should map to failure categories. A DataAgent case can classify failures into semantic-layer errors, SQL generation errors, query timeouts, evidence interpretation errors, and permission refusals. A customer service Agent can classify policy retrieval failures, order-tool failures, refund-rule conflicts, and human takeover timeouts. Failure classes help readers understand how the platform should improve, and they connect back to Chapters 38 to 42 on Trace, evaluation, cost, and SLO.

## 54.3 Correspondence with previous chapters

*Table 54-6: Correspondence between case types, earlier chapters, and engineering questions. Source: Compiled by this book.*

| Case type | Key chapters | High-risk issues |
| --- | --- | --- |
| Enterprise knowledge assistant | Chapters 20, 21, 27, 40 | Knowledge update, evidence citation, memory boundaries, answer evaluation |
| Ticketing or customer service Agent | Chapters 8, 23, 30, 51 | Structured output, tool invocation, human takeover, content safety |
| Development Agent | Chapters 22, 23, 28, 39 | Long-task execution, code-tool permissions, multi-Agent collaboration, evaluation |
| Operations Agent | Chapters 38, 42, 45, 46 | Trace, SLO, gateway governance, GitOps change boundaries |

Table 54-6 prevents cases from drifting away from the body of the book. It does not require every case to cover every chapter. A ticketing Agent without structured output and human takeover cannot support the claims in Chapters 8 and 30. An operations Agent without Trace, SLO, and change boundaries is still a tool demo rather than a production case.

### 54.3.1 Filter out cases with functionality but no platform

Whether a case belongs in this book also depends on whether it reflects platform capability. If the material only shows a large model generating a result, while Runtime, Registry, Gateway, Memory, Eval, Trace, and Guardrails remain invisible, the material belongs in a blog post or product introduction rather than the main text.

During review, use a simple criterion: a case should include at least three platform capabilities, and each should have evidence. A knowledge assistant usually needs RAG, Memory, and Eval. A ticketing Agent usually needs Registry, Human-in-the-loop, and Guardrails. A DataAgent case usually needs a semantic layer, `sql_executor`, Trace, and evaluation samples.

### 54.3.2 Correspondence between case materials and engineering evidence

The first edition already includes a mini-platform and test cases. Later cases should prioritize scenarios that correspond to existing engineering paths instead of inventing an unverifiable system. A case does not need to include all code in the text, but it should state which type of material maps to which type of engineering evidence.

*Table 54-7: Minimal correspondence between case materials and mini-platform capabilities. Source: Compiled by this book.*

| Case material | Corresponding mini-platform capability | Text should explain |
| --- | --- | --- |
| Task status transitions | Runtime / Run status | How status progresses from input to completion or failure |
| Tool call records | Tool Registry / executor | Tool contract, permission, and failure response |
| Metric definitions and queries | semantic layer / sql_executor | Metric binding, SQL validation, and read-only restriction |
| Evidence citation | RAG / retrieval | Document version, cited snippet, and evidence coverage |
| Evaluation samples | eval / benchmark | Sample source, labeling, and failure classification |

## 54.4 Case material publication threshold

Later versions may use anonymized composite scenarios, but the text must clearly state that they are common engineering scenarios rather than real company stories. The main text must not include customer names, production data, internal domains, real tickets, real accounts, or unverified benefit figures. If a case needs to show interfaces, logs, or reports, use sanitized samples and cite the source in the figure or table caption.

The writing process should be separated into material registration, evidence review, text rewriting, and release review. During material registration, the author submits the task description, sanitized samples, system topology, risk boundaries, and evaluation material. Editors check completeness first rather than polishing incomplete material. During evidence review, reviewers check whether the material supports every conclusion in the text. Any statement about revenue, accuracy, latency, cost, or deployment scale needs a source. Unsupported content should be marked as an unverified hypothesis or removed. Only after those checks should the material enter formal case writing. The writing should preserve causal chains and failure boundaries, with minimal product language.

*Table 54-8: Case supplemental writing process and exit criteria. Source: Compiled by this book.*

| Stage | Input | Output | Exit criteria |
| --- | --- | --- | --- |
| Material registration | Task description, samples, topology, screenshots | Material list | Return if key links are missing |
| Evidence review | Material list, evaluation records | List of valid conclusions | Delete or downgrade unsupported conclusions |
| Text rewriting | Valid conclusions, chapter mapping | Case text | Pass tone, figure, table, and citation review |
| Release review | Text, images, data sources | Merged version | No sensitive information, no exaggerated benefits |

Editors should keep return comments during this process. A returned case usually means key evidence is missing, not that the writing failed. If tool-call records are missing, the text can only say that governed tool calls are required by design. It cannot claim that business systems have already been integrated safely. If evaluation samples are missing, the text can describe an evaluation plan, but it cannot say quality has reached a usable level. If human-confirmation records are missing, the text can state the confirmation requirement, but it cannot claim that risk actions are already controlled.

Figures and tables in later cases need the same evidence discipline. Flow diagrams, state machines, tool topologies, and evaluation tables should come from sanitized material or explainable synthetic examples. Captions should identify the source, and body text should refer to the figure or table number. If a diagram shows a generic pattern, "Source: Compiled by this book" is acceptable. If a diagram is redrawn from a real project after sanitization, the caption should say so. The first edition does not include specific case figures because there is not enough public business evidence, not because the case chapters do not need diagrams.

Later versions should start with a small number of cases that can be reviewed deeply. Three evidence-backed cases are more useful than ten complete-looking stories that cannot be replayed. The case chapters should show how enterprise Agent systems land across data, tools, permissions, evaluation, and organizational responsibility.

## Chapter Recap

This chapter keeps a case-writing framework without providing unverified business cases. Later cases should first let readers reconstruct the task, chain, evidence, and boundary, then use platform capabilities to explain how the work was done. Case writing should not wrap feature lists in stories, and it should not fill material gaps with fictional companies, screenshots, or benefit numbers. Sanitization must cover system names, data samples, logs, tool parameters, screenshot metadata, and personnel roles. Evaluation metrics must state sample origin, review criteria, and failure classes, and offline results should not be written as production benefits. Only when those materials are ready should a case enter the main text.

## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE.

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).

OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

Model Context Protocol. (n.d.). [Specification and documentation](https://modelcontextprotocol.io/).
