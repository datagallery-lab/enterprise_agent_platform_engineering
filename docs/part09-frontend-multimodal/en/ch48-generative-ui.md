# Chapter 48 Generative UI and Rich Interaction

---

Generative UI gives an Agent a way to return structured, editable, and task-specific interfaces instead of plain text. In enterprise systems, this capability is useful only when the generated UI is governed. A model should not freely emit arbitrary code, hidden actions, or unreviewed data bindings. The platform needs schemas, component allowlists, artifact versions, approval states, and evidence references. This chapter discusses how Generative UI becomes a production interface: task workspaces, tool-call rendering, editable artifacts, business controls, data visualization, rendering security, approval flow, and version governance.

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

The review question is not whether the UI looks rich. It is whether each rich element has a controlled source, version, permission boundary, and review path. This distinction matters in DataAgent scenarios. A chart card is useful only when the user can trace it back to the metric definition, SQL result, data version, and explanation text. A report editor is useful only when revisions preserve evidence references. A generated form is useful only when submit actions go through backend permission and approval checks. Rich interaction without these controls tends to produce attractive demos and weak production systems.

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

Controlled rendering can be bypassed when model text is treated as trusted UI. Markdown with embedded HTML, generated JavaScript, unsafe links, and unescaped table content can all create security and data-leakage problems. The frontend should render model output through safe components and sanitize free text. The backend should also avoid returning raw internal values to the UI. Tool results can be summarized for display while full values remain in controlled evidence storage. This keeps the frontend useful without turning it into a data exfiltration surface.

Rendering should include negative paths. A failed tool call needs a card with failure category, retry eligibility, and fallback path. A permission denial needs an explanation that the user can act on without revealing hidden data. A partial result needs a visible quality marker. If the UI only has polished success cards, users learn to distrust the system the first time a real task fails.

## 48.4 Artifacts and editable outputs

Artifacts are generated outputs that users can inspect, edit, version, and publish. Examples include reports, SQL drafts, charts, policy responses, quotation drafts, and checklist documents. An artifact differs from a chat answer because it has identity, type, version, owner, and lifecycle. The platform should record who created the artifact, which run produced it, which evidence it cites, who edited it, and whether it has been approved or published. Without those records, an artifact becomes a pasted answer with no governance.

Artifacts should also carry dependency metadata. A chart depends on a query result, a metric definition, and a visualization spec. A report depends on several evidence references and reviewer edits. A quotation draft depends on customer data, product rules, discount policy, and approval state. When one dependency changes, the platform should know which artifacts need review instead of relying on users to notice stale content.

## 48.5 Business controls and data visualization

Business controls include filters, metric selectors, approval buttons, export actions, and chart configuration. They should be generated from schemas or server-side descriptors, not from arbitrary model text. Data visualization should bind to data references, metric definitions, and query ids instead of raw untraceable values.

*Table 48-3: Business UI controls and required contracts. Source: Compiled by this book.*

| Control | Required contract |
| --- | --- |
| Metric selector | Metric id, version, permission |
| Filter panel | Allowed fields and value domain |
| Chart card | Query id, data reference, chart spec |
| Export button | Artifact id, approval state, retention policy |
| Approval action | Run id, approver, decision payload |

### 48.5.1 Artifact lifecycle and workspace

Artifacts should move through clear states: draft, reviewed, approved, published, archived, or rejected. A workspace can show several artifacts from one run, but each artifact should keep its own version history. This allows a user to edit a chart explanation without changing the underlying SQL result, or to revise a report draft without losing the evidence chain. The workspace should also make ownership clear. A user can edit wording, but metric definitions, tool results, and approval decisions should remain governed by their source systems.

This ownership boundary should appear in the UI. Editable text can show normal editing controls. Derived data can show a refresh or inspect action, but not arbitrary editing. Approval decisions should show approver identity and state. These details reduce confusion when several people work in the same artifact, and they prevent the model or a user from changing governed facts through a text editor.

## 48.6 UI security and approval workflow

Generative UI expands the attack surface. A malicious instruction can ask the model to render a fake approval button, hide a warning, create a misleading chart, or place sensitive data in a visible card. The UI layer must therefore enforce component allowlists, schema validation, content sanitization, and backend-confirmed actions. Approval workflow should never be a frontend-only button. The button is a view of a Runtime state. Clicking it sends a decision payload to the backend, where permission, approver identity, timeout, and audit rules are enforced.

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

