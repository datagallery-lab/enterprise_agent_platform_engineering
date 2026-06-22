# Chapter 55 Case Review and Platform Integration

---
## Chapter Summary

After completing a case, it cannot be directly released as the final version. Enterprise Agent cases involve tool permissions, business scopes, human verification, and audit evidence—any boundary written incorrectly may cause users to misunderstand the system’s true automation capabilities. This chapter defines the method for case re-review and platform-level consolidation: first verify whether the evidence supports the conclusion, then check if the risk boundaries are clearly defined, and finally distill isolated scenarios into reusable platform capabilities. Although sales, finance, and legal seem like three distinct domains, they often reuse the same underlying capabilities: the Runtime manages execution state, the Registry controls tools, the semantic layer manages business scope, and Guardrails plus approval chains manage risks. The goal of re-review is not to make the case more flashy, but to ensure it can be reused by engineering teams and traced by reviewers.
## Key Terms

case review, platform convergence, extraction of common capabilities, completion checklist, scenario boundaries
## Learning Objectives

- Be able to explain the verification dimensions in case review (evidence, desensitization, capability correspondence, reproducibility).
- Be able to extract shared platform capabilities from different scenarios such as sales, finance, and legal.
- Be able to rewrite single-point cases into descriptions pointing to shared capabilities using a platform-based convergence approach.
- Be able to provide prioritization and preparation requirements for supplementing cases in future versions.

---
## Opening Scenario

Business agent scenarios such as sales, finance, and legal impact pricing, settlement, compliance judgments, or contractual responsibilities. Therefore, they cannot be written solely based on whether the "function is demonstrable." The first Chinese edition does not fabricate specific company stories, go-live data, or conclusions about benefits. This chapter defines the review standards for subsequent cases and explains how cases evolve from a single-point agent to the platform capabilities of enterprise-level, AI-native business systems.

---
## 55.1 Common Boundaries in Sales, Finance, and Legal Scenarios

Sales, finance, and legal scenarios generally carry higher risks than ordinary knowledge Q&A because they impact quotations, settlements, compliance judgments, or contractual liabilities. When supplementing case studies, it is essential to first specify the task boundaries. Simply stating “require manual confirmation” is insufficient. Instead, clearly describe at what step the system stops, who takes over, what is confirmed, and how the confirmation result feeds back into the system.

*Table 55-1: Boundaries between automated and manual confirmation parts in sales, finance, and legal scenarios. Source: compiled by the author.*

| Scenario      | Parts that can be automated                        | Parts requiring mandatory manual confirmation         |
|---------------|---------------------------------------------------|--------------------------------------------------------|
| Sales Agent   | Summarize customer background, retrieve past quotes, generate quote drafts | Official quotes, discount exceptions, customer commitments |
| Finance Agent | Explain metric changes, generate checklists, identify anomalous vouchers | Finance conclusion confirmations, scope changes, official disclosures |
| Legal Agent   | Extract clauses, identify risks, generate review draft comments | Legal judgments, contract signing recommendations, liability commitments |

The commonality among these three types of scenarios is that the system can help humans arrive at judgments faster but cannot assume responsibility on their behalf. During review, particular caution should be taken with two types of descriptions: one is calling “draft generation” the same as “completing a business action”; the other is equating “assisted judgment” with “automatic decision-making.” Both approaches push the agent’s boundaries too far.

### 55.1.1 Boundaries Must Be Reflected in States and Actions

Simply writing “manual confirmation required” in a case is still too abstract. Reviewers should ask: At what state does the confirmation occur? What materials does the system provide to the human? After confirmation, what does the system do next? If the human rejects or times out, how does the system handle it?

Taking sales quotation as an example, a relatively robust state design is: The agent first generates a quote draft and risk note; if the discount is below a regular threshold, the system just records the draft; if the discount exceeds the threshold, the run state enters `waiting_approval`; only after the manager confirms does the system allow sending the official quotation email. This state transition should be visible in trace logs rather than only described in design documents.

*Table 55-2: State boundaries in high-risk business cases. Source: compiled by the author.*

