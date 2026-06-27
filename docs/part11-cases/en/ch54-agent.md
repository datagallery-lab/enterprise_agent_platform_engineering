# Chapter 54 Business case admission and writing method

---

Enterprise Agent cases are easy to turn into feature demos with outcome claims. A team builds a knowledge assistant that answers policy questions in a demo environment, and the case becomes "enterprise knowledge management efficiency improvement." A ticket Agent produces a fluent complaint summary, and the case becomes "customer service automation." A development Agent runs one code-change path in a repository, and the case becomes "developer productivity improvement." These statements look complete, but they do not survive review. Readers need to know where the task sits in the business process, which data and tools the system used, which actions were actually automated, where the system stopped for human confirmation, and whether failures can be replayed.

The difficult part of case writing is evidence, not dramatic storytelling. An offline experiment can show model behavior on one sample set, but it cannot prove that production permissions, audit, cost, and human takeover are ready. A screenshot can show the interaction shape, but it cannot prove that tool calls are governed. User feedback can show that a direction has value, but it cannot replace evaluation sets, Trace records, or review logs. If a case skips these limits, readers may assume that connecting a model and a knowledge base is enough to create trustworthy automation.

This chapter starts with case admission rules instead of company stories without evidence. An enterprise Agent case must meet a stricter evidence bar than an ordinary product case. It must explain what happened and why the reader should trust the evidence. Before material enters the public text, the material should describe the real task, provide evidence for data, tools, permissions, evaluation, and human confirmation, and connect the case back to the platform capabilities discussed earlier. If that evidence is missing, the material can remain in the candidate backlog, but cases without evidence, synthetic screenshots, or unsupported benefit numbers cannot be used to fill the gap.

Enterprise knowledge assistants, ticketing or customer service Agents, development Agents, and operations Agents can all demonstrate platform capability. They are also the easiest scenarios to flatten into generic feature stories. A knowledge assistant must prove evidence citation, permission filtering, and knowledge updates. A ticketing Agent must prove governed tool calls, human takeover, and content safety. A development Agent must prove code-tool permissions, long-running execution, and evaluation. An operations Agent must prove Trace, SLO, and change boundaries. Each direction can become a case only when the task, chain, evidence, and boundary can be reconstructed. This chapter sets that evidence line for later case writing, so readers can connect case material back to platform capabilities instead of reading it as promotional copy.

---

## 54.1 Case Inclusion Criteria

Before a case enters the public text, a straightforward question must be answered: can readers reconstruct how this was done from the material? If the material only says "used Agent to improve efficiency," "integrated a knowledge base," or "automatically generated a report," but omits task input, system boundary, failure handling, and evaluation evidence, it is still promotional material instead of a case.

A qualified case must meet at least four conditions. These conditions are not formatting rules. They correspond to the four places where enterprise Agent cases most often become disputed: unclear task definition, disconnected platform capability, missing chain evidence, and overstated effect. During review, the team should be able to answer why the system made a suggestion, whether unauthorized data entered the model, where an efficiency claim came from, and which record supports each statement. If those answers only exist orally, the material is not ready.

*Table 54-1: Four conditions and acceptance criteria for cases included in the public text. Source: Compiled by this book.*

| Condition | Acceptance criteria |
| --- | --- |
| Clear business task | Clearly specify user roles, inputs, outputs, decision actions, and risk boundaries |
| Corresponding platform capability | Map to Runtime, Tool Registry, MCP, Planner, Memory, RAG, Eval, Trace, or Guardrails |
| Clear data and tool topology | Describe involved systems, data objects, permissions, audits, and failure recovery actions |
| No exaggerated outcomes | Avoid reporting unsupported cost reduction, efficiency improvement, accuracy, or deployment scale |

These four conditions block four common problems: unclear task, detached capability, missing evidence, and exaggerated result. The material can be checked against Table 54-1, and the same standard should be used in review. If any condition cannot be confirmed, the material can enter the material repository, but it should not appear in the public text.

Admission review should also leave actionable return comments. When material is immature, the review should identify which part of the chain is missing: task input, tool-call record, permission topology, evaluation sample, or human-confirmation record. This helps the team fill the evidence gap. Otherwise, the team may only add more background narrative, making the text look fuller while leaving the evidence problem unchanged. Case chapter work means shifting the question from whether the story sounds convincing to whether the evidence connects.

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

