# Ch.02 The Boundary of an Enterprise Agent Platform

> **Chapter goal**: Help readers clarify what an enterprise is really building when it says "platform," how that differs from Agent applications, Agent frameworks, and low-code tools, and why platform boundaries become unavoidable once an enterprise enters the multi-Agent stage.
>
> **Intended readers**: Platform owners, architects, product leaders, AI office teams, and organizations preparing to move from isolated pilots toward platform-level construction.

![Multi-Agent shared platform boundary](images/ch2-1_en.png)

*Figure 2-1 Multi-Agent shared platform boundary: business Agents may each serve different tasks, but model, data, tool, process, and governance capabilities must be consolidated into a shared platform layer.*

---

## Why Enterprises Need Platforms, Not Isolated Agents

Chapter 1 discussed the problems that appear when a single Agent moves from "answering" to "executing." Chapter 2 raises the viewpoint by one level: what happens if Shanlan Group does not build only one quotation assistant, but gradually builds a quotation Agent, an operating-analysis Agent, a ticket Agent, and an invoice Agent?

At first glance, this should be good news. It means the enterprise has found multiple entry points for AI adoption, and each team is producing visible results.

Reality is often the opposite.

In the first year, Shanlan Group launched four pilots:

- A quotation Agent in manufacturing, responsible for reading contracts, checking inventory, and generating quotation drafts;
- An operating-analysis Agent in retail, responsible for asking data questions, finding anomalies, and writing review notes;
- A ticket Agent in the service center, responsible for summarizing complaints and suggesting handling actions;
- An invoice Agent in the finance shared-service center, responsible for recognizing invoices, matching orders, and generating voucher drafts.

All four pilots proved that a single point could work. The real difficulty appeared when the group wanted to bring these capabilities under unified governance.

The platform owner quickly had to ask a chain of questions:

- Which Agents can access customer identity information?
- Which tools can create real business side effects?
- Which model is used most often, costs the most, and fails most easily?
- Which Agents must go through approval, and which can execute automatically?
- If a task fails, can its decision process be replayed end to end?

If these questions have no unified answers, the enterprise has not truly entered the platform stage. It merely owns a set of fragmented intelligent projects.

That is the central position of this chapter: **the real enterprise difficulty is never only "can we build an Agent?" It is "can we let a group of Agents run for a long time under the same set of rules?"**

## Applications, Frameworks, and Platforms: Three Boundaries and Common Misjudgments

The most common conceptual mistake in the Agent field is mixing applications, frameworks, and platforms together. They are related, but they are not at the same layer.

| Layer | What it solves | Typical form |
|---|---|---|
| **Agent application** | How a specific business task gets done | Quotation Agent, DataAgent, ticket Agent |
| **Agent framework** | How a single Agent organizes state, calls tools, and manages memory | LangGraph, AutoGen, CrewAI, in-house orchestration framework |
| **Agent platform** | How multiple Agents share capabilities and are governed uniformly | Model gateway, tool registry, Runtime, Trace, Eval, Policy |

This distinction matters.

A framework focuses on "how to write one Agent." A platform focuses on "how to let many Agents exist inside an enterprise for a long time without fighting each other, rebuilding the same wheels, or losing governability."

An enterprise can hold both statements at the same time:

1. "Our application teams may choose the framework that fits them."
2. "All Agents must go through the same platform contract."

There is no contradiction. The platform is not there to replace frameworks. It is there to absorb the enterprise complexity above frameworks.

Low-code tools, Agent Studios, and visual flow editors should also be put back into this three-layer structure. They may solve "building an Agent application quickly" very well, but that does not automatically mean they solve the platform problem.

So, when deciding whether something is a "platform," do not look only at whether it has a console or a drag-and-drop interface. Ask whether it answers these questions:

- How are model calls across multiple Agents managed uniformly?
- How are tool capabilities across multiple Agents defined, classified, and versioned uniformly?
- How are permissions, approvals, traces, and evaluations connected uniformly across multiple Agents?

If these questions are still handled project by project, then the organization does not yet have a platform.

## The Five Shared Problems a Platform Manages: Models, Data, Tools, Processes, and Governance

An enterprise Agent platform may look like a pile of components, but in essence it manages five categories of shared problems.

| Shared problem | What the platform must answer |
|---|---|
| **Model problem** | Which model to call, how to route, how to rate-limit, how to aggregate cost |
| **Data problem** | Which data can be read, which metric definition applies, under which identity, and how to desensitize |
| **Tool problem** | Which capabilities exist, who can call them, whether parameters are valid, and whether side effects may occur |
| **Process problem** | What can execute automatically, what must wait for humans, and how long-running tasks recover |
| **Governance problem** | How to evaluate, record, replay, audit, and continuously improve |

It is closer to enterprise reality to understand the platform as "a unified solution to five categories of shared problems" than as "a collection of eight modules." Enterprises do not grow from architecture diagrams first. They grow from problems.

Why did Shanlan Group's first four pilots run into platform issues so quickly? Because although their businesses were different, the five categories of problems were almost identical:

- All needed to call models;
- All needed to read data or documents;
- All needed to call tools;
- All needed to judge risk;
- All needed to be explained and reviewed after errors.

For this reason, "platform boundary" is not technical fastidiousness. It is the result of consolidating shared problems.

Many enterprises will naturally compare this with data platforms, technology platforms, or capability platforms they have built before. That comparison is reasonable, but it must be handled carefully. An Agent platform certainly relates to those predecessors, but it cannot be reduced to them.

A data platform focuses on aggregating, governing, and using data assets. An application platform focuses on development efficiency and service reuse. An Agent platform focuses on task-execution chains in which models are the decision core. It borrows many assets from data and application platforms, but it carries a new responsibility: model decisions, tool side effects, human approvals, task replay, and version evaluation. In other words, an Agent platform does not replace the data platform or the middle platform. It adds a new responsibility layer above them.

![Five shared problems managed by the platform](images/ch2-2_en.png)

*Figure 2-2 Five shared problems managed by the platform: models, data, tools, processes, and governance together determine whether enterprise Agents can move from isolated pilots to long-term operation.*

## Drawing the Platform Boundary: What to Unify and What to Leave to the Business

Once we accept that a platform unifies shared problems, the next practical question is: which capabilities should belong to the platform, and which should remain in the application layer?

There is no universal rule, but there is a useful sequence of judgment.

Ask four questions first:

1. Will this capability be reused across multiple Agents?
2. Does it affect permissions, cost, auditability, or evaluation?
3. Does it depend on rules specific to one business domain?
4. Would platformizing it significantly reduce future onboarding cost?

Many boundaries become clear under these questions:

| Capability | Better ownership | Reason |
|---|---|---|
| Model-call entry point | Platform | All Agents reuse it; it affects cost and rate limits |
| Tool registration and risk level | Platform | Directly affects side-effect control and audit |
| Unified approval channel | Platform | High-risk actions cannot each invent their own approval path |
| Manufacturing quotation discount rules | Application | Strongly domain-specific |
| Service-center ticket priority policy | Application | Highly dependent on departmental business |
| Unified trace fields and run_id convention | Platform | Otherwise cross-Agent replay is impossible |
| Semantic-layer foundation | Mostly platform | Metrics and definitions must be unified |
| Business explanation details in the semantic layer | Platform and application jointly | Platform defines the frame; applications add domain knowledge |

This shows that platform boundaries are not "the bigger the platform, the better," nor "the thinner the platform, the more modern."

If the platform is too thin, it degenerates into a model gateway. If it is too thick, it becomes a monster that swallows all business logic. Mature platforms usually constrain strongly where unification is necessary and provide extension slots where difference is healthy.

Another underestimated dimension is **change velocity**. If a capability changes rapidly, is frequently experimented with, and depends heavily on specific business feedback, platformizing it too early slows innovation. If a capability changes more slowly and must be reused consistently, it should be platformized earlier. Many platforms are blamed for "blocking the business" not because platformization is wrong, but because highly volatile business logic was pulled into the platform too soon.

**When does an enterprise truly need platformization?**

Not every enterprise needs a platform team the moment it builds two Agents. A more practical test is whether three signals have appeared:

| Signal | What it indicates |
|---|---|
| **Repeated construction** | Different teams repeatedly wrap models, tools, RAG, approval, and logging |
| **Governance fracture** | The enterprise cannot answer permissions, cost, trace, and evaluation questions uniformly |
| **Onboarding friction** | Every new Agent rebuilds infrastructure from scratch |

When all three signals appear, platformization is no longer "nice to have." Without it, follow-up adoption will be dragged down.

This also explains a common illusion: the first two pilots move smoothly, and the third suddenly slows down. The first two projects can still advance independently. Starting with the third, infrastructure and governance costs begin to erupt together.

There is also a reality many teams overlook: platformization does not happen because technologists enjoy abstraction. It happens because the enterprise has begun to bear the management cost of "every project doing its own thing." Budget review starts asking who owns the model bill. Security starts asking who can access which data. Business teams start asking why different Agents answer the same question differently. Platforms are born under this pressure.

**Three common platform illusions.**

In early platform construction, enterprises easily fall into three states that look like platforms but are not yet platforms.

The first is the **gateway illusion**. The team builds a unified model entry point and believes the platform is done. But if tool contracts, risk levels, traces, and evaluations are still scattered across business projects, the "platform" is only a gateway.

The second is the **console illusion**. A polished page lets users create Agents and view call records, so everyone feels the platform problem has been solved. But if the page has no unified runtime contract and governance contract behind it, it is still only a management interface.

The third is the **framework illusion**. All application teams use the same Agent framework, and the organization assumes the platform is unified. A framework reduces implementation differences at the application layer, but it does not automatically solve multi-Agent governance.

These illusions are common because each solves a real pain point, so it is easy to over-name them. But a platform is heavier and slower than any of them because it solves enterprise commonality rather than single-point development efficiency.

Their danger is not that they have no value. Their danger is that they create the false feeling that "the platform problem has been solved." If the organization expands the number of Agents on top of that illusion, the later cost of adding governance will multiply.

## How Platforms Are Adopted by Organizations: Collaboration, Admission, and Governance Committees

When discussing platforms inside an enterprise, technical boundaries are not enough. Responsibility boundaries matter just as much. Once a platform exists, many decisions previously scattered across teams are redistributed.

| Decision question | Usually decided in pilot stage by | Better decided in platform stage by |
|---|---|---|
| Which model to use | Project team | Platform policy, with application requirements submitted |
| Which tools are callable | Project team wraps its own tools | Platform defines contracts; business adds details |
| Which actions require approval | Informal business agreement | Platform and security define rules together |
| How traces are recorded | Each project logs for itself | Platform unifies fields and run semantics |
| How version quality is judged | Subjective demo | Platform and business maintain evaluation criteria together |

This table reveals a practical fact: a platform is not merely a shared service center everyone naturally likes. It reallocates standard-setting power, admission power, and part of release authority. Real platform construction is therefore both technical engineering and organizational negotiation.

For this reason, the hardest resistance a platform team meets is often not purely technical. It usually comes from two sides.

Business teams worry that the platform will slow onboarding, limit flexibility, and pull experimentation into unified processes too early. Security and governance teams worry that the platform concentrates risk, gives systems too much decision power, and creates a new audit black box.

A mature platform team must answer both sides: it must prove "I will not slow you down" and "I can hold the boundary." That is why platform work is not only coding. It is institutional design.

**The economics of platforms: why "sharing" is not enough.**

The easiest slogan in enterprise platform work is "shared reuse." It is not wrong, but it is too empty. Sharing is not the goal. Reducing marginal cost is.

If every new Agent at Shanlan Group must reconnect models, permissions, tools, traces, approvals, and evaluations, the first Agent may be fast, the second still tolerable, and the third painfully slow. The economic meaning of a platform is that the Nth Agent costs far less to onboard than the first.

Costs can be divided into five categories:

| Cost type | Without platform | Ideal state with platform |
|---|---|---|
| Model integration cost | Each project integrates and bills independently | Unified routing, quota, and billing |
| Tool integration cost | Each project wraps tools repeatedly | Tools are registered once and reused by many Agents |
| Governance cost | Each project explains risk separately | Unified risk levels, approval, and audit |
| Evaluation cost | Each project relies on manual trial | Shared evaluation methods and regression flows |
| Learning cost | Each team explores from zero | Platform provides templates, samples, and admission process |

If a platform does not reduce these marginal costs, it is just a larger project, not a platform. Many so-called platform failures are essentially failures to make business teams feel that "using the platform is cheaper, faster, and more stable than doing it ourselves."