Rich outputs need version governance because users edit them. A report may cite a metric version, a chart may use a query result, and a narrative may be revised after review. The platform should store artifact versions, evidence references, editor identity, approval status, and publication history. Version governance also supports rollback. If a chart was generated from the wrong metric definition, the platform should identify affected artifacts and mark them for review. If a component schema changes, old artifacts should remain renderable or be migrated through a controlled process.

Artifact versions should be visible enough for reviewers. A published report should show which version was approved and which evidence set it used. A draft should show whether it has unreviewed changes. If an Agent regenerates a section, the system should keep the old version and explain what changed. This is the difference between a convenient editor and a governable artifact workflow.

## 48.8 Artifact publishing boundary and long-term maintenance

Once an artifact leaves the conversation window, it enters enterprise content governance. A business analysis report may be sent to a meeting system. A quotation draft may enter approval. A SQL draft may be saved as a metric query. A chart may be embedded in a weekly report. Publishing boundaries should be designed when the artifact is created: which outputs can stay only in the session, which can be saved to a personal workspace, which can enter a team workspace, which can be exported, and which require approval. If the boundary is left to user habit, Generative UI can push temporary model output into formal business workflows where responsibility becomes hard to trace.

Two checks should happen before publishing. The first is evidence review. Data, documents, metric definitions, SQL, charts, and human edits referenced by the artifact should remain visible, versioned, and permission aware. The second is action review. Publishing, exporting, sending, and archiving should be confirmed by the backend, with approval state and audit records. A report editor may allow users to improve wording, but it should not let copying and pasting bypass metric definitions or data permissions. A chart may allow a different display form, but it should not hide denominators, sample range, or filter conditions. The closer rich interaction gets to official artifacts, the more carefully evidence and action need separate governance.

Long-term maintenance must answer how old artifacts remain readable. Component libraries change, chart libraries are replaced, data references expire, and permissions evolve. The platform should not make historical reports unreadable because a frontend component changed. It also should not continue showing sensitive details after user permission changes. A practical approach is to store both the rendering contract and a read-only summary. If the old component remains compatible, render it as before. If it is incompatible, show a static summary, evidence links, and a regeneration action. If permissions changed, preserve artifact metadata and recheck sensitive data before display. This keeps historical artifacts usable without weakening current security rules.

Artifact feedback should return to the platform. When users edit a conclusion, delete a chart, rewrite a recommendation, or reject an export, the change tells the platform where the model or tool chain needs work. The platform should associate that feedback with run id, artifact id, component type, evidence reference, and user role. Evaluation and product operations can then use it. If most users delete a chart type, chart selection may be wrong. If users repeatedly rewrite metric explanations, the semantic layer may need clearer definitions. If approvers reject the same export pattern, risk copy and permission policy may need revision. The long-term value of Generative UI comes from these maintenance records as much as from the first generated interface.

The first platform version can define a minimal artifact publishing protocol. It should cover artifact type, artifact version, source Run, evidence references, executable actions, approval requirements, export policy, and rollback method. Each rich output then enters the workspace through the same protocol, giving frontend components and backend governance a shared vocabulary. Later additions such as charts, forms, report blocks, and approval cards can use the same lifecycle instead of leaving each business system to invent temporary interaction rules.

## 48.9 Operating review for rich interactive artifacts

After Generative UI goes live, the platform should review more than component render success. It should ask whether the artifact continued to be useful. After a chart is generated, did the user change the metric, hide a dimension, delete the chart, export the report, or submit it for approval? After a quotation draft is generated, which fields did sales edit, which discounts did approvers reject, and which evidence links were opened? After a SQL draft becomes an artifact, was it saved as a reusable query, or rejected because of permission or metric-definition issues? These behaviors say more about the component contract than the first generated view.

Operating review should route feedback back to platform capability. Frequent deletion of one chart type may mean chart selection rules are poor. Repeated rewriting of metric explanations may mean the semantic layer description is weak. Repeated rejection of a certain export pattern may mean risk copy and approval conditions are unclear. Historical artifacts that often fail to open point to weak component compatibility or static-summary strategy. Review material should include `run_id`, `artifact_id`, component version, data references, evidence references, user edits, and approval results. Frontend teams, platform teams, and business owners can then improve the same artifact path from shared evidence.

