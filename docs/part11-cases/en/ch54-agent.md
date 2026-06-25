# Chapter 54 Business Case Eligibility and Writing Methodology

---
## Chapter Summary

Enterprise agent case studies are among the easiest content to write badly. When source material is thin, authors dress up a feature demo as a production deployment, pass off an offline experiment as a live result, or invent fictional companies to paper over missing organizational context. Cases written this way look complete on the surface yet mislead readers about which capabilities are genuinely available and which risks have actually been brought under control. This chapter establishes the criteria a business case must meet before it can appear in the main text: first, determine whether the task is real and can be described with precision; next, verify that evidence exists for the data, tools, permissions, evaluation, and human-confirmation steps involved; finally, assess whether the case can be tied back to the platform capabilities introduced in earlier chapters. Declining to fabricate cases in the first edition is not an evasion of deployment realities — it is about setting the evidentiary bar for case writing before any cases are written at all.
## Key Terms

Case Admission, Engineering Evidence, Data Masking, Case Structure, Capability Mapping
## Learning Objectives

- Be able to explain why the first edition did not directly write cases, and how the admission criteria are defined.
- Be able to identify which types of materials can support a compliant case (real data, desensitization, engineering process).
- Be able to write a case using the recommended structure that can be included in this book.
- Be able to clearly link the case conclusions with the platform capability chapters previously discussed.

---
## Opening Scenario

Enterprise knowledge assistants, ticketing/customer service agents, development agents, and operations agents are all scenarios well suited to demonstrate platform capabilities. However, they are also the easiest to turn into generic feature stories. The Chinese first edition will refrain from writing specific company stories or fabricating go-live outcomes, metric benefits, or organizational backgrounds. This chapter first defines the minimum threshold for cases to enter the formal text: cases must be able to link back to the platform capabilities discussed earlier and illustrate how data, tools, permissions, evaluation, and human-machine collaboration jointly support a business task.

---
## 54.1 Case Inclusion Criteria

Before a case enters the main text, a straightforward question must be answered: Can readers reconstruct how this was actually done from the provided material? If the presentation only shows result statements like “Used Agent to improve efficiency,” “Integrated knowledge base,” or “Automatically generated report,” but does not reveal the task inputs, system boundaries, failure handling, and evaluation evidence, it is not yet a case—just promotional material.

A qualified case must meet at least four criteria.

*Table 54-1: Four conditions and acceptance criteria for cases included in the main text. Source: Compiled by this book.*

| Condition         | Acceptance Criteria                                                              |
|-------------------|----------------------------------------------------------------------------------|
| Clear business task | Clearly specify user roles, inputs, outputs, decision actions, and risk boundaries |
| Corresponding platform capability | Map to Runtime, Tool Registry, MCP, Planner, Memory, RAG, Eval, Trace, or Guardrails |
| Clear data and tool topology | Describe involved systems, data objects, permissions, audits, and failure recovery actions |
| No exaggerated outcomes | Avoid reporting unverified cost reduction, efficiency improvement, accuracy, or deployment scale |

These four criteria are not a formal checklist. They respectively guard against four common problems: unclear tasks, disconnected capabilities, missing evidence in the workflow, and exaggerated effects. Case authors should self-check using Table 54-1, and reviewers should use the same standards. If any criterion cannot be confirmed, the case can enter the material repository but should not appear in the main text.

### 54.1.1 Tasks Must Be Reproducible

Having a clear task is not the same as writing a sentence like “Sales need automatic quoting” or “Operations need to analyze decline reasons.” A reproducible task must contain at least five elements: who initiates it, what input they bring, what output they expect, which system actions are allowed, and which actions must stop and escalate to a human.

Take a quoting scenario as an example: “Generate pricing recommendations” is still too vague. A better description is: The salesperson selects customers and product packages in the CRM; the system reads historical contracts, inventory status, and discount policies, then generates a quote draft with risk warnings; final quotes, discount exceptions, and customer commitments must be approved by the sales manager. Only then can readers judge whether it’s a Copilot, Workflow, or a task execution system with an Agent closed loop.

