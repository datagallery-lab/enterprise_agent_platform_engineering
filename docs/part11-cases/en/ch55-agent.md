# Chapter 55 Case Review and Platform Integration

---

A case should not enter the public text until its evidence boundary is clear. Enterprise Agent cases involve tool permissions, business definitions, human confirmation, and audit evidence. If one boundary is written incorrectly, readers may misunderstand what the system can automate. A sales Agent may look like it only produces a quotation draft, but it touches discount approval, inventory commitment, and contract responsibility. A finance Agent may look like it only explains metric movement, but it touches metric versions, abnormal vouchers, and formal disclosure. A legal Agent may look like it only extracts clauses, but it touches legal judgment, responsibility statements, and signing advice. If case writing only shows that "the system can produce a result," it compresses all of these responsibilities into a feature demo.

The first review task is to check whether the evidence supports the conclusion. A case can say that the system generated a quotation draft, but it must state which data the draft used, where discount rules came from, and which actions stopped before approval. A case can say that the system assisted financial analysis, but it must state metric definitions, anomaly localization, and review records. A case can say that the system helped with contract review, but it must state clause evidence, risk labels, and final signing responsibility. Without these materials, the draft cannot hide behind a vague phrase such as "manual confirmation is retained," because readers still do not know where confirmation happened or who was responsible after failure.

The second review task is to bring the case back to platform capability. Sales, finance, and legal cases look like different businesses, but they often reuse the same capabilities underneath: Runtime manages execution state, Registry governs tools, the semantic layer governs definitions, Guardrails and approval chains govern risk, and Trace supports review after the fact. If a case only proves that one application performs one function, without showing how these platform capabilities work together, it is not yet a formal case for this book. It can be product material or an internal retrospective, but it does not prove the design of an enterprise-grade AI-native business system.

Cases also expose gaps in the main chapters. If several cases get stuck on approval timeout, Chapter 30 needs stronger recovery strategy. If several DataAgent cases get stuck on metric definitions, Chapters 33 and 34 need stronger version and compilation contracts. If several ticketing cases cannot explain failure reasons, Chapter 38 Trace and Chapter 39 evaluation samples are still insufficient. A case is useful when it tests whether the earlier architecture can survive real workflows, not when it only adds a complete-looking story near the end of the book.

This chapter does not fabricate company stories, go-live data, or benefit conclusions. This chapter gives the review method and platform integration method: first review evidence, then review risk boundaries, then extract reusable platform capabilities from single scenarios. After reading it, readers should be able to judge whether a candidate case can be published, what form it should be downgraded to when evidence is thin, and which main chapters should absorb the problems exposed by review.

---

## 55.1 Common Boundaries in Sales, Finance, and Legal Scenarios

Sales, finance, and legal scenarios usually carry more risk than ordinary knowledge Q&A because they affect quotation, settlement, compliance judgment, or contract responsibility. Case writing must first state the task boundary. The phrase "manual confirmation is retained" is not enough. The text must state where the system stops, who takes over, what is confirmed, and how the confirmation result returns to the system.

During review, the easiest problems often sit in the verbs. If the case says "generate a quotation," readers may understand it as a formal external quotation. If the case says "complete financial analysis," readers may understand it as a publishable conclusion. If the case says "review a contract," readers may understand it as a legal judgment. A safer draft splits the action: the system generates a draft, lists evidence, flags risk, submits approval, waits for confirmation, and records the result. Each verb maps to a system state or a human responsibility, which makes the case boundary much clearer.

*Table 55-1: Boundaries between automated and manual-confirmation parts in sales, finance, and legal scenarios. Source: Compiled by this book.*

| Scenario | Parts that can be automated | Parts requiring mandatory human confirmation |
| --- | --- | --- |
| Sales Agent | Summarize customer background, retrieve past quotes, generate quote drafts | Formal quotes, discount exceptions, customer commitments |
| Finance Agent | Explain metric changes, generate checklists, identify anomalous vouchers | Financial conclusion confirmation, definition changes, formal disclosure |
| Legal Agent | Extract clauses, identify risks, generate review draft comments | Legal judgment, contract signing advice, liability commitments |