Rich artifacts also need maintenance ownership. Component-library upgrades belong to frontend teams, but old artifact readability is shared by platform and content governance. Metric explanations come from data teams, chart rendering from frontend, export permission from security policy, and approval state from Runtime. If ownership is vague, the artifact becomes a cross-team object that nobody truly maintains. The first version can require every artifact type to have an owner, retention window, export policy, and compatibility policy. That simple requirement prevents Generative UI from turning from a polished interface into temporary content that cannot be replayed.

## 48.10 Compatibility testing and degradation strategy for rich components

Rich interactive components need compatibility testing before launch. Charts, forms, report blocks, approval cards, data tables, and editable Artifacts all depend on component version, browser capability, data shape, permission state, and backend events. A component that renders in development may fail for historical messages, old reports, mobile clients, read-only mode, or users whose permission changed. Compatibility testing should cover old component versions, old data references, reduced permissions, expired evidence, failed exports, and changed approval state.

Degradation strategy belongs in the rendering contract. If a component fails to load, the UI can show a static summary, evidence links, and a regeneration entry. If a data reference expires, the UI can ask for recomputation or permission request. If approval state conflicts, the server state should win. If a historical version cannot be rendered with the current component, the UI should preserve a read-only snapshot and explain the change. The frontend should not make an entire message unreadable because one component failed, and it should not bypass permission checks to keep the screen looking complete.

Compatibility testing also supports long-term maintenance. Component-library upgrades, chart-library replacement, data-domain migration, and report-template changes should first run against historical Artifact samples. The sample set should include several tenants, permission levels, component types, and publication states. With this test set, Generative UI becomes a business artifact that can be retained and reviewed over time instead of a one-time generation effect.

## 48.11 Review responsibility in rich interactive interfaces

The more controls Generative UI creates, the clearer review responsibility must be. Charts, filters, approval cards, report paragraphs, export buttons, and task state may appear in the same interface, but they come from different authority sources. Data teams own metrics and data references. Runtime owns state and approval. Frontend teams own rendering and accessibility. Security teams own export and sensitive information. Business owners own final publication. If the interface presents all of them as one generated result, users may assume every part can be edited like text.

Responsibility should be expressed through component contracts. Editable paragraphs can be rewritten. Metric cards can expose definitions and refresh. Approval cards can accept decisions only from authorized reviewers. Export buttons should bind artifact, permission, and retention policy. Clear component contracts help users understand what can be changed, what requires a request, and what must return to the source system. The long-term usability of Generative UI depends on whether these responsibility boundaries are visible in the interface.

Launch review can sample several risky operations: whether users can change metric facts by editing text, whether they can export an artifact without approval, whether they can keep viewing sensitive charts after permission changes, and whether historical reports can trace data sources. If these checks are not covered by component contracts, a rich interface will hide governance problems under polished interaction.

## 48.12 Permission revalidation for rich artifacts

Permissions can change after a rich artifact is saved. A user may have permission to view a chart when a report is generated, but lose that permission a month later. Team changes, project closure, customer-scope changes, and masking-policy updates all affect historical artifacts. If Generative UI validates permission only at generation time, reports and editable artifacts become cached paths around current access control.

Permission revalidation should separate metadata from content. Artifact title, creation time, version, and approval state can remain visible for audit. Chart data, detail tables, sensitive fields, and external export should be checked against current permission. If the current user no longer has access, the interface can show that the artifact exists, hide sensitive views, and offer access request or regeneration. The platform keeps historical material manageable without leaving sensitive content visible because it was generated earlier.

A first version can revalidate on three actions: opening an artifact, exporting an artifact, and publishing an artifact. Each check records user, permission version, artifact version, and result. The closer rich interaction gets to formal business material, the more important this revalidation becomes.

## 48.13 Operating evidence for artifact workspaces

Artifact workspaces need operating evidence because users often treat them as formal work products. A generated report, editable chart, approval card, or quotation draft may live longer than the conversation that created it. The platform should record how the artifact was created, which evidence it used, which user edits changed it, which approvals were applied, and where it was later exported. Without this evidence, a polished workspace becomes difficult to audit once it leaves the chat surface.