That is why the platform team cannot only emphasize governance. Governance matters, but if the platform only says "no," "needs approval," and "wait for scheduling," business teams will route around it. A good platform must provide two values at the same time: faster business delivery and lower risk.

**How platform capabilities should be consolidated by stage.**

A platform is not designed once. It is consolidated through reuse. Starting from Shanlan Group's four pilots, capabilities can be divided into three categories.

The first category is **immediate consolidation**. These capabilities must exist from the first production-grade Agent; otherwise the system cannot launch or cannot be governed. Examples include model entry, tool risk levels, task trace, and approval state.

The second category is **consolidation after reuse**. These capabilities should first be validated inside specific applications, then abstracted into the platform after more than one business scenario needs them. Examples include industry-term parsing, document-processing templates, and complex metric explanation logic.

The third category is **capabilities that should not be platformized**. These depend heavily on business strategy. The platform should provide interfaces and constraints, not take over the logic. Examples include manufacturing discount policy, customer-service complaint grading details, and department-specific prompt templates.

| Capability type | When to consolidate | Examples |
|---|---|---|
| Immediate consolidation | Before the first production-grade Agent | Model gateway, tool risk levels, trace, approval state |
| Consolidate after reuse | After cross-scenario reuse appears | Document parsing templates, evaluation sample structure, semantic-layer extension rules |
| Should not be platformized | Remain in business applications long term | Discount policy, service business rules, department-specific prompt templates |

This table avoids two extremes: over-abstracting on day one, or never abstracting at all.

**The relationship between Agent platforms, data platforms, and business middle platforms.**

If Shanlan Group has already built a data platform, business middle platform, or technology platform, is the Agent platform old wine in a new bottle or a new layer?

The answer is: it does not replace existing platforms. It is a task-execution layer above them.

The data platform answers where data comes from, how reliable it is, what definitions apply, and who can access it. The business middle platform answers how business capabilities are reused. The technology platform answers how applications are developed, deployed, and observed. The Agent platform answers how a model-centered system dynamically advances tasks on top of those resources.

| Platform type | Primary object | Primary problem |
|---|---|---|
| Data platform | Tables, metrics, lineage, quality | Data trust and usability |
| Business middle platform | Business capabilities, services, domain objects | Capability reuse |
| Technology platform | Applications, services, infrastructure | Development and runtime efficiency |
| Agent platform | Tasks, tools, model decisions, trace | Dynamic execution and governance |

Therefore, the Agent platform should not bypass existing platforms. It should consume the semantic layer and permission capabilities of the data platform, the service capabilities of the business middle platform, and deployment and observability capabilities of the technology platform. But it must also add what those platforms do not cover: model decisions, tool-call risk, task state, human intervention, and evaluation regression.

If the Agent platform becomes another island, it repeats the old middle-platform problem. If it is forced entirely into old platforms, the new complexity of Agents is flattened. The right position is to inherit existing platform assets while adding new contracts for the task-execution era.

**A platform is not a component repository. It is an operating institution.**

Many enterprises initially understand a platform as a component repository: model-call wrappers here, a few tool SDKs there, plus a log collector. That understanding is too light.

An enterprise Agent platform is complex because it does not manage one function, one service, or one model. It manages a continuously running task chain. That chain includes a user goal, model judgment, tool actions, data access, approvals, result delivery, and failure recovery. What the platform truly unifies is the institution across these links.

The platform institution can be divided into five parts:

| Institution | What it regulates |
|---|---|
| **Admission institution** | Which Agents may launch and what conditions they must meet |
| **Tool institution** | How tools are registered, classified, authorized, and retired |
| **Runtime institution** | How tasks are created, paused, resumed, and terminated |
| **Evaluation institution** | How versions are compared and quality regresses |
| **Incident institution** | How errors are replayed, assigned, fixed, and reviewed |

These institutions eventually appear in code, configuration, processes, documents, and organizational meetings. They are less spectacular than model capability, but they decide whether Agents can enter production.

If Shanlan Group only builds a model gateway, business teams will still define tools, logs, and approval rules on their own. There will appear to be a platform, but the institution remains scattered. Real platformization requires these institutions to begin unifying.

**Productizing the platform so business teams want to onboard.**

One common platform-team mistake is designing only from the governance side. Security teams may like the resulting platform, but business teams will avoid it.

A successful Agent platform must be infrastructure, governance system, and product at the same time. It must control risk, but it must also make business teams feel that onboarding is faster, easier, and more likely to succeed.

From the business team's point of view, the key questions are concrete:

| Business-team question | Platform answer |
|---|---|
| I want to build an Agent. Who do I talk to first? | A clear onboarding entry and consultation mechanism |
| What materials do I need? | Task-definition, tool-list, and evaluation templates |
| How long to get the first version running? | A standard onboarding path and reference examples |
| Where will the platform block me? | Public risk levels and approval rules in advance |
| How do we prove value after launch? | Metric definitions, feedback collection, and version evaluation methods |

If the platform team cannot answer these, the business sees the platform as an abstract governance requirement. Platform productization means translating governance into a usable path.

That is why later chapters in this book cover not only Runtime, Registry, and Policy, but also frontends, evaluation, and organizational routes. A platform is not a pile of backend services. It must be understood and adopted by business teams.

**How to control platform "thickness."**

If the platform is too thin, it loses control. If it is too thick, it slows the business. How do we judge the proper thickness?

A simple rule is: the platform should be thick in governance and reuse, and light in business difference.

| Where the platform should become thicker | Where the platform should stay light |
|---|---|
| Model entry, cost, rate limits | Business-specific prompts |
| Tool schema, version, risk level | Business-strategy details |
| Trace, evaluation, approval | Product wording for a specific scenario |
| Identity, permission, tenant isolation | One team's UI preference |
| Runtime state, task recovery | Temporary experiments inside a domain |

Behind this rule is the speed difference between platform and application. Platform capabilities, once established, should be stable, reusable, and auditable. Application capabilities need rapid experimentation, closeness to business, and frequent change. Forcing application speed into platform rhythm makes the business suffer. Putting platform responsibility into application speed makes governance collapse.

The difficulty of a mature platform is holding both speeds at once.

**Non-technical assets an Agent platform needs.**

If you look only at code, a platform looks like a set of services. In real enterprise adoption, it also needs many non-technical assets.

