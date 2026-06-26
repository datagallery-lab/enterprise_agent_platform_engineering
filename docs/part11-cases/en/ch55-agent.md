# Chapter 55 Case Review and Platform Integration

---

After a case is written, it still cannot go straight into the formal version. Enterprise Agent cases involve tool permissions, business definitions, human confirmation, and audit evidence. If one boundary is written incorrectly, readers may misunderstand what the system can automate. A sales Agent may look like it only produces a quotation draft, but it touches discount approval, inventory commitment, and contract responsibility. A finance Agent may look like it only explains metric movement, but it touches metric versions, abnormal vouchers, and formal disclosure. A legal Agent may look like it only extracts clauses, but it touches legal judgment, responsibility statements, and signing advice. If case writing only shows that "the system can produce a result," it compresses all of these responsibilities into a feature demo.

The first review task is to check whether the evidence supports the conclusion. A case can say that the system generated a quotation draft, but it must state which data the draft used, where discount rules came from, and which actions stopped before approval. A case can say that the system assisted financial analysis, but it must state metric definitions, anomaly localization, and review records. A case can say that the system helped with contract review, but it must state clause evidence, risk labels, and final signing responsibility. Without these materials, the draft cannot hide behind a vague phrase such as "manual confirmation is retained," because readers still do not know where confirmation happened or who was responsible after failure.

The second review task is to bring the case back to platform capability. Sales, finance, and legal cases look like different businesses, but they often reuse the same capabilities underneath: Runtime manages execution state, Registry governs tools, the semantic layer governs definitions, Guardrails and approval chains govern risk, and Trace supports review after the fact. If a case only proves that one application performs one function, without showing how these platform capabilities work together, it is not yet a formal case for this book. It can be product material or an internal retrospective, but it does not prove the design of an enterprise-grade AI-native business system.

Cases also expose gaps in the main chapters. If several cases get stuck on approval timeout, Chapter 30 needs stronger recovery strategy. If several DataAgent cases get stuck on metric definitions, Chapters 33 and 34 need stronger version and compilation contracts. If several ticketing cases cannot explain failure reasons, Chapter 38 Trace and Chapter 39 evaluation samples are still insufficient. Cases are not decoration at the end of the book. They are material for checking whether the earlier architecture can survive real workflows.

The Chinese first edition does not fabricate company stories, go-live data, or benefit conclusions. This chapter gives the review method and platform integration method: first review evidence, then review risk boundaries, then extract reusable platform capabilities from single scenarios. After reading it, readers should be able to judge whether a candidate case can be published, what form it should be downgraded to when evidence is thin, and which main chapters should absorb the problems exposed by review.

---

## 55.1 Common Boundaries in Sales, Finance, and Legal Scenarios

Sales, finance, and legal scenarios usually carry more risk than ordinary knowledge Q&A because they affect quotation, settlement, compliance judgment, or contract responsibility. Case writing must first state the task boundary. The phrase "manual confirmation is retained" is not enough. The text must state where the system stops, who takes over, what is confirmed, and how the confirmation result returns to the system.

During review, the easiest problems often sit in the verbs. If the author writes "generate a quotation," readers may understand it as a formal external quotation. If the author writes "complete financial analysis," readers may understand it as a publishable conclusion. If the author writes "review a contract," readers may understand it as a legal judgment. A safer draft splits the action: the system generates a draft, lists evidence, flags risk, submits approval, waits for confirmation, and records the result. Each verb maps to a system state or a human responsibility, which makes the case boundary much clearer.

*Table 55-1: Boundaries between automated and manual-confirmation parts in sales, finance, and legal scenarios. Source: Compiled by this book.*

| Scenario | Parts that can be automated | Parts requiring mandatory human confirmation |
| --- | --- | --- |
| Sales Agent | Summarize customer background, retrieve past quotes, generate quote drafts | Formal quotes, discount exceptions, customer commitments |
| Finance Agent | Explain metric changes, generate checklists, identify anomalous vouchers | Financial conclusion confirmation, definition changes, formal disclosure |
| Legal Agent | Extract clauses, identify risks, generate review draft comments | Legal judgment, contract signing advice, liability commitments |

These three scenarios share one trait: the system helps people approach judgment faster, while people and organizations still carry responsibility. Reviewers should watch for two expressions in particular: treating "draft generation" as "completing the business action," and treating "assisted judgment" as "automatic decision-making." Both push the Agent boundary too far. Stating the boundary clearly does not weaken the case. It makes the system more credible, because production systems must know which actions can run automatically, which actions must wait, and which actions should be refused.

### 55.1.1 Boundaries Must Be Reflected in States and Actions

