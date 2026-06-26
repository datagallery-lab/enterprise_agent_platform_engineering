# Chapter 48 Generative UI and Rich Interaction

---

Generative UI gives an Agent a way to return structured, editable, and task-specific interfaces instead of plain text. In enterprise systems, this capability is useful only when the generated UI is governed. A model should not freely emit arbitrary code, hidden actions, or unreviewed data bindings. The platform needs schemas, component allowlists, artifact versions, approval states, and evidence references.

This chapter discusses how Generative UI becomes a production interface: task workspaces, tool-call rendering, editable artifacts, business controls, data visualization, rendering security, approval flow, and version governance.

---

## 48.1 Domestic enterprise Generative UI and DataAgent UI comparison

Domestic DataAgent and enterprise Agent products often converge on a similar interaction style: the user asks a business question, the system shows retrieval or SQL progress, returns charts or cards, and allows export or report generation. The difference is whether these UI elements are governed artifacts or temporary visual output.

*Table 48-1: Generative UI comparison dimensions. Source: Compiled by this book.*

| Dimension | Demo UI | Production UI |
| --- | --- | --- |
| Component source | Model writes display content | Platform renders approved components |
| Data binding | Direct values in the response | Data references with permission checks |
| Editing | Local edits only | Versioned artifact workflow |
| Approval | Visual button | Backend state transition |
| Audit | Screenshot or log | Trace, artifact version, and evidence ref |

The review question is not whether the UI looks rich. It is whether each rich element has a controlled source, version, permission boundary, and review path.

This distinction matters in DataAgent scenarios. A chart card is useful only when the user can trace it back to the metric definition, SQL result, data version, and explanation text. A report editor is useful only when revisions preserve evidence references. A generated form is useful only when submit actions go through backend permission and approval checks. Rich interaction without these controls tends to produce attractive demos and weak production systems.

## 48.2 Task-oriented interaction interface

Task-oriented UI starts from the work the user is trying to finish. A refund dispute needs order status, policy evidence, exception approval, and response draft. A business analysis task needs metric definition, SQL result, chart, explanation, and report export. A contract review task needs clause extraction, risk tags, reviewer notes, and final responsibility boundary.

Generative UI should assemble these pieces into a workspace. The workspace can contain cards, tables, charts, forms, notes, and artifacts, but the platform should decide which components are allowed for a task type. This prevents the model from inventing controls that the backend cannot execute.

Task workspaces should also preserve unfinished state. Users may leave a report draft, return after a review, or ask a follow-up question that depends on a previous chart. The workspace therefore needs artifact ids, selected evidence, current filters, and pending approvals. If the UI stores this only in browser state, the task becomes impossible to review or resume after a session expires.

## 48.3 Tool-call rendering patterns

Tool-call rendering shows users what the Agent is doing and what evidence the action produced. A tool card should show the tool name, purpose, safe parameter summary, status, result summary, error category, and any required confirmation. Sensitive parameters should be redacted or represented as references.

*Table 48-2: Tool-call rendering patterns. Source: Compiled by this book.*

| Pattern | Use case | Risk control |
| --- | --- | --- |
| Progress card | Long-running query or file parsing | Show status and cancellation path |
| Evidence card | Retrieval, SQL, or metric lookup | Show source and version |
| Approval card | High-risk action | Pause Runtime until decision |
| Error card | Tool failure or permission denial | Show recovery path without leaking internals |

### 48.3.1 Where controlled rendering can be bypassed

Controlled rendering can be bypassed when model text is treated as trusted UI. Markdown with embedded HTML, generated JavaScript, unsafe links, and unescaped table content can all create security and data-leakage problems. The frontend should render model output through safe components and sanitize free text.

The backend should also avoid returning raw internal values to the UI. Tool results can be summarized for display while full values remain in controlled evidence storage. This keeps the frontend useful without turning it into a data exfiltration surface.

Rendering should include negative paths. A failed tool call needs a card with failure category, retry eligibility, and fallback path. A permission denial needs an explanation that the user can act on without revealing hidden data. A partial result needs a visible quality marker. If the UI only has polished success cards, users learn to distrust the system the first time a real task fails.

## 48.4 Artifacts and editable outputs

Artifacts are generated outputs that users can inspect, edit, version, and publish. Examples include reports, SQL drafts, charts, policy responses, quotation drafts, and checklist documents. An artifact differs from a chat answer because it has identity, type, version, owner, and lifecycle.

The platform should record who created the artifact, which run produced it, which evidence it cites, who edited it, and whether it has been approved or published. Without those records, an artifact becomes a pasted answer with no governance.