| Non-technical asset | Purpose |
|---|---|
| Glossary | Lets business, platform, data, and security teams use the same language |
| Scenario grading list | Clarifies which scenarios are fit for pilots and which are not yet fit |
| Risk grading specification | Unifies risk judgment for tools and actions |
| Onboarding templates | Reduces preparation cost for new Agents |
| Evaluation sample templates | Moves quality discussion from feelings to samples |
| Postmortem template | Lets errors create learning instead of one-off fixes |

These assets do not emerge automatically from code. The platform team must deliberately build them. Without them, platform promotion is hard to scale. With them, new teams do not restart from zero each time.

This is why the book repeatedly emphasizes shared language. An enterprise Agent platform cannot be understood or advanced by one person alone. Multiple teams need shared judgment standards.

**Platformization is staged evolution, not one big bite.**

Platform construction often fails at two rhythms. One rhythm builds only temporary support for the next pilot, and the temporary solution becomes heavier over time. The other wants to finish the final platform on day one and delivers no usable pilot for months.

A healthier rhythm usually has three stages:

| Time scale | Goal | Minimum delivery |
|---|---|---|
| **30 days** | Support the first production-grade pilot | Runtime, model entry, minimal tool registry, basic trace |
| **90 days** | Establish unified governance foundation | Risk levels, approval channel, cost aggregation, basic evaluation |
| **6-12 months** | Form reusable platform capabilities | Semantic layer, platform admission, organizational mechanism, shared components |

The point is not the exact numbers. The point is the sequence: **make the execution chain controllable first, then make platform capabilities reusable, and only then pursue scale and organization.**

If Shanlan Group wants to move from four successful pilots to the platform stage, it should follow this logic instead of maxing out all capabilities at the beginning.

**Build, buy, or take a hybrid route.**

At a certain stage, every enterprise will discuss a practical question: should we build the platform ourselves or buy a product?

An honest answer is usually: most enterprises end up on a hybrid route.

| Route | Suitable situation | Biggest risk |
|---|---|---|
| **Buy-first** | Need fast start, standardized scenarios, limited internal engineering capacity | Platform boundary is constrained by product; deep integration is hard |
| **Build-first** | Complex business, highly customized data and tool systems, high compliance demands | Long-term investment and organizational complexity are underestimated |
| **Hybrid** | Own key contracts, adopt mature generic capabilities | Without clear architecture governance, neither side goes deep enough |

For a multi-business organization like Shanlan Group, a stable route is often this: use mature solutions for model gateway, basic observability, and some generic components; keep tool contracts, semantic layer, risk levels, approval chains, and platform admission mechanisms in-house. These parts are directly connected to the enterprise's own business and responsibility boundaries.

Another build-vs-buy test is "where differentiation lies." If a capability does not create differentiation and does not carry core responsibility, buying more is reasonable. If a capability directly connects enterprise data, business process, and responsibility boundary, outsourcing it should be approached carefully.

| Capability | Degree of buyability | Reason |
|---|---|---|
| Generic model gateway | High | Mature solutions exist for routing, rate limits, and billing |
| Generic observability dashboard | Medium-high | Start with a product, then add enterprise fields |
| Generic RAG tools | Medium | Base capabilities can be bought, but enterprise knowledge organization must be customized |
| Tool risk grading | Low | Strongly bound to enterprise processes and responsibility |
| Semantic-layer definitions | Low | Directly determine trustworthiness of business answers |
| Agent admission process | Low | Part of enterprise governance institution |

This table does not tell every enterprise to build everything itself. It reminds teams not to buy away core responsibility boundaries.

**The minimum steps for a new Agent to onboard to the platform.**

Once the platform exists, it is not only for existing projects to reuse. It must also answer: how does a new business team onboard?

A truly executable minimum admission process has at least five steps:

| Step | Question to answer |
|---|---|
| **Task definition** | What exactly is this Agent responsible for, and what is it not responsible for? |
| **Tool review** | Which tools will it call, which are read-only, and which have side effects? |
| **Risk grading** | Which actions may execute automatically, and which require confirmation or approval? |
| **Evaluation preparation** | How do we know it is better than the old way, or at least not worse? |
| **Platform integration** | Is it included in the unified Runtime, Gateway, Trace, and Policy? |

These steps look like thresholds, but their essence is cost reduction. The admission process exists not to make business teams wait, but to prevent every new Agent from creating a new pile of technical debt.

From a communication perspective, the five steps also act as a translation layer. They translate "I want an intelligent assistant" into questions the platform team can handle: task boundary, tool list, risk level, acceptance method, and unified runtime path. Without this layer, business and platform teams often speak from entirely different contexts and both feel misunderstood.

**Platform incident review: why missing unified trace is fatal.**

Imagine Shanlan Group's operating-analysis Agent gives an incorrect conclusion: "The decline in East China gross margin mainly comes from excessive promotion discounts in beauty products." The business team adjusts its strategy based on this conclusion. Several days later, they discover that the real cause was an incorrectly included logistics-cost field.

At that point, the platform team must answer a chain of questions:

- Which tables did the Agent query?
- Which metric definition did it use?
- Which model generated the analysis plan?
- Was the SQL checked by the semantic layer?
- Did the explanation cite the wrong field?
- Did the user see any uncertainty warning?
- Could this error affect similar questions?

If every Agent records its own logs, these questions may be impossible to answer. Even if they can be answered, the evidence must be stitched from different systems. The meaning of unified trace lies here: it is not to make the platform look professional. It is to preserve system memory when incidents occur.

Many enterprises do not realize trace is not a "later feature" until the first incident. For Agents that can call tools and influence business judgment, trace is a launch prerequisite.

**Platform metrics: how to know whether the platform itself is good.**

Business Agents have business metrics. Platforms should have platform metrics. Otherwise, platform teams easily prove only that they built many capabilities, not that those capabilities reduced enterprise adoption cost.

| Metric | Meaning |
|---|---|
| Average onboarding cycle for new Agents | Measures whether the platform reduces onboarding cost |
| Tool reuse rate | Measures whether the Registry is truly reused |
| Approval coverage of high-risk actions | Measures whether Policy catches key risks |
| Trace completeness | Measures incident replay capability |
| Evaluation coverage | Measures whether launch quality is quantifiable |
| Average cost per task | Measures whether model and tool calls are governable |
| Business-team satisfaction | Measures whether the platform helps business rather than only adding constraints |

These metrics force platform teams to look at efficiency and governance together. If they look only at efficiency, the platform may lose control. If they look only at governance, no one may use it. A good platform improves both.