### 54.1.2 Evidence Should Cover the Workflow, Not Just Results

Many cases show a beautiful result screenshot but skip how the system arrives at that result. For this book, screenshots only prove the interface appeared—they do not prove the workflow is trustworthy. Case evidence must cover input, retrieval, tool calls, permission checks, output, review, and feedback. Trace records, Tool Call logs, evaluation samples, sanitized logs, and human review sheets are often more important than final screenshots.

*Table 54-2: Case evidence materials and the conclusions they can support. Source: Compiled by this book.*

| Evidence Material    | Supported Conclusions                   | Unsupported Conclusions                 |
|---------------------|----------------------------------------|---------------------------------------|
| Sanitized task samples | Task type, input complexity, user roles | Deployment scale, business benefits    |
| Tool Call records     | Which systems were called, side effects | Tool results are definitely correct    |
| Trace and state machines | How the task progresses, where human confirmation occurs | Model capability superiority over alternatives |
| Evaluation sets and human reviews | Quality boundaries, common failure types     | ROI, organizational efficiency gains  |
| Sanitized screenshots | How users see results and evidence      | Production workflow is stable          |

Writers should avoid overstating the extrapolated scope of evidence. One offline evaluation can indicate quality trends but cannot directly show deployment benefits; a segment of sanitized logs can illustrate workflow shape but cannot prove the system meets production SLOs.

### 54.1.3 Sanitization Is More Than Name Replacement

Case sanitization is not just changing company names to “a certain enterprise.” It must address business identities, customer information, system domain names, field definitions, approval roles, ticket numbers, log timestamps, and metadata embedded in screenshots. For Agent cases, special care should be taken for tool call parameters and retrieval snippets, as these often expose internal system structures.

*Table 54-3: Agent case sanitization checklist. Source: Compiled by this book.*

| Object       | Common Leakage Points                 | Writing Treatment                          |
|--------------|-------------------------------------|-------------------------------------------|
| Business entity | Customer names, supplier names, stores, contract numbers | Replace with roles or categories while preserving task relationships |
| Data fields  | Internal field names, metric definitions, permission tags | Keep semantics, replace implementation details |
| Tool calls   | Internal domain names, real APIs, account IDs | Write as interface types and necessary parameters |
| Logs and traces | Timestamps, request IDs, user IDs          | Use synthetic IDs, preserve state transitions |
| Screenshots  | Watermarks, navigation bars, org charts, avatars | Redraw or crop, keep only areas needed for explanation |

If sanitization would destroy key causal relationships in the case, do not forcibly publish it. Instead, hold the material for internal review and only release public versions after obtaining sufficiently anonymized samples.
## 54.2 Recommended Case Structure

Each case study is recommended to follow a consistent structure to facilitate cross-references with the capability chapters earlier. The purpose of having a consistent structure is not to create a rigid template, but to enable readers to compare different scenarios: which capabilities are scenario-specific, and which should be consolidated as common platform features.

1. Business Task: Who initiates the task, under what scenario, and why fixed workflows or ordinary Q&A cannot handle it alone.
2. Data and Tools: What systems, documents, tables, APIs, or human approval steps the task needs to access.
3. Agent Design: How to split the Planner, tool invocations, memory, retrieval, human-in-the-loop confirmation, and result delivery.
4. Execution Flow: What states the task transitions through from input to output, and where tracing and audit evidence are recorded.
5. Risk Control: Which actions must be refused, downgraded, reviewed, or handed over to humans.
6. Evaluation Methods: How to use offline samples, manual reviews, online feedback, and business metrics to judge usability.

### 54.2.1 Start from the Task, Not from System Capabilities

Poor cases often start like this: “This case is based on RAG, Planner, Tool Registry, and Guardrails to build an intelligent customer service Agent.” This sentence may sound complete, but actually does not tell the reader why such a system is needed. A better approach is to first describe task frictions: customer service needs to handle refund disputes within minutes, but the order system, logistic system, and policy knowledge base are scattered across different systems; fixed workflows only cover standard refunds and fail when promotions overlap, partial shipments occur, or manual promises are involved.