These three scenarios share one trait: the system helps people approach judgment faster, while people and organizations still carry responsibility. Review should watch for two expressions in particular: treating "draft generation" as "completing the business action," and treating "assisted judgment" as "automatic decision-making." Both push the Agent boundary too far. Stating the boundary clearly does not weaken the case. It makes the system more credible, because production systems must know which actions can run automatically, which actions must wait, and which actions should be refused.

### 55.1.1 Boundaries Must Be Reflected in States and Actions

Simply writing "manual confirmation required" is still too abstract. Review should ask: in which state does confirmation occur, what material does the system provide to the person, what does the system do after confirmation, and how does the system handle rejection or timeout? For sales quoting, a reliable state design is: the Agent first generates a quote draft and risk note; if the discount stays below the regular threshold, the system records the draft; if the discount exceeds the threshold, the Run state enters `waiting_approval`; after manager approval, the system may generate the formal quotation email. This state transition should be visible in Trace instead of existing only in a design document.

*Table 55-2: State boundaries in high-risk business cases. Source: Compiled by this book.*

| State | System action | Human action | Review focus |
| --- | --- | --- | --- |
| draft_ready | Generate draft, list evidence and risks | Read and revise | Whether the draft clearly marks that it is not yet effective |
| waiting_approval | Pause high-risk actions, send approval request | Confirm, reject, or request supplements | Whether the approver has authority |
| approved | Continue executing approved actions | Take responsibility for business confirmation | Whether executed actions match approval |
| rejected | Stop execution and record reason | Provide rejection reason | Whether the system can bypass rejection |
| escalated | Escalate to human or work order | Take over the task | Whether context is transferred completely |

### 55.1.2 Review Must Distinguish "Capability Demonstration" from "Case Publication"

Just because a demo runs successfully does not mean the case can be published. A demo usually proves only that the system can produce a result under ideal input. A case must describe how it handles boundary input, insufficient permission, missing evidence, and tool failure. The reference book's practical projects work because project, code, and smoke tests support one another. This book does not rely on fabricated practical projects, so case review has to state the evidence requirement more explicitly.

A formal case should answer at least three follow-up questions. First, when the user provides incomplete input, how does the system clarify or degrade? Second, when a tool returns an error or permission is insufficient, how do the frontend and Trace record it? Third, when human review finds the result unreliable, how does the system preserve feedback and enter the next evaluation round? Demo videos rarely show these paths, but production cases must show or explain them.

*Table 55-3: Differences between demos, internal retrospectives, and formal cases. Source: Compiled by this book.*

| Material type | What can be shown | Limitations | Suitable for main text |
| --- | --- | --- | --- |
| Functional demo | Ideal path and UI interaction | Lacks failure samples, permission evidence, and evaluation | Not suitable alone |
| Internal retrospective | Real problem, failure reason, fix action | May contain sensitive information | Can become material after sanitization |
| Offline evaluation | Sample quality and model boundary | Does not represent production gains | Can support quality conclusions |
| Formal case | Task chain, evidence, risk, evaluation | Requires review overhead | Suitable for main text |

## 55.2 Platform integration writing method

Cases should describe an Agent's function and also explain how platform capabilities are accumulated. If a sales Agent, a finance Agent, and a legal Agent each implement tool permissions, approvals, Trace, and evaluation from scratch, the result is repeated construction instead of a platform. Platform integration extracts common capabilities from cases and writes them back into earlier platform chapters.

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

As cases grow, indexes should not be organized only by business type. Readers may want to find how approvals are handled, how tool permissions are managed, or how DataAgent evaluations are conducted. They may also look for sales, finance, or legal scenarios. The case index therefore needs at least two entry points: business scenario and platform capability. Part XI can keep this indexing method and expose it in navigation once public cases are ready.

## 55.4 Case review materials

When adding new case studies later, the following materials should be prepared together:

- Sanitized business task description.
- Data object, tool, and permission topology.
- Run state machine or sequence diagram.
- Human confirmation and refusal boundaries.
- Evaluation samples and acceptance criteria.
- Failure modes and rollback actions.

