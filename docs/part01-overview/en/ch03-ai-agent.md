# Chapter 3 AI-Native Business Systems: Agents Reshape Enterprise Software

---
## Chapter Summary

There is a fundamental divide between simply adding a chat box to an "old system" and building an AI-native system from the ground up. The former places an assistant alongside existing pages to improve local efficiency, while the latter centers around "tasks" rather than "pages," shifting user behavior from sequentially navigating functions to delegating goals to the system. This chapter first clarifies the essential difference between these two approaches, then explains that existing ERP, CRM, and BI systems will not disappear but will instead be modularized and restructured as tools. Next, it provides criteria for prioritizing which business processes are most suitable for AI-native transformation. Finally, using the example of business analysis evolving from manual data assembly to a task-oriented workbench, it illustrates why implementing AI-native capabilities simultaneously involves product, platform, and organizational challenges.
## Key Terms

AI native, task-centered, page-centered, system tooling, product form, migration priority
## Learning Objectives

- Be able to distinguish the essential differences between "AI Augmentation" (adding AI to existing systems) and "AI Native" (task-centered reconstruction) transformations.
- Be able to explain why existing business systems are retained as tools rather than replaced in an AI Native architecture.
- Be able to prioritize the migration to AI Native workflows in enterprise business based on value, feasibility, and risk.
- Be able to identify the appropriate application scenarios for the three product forms: task assistants, embedded copilots, and agent workbenches.

---
## Opening Scenario

![Figure 3-1: Comparison between Legacy Systems with Added AI and AI-Native Business Systems](../../images/part1/en/ch03-01.png)

*Figure 3-1: Comparison between Legacy Systems with Added AI and AI-Native Business Systems. Source: drawn by the author. Alt text: On the left, the "Legacy System plus AI" has an assistant attached to the original page, and the user still operates features one by one; on the right, the "AI-Native" system is task-centered, where the user states a goal and the system orchestrates multiple legacy systems to accomplish it. The comparison highlights the shift of interaction entry points from pages to tasks.*

Legacy systems add localized intelligence within existing modules, while AI-native business systems take business tasks as entry points and use agents to reorganize underlying system capabilities.

---
## 3.1 Why "Old Systems Plus AI" Is Not the Same as AI-Native

A multi-business enterprise’s digital infrastructure is not outdated. The retail division has BI, the manufacturing division uses ERP, the customer service center operates a ticketing system, the financial shared service center manages a billing platform, and the headquarters maintains a knowledge base. Over the past few years, AI capabilities have been gradually added to these systems:

- BI supports natural language queries.
- CRM can automatically summarize customer statuses.
- ERP can alert on inventory anomalies.
- The ticketing system can automatically summarize and categorize tickets.
- The knowledge base supports semantic search.

These capabilities represent genuine progress, but they have not fundamentally changed how business collaboration occurs.

For example, before the group’s operational review meeting, the operations director still needs to repeat the same routine: open BI to check sales data, open the inventory system to identify shortages, open the customer service system to review complaints, open the knowledge base to revisit last month’s activity review, then compile all this information into a single report. Each system’s AI helps locally, but none take overall responsibility for the task of “preparing a usable operational review report for the meeting.”

This precisely highlights the fundamental difference between AI-augmented and AI-native systems. AI-augmented systems add smarter capabilities within existing legacy systems; AI-native systems put “completing the task” itself at the center of the system design. The former improves local efficiency; the latter rewrites system roles and division of labor.
## 3.2 From Page-Centered to Task-Centered: What Does AI Native Truly Change?

Many teams, when they first hear "AI native," immediately think of changes to the interface: buttons replaced by conversations, forms replaced by chat windows. But if the understanding stays only at this superficial level, it is far too shallow.

AI native business systems fundamentally change at least four aspects.

*Table 3-1: From Entry to Interaction — Comparison Between Traditional Business Systems and AI Native Systems. Source: Compiled by the author.*

| Change | Traditional Business System | AI Native Business System |
|---|---|---|
| **Entry** | User operates within a specific system module | User states a goal or a task |
| **Process** | Process steps predefined by pages and rules | Agent dynamically organizes steps around the goal |
| **Responsibility** | Each system responsible only for its own module | Agent responsible for end-to-end task results |
| **Collaboration** | Humans switch and piece together different systems | Systems switch between tools; humans provide constraints and validation |