Only after clearly defining the task do platform capabilities have context. RAG is used to find policies, Tool Registry limits order queries and refund calculations, Human-in-the-loop handles exceptional refunds, and Trace preserves evidence. This sequence aligns more closely with a reference book style: first show the problem, then provide the engineering structure.

### 54.2.2 Clearly Specify the “Non-automated” Parts

Agent case studies often overstate automation coverage. Truly mature enterprise cases clearly specify what the system does not do. For example, in sales quoting cases, the Agent can summarize information, generate drafts, and check discount policies but cannot make commitments to customers on behalf of sales; in legal review cases, the Agent can extract clauses and flag risks but cannot give final legal opinions; in finance analysis cases, the Agent can explain metric changes but cannot confirm disclosure standards on behalf of responsible personnel.

These boundaries are not conservative but are prerequisites for trustworthy production systems. When writing, separate “automatically completed,” “requiring confirmation,” and “must reject” actions so readers can evaluate if the case is truly feasible.

*Table 54-4: Expressions of Automation Boundaries in Case Writing. Source: Compiled by this book.*

| Action Category | What to State When Writing | Example |
| --- | --- | --- |
| Automatically Completed | Inputs, outputs, success conditions, and audit logs | Query historical orders and generate refund reason summary |
| Require Confirmation | Who confirms, what is confirmed, how timeout is handled | Manager confirms excessive discount before formal quote is issued |
| Must Reject | Rejection conditions, user prompts, and logging methods | User requests bypassing approval or accessing unauthorized contracts |
| Degraded Handling | Degradation trigger conditions and fallback paths | Switch to human knowledge base ticket when insufficient retrieval evidence |

### 54.2.3 Write Evaluation as Evidence, Not Slogans

Phrases like “accuracy improvement” or “efficiency gains” only have meaning if the evaluation criteria are clear. A case study must at least specify where samples come from, who performed annotation or review, how failure types are classified, and which metrics are process indicators only. For Agent cases, judging only final answer accuracy is insufficient; you must also assess whether tool invocations are correct, permissions are respected, human confirmation triggers as expected, and whether failures leave evidence for audit.

*Table 54-5: Case Evaluation Metrics and Their Applicable Boundaries. Source: Compiled by this book.*

| Metric | Suitable Questions Answered | Risks |
| --- | --- | --- |
| Task Completion Rate | Can the system complete the entire task flow? | May mask high-risk actions corrected manually |
| Evidence Hit Rate | Does the answer cite the correct documents or data? | Does not prove correctness of reasoning |
| Tool Invocation Success Rate | Are tool parameters and returns contract-compliant? | Does not prove acceptance of business outcome |
| Human Takeover Rate | Does the system know to pause at boundaries? | Too low may imply overreach, too high may imply unusability |
| Review Pass Rate | Can business staff approve the results? | Depends on the consistency of review standards |
## 54.3 Correspondence with Previous Content

*Table 54-6: Correspondence between various case types and the key chapters and critical engineering issues covered earlier. Source: Compiled in this book.*

| Case Type | Key Chapters | Critical Issues |
| --- | --- | --- |
| Enterprise Knowledge Assistant | Chapters 20, 21, 27, 40 | Knowledge update, evidence citation, memory boundaries, and answer evaluation |
| Ticketing / Customer Service Agent | Chapters 8, 23, 30, 51 | Structured output, tool invocation, human takeover, and content safety |
| R&D Agent | Chapters 22, 23, 28, 39 | Long task execution, code tool permissions, multi-agent collaboration, and evaluation |
| Operations Agent | Chapters 38, 42, 45, 46 | Trace, SLO, gateway governance, and GitOps change boundaries |

This table is not intended to require every case to cover all chapters but to prevent cases from being disconnected from the main text. For example, a ticketing agent case that does not explain structured output and human takeover cannot support the claims in Chapters 8 and 30; an operations agent without trace, SLO, and change boundary features counts only as a tool demo rather than a production case.

### 54.3.1 Filtering Out Cases That Have “Functionality But No Platform”