Without these materials, the case can remain in a candidate backlog, but it should not enter the public text. Fabricated companies, benefits, or screenshots only make a case look complete while weakening the evidence standard of the whole book. The supplement list should support decisions instead of create documentation burden. A sanitized task description helps teams judge whether the scenario is real. Data, tool, and permission topology helps teams judge the system boundary. A Run state machine helps teams replay the task. Human confirmation and refusal boundaries help teams judge whether risk is controlled. Evaluation samples and acceptance criteria help teams judge whether conclusions are trustworthy. Failure modes and rollback actions help teams judge whether the case is close to production. Each item maps to a judgment point in the text, and missing material should lower the strength of the conclusion.

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

The review record does not need to be complicated, but it should support publication decisions. `case_id` should use a candidate identifier instead of a customer name. Scenario type should distinguish DataAgent, customer service, sales, operations, legal, and other directions. Evidence status should state whether samples, Trace, evaluation, and screenshots are complete. Sanitization status should record whether images, logs, data, and business terms passed sensitive-information checks. Risk boundaries should state whether automatic execution, confirmation, refusal, and degradation are clear. Main-chapter mapping should show which chapters the case supports and whether reverse revision is needed. The review conclusion should state whether the case is approved, returned, retained as material, or not published.

Review records also help plan evidence maturity. If many candidate cases are returned because Trace is missing, the platform needs better run records before more cases are published. If sanitized screenshots are unavailable across cases, the case preparation process needs a unified redraw rule. If benefit numbers have no source, case guidance should state the evidence boundary more plainly. The review table is a quality feedback system for the book. When a case is accepted, the review record should still remain in internal evidence material so that future updates, English translation, or new diagrams do not repeat the same sensitive-information and overclaiming problems.

## 55.5 Downgrade writing when case material is insufficient

Case review often encounters insufficient material. A real project may lack complete Trace records, public screenshots, or shareable business data. In that situation, the text should not force the material into a complete success case. It should be downgraded to a method case, chain example, or problem retrospective. Downgrading does not lower quality. It states the evidence boundary honestly so that readers know which conclusions come from a real chain and which are abstracted method summaries.

When material is thin, preserve the task chain first. Readers need to see the user goal, Agent decomposition, tool calls, risk control, and review method. Numbers can be sanitized, screenshots can be redrawn, and field names can be replaced with general names, but the chain cannot break. If the chain itself cannot be proven, the material should not be written as a case. It can only become a design suggestion or a direction for later validation.

Chapter 54 handles case admission. Chapter 55 feeds case review back into the main chapters. Gaps found during review should revise the body of the book: if cases keep failing at semantic-layer definitions, Chapter 33 should strengthen metric governance; if cases keep failing at report publication, Chapter 36 should strengthen EvidenceRef and review flow; if cases keep getting stuck at approval, Chapter 30 should strengthen HITL state recovery. Case chapters should be part of the quality loop of the whole book.

Before publication, each case should also define reader value. A case should teach at least one platform capability, one engineering boundary, or one failure lesson. Business background, screenshots, and outcome descriptions alone are not enough. Case writing should return to the main line of this book: how an enterprise Agent platform turns model capability into a governable, replayable, operable business system.

## 55.6 Case review workflow

Case review should follow an explicit workflow instead of leaving publication judgment to evidence maturity at the end. The first step is scenario-boundary review: who the user is, what the task is, which actions the system performs, which actions people confirm, and which capabilities are only demonstrated. The second step is evidence-chain review: whether input, tool calls, data sources, Trace, evaluation samples, human review, and final artifacts correspond to one another. The third step is platform-integration review: which shared capabilities the case consolidates, which parts remain scenario-specific, and which issues should be written back into the main chapters.

Review should distinguish missing material from missing capability. Missing material means the system may already have the capability, but the text does not show evidence, such as Trace screenshots, failure samples, or evaluation results. Missing capability means the system does not yet implement the behavior, such as approval recovery, permission clipping, or report versioning. The first problem can be fixed by adding material. The second cannot be written as a completed capability. It can only be described as a later extension direction or a design constraint.

Review should also avoid overfilling the story. This book does not require every case to cover the full platform. It requires honest scope. A read-only question-answering case can focus on semantic layer, NL2SQL, and EvidenceRef. A write-action case should focus on HITL, tool idempotency, and compensation. An organization-governance case can focus on evaluation and operating cadence. Clear case boundaries make the platform design more believable.

