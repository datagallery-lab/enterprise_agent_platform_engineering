# Chapter 37 DataAgent Benchmarking and Ecosystem

---

This chapter benchmarks DataAgent-related products and open-source ecosystems, explaining the respective boundaries best suited for BI Copilot, Notebook Agent, semantic layer tools, and analytics workbenches. The product forms in this field are highly differentiated: some excel at data querying, some specialize in notebook collaboration, and some are essentially semantic layers. Directly comparing "which is better" is meaningless; what matters is which segment of the DataAgent workflow they cover. This chapter aligns mainstream open-source solutions like DB-GPT and ChatBI with commercial products across capability dimensions, helping teams decide whether to build in-house, purchase, or combine solutions.

The first five chapters of Part VI respectively define **Product Boundaries** (Chapter 32), **Semantic Layer** (Chapter 33), **NL2SQL** (Chapter 34), **Python Analysis** (Chapter 35), and **Expression and Output Evaluation** (Chapter 36). If readers have followed the complete Run pipeline in [Chapter 32 §4 East China Decline Case](ch32-dataagent.md), they will naturally come to the final question: **With numerous DataAgent / Text-to-SQL products in the industry, should multi-business scenarios build their own, purchase, or adopt a hybrid approach?**

The answer is: **No single product can replace the combination of the Part V platform plus all six chapters of Part VI**, but enterprises do not need to reinvent every wheel from scratch. This chapter explains why the ecosystem is highly fragmented, which capabilities mainstream solutions cover, the boundary between ChatBI and DataAgent, and how to prove continued improvement of chosen solutions using **Evaluation and Business Gold Standard Sets**. This chapter sequentially presents: why the ecosystem is fragmented (§1); open source vs. commercial classifications (§2); comparison of mainstream open source (§3); differences between ChatBI, BI Copilot, and DataAgent (§4); build vs. buy vs. hybrid (§5); evaluation and continuous improvement (§6); enterprise selection checklist and **Part VI summary** (§7).

## 37.1 Why the DataAgent Ecosystem Diverges

Why isn't there a "standard DataAgent product" that can be directly purchased and deployed? The fundamental reason is that **DataAgent must simultaneously meet four distinct types of demand**: conversational entry, Text-to-SQL technology, enterprise deployment compliance, and organizational-level data governance. Most products on the market start from only **one of these axes**, and supplement the other capabilities through integrations or external add-ons. The four differentiation axes are as follows:

*Table 37-1: Typical products and capability gaps along each DataAgent differentiation axis. Source: compiled by the authors.*

| Differentiation Axis | Typical Products | Capability Gaps |
| --- | --- | --- |
| **Entry Point** | ChatBI conversation window | Lacks platform governance (Runtime, Registry, Trace) |
| **Technical Route** | Text-to-SQL libraries (e.g., Vanna, see §2 explanation) | Lacks semantic layer and HITL |
| **Deployment** | SaaS Copilot | Lacks privatization and multi-tenancy |
| **Organization** | Data Middle Platform project | Lacks Agent Runtime and Run six states |

Take retail operations analysis as an example: when the operations director says, "Last week's East China GMV decline top SKUs," it requires at least **Question Frame parsing** (Chapter 32), **Metric binding and disambiguation** (Chapter 33), **read-only SQL execution** (Chapter 34), **category contribution Python scripts** (Chapter 35), and **chart/report approval** (Chapter 36), plus end-to-end **Run auditing and evaluation** (Chapters 37 and 39). Purchasing a "conversational data query" SaaS typically only covers entry and NL2SQL demo; **semantic layer definitions, sandbox analysis, and HITL publication** still need to be built or integrated by the enterprise.

Therefore, product comparison cannot start from a feature list. A more reliable approach is to first list the business workflow: who asks, which metric definitions to use, can follow-up queries be made, is approval required, who receives the report, and who fixes samples after failures. Only after these constraints are clear can Vanna, WrenAI, DB-GPT, Defog, or BI Copilot be positioned appropriately. Otherwise, teams easily buy a demo-strong NL2SQL tool only to find it lacks metric versions, has no `tenant_id` injection, and provides no report-level evidence when deployed.

A survey of LLM/Agent-as-Data-Analyst capabilities classifies Agent abilities as multidimensional combinations including **semantic awareness, toolchain orchestration, and autonomous pipelines** (Tang et al. 2025). Few single products cover all these at once. Common enterprise deployment looks like: **Part V platform (Chapters 22-30) + semantic layer (Chapter 33) + specialized tools (Chapters 34-36)**, unified by a Registry audit, instead of expecting one ChatBI to do everything.

Public benchmarks are also encouraging this shift in understanding. **Spider 2.0** (Lei et al. 2024) and **BIRD-INTERACT** (Huo et al. 2026) move evaluation from "single-sentence SQL translation" toward **enterprise workflows, multi-round clarifications, and interactive error correction**. This aligns with the full chain of **diagnosis + comparison + reporting** defined in Chapter 32 ([§1](ch32-dataagent.md)). Products still stuck on "turning natural language into a single SELECT statement" will inevitably struggle with multi-step analysis Runs like the East China decline example.

### 37.1.1 Product Selection and Integration Risks

**Misconception 1: Deploying a ChatBI is equivalent to deploying a DataAgent platform.**
ChatBI typically represents a **subset of query types** (Chapter 32 §2), lacking `waiting_human` approval chains, Handoff, and cross-Agent orchestration; operational monthly report Runs still rely on Part V Runtime. **Misconception 2: Introducing DB-GPT eliminates the need for Part V.**
**DB-GPT** (eosphoros-ai 2024) is an open-source **Agent application framework** (with built-in Runtime shell and data plugins). If an enterprise already has `core/runtime/` and `core/registry/`, introducing DB-GPT as a whole will create a **dual Runtime** scenario (see Chapter 31 common misconceptions). It is better to **adopt components, not the full platform shell**.

**Misconception 3: High accuracy in NL2SQL demos is sufficient for deployment.**
The East China case shows ambiguity between `gmv_tax_excluded` and `gmv_ops` already at the Linking stage (Chapter 33 §4); without **business gold standard datasets** and **definition footnote evaluations**, deployment complaints about definitions will overshadow SQL syntax accuracy.