Each part should survive evidence questioning. The business task should explain why users cannot solve it with a fixed process. Data and tools should explain which fields are read-only and which actions create side effects. Agent design should explain why planning is needed instead of a single answer. The execution chain should explain how Trace reconstructs what happened. Risk control should explain where the system stops. Evaluation should explain whether the sample and review criteria support the conclusion. If these questions cannot be answered, the case should not enter the public text.

### 54.2.1 Task-first narrative order

Weak cases often start like this: "This case uses RAG, Planner, Tool Registry, and Guardrails to build an intelligent customer service Agent." The sentence sounds complete, but it does not tell the reader why the system is needed. A better opening starts from task friction: customer service needs to handle refund disputes within minutes, while the order system, logistics system, and policy knowledge base sit in different systems; fixed workflows cover standard refunds, but they fail when promotions overlap, partial shipments occur, or a human promise has already been made.

Once the task is clear, platform capabilities have a place. RAG finds policies, Tool Registry constrains order queries and refund calculation, Human-in-the-loop handles exceptional refunds, and Trace preserves evidence. This order matches the reference book's style: show the problem first, then give the engineering structure.

### 54.2.2 Clearly specify the parts that are not automated

Agent cases often overstate automation. Mature enterprise cases clearly mark where the system stops. In sales quoting, the Agent can summarize information, generate drafts, and check discount policies, while customer commitments remain with sales. In legal review, the Agent can extract clauses and flag risks, while final legal opinions remain with legal owners. In finance analysis, the Agent can explain metric changes, while disclosure definitions remain with responsible staff. These boundaries are prerequisites for trustworthy production systems. When writing, separate actions that are automatically completed, require confirmation, must be rejected, or should degrade to a fallback path. Readers can then judge whether the case is feasible in production.

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

Table 54-6 prevents cases from drifting away from the body of the book. It does not require every case to cover every chapter. A ticketing Agent without structured output and human takeover cannot support the claims in Chapters 8 and 30. An operations Agent without Trace, SLO, and change boundaries is still a tool demo instead of a production case.

### 54.3.1 Filter out cases with functionality but no platform

Whether a case belongs in this book also depends on whether it reflects platform capability. If the material only shows a large model generating a result, while Runtime, Registry, Gateway, Memory, Eval, Trace, and Guardrails remain invisible, the material belongs in a blog post or product introduction instead of the public text.

During review, use a simple criterion: a case should include at least three platform capabilities, and each should have evidence. A knowledge assistant usually needs RAG, Memory, and Eval. A ticketing Agent usually needs Registry, Human-in-the-loop, and Guardrails. A DataAgent case usually needs a semantic layer, `sql_executor`, Trace, and evaluation samples.

### 54.3.2 Correspondence between case materials and engineering evidence

Case selection should prioritize scenarios that correspond to existing engineering paths instead of inventing an unverifiable system. A case does not need to include all code in the text, but it should state which type of material maps to which type of engineering evidence.

*Table 54-7: Minimal correspondence between case materials and mini-platform capabilities. Source: Compiled by this book.*

| Case material | Corresponding mini-platform capability | Text should explain |
| --- | --- | --- |
| Task status transitions | Runtime / Run status | How status progresses from input to completion or failure |
| Tool call records | Tool Registry / executor | Tool contract, permission, and failure response |
| Metric definitions and queries | semantic layer / sql_executor | Metric binding, SQL validation, and read-only restriction |
| Evidence citation | RAG / retrieval | Document version, cited snippet, and evidence coverage |
| Evaluation samples | eval / benchmark | Sample source, labeling, and failure classification |

## 54.4 Case material publication threshold

Prepared cases may use anonymized composite scenarios, but the text must clearly state that they are common engineering scenarios instead of real company stories. The public text must not include customer names, production data, internal domains, real tickets, real accounts, or unsupported benefit figures. If a case needs to show interfaces, logs, or reports, use sanitized samples and cite the source in the figure or table caption.