## 55.7 Relationship to Chapter 54

Chapter 54 is responsible for case admission and writing method. Chapter 55 brings case review back to the platform main line. The two chapters should not repeat the same advice about how cases should be written. A better division is: Chapter 54 tells teams which cases can enter the book, what material they need, and how to downgrade when material is insufficient; Chapter 55 checks whether those cases really support the book's claims and maps review conclusions back to the earlier chapters.

The mapping can be concrete. If a sales case exposes tool-permission and approval issues, it should return to Chapters 23 and 30. If a financial query case exposes metric-definition problems, it should return to Chapters 33 and 34. If a report case exposes weak evidence, it should return to Chapters 36 and 38. If a security case exposes over-permission or injection risk, it should return to Chapters 50 and 51. Cases are therefore not an appendix after the main text. They are material for validating the platform architecture.

At the end of the book, Chapter 55 can serve as a quality gate for the whole book. It reminds readers that cases are not here to prove that Agent systems are powerful. They test whether the platform design can withstand real business processes. Cases that pass review can enter the public version. Cases with insufficient material should be downgraded to design discussion instead of written as successful production practice.

## 55.8 Case Review Ledger and Version Roadmap

Case review needs a ledger instead of scattered review comments. The ledger should record candidate case ID, business direction, material status, evidence source, sanitization status, risk boundary, main-chapter mapping, review conclusion, and next action. Candidate IDs should avoid customer names or project codenames so sensitive information is not exposed during material preparation. Material status should distinguish whether task description, Trace, tool calls, evaluation samples, screenshots, and human review are complete. Review conclusions should be explicit: approved, returned for more material, downgraded to method example, retained for evidence review, or excluded from the public text.

The ledger also becomes a evidence roadmap. If complete public cases are not yet available, Part XI can keep methods and admission standards. The ledger can then help select the DataAgent, ticketing or customer service, operations, or sales cases with the strongest evidence. Selection should follow material quality and mainline value, not how fashionable a scenario sounds. A well-evidenced ticketing Agent is often more suitable for the book than a high-value industry story with only outcome description. The ledger keeps evolution tied to evidence maturity.

The ledger should also record reverse-revision items. If a case shows that Chapter 30 does not explain approval timeout clearly enough, record a HITL timeout recovery supplement. If a case shows that Chapter 33 lacks metric-version migration, record a semantic-layer change-governance supplement. If a case shows that Chapter 51 security policy cannot explain a refusal, record a policy-evidence and refusal-explanation supplement. These items should enter the main text revision plan. Cases validate the architecture; they are not display material after the body of the book.

## 55.9 Maintenance After Cases Enter The Text

Cases still need maintenance after they enter the text. Business rules, protocol versions, tool contracts, diagram material, and evaluation criteria all change. Without maintenance, a case turns from engineering evidence into a historical snapshot. Maintenance should first check three things: whether the task chain can still be replayed, whether the risk boundary is still supported, and whether the case still maps to the main chapters. If a tool interface has been retired, the text can keep it as historical material but should mark the version. If a metric definition has migrated, the explanation should be updated or the case should leave the default set. If a diagram comes from an old process, redraw it or mark the version.

English maintenance has to move with Chinese maintenance. Case translation should synchronize figure captions, table captions, terminology, evidence boundaries, material sources, and body text together. If Chinese says that a diagram was redrawn from a sanitized case, English should say the same. If Chinese downgrades a material item to a method example, English should not call it a production case. Divergent bilingual boundaries give readers different risk judgments. When adding a new case later, first settle the Chinese evidence and expression boundary, then rewrite the English version under the same logic instead of translating sentence by sentence.

Maintenance also includes removal. A case that can no longer be replayed, has higher sanitization risk, loses the source for benefit claims, or no longer maps to revised main chapters should leave the body text or downgrade to internal material. Removing a case protects the evidence standard. An engineering book is not weakened by having fewer cases; it is weakened by cases that look rich but fail review. With a review ledger and evidence roadmap, the number of cases can grow gradually without lowering the quality bar.

## 55.10 From Review Conclusions To Revision Tasks

