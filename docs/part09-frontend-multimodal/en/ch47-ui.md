# Chapter 47 Dialogue UI and Streaming Output

---

Enterprise Agent UI is a task surface, not a text renderer. A user expects to see what the Agent is doing, which tool is running, which evidence is being used, whether approval is waiting, and how to recover after a failure. If the frontend only renders final Markdown, the system hides the execution responsibility that earlier chapters have spent so much effort making explicit.

Streaming output therefore needs a protocol, a message model, and observable frontend state. The backend emits events from Runtime, Tool Registry, Planner, Memory, RAG, and Human-in-the-loop. The frontend reduces those events into stable messages, progress cards, evidence panels, approvals, errors, and final artifacts. This chapter treats the dialogue UI as part of the platform contract.

---

## 47.1 Enterprise Agent UI composition

An enterprise Agent UI usually contains five layers. The input layer accepts text, files, voice, and structured parameters. The conversation layer keeps user turns, assistant turns, tool cards, evidence cards, approval cards, and final outputs. The task layer exposes run status, step progress, retry actions, and cancellation. The evidence layer shows citations, SQL, charts, uploaded files, permissions, and generated artifacts. The feedback layer collects corrections, review results, and user acceptance.

*Table 47-1: Enterprise Agent UI components and platform responsibilities. Source: Compiled by this book.*

| UI component | Platform responsibility | Review focus |
| --- | --- | --- |
| Message list | Preserve turns, tool events, and final outputs | Whether state can be replayed |
| Tool card | Expose parameters, status, errors, and side effects | Whether high-risk actions are marked |
| Evidence panel | Show citations, data references, and metric definitions | Whether users can inspect sources |
| Approval card | Pause execution and collect decisions | Whether approval maps to backend state |
| Feedback entry | Collect correction and review signals | Whether feedback enters evaluation |

The UI should not invent state that the backend does not know about. If the frontend shows "approved" while Runtime still waits, the audit trail breaks. If the frontend hides tool errors and only shows the final answer, failure analysis becomes impossible. A production UI has to make backend state visible without exposing sensitive internal details.

This separation also affects product design. A chat-style input can still be the entry point, but the main workspace should reserve room for stateful objects: running steps, tool evidence, approval decisions, generated charts, and feedback. Teams often discover this too late. The first demo works because one answer fits on one screen. The first production workflow fails because users need to inspect the query behind the chart, check whether the policy document is current, and see whether an approval is still pending. Designing the UI around task objects from the start prevents that later redesign.

## 47.2 Streaming interaction protocol

Streaming protocols translate backend execution into user-visible progress. Token streaming is only one event type. Enterprise Agent frontends also need events for run creation, planning, retrieval, tool invocation, human approval, artifact creation, warning, error, retry, and completion.

*Table 47-2: Common streaming event types. Source: Compiled by this book.*

| Event type | Meaning | UI rendering |
| --- | --- | --- |
| `run.started` | Runtime accepted the task | Create task container |
| `message.delta` | Model text is being generated | Append text incrementally |
| `tool.started` | Tool call begins | Show tool card and spinner |
| `tool.completed` | Tool call returns | Render result summary and evidence |
| `approval.waiting` | Execution pauses for a person | Show approval card |
| `artifact.updated` | Editable output changes | Refresh artifact preview |
| `run.failed` | Task cannot continue | Show error, reason, and recovery action |

The protocol should use stable identifiers. A message id, run id, step id, tool call id, and artifact id let the frontend update the right element instead of appending duplicate cards. Idempotency matters because networks reconnect and SSE clients may replay events. Version compatibility belongs in the protocol as well. A frontend released this week may connect to a backend service released next week, and cached pages may keep an older reducer in the browser. Events should therefore include a schema version and optional fields should have documented defaults. When the backend adds a new event type, the frontend should degrade gracefully by showing a generic status card instead of dropping the event silently.

### 47.2.1 State expression in streaming events