In the traditional model, the user's job is to "piece it together themselves"; in the AI native model, the user’s role shifts to "defining goals, supplementing constraints, and deciding whether to accept results." User mindset shifts from "operating systems" to "managing tasks."

There is also a deeper change often overlooked: in traditional systems, the page is the primary organizing principle of the system; in AI native systems, tasks begin to replace pages as the core organizing principle. Previously, enterprise software trained people to be "module users"; AI native systems train people to be "task initiators." These two kinds of training feed back into product design, data organization, and even departmental collaboration styles.

This change will invalidate many traditional assumptions in enterprise software. In the past, the core design question was "which page does the user perform which action on"; now, system design becomes "after the user states a goal, how does the system organize a controllable task chain." Previously, product managers mainly cared about smooth page flows; now they must also care whether task status is transparent, evidence is sufficient, risk points are identifiable, and whether the process can continue after failures.

### 3.2.1 The Relationship Between AI Native, Digitization, Automation, and Intelligence

Enterprises have already gone through multiple rounds of system upgrades: digitization, automation, and intelligence. AI native is not a new slogan popping out of thin air; it evolves on top of these stages.

*Table 3-2: Goals, System Forms, and Limitations from Digitization, Automation, Intelligence to AI Native. Source: Compiled by the author.*

| Stage | Core Goal | Typical System Form | Limitations |
|---|---|---|---|
| **Digitization** | Bring business objects and processes into the system | ERP, CRM, OA, data warehouse | Many systems with rigid boundaries; users must piece together manually |
| **Automation** | Delegate stable processes to rule execution | Workflow, RPA, approval flows | Suited for fixed processes; not good for open-ended tasks |
| **Intelligence** | Add prediction, recommendation, generation to local functions | Intelligent search, recommendations, summarization | Intelligence is local; end-to-end tasks still organized by humans |
| **AI Native** | Enable dynamic organization of capabilities around task goals | Agent workbenches, task-based agents, generative UI | Requires platform, data, governance, and organizational support |

This table illustrates that AI native does not negate previous stages. Without digitization, there are no data or systems to call on; without automation, there are no embedded process nodes; without intelligence accumulation, there are insufficient local capabilities. AI native builds on this foundation by elevating “tasks” to a new organizing center.

If a multi-line enterprise does not have ERP, BI, CRM, ticketing systems, and knowledge bases, operational analysis agents have nothing to call on; without approval flows, quotation agents cannot safely access business processes. Therefore, AI native does not overthrow past informatization—it reorchestrates existing informatization assets.
## 3.3 Legacy Systems Will Not Disappear but Will Be Toolified and Reorchestrated

When discussing AI native systems, there is a common misconception: that all legacy systems will be replaced by a single conversational interface in the future. This judgment is overly simplistic.

ERP, CRM, BI, ticketing, and financial systems will not vanish just because Agents emerge. The reason is straightforward: they embody enterprise facts, rules, permissions, auditing, and transactional consistency. Agents should not bypass these systems but rather transform them into callable, interpretable, and governable tools.

*Table 3-3: Legacy systems like ERP and CRM shift from direct page operations to providing tool capabilities. Source: compiled by the author.*

| Legacy System Role | Past | AI Native Stage |
|---|---|---|
| ERP | Users directly operate pages | Provide tool capabilities for orders, inventory, procurement, finance, etc. |
| CRM | Users maintain customers and opportunities | Provide customer context, communication history, and action suggestions |
| BI | Users view reports | Provide metric queries, semantic layers, and data explanations |
| Ticketing System | Users process tickets | Provide event streams, status changes, and disposition actions |
| Knowledge Base | Users search materials | Provide referenceable policies, cases, and documentation |

Therefore, the key to AI native systems is not to “eliminate legacy systems” but to gradually transform legacy systems from user-operated interfaces into tools that Agents can call within authorization scopes. If done well, user experience will be simplified; if done poorly, it will result in Agents bypassing systems, losing permission control, and producing untraceable outcomes.