**How platform and business teams collaborate.**

Platform boundaries are not drawn only in architecture diagrams. They are drawn in collaboration models. Many enterprise platforms fail not because of weak technology, but because platform and business teams never form a stable cooperation model.

If Shanlan Group's platform team simply says "all of you must onboard to the platform," resistance is likely. Business teams will see the platform as extra process, control, and scheduling bottleneck. If business teams build freely, the platform team loses unified governance. Sustainable collaboration requires clear responsibility separation.

| Work | Business team owns | Platform team owns | Jointly completed |
|---|---|---|---|
| Task definition | Explain goals, deliverables, and business constraints | Provide task templates and review methods | Judge whether the scenario fits Agent |
| Data and knowledge | Provide business definitions, policies, and cases | Connect semantic layer, permissions, and knowledge foundation | Maintain trusted context |
| Tool capability | Propose business actions needed | Define tool contracts, risk levels, versions | Review side-effect boundaries |
| Evaluation and acceptance | Define business success criteria | Provide evaluation methods and regression mechanisms | Build samples and metrics |
| Launch operations | Collect feedback and promote usage | Provide monitoring, trace, and cost views | Review version outcomes regularly |

The core meaning is: the platform team should not define business for the business team, and the business team should not carry platform governance alone. The platform productizes and institutionalizes "how to build Agents" so business teams can enter through the same path.

One workable rhythm is to form "scenario co-creation squads." Each key Agent scenario includes a business owner, product manager, platform architect, data owner, and security representative. The point is not to hold many meetings, but to align task boundaries, data readiness, tool risk, and acceptance criteria early.

For Shanlan Group, the operating-analysis Agent squad might include the operations owner, BI product manager, data-platform architect, Agent-platform architect, and internal-control representative. The quotation Agent squad should add sales management, legal, or commercial-approval roles. Members vary by scenario, but the method should stay consistent.

If the platform team only provides underlying capabilities and does not join early scenario definition, many issues erupt before launch. If it over-enters business details, it becomes another super product team. A good collaboration model lets the platform provide methods and boundaries, the business provide goals and judgment, and both complete a production-ready task chain together.

**Platform governance committee: not for meetings, but for unified decision criteria.**

When an enterprise has only one or two Agent pilots, many decisions can be negotiated inside project teams. When Shanlan Group simultaneously advances operating analysis, quotation, service quality, finance invoices, and knowledge assistants, ad hoc negotiation fails quickly.

A lightweight but formal governance mechanism is needed. It may be called a platform governance committee or AI platform review meeting; the name is not important. It must answer three categories of questions:

| Decision type | Typical questions | Roles involved |
|---|---|---|
| Admission decision | Which Agents may enter production, and which stay pilots? | Platform, business, product, security |
| Risk decision | Which actions require approval, and which must never execute automatically? | Platform, security, legal, internal control |
| Roadmap decision | Which capabilities move into the platform, and which stay in applications? | Platform, architecture, data, business |

The committee's most important value is stable decision criteria. Otherwise, Department A's Agent may send customer emails automatically while Department B cannot even send internal notifications; one scenario has strict trace requirements while another records nothing. Such inconsistency quickly burns platform credibility.

Governance must not become heavy approval for everything. It should focus on cross-scenario, cross-department, responsibility-boundary issues, not every prompt, page, or business wording. The governance committee is not a product review or code review. It is a boundary review for enterprise Agents.

A healthy rhythm is: low-risk scenarios follow the standard admission flow; medium-risk scenarios are reviewed jointly by platform and security; high-risk scenarios enter the governance committee. This controls risk without letting meetings hold every project hostage.

![Platform admission and governance mechanism](images/ch2-3_en.png)

*Figure 2-3 Platform admission and governance mechanism: a new Agent must pass shared gates such as task definition, tool review, risk grading, evaluation preparation, and runtime integration before production monitoring.*

**Three construction routes: framework-first, product-first, and platform-first.**

When enterprises enter the Agent stage, three routes are common.

The first is framework-first. The technical team chooses an Agent framework and quickly builds applications. This starts fast and suits exploration, but it tends to focus attention on "how to orchestrate Agents" while ignoring governance. Engineering teams often feel excited on this path because capability jumps are visible in the short term. But once multiple teams need reuse, they discover that frameworks do not replace permissions, evaluation, trace, admission, and organizational mechanisms.

The second is product-first. The enterprise purchases an Agent Studio, knowledge assistant, or industry product to let the business use something quickly. This is suitable for fast demand validation and organizations with limited internal engineering capacity. Its risk is that platform boundaries become defined by the vendor product, and the enterprise's own tool system, data definitions, and governance institutions may be hard to embed deeply.

The third is platform-first. The enterprise first defines unified model entry, tool contracts, risk grading, trace, and evaluation, then advances scenarios on that basis. This is more stable in the long run, but without business scenarios pulling it forward, it easily becomes an idle technical platform.

| Route | Advantage | Risk | Better fit |
|---|---|---|---|
| Framework-first | Fast exploration, high technical freedom | Later governance debt is expensive | Strong engineering teams in early pilot stage |
| Product-first | Fast business value and low entry barrier | Bound by product limits, insufficient deep governance | Organizations seeking quick start with standardized scenarios |
| Platform-first | Stable long-term governance and reuse | Can idle without scenario traction | Multi-business organizations advancing many Agents in parallel |

For an organization like Shanlan Group, the best route is often not one of the three alone, but "scenario-driven platform-first." The platform is not built behind closed doors. Two or three representative scenarios pull it forward: operating analysis represents data intelligence, quotation represents execution and approval, and service quality represents knowledge and quality management. Platform capabilities consolidate with these scenarios, while insisting on a unified contract when they do.

The difficulty is that the platform team must serve specific scenarios without being captured by them. It must identify common capabilities inside each scenario and turn them into platform contracts, rather than promoting one scenario's special logic into a group-wide standard.

**Platform construction and cost governance: LLM Gateway is only the starting point.**

Many enterprises begin Agent platform work with an LLM Gateway. This is reasonable. If model calls are not unified, cost, rate limits, model selection, and compliance audit will all lose control. But stopping at Gateway is far from enough.

LLM Gateway manages "how models are called." An Agent platform must also manage "why they are called, for whom, for what task, and what action the result enters." Without those questions, cost governance remains crude.

