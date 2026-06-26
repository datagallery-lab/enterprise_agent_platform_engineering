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

The protocol should use stable identifiers. A message id, run id, step id, tool call id, and artifact id let the frontend update the right element instead of appending duplicate cards. Idempotency matters because networks reconnect and SSE clients may replay events.

Version compatibility belongs in the protocol as well. A frontend released this week may connect to a backend service released next week, and cached pages may keep an older reducer in the browser. Events should therefore include a schema version and optional fields should have documented defaults. When the backend adds a new event type, the frontend should degrade gracefully by showing a generic status card instead of dropping the event silently.

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

This is also where frontend errors become debuggable. If a card appears twice, the reducer should reveal whether the backend emitted duplicate ids or the client applied the same event twice. If text arrives after completion, the reducer should reject or quarantine the event rather than silently mutating a completed answer.

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

The platform should avoid binding backend semantics to one UI library. A stable event protocol lets teams replace components without changing Runtime.

Procurement decisions should separate component maturity from platform fit. A polished chat component can reduce frontend work but still leave the team to implement approval state, tool evidence, tenant masking, and trace correlation. A lower-level SDK may require more UI work but fit a custom Runtime better. The decision should be made with a small production-like flow, such as a DataAgent query that includes SQL generation, chart rendering, evidence display, feedback, and an approval branch.

### 47.4.1 SSE, WebSocket, and HTTP chunked response

SSE is simple and works well for one-way event streams from backend to browser. It fits most Agent progress output. WebSocket is useful when the client also sends frequent control messages, such as real-time voice, collaborative editing, or low-latency interruption. HTTP chunked response is easy for text generation but usually too weak for structured Agent events.

The choice should reflect control requirements. If the user only receives progress, SSE is often enough. If the user can interrupt, approve, edit, and speak while the Agent runs, the system may need WebSocket or a separate control channel.

Operational constraints matter too. SSE is easier to pass through many enterprise gateways, but long-lived connections still need heartbeat and timeout policy. WebSocket gives more control, but some corporate networks inspect or block it. HTTP chunked response is widely supported, yet it often mixes text and control information in ways that become hard to evolve. The platform should document the failure behavior for each choice: reconnect delay, last event id, duplicate handling, and user-visible error copy.

### 47.4.2 Self-built protocol and UI SDK

A self-built protocol is justified when enterprise state is richer than the public SDK model. The protocol should define event types, required ids, allowed status transitions, error payloads, reconnect behavior, and compatibility rules. A small internal UI SDK can then expose hooks such as `useRun`, `useMessages`, `useToolCards`, and `useArtifacts`.

The risk is protocol drift. If every application adds private event fields, shared components lose value. Platform teams should publish versioned event schemas and regression samples.

### 47.4.3 Client-side token stitching and event reducer

Client-side token stitching looks simple but fails easily under reconnect, retry, and cancellation. The reducer should know whether a delta belongs to the active message block, whether it has already been applied, and whether the message has reached a terminal status.

For tool and approval events, the reducer should update structured objects instead of appending text. This keeps operational state separate from narrative explanation and makes audit replay possible.

### 47.4.4 Domestic enterprise Agent and DataAgent UI comparison

Many domestic enterprise Agent and DataAgent products expose similar UI elements: question input, SQL or tool progress, chart cards, evidence references, report export, and feedback. The difference lies in how much of that UI is backed by platform state. A demo can show a chart after a query. A production platform needs the chart to connect to query id, metric definition, permission result, data version, and evaluation feedback.

When reviewing products or internal implementations, look past visual polish. Check whether each visible element has a backend object and whether that object can be traced.

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

## Chapter Recap

Dialogue UI is part of the enterprise Agent platform contract. It should expose task state, tool execution, evidence, approval, artifacts, and recovery paths. Streaming output needs structured events, stable ids, and deterministic reducers. Frameworks can accelerate implementation, but production readiness depends on state consistency, observability, permission boundaries, and replayable evidence.

## References

Vercel. (n.d.). [AI SDK documentation](https://sdk.vercel.ai/docs).

assistant-ui. (n.d.). [Documentation](https://www.assistant-ui.com/).

CopilotKit. (n.d.). [Documentation](https://docs.copilotkit.ai/).

AG-UI. (n.d.). [Protocol documentation](https://docs.ag-ui.com/).