Case review conclusions should become follow-up tasks. Approved cases enter the publication queue. Returned cases list missing material. Downgraded cases state whether they become method examples, chain examples, or internal retrospectives. Cases excluded from the public text should state the reason: sanitization risk, weak evidence, unsupported benefit claims, or main chapters that are not ready. The team then knows whether to add Trace, evaluation samples, screenshots, approval records, or lower the strength of the wording. Without this step, review becomes a subjective decision and the next revision will repeat the same gap.

Follow-up tasks should go to specific roles. Business teams add task background, user goals, and review comments. Platform teams add Runtime, Registry, Trace, HITL, and protocol evidence. Data teams add metric definitions, semantic-layer versions, and data permission boundaries. Security or compliance teams add policy, sanitization, and audit requirements. A final prose pass unifies prose, figure and table numbering, citations, and evidence boundaries. Cases often fail because ownership is vague: business teams cannot produce Trace, platform teams cannot explain business value, and the text lacks evidence for deletion decisions. Assigning tasks to the right role gives the case a chance to become complete.

Review conclusions should also enter the evidence plan. The book can keep the method framework and a few public chains until complete industry cases have enough evidence. Chinese should settle material boundaries first, and English should then be rewritten under the same boundary. Diagrams can start as self-drawn structure diagrams and later be replaced after sanitized material passes review. This route is more reliable than trying to make every case complete at once. It lets the book establish a quality standard first, then add material depth.

Finally, review tasks should return to reader value. Before a case enters the text, it should answer what the reader learns: a platform capability, a risk boundary, a failure repair method, or an organizational collaboration pattern. If the answer is only that an industry can use Agents, the material is not ready. Enterprise Agent platform engineering needs cases that help readers reuse judgment in their own projects.

Task-based review also reduces rework. Authors add evidence before expanding prose. Editors confirm boundaries before polishing language. The English version aligns material sources before rewriting expression. When this order is reversed, the manuscript often reads smoothly while evidence cannot support the claims. Deleting or downgrading at that point costs more than early review. Case chapters need this front-loaded judgment because business stories, interface screenshots, and outcome descriptions can easily pull the draft away from evidence.

Case review should become an operating habit. Whenever the team adds a case, replaces a diagram, updates the English version, or revises a main chapter, it should return to the review ledger and check material, evidence, and boundary. This keeps the case chapters from drifting after publication. They remain a quality gate that connects real business material to the platform engineering mainline.

That is the closing role of Chapter 55: case writing becomes a publishing process with ongoing review, write-back, and maintenance.

With that process, the case section can gain depth across editions without losing coherence.

## 55.11 From Case Review To Main-Chapter Calibration

Case review can guide calibration of the main chapters. If candidate cases repeatedly lack Trace, the observability chapters need more concrete treatment of Run replay, evidence export, and incident review. If cases cannot explain tool permission, the Tool Registry and MCP chapters need stronger coverage of permission inheritance, credential rotation, and Server admission. If case material cannot describe metric definitions clearly, the DataAgent chapters need more detail on semantic-layer versions, metric migration, and query evidence. Priorities should come from these review gaps, not from chapter length alone.

This turns the case section into a quality loop for the whole book. Cases are not a display area after the main chapters. They are material for testing whether the main text is specific enough for engineering work. A chapter is close to usable when it helps a team prepare case material, identify missing evidence, and define downgrade boundaries. If readers still cannot tell what evidence to keep before launch, how to replay failure, or which actions need human confirmation, the chapter needs more depth. Chapter 55 makes that judgment explicit so main-chapter additions have a clear direction.

This mechanism also prevents expansion for its own sake. New material should serve at least one review action: helping teams prepare material, helping teams judge evidence, helping platform teams add run records, or helping the English version keep the same boundary. A paragraph that serves none of these actions should not enter the case-closing chapter even if it reads smoothly. The more disciplined the case section is, the better it protects the evidence standard of the book.

## 55.12 Ongoing Maintenance For Case Chapters

Case chapters also need maintenance after publication. Platform capabilities change, terms change, diagrams are replaced, the English version is updated, and real case material may become available later. Without maintenance rules, the text can drift: the main chapters update platform boundaries while cases keep old wording, Chinese cases add evidence while English cases stay behind, or diagrams change while text still cites the old figure.