| State            | System Action                               | Human Action                  | Review Focus                          |
|------------------|---------------------------------------------|------------------------------|-------------------------------------|
| draft_ready      | Generate draft, list evidence and risks      | Read and revise              | Whether the draft clearly marks it is not effective yet |
| waiting_approval | Pause high-risk actions, send approval request | Confirm, reject, or request supplements | Whether approver has authority       |
| approved        | Proceed to execute approved actions           | Take responsibility for business confirmation | Whether executed actions match approval |
| rejected        | Stop execution and record reasons             | Provide rejection reasons    | Whether system circumvents rejection |
| escalated       | Escalate to human or work order                | Take over the task           | Whether context is fully transferred |

### 55.1.2 Review Must Distinguish “Capability Demonstration” from “Case Publication”

Just because a demo runs successfully does not mean the case can be published. A demo only proves the system can produce a result under ideal input; a case must describe how it handles boundary inputs, insufficient permissions, missing evidence, and tool failures. The reference book’s practical projects succeed because project, code, and smoke tests reinforce each other. Since this book’s first edition does not provide practical projects yet, it is even more important to clearly specify evidence requirements during case review.

*Table 55-3: Differences between demos, internal retrospectives, and formal cases. Source: compiled by the author.*

| Material Type   | What Can Be Shown                         | Limitations                              | Suitable for Publication in Main Text? |
|-----------------|------------------------------------------|-----------------------------------------|----------------------------------------|
| Functional Demo | Ideal paths and user interface interaction | Lacks failure samples, permission, and evaluation | Not suitable to stand alone             |
| Internal Retrospective | Real problems, failure reasons, fix actions | May contain sensitive information         | After anonymization, can serve as material |
| Offline Evaluation | Sample quality and model boundaries       | Does not represent production gains       | Can support quality conclusions         |
| Formal Case     | Task chains, evidence, risks, evaluation | Requires review overhead                   | Suitable for main text                   |
## 55.2 Platform-Based Convergence Writing Approach

Cases should not only describe the functionality of a single Agent but also explain how platform capabilities are accumulated. If a sales Agent, a finance Agent, and a legal Agent each implement tool permissions, approvals, traceability, and evaluation from scratch, it is not platform-based but repeated development. Platform convergence requires extracting common capabilities from the cases and reflecting them back in the earlier platform chapters.

When supplementing cases later, each case must answer the following questions:

1. Which capabilities belong to business applications, and which should be integrated into a shared platform?
2. Which tools need to be registered in the Tool Registry, and which calls require approval or auditing?
3. Which context should go into RAG, which belong to Memory, and which must come from the semantic layer or master data systems?
4. Which results can be delivered automatically, and which should only be drafts or suggestions?
5. Which metrics are used to evaluate quality, cost, latency, review burden, and business value?

### 55.2.1 Extracting Shared Capabilities from Single-Point Cases

Platform-based convergence does not mean erasing all business differences. It retains business application variances while identifying reusable operational mechanisms. Discount approval in sales, calibration confirmation in finance, and liability opinion signing in legal may seem different on the surface, but all can be abstracted as “human confirmation before high-risk actions.” Such capabilities should be consolidated into Runtime and Human-in-the-loop frameworks, rather than implemented independently by each application.

*Table 55-4: Extracting Shared Platform Capabilities from Single-Point Cases. Source: Compiled by the author.*

| Single-Point Phenomenon                | Extractable Platform Capability             | Corresponding Chapters      |
|--------------------------------------|---------------------------------------------|----------------------------|
| Discounts over threshold require approval | Run state machine, approval nodes, timeout handling | Chapters 22, 30             |
| SQL queries may overload the database | sql_executor resource limits, read-only policies | Chapters 34, 42             |
| Answers must cite policy texts       | RAG evidence coverage, citation validation  | Chapters 20, 40             |
| Tool parameters may exceed permissions | Tool Registry, policy engine                | Chapters 23, 51             |
| Multiple roles involved simultaneously | Multi-Agent task division and handoff protocol | Chapters 28, 30             |

### 55.2.2 Clearly Define Ownership in Platform Convergence