Operating evidence should separate artifact state from conversation state. A conversation can be archived while a report remains active. A Run can finish while an artifact keeps receiving edits. A user can lose access to the source data after the artifact was created. The artifact record therefore needs its own lifecycle: draft, under review, approved, published, archived, withdrawn, or regenerated. Each state transition should name the actor, reason, timestamp, policy version, and affected evidence references.

This record helps product teams as much as auditors. If users repeatedly regenerate the same chart, the default chart selection may be wrong. If reviewers approve the narrative but reject exports, the artifact may be useful inside the workspace but unsafe for distribution. If business users edit the same metric explanation in many reports, the semantic layer likely needs clearer wording. These signals are better than generic satisfaction scores because they show which component, action, or evidence path failed.

The workspace should also make support easier. When a user asks why an exported artifact differs from the conversation, support should compare artifact version, data reference, permission result, manual edits, and export policy. If this requires a developer to query several systems manually, Generative UI has not yet become a production capability. A first version can keep the operating evidence compact, but it should be structured enough for Trace, Eval, policy review, and customer support to read the same artifact history.

## 48.14 Multi-user collaboration and conflict handling for artifacts

After Generative UI enters enterprise workflow, an artifact is often edited and reviewed by several people. A sales quotation draft may be generated by an Agent, edited by sales, commented on by legal, checked by finance, and approved by a manager before export. If the platform still treats the artifact as a temporary component inside one user's conversation, later disputes are difficult to explain. The team may not know who changed a number, who removed evidence, who approved export, or which version reached the customer. Multi-user collaboration requires artifacts to have their own permission model, versions, locks, comments, and publication records.

Conflict handling should depend on content type. Ordinary prose can allow concurrent edits with revision history. Chart configuration must stay bound to data references and metric versions; saving visual parameters alone is not enough. Approval decisions, quotation amounts, contract clauses, and export settings are high-risk fields and should have a named owner or locking rule. If two users edit the same chart at the same time, the platform should identify whether the conflict is about display, data reference, or approval state. Display conflicts may be merged. Data-reference conflicts need review. Approval conflicts should return to the responsible owner.

The Agent may also participate in collaboration. When a user asks the Agent to rewrite a report based on the latest comments, the Agent should not overwrite paragraphs that have already passed human review. A safer pattern is to generate proposed changes, mark affected evidence references and fields, and let the owner accept or reject them. For artifacts already published or under approval, the Agent should create a new version or a revision proposal instead of modifying the original version. This preserves human accountability while still using the model to reduce editing work.

A first version can keep artifact collaboration to a few rules: each artifact has an owner, each edit creates a version, each high-risk field change requires review, and each export binds to a version number and permission result. The platform does not need a full office suite on day one, but it does need traceable, reversible, and explainable key actions. The closer a rich interface gets to a formal business tool, the more important these records become.

This also changes frontend design. The UI should show whether the artifact is a draft, under review, approved, published, withdrawn, or regenerated. It should show when an Agent suggestion is pending human acceptance. It should warn users before they edit a field that will trigger re-approval. These small state signals prevent users from treating every editable surface as informal text. They also make support and audit work easier because the interface reflects the same lifecycle recorded in the backend.

## 48.15 Artifact withdrawal and notification flow

Once an artifact is downloaded, exported, embedded in a report, or shared with another team, it is no longer only a component in a workspace. If a metric definition is later found wrong, permissions change, approval is revoked, chart interpretation is corrected, or source evidence becomes invalid, the platform needs a way to withdraw or mark the old version. Without withdrawal, rich artifacts circulate like ordinary files. The interface looks modern, but governance still behaves like email attachments.

Withdrawal is separate from deletion. A published artifact may need to remain available for audit while losing its status as current evidence. The platform should distinguish several actions: hide content, mark expired, revoke publication, replace with a new version, and notify recipients. Internal drafts can expire quietly. Approved reports should keep the old version and withdrawal reason. External exports should record who was notified and what repair action was taken. If an artifact is embedded in other pages or meeting material, the platform should locate those references together with the original workspace.

Notification should follow impact scope. A chart-style correction may notify only the editor. A metric-definition error should notify the report owner and reviewers. A permission leak or external export error should notify security, compliance, and the business owner. The message should state affected version, reason, recommended action, and replacement version. Users need to know whether to download again, re-approve, replace meeting material, or stop using an old link.