A streaming event should describe state as well as text. The frontend needs to know whether a tool is pending, running, completed, failed, cancelled, or waiting for approval. It also needs to know whether the event is final or can be superseded by later events.

Weak protocols force the frontend to infer state from natural language such as "I am querying the database." That inference breaks as soon as the model wording changes. A stronger protocol sends explicit state and keeps model text separate from operational events. The model can explain what happened, but Runtime remains the source of state.

## 47.3 Message model and incremental rendering

The message model is the frontend projection of the run. A single user turn may produce assistant text, multiple tool cards, an approval request, a chart, and a final report. Treating all of these as one string makes partial updates and replay difficult.

*Table 47-3: Message model objects. Source: Compiled by this book.*

| Object | Main fields | Purpose |
| --- | --- | --- |
| Message | id, role, content blocks, status | Preserve conversation turns |
| Step | id, run id, type, status | Track execution progress |
| Tool call | id, tool name, arguments, result, error | Render governed tool execution |
| Evidence ref | source, version, snippet, permission | Connect output to evidence |
| Artifact | id, type, version, content reference | Manage editable outputs |

Incremental rendering should update objects by id. A token delta appends to a text block. A tool event updates a tool card. An approval decision updates the waiting step. This design makes reconnect and replay tractable because the frontend can rebuild the view from the event stream.

### 47.3.1 From event stream to stable message model

The event reducer is the boundary between stream noise and UI state. It receives ordered events, checks ids, applies status transitions, ignores duplicate deltas, and marks terminal states. The reducer should be deterministic: given the same event list, it should produce the same UI state.

This is also where frontend errors become debuggable. If a card appears twice, the reducer should reveal whether the backend emitted duplicate ids or the client applied the same event twice. If text arrives after completion, the reducer should reject or quarantine the event instead of silently mutating a completed answer.

The reducer should be tested with recorded event sequences. Useful samples include reconnect after partial text, a tool failure followed by retry, approval timeout, cancellation while a tool is running, and late-arriving deltas after completion. These tests are small, but they catch many UI bugs that manual clicking misses. The expected result should be a stable message tree, not a screenshot comparison alone.

## 47.4 Agent frontend framework selection

Frontend framework selection should start from the event contract. Vercel AI SDK, assistant-ui, CopilotKit, AG-UI, and custom React/Vue implementations all help with parts of the interaction, but none removes the need for enterprise state, permissions, approval, and audit.

*Table 47-4: Frontend framework choices. Source: Compiled by this book.*

| Choice | Strength | Enterprise boundary |
| --- | --- | --- |
| Streaming SDK | Fast model-call and streaming integration | Needs platform state and audit integration |
| Chat component library | Good message and thread UI | Does not own backend execution semantics |
| In-app copilot framework | Connects Agent to product state | Requires permission and approval governance |
| Custom protocol | Fits internal Runtime exactly | Higher maintenance and testing cost |

The platform should avoid binding backend semantics to one UI library. A stable event protocol lets teams replace components without changing Runtime. Procurement decisions should separate component maturity from platform fit. A polished chat component can reduce frontend work but still leave the team to implement approval state, tool evidence, tenant masking, and trace correlation. A lower-level SDK may require more UI work but fit a custom Runtime better. The decision should be made with a small production-like flow, such as a DataAgent query that includes SQL generation, chart rendering, evidence display, feedback, and an approval branch.

### 47.4.1 SSE, WebSocket, and HTTP chunked response

SSE is simple and works well for one-way event streams from backend to browser. It fits most Agent progress output. WebSocket is useful when the client also sends frequent control messages, such as real-time voice, collaborative editing, or low-latency interruption. HTTP chunked response is easy for text generation but usually too weak for structured Agent events. The choice should reflect control requirements. If the user only receives progress, SSE is often enough. If the user can interrupt, approve, edit, and speak while the Agent runs, the system may need WebSocket or a separate control channel.