Once shared capabilities are consolidated, responsible parties must be assigned. During case review, ownership should be checked: the business team is responsible for rule interpretation; the platform team for runtime and tool governance; the security team for policies and auditing; the data team for calibrations and data lineage. If the text only states “platform handles it uniformly” without clarifying who maintains rules, approves exceptions, or manages incidents, readers may mistakenly think the platform is an abstract layer with no organizational cost.

*Table 55-5: Responsibility Attribution for Platform Capabilities. Source: Compiled by the author.*

| Capability              | Primary Responsible Party       | Questions to Ask During Review                      |
|------------------------|--------------------------------|----------------------------------------------------|
| Tool registration and permissions | Platform team, Security team   | Who approves tool launch? Who handles unauthorized calls? |
| Metrics definitions and semantic layer | Data team, Business owner     | How are metric changes communicated to Agents?    |
| Approval workflows      | Business owner, Platform team   | How to handle absent or rejecting approvers?      |
| Evaluation samples      | Business team, Evaluation team  | Do samples cover failure and edge cases?           |
| Trace and audit         | Platform team, Compliance team  | How long is evidence retained? Who can access it? |
## 55.3 Relationship to the Main Chapters of the First Edition

*Table 55-6: Common convergence problems in platform consolidation and their corresponding main chapters in the first edition. Source: compiled by the authors.*

| Convergence Problem | Corresponding Chapter |
| --- | --- |
| How a standalone Agent enters a unified runtime | Chapter 22: Agent Runtime |
| How tools and permissions are governed centrally | Chapter 23: Tool Registry; Chapter 24: MCP |
| How multi-role tasks are divided | Chapter 28: Multi-Agent Collaboration; Chapter 30: Human-in-the-Loop |
| How data issues enter a trusted analytics pipeline | Part III; Part VI |
| How quality and cost are continuously evaluated | Part VII |
| How security, compliance, and organizational requirements are operationalized | Part X |

During case review, the main chapters are not merely "further reading"—they serve as the basis for verifying whether a case holds up. For example, a DataAgent case without a semantic layer can hardly support trusted analytics; a customer-service Agent case without human takeover can hardly handle long-running or high-risk scenarios; a software-engineering Agent case without tool-permission isolation cannot be summarized simply as "improving development efficiency."

### 55.3.1 Revising the Main Chapters in Reverse

Good cases do more than cite earlier content—they expose gaps in it. When multiple cases require a capability that the main chapters have not adequately explained, those chapters need to be supplemented. For instance, if later cases repeatedly raise the question of "what to do when an approval times out," Chapter 30 should be expanded to cover long-task waiting and recovery strategies; if multiple DataAgent cases encounter "metric-definition changes causing incorrect explanations," Chapters 33 and 34 should be expanded to cover definition versioning and SQL compilation cache invalidation.

*Table 55-7: Trigger conditions for cases prompting reverse revisions to main chapters. Source: compiled by the authors.*

| Problem Recurring in Cases | Chapter to Supplement | Direction of Supplementation |
| --- | --- | --- |
| Approval waiting, timeouts, and recovery | Chapter 22; Chapter 30 | Run states and human-takeover mechanisms |
| Tool parameter privilege escalation | Chapter 23; Chapter 51 | Tool schema, policies, and auditing |
| Metric-definition conflicts | Chapter 33; Chapter 34 | Semantic-layer versioning and SQL compilation contracts |
| Insufficient evidence citation | Chapter 20; Chapter 40 | RAG evaluation and citation verification |
| Uncontrolled costs | Chapter 41; Chapter 45 | Caching, gateway rate limiting, and budgeting |

### 55.3.2 Case Indexes Should Serve the Reader's Path

As the number of cases grows, organizing them by business type alone will be insufficient. Readers may want to find "how approvals are handled," "how tool permissions are managed," or "how DataAgent evaluations are conducted"—or they may be looking for "sales / finance / legal scenarios." The case index therefore needs at least two entry points: one organized by business scenario and one organized by platform capability. In the first edition, this indexing approach can be provisionally maintained within Part XI; once the full set of cases has been added, it can be surfaced in the navigation and index pages.
## 55.4 Checklist for Subsequent Version Supplements