Simply writing "manual confirmation required" is still too abstract. Reviewers should ask: in which state does confirmation occur, what material does the system provide to the person, what does the system do after confirmation, and how does the system handle rejection or timeout?

For sales quoting, a reliable state design is: the Agent first generates a quote draft and risk note; if the discount stays below the regular threshold, the system records the draft; if the discount exceeds the threshold, the Run state enters `waiting_approval`; after manager approval, the system may generate the formal quotation email. This state transition should be visible in Trace rather than existing only in a design document.

*Table 55-2: State boundaries in high-risk business cases. Source: Compiled by this book.*

| State | System action | Human action | Review focus |
| --- | --- | --- | --- |
| draft_ready | Generate draft, list evidence and risks | Read and revise | Whether the draft clearly marks that it is not yet effective |
| waiting_approval | Pause high-risk actions, send approval request | Confirm, reject, or request supplements | Whether the approver has authority |
| approved | Continue executing approved actions | Take responsibility for business confirmation | Whether executed actions match approval |
| rejected | Stop execution and record reason | Provide rejection reason | Whether the system can bypass rejection |
| escalated | Escalate to human or work order | Take over the task | Whether context is transferred completely |

### 55.1.2 Review Must Distinguish "Capability Demonstration" from "Case Publication"

Just because a demo runs successfully does not mean the case can be published. A demo usually proves only that the system can produce a result under ideal input. A case must describe how it handles boundary input, insufficient permission, missing evidence, and tool failure. The reference book's practical projects work because project, code, and smoke tests support one another. This book's first edition does not yet provide practical projects, so case review has to state the evidence requirement more explicitly.

A formal case should answer at least three follow-up questions. First, when the user provides incomplete input, how does the system clarify or degrade? Second, when a tool returns an error or permission is insufficient, how do the frontend and Trace record it? Third, when human review finds the result unreliable, how does the system preserve feedback and enter the next evaluation round? Demo videos rarely show these paths, but production cases must show or explain them.

*Table 55-3: Differences between demos, internal retrospectives, and formal cases. Source: Compiled by this book.*

| Material type | What can be shown | Limitations | Suitable for main text |
| --- | --- | --- | --- |
| Functional demo | Ideal path and UI interaction | Lacks failure samples, permission evidence, and evaluation | Not suitable alone |
| Internal retrospective | Real problem, failure reason, fix action | May contain sensitive information | Can become material after sanitization |
| Offline evaluation | Sample quality and model boundary | Does not represent production gains | Can support quality conclusions |
| Formal case | Task chain, evidence, risk, evaluation | Requires review overhead | Suitable for main text |

## 55.2 Platform integration writing method

Cases should describe an Agent's function and also explain how platform capabilities are accumulated. If a sales Agent, a finance Agent, and a legal Agent each implement tool permissions, approvals, Trace, and evaluation from scratch, the result is repeated construction rather than a platform. Platform integration extracts common capabilities from cases and writes them back into earlier platform chapters.

When cases are added later, each one should separate the business application from the shared platform. The business application handles scenario rules, user interface, and task context. The shared platform handles run state, tool registration, approval insertion, audit records, evaluation samples, and cost control. Tool calls also need a clear split: which tools are registered in the Tool Registry, which calls require approval or audit, and which calls are read-only. Context sources should be separated as well: RAG provides textual evidence, Memory preserves session and preference context, and the semantic layer or master data system provides authoritative business objects such as metrics, customers, contracts, and orders.

Result delivery needs the same layering. Low-risk summaries can return directly to users. High-risk quotations, financial conclusions, and legal opinions can only be drafts or suggestions until a responsible person confirms them. Evaluation should cover quality, cost, latency, review burden, and business value. Written this way, a case shows which responsibilities belong to business rules and which belong to platform mechanisms, instead of putting everything into an "Agent completed it automatically" sentence.

Platform integration has one hard part: preserve business difference while avoiding duplicated foundation work. Sales quoting and financial analysis use different rules, but both require tool permission, definition versioning, approval state, and Trace evidence. Customer service tickets and operations alerts involve different objects, but both require a task state machine, failure recovery, and human takeover. Case writing should separate business rules, maintained by the business team, from platform mechanisms, maintained by the platform.

This writing method also helps readers judge investment priority. If three cases all need approval chains, Chapter 30's human-in-the-loop capability should come first. If several cases hit metric-definition conflicts, Chapters 33 and 34 need stronger semantic-layer and NL2SQL governance. If several cases cannot explain why they failed, Chapters 38 and 39 need more Trace and evaluation evidence. A case is not an appendix after the main text. It tests whether the earlier architecture is complete.