---

## 37.2 Open-Source Frameworks and Commercial Products

The tools listed in the table below - **Vanna, WrenAI, DB-GPT**, and others - are **GitHub open-source projects or commercial Copilot products**, not terms coined by this book. Before reading the table, note the **one-line positioning** of each entry.

*Table 37-2: One-line positioning and typical use cases for open-source frameworks and commercial products. Source: compiled by the authors.*

| Name | One-Line Summary | Typical Use Case |
| --- | --- | --- |
| **Vanna** (vanna-ai 2024) | Uses a vector store to retrieve **historical Question-SQL pairs**, RAG-augmented generation | Rapid POC, private schema adaptation |
| **WrenAI** (Canner 2024) | **Semantic layer + conversational BI** | Unified metric modeling and natural-language querying |
| **DB-GPT** (eosphoros-ai 2024) | **Agent application framework** + data plugin templates | Building data apps from scratch (compatible with the Part V dual-runtime architecture) |
| **Defog** (Defog.ai 2024) | Skews toward **Text-to-Python and automated reporting** | Analysis + narrative generation |
| **Sherlock** | **Research-oriented** deep-analysis agent prototype | Reasoning-chain reference; limited enterprise governance |
| **Power BI Copilot** (Microsoft 2024) | **Built-in Copilot** within a BI product | Modifying charts and filters; not a platform-level DataAgent |

### 37.2.1 Ecosystem Map

Mapped along two axes - **library vs. platform** and **NL2SQL vs. full-pipeline** - the mainstream solutions can be roughly positioned as follows:

*Table 37-3: Positioning of each product along the "library/platform" and "NL2SQL/full-pipeline" axes. Source: compiled by the authors.*

| Product | Library/SDK ↔ Platform | NL2SQL ↔ Full-Pipeline | Brief Positioning |
| --- | --- | --- | --- |
| Vanna | Leans library | Leans NL2SQL | Vector retrieval of historical SQL + schema (RAG) |
| Sherlock | Leans library | Leans full-pipeline | Research-oriented deep analysis |
| WrenAI | Middle | Middle | Semantic layer + conversational BI |
| Defog | Middle | Leans full-pipeline | Python analysis and reporting |
| DB-GPT | Leans platform | Leans full-pipeline | Agent application framework |
| Power BI Copilot | Leans platform | Leans NL2SQL | BI-embedded Copilot |
| mini-platform | Leans platform | Full-pipeline | Reference implementation sharing the same lineage as Part V |

*Table 37-4: Representative products by category, their key strengths, and their relationship to mini-platform. Source: compiled by the authors.*

| Category | Representative | Key Strengths | Relationship to mini-platform |
| --- | --- | --- | --- |
| **Open-source platform** | DB-GPT (eosphoros-ai 2024) | Agent framework + data app templates | Maps to `core/runtime/` + data plugins; avoid duplicating the runtime |
| **Semantic layer + NL2SQL** | WrenAI (Canner 2024) | Metric modeling + conversational BI | Maps to `infra/semantic_layer/`; integrated via Registry HTTP proxy |
| **Question-SQL retrieval augmentation** | Vanna (vanna-ai 2024) | Vector retrieval of **historical Question-SQL pairs** and schema fragments | Can be wrapped as the backend training pipeline for `tools/sql_executor/` |
| **Python analysis agent** | Defog (Defog.ai 2024) | Text-to-Python, reporting | Maps to `tools/python_sandbox/` + `tools/chart_renderer/` |
| **Research / deep agent** | Sherlock | Complex reasoning experiments | Used only as a Planner reasoning-chain reference; no enterprise Registry |
| **Commercial BI Copilot** | Power BI Copilot (Microsoft 2024) | Embedded BI, low barrier to entry | **Coexists** with DataAgent; metric definitions aligned through the semantic layer |
| **Book reference** | mini-platform | Shares lineage with the Part V platform | Module paths for Part VI chapters are listed in §7 |

---

## 37.3 Comparison of mainstream open source solutions

Section 37.2 explains what each open source project is. This section answers which chapters of Part VI they cover and how they correspond to the mini-platform modules.

*Table 37-5: Comparison of DB-GPT, Vanna, WrenAI, and other open source solutions by capability dimension. Source: compiled by this book.*

| Capability / Chapter | DB-GPT | Vanna | WrenAI | Defog | Sherlock | mini-platform (book modules) |
| --- | --- | --- | --- | --- | --- | --- |
| Agent Runtime (Chapter 22) | Own | None | Partial | Partial | Experimental | ✓ `core/runtime/` |
| Tool Registry (Chapter 23) | Partial | None | Partial | Partial | None | ✓ `core/registry/` |
| Semantic Layer (Chapter 33) | Connectable | Weak | **Strong** | Medium | Weak | `infra/semantic_layer/` · `agents/data_agent/linker.py` |
| NL2SQL (Chapter 34) | ✓ | **Strong** | ✓ | Medium | Medium | `tools/sql_executor/` |
| Python Sandbox (Chapter 35) | ✓ | Weak | Weak | **Strong** | Medium | `tools/python_sandbox/` |
| Reports / Charts (Chapter 36) | Partial | Weak | Medium | **Strong** | Medium | `tools/chart_renderer/` · `agents/data_agent/templates/` |
| HITL / Multi-Tenancy | Weak | Weak | Medium | Medium | Weak | ✓ Part V Run chain · `core/policy/` |
| Enterprise Eval (Chapters 36-39) | Partial | Weak | Medium | Medium | Experimental | `core/eval/` · Chapter 39 |

!!! note "mini-platform Implementation Status"
    Part V modules in the table (`core/runtime/`, `core/registry/`, etc.) and `mini-platform/projects/multi-agent-workflow/` **already exist in the repo**.
    Part VI columns (`tools/sql_executor/`, `tools/python_sandbox/`, `infra/semantic_layer/client.py`, etc.) represent **book target contracts**, integrated iteratively with Part VI engineering; the selection evaluation should be considered proofs of concept only and not assume full directory presence in the repo.