Case preparation should be separated into material registration, evidence review, text rewriting, and release review. During material registration, the team submits the task description, sanitized samples, system topology, risk boundaries, and evaluation material. Completeness is checked first instead of polishing incomplete material. During evidence review, each conclusion is checked against whether the material supports every conclusion in the text. Any statement about revenue, accuracy, latency, cost, or deployment scale needs a source. Unsupported content should be marked as a hypothesis that still needs evidence or removed. Only after those checks should the material enter public case writing. The writing should preserve causal chains and failure boundaries, with minimal product language.

*Table 54-8: Case supplemental writing process and exit criteria. Source: Compiled by this book.*

| Stage | Input | Output | Exit criteria |
| --- | --- | --- | --- |
| Material registration | Task description, samples, topology, screenshots | Material list | Return if key links are missing |
| Evidence review | Material list, evaluation records | List of valid conclusions | Delete or downgrade unsupported conclusions |
| Text rewriting | Valid conclusions, chapter mapping | Case text | Pass tone, figure, table, and citation review |
| Release review | Text, images, data sources | Merged version | No sensitive information, no exaggerated benefits |

Editors should keep return comments during this process. A returned case usually means key evidence is missing, not that the writing failed. If tool-call records are missing, the text can only say that governed tool calls are required by design. It cannot claim that business systems have already been integrated safely. If evaluation samples are missing, the text can describe an evaluation plan, but it cannot say quality has reached a usable level. If human-confirmation records are missing, the text can state the confirmation requirement, but it cannot claim that risk actions are already controlled.

Figures and tables in current and future cases need the same evidence discipline. Flow diagrams, state machines, tool topologies, and evaluation tables should come from sanitized material or explainable synthetic examples. Captions should identify the source, and body text should refer to the figure or table number. If a diagram shows a generic pattern, "Source: Compiled by this book" is acceptable. If a diagram is redrawn from a real project after sanitization, the caption should say so. Specific case figures should appear only when public business evidence is strong enough; the case chapters still need diagrams when evidence supports them.

Public cases should start with a small number of scenarios that can be reviewed deeply. Three evidence-backed cases are more useful than ten complete-looking stories that cannot be replayed. The case chapters should show how enterprise Agent systems land across data, tools, permissions, evaluation, and organizational responsibility.

## 54.5 Minimal Case Package

Before writing a business case, teams should prepare a minimal case package. The package does not have to look polished. Its purpose is to decide whether the case can be reviewed. It should contain at least six materials: sanitized task description, input samples, tool and data boundaries, execution chain, risk handling, and evaluation or review evidence. The task description explains who faced which problem in which workflow. Input samples show the complexity the system actually handled. Tool and data boundaries show what the system read, which tools it invoked, and which actions created side effects. The execution chain shows how the task moved from start to completion, refusal, or human handoff. Risk handling shows where the system stopped. Evaluation or review evidence explains why the team can claim the solution is usable.

The package should keep failure material. Many cases submit only the success path. They read smoothly but say little about platform boundaries. Enterprise Agent value often appears in failure paths: whether the system refuses when permission is missing, downgrades when retrieval evidence is weak, keeps Trace when SQL times out, reassigns when approval times out, and asks for human confirmation when tool outputs conflict. Without failure samples, the text can describe design intent, but it cannot claim production experience. Authors should provide at least one successful chain, one refusal chain, and one downgrade or human-handoff chain.

The package should distinguish real material from synthetic material. Sanitized real material can support the statement that this task chain appeared in an actual workflow. Synthetic material can support an explainable pattern, but it cannot support claims about deployment scale, business benefit, or stability. Both can be useful, but the strength of the conclusion differs. During review, claims should trace each claim back to its source: real Trace, sanitized sample, offline evaluation, expert review, or a general pattern summarized from engineering experience. Different sources require different wording.

The package can stay lightweight. A folder, a few sanitized JSON files, two flow diagrams, one Trace export, a small evaluation sample set, and a review note are enough to judge the material. The important property is traceability, not presentation. If the material abstracts common patterns from several real projects, the text should call it a composite scenario or general pattern so readers do not mistake it for a complete production story from one company.

## 54.6 Public-Version Writing Boundary