Maintenance should record material state, masking state, diagram state, English sync state, related chapters, and latest review time for each case. When a main chapter adds a capability, the case should be checked for missing evidence. When a case receives new material, the main chapter should be checked for explanations that need strengthening. Case chapters and main chapters are not one-way dependencies. Real material often exposes weak spots in the main text.

Cases can be classified into three maintenance states: publishable case, method sample, and candidate material. A publishable case needs complete evidence and masking confirmation. A method sample explains writing method and admission standard. Candidate material records evidence gaps without entering the formal narrative. This lets the case section grow as material matures while avoiding invented completeness.

## 55.13 Evidence gaps in case chapters

Case chapters may leave gaps, but the reason for each gap should be clear. If real project material is not available, the text should not invent companies, numbers, or incidents. A steadier approach is to write available public information as method and mark missing parts as evidence requirements: business goal, original process, platform change, launch metric, failure sample, human review, and follow-up operations. Readers can see how a case should be built, and teams know what to request from project owners.

Evidence gaps also protect sensitive information. Customer names, revenue, contracts, permission policy, and incident details from enterprise projects may not be suitable for a public book. The chapter can use a sanitized task-chain description, but it should keep the reasoning structure: where the task starts, which platform capabilities are called, where risk pauses the task, how humans confirm, and how the artifact enters downstream work. Sanitization should not turn the case into a vague story. The evidence structure still needs to hold.

Additional case material should support platform judgment before adding narrative color. Readers need to know why the task was suitable for Agents, which capabilities were actually reused, where the system failed, and how the platform changed afterward. The value of a case chapter is that it tests the engineering method from earlier chapters inside a real organization.

## 55.14 Release cadence for case review

Case review should follow a fixed release cadence. The case section can keep methods and a small number of chain examples until public cases have complete evidence. The release note should state which material meets publication conditions and which material remains under evidence review. A cadence prevents two risks: filling the book with unverified success stories for completeness, or leaving the case chapters permanently abstract because real material is not yet public. It tells teams when to add evidence, when to downgrade claims, and when to remove material that no longer supports the text.

The cadence should connect to main-chapter revision. Whenever the body adds material on Runtime, Registry, Trace, Eval, security, or compliance, the team should check the case ledger for material that can be upgraded. Whenever case review exposes a gap, the revision task should return to the relevant chapter. A ticketing Agent case missing approval-timeout evidence feeds Chapter 30. A DataAgent case missing metric-migration material feeds Chapters 33 and 34. A security case missing false-positive appeal material feeds Chapter 51. Cases then keep strengthening the book instead of sitting as a separate ending.

Bilingual review should happen before publication. If a Chinese case is downgraded to a method example, the English version must carry the same downgrade. If a Chinese caption says a diagram is redrawn from sanitized material, the English caption should state the same source. If Chinese removes an unsupported benefit claim, English cannot keep an equivalent claim. Case chapters are especially prone to boundary drift in translation because English readers do not see the Chinese review record. Bilingual review should inspect titles, figures, tables, evidence sources, claim strength, and risk boundary.

The cadence should also allow exit. A case kept as a method sample may later exit because the material cannot be sanitized, the project stops, the benefit definition loses its source, or the main chapters move past the old boundary. Exit does not waste the work. The evidence review record still retains failure samples, tool contracts, evidence requirements, and writing lessons. For an engineering book, preserving the case standard matters more than preserving the case count. A case section that can admit, upgrade, downgrade, and retire material shows that the book's evidence system is alive.

## 55.15 Text consolidation after case review

When text consolidation after case review reaches production, the platform needs a shared evidence standard for fact check, sample replay, figure source, responsibility boundary, publishable information, edit record, and review conclusion. This standard is not paperwork for its own sake. It lets business, platform, data, security, and operations teams discuss the same facts. Without this material, incident review depends on memory and personal judgment. With it, the team can see which inputs were valid, which actions executed, which artifacts can still be used, and which results need correction or withdrawal.