Operational constraints matter too. SSE is easier to pass through many enterprise gateways, but long-lived connections still need heartbeat and timeout policy. WebSocket gives more control, but some corporate networks inspect or block it. HTTP chunked response is widely supported, yet it often mixes text and control information in ways that become hard to evolve. The platform should document the failure behavior for each choice: reconnect delay, last event id, duplicate handling, and user-visible error copy.

### 47.4.2 Self-built protocol and UI SDK

A self-built protocol is justified when enterprise state is richer than the public SDK model. The protocol should define event types, required ids, allowed status transitions, error payloads, reconnect behavior, and compatibility rules. A small internal UI SDK can then expose hooks such as `useRun`, `useMessages`, `useToolCards`, and `useArtifacts`. The risk is protocol drift. If every application adds private event fields, shared components lose value. Platform teams should publish versioned event schemas and regression samples.

### 47.4.3 Client-side token stitching and event reducer

Client-side token stitching looks simple but fails easily under reconnect, retry, and cancellation. The reducer should know whether a delta belongs to the active message block, whether it has already been applied, and whether the message has reached a terminal status. For tool and approval events, the reducer should update structured objects instead of appending text. This keeps operational state separate from narrative explanation and makes audit replay possible.

### 47.4.4 Domestic enterprise Agent and DataAgent UI comparison

Many domestic enterprise Agent and DataAgent products expose similar UI elements: question input, SQL or tool progress, chart cards, evidence references, report export, and feedback. The difference lies in how much of that UI is backed by platform state. A demo can show a chart after a query. A production platform needs the chart to connect to query id, metric definition, permission result, data version, and evaluation feedback. When reviewing products or internal implementations, look past visual polish. Check whether each visible element has a backend object and whether that object can be traced.

## 47.5 Reliable interaction and frontend observability

Frontend observability connects user experience to backend evidence. The UI should record render latency, stream interruption, reducer errors, duplicate event ids, failed uploads, approval timeouts, and user feedback. These signals should carry run id and trace id so backend and frontend teams can investigate the same incident.

Privacy boundaries still apply. Do not log raw prompts, file contents, or sensitive evidence in frontend analytics. Log references, ids, statuses, and error categories. When a user reports that an answer disappeared or a card showed the wrong state, these records should help reconstruct the event sequence.

Frontend observability should be correlated with backend Trace. A render error without run id is a frontend bug report; a render error with run id, step id, and event id becomes production evidence. Teams can then compare what Runtime emitted, what the network delivered, and what the reducer applied. This is especially useful for intermittent streaming issues, where screenshots rarely capture the moment that state diverged.

## 47.6 Dialogue UI acceptance criteria

A dialogue UI is ready for production only when it can render normal execution and abnormal paths. It should show progress without fabricating state, preserve evidence without leaking sensitive content, support reconnect without duplicate cards, expose approvals as backend state, and collect feedback into evaluation.

*Table 47-5: Dialogue UI acceptance criteria. Source: Compiled by this book.*

| Area | Acceptance criterion |
| --- | --- |
| State consistency | UI state can be rebuilt from event history |
| Failure handling | Tool errors, timeouts, and cancellations are visible |
| Evidence | Citations and data references are inspectable |
| Approval | Human decisions map to Runtime state |
| Observability | Frontend events carry run id and trace id |

## 47.7 Abnormal paths and acceptance samples before launch

Dialogue UI acceptance cannot focus only on the happy path. Enterprise Agent frontends often fail at the edges: network jitter, tool failure, approval waiting, page refresh, browser reconnect, long task recovery, and late events. The user sees UI state while the backend owns Run state. If the two are not mapped consistently, the same task will appear as different facts in different systems. Runtime may have cancelled a task while the frontend still says it is generating. An approval may have expired while the button remains clickable. A tool may fail and the model may still continue with a conclusion, leading the user to believe the analysis completed. These cases rarely appear in demos, but they erode trust in production.