Shanlan Group may encounter this situation: one operating-analysis task queries multiple tables, generates several rounds of analysis, and repeatedly revises a report; the service-quality Agent summarizes tens of thousands of tickets per day; the quotation Agent frequently calls models during sales peaks to generate drafts. Their cost structures are completely different. If the platform only looks at token totals, it is hard to judge where cost is waste and where it is investment.

Meaningful cost governance needs at least four levels:

| Level | Focus | Typical question |
|---|---|---|
| Model level | Tokens, model unit price, routing strategy | Are we using a model that is too strong or too expensive? |
| Task level | Average cost per task | How much does one operating-analysis task cost? |
| Scenario level | Relationship between cost and business benefit | Does daily service quality cost improve inspection coverage? |
| Organization level | Department quota and budget attribution | Which department, Agent, and version consumes the most? |

These levels turn cost governance from "saving tokens" into managing business input-output. A cheaper model may not lower total cost if error and rework increase. An expensive model may not be waste if it sharply reduces human review. The platform must provide that judgment, not simply push down call fees.

Gateway is the cost entry point, not the whole of cost governance. Real Agent cost governance must be considered together with task, scenario, evaluation, and return.

**Quotation Agent onboarding: a sample from requirement to admission.**

To make the platform admission process concrete, consider Shanlan Group's quotation Agent.

The initial business request might be one sentence: "We hope the system can automatically generate quotations based on customer context and give competitive prices." If development starts from this sentence, it is dangerous. The platform team must break it into admission questions.

First, clarify the deliverable. The quotation Agent's deliverable is not "the final quotation." It is "quotation draft + discount rationale + risk warning + approval recommendation." This definition is critical because it positions the system at the draft and recommendation layer, not the external commitment layer.

Second, clarify data and knowledge sources. It needs customer tier, historical contracts, current inventory, regional pricing policies, temporary promotion rules, competitive strategy, and gross-margin floor. These sources must have authoritative systems and update times. A rule that exists only as a sales manager's oral experience cannot be used as hard system evidence.

Third, clarify the tool list. The quotation Agent may need to query CRM, ERP, contract, inventory, and approval systems, but early versions should not directly call customer email-sending tools. It may generate an email draft, but not send it to the customer automatically.

Fourth, clarify risk levels. Querying customer history is read-only and low risk. Generating a quotation draft is reversible writing and low-to-medium risk. Submitting for approval is medium risk. Sending customer quotations is high risk. Bypassing approval or modifying price master data should be prohibited.

Fifth, clarify evaluation samples. Do not rely on a sales manager trying it a few times and liking it. Platform and business teams should prepare historical quotations, abnormal cases, boundary cases, new customers, low inventory, promotion conflicts, excessive discounts, and special contract clauses.

Sixth, clarify launch form. The first stage only generates drafts for internal sales. The second allows approval submission. The third may consider customer-communication templates. Each stage has a clear risk gate.

Organized as an admission table:

| Admission item | Answer for quotation Agent |
|---|---|
| Task positioning | Generate quotation draft, rationale, and approval recommendation |
| Out of scope | Does not directly promise price to customer; does not bypass approval |
| Key data | Customer tier, historical contracts, inventory, pricing policy, promotion rules |
| Tool scope | CRM query, ERP query, contract query, approval draft creation |
| High-risk actions | Customer contact, formal quotation, price master-data modification |
| Human nodes | Discounts above threshold, policy conflict, confirmation before formal send |
| Evaluation samples | Historical quotations, abnormal quotations, boundary discounts, policy-conflict cases |
| Launch strategy | Internal draft first, then approval linkage, then possible external contact |

This sample shows that platform onboarding does not slow business ideas. It turns business ideas into production-ready task systems. Without this step, a quotation Agent may be clever in demos and dangerous in production.

**Three signals of platform success: business, technical, and governance.**

Whether a platform is good cannot be judged only by component lists or the number of business pilots. A more complete view asks whether three signals appear together.

The first is business signal. Do business teams proactively come to the platform? Can new scenarios start faster? Do Agents actually reduce task time, rework, and system switching? If the platform only makes teams fill more forms, wait for schedules, and explain more, the business signal is weak.

The second is technical signal. Are tools reused? Is trace complete? Can evaluation regress? Can model cost be aggregated by task and scenario? If every Agent still wraps tools, records logs, and maintains prompts and evaluations separately, the technical signal is weak.

The third is governance signal. Can the enterprise clearly answer which high-risk actions exist, who approved what, how errors replay, and how versions are taken offline? If security and compliance teams still rely on asking project teams for materials manually, the governance signal is weak.

| Signal type | Strong signal | Weak signal |
|---|---|---|
| Business | Business teams onboard actively; scenario replication speeds up | Business teams bypass platform and run isolated pilots |
| Technical | Unified view of tools, trace, evaluation, and cost | Every project builds its own stack |
| Governance | Shared criteria for risk grading, approval, and incident review | Errors rely on ad hoc questioning and manual stitching |

A mature platform may not have the most capabilities at the beginning, but it must improve all three signals. Improving only business may lose control; improving only technology may become self-entertainment; improving only governance may leave no one willing to use it.

**Common organizational failures in platform roadmaps.**

Finally, we need to discuss an uncomfortable reality: platform failures often fail not in architecture diagrams, but in organizational relationships.

The first failure is that the platform team is too far from the business. It builds a complete capability set without deep connection to real scenarios. The result is many modules that "should exist," but no business team truly onboards. This is a lack of scenario traction.

The second failure is that business teams are too far from the platform. Each department uses its own budget, vendor, and framework to build Agents. Short term, this feels fast. Long term, governance fractures completely. When the group wants to unify cost, permissions, and risk, every project has become its own small system.

The third failure is putting security last. Many projects involve security and compliance only before launch, then high-risk actions, sensitive data, and approval boundaries all need rework. Security is not a gate at release time. It should participate from scenario definition.

The fourth failure is treating the platform team as a pure infrastructure team. An Agent platform needs infrastructure skills, but it also must understand products, data, business processes, and governance institutions. If the platform team only provides APIs and cannot help define task boundaries, it is hard for it to become a real platform.

The fifth failure is lacking a long-term operating mechanism. Launching an Agent is not the end. It is the beginning. Models change, business rules change, metric definitions change, and user behavior changes. Without version review, feedback loops, and evaluation regression, the platform quickly degenerates into a set of unmaintained pilots.

None of these failures means one team "did the wrong thing." They mean the enterprise did not operate the Agent platform as a cross-functional system. Chapter 2 talks about platform boundaries because those boundaries are both technical and organizational.