### 55.2.1 Extract shared capabilities from single-point cases

Platform integration does not erase business differences. It keeps the differences in business applications while identifying reusable operating mechanisms. Discount approval in sales, definition confirmation in finance, and responsibility opinion signing in legal look different on the surface, but all can be treated as human confirmation before high-risk actions. This capability should be consolidated into Runtime and Human-in-the-loop instead of being reimplemented by every application.

*Table 55-4: Extracting shared platform capabilities from single-point cases. Source: Compiled by this book.*

| Single-point phenomenon | Extractable platform capability | Corresponding chapters |
| --- | --- | --- |
| Discounts over threshold require approval | Run state machine, approval nodes, timeout handling | Chapters 22, 30 |
| SQL queries may overload the database | sql_executor resource limits, read-only policies | Chapters 34, 42 |
| Answers must cite policy texts | RAG evidence coverage, citation validation | Chapters 20, 40 |
| Tool parameters may exceed permissions | Tool Registry, policy engine | Chapters 23, 51 |
| Multiple roles participate in one task | Multi-Agent task division and handoff protocol | Chapters 28, 30 |

### 55.2.2 Platform integration ownership

Once shared capabilities are consolidated, someone must own them. During case review, ownership should be checked: the business team explains rules, the platform team owns runtime and tool governance, the security team owns policy and audit, and the data team owns definitions and lineage. If the text only says "the platform handles it uniformly" without explaining who maintains rules, approves exceptions, or handles incidents, readers may assume the platform is an abstract layer with no organizational cost.

*Table 55-5: Responsibility attribution for platform capabilities. Source: Compiled by this book.*

| Capability | Primary responsible party | Questions to ask during review |
| --- | --- | --- |
| Tool registration and permissions | Platform team, security team | Who approves tool launch? Who handles unauthorized calls? |
| Metric definitions and semantic layer | Data team, business owner | How are metric changes communicated to Agents? |
| Approval workflows | Business owner, platform team | How are absent or rejecting approvers handled? |
| Evaluation samples | Business team, evaluation team | Do samples cover failure and boundary scenarios? |
| Trace and audit | Platform team, compliance team | How long is evidence retained? Who can access it? |

Ownership also needs to be written into the change process. When business rules change, who notifies the Agent? When a semantic-layer field is removed, who triggers evaluation regression? When a tool API changes parameters, who updates the Tool Registry? When the approver organization changes, who maintains the approval chain? If these questions are missing, the case silently assumes that the platform knows everything. In practice, the platform can only execute declared and maintained rules. It cannot absorb all organizational change by itself.

Case review should therefore check both operating responsibility and maintenance responsibility. Operating responsibility answers who handles online incidents. Maintenance responsibility answers who updates rules when they change. If a finance Agent depends on business metrics, the data team and business owner must be responsible for metric versions. The platform team can only ensure that the selected version is referenced and recorded correctly after it enters Runtime.

## 55.3 Relationship to the Main Chapters of the First Edition

Case integration cannot drift away from the main chapters. A single Agent that enters unified run state should return to Chapter 22. Tool and permission governance should return to Chapters 23 and 24. Multi-role task division, handoff, and waiting should return to Chapters 28 and 30. Data issues in trusted analytics should return to Part III and Part VI. Quality, cost, SLO, and evaluation should return to Part VII. Security, compliance, and organizational mechanisms should return to Part X.

During case review, the main chapters are more than "further reading." They are the basis for checking whether a case holds up. A DataAgent case without a semantic layer can hardly support trusted analytics. A customer-service Agent case without human takeover can hardly handle long-running or high-risk scenarios. A development Agent case without tool-permission isolation cannot be summarized as "improving developer productivity."

### 55.3.1 Revising the Main Chapters in Reverse

Good cases cite earlier content and expose gaps in it. When several cases require a capability that the main chapters do not explain well enough, those chapters need to be supplemented. If later cases repeatedly ask what happens when approval times out, Chapter 30 should cover long-task waiting and recovery. If several DataAgent cases encounter metric-definition changes that cause incorrect explanations, Chapters 33 and 34 should cover definition versioning and SQL compilation cache invalidation.

*Table 55-6: Trigger conditions for cases prompting reverse revisions to main chapters. Source: Compiled by this book.*