Teams should prepare frontend replay samples before launch. The samples can stay small, but they should cover real failures: reconnect after streaming text is interrupted, retry after tool timeout, approval card expiration, task recovery after page refresh, upload parsing failure, permission denial in a DataAgent query, and a late token delta after the final report was generated. Each sample should preserve the event sequence, expected UI state, and visible recovery action. Acceptance should inspect more than screenshots. The reducer should rebuild the same message tree from the same event history. If one event sequence produces different UI across browsers or refresh timing, the frontend state machine is not ready for production.

Abnormal paths also need consistent user-facing copy. A tool failure should name the failed step, whether retry is possible, whether existing evidence remains valid, and whether a human should take over. Permission denial should not be phrased as model inability; it should say that policy blocked this access. Approval timeout should enter task state and Trace instead of disappearing from the page. UI copy affects how users assign responsibility. Vague errors push users to keep asking the model while the real issue sits in the tool, permission, or network layer.

Task recovery should be designed as a core behavior. Enterprise users will not stay on one browser tab while a long task runs. They may refresh, switch devices, close the browser, return later, or enter the task through a notification. On recovery, the UI should fetch current Run state and historical events from the backend, then subscribe to subsequent events. Browser memory should never be the source of task truth. If recovery shows only the final answer, the user loses tool, evidence, approval, and error history. If recovery replays every token as fresh text, duplicate content appears. A steadier design is for the backend to provide a snapshot plus incremental events, and for the frontend to merge both through the same reducer.

Acceptance should include the feedback loop. When a user marks an answer wrong, edits a report, rejects a chart, or chooses a different metric definition, the platform should receive structured feedback instead of a loose analytics event. At minimum, feedback should carry run id, artifact id, evidence reference, edited location, and final disposition. Chapter 39's evaluation system can then identify whether the error came from retrieval, tool execution, generation, visualization, or user interpretation. A dialogue UI that only displays results and does not return user corrections to the platform deprives later evaluation and governance of the most useful samples.

## 47.8 Event protocol version review

After launch, the frontend event protocol should be reviewed with the same care as a backend API. Events such as `message.created`, `token.delta`, `tool.call.started`, `tool.call.finished`, `approval.waiting`, `artifact.updated`, and `run.cancelled` become dependencies for frontend reducers, mobile clients, audit systems, Trace, evaluation feedback, and support diagnosis. Adding fields, renaming states, or changing event order can affect historical task recovery and incident review. The platform should maintain protocol versions, compatibility windows, and replay samples instead of treating events as page-local implementation details.

Version review should inspect three kinds of material. The first is event schema: whether fields have stable meaning, whether machine actions and human actions are separated, and whether each event carries `run_id`, `trace_id`, `seq`, `event_id`, and tenant context. The second is replay samples: normal streaming answers, tool failure, approval timeout, user cancellation, report generation, late events, and reconnect should all rebuild the UI from the same event history. The third is error copy: after a protocol change, user-visible status should still match Runtime truth. If the backend has cancelled a task, the frontend should not keep saying that analysis is running. If a tool returns permission denial, the UI should not render it as model incapability.

Event protocol review also supports evaluation. Downvotes, evidence expansion, report edits, question retries, and rejected approvals should enter replayable events instead of living only as product analytics. Evaluation needs to know which evidence, Artifact, or tool phase exposed the problem before it can locate the error source. If frontend events only serve experience metrics, the platform loses some of its best operating samples. Once event protocols are reviewed as versioned contracts, UI, Runtime, and evaluation teams can discuss quality issues around the same Run.

## 47.9 Accessibility and business continuity in dialogue interfaces

Enterprise Agent UI also needs accessibility and business continuity. Streaming output, tool cards, approval buttons, error messages, and evidence expansion must work beyond an ideal desktop demo. Customer-service agents, mobile approvers, field operators, low-bandwidth networks, and assistive reading tools all shape interface design. A UI that focuses only on visual streaming effects can make task state harder to read in production, especially when a connection drops or a long task pauses between tool calls.