Public writing should separate what the material proves from what the text infers. Proven material includes task chain, tool calls, state transitions, approval records, evidence references, sample review, and failure classes. Inferred material includes future extension direction, possible organizational benefit, and platform capabilities that may be consolidated later. The first group can be written as case facts. The second should be written as analysis or recommendation. Revenue, efficiency, cost, or deployment-scale claims need sources; otherwise they should be removed.

This boundary also affects titles and summaries. A case title should avoid claiming a full industry success practice unless the material supports production launch and replayable benefit. More accurate titles name the task type or engineering boundary, such as "Evidence-chain organization in business analysis tasks," "Tool permission and human handoff in ticketing Agents," or "Approval boundary in sales quotation scenarios." Such titles reduce promotional tone and tell readers that the chapter explains an engineering problem.

Public cases also need the right level of detail. If the text is too abstract, readers see only a generic process. If it is too detailed, it may leak system structure, business rules, or customer information. A useful level preserves relationships among input, tools, state, evidence, and responsibility while replacing real system names, field names, accounts, timestamps, and business identities. The text can say that an order-query tool returned three state classes without showing the real API path. It can say that the approver role was finance controller without showing the person's name or organization hierarchy. It can say that a report referenced a semantic-layer metric version without exposing an internal metric table name.

When material is thin, the public version should downgrade explicitly. Missing Trace turns the text into a design method or pending-evidence note. Missing evaluation turns it into a chain example. Missing public screenshots calls for redrawn diagrams. Missing benefit evidence removes benefit claims. Downgrading keeps evidence and conclusion aligned. Readers trust a bounded case more than a complete-looking success story that cannot be replayed.

## 54.7 Author Self-Review Questions

Before a case enters review, teams can check it with a short set of questions. Can the case explain the business task in one sentence before naming technologies? Can readers see the causal relationship among user input, system decomposition, tool calls, human confirmation, and final delivery? Does every conclusion map to Trace, samples, human review, or public documentation? Are automation boundaries clear: which actions the system completes, which require confirmation, and which must be refused? Does the material include failure samples, or does it only show the smooth path?

Authors should also check whether the case supports the platform mainline of this book. A case that only says the model answered well, while Runtime, Registry, Policy, Trace, Eval, Memory, semantic layer, and HITL remain invisible, does not belong in the main body. It may work as a product article, but it does not support enterprise Agent platform engineering. By contrast, a small business scenario can belong in the book if it shows task state, tool governance, evidence references, human boundaries, and evaluation review.

Finally, the language should be reviewed. Case writing should avoid promotional phrases such as "successfully built," "comprehensively improved," or "deeply integrated." A stronger version states conditions, actions, evidence, and limits: under which input, which capability was invoked, which evidence was retained, where the system stopped, and how the result was judged. The credibility of a case chapter comes from these details, not from adjectives.

## 54.8 Review Output and Text Revision

After case review, the output should not be only "approved" or "rejected." A useful output is an executable evidence note: which materials can be written as facts, which can only be written as method, which sentences need downgrade, which diagrams need redrawing, and which risk boundaries need more evidence. If Trace is complete but evaluation samples are thin, the text can describe the execution chain but should not claim quality. If tool-call records are complete but approval records are missing, the text can describe governed tool invocation but should not claim full control over high-risk actions. If sanitized screenshots are available but data source is unclear, the diagram can stay while metric explanations should be removed or marked as pending evidence.

Review output should also mark write-back points to the main chapters. If case material repeatedly exposes issues in tool permission, approval recovery, metric definition, evidence citation, or cost control, those issues should be brought those issues back to Chapters 23, 30, 33, 36, 41, and related chapters. Cases then become more than end-of-book supplements; they help strengthen the main body. Even when complete public cases are not available, the review rules can still inspect earlier chapters: whether each engineering module produces the evidence a case needs, and whether each launch judgment can be supported by Trace, Eval, HITL, or release ledgers.

Revision should preserve the limits found during review. Many cases become more restrained after review: benefit claims are removed, automation scope narrows, failure paths are added, and screenshots become sanitized redraws. This does not weaken the case. It moves the text from promotional copy back to engineering prose. Readers need transferable judgment: how to prepare material, how to identify evidence gaps, how to downgrade expression, and how to turn a single experience into platform capability. If those judgments are clear, a case can serve the book even without customer names or attractive numbers.