The emphasis in Chapter 2 on Tool Registry, Policy, and Trace reflects this principle. After legacy systems are toolified, the risk level of tools, call permissions, and outcome recording become essential platform management responsibilities.

### 3.3.1 Why User Mental Models Must Evolve Together

Many enterprises underestimate the importance of changing user mental models. As a result, system capabilities roll out, but users continue using the system in old ways, causing slow value realization.

Users trained on traditional systems have a mental model like this: Which page should I go to first? What should I enter in this field? Which button leads to the next step? How do I export the results to hand off to someone else?

AI native systems require a different set of skills: What exactly am I trying to accomplish? What constraints should I provide to the system? At what step is the task now? Are the results trustworthy, and do I need to confirm key points?

This is not a minor change. Users are no longer primarily “system operators” but rather “task initiators” and “result adjudicators.” If enterprises do not help users with this mental shift, typical problems arise: a technically functional AI native system that fails to be adopted in practice.
## 3.4 Which Businesses Are First to Become AI-Native: Scenario Prioritization and Migration Order

Not all business domains enter the AI-native stage simultaneously. In reality, the first to be transformed are often those tasks that are "cross-system, cross-knowledge sources, and cross-role," rather than highly structured, strong transactional, one-step operations.

*Table 3-4: Types of Tasks Suited for Priority AI-Native Transformation with Examples from a Multi-Business-Line Enterprise. Source: Compiled in this book.*

| Task Type                     | Why It’s Suitable for Priority Transformation     | Example from a Multi-Business-Line Enterprise       |
|-------------------------------|--------------------------------------------------|-----------------------------------------------------|
| **Cross-System Information Integration** | High cost of manual system switching and result stitching | Operational analysis, sales review, after-sales diagnosis |
| **Document-Intensive Tasks**            | Rules and bases scattered across documents and knowledge bases | Compliance review, bid response, contract review    |
| **Draft-Type Outputs**                  | Results can be generated first, then verified by humans | Quotation drafts, weekly operation reports, customer reply suggestions |
| **Diagnostic Tasks**                    | Require stepwise narrowing-down, not single-point queries | Gross profit anomaly analysis, inventory exception root cause |

In contrast, completely structured, one-time, strong transactional processes are usually not the first to be agent-automated. For example, actions like payment, contract signing, or master data deletion won’t suddenly become suited for automation just because of the phrase “AI-native.”

If a multi-business-line enterprise can only focus on three to five AI-native scenarios in a year, it should not pick based solely on which department is most enthusiastic. A more reliable approach is to simultaneously consider business value, task structure, data readiness, and risk controllability.

*Table 3-5: Typical Scenarios Scored Across Dimensions of Value, Structure, Data, and Risk with Recommendations. Source: Compiled in this book.*

| Scenario                    | Business Value | Task Structure | Data Readiness | Risk Controllability | Recommendation      |
|-----------------------------|----------------|----------------|----------------|----------------------|---------------------|
| Operational Analysis Material Generation | High           | High           | Medium-High    | High                 | Pilot with priority  |
| Customer Service Ticket Quality Inspection | Medium-High   | Medium         | High           | High                 | Pilot with priority  |
| Quotation Draft Generation  | High           | Medium-High    | Medium         | Medium               | Pilot with enhanced approval |
| Automatic Customer Email Reply | Medium      | Medium         | Medium         | Low                  | Proceed cautiously    |
| Automatic Payment Approval  | High           | Low            | Medium         | Very Low             | Defer Agent automation |

This prioritization is not about absolute correctness but about ensuring decision transparency. Many AI projects fail not because the scenario lacked value but because they initially chose a scenario with high value but also very high risk and unprepared data, ultimately exhausting organizational trust.

### 3.4.1 How AI-Native Systems Build Trust

Whether an AI-native system is adopted by the business ultimately depends on trust. This trust is not about “users thinking the model is smart”; it’s about whether users dare to entrust real tasks to the system.

Enterprise user trust typically comes from five sources.

*Table 3-6: Types of System Deliverables Required to Build User Trust. Source: Compiled in this book.*