When adding new case studies later, the following materials must be supplemented simultaneously.

- Desensitized business task descriptions.
- Data objects, tools, and permissions topology.
- Run state machines or sequence diagrams.
- Manual confirmation and rejection boundaries.
- Evaluation samples and acceptance criteria.
- Failure modes and rollback actions.

Without these materials, the case should not be included in the formal main text. It can be reserved for future plans but should not be filled with fabricated companies, fabricated benefits, or fabricated screenshots.

### 55.4.1 Supplement Priority

Subsequent case studies should not be evenly distributed. Priority should go to scenarios that cover the main thread of the entire book and can reuse the mini-platform. The first batch of cases is recommended to start with two categories: one is DataAgent trusted analysis, which can link semantic layer, NL2SQL, Trace, and evaluation; the other is work order/customer service Agent, which can integrate structured output, tool invocation, manual takeover, and Guardrails. Sales, legal, operation, and maintenance cases can be in the second batch, to be written after evidence materials become more sufficient.

*Table 55-8: Priority for Supplementing Subsequent Cases. Source: Compiled for this book.*

| Priority | Case Direction        | Why Priority                                   | Materials to Prepare                         |
| -------- | --------------------- | ---------------------------------------------- | --------------------------------------------|
| First batch | DataAgent Business Analysis | Covers Part III, Part VI, Part VII           | Semantic layer samples, SQL execution logs, evaluation sets |
| First batch | Work Order / Customer Service Agent | Covers tool invocation, manual takeover, security boundaries | Work order samples, tool contracts, takeover records |
| Second batch | Sales Quotation Agent   | High business value, but approval and responsibility boundaries are sensitive | Quotation rules, discount approvals, desensitization process |
| Second batch | Operation and Maintenance Agent | Can demonstrate Trace, SLO, and GitOps boundaries | Alert samples, change process, rollback records |
| Defer | Legal Review Agent      | High risk, difficulty in desensitizing materials | Clause samples, review criteria, responsibility boundaries |

### 55.4.2 Keep Review Records

Rejected cases also have value. The reason for rejection can reflect engineering materials that need to be supplemented later in this book: missing evaluation samples, missing permissions topology, missing failure recovery, missing desensitized screenshots, or unverifiable benefit figures. It is recommended to maintain a case review table going forward, recording the status of each candidate case instead of letting materials scatter across documents and chat logs.

*Table 55-9: Fields for Case Review Records. Source: Compiled for this book.*

| Field             | Description                           |
| ----------------- | ----------------------------------- |
| case_id           | Candidate case ID, avoid using client names |
| Scenario Type     | DataAgent, Customer Service, Sales, Operations, Legal, etc. |
| Evidence Status   | Completeness of samples, Trace, evaluation, screenshots |
| Desensitization Status | Whether sensitive information review is complete |
| Risk Boundaries   | Whether automatic, confirmation, rejection, and downgrade are clearly defined |
| Main Chapter Mapping | Corresponding chapters and whether backward revisions are needed |
| Review Conclusion | Approved, rejected, reserved materials, not published yet |
## Chapter Recap

This chapter currently serves to define the writing standards for business cases and platform convergence. Formal cases should be completed in future versions with real, auditable task flows, desensitized samples, and evaluation criteria; until then, the first edition does not use hypothetical cases to replace engineering evidence.

- The review must separate "functional demonstration" from "case publication"; the latter must include evidence of failure modes, permissions, evaluation, and data desensitization.
- Platform convergence should extract shared capabilities from individual scenarios and clearly specify ownership responsibilities.
- Cases can be used to iteratively revise main chapters, especially those on approval processes, tool permissions, semantic layer versions, referenced evaluations, and cost governance.
- Future additions should start by covering highly reusable cases for DataAgent and work order/customer service, then expand to sales, operations, and legal domains.
## References

Yin, R. K. (2018). *Case Study Research and Applications: Design and Methods*. SAGE.

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).

OWASP. (n.d.). [*Top 10 for Large Language Model Applications*](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

OpenTelemetry. (n.d.). [Documentation](https://opentelemetry.io/docs/).