Chapter rhythm matters as well. A case-method chapter should not be filled with tables and checklists. Tables are useful for material types, review states, and process steps. Judgment logic, evidence boundaries, and writing trade-offs work better as prose. When extending this chapter, new material should first explain why a writing rule exists, how to handle weak evidence, and how a case changes platform design. Adding more checklists should be the last choice. This makes Chapter 54 an executable writing method instead of a collection of rules.

The method also serves collaboration. Business, platform, data, security, and compliance teams read the same minimal case package through different lenses. Business teams judge whether the task is real. Platform teams judge whether state and tools can be replayed. Data teams judge whether definitions and permissions are clear. Security and compliance teams judge whether evidence and sanitization are sufficient. Chapter 54 should let these roles apply the same standard to the same material. If everyone adds content only from personal experience, the case becomes a patchwork of perspectives. If review questions and evidence rules are shared, the case can form one coherent narrative.

Case writing therefore does not have to wait until every material item is perfect. Teams can first use the minimal case package to judge material strength, then decide whether the case becomes a formal case, method example, chain example, or deferred material. This process tells teams where the gap is and tells readers what evidence standard the book applies. Case chapter quality comes from this judgment, not from the number of cases.

Later editions should keep the same order: material package first, review conclusion second, prose expansion last. With that order, enthusiasm for storytelling does not outrun evidence. The English edition should follow the same boundary: settle material source, sanitization scope, and claim strength first, then rewrite the narrative. Clear evidence order makes the text more stable and easier to review.

## 54.9 How Case Method Constrains The Main Text

The case method chapter should do more than guide later case writing. It should also constrain how earlier chapters are written. When a chapter introduces a platform capability, it should be able to state what evidence that capability leaves in a case package. Runtime leaves states and events. Registry leaves tool versions and execution results. The semantic layer leaves metric versions and query definitions. Trace leaves execution paths. Eval leaves samples and failure classes. HITL leaves approval responsibility and recovery records. If the text explains a design principle but cannot say how a case would verify it, that passage is still conceptual.

This constraint helps teams decide where expansion is useful. Expansion should not simply add more explanation around a concept. It should answer the questions readers will ask in a real project: what evidence is checked before launch, who owns the failure path, how to downgrade when material is thin, and which claims cannot be written as facts. Chapter 54 can therefore serve as a writing verifier for the whole book. Whenever new content is added, the team can ask: if a future case had to prove this paragraph, what would the minimal case package need to contain? If the answer is unclear, the engineering anchor of the paragraph is still weak.

The method also affects figure and table use. A writing boundary that can be explained in prose should not become a table by default. Tables are useful when comparing material states, review phases, and exit criteria. Judgment logic, evidence boundaries, and downgrade decisions often read better as prose. This keeps the case chapter from feeling like a stack of review forms. When complete public cases are not available, the method chapter needs this restraint even more. It sets admission standards, downgrade paths, and review workflow so current and future cases can enter the book without lowering the evidence bar.

## 54.10 Case Admission And Protection Of Real Material

Case admission should protect real material. Enterprise cases often contain customer names, business processes, metric definitions, internal screenshots, cost data, and failure records. Masked chains and abstract tasks can be used, but it should not fill missing material with company stories without evidence. A steadier approach is to describe task type, platform capability, evidence structure, and risk boundary while masking enterprise identity, amounts, and sensitive process details.

Protection of real material also affects diagrams and screenshots. If a screenshot cannot be published, a simulated image should not pretend to be the real system. The case can use architecture diagrams, process diagrams, or field sketches and state that the figure is self-drawn. If metric results cannot be disclosed, the text should explain definitions and validation method instead of unauthorized benefit numbers. If a failure case involves security or customer risk, the text should describe failure class and repair action without publishing reusable attack details.

The goal of case admission is to make the method reusable, not to make a result sound impressive. A qualified case should explain user task, Agent decomposition, platform capability calls, evidence retention, human nodes, failure recovery, and later review. When material is insufficient, it is better to write a method sample or mark the case as pending than to complete the story artificially.