A first version can keep withdrawal simple but explicit. Each artifact records publication scope, reference locations, export records, and recipients. Withdrawal creates a new state and notification tasks. Support staff can query impact by artifact id. With this capability, a Generative UI artifact can enter formal business flow and still be corrected when needed. Production value does not come only from fast generation; it also comes from the ability to recover impact when a generated work product is wrong.

## 48.16 Pre-release acceptance for interactive artifacts

Before a Generative UI artifact is released, acceptance should move from whether the page renders to whether the artifact can be used in business work. Review should check that data references exist, charts bind to metric versions, user edits create versions, export revalidates permission, approval state comes from the backend, and withdrawal plus notification can run. Component rendering alone misses ownership problems across the artifact lifecycle.

Acceptance should also cover degraded display. If a chart fails to render, the workspace should show a table or data summary. If permission is missing, it should keep metadata visible while hiding sensitive content. If evidence expires, it should mark the conclusion as stale. If multi-user edits conflict, it should prompt users to choose a version. A rich interface without a degradation path can block the whole task when a single component fails.

A first version can turn pre-release acceptance into an artifact sample set. Each sample contains input evidence, component schema, permission state, edit action, approval action, and expected export result. Designers, frontend engineers, backend engineers, data teams, and security reviewers can then discuss the same work product sample instead of checking interface, API, and policy in separate tracks.

Interactive artifacts also need a clear edit model. A generated chart, report section, form, or dashboard is rarely final at first render. Users may change a metric, hide a column, rewrite an explanation, add a comment, or request approval. The platform should distinguish model-generated content, user edits, tool-derived data, and reviewer decisions. Each edit should create a new artifact version with author, time, evidence references, permission state, and publication status. If edits overwrite the original silently, later reviewers cannot tell whether an error came from the model, a tool, or a human correction.

The edit model should connect with evaluation. When users repeatedly change the same chart type, metric explanation, or generated form field, those edits are valuable samples. They can show weak semantic-layer descriptions, poor component selection, incomplete evidence binding, or unclear approval copy. The artifact workspace should capture accepted edits and rejected suggestions as structured feedback. Chapter 39 Eval can then use artifact-level feedback with more detail than thumbs-up or thumbs-down signals. Rich UI becomes a source of learning because it records what users changed in real work.

Permission revalidation is especially important after edits. A user may generate an artifact under one permission scope and later share it with a broader audience. A chart may become safe after aggregation, while a table remains sensitive. A report may contain one paragraph that can be exported and another that requires approval. The artifact should carry permission metadata at component or evidence level, with document-level policy used as the outer boundary. Export, sharing, embedding, and external sending should revalidate this metadata. This prevents an attractive artifact from bypassing the data controls that would have applied to the original query.

Degradation should be designed as a business state, not an error screen. If a chart library fails, the artifact can show a table and keep the evidence references. If a user lacks access to one metric, the artifact can mask that block and keep the rest of the report available. If a component version is retired, the workspace can show a static rendering with a warning and a migration path. Degraded artifacts should keep enough structure for review and correction. A blank panel destroys trust and removes the material needed to repair the issue.

Rich components also introduce security concerns that plain text does not have. A component may render external links, HTML fragments, file previews, embedded charts, or user-provided labels. The platform should sanitize input, restrict component types, enforce schema validation, and prevent hidden actions from appearing as ordinary UI. A generated button should never execute a tool unless the backend has created a matching action with permission, state, and idempotency key. Component safety belongs in the artifact contract; it cannot depend on visual review alone.

For a first version, Generative UI should favor a small component set with strong contracts: text block, evidence card, metric card, table, chart, form draft, approval card, and report section. Each component should define required data, allowed actions, permission behavior, fallback rendering, and audit fields. This smaller surface is easier to operate and safer to expand. Once these components produce stable artifacts, the platform can add richer layouts with the same version, evidence, and recovery model.

## 48.17 Artifact permission metadata and export revalidation

Permissions for rich artifacts should not exist only at the document level. A report may contain public metrics, department-sensitive metrics, customer details, human comments, and model-written summaries. A dashboard may include a shareable trend chart and a detail table that must remain inside the original tenant. If the platform assigns one permission state to the whole artifact, export and sharing will either overexpose data or block too much. A better design attaches permission metadata to components, fields, and evidence references, with document-level policy as the outer boundary.