*Capability ratings represent directional comparison, not version scores (verified June 2025).*

### 37.3.1 Key Points for Selecting Each Solution

**Vanna** (vanna-ai 2024) excels at **vector retrieval of historical SQL plus table schema fragments (RAG, retrieval-augmented generation)**, making it suitable for **POC and quick adaptation to private schemas**. In the East China case, using only Vanna can generate Top SKU queries quickly, but **GMV ambiguity disambiguation** (`gmv_ops` vs `gmv_tax_excluded`) and **view-level permission** require integration with `infra/semantic_layer/` and `core/policy/`; otherwise, it is hard to go into production.

**WrenAI** (Canner 2024) emphasizes the **semantic layer + conversational BI (GenBI, i.e., natural language driven charts/analytics)**, closely aligned with the route of Chapter 33. The `sales_ops` view and metric versioning strategy can be directly analogized. WrenAI still requires enterprise `core/runtime/` and Chapter 30 HITL integration; multi-Agent governance should not run parallel to Part V dual tracks.

**DB-GPT** (eosphoros-ai 2024) provides **Agent application shells and data plugins**. If the enterprise already has the platform from Chapters 22 to 30, a safer approach is: **register NL2SQL training or plugin logic as Tools via the Registry**, instead of introducing a second Runtime (consistent with the framework conclusions in [Chapter 31](../../part05-agent-capabilities/en/ch31.md)).

**Defog** (Defog.ai 2024) focuses on **Text-to-Python and automated reporting**, overlapping strongly with the Chapter 35-36 `python_sandbox` + `chart_renderer` combination. The East China business decline analysis scenario's **category contribution step** corresponds to Defog's strengths; data retrieval should still route through the read-only `sql_executor` chain.

**Sherlock** is a **research-oriented deep analysis Agent** prototype, valuable for complex reasoning chain design, but **mostly lacks enterprise-grade Runtime, row-level permissions, and Eval pipelines**. It is not recommended to fully replace the Part V platform; its Planner multi-step reasoning strategy can be referenced, but engineering implementation should return to `core/planner/`.

When comparing open source solutions, the operational responsibilities after integration are the easiest to underestimate. Introducing a second Runtime fragments Tracing; bypassing the enterprise semantic layer fragments metric definitions; allowing vendor tools to execute SQL directly fragments Policy responsibilities. The comparison table only shows capability coverage and cannot replace architectural judgment. Any external component entering the production chain should first be wrapped as a Registry Tool to undergo the same audit, permission control, cost, and Eval rules.

!!! note "Comparison ≠ Procurement Recommendation"
    The above table reflects current community versions; selection requires **proof of concept** and **security audit**. This chapter only provides **capability mapping** and mini-platform module correspondence.

---

## 37.4 Product Differences Among ChatBI, BI Copilot, and DataAgent

These three product types have similar names but distinct responsibility boundaries:

*Table 37-6: Differences among ChatBI, BI Copilot, and DataAgent. Source: Compiled by the authors.*

| Dimension            | ChatBI               | BI Copilot (Microsoft 2024)         | DataAgent (This Book)                          |
|----------------------|----------------------|------------------------------------|------------------------------------------------|
| Positioning          | Conversational querying | Embedded BI assistant               | Platform-hosted data task agent                 |
| Semantic Layer       | Uncertain            | Depends on BI datasets              | **Mandatory** Chapter 33 · `infra/semantic_layer/` |
| Multi-step Analysis  | Weak                 | Medium                            | Planner chain Chapters 34-36 · `sql_executor` -> `python_sandbox` -> `chart_renderer` |
| Approval             | Usually unsupported  | Usually unsupported                | HITL Chapter 30 · Report-level `waiting_human` |
| Integration with ERP/Agent Orchestration | Weak     | Weak                              | Handoff Chapter 28 · `agents/data_agent/`       |
| Evaluation           | Vendor-dependent     | Vendor-dependent                   | Spider 2.0 / BIRD-INTERACT + business gold standard set · `core/eval/` |

**ChatBI** is suited for scenarios involving "single-turn data queries, small user scale, and low compliance requirements"; once **multi-turn clarifications, Python analysis, report approval, and run audit** are needed, the use case shifts into the DataAgent domain (Chapter 32 Four Product Forms). **BI Copilot** lowers the operation barrier for existing BI users, but its **definitions are locked within the BI dataset**, making it difficult to serve as a group-level **authoritative source of metrics**. The industry scenario strategy is: **Tableau Copilot serves as analyst assistance** (inventory, fixed dashboards); **DataAgent handles business querying and monthly report run chains** (Eastern China decline diagnosis, Controller approval and publication). Both can **coexist**, but their data definitions must be **unified at the semantic layer** `infra/semantic_layer/models/` (Chapter 33 Operational Analysis Example) to avoid conflicting GMVs between Copilot and Agent.

---

## 37.5 Self-Development, Procurement, and Hybrid Approaches

### 37.5.1 Four Approaches and Their Applicable Scenarios

*Table 37-7: Applicable scenarios and risks of the four approaches including self-building and procurement. Source: Compiled by the author.*

| Approach | Applicable Scenario | Risks |
| --- | --- | --- |
| **Procure SaaS ChatBI** | Need fast deployment, few users, acceptable data export | Data scope uncontrollable, difficult to integrate HITL and Eval |
| **Procure + Self-Built Semantic Layer** | Have middle platform and Cube/dbt foundation | High integration cost of two separate platforms |
| **Hybrid: Platform Self-Development + Components** | Have Part V team ⭐ | Requires architectural discipline, forbids dual Runtime |
| **Fully Self-Developed** | Strong compliance, long-term ROI, deep customization | Slow initial delivery |

These conclusions align with the framework in [Chapter 31](../../part05-agent-capabilities/en/ch31.md): **Runtime / Registry / Obs should be self-developed or unified within Part V**; **NL2SQL can connect to Vanna training pipeline**, packaged as backend capabilities under `tools/sql_executor/`; **Semantic layer can use Cube or Wren engine**, unified by `infra/semantic_layer/client.py` exposing `resolve_metric()` and `compile_query()` interfaces. External components are **called via Registry's HTTP proxy** (unified audit, unified tracing), not by business code directly calling third-party SDKs.