| Recurring problem in cases | Chapter to supplement | Supplement direction |
| --- | --- | --- |
| Approval waiting, timeout, recovery | Chapters 22, 30 | Run state and human takeover mechanism |
| Tool parameter privilege escalation | Chapters 23, 51 | Tool schema, policy, and audit |
| Metric-definition conflicts | Chapters 33, 34 | Semantic-layer versioning and SQL compilation contracts |
| Insufficient evidence citation | Chapters 20, 40 | RAG evaluation and citation verification |
| Uncontrolled cost | Chapters 41, 45 | Cache, gateway rate limiting, and budget |

### 55.3.2 Case Indexes Should Serve the Reader's Path

As cases grow, indexes should not be organized only by business type. Readers may want to find how approvals are handled, how tool permissions are managed, or how DataAgent evaluations are conducted. They may also look for sales, finance, or legal scenarios. The case index therefore needs at least two entry points: business scenario and platform capability. The first edition can keep this indexing method in Part XI and later expose it in navigation after formal cases are ready.

## 55.4 Case review materials

When adding new case studies later, the following materials should be prepared together:

- Sanitized business task description.
- Data object, tool, and permission topology.
- Run state machine or sequence diagram.
- Human confirmation and refusal boundaries.
- Evaluation samples and acceptance criteria.
- Failure modes and rollback actions.

Without these materials, the case can remain in a future backlog, but it should not enter the formal main text. Fabricated companies, benefits, or screenshots only make a case look complete while weakening the evidence standard of the whole book.

The supplement list should support decisions rather than create documentation burden. A sanitized task description helps reviewers judge whether the scenario is real. Data, tool, and permission topology helps reviewers judge the system boundary. A Run state machine helps reviewers replay the task. Human confirmation and refusal boundaries help reviewers judge whether risk is controlled. Evaluation samples and acceptance criteria help reviewers judge whether conclusions are trustworthy. Failure modes and rollback actions help reviewers judge whether the case is close to production. Each item maps to a judgment point in the text, and missing material should lower the strength of the conclusion.

Authors can start with a minimal case package. It does not need to be a full project report, but it should contain a sanitized task, an explainable execution chain, a tool and permission description, a set of evaluation or review samples, and one failure-handling record. After the minimal case package passes review, the team can decide whether to expand it into a full chapter.

### 55.4.1 Supplement Priority

Later cases should not be expanded evenly. Priority should go to scenarios that cover the book's main line and can reuse the mini-platform. The first batch should start with DataAgent trusted analysis, which connects semantic layer, NL2SQL, Trace, and evaluation, and ticketing or customer service Agent, which connects structured output, tool invocation, human takeover, and Guardrails. Sales, operations, and legal cases can come later after evidence material is stronger.

*Table 55-7: Priority for supplementing subsequent cases. Source: Compiled by this book.*

| Priority | Case direction | Why priority | Materials to prepare |
| --- | --- | --- | --- |
| First batch | DataAgent business analysis | Covers Part III, Part VI, Part VII | Semantic-layer samples, SQL execution logs, evaluation sets |
| First batch | Ticketing or customer service Agent | Covers tool invocation, human takeover, security boundary | Ticket samples, tool contracts, takeover records |
| Second batch | Sales quotation Agent | High business value, but approval and responsibility boundaries are sensitive | Quotation rules, discount approval, sanitization flow |
| Second batch | Operations Agent | Shows Trace, SLO, and GitOps boundaries | Alert samples, change process, rollback records |
| Deferred | Legal review Agent | High risk and difficult sanitization | Clause samples, review criteria, responsibility boundary |

### 55.4.2 Keep Review Records

Rejected cases also have value. The rejection reason can reveal engineering material this book still needs: missing evaluation samples, missing permission topology, missing failure recovery, missing sanitized screenshots, or unverifiable benefit figures. Later versions should keep a case review record instead of letting material scatter across documents and chat logs.

The review record does not need to be complicated, but it should support editorial decisions. `case_id` should use a candidate identifier rather than a customer name. Scenario type should distinguish DataAgent, customer service, sales, operations, legal, and other directions. Evidence status should state whether samples, Trace, evaluation, and screenshots are complete. Sanitization status should record whether images, logs, data, and business terms passed sensitive-information checks. Risk boundaries should state whether automatic execution, confirmation, refusal, and degradation are clear. Main-chapter mapping should show which chapters the case supports and whether reverse revision is needed. The review conclusion should state whether the case is approved, returned, retained as material, or not published.

Review records also help plan later editions. If many candidate cases are returned because Trace is missing, the platform needs better run records before more writing. If sanitized screenshots are unavailable across cases, the editorial process needs a unified redraw rule. If benefit numbers have no source, author guidance should state the evidence boundary more plainly. The review table is a quality feedback system for the book. When a case is accepted, the review record should still remain in internal editorial material so that later reprints, English translation, or new diagrams do not repeat the same sensitive-information and overclaiming problems.