## 54.11 Interview and review process for case material

Case material is best collected through interviews and review. Authors can interview business owners, platform engineers, data owners, and security or compliance owners to confirm business goals, platform changes, data evidence, and risk boundaries. Interview notes should not go straight into the chapter. They should become a reviewable material pack: task chain, launch evidence, failure samples, review conclusions, and public scope.

The review process should protect real projects. The project team confirms technical facts. The business owner confirms scenario description. Security and compliance owners confirm sanitization scope. The team then decides what enters the public text. This keeps the case from becoming marketing copy and prevents it from becoming empty because sensitive details were removed. Even if a case is incomplete, the material structure can remain until real detail is available.

## 54.12 Downgraded writing when material is incomplete

When case material is incomplete, the text should downgrade the claim instead of completing the story. Material without Trace can become task-chain design or a pending-review chain, with a clear note about which states and events the system should retain. Material without evaluation samples can become an evaluation plan or sample-construction method; it cannot claim that quality is production-ready. Material without publishable screenshots can use redrawn process diagrams, but captions should say they are self-drawn. Material without benefit data should remove benefit claims and state what evidence would be needed, such as manual handling time, review pass rate, and rework rate. This makes the case more restrained, but it protects the credibility of the text.

Downgraded writing should still preserve reusable engineering judgment. A customer-service Agent with tool-interface design but no real ticket Trace can still discuss tool allowlists, idempotency keys, error codes, and human handoff. It should not claim stable handling of customer-service requests. A DataAgent example with a semantic-layer sample and SQL executor, but no business review record, can explain metric binding and read-only validation. It should not claim that the business accepted the operating analysis. Evidence strength determines claim strength, and the text should make that relationship visible in the prose.

Downgrade should also avoid empty template language. Readers do not need a vague sentence saying that material can be improved later. They need to know which evidence should be added next. Missing tool-call records call for Registry invocation logs and execution results. Missing approval records call for approver role, approval basis, timeout handling, and recovery state. Missing evaluation samples call for sample source, labeling rule, failure classes, and review owner. Missing sanitized diagrams call for redrawn figures and source notes. Each gap should map to a concrete evidence action.

This approach also prepares Chapter 55. Chapter 54 defines the downgrade principle, and Chapter 55 can turn review comments into publication decisions: enter the public text as a formal case, stay as a method example, remain pending, or be removed. The book can include fewer cases, but it should not lower the evidence bar. When more real material becomes available, the team can upgrade downgraded sections into case facts. The case part of the book then grows with evidence instead of being filled by unsupported completeness.

## 54.13 Completeness review for case admission material

When completeness review for case admission material reaches production, the platform needs a shared evidence standard for business goal, original samples, system boundary, data source, human review, failure samples, launch evidence, and publishable scope. This standard is not paperwork for its own sake. It lets business, platform, data, security, and operations teams discuss the same facts. Without this material, incident review depends on memory and personal judgment. With it, the team can see which inputs were valid, which actions executed, which artifacts can still be used, and which results need correction or withdrawal.

This evidence should connect to Chapter 32 on the DataAgent mainline, Chapter 50 on security, and Chapter 53 on organizational governance. The upstream chapters provide the capability base, downstream chapters consume the runtime result, and this chapter explains how the middle layer is verified. If a capability looks complete inside one chapter but cannot enter Trace, Eval, release records, or the compliance evidence package, the production system still has a break in the chain. Readers should treat cross-chapter interfaces as engineering contracts, not as a reading order.

Common risks include material coming only from interviews, missing failure samples, business outcome that cannot be mapped to platform capability, and sensitive details that cannot be published. A successful demo rarely exposes these problems because demo samples are usually clean, short, and direct. Real business traffic brings stale data, abnormal input, permission changes, user withdrawal, budget limits, and long-running state. If the platform does not turn those situations into samples and ledgers, later scenarios will hit the same class of issues again.

Material coming only from interviews should be turned into a tracked review item when it appears repeatedly. The operating record should at least state owner, version, sample, affected scope, action, and review time. It does not need to become a long process report, but it must be clear enough for a later maintainer to understand the decision. For high-risk capability, the record should also state which conditions allow wider use and which failures require degradation or withdrawal.