This scenario is suitable for a **hybrid approach**: Part V and DataAgent applications (`agents/data_agent/`) are self-developed; semantic layer is based on Cube-style YAML hosted under `infra/semantic_layer/models/`; NL2SQL can leverage Vanna's question-SQL retrieval enhanced `sql_executor` generation phase, but **execution and Policy must not be outsourced**.

Organizational roles should also be reflected in the selection plan. Platform team is responsible for Runtime, Registry, Trace, Policy, and Eval pipelines; Data team handles semantic layer, metric versioning, sample sets, and lineage; Business teams handle gold-standard question formulation, report acceptance, and feedback adoption. Procuring components may reduce implementation cost in some sections but cannot replace these responsibilities. Without clear ownership, system errors become a back-and-forth blame game between "model issues", "data issues", and "vendor issues."

### 37.5.2 Design Trade-offs

*Table 37-8: Two trade-offs for several key DataAgent design decisions. Source: Compiled by the author.*

| Decision | Option A | Option B |
| --- | --- | --- |
| NL2SQL Engine | Self-developed Planner + Gateway + `sql_executor` | Vanna training + packaged as Registry Tool |
| Semantic Layer | Cube / Wren open source engine | Fully self-developed YAML under `infra/semantic_layer/models/` |
| Frontend | Self-developed Generative UI (Chapter 48) | Embedded Power BI Copilot, semantic layer updates for scope consistency |
| Python Analysis | Self-developed sandbox `tools/python_sandbox/` | Inspired by Defog report template, sandbox still self-developed |

**Bottom line for procurement decisions**: Any introduced solution must not bypass the triad of **`tenant_id` injection, read-only execution, and `metric_id@version` audit** (see Chapter 34 §5); otherwise, a case like East China could pass in demo environments but fail security review in production.

---

## 37.6 Evaluation and Continuous Improvement

Selection answers the question "What to buy"; evaluation answers "Did it improve after buying/building?" DataAgent's evaluation must run **public benchmarks plus business gold standard datasets** in parallel. The former ensures technical regression testing, while the latter ensures **alignment of definitions and narratives** with real business queries.

### 37.6.1 Offline Evaluation

Public datasets like **Spider 2.0**, **BIRD**, and **BIRD-INTERACT** are used for technical regression; see [Chapter 32 §1](ch32-dataagent.md) for details. The **business gold standard dataset** is used to ensure definition and narrative consistency; these two are not interchangeable.

*Table 37-9: DataAgent offline evaluation datasets and related modules. Source: This book.*

| Level | Dataset | Chapter | mini-platform |
| --- | --- | --- | --- |
| SQL correctness | BIRD, Spider 2.0 (Lei et al. 2024) | Chapter 39 | `core/eval/` SQL subset |
| Multi-turn interaction | BIRD-INTERACT (Huo et al. 2026) | Chapter 39 | Clarification / ASK scenario replay |
| Insights and reports | Business gold standard dataset (≥50 items) | Chapter 36 §6 | Definition footnotes, EvidenceRef coverage |

The business gold standard dataset should include East China decline **variant query forms** (e.g., "sales revenue" vs. "GMV", "East China" vs. "Su-Wan region"), with each labeled for expected `metric_id@version` and whether HITL (human-in-the-loop) was triggered. Failed evaluation samples immediately feed back to `infra/semantic_layer/` Glossary and Prompt versions.

### 37.6.2 Online Metrics

*Table 37-10: Uses and related modules of DataAgent online metrics. Source: This book.*

| Metric | Use | Related Module |
| --- | --- | --- |
| First-query resolution rate | Product usability | Run Trace · Chapter 38 |
| Definition complaint rate | Semantic layer quality | `infra/semantic_layer/` changelog |
| Approval pass rate | Report / HITL quality | Chapter 30 · `agents/data_agent/templates/` |
| Run cost | Capacity and model selection | Chapter 41 |

**Continuous improvement loop**: Failed eval samples -> semantic layer / Glossary revision -> Prompt / Tool version bump -> regression (Liu et al. 2025). Similar to the "framework benchmarking iteration" in Chapter 31, DataAgent iteration focuses mainly on business samples, with public benchmarks as secondary. Spider 2.0 high scores but missing East China case definition footnotes still count as a release blocker.

Failed samples must enter a clear queue. For definition binding issues, prioritize fixing Glossary, Metric aliases, or View permissions; for SQL structural errors, revisit schema linking, historical Question-SQL pairs, or `sql_executor` validation; for missing chart fields, fix `chart_renderer` spec validation; for report wording exaggerations or missing EvidenceRef, revise templates and output evaluation. This approach is slower than generally "optimizing prompts," but each change has clear ownership and explains why the next version is better. [Chapter 39](../../part07-observability-eval/en/ch39-dataagent-eval-benchmark.md) and **Chapter 50** provide **platform-level** evaluation and policy automation; Part VI emphasizes: **business samples must not rely only on public benchmarks as substitutes**.

---

## 37.7 Enterprise selection ultimately lands on responsibility boundaries

### 37.7.1 Selection conclusions must identify the accountable owner

The final selection decision should not stop at "which product has which feature." It must name who owns Runtime, Registry, semantic definitions, SQL execution, Python analysis, report approval, evaluation samples, and incident repair. A vendor tool can cover some functions, but it cannot own enterprise accountability for data definitions, permission boundaries, audit evidence, or business acceptance. For CTOs and data leaders, the following checklist is therefore a responsibility checklist as much as a capability checklist. **Capabilities and Architecture**