| Trust Source           | What the System Must Provide                          |
|------------------------|------------------------------------------------------|
| **Visible Process**       | Users know what the system is doing instead of waiting blindly |
| **Verifiable Evidence**   | Conclusions can be traced back to data, documents, rules, or tool outputs |
| **Controllable Risk**     | High-risk actions require confirmation, approval, or downgrade |
| **Recoverability**        | Ability to retry, take over, rollback, or continue after failure |
| **Sustainable Improvement** | User feedback is incorporated into evaluation and version iterations |

If an agent’s output looks great but doesn’t provide evidence, business users at best consider it “inspirational.” If it provides evidence, status, and approval gateways, users start taking it seriously as a work system.

This also explains why an AI-native workbench cannot just be a chat box. Although chat boxes excel at expression, they are poor carriers of trust mechanisms. Task status, evidence zones, approval controls, and replay entry points—these features, which may seem less “intelligent,” are actually key to enterprise adoption.
## 3.5 AI-Native Product Forms: Task Assistants, Embedded Copilots, and Agent Workbenches

The journey of a multi-business-line enterprise can be summarized in three broad phases.

The first phase is **AI Augmentation**. Every system gains a degree of intelligence, but system boundaries and collaboration patterns remain fundamentally unchanged. BI is still BI; CRM is still CRM — they simply do a better job of understanding natural language and summarizing content.

The second phase is **Agent Embedding**. Agents capable of handling cross-system tasks begin to appear. Rather than serving as isolated point solutions, these agents can orchestrate short task chains. Operational analysis agents, quotation agents, and customer-service quality-inspection agents typically belong to this phase.

The third phase is a true **AI-Native Business System**. At this point, what users interact with is no longer primarily a legacy system but a task-centric workbench. The system organizes its own steps, generates intermediate results, initiates approvals, and persists an audit trail, while legacy systems gradually recede to the tooling layer.

Most enterprises will spend a prolonged period between the first and second phases. The third phase is neither achieved in a single effort nor entered simultaneously across all departments. It typically begins in the business domain where the fit is strongest and then spreads gradually.

![Figure 3-2: Three-phase migration toward AI-native business systems](../../images/part1/en/ch03-02.svg)

*Figure 3-2: Three-phase migration toward AI-native business systems. Source: original illustration by the authors. Alt text: Three phases shown left to right — Digitization (moving operations into systems), AI Augmentation (adding assistants to legacy systems), and AI Native (restructuring around tasks) — with arrows indicating that capabilities accumulate progressively rather than replacing what came before.*

Enterprises typically move from AI augmentation within legacy systems, through cross-system agent embedding, and ultimately arrive at a task-centric AI-native business system.

### 3.5.1 An AI-Native System Is Not a Chat Box — It Is a Task Workbench

When the topic of AI-native front ends comes up, the most common misconception is that swapping a search box for a chat box counts as AI-native. That is clearly insufficient.

A genuinely usable AI-native workbench must surface at least five categories of information for the user.

*Table 3-7: The role of each element in a task workbench. Source: compiled by the authors.*

| Workbench Element | Role |
|---|---|
| **Task Status** | Tells the user whether the system is planning, executing, awaiting approval, or has failed |
| **Evidence and Citations** | Tells the user which data sources, rules, and documents produced the result |
| **Structured Result Area** | Charts, tables, drafts, and action items must not all be buried inside conversation bubbles |
| **Human Takeover Entry Point** | When the system is uncertain, the user must be able to intervene, edit, and resume |
| **Approval and Confirmation Controls** | High-risk actions must not be hidden inside an ordinary message stream |

This means an AI-native front end is typically a combination of conversation, task flow, structured results, and approval controls — not simply a larger input box.

Users do not merely type "generate an operational analysis report" and wait for the system to emit a wall of text. A better experience looks like this: the system first displays the task goal and scope, asking the user to confirm that this analysis will focus on East China, gross margin, and last week's data; it then shows which metrics it intends to query and which data sources it will reference; if it discovers mid-execution that a particular metric has two conflicting definitions, it pauses and asks the user to choose; finally, it delivers charts, conclusions, citations, and action items, and allows the user to submit the output to an approval workflow for meeting materials.

That is an AI-native workbench — not "a report stuffed into a chat box."