A case’s inclusion in this book also depends on whether it reflects platform capabilities. If the material only shows "calling a large model to generate a result," but provides no insight into the role of Runtime, Registry, Gateway, Memory, Eval, Trace, or Guardrails, then it is better suited for a blog post or product intro rather than inclusion in the main text.

During review, a simple criterion can be used: the case should use at least three types of platform capabilities with evidence for each. For example, knowledge assistant cases typically require RAG, Memory, and Eval; ticketing agents typically require Registry, Human-in-the-loop, and Guardrails; DataAgent cases usually need semantic layer, sql_executor, Trace, and evaluation samples.

### 54.3.2 Minimal Correspondence with mini-platform

The first edition already includes a mini-platform and test cases. When adding new cases later, priority should be given to scenarios that correspond to existing engineering pathways rather than creating a separate unverifiable system. Cases don’t need to include all code inline but should at least clarify which module the minimal implementation falls under.

*Table 54-7: Minimal correspondence between case materials and mini-platform capabilities. Source: Compiled in this book.*

| Case Material | Corresponding mini-platform Capability | Should Explain in Text |
| --- | --- | --- |
| Task status transitions | Runtime / Run status | How status progresses from input to completion or failure |
| Tool call records | Tool Registry / executor | Tool contract, permissions, and failure responses |
| Metric definitions and queries | semantic layer / sql_executor | Metric binding, SQL validation, and read-only restrictions |
| Evidence citation | RAG / retrieval | Document version, cited snippet, and evidence coverage |
| Evaluation samples | eval / benchmark | Sample origin, labeling, and failure classification |
## 54.4 Follow-up Requirements for Supplemental Case Writing

For subsequent versions supplementing cases, anonymized composite scenarios can be used, but it must be clearly stated that these are common engineering scenarios rather than real company stories. Do not include customer names, production data, internal domains, real tickets, real accounts, or unverified revenue figures. If the case needs to show interfaces, logs, or reports, desensitized samples must be used, and the source of charts or tables should be cited in the captions.

The supplemental writing process is recommended to be carried out in three steps.

The first step is material registration. The author submits the task description, desensitized samples, system topology, risk boundaries, and evaluation materials. Editors only check whether materials are complete; they do not polish the content in this step.

The second step is evidence verification. Reviewers check whether the materials support every conclusion in the main text. Any statements involving revenue, accuracy, latency, cost, or deployment scale must have sources; content without sources must be marked as “unverified hypothesis” or removed.

The third step is main text rewriting. Only materials that pass the first two steps proceed to formal case writing. When writing, prioritize preserving causal chains and failure boundaries; minimize product marketing language.

*Table 54-8: Case Supplemental Writing Process and Exit Criteria. Source: Compiled by this book.*

| Stage        | Input                      | Output            | Exit Criteria                    |
|--------------|----------------------------|-------------------|---------------------------------|
| Material Registration | Task description, samples, topology, screenshots | Material list    | Return if critical links missing |
| Evidence Verification  | Material list, evaluation records         | List of valid conclusions | Delete or downgrade unsupported conclusions |
| Main Text Rewriting    | Valid conclusions, chapter mapping         | Case text        | Pass tone, charts, and citations review |
| Release Review         | Text, images, data sources                  | Merged version   | No sensitive info, no exaggerated benefits |
## Chapter Recap

This chapter currently serves as a framework for case study writing and does not provide unverified business cases. Subsequent cases must support the main storyline throughout the book: applying the platform capabilities discussed earlier into concrete task workflows, rather than simply wrapping feature lists in stories.

- Before entering the main text, each case must be able to reconstruct the tasks, workflows, evidence, and boundaries.
- Data anonymization should address metadata in systems, data, logs, tool parameters, and screenshots—not just replace company names.
- Cases should start by describing the tasks, then explain how platform capabilities are involved; avoid beginning with a stack of technical jargon.
- Evaluation metrics must clarify the sample, review criteria, and failure classifications; offline results should never be presented as live production benefits.
## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE.

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).

OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

Model Context Protocol. (n.d.). [Specification and documentation](https://modelcontextprotocol.io/).