This evidence should connect to Chapter 54 on case admission, Chapter 38 on Trace, and Chapter 52 on compliance evidence. The upstream chapters provide the capability base, downstream chapters consume the runtime result, and this chapter explains how the middle layer is verified. If a capability looks complete inside one chapter but cannot enter Trace, Eval, release records, or the compliance evidence package, the production system still has a break in the chain. Readers should treat cross-chapter interfaces as engineering contracts, not as a reading order.

Common risks include case text turning into promotional copy, problems being softened too much, missing evidence between platform capability and business result, and public drafts leaking internal information. A successful demo rarely exposes these problems because demo samples are usually clean, short, and direct. Real business traffic brings stale data, abnormal input, permission changes, user withdrawal, budget limits, and long-running state. If the platform does not turn those situations into samples and ledgers, later scenarios will hit the same class of issues again.

Case text turning into promotional copy should be turned into a tracked review item when it appears repeatedly. The operating record should at least state owner, version, sample, affected scope, action, and review time. It does not need to become a long process report, but it must be clear enough for a later maintainer to understand the decision. For high-risk capability, the record should also state which conditions allow wider use and which failures require degradation or withdrawal.

A first version can build this habit in a few representative scenarios. It is better to make high-traffic, high-risk, externally visible paths solid first, then copy the sample, ledger, and review method to related capabilities in other chapters. This makes the chapter read like engineering guidance: it explains how the capability is integrated, validated, operated, and retired.

## 55.16 Using case review to revise the main text

Case review should decide more than whether a case can be published. It should also revise the main text. Real cases often expose claims that are too neat: a tool integration needs extra approval inside an enterprise network, an evaluation sample expires after business change, a Trace field is insufficient during incident review, or a UI message causes users to misunderstand system state. These findings should be written back to the relevant chapters instead of being listed as a lesson at the end of a case.

Reverse revision needs clear routing. Tool issues go back to Chapters 23 and 24. Planner issues go back to Chapter 25. DataAgent issues go back to Chapters 32 through 36. Observability issues go back to Chapter 38. Compliance issues go back to Chapter 52. Ownership issues go back to Chapter 53. In this form, case chapters become part of the book quality-control process. Readers can see that cases are used to calibrate engineering judgment, not decorate the book.

A first version can add a small field to the case-review record: target chapter, judgment to revise, evidence, revision status, and follow-up sample. This field keeps cases and theory connected. As more cases enter the manuscript, the main text should contain fewer template claims and more production-grounded judgment.

## 55.17 Feedback archiving after case publication

Case publication still needs feedback archiving. Readers and business teams may point out inaccurate wording, weak evidence, inconsistent terminology, or process changes. If this feedback stays only in chat records, the next revision has to rediscover context. Platform-style writing should attach feedback to case number, chapter number, evidence material, and handling status.

Archived feedback also helps continued maintenance. If one case repeatedly receives questions about a metric definition, the main text needs a clearer definition. If one case repeatedly raises security-approval questions, Chapters 50 or 52 need a stronger connection. If readers cannot understand the platform boundary in a case, the overview chapters need better expectation setting. Case feedback then becomes input for the whole book, not isolated comments.

## 55.18 Diff notes between case versions

Case chapters will be revised many times. Version changes should state what changed: which evidence was added, which unproven judgment was removed, which figures were replaced by public versions, and which business metrics moved to ranges or relative descriptions. Without diff notes, readers cannot see where quality improved.

Diff notes also protect writing boundaries. Some edits come from confidentiality, some from weak evidence, and some from business-process change. Recording the reason prevents a later revision from adding removed material back by accident. A first version can maintain concise internal diff notes while the public text shows only the final narrative.

## Chapter Recap

Business cases and platform integration need explicit writing standards. Formal cases need auditable task chains, sanitized samples, and evaluation criteria. When material is insufficient, the text should keep rules and evidence lists instead of fabricating companies, benefits, or screenshots. Case review must separate functional demos from publishable cases. Publishable cases need evidence for failure, permission, evaluation, and sanitization, and they must explain how a scenario extracts into shared modules. New public cases can start with DataAgent and ticketing or customer service scenarios because they cover much of the platform main line and can expose gaps in Runtime, Registry, Trace, evaluation, and security chapters.

## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE. NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework). OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/). OpenTelemetry. (n.d.). [Documentation](https://opentelemetry.io/docs/).