![Figure 3-3: Structure of an AI-native task workbench](../../images/part1/en/ch03-03.png)

*Figure 3-3: Structure of an AI-native task workbench. Source: original illustration by the authors. Alt text: The workbench is divided into zones for task objectives, execution progress, evidence sources, and human confirmation entry points; the central area shows the system invoking multiple tools to advance the task, reflecting "task" rather than "page" as the organizing principle.*

An enterprise-grade task workbench must simultaneously present task status, execution progress, evidence citations, structured results, human takeover controls, and approval confirmations.
## 3.6 Business Analysis Meeting Case Study: From Manual Material Compilation to Task Workbench

Let's look at a complete case to understand how AI-native business systems fundamentally change ways of working.

A multi-line business enterprise holds its weekly business analysis meeting every Monday morning. Traditionally, starting Friday afternoon, the operations lead asks each region to submit data. The data team exports reports on sales, gross margin, inventory, promotions, and customer complaints. The operations specialist manually consolidates results from multiple systems into a PPT and then consults regional managers for explanations. By the Monday meeting, materials are usually ready, but they have three problems: first, inconsistent data definitions; second, root cause analysis often relies on manual experience; third, action items and follow-ups tend to get scattered across emails and chat groups.

If AI is just used to enhance existing systems, each system becomes a little smarter. The BI tool can answer “What was the gross margin in East China last week?” The ticket system can summarize complaints. The knowledge base can retrieve promotional reviews. The user experience improves, but the operations lead still has to do manual stitching.

If the system enters an Agent embedding phase, a business analysis Agent can take over a whole task chain. The user states the objective: “Prepare the business analysis meeting materials for next Monday, focusing on East China’s abnormal gross margin.” The system first confirms analysis scope: time, region, metrics, meeting templates. It then queries sales, gross margin, promotions, inventory, complaints data, finds the margin decrease mainly comes from two categories, and further checks if it relates to promotional discounts, logistics costs, or out-of-stock substitution sales. If conflicting metric definitions exist, the system pauses for the user to select the preferred definition.

Ultimately, it doesn’t generate a chat response but a set of meeting materials: anomaly summary, charts, evidence references, possible causes, questions to confirm, and suggested actions. Users can edit conclusions or assign actions to regional managers.

If further developed into an AI-native business workbench, the change is more drastic. Business analysis is no longer just preparing materials weekly on demand but a continuously running task space. The system continuously monitors key metrics, generates tasks upon anomalies, accumulates evidence, and prompts responsible persons to add explanations. Before meetings, materials just aggregate this week’s task status, evidence, and decision recommendations. After meetings, action items continue to be tracked in the same workbench.

The differences across these three stages can be summarized as follows:

*Table 3-8: Human-Machine Division of Labor at Each Stage of Business Analysis Meeting—From Traditional Mode to Task Workbench. Source: Compiled by this book.*

| Stage                | What User Mainly Does                                   | What System Mainly Does                             | How Meeting Materials Are Formed                   |
|----------------------|--------------------------------------------------------|----------------------------------------------------|----------------------------------------------------|
| Traditional Mode     | Manually query, manually compile, manually ask people  | Provide reports and records                         | Manually organized                                |
| AI Enhancement       | Ask AI in multiple systems                              | Each answers partial questions                      | Manually stitch together AI outputs                |
| Agent Embedding      | Define analysis goals, confirm key nodes               | Cross-system root cause analysis, generate drafts  | Agent generates, human reviews                      |
| AI-Native Workbench  | Manage ongoing tasks and action items                   | Continuous monitoring, attribution, evidence accumulation | Workbench auto-aggregates                           |

This case shows that AI-native’s essence is not “automatically writing PPTs.” The real transformation is turning business analysis from one-time, ad hoc material preparation into continuous task management. The system does more than generate content—it reorganizes relationships between data, evidence, meetings, and actions.

![Figure 3-4: Business Analysis Meeting — From Manual Material Compilation to Task Workbench](../../images/part1/en/ch03-04.png)