Artifacts should also carry dependency metadata. A chart depends on a query result, a metric definition, and a visualization spec. A report depends on several evidence references and reviewer edits. A quotation draft depends on customer data, product rules, discount policy, and approval state. When one dependency changes, the platform should know which artifacts need review rather than relying on users to notice stale content.

## 48.5 Business controls and data visualization

Business controls include filters, metric selectors, approval buttons, export actions, and chart configuration. They should be generated from schemas or server-side descriptors, not from arbitrary model text. Data visualization should bind to data references, metric definitions, and query ids rather than raw untraceable values.

*Table 48-3: Business UI controls and required contracts. Source: Compiled by this book.*

| Control | Required contract |
| --- | --- |
| Metric selector | Metric id, version, permission |
| Filter panel | Allowed fields and value domain |
| Chart card | Query id, data reference, chart spec |
| Export button | Artifact id, approval state, retention policy |
| Approval action | Run id, approver, decision payload |

### 48.5.1 Artifact lifecycle and workspace

Artifacts should move through clear states: draft, reviewed, approved, published, archived, or rejected. A workspace can show several artifacts from one run, but each artifact should keep its own version history. This allows a user to edit a chart explanation without changing the underlying SQL result, or to revise a report draft without losing the evidence chain.

The workspace should also make ownership clear. A user can edit wording, but metric definitions, tool results, and approval decisions should remain governed by their source systems.

This ownership boundary should appear in the UI. Editable text can show normal editing controls. Derived data can show a refresh or inspect action, but not arbitrary editing. Approval decisions should show approver identity and state. These details reduce confusion when several people work in the same artifact, and they prevent the model or a user from changing governed facts through a text editor.

## 48.6 UI security and approval workflow

Generative UI expands the attack surface. A malicious instruction can ask the model to render a fake approval button, hide a warning, create a misleading chart, or place sensitive data in a visible card. The UI layer must therefore enforce component allowlists, schema validation, content sanitization, and backend-confirmed actions.

Approval workflow should never be a frontend-only button. The button is a view of a Runtime state. Clicking it sends a decision payload to the backend, where permission, approver identity, timeout, and audit rules are enforced.

The same rule applies to generated controls. If the model suggests a "refund" button or "publish" button, the frontend should render it only when the backend has issued an allowed action descriptor. The descriptor should include action id, required role, risk level, timeout, and confirmation copy. Otherwise the UI can accidentally create the appearance of an action the platform has not authorized.

### 48.6.1 Product and engineering constraints for rendering security

Rendering security combines product design and engineering control. Product design decides which actions users can see and when warnings are mandatory. Engineering control ensures generated content cannot escape schemas, execute code, or create hidden side effects.

#### Model-generated code and component allowlists

The model should not generate arbitrary frontend code for production. It can select from an allowlist of components and fill schema-defined fields. New components should go through code review, security review, and regression tests before the model can call them.

#### In-conversation cards and standalone artifact workspace

In-conversation cards are good for lightweight status and evidence. Standalone artifact workspaces are better for long reports, dashboards, and editable outputs. Mixing the two without lifecycle rules causes users to lose track of which version is authoritative.

#### Direct frontend data rendering and data-reference rendering

Directly rendering raw data in the frontend is risky when data is sensitive or large. Data-reference rendering lets the UI request a controlled view from the backend. The UI receives a chart or table view that already respects permissions, retention rules, and masking policy.

#### Frontend tool calls and backend tool rendering

Frontend tool calls are useful for local UI actions, but business tools should execute through the backend. Backend execution gives the platform a place to enforce permission, idempotency, audit, and compensation. The frontend should render the result, not bypass governance.

## 48.7 Version governance for rich interactive outputs

Rich outputs need version governance because users edit them. A report may cite a metric version, a chart may use a query result, and a narrative may be revised after review. The platform should store artifact versions, evidence references, editor identity, approval status, and publication history.

Version governance also supports rollback. If a chart was generated from the wrong metric definition, the platform should identify affected artifacts and mark them for review. If a component schema changes, old artifacts should remain renderable or be migrated through a controlled process.

Artifact versions should be visible enough for reviewers. A published report should show which version was approved and which evidence set it used. A draft should show whether it has unreviewed changes. If an Agent regenerates a section, the system should keep the old version and explain what changed. This is the difference between a convenient editor and a governable artifact workflow.

## Chapter Recap

Generative UI is valuable when it turns Agent output into governed workspaces, not when it gives the model free control over the interface. Production systems need component allowlists, schemas, evidence references, artifact versions, backend approval state, and safe rendering. Rich interaction should make the task easier to complete while preserving auditability and security.

## References

Vercel. (n.d.). [AI SDK documentation](https://sdk.vercel.ai/docs).

Open Web Application Security Project. (n.d.). [Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

C2PA. (n.d.). [Technical specification](https://c2pa.org/specifications/).
