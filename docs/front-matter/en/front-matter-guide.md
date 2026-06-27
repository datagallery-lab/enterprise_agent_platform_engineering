# Front Matter Guide: Structure, Reading Paths, and Release Boundary

## Purpose

This book covers model inference, data infrastructure, knowledge engineering, Agent Runtime, DataAgent, evaluation, deployment, frontend interaction, security, and organizational governance. It should not be read only as a linear textbook. A better approach is to identify the problem you are facing, then enter the matching part of the book.

This guide explains the main line of the book, gives reading paths by role and problem type, and clarifies the scope of the current edition.

## Book Structure

The book can be read in four layers.

The first layer is platform perspective. Part I explains what Agents are, why enterprises need platforms, how AI-native business systems differ from conventional software, and how the rest of the book forms a reference architecture.

The second layer is capability foundation. Parts II to IV cover model inference, data infrastructure, vector retrieval, and knowledge engineering. They answer what model, data, and knowledge environment an Agent needs before answering, retrieving, and executing can become governable capabilities.

The third layer is Agent and DataAgent. Part V covers Runtime, Tool Registry, MCP, Planner, Workflow, Memory, multi-agent collaboration, protocols, and HITL. Part VI applies those platform capabilities to DataAgent product forms, semantic layers, NL2SQL, Python analysis, visualization, reporting, and ecosystem comparison.

The fourth layer is production governance. Parts VII to X cover observability, evaluation, cost, SLOs, deployment, gateway, frontend, multimodality, security, compliance, and organizational evolution. These topics decide whether the system can run over time rather than remain a prototype.

Part XI is currently a case-methodology section. It defines how real cases should be admitted, reviewed, and consolidated into platform capabilities. It does not fabricate unverified business stories.

## Reading By Role

| Role | Recommended Path | Reading Goal |
| --- | --- | --- |
| AI platform leader / CTO | Part I -> Part V -> Part VI -> Part X | Decide platform boundary, investment order, organizational responsibility, and risk governance |
| Architect | Part I -> Part II -> Part III -> Part IV -> Part V -> Part VIII | Build an interface map across models, data, retrieval, runtime, and deployment |
| Data intelligence engineer | Part III -> Part IV -> Part VI -> Part VII | Build trustworthy question-answering, analysis, reporting, evaluation, and observability paths |
| AI application developer | Part II -> Part V -> Part IX -> mini-platform | Understand the runtime and interaction constraints between demo and production |
| Security / compliance owner | Part I -> Part VII -> Part X -> Appendix H | Translate tool risk, content safety, auditability, and regulation into engineering controls |

## Reading By Problem

If the question is how to choose models, start with Part II and then return to evaluation and cost in Part VII. Do not evaluate models only by leaderboard scores; include task profile, data boundary, output contract, latency, and rollback.

If the question is why DataAgent answers are unstable, start with Parts III, VI, and VII. Many failures come from semantic layers, table relationships, permission filters, SQL execution, evidence citation, and evaluation criteria rather than the model alone.

If the question is how an Agent moves from prototype to production, start with Parts V, VIII, and X. Runtime state machines, tool registration, gateways, multi-tenancy, security policies, human takeover, and audit chains are production foundations.

If the question is how teams should govern the platform, start with Parts I, VII, X, and the appendices. A platform cannot be owned by one application team alone; it needs shared terminology, gates, logs, owners, and review processes.

## Figures, Tables, Appendices, and Checklists

Figures in this book define system boundaries, flows, and state relationships. Tables express decisions, contracts, risk controls, and checklist items. They should be used as architecture-review templates rather than decorative illustrations.

Appendices support execution: installation, terminology, APIs, evaluation sets, writing rules, further reading, technical comparisons, and compliance checklists. The body of the book builds judgment; the appendices help turn judgment into action.

## First English Release Boundary

The current edition prioritizes stable technical chapters, reviewable figures and code references, and a locally buildable web-book project. Case chapters use admission and review standards unless source material, sanitization, and factual checks are sufficient for a full case.

When citing the book, record the reading date, chapter number, and page path so that later content changes can still be traced back to the original context.