*Figure 3-4: Business Analysis Meeting — From Manual Material Compilation to Task Workbench. Source: Self-drawn for this book.*
*Alt text: Top 'Traditional Mode' shows operations staff manually querying and compiling materials across BI, inventory, and customer service systems. Bottom 'Task Workbench' shows user setting analysis goals, system automatically retrieving data and diagnosing, generating evidence-backed materials. The arrows highlight the step count difference between the two paths.*

AI-native systems organize cross-system data retrieval, anomaly root cause analysis, evidence accumulation, report generation, and action item follow-up into a continuous task chain.

### 3.6.1 User Training Focus: Task Templates, Not Prompts

Many enterprises immediately organize “prompt training” after launching AI-native systems. While helpful, simply teaching users how to write prompts can misdirect focus. What enterprise users truly need to learn is not chatting with the model but expressing work as executable tasks.

For example, “Help me analyze East China” is too vague. A better task definition should specify scope, goals, constraints, and deliverables: “Analyze last week’s East China gross margin decline causes, focusing on comparing impact of promotions, inventory, and logistics costs; output draft meeting materials and highlight questions needing regional manager confirmation.” This is not prompt engineering but task definition skill.

Therefore, AI-native systems should provide task templates, not just a blank input box. Task templates help users express goals clearly and help the system consistently understand boundaries.

*Table 3-9: Roles of Various Elements in a Business Analysis Task Template. Source: Compiled by this book.*

| Template Element | Purpose                                                  |
|------------------|----------------------------------------------------------|
| Task Goal        | Clarify what to accomplish, not just vague questions      |
| Analysis Scope   | Limit by time, region, product category, customer, process |
| Constraints      | Specify definitions, rules, risk boundaries               |
| Deliverables     | Specify report, charts, draft, recommendations, action items|
| Human Nodes      | Indicate where confirmation or approval is needed         |

A multi-line business can prepare a set of task templates for different scenarios: business analysis template, quotation draft template, customer service quality inspection template, invoice anomaly template, contract clause review template. Users start from business tasks, not from blank dialogs. This lowers entry barriers and makes platform evaluation and governance easier.

Task templates also have an added value: they solidify organizational experience. How excellent operations managers prepare business analysis meetings, how senior sales judge quotation risks, how finance supervisors check invoice anomalies—all can gradually be embedded into templates. The long-term value of AI-native systems emerges through this accumulation.

![Figure 3-5: From Functional Menus to Role Task Maps](../../images/part1/en/ch03-05.png)

*Figure 3-5: From Functional Menus to Role Task Maps. Source: Self-drawn for this book.*
*Alt text: On the left, a functional menu tree organized by system modules; on the right, a high-frequency task map organized by roles such as operations, sales, and customer service. Arrows indicate the product organization shifting from "function-first" to "role-task-first."*

AI-native business systems no longer organize entry only by function modules but build workspaces centered on high-value tasks for different roles.
## 3.7 Chapter Conclusion: AI-Native Will Ultimately Return to the Platform Panorama

What this chapter truly aims to deliver to readers is a demystified understanding of the term "AI-native business system."

First, AI-native is not just "adding another chat box"; it means the system organizes itself around tasks rather than pages.

Second, legacy systems will not disappear but will recede into the tool layer. They will continue to provide facts, rules, permissions, auditing, and transactional consistency.

Third, the best candidates for early AI-native adoption are those tasks that span multiple systems and knowledge sources, where draft generation and diagnostics are possible.

Fourth, the AI-native front end should be designed as a task workspace rather than simply an enlarged chat interface.

Fifth, AI-native is not a purely technical movement; it inevitably impacts product design, data, platform, security, and business collaboration methods.

The next chapter will regroup these conclusions into a complete map: Given that agent platforms ultimately serve AI-native business systems, why does the rest of this book proceed along the route of models, data, knowledge, platforms, evaluation, and security?
## References

Yao, S. et al. (2023). [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629). ICLR.

Schick, T. et al. (2023). [*Toolformer: Language Models Can Teach Themselves to Use Tools*](https://arxiv.org/abs/2302.04761). NeurIPS.

Model Context Protocol. (n.d.). [Specification and documentation](https://modelcontextprotocol.io/).

NIST. (2023). [*AI RMF 1.0*](https://www.nist.gov/itl/ai-risk-management-framework).