## 55.5 Downgrade writing when case material is insufficient

Case review often encounters insufficient material. A real project may lack complete Trace records, public screenshots, or shareable business data. In that situation, the draft should not force the material into a complete success case. It should be downgraded to a method case, chain example, or problem retrospective. Downgrading does not lower quality. It states the evidence boundary honestly so that readers know which conclusions come from a real chain and which are abstracted method summaries.

When material is thin, preserve the task chain first. Readers need to see the user goal, Agent decomposition, tool calls, risk control, and review method. Numbers can be sanitized, screenshots can be redrawn, and field names can be replaced with general names, but the chain cannot break. If the chain itself cannot be proven, the material should not be written as a case. It can only become a design suggestion or a direction for later validation.

Chapter 54 handles case admission. Chapter 55 feeds case review back into the main chapters. Gaps found during review should revise the body of the book: if cases keep failing at semantic-layer definitions, Chapter 33 should strengthen metric governance; if cases keep failing at report publication, Chapter 36 should strengthen EvidenceRef and review flow; if cases keep getting stuck at approval, Chapter 30 should strengthen HITL state recovery. Case chapters should be part of the quality loop of the whole book.

Before publication, each case should also define reader value. A case should teach at least one platform capability, one engineering boundary, or one failure lesson. Business background, screenshots, and outcome descriptions alone are not enough. Case writing should return to the main line of this book: how an enterprise Agent platform turns model capability into a governable, replayable, operable business system.

## 55.6 Case review workflow

Case review should follow an explicit workflow instead of leaving publication judgment to author intuition at the end. The first step is scenario-boundary review: who the user is, what the task is, which actions the system performs, which actions people confirm, and which capabilities are only demonstrated. The second step is evidence-chain review: whether input, tool calls, data sources, Trace, evaluation samples, human review, and final artifacts correspond to one another. The third step is platform-integration review: which shared capabilities the case consolidates, which parts remain scenario-specific, and which issues should be written back into the main chapters.

Review should distinguish missing material from missing capability. Missing material means the system may already have the capability, but the draft does not show evidence, such as Trace screenshots, failure samples, or evaluation results. Missing capability means the system does not yet implement the behavior, such as approval recovery, permission clipping, or report versioning. The first problem can be fixed by adding material. The second cannot be written as a completed capability. It can only be described as a later extension direction or a design constraint.

Review should also avoid overfilling the story. The first edition does not require every case to cover the full platform. It requires honest scope. A read-only question-answering case can focus on semantic layer, NL2SQL, and EvidenceRef. A write-action case should focus on HITL, tool idempotency, and compensation. An organization-governance case can focus on evaluation and operating cadence. Clear case boundaries make the platform design more believable.

## 55.7 Relationship to Chapter 54

Chapter 54 is responsible for case admission and writing method. Chapter 55 brings case review back to the platform main line. The two chapters should not repeat the same advice about how cases should be written. A better division is: Chapter 54 tells authors which cases can enter the book, what material they need, and how to downgrade when material is insufficient; Chapter 55 checks whether those cases really support the book's claims and maps review conclusions back to the earlier chapters.

The mapping can be concrete. If a sales case exposes tool-permission and approval issues, it should return to Chapters 23 and 30. If a financial query case exposes metric-definition problems, it should return to Chapters 33 and 34. If a report case exposes weak evidence, it should return to Chapters 36 and 38. If a security case exposes over-permission or injection risk, it should return to Chapters 50 and 51. Cases are therefore not an appendix after the main text. They are material for validating the platform architecture.

At the end of the first edition, Chapter 55 can serve as a quality gate for the whole book. It reminds authors and readers that cases are not here to prove that Agent systems are powerful. They test whether the platform design can withstand real business processes. Cases that pass review can enter the formal version. Cases with insufficient material should be downgraded to design discussion rather than written as successful production practice.

## Chapter Recap

Business cases and platform integration need explicit writing standards. Formal cases need auditable task chains, sanitized samples, and evaluation criteria. When material is insufficient, the first edition should keep rules and supplement lists rather than fabricate companies, benefits, or screenshots. Case review must separate functional demos from publishable cases. Publishable cases need evidence for failure, permission, evaluation, and sanitization, and they must explain how a scenario extracts into shared modules. Future case writing can start with DataAgent and ticketing or customer service scenarios because they cover much of the platform main line and can expose gaps in Runtime, Registry, Trace, evaluation, and security chapters.

## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE.

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).

OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

OpenTelemetry. (n.d.). [Documentation](https://opentelemetry.io/docs/).