Accessibility should become part of the component contract. Tool cards need clear state text and keyboard paths. Approval buttons should be identifiable by screen readers. Error messages should state the failed phase and available recovery action. Evidence references should lead to readable sources. After streaming ends, the interface should expose a stable final version instead of leaving users to infer where the answer stopped. Business continuity requires the same task to survive refresh, reconnect, and device switching. The frontend should fetch current Run state and historical events from Runtime instead of treating browser memory as the source of truth.

These requirements may look like frontend details, but they affect platform trust. If users cannot tell whether a task is still running, they submit duplicates. If approvers cannot inspect evidence, they move confirmation offline. If report generation loses edit state after refresh, users copy content into local documents. Each move outside the platform removes samples from Trace, Eval, and security audit. Dialogue UI quality therefore affects whether the Agent platform can keep learning from real work.

## 47.10 Operating support material for dialogue entry points

After a dialogue UI goes live, the frontend team needs operating support material. The material should describe event protocol, message state, failure prompts, cancellation behavior, reconnection strategy, attachment limits, permission display, and Trace linkage. Support, business operations, and platform on-call teams can then tell whether the model failed to answer, a tool is still running, the frontend lost streaming events, or the backend has moved into an approval state. Without this material, the dialogue entry point is operated like a generic chat box, and real incidents get reported only as "the AI did not respond."

User-facing copy should also be tied to runtime state. Error messages, waiting messages, approval messages, permission messages, and degradation messages should come from the same state model instead of being assembled separately by each component. When a Run is queued, executing, waiting for confirmation, partially failed, or cancelled, the text, buttons, and next actions should remain consistent. If the frontend only optimizes successful rendering, operations teams cannot explain abnormal paths. If the backend returns only internal error codes, users cannot continue the task. Dialogue UI quality is visible in whether these intermediate states can be understood and handled.

A first version can use a lightweight acceptance checklist for the dialogue entry point: whether messages remain complete after reconnection, whether tool failure preserves context, whether user cancellation stops backend execution, whether expired approval buttons become invalid, and whether frontend events appear in Trace. The checklist does not need to cover every experience detail, but it should cover states that affect business responsibility. The dialogue entry point then becomes an operable task interface instead of a window that shows only successful paths.

## 47.11 Incident material for dialogue interfaces

When a dialogue interface fails, users usually report symptoms such as "it got stuck", "nothing came back", or "the button does not work." Engineering teams need enough material to translate those symptoms into a diagnosable event. A frontend incident should preserve session id, Run id, message index, streaming event index, last successfully rendered block, frontend error, backend state, tool-call state, and the message shown to the user. Without these records, debugging moves back and forth among frontend, gateway, Runtime, and model service.

Incident material should also include user actions. Refreshing the page, cancelling the task, submitting the same request twice, or closing the window before approval changes backend behavior. The frontend should write these actions into the event stream, while avoiding full logging of sensitive raw content. Observability for dialogue UI should support task review without turning the chat window into another leakage surface.

A first version can maintain several fixed incident samples: streaming interruption, tool timeout, expired approval, permission denial, attachment parsing failure, and user cancellation. Each sample should let reviewers jump from frontend timeline to backend Trace. Dialogue UI quality then covers operating governance as well as visual experience.

## 47.12 Review cadence for dialogue interaction contracts

Dialogue interaction contracts need periodic review after the first release. The UI usually evolves faster than Runtime: product teams add an export button, a new attachment type, a chart editor, a report drawer, or an approval card, while the backend event model changes more slowly. If these changes are treated as page work, the contract between UI state and platform state becomes unclear. A quarterly review can inspect whether every visible action still maps to a backend event, whether each event has an owner, and whether the support team can explain the state shown on screen.