A first version can build this habit in a few representative scenarios. It is better to make high-traffic, high-risk, externally visible paths solid first, then copy the sample, ledger, and review method to related capabilities in other chapters. This makes the chapter read like engineering guidance: it explains how the capability is integrated, validated, operated, and retired.

## 54.14 Case downgrade when material is incomplete

The case-admission chapter should explain how to downgrade a case when the material is incomplete. Many enterprise cases are not unusable; they simply do not have enough evidence for a full narrative. Interviews can explain demand, but they do not prove platform capability. Screenshots can show interaction shape, but they do not prove runtime quality. Business outcome can show value, but it may not show which part of the result came from the Agent. In this situation, the book should not force the material into a full case. It should downgrade the material into a problem fragment, method note, or boundary reminder, stating what is proven and what still needs evidence.

A downgraded case can still have engineering value. User questions and human edits can become a section on evaluation samples. An incident review can become a section on platform gaps. Tool integration material can become a section on tool contracts and approval boundaries. This is more reliable than inventing a complete business story, and it is closer to a technical book style: method first, engineering judgment next. Readers get a reusable reasoning path instead of a story they cannot verify.

A first version can assign each candidate case a status: full chapter, fragment, pending evidence, or not publishable. Status changes should record missing material, owner, next review time, and publication constraints. This keeps the case chapters useful even when the source material is uneven.

## 54.15 Evidence levels for case material

Case material can be managed by evidence level. The strongest level is replayable operating evidence: Trace, evaluation samples, release records, and incident reviews. The second level is checkable business material: original requirements, user feedback, human edits, and acceptance conclusions. The third level is interview or verbal explanation, which should mainly provide background. Different levels can be used together, but the text should make clear which claims are supported by operating evidence and which are scenario context.

Evidence levels keep case writing from drifting. If only interviews exist, the text should not claim that platform effect has been verified. If only business outcome exists, the text should not attribute the whole result to the Agent. If only screenshots exist, the text should not infer mature backend governance. Teams can track evidence level for each case paragraph. The final text does not need to show the marks, but the team knows which sentences can be stated firmly and which should stay conservative.

## 54.16 Preserving readability after case anonymization

A case should remain readable after anonymization. Company names, department names, exact metrics, and internal systems can be replaced, but the task chain, responsibility boundary, evidence type, and failure handling should remain as clear as possible. If anonymization leaves only abstract nouns, readers cannot tell why the case works or how to transfer the lesson to their own platform.

Readability can be preserved through structure: state the user task, describe which platform capabilities the Agent used, explain the risk and repair action, and then state which evidence supports the conclusion. Business details can be blurred; the engineering chain should stay visible. A first version can check each anonymized case for task context, platform action, failure sample, and reason for redaction. The case can then meet publication constraints while still explaining engineering practice.

Anonymization should also preserve sequence. Readers need to know where the problem appeared, which platform actions followed, where human review entered, and how the final artifact was published or withdrawn. Exact dates can be hidden, but stages such as pilot, canary, production, and review should remain visible.

Review should also check whether anonymization changes responsibility. Names and departments can be hidden, but the distinction between business owner, platform owner, and data owner should remain. For approval, incident, or retirement cases, the text should still show who raised the issue, who approved the change, and who owns later maintenance. If public material cannot preserve that role structure, the material is better used as a method fragment than as a full case. When needed, split the case into business background and platform engineering action so readers can see reusable judgment. Redaction should support credibility without weakening readability or context, and it should leave room for later evidence.

## Chapter Recap

This chapter keeps a case-writing framework without providing business cases without evidence. Cases should first let readers reconstruct the task, chain, evidence, and boundary, then use platform capabilities to explain how the work was done. Case writing should not wrap feature lists in stories, and it should not fill material gaps with company stories, screenshots, or benefit numbers. Sanitization must cover system names, data samples, logs, tool parameters, screenshot metadata, and personnel roles. Evaluation metrics must state sample origin, review criteria, and failure classes, and offline results should not be written as production benefits. Only when those materials are ready should a case enter the public text.

## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE.

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).

OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

Model Context Protocol. (n.d.). [Specification and documentation](https://modelcontextprotocol.io/).