- [ ] Is a **semantic layer enforced**, forbidding Agents from long-term direct access to physical tables? (`infra/semantic_layer/`)
- [ ] Is there an **Agent Runtime + Registry + Trace** (Part V) instead of just a Chat UI? (`core/runtime/` · `core/registry/`)
- [ ] Is NL2SQL implemented as **read-only + tenant injection + auditing**? (`tools/sql_executor/` · `core/policy/`)
- [ ] Does complex analysis run in a **sandboxed Python environment** instead of unconventional SQL workarounds? (`tools/python_sandbox/`)
- [ ] Are external reports supported with **HITL (Human-In-The-Loop) + evidence**? (Chapter 30 · `agents/data_agent/templates/`)

**Evaluation and Operations**

- [ ] Is online sampling done in **Spider 2.0 / BIRD-INTERACT style** scenarios (Lei et al. 2024; Huo et al. 2026)?
- [ ] Is there a **business gold standard question set** (≥50 items, including ambiguity variants)?
- [ ] Are **adoption rates, complaint about definitions, and negative user feedback** tracked? (`core/eval/`)

**Vendors / Open Source**

- [ ] Does privatization and data residency meet compliance requirements?
- [ ] What is the integration cost with existing Cube / dbt / BI tools?
- [ ] Will it cause **dual runtimes clashing with Part V**? (See Chapter 31)

### 37.7.2 Walkthrough: The "East China Decline" Case Across Six Part VI Chapters

Below repeats the exact phrase from [Chapter 32 §4](ch32-dataagent.md) by the operations director: "Sales in East China last week declined significantly vs. the prior week. What are the main SKUs? Does it relate to category structure?"

*Table 37-11: The "East China Decline" case across Part VI six chapters' steps and modules. Source: compiled from this book.*

| Chapter | What this step does (in plain language) | Mini-platform Module |
| --- | --- | --- |
| **Chapter 32** | Parse original phrase into a Question Frame: diagnosis task, East China, last week vs prior week, by SKU | `agents/data_agent/` |
| **Chapter 33** | Bind "GMV" to `gmv_ops@2025Q1`, expand "East China" as `EAST`, output compilable Linked Schema | `infra/semantic_layer/` · `linker.py` |
| **Chapter 34** | Compile Semantic SQL, add `tenant_id` on server side, read-only execute, take top SKU wide table | `tools/sql_executor/` |
| **Chapter 35** | Read SQL result file, calculate each category's contribution to decline gap | `tools/python_sandbox/` |
| **Chapter 36** | Draw SKU contribution bar chart, draft business meeting report, get approval and publish | `chart_renderer/` · `templates/` |
| **Chapter 37** | Use business gold standard set plus open-source benchmarks for Eval, drive glossary/prompt improvements | `core/eval/` |

All six chapters connect one **single Run** (e.g. `run-8f3a`): Chapters 32-33 complete understanding and Linking before Planner starts; Chapters 34-36 sequentially call Tools inside Planner loop; Chapter 37 defines **post-launch Eval to prove improvement over last quarter**, and constraints on introducing components like Vanna / Wren in the next version.

## 37.8 Platform responsibility in ecosystem benchmarking

External tools should enter the platform through explicit contracts. A product may supply NL2SQL training, semantic modeling, chart drafting, or Python analysis, but production execution still needs tenant injection, read-only control, Trace, policy enforcement, evaluation, and HITL where required. If an integration bypasses these controls, the enterprise gains a demo capability while weakening the platform.

The platform team should convert each ecosystem comparison into a responsibility map: which component is reused, which interface wraps it, which data leaves the trust boundary, which evidence is recorded, and which owner handles failures. This keeps benchmarking connected to implementation instead of turning it into a feature matrix.

*Table 37-12: Code paths, responsibilities, and main chapters for Part VI modules. Source: compiled from this book.*

| Module Path | Responsibility | Main Chapters |
| --- | --- | --- |
| `agents/data_agent/` | AgentSpec, Question Frame, Linker | Chapters 32-33 |
| `infra/semantic_layer/` | Metrics, Views, Definition Parsing, `trusted_context()` | Chapter 33 |
| `tools/sql_executor/` | Read-only SQL, validation, execution | Chapter 34 |
| `tools/python_sandbox/` | Analysis sandbox, contribution calculation | Chapter 35 |
| `tools/chart_renderer/` | Chart specifications and rendering | Chapter 36 |
| `agents/data_agent/templates/` | Report templates, EvidenceRef | Chapter 36 |
| `core/policy/` | Row-level permissions, data masking (baseline at execution side in `sql_executor`) | Chapters 34 + 50 |
| `core/eval/` | Output quality evaluation pipeline | Chapters 36 + 39 |

**Recommended Reading Order**: Chapter 32 (Product Boundary) -> Chapter 33 (Semantic Layer) -> Chapter 34 (NL2SQL) -> Chapter 35 (Python) -> Chapter 36 (Expression and Eval) -> Chapter 37 (this chapter). Run / Registry / HITL foundational components are in Part V ([Chapters 22-30](../../part05-agent-capabilities/en/ch22-agent-runtime.md)).

## 37.9 Continuous evaluation after selection

Selection is only the first gate. After a component enters the DataAgent chain, the platform should evaluate it through business gold standard questions, public benchmark subsets, online feedback, definition complaints, approval pass rates, and cost traces. Improvement must be measurable at the Run level, also inside a vendor console.

Failed samples should flow back to the responsible layer. Definition errors update the semantic layer and glossary; SQL errors update schema linking and validation; Python analysis failures update sandbox templates; report wording and missing evidence update output evaluation. Continuous evaluation protects the platform from assuming that a purchased or open-source component remains correct as data, metrics, and business language evolve.

The progression of Part VI's six chapters: **Chapter 32 -> Chapter 33 -> Chapter 34 -> Chapter 35 -> Chapter 36 -> Chapter 37**. First define product boundaries and Question Frame, then semantic layer and NL2SQL, followed by Python analysis and expression-layer Eval, and finally ecosystem selection. Execution and approval from Chapter 34 to 36 rely on Part V's Runtime, Registry, and HITL (see recommended reading order above).

*Table 37-13: One-sentence summary of core capabilities in Part VI's six chapters. Source: compiled from this book.*