The review should include real incidents along with component screenshots. Teams can sample recent user reports and rebuild the event path: what the user clicked, which event reached the frontend, which Runtime state was active, which tool result arrived late, and what message was shown. This exercise often exposes small defects that are invisible in design review. For example, a disabled button may look correct, but the backend might still accept the same action through a retry event. A cancelled stream may disappear from the page, while a long-running tool continues to execute.

Interaction contracts also need compatibility rules. Mobile clients, embedded widgets, customer-service consoles, and analytics pipelines may consume the same event stream. Removing a field or changing a state name can break recovery outside the main web app. The platform should mark deprecated fields, keep replay samples for old runs, and define how long older clients remain supported. This discipline keeps the dialogue interface from becoming a collection of local assumptions.

The final review question is whether the UI still supports the platform's governance model. Evidence expansion, report editing, approval, export, feedback, and cancellation should all produce structured records. If a new interaction cannot be traced, evaluated, or audited, it is not ready for enterprise use even if it feels convenient in the browser.

## 47.13 State recovery and user communication

Much of dialogue UI reliability comes from recovery behavior. Users close the browser, lose network for a few seconds, move a phone app into the background, or reconnect through a corporate proxy. The frontend connection may break while the backend Run continues. The interface should not treat a broken connection as task failure, and it should not create a new task after every refresh. A better design separates frontend session, backend Run, streaming cursor, and artifact state. When the page recovers, the frontend first reads the latest Run state and then fills missing events from the cursor. If the Run has moved into a long-task queue, the UI should show queue state and the next expected step instead of replaying a partial token stream.

Recovery logic must also prevent duplicate actions. If a user clicks "generate report" several times while waiting for a tool result, the frontend should return the existing `run_id` or clearly show that a task is already running. If a user refreshes after approving an action, the server should use an idempotency key to decide whether the approval already took effect. If a user cancels a task and later reopens the page, the interface should show the cancellation result and available recovery options instead of an old loading state. Every high-risk UI action needs backend state and idempotency semantics; a disabled button in the browser is not enough protection.

User communication should be organized around task state. The system can say "querying data," "waiting for approval," "moved to async generation," "authorization required," or "cancelled and ready to resubmit" without exposing model, queue, or tool internals. Messages should distinguish temporary waiting, recoverable failure, permanent rejection, and human-handling paths. If every problem becomes "generation failed," users retry blindly. If every wait becomes "processing," users do not know whether they should provide more information. Clear state messaging reduces duplicate submissions and lowers support cost.

A first version can define recovery acceptance samples: page refresh, network reconnect, duplicate submission, returning after approval, long-task recovery, and concurrent actions from multiple browser tabs. Each sample should check frontend display, backend Run, Trace, artifact state, and visible user actions. This moves dialogue UI quality from visual review into runtime review. The frontend becomes part of the Agent platform contract, with behavior that must match backend state.

## 47.14 Consistency governance across entry points

An enterprise Agent UI rarely lives in one web page. Customer-service consoles, data-analysis plugins, mobile apps, enterprise messaging, embedded BI pages, and internal operations tools may all connect to the same Agent Runtime. If each entry point defines its own message states, button actions, and error text, users will see different meanings for the same task. Support teams will also struggle to replay a Run. Consistency governance should define session, Run, Step, Artifact, approval, and export states as platform contracts instead of leaving each frontend team to interpret them locally.

The first requirement is shared event semantics. A `run_cancelled` event should mean that the backend task has entered cancellation state on web, mobile, and service-console clients. It should never be implemented as a local action that only hides a loading indicator in the current page. An approval card should enforce the same permission, expiry, and idempotency rules across entry points. Layout can differ, but the business action cannot. If a user cancels a task on mobile while the desktop workspace keeps generating a report, the platform has created a state conflict that is difficult to explain.

Entry points should also share replay and support material. A user may ask the first question in a messaging app, continue editing a report in a web workspace, and later open the artifact from an email link. Support staff should be able to follow the same `run_id` across those surfaces. The platform can require every entry point to record entry type, client version, event-protocol version, visible action, and local error. During incident review, the team can then tell whether the problem came from Runtime, network, frontend version, or an entry point that did not implement a new state.