Export revalidation should recalculate visibility. A user had permission when the artifact was generated, but that does not prove the user can export it later or that recipients can read it. The platform should recheck permission, evidence validity, masking state, and approval state before sharing, downloading, embedding, sending external email, or generating PDF. If only some components fail, the system can produce a degraded version: hide sensitive tables, keep chart summaries, replace fields with masked values, or require approval before export.

Permission metadata also supports audit and withdrawal. When an artifact is withdrawn, the platform should know which component, evidence reference, or export action caused the risk. A document-level abnormal state is too coarse for repair. Component-level location allows local replacement, renewed approval, or targeted notification to affected recipients. Governance granularity then matches the expressive power of rich artifacts.

A first version can record four fields for each component: data source, permission level, evidence reference, and export policy. Before export, the backend produces the downloadable version from these fields and writes the validation result to Trace. The frontend displays state, but it cannot bypass backend revalidation. Generative UI can then become more flexible without weakening existing data boundaries.

## 48.18 Reuse and invalidation of artifact templates

Artifact templates accumulate with business workflows. Report sections, metric cards, approval cards, chart layouts, export forms, and evidence cards can all move from one generation into reusable templates. Reuse reduces generation cost and gives users a more stable work product. When a template becomes stale, however, the error is copied in bulk. An old metric definition, approval field, or export note can keep appearing in new artifacts, making the interface look governed while the content no longer applies.

Template reuse should bind to applicability conditions. Each template should record task type, data domain, metric version, permission requirement, component schema, latest review time, and owner. When the Agent selects a template, it should check task conditions before relying on natural-language similarity. If a template lacks evidence references, permission metadata, or fallback rendering, it should not enter a formal workspace.

A first version can give templates five states: draft, pilot, standard, frozen, and retired. Draft templates are used only in the current task. Pilot templates apply to limited scenarios. Standard templates enter the platform component library. Frozen templates wait for definition review. Retired templates keep migration notes. Generative UI reuse then becomes asset management instead of copying one successful generation into every scenario.

## 48.19 Frontend governance of the artifact lifecycle

When frontend governance of the artifact lifecycle reaches production, the platform needs a shared evidence standard for artifact state, template version, data source, edit history, permission, withdrawal, and publication channel. This standard is not paperwork for its own sake. It lets business, platform, data, security, and operations teams discuss the same facts. Without this material, incident review depends on memory and personal judgment. With it, the team can see which inputs were valid, which actions executed, which artifacts can still be used, and which results need correction or withdrawal.

This evidence should connect to Chapter 36 on reports, Chapter 38 on Trace, and Chapter 52 on compliance. The upstream chapters provide the capability base, downstream chapters consume the runtime result, and this chapter explains how the middle layer is verified. If a capability looks complete inside one chapter but cannot enter Trace, Eval, release records, or the compliance evidence package, the production system still has a break in the chain. Readers should treat cross-chapter interfaces as engineering contracts, not as a reading order.

Common risks include users treating drafts as final results, template upgrades changing historical display, and edits invalidating evidence references. A successful demo rarely exposes these problems because demo samples are usually clean, short, and direct. Real business traffic brings stale data, abnormal input, permission changes, user withdrawal, budget limits, and long-running state. If the platform does not turn those situations into samples and ledgers, later scenarios will hit the same class of issues again.

Users treating drafts as final results should be turned into a tracked review item when it appears repeatedly. The operating record should at least state owner, version, sample, affected scope, action, and review time. It does not need to become a long process report, but it must be clear enough for a later maintainer to understand the decision. For high-risk capability, the record should also state which conditions allow wider use and which failures require degradation or withdrawal.

A first version can build this habit in a few representative scenarios. It is better to make high-traffic, high-risk, externally visible paths solid first, then copy the sample, ledger, and review method to related capabilities in other chapters. This makes the chapter read like engineering guidance: it explains how the capability is integrated, validated, operated, and retired.

## Chapter Recap

Generative UI is valuable when it turns Agent output into governed workspaces, not when it gives the model free control over the interface. Production systems need component allowlists, schemas, evidence references, artifact versions, backend approval state, and safe rendering. Rich interaction should make the task easier to complete while preserving auditability and security.

## References

Vercel. (n.d.). [AI SDK documentation](https://sdk.vercel.ai/docs).

Open Web Application Security Project. (n.d.). [Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

C2PA. (n.d.). [Technical specification](https://c2pa.org/specifications/).