| Chapter | One Sentence Summary |
| --- | --- |
| **32** | DataAgent ≠ NL2SQL; four product forms and Question Frame |
| **33** | Foundation of definitions and Schema Linking |
| **34** | Secure SQL, validation, and self-healing |
| **35** | Sandboxed Python cooperating with SQL |
| **36** | Insights, charts, reports, and output evaluation |
| **37** | Ecosystem benchmarking, selection, and continuous improvement |

**Next Steps**: Part VII [Chapter 39](../../part07-observability-eval/en/ch39-dataagent-eval-benchmark.md) builds the **evaluation pipeline** (`core/eval/`); Part IX [Chapter 48](../../part09-frontend-multimodal/en/ch48-generative-ui.md) enhances **Generative UI**, continuing Chapter 36's front-end rendering for charts and reports.

## 37.10 Composition route for ecosystem capabilities

The practical route is usually composition. Enterprises keep the platform spine, then selectively introduce ecosystem components where they provide leverage: Vanna-like question-SQL retrieval can support NL2SQL generation, WrenAI or Cube-style semantic modeling can inform metric services, Defog-like analysis patterns can inspire Python report templates, and BI Copilot can coexist with governed dashboards. The composition must still pass through Registry, Policy, Trace, and Eval. Composition also requires exit paths. If a component becomes too costly, fails compliance review, or cannot support business samples, the platform should know how to replace it without rewriting the whole DataAgent chain. Stable internal contracts are the reason this is possible.

## 37.11 Review method for benchmarking conclusions

Benchmarking conclusions should be reviewed like architecture decisions. Each conclusion needs evidence: tested data scope, sample set, security boundary, latency and cost results, integration assumptions, failure cases, and the owner responsible after launch. A conclusion based only on demos, public claims, or a single benchmark score should not drive production selection.

Reviewers should also check whether the comparison language is grounded. The goal is not to declare a winner across unlike products, but to determine which capability enters which part of the platform, under which contract, and with which rollback path. That makes ecosystem benchmarking useful for engineering decisions instead of procurement slides.

---

## 37.12 Annual Review and Replacement Path for Ecosystem Choices

The DataAgent ecosystem changes quickly, so annual review should be part of selection. Open-source projects may add semantic-layer support, introduce new connectors, or stop maintenance. Commercial products may change pricing, log export, private-deployment strategy, or data residency terms. Internal platforms also change boundaries as Runtime, Registry, Trace, and Eval mature. A selection conclusion describes conditions at one point in time; it cannot replace ongoing review.

Review should first check whether platform assets remain under enterprise control. Business gold-standard samples, semantic-layer definitions, SQL generation records, user feedback, Trace, report templates, and evaluation results should ideally exist outside one vendor. If these assets are locked inside an external product, replacement becomes hard. Enterprises can buy interaction experience, SQL generation, or reporting capability, but evidence assets should be exportable, replayable, and portable. A successful product with locked evidence raises future migration cost.

Replacement paths should be designed early. If an external NL2SQL component degrades, the platform should be able to switch back to an internal executor or another Registry Tool. If a BI Copilot cannot export logs, the platform should limit its participation in high-risk reports. If an open-source framework stops being maintained, the platform should still keep ToolSpec, semantic layer, and evaluation samples so the business chain does not fail as a whole. Replacement may not happen immediately, but interfaces and evidence need to be ready.

Annual review should also inspect collaboration. Procurement teams care about contracts and price. Data teams care about semantic layer and permissions. Platform teams care about Trace, Registry, and SLO. Business teams care about adoption and report quality. Security and compliance teams care about data egress and audit. The conclusion should state which capabilities remain outsourced next year, which move into the internal platform, which stay paused, and which leave the default candidate set. Ecosystem selection then becomes part of the platform roadmap instead of a one-time purchasing decision.

## 37.13 DataAgent Operating Review And Mainline Write-Back

DataAgent review after launch should return to the whole task chain. A failed analytics question may come from semantic-layer definitions, NL2SQL generation, permission filtering, query execution, Python computation, chart explanation, report language, or frontend interaction. If review only checks whether the final answer was correct, the team misses many platform issues: users misunderstood metric names, SQL executed but scanned too much data, chart conclusions lacked EvidenceRef, permissions changed during report publication, or human-review comments never returned to evaluation sets. DataAgent is valuable because it connects these issues through one evidence chain.

Review material should preserve task goal, user role, semantic-layer version, generated SQL, execution plan, result summary, Python code snippet, chart specification, EvidenceRef, human edits, and publication action. For sensitive fields, field-level fingerprints and masked summaries can be stored, but the source of error must remain explainable. Each review should produce a write-back action: semantic-layer definitions are refined, evaluation sets receive new samples, permission policy gains a boundary, report templates add evidence prompts, or frontend components improve abnormal-path copy. A review without write-back is only an incident record and does not make the next DataAgent run more stable.

Mainline write-back also serves the book structure. Chapter 33 explains the semantic layer. Chapter 34 explains NL2SQL. Chapter 35 explains Python execution. Chapter 36 explains report expression. Chapter 38 explains Trace. Chapter 39 explains Eval. Chapter 37 should review these capabilities from one operating perspective, so readers see a verifiable, recoverable, and improvable analytics chain instead of several adjacent data functions. This is what makes DataAgent the mainline of the book.

## 37.14 Business Acceptance Samples For DataAgent

DataAgent business acceptance should not stop at successful SQL execution. Business users care whether the metric is correct, the explanation is trustworthy, the chart communicates clearly, and the report can enter a meeting or approval flow. Acceptance samples should include real question, business context, expected metric, acceptable definition, rejected wrong definitions, chart requirements, evidence requirements, and human-review criteria. The platform can then judge whether DataAgent supports real business work.

Acceptance samples should cover disputed scenarios. Mixing sales amount and collected cash, mixing calendar month and fiscal month, changing customer ownership, outliers affecting trends, permission causing missing data, and empty results with different causes all test DataAgent better than ordinary queries. Each sample should state whether the system should clarify, refuse, degrade, or generate a report. If the system gives a direct conclusion under a disputed definition, semantic layer, prompt, or approval boundary still needs work.