## Long-Term Platform Operation: Reverse Boundaries, Cost, Catalogs, and Maturity

When defining platform boundaries, many teams only write what the platform "should provide." That is insufficient. A mature platform must also state clearly what it **should not** do. Otherwise the platform keeps expanding until it slows business and takes on responsibilities it should not carry.

First, the platform should not define business goals for business teams. Whether the operating-analysis Agent serves weekly meetings, monthly meetings, or special reviews, and whether the quotation Agent serves key-account sales or channel sales, must be defined by business and product. The platform can provide task templates and review methods, but it cannot decide what matters most.

Second, the platform should not swallow all business rules. Discount strategies, service quality details, reimbursement definitions, and legal clause preferences all have strong domain attributes. The platform may require that these rules connect in a governable way, but should not write them all into the platform core. Otherwise every business change becomes a platform release.

Third, the platform should not force all scenarios into one rhythm. Low-risk exploration needs speed; high-risk production needs stability. The platform should provide graded paths, not one process for all projects.

Fourth, the platform should not replace existing enterprise platforms. Data platforms, identity platforms, approval platforms, and service-governance platforms still have their own responsibilities. The Agent platform should connect and enhance them, not create a parallel universe.

Fifth, the platform should not eliminate experimentation in the name of governance. Early Agent scenarios require trial and error. The platform must protect production boundaries, but leave room for sandboxes, pilots, and low-risk exploration.

| What the platform should not do | What happens if it does | Better boundary |
|---|---|---|
| Define business goals for the business | Platform becomes a business-product team with misplaced responsibility | Platform provides method; business defines goals |
| Swallow all rules | Platform releases are crushed by business change | Platform governs contracts; applications govern domain rules |
| Use one process for all scenarios | Low-risk projects slow down while high-risk projects still escape control | Manage by risk level |
| Replace existing platforms | Duplicate architecture and fractured governance | Consume existing platform capabilities |
| Kill experimentation | Business routes around the platform | Provide sandboxes and layered admission |

This reverse-boundary table matters. A platform is not more mature because it is responsible for more. It is more mature when it knows what it should and should not own.

**Platform operation: the real work begins after launch.**

Many enterprises understand platform construction as "delivering a set of capabilities." But an Agent platform is not a one-time deliverable. It is a long-term operating system.

The reason is simple: the Agent operating environment keeps changing. Model versions change, business rules change, tool interfaces change, metric definitions change, and user behavior changes. An Agent that is stable today may degrade three months later because a promotion rule, metric definition, or model version changed. Without platform operation, the system slowly drifts.

Platform operation includes at least five kinds of work.

The first is scenario operation. The platform team continuously tracks which Agents are used, which scenarios create value, and which needs should be merged or retired. Not every pilot deserves to exist forever; the platform must manage the scenario portfolio.

The second is quality operation. Evaluation samples must be updated, failure cases consolidated, and user feedback classified. Quality is not tested once before launch; it regresses continuously.

The third is cost operation. The platform regularly examines model calls, task cost, department budgets, and benefit relationships. Cost governance should not appear only when bills explode.

The fourth is risk operation. High-risk tools, approval strategies, and sensitive-data access should be reviewed regularly. When business boundaries change, old risk levels may no longer apply.

The fifth is ecosystem operation. Business teams, vendors, and internal developers may all connect to the platform. The platform needs documents, templates, training, examples, and support mechanisms, not only APIs.

| Operation type | Main question | Typical actions |
|---|---|---|
| Scenario operation | Which Agents deserve continued investment? | Usage analysis, value review, scenario retirement |
| Quality operation | Are results continuously trustworthy? | Evaluation regression, failure-sample consolidation |
| Cost operation | Is investment controlled? | Cost aggregation, model-routing optimization |
| Risk operation | Are boundaries still valid? | Risk review, approval policy updates |
| Ecosystem operation | Are teams willing to onboard? | Templates, training, developer support |

If Shanlan Group builds four Agents in the first year and twenty in the second, platform operation becomes more important than platform construction. The question is no longer "do we have capabilities?" but "are so many capabilities still trustworthy, controllable, and worth keeping?"

**Platform catalogs: making capabilities discoverable, understandable, and reusable.**

To reduce onboarding cost, platform capabilities must be discoverable. Many enterprise platform capabilities go unused not because they are worthless, but because business teams do not know what exists, how to use it, or whether they are allowed to use it.

An Agent platform needs a "capability catalog." It is not merely a tool list or developer documentation. It is an asset view for business, product, platform, and security roles.

There should be at least four catalogs.

The first is an Agent scenario catalog. It records Agents already launched or piloted, including task goals, scope, owner, usage metrics, and risk level. It prevents departments from rebuilding similar scenarios repeatedly.

The second is a tool capability catalog. It records which business tools Agents can call, what each tool does, parameter requirements, risk level, and owner. It is the business-readable version of the Tool Registry.

The third is a data and knowledge catalog. It records which metrics, documents, policies, and knowledge bases can be used in Agent scenarios, where authoritative sources are, update frequency, and applicable permissions.

The fourth is a template and evaluation catalog. It records reusable task templates, prompt templates, evaluation sample structures, and launch checklists. It lets new teams avoid starting from zero.

| Catalog type | Audience | Value |
|---|---|---|
| Agent scenario catalog | Management and business teams | Reveals existing construction and reuse opportunities |
| Tool capability catalog | Product, development, security | Clarifies callable actions and risks |
| Data and knowledge catalog | Data and business teams | Clarifies trusted context sources |
| Template and evaluation catalog | Product, platform, business | Reduces onboarding cost for new scenarios |

This catalog may look like documentation work, but it is core platform productization. Without catalogs, platform capability spreads only through personal networks. With catalogs, the platform becomes a usable enterprise asset.

**How vendors and external products connect to the platform.**

Most enterprises will not build all Agent capabilities themselves. Shanlan Group may purchase knowledge-base products, service-quality products, model gateways, or industry solutions. The question is not whether to buy. The question is whether purchased products can enter the unified platform boundary.

When external products connect to the Agent platform, at least six things must be checked.

First, whether they support unified identity and permission. An external product must not bypass the enterprise identity system.

Second, whether they support tool and data-access boundaries. Which enterprise systems and data external products can call must be visible to the platform.