A first version can keep this governance to a few strict rules: core event names are shared, idempotency keys are shared, high-risk actions require server confirmation, error states use the same message dictionary, and every entry point can reach Trace or a support view. The interface can still look different across products. The task semantics remain stable. For enterprise deployment, this matters more than visual polish because it determines whether the Agent can be operated reliably across business surfaces.

## 47.15 Regression samples for frontend exception paths

Dialogue UI quality cannot be judged only by the main happy path. Enterprise Agent frontends need regression samples for exception paths: reconnect after SSE disconnect, duplicate event delivery, late tool-call results, token arrival after user cancellation, approval-state changes, mobile backgrounding, browser refresh, session expiry, and the same Run opened on multiple devices. Each sample should record initial state, event sequence, expected frontend state, and backend Run state. Frontend fixes can then be replayed together with the Runtime event model instead of being checked only through manual page clicking.

Regression samples should also cover user communication. When a task fails, the interface should tell the user what action remains available: retry, add information, wait for approval, inspect generated material, contact support, or start a new task. If the UI only says that an error occurred, users tend to submit the task again and create duplicate Runs. If every abnormal case is shown as the model still thinking, users misunderstand system state. Error copy, button state, and event subscription should be tested in the same sample set.

A first version can start with ten frequent exceptions and connect them to frontend unit tests and browser replay. The samples should run whenever Runtime event protocol, Artifact workspace, or HITL flow changes. Dialogue UI is not a chat shell; it is the user's entry point into platform runtime state. Stable exception paths make long-running and high-risk tasks easier to trust.

Regression samples should include cross-entry behavior. A user may start a Run in a web workspace, approve it from a mobile notification, and later inspect the result in an embedded business console. The same Run should carry one task state, one approval record, and one artifact version across those surfaces. If each client stores local status, the platform can show different versions of the same task. Acceptance should therefore replay device switching, stale client versions, expired sessions, and delayed notifications. These samples are more useful than another visual review because they test whether the interface still matches Runtime.

Dialogue UI also needs evidence for support teams. When a user reports that an answer disappeared or a button became invalid, support should not ask for screenshots as the main diagnostic record. The platform should provide a support view with client version, event cursor, last rendered block, backend state, tool state, visible user action, and error message. Sensitive content can remain masked while the state path stays visible. This lets support distinguish frontend rendering failure, backend timeout, permission refusal, tool error, and user cancellation. Without this evidence, every incident sounds like model failure and the wrong team receives the ticket.

Long-running tasks require a different interaction rhythm from ordinary chat. Report generation, data extraction, file parsing, and approval waiting can take minutes or hours. The interface should offer stable task cards, async notification, resumable artifacts, and clear ownership of waiting states. Users should be able to leave the page and return without losing context. If the system needs user input, the card should state what is missing and who can act. If the system is waiting on a human approver, it should show expiry and escalation path. This reduces repeated prompting and keeps high-value tasks inside the platform record.

The UI contract should also protect users from stale actions. A card generated yesterday may contain an export button, an approval button, or a rerun button whose conditions have changed. Permissions may have expired, data may have been updated, and the underlying artifact may have been withdrawn. High-risk actions should revalidate state on the server before execution. The frontend can show the button, but the backend decides whether the action is still valid. This design prevents old UI state from becoming an accidental privilege path.

For a first version, the dialogue UI can define a small set of operating states: composing, queued, running, waiting for tool, waiting for approval, partially failed, completed, cancelled, and expired. Each state should have allowed user actions, visible message, Trace event, and recovery path. Product teams can still design different layouts, but the semantics stay stable. When dialogue interfaces follow this contract, they become part of the platform's operating model instead of a thin wrapper around model output.

## 47.16 Operating support view and issue diagnosis