Business acceptance should write back to the platform roadmap. If samples repeatedly fail on metric explanation, semantic-layer work should move first. If they fail on query performance, data products and OLAP need work. If they fail on expression, report templates and EvidenceRef need repair. If they fail on permission, policy and user copy need improvement. DataAgent's mainline value is connecting business acceptance with platform construction.

## 37.15 Replacement rehearsal after ecosystem selection

DataAgent ecosystem selection should discuss replacement as well as adoption. Open-source frameworks, commercial products, semantic-layer components, NL2SQL modules, and visualization components may be replaced because of cost, quality, compliance, maintenance, or vendor changes. If the replacement path is not designed at the beginning, the platform can become tied to one tool's state model, configuration format, or data store, and migration cost will grow.

Replacement rehearsal can start from a low-risk path. The team selects a typical data-question task and records question, semantic-layer input, SQL, execution result, report artifact, Trace, and evaluation sample. The candidate solution then runs the same path. The comparison should focus less on whether the candidate produces a prettier answer and more on whether interface contracts, error types, permission trimming, evidence records, and rollback method remain compatible. If Trace breaks or permission semantics change, an adapter should come before replacement.

A first version of ecosystem governance can require every external capability to have an exit note: how data is exported, how configuration migrates, how historical Runs are retained, how evaluation samples are reused, and how user entry points switch. Ecosystem selection then becomes steadier, and the platform keeps room to move when the technical route changes.

## 37.16 Canary admission samples for ecosystem components

Before an ecosystem component enters the DataAgent chain, it should pass canary admission samples. These samples are different from general benchmarks. They check whether the component can fit the enterprise runtime model. The set should cover at least four task classes: normal data questions, definition disputes, permission boundaries, and failure recovery. Normal questions verify that the component can handle core metrics. Definition disputes verify that it does not silently choose among several Metrics. Permission-boundary samples verify tenant, role, and data-domain controls. Failure-recovery samples verify whether SQL errors, empty results, timeouts, and weak evidence can return state to Runtime.

Admission samples should match component responsibility. If the introduced component is NL2SQL, samples should inspect Linked Schema, read-only SQL, cost thresholds, error codes, and SQL artifacts. If it is a semantic-layer component, samples should inspect Metric version, dimension mapping, alias conflict, and deprecated definitions. If it is a report or visualization component, samples should inspect chart citations, EvidenceRef, publication state, and human review. Each component must prove that its results can write back to Trace and Eval. Success inside a vendor console is not enough.

Canary also needs exit conditions. Good performance on low-risk samples does not qualify a component for every business domain. If permission-denial samples fail, semantic versions cannot be exported, Trace cannot be connected, error codes cannot be mapped, or ownership is unclear, the component should stay in pilot. Even after admission, it should not enter default routing immediately. The platform can limit tenant, data domain, question type, and call volume while observing failed samples and user corrections. Scope can widen only after the component keeps stable evidence under real traffic.

Admission samples change the way ecosystem benchmarking should be written. Chapter 37 should compare product functions together with the samples a product must pass before entering enterprise DataAgent. Readers can then compare procurement demos, open-source trials, and internal development under one evidence standard. A component enters DataAgent because it can carry enterprise definitions, permissions, runtime evidence, and rollback responsibility, not because the demo looks fluent.

## 37.17 Runtime cost attribution for ecosystem composition

Cost attribution becomes harder after DataAgent combines ecosystem components. One user question may call the semantic layer, NL2SQL, OLAP engine, Python sandbox, chart generation, report templates, and an LLM judge. If the platform counts only the final model call, it underestimates real consumption. If it counts only data-query cost, it misses retries, human review, and report rewriting. After ecosystem selection enters production, cost should be attributed along the task path.

Cost attribution should cover component, tenant, task type, and failure path. Component-level attribution shows which ecosystem capability is expensive. Tenant-level attribution supports quota and billing. Task-type attribution helps decide which scenarios fit synchronous answers and which should move to asynchronous reports. Failure-path attribution exposes cases where failure is expensive, such as repeated SQL repair, chart redraws, or report rejection. Without these splits, teams tend to blame model price while the real bottleneck may sit in data scanning, sandbox execution, or report rework.

Runtime cost should be read together with quality evidence. A low-cost component that often produces wrong SQL or unverifiable charts can create downstream human cost. A higher-cost component that reduces human review and meeting disputes may fit high-value scenarios. DataAgent selection should compare task-completion cost, dispute-handling cost, replacement cost, and per-call price together. This makes self-development, procurement, and hybrid routes closer to production reality.

A first version can keep a cost ledger for core data-question tasks. The ledger records user question, component calls, query scan, model call, sandbox execution, report generation, human review, and final acceptance. After each ecosystem-component change, the same task set compares cost and quality. Chapter 37's ecosystem benchmarking then lands in runtime economics instead of feature lists and demos.

## 37.18 Business attribution for DataAgent operating cost

DataAgent cost spans several systems: model calls, SQL queries, vector retrieval, Python sandbox, report generation, cache, Trace storage, and human review. If cost is summarized only at the infrastructure layer, business teams see a total bill but cannot decide which tasks deserve optimization, which should be limited, and which should move to async execution. Operating cost should return to business tasks and user commitments.

Cost attribution should aggregate by Run. Each DataAgent task records model tokens, tool-call count, query time, scanned data volume, Python execution resources, artifact storage, human review, and failed retries. The platform then aggregates by tenant, business line, task type, and artifact type. Teams can see whether one report type is costly because data scans are large, context is long, retries are frequent, or human review dominates.

A first version can emit a cost summary for DataAgent. Users do not need a detailed bill in every answer, but business owners and platform teams need unit cost, success rate, and adoption for each task class. A high-cost task with low adoption should be optimized or retired. A high-cost task that supports a key process should receive budget and approval. Cost governance is not about lowering every call. It is about explaining resource use against business value.

## 37.19 Validation window after replacing ecosystem components