Third, whether they support trace or at least export key runtime records. Otherwise errors cannot be reviewed.

Fourth, whether they can enter the evaluation mechanism. The platform must know whether quality improved after version changes, not merely hear vendor explanations.

Fifth, whether they can enter the cost view. Product fees, model fees, and call fees must be aligned with scenario value.

Sixth, whether the enterprise controls key configuration and governance policies. High-risk actions, sensitive data, and approval boundaries cannot be left entirely to vendor black boxes.

| Integration requirement | If missing |
|---|---|
| Unified identity | Permission bypass and unclear responsibility |
| Data boundary | Sensitive data exposure or misuse |
| Runtime records | Incidents cannot be replayed |
| Evaluation mechanism | Version quality cannot be controlled |
| Cost view | Input-output cannot be explained |
| Governance strategy | Core risk is outsourced to a black box |

This is the real meaning of the hybrid route. It is not simply buying some things and building others. Whether built or bought, everything must enter the same platform contract. Vendor products can become part of the platform ecosystem, but they should not become governance islands.

**Platform budgets: from project budgets to capability budgets.**

Agent platform construction also changes budgeting. Traditional pilots are often funded by project: one budget for operating analysis, one for quotation, one for service quality. This works early, but creates long-term problems: each project pays only for itself, and shared capabilities are hard to fund.

After platformization, enterprises need to move gradually from project budgets to capability budgets.

Project budgets focus on a business outcome: I want to build a quotation Agent, and here is its value. Capability budgets focus on cross-scenario foundations: tool registration, trace, evaluation, semantic layer, model governance, approval integration. These may not serve only one project, but they determine the marginal cost of all future projects.

If Shanlan Group only budgets by project, common contradictions appear. Every business team wants unified trace, but no one wants to pay for the trace platform. Every team wants accurate semantic definitions, but no one wants to fund public metric governance. Every team wants model calls to be cheaper, but no one wants to invest in routing, caching, and evaluation.

A healthier budget structure usually has three parts:

| Budget type | Purpose | Beneficiaries |
|---|---|---|
| Platform foundation budget | Model entry, trace, tool catalog, approval, evaluation foundation | All Agent scenarios |
| Scenario construction budget | Specific Agent applications and business workbenches | Corresponding business departments |
| Operation optimization budget | Quality regression, cost optimization, template consolidation, training | Platform and business together |

This structure lets the platform stop relying entirely on individual projects to "incidentally" build shared capability. It also helps management see that platform investment is not a cost sink; it reduces future Agent onboarding and governance cost.

Capability budgets must still be assessed. A platform cannot claim value merely because it is public. Metrics such as new-Agent onboarding cycle, tool reuse rate, trace completeness, evaluation coverage, and cost per task all evaluate capability budgets.

**Platform maturity: from project support to enterprise operating-system foundation.**

To make the platform roadmap measurable, Agent platform maturity can be divided into five stages.

Stage 0 is project self-build. Each Agent project connects models, tools, logs, and evaluations on its own. This suits exploration but does not scale.

Stage 1 is unified entry. The enterprise has a model gateway, basic permissions, and simple call records. It solves part of cost and onboarding, but does not yet manage task execution.

Stage 2 is unified runtime. Agent task state, tool calls, trace, and approval begin to enter the same platform contract. The enterprise can start answering "what did the system do?"

Stage 3 is unified governance. Risk grading, evaluation regression, cost aggregation, admission process, and incident review become institutions. The enterprise can answer "is the system trustworthy over time?"

Stage 4 is ecosystem platform. Business teams, internal developers, and external vendors can build Agents on the platform; the platform provides catalogs, templates, evaluations, operations, and training. The enterprise can repeatedly copy AI-native scenarios.

| Stage | Name | Typical features | Core question |
|---|---|---|---|
| 0 | Project self-build | Each project does its own thing | Can we make it work? |
| 1 | Unified entry | Model, permission, and call entry begin to unify | Can we control access? |
| 2 | Unified runtime | Tasks, tools, trace, and approval are unified | Can we execute stably? |
| 3 | Unified governance | Evaluation, cost, risk, and admission are unified | Can we trust it long term? |
| 4 | Ecosystem platform | Catalogs, templates, vendors, business co-creation | Can we replicate at scale? |

For Shanlan Group, the realistic first-year target is usually not stage 4. It is moving from stage 1 to stage 2 while laying the foundation for stage 3. In other words: unify entry first, then runtime, then governance. This sequence is more reliable than pursuing a large, complete platform from day one.

**Why the next chapter must discuss AI-native business systems.**

If Chapter 2 stopped at "the platform is shared infrastructure," readers could still understand it as a pile of underlying capabilities.

But the platform ultimately serves not itself, but a new form of business system.

Shanlan Group ultimately needs a platform not because the platform is elegant, but because more business tasks begin to show the same trend:

- Users no longer only want to look up an answer; they want to finish a piece of work;
- Systems no longer assist inside one module; they advance tasks across systems;
- Results are no longer just text outputs; they must enter approval, workflow, archive, and review;
- Responsibility no longer sits in a page feature; it sits in an entire task chain.

This naturally pushes us to Chapter 3: if the platform supports a new class of business system, what does "AI-native business system" actually mean? Where is the boundary between it and "adding AI features to old systems"?

In other words, although Chapter 2 discusses platforms, it mainly prevents readers from treating the platform as a self-contained technology project. The value of a platform is not the platform itself. It is that it lets the enterprise steadily grow a new generation of business systems. Chapter 3 continues from that question: what is fundamentally different about the business form the platform supports?

## Chapter 2 Closing: The Platform Ultimately Serves AI-Native Business Systems

This chapter delivers a platform judgment framework.

First, the enterprise difficulty is not "writing one Agent." It is "managing a group of Agents."

Second, applications, frameworks, and platforms are three different problems. Mixing them distorts later construction goals.

Third, what a platform really manages is the five shared problems of models, data, tools, processes, and governance. Platform boundaries are the consolidation boundaries of those shared problems.

Fourth, the platform must be neither so thin that it is only a model gateway, nor so thick that it swallows business logic. A mature platform constrains strongly where unification is necessary and leaves space where differences should remain.

Fifth, platformization is not technical fastidiousness. It is an organizational problem enterprises inevitably face in the multi-Agent stage.

The next chapter raises the view again: if the platform ultimately serves a new kind of business system, what is the essential difference between an "AI-native business system" and "adding AI features to old systems"?