After a dialogue UI reaches production, support teams need evidence that is more reliable than screenshots. User reports such as "the answer disappeared," "the button stopped working," or "it keeps generating" can mean frontend rendering failure, backend timeout, permission refusal, tool error, user cancellation, event loss, or an old client version. If support can only ask the user to repeat the action, the issue is hard to reproduce and users will treat every abnormal case as model instability.

The platform should provide an operating support view that places frontend and backend state on one page. The view can show client version, entry point, event cursor, last rendered block, backend Run state, current Step, tool state, visible user action, error message, and Trace link. Sensitive content can remain masked while the state path stays visible. Support can then tell whether the frontend missed an event, the backend completed without showing an artifact, the user's permission expired, or an approval action was no longer valid.

The same view helps engineering teams locate version issues. If one abnormal pattern clusters on old mobile clients, the repair path is client upgrade and compatibility. If it clusters on one event-protocol version, the repair path is the reducer and event contract. If it clusters on long-task recovery, the repair path is Run cursor and artifact-state synchronization. Without this evidence, frontend incidents keep moving to the Runtime team, while the Runtime team cannot reproduce them.

A first version can keep the support view internal. It shows runtime state, event version, error category, and a masked task summary. When a user report becomes a ticket, support binds it to `run_id` and entry point before deciding whether to route it to frontend, platform, data, or security teams. Dialogue UI operations then move from "the page can be used" to "issues can be diagnosed."

## 47.17 Failure-path expression in conversational UI

When failure-path expression in conversational ui reaches production, the platform needs a shared evidence standard for task state, streaming fragment, cancel entry, retry note, tool error, human takeover, and final artifact. This standard is not paperwork for its own sake. It lets business, platform, data, security, and operations teams discuss the same facts. Without this material, incident review depends on memory and personal judgment. With it, the team can see which inputs were valid, which actions executed, which artifacts can still be used, and which results need correction or withdrawal.

This evidence should connect to Chapter 22 on Runtime, Chapter 38 on Trace, and Chapter 50 on security. The upstream chapters provide the capability base, downstream chapters consume the runtime result, and this chapter explains how the middle layer is verified. If a capability looks complete inside one chapter but cannot enter Trace, Eval, release records, or the compliance evidence package, the production system still has a break in the chain. Readers should treat cross-chapter interfaces as engineering contracts, not as a reading order.

Common risks include users unable to distinguish reasoning from execution, background work continuing after cancellation, and tool failures being presented as ordinary replies. A successful demo rarely exposes these problems because demo samples are usually clean, short, and direct. Real business traffic brings stale data, abnormal input, permission changes, user withdrawal, budget limits, and long-running state. If the platform does not turn those situations into samples and ledgers, later scenarios will hit the same class of issues again.

Users unable to distinguish reasoning from execution should be turned into a tracked review item when it appears repeatedly. The operating record should at least state owner, version, sample, affected scope, action, and review time. It does not need to become a long process report, but it must be clear enough for a later maintainer to understand the decision. For high-risk capability, the record should also state which conditions allow wider use and which failures require degradation or withdrawal.

A first version can build this habit in a few representative scenarios. It is better to make high-traffic, high-risk, externally visible paths solid first, then copy the sample, ledger, and review method to related capabilities in other chapters. This makes the chapter read like engineering guidance: it explains how the capability is integrated, validated, operated, and retired.

## Chapter Recap

Dialogue UI is part of the enterprise Agent platform contract. It should expose task state, tool execution, evidence, approval, artifacts, and recovery paths. Streaming output needs structured events, stable ids, and deterministic reducers. Frameworks can accelerate implementation, but production readiness depends on state consistency, observability, permission boundaries, and replayable evidence.

## References

Vercel. (n.d.). [AI SDK documentation](https://sdk.vercel.ai/docs). assistant-ui. (n.d.). [Documentation](https://www.assistant-ui.com/). CopilotKit. (n.d.). [Documentation](https://docs.copilotkit.ai/). AG-UI. (n.d.). [Protocol documentation](https://docs.ag-ui.com/).