After DataAgent ecosystem components reaches production, a successful demo is not enough evidence. The platform needs stable fields for replacement rationale, compatibility scope, sample replay, cost movement, missing capability, and rollback conditions, and those fields should connect to release records, Trace, evaluation samples, and incident notes. When a production issue appears, teams can follow one set of facts to understand scope, ownership, and repair order instead of stitching together model logs, business logs, and verbal explanations.

This evidence also connects the surrounding chapters. It links to Chapter 32 on the overall architecture, Chapter 38 on Trace, and Chapter 41 on cost governance: upstream capabilities provide assumptions, downstream capabilities consume the result, and governance capabilities preserve evidence and review decisions. If these materials do not share identifiers and versions, the production system splits apart. Business owners see user complaints, platform owners see system errors, and security or compliance teams see explanations written after the fact. That separation makes it hard to decide whether the issue came from data, model behavior, tool contracts, workflow state, or organizational ownership.

Common production risks include a new component improving a benchmark while losing evidence fields, interface semantics that do not match, and vendor capability changes that shift responsibility. These risks are less visible during demos because demos usually exercise the successful path. Production users bring boundary cases, repeated requests, permission changes, and long-running state. The platform team should turn such failures into release samples. Some samples should block launch, some can be handled by degradation, and some require the business owner to accept the remaining risk with a review date.

Ecosystem replacement should enter a canary domain first, then expand only after sample results and operating cost support the move. The record can stay compact, but it should include time, version, owner, sample, action, and the next review condition. Without those fields, review remains informal experience. With them, one production issue can become material for later releases, evaluation suites, and training.

A first platform version can start with a small set of high-risk paths. Choose flows with high traffic, high business impact, or sensitive data, require an evidence package for each change, and then expand the practice to ordinary scenarios. This keeps the capability at the engineering level: runnable, explainable, and recoverable.
## 37.20 Trial-run validation for benchmarking conclusions

DataAgent ecosystem benchmarking should not stop at a feature matrix. A product may support NL2SQL, chart generation, knowledge bases, or workflows, but that does not mean it can enter enterprise production. A trial run should use real business questions, real permissions, and the real semantic layer. Trace should record each step, and business reviewers should decide whether the result is usable. Only then does feature benchmarking become platform selection judgment.

The trial run should also observe hidden cost. One product may answer quickly but require heavy human editing. One framework may be flexible but leave all governance to the platform team. One commercial product may have a complete interface but lack Trace, permission, or private-deployment capability. Benchmarking conclusions should record these costs so procurement or self-build decisions are not driven by demos alone.

A first version can express ecosystem comparison as a trial protocol: task samples, integration scope, success criteria, failure samples, human cost, platform gaps, and replacement difficulty. Chapter 37 then supports the DataAgent mainline and gives evidence for procurement, self-build, or hybrid routes.

## Chapter Recap

1. The DataAgent ecosystem **differentiates along four dimensions: entry point, technical approach, deployment form, and organizational governance**; it is rare for a single product to cover the entire chain in Part VI. For example, the East China business decline analysis scenario requires collaboration across six chapters.
2. **Vanna / WrenAI / DB-GPT / Defog / Sherlock** each have their strengths. Enterprises should adopt a **hybrid integration** approach (components registered in the Registry) instead of duplicating Part V platforms or importing two runtimes as a whole package.
3. **ChatBI is an early subset of DataAgent**; BI Copilot and DataAgent coexist and should be harmonized through the `infra/semantic_layer/`.
4. Selection must consider **architecture (Part V), semantic layer, evaluation, and HITL**, more than NL2SQL demos. The procurement baseline requires tenant injection, read-only execution, and auditability via `metric_id@version`.
5. Part VI's six chapters plus the Part V platform form the **complete DataAgent mainline map** in this book. Section 7's walkthrough table gradually maps the East China decline case to the `mini-platform/` module paths.

- [ ] Has the §7 selection checklist been completed?
- [ ] Does the proof of concept cover **multi-round clarifications + Python analysis + report approval** (full East China decline chain)?
- [ ] Is the responsibility for **12-month evaluation and semantic layer governance** clearly assigned?
- [ ] Are the introduced open-source components mapped to the Registry Tool, with no second runtime introduced?

- [Chapter 32](ch32-dataagent.md) to [Chapter 36](ch36.md) - Entire Part VI
- [Chapter 31 Framework Benchmark](../../part05-agent-capabilities/en/ch31.md) · [Chapter 39 Evaluation](../../part07-observability-eval/en/ch39-dataagent-eval-benchmark.md)
- [Chapter 53 Organizational Evolution](../../part10-security-org/en/ch53.md)

---

## References

Liu, X., et al. (2025). NL2SQL survey. *IEEE TKDE*. [https://doi.org/10.1109/TKDE.2025.3592032](https://doi.org/10.1109/TKDE.2025.3592032) Tang, Z., et al. (2025). LLM/Agent-as-Data-Analyst: A survey. arXiv:2509.23988. [https://arxiv.org/abs/2509.23988](https://arxiv.org/abs/2509.23988) Lei, F., et al. (2024). Spider 2.0. *ICLR 2025*. arXiv:2411.07763. [https://arxiv.org/abs/2411.07763](https://arxiv.org/abs/2411.07763) Huo, N., et al. (2026). BIRD-INTERACT. *ICLR 2026*. arXiv:2510.05318. [https://arxiv.org/abs/2510.05318](https://arxiv.org/abs/2510.05318) eosphoros-ai. (2024). *DB-GPT*. GitHub. [https://github.com/eosphoros-ai/DB-GPT](https://github.com/eosphoros-ai/DB-GPT) Canner. (2024). *WrenAI*. GitHub. [https://github.com/Canner/WrenAI](https://github.com/Canner/WrenAI) vanna-ai. (2024). *Vanna*. GitHub. [https://github.com/vanna-ai/vanna](https://github.com/vanna-ai/vanna) Defog.ai. (2024). *Defog*. [https://github.com/defog-ai/defog](https://github.com/defog-ai/defog) Microsoft. (2024). *Copilot in Power BI*. [https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)

Cube. (2025). Semantic layer docs. [https://cube.dev/docs/product/introduction](https://cube.dev/docs/product/introduction)
