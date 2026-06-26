# Chapter 49 Multimodal Input and Voice Agent

---

Multimodal and voice interfaces widen the Agent input boundary. Users may upload files, screenshots, charts, audio, video, or speak in real time. These inputs are useful because enterprise work is rarely pure text. They also introduce parsing errors, permission risks, evidence gaps, latency constraints, and audit questions.

This chapter treats multimodal input as an admission and evidence problem. A file or voice stream should enter the Agent only after the platform knows its source, type, parsing status, permission boundary, retention policy, and relationship to the current task.

---

## 49.1 Domestic multimodal and voice Agent UI comparison

Current products often expose file upload, screenshot Q&A, document parsing, voice input, real-time transcription, and voice response. These features look similar on the surface. The production difference is whether the platform records parsing evidence, user permission, original-source retention, and model input boundaries.

The same feature can have different risk depending on task context. A screenshot in a support chat may be low risk after masking, while a screenshot in a finance workflow may contain customer identifiers, account balances, and internal comments. A voice transcript for note taking may be temporary, while a voice approval for a high-risk workflow may require stronger identity, retention, and replay rules. Product design should define these differences before the input enters the Agent.

*Table 49-1: Multimodal UI comparison dimensions. Source: Compiled by this book.*

| Dimension | Demo behavior | Production requirement |
| --- | --- | --- |
| File upload | User uploads and asks | Type check, virus scan, permission, parsing state |
| Image input | Model reads screenshot | OCR evidence, region reference, sensitive masking |
| Voice input | Speech becomes text | ASR confidence, interruption, transcript review |
| File reference | Context is attached | Versioned reference and retention policy |
| Audit | Chat log only | Input id, parser version, transcript, Trace |

## 49.2 Product boundary for multimodal input

The product should define which multimodal inputs are accepted for each task. A financial analysis Agent may accept spreadsheets and charts but reject arbitrary executables. A legal review Agent may accept contracts but require stronger retention and review rules. A customer service Agent may accept images but should avoid storing unnecessary personal data.

The UI should show parsing status and evidence quality. If a file is still parsing, the Agent should not pretend it has read it. If OCR confidence is low, the answer should either ask for clarification or mark the evidence as weak.

The boundary should also be visible in follow-up turns. When the user asks "use the document I uploaded earlier," the UI should show which document version is in scope. If a file expired or was deleted, the Agent should ask for a new upload instead of relying on stale embeddings. This prevents silent context drift, a common source of wrong answers in file-heavy workflows.

### 49.2.1 File, voice, and context-reference boundaries

Files, voice, and context references have different risks. Files may contain hidden metadata or sensitive fields. Voice may contain personal information and transcription errors. Context references may point to data the user can see in the product but the Agent is not allowed to use.

The platform should convert each input into a governed reference. The model receives a controlled representation, while the original object remains in storage with retention and access rules.

Reference objects should include enough metadata for review: uploader, task id, parser version, derived text version, permission scope, and retention state. The answer can then cite a file section, transcript segment, or screenshot region without exposing the raw object to every downstream component.

### 49.2.2 Admission conditions for multimodal input entering the Agent

An input should enter the Agent only after basic checks pass: supported type, size limit, malware scan where needed, user permission, parser availability, retention policy, and task relevance. If a check fails, the UI should explain the failure and provide a safe fallback.

Admission checks should run before expensive parsing whenever possible. Size, type, tenant, and user permission can be checked immediately. Parser availability and content quality are known later. Splitting these checks gives users faster feedback and gives operators clearer failure categories.

*Table 49-2: Multimodal input admission conditions. Source: Compiled by this book.*

| Condition | Why it matters |
| --- | --- |
| Supported type | Prevents unsafe or meaningless parsing |
| Permission | Keeps user-visible data separate from Agent-usable data |
| Parser status | Avoids answers based on incomplete extraction |
| Retention policy | Controls storage of sensitive originals |
| Task relevance | Reduces context pollution |

## 49.3 File upload and asynchronous parsing

File upload should be asynchronous. The frontend uploads the file, the backend creates a file object, and the parser pipeline extracts text, tables, images, metadata, and evidence spans. The Agent should receive references to parsed content only after the parser marks a version as ready.

The UI should expose intermediate states: uploaded, scanning, parsing, parsed, failed, expired, or deleted. These states help users understand why a file is not yet available and help operators diagnose parser failures.

Asynchronous parsing also protects the Agent runtime. Long document parsing should not block a live run or consume model context before extraction quality is known. The run can subscribe to file-ready events, or it can continue with available context and mark the missing file as pending. Either way, the final answer should state what evidence was actually included.

### 49.3.1 File upload and asynchronous parsing pipeline

A typical pipeline contains upload, validation, storage, parsing, indexing, evidence generation, and cleanup. Each stage should record status and error category. If parsing fails, the Agent can still answer from other context, but it should not claim to have read the failed file.

*Table 49-3: File parsing pipeline states. Source: Compiled by this book.*

| State | Meaning | UI behavior |
| --- | --- | --- |
| uploaded | File object created | Show pending status |
| scanning | Security checks running | Disable Agent use |
| parsing | Parser extracts content | Show progress |
| ready | Parsed version available | Allow reference in task |
| failed | Parser failed | Show reason and retry path |
| expired | Retention window ended | Remove from selectable context |

## 49.4 Voice Agent architecture

Voice Agent architecture usually contains capture, voice activity detection, ASR, dialogue runtime, TTS, playback, and interruption control. The Agent runtime should still remain the source of task state. ASR and TTS are interface services, not replacements for tool governance, approval, Trace, or evaluation.

Latency matters because users perceive voice interaction as continuous. The system may need partial transcription, streaming model output, and streaming TTS. These optimizations should not hide uncertainty. Low-confidence ASR segments should be marked or confirmed before high-risk actions.

Voice architecture should keep task state separate from audio state. A user may interrupt playback without cancelling the task, or cancel the task without deleting the transcript. Treating every interruption as a task failure makes voice interaction brittle. Treating every spoken confirmation as a completed approval creates risk. Runtime should receive explicit control events from the voice layer.

## 49.5 Real-time voice interaction control

Real-time voice interaction needs controls for interruption, barge-in, silence timeout, confirmation, and handoff. If the user interrupts, the system should cancel or pause the current generation and record the transition. If the Agent needs approval, voice UI should make the approval boundary explicit instead of treating spoken "yes" as a universal authorization.

Voice confirmation should be risk-aware. Low-risk preferences can be accepted through voice. High-risk actions such as sending a quote, updating a record, or approving a refund should require stronger identity and decision records.

Real-time voice also needs recovery paths. If ASR confidence drops, the system can repeat the recognized phrase, switch to text confirmation, or escalate to a human. If TTS fails, the session can continue in text mode. If network latency becomes high, the UI should show that the Agent is still listening or processing rather than leaving the user uncertain.

## 49.6 Multimodal permissions and audit trail

Multimodal permission is more complex than chat permission. A user may upload a file they can view but cannot share with a model. A screenshot may contain unrelated personal data. An audio recording may include another person's voice. The platform should record input source, uploader, access scope, parser version, derived references, and deletion state.

Audit records should avoid storing more than necessary. Store ids, hashes, parser versions, confidence, and evidence references. Store raw files or audio only when policy permits and the business purpose is clear.

Audit policy should distinguish original inputs from derived representations. A transcript may be retained for review while raw audio is deleted. OCR spans may be retained while the original screenshot is masked. Embeddings may need deletion when the source file expires. These choices should be explicit because multimodal inputs can create more derived data than teams expect.

### 49.6.1 Design constraints for multimodal interaction

Multimodal design should make hidden processing visible. Users should know whether the system is reading an uploaded file, a parsed excerpt, a screenshot region, or a transcript. The UI should separate original objects from derived text so users can review what the model actually saw.

#### Asynchronous parsing and synchronous Q&A

Synchronous Q&A should not wait indefinitely for slow parsing. If parsing is unfinished, the Agent can ask the user to wait, answer from available context, or create a follow-up task. The answer should state which files were included.

#### WebRTC, WebSocket, and recording upload

WebRTC suits low-latency voice sessions. WebSocket suits custom bidirectional control. Recording upload suits asynchronous review or batch transcription. The choice should follow latency, reliability, consent, and audit requirements.

#### Direct multimodal models and parser pipelines

Direct multimodal models are useful for images and mixed content, but parser pipelines provide stronger evidence control for documents, tables, and regulated files. Many enterprise tasks need both: model perception for flexible input and parser output for traceable evidence.

#### Preserving original audio and preserving only transcripts

Keeping original audio helps dispute resolution but increases privacy and retention risk. Keeping only transcripts lowers risk but may lose tone, speaker, and correction evidence. The policy should be explicit and task-specific.

## 49.7 Evidence governance for multimodal entry points

Every multimodal input should produce evidence references that the answer can cite. A spreadsheet cell, OCR span, screenshot region, audio timestamp, or transcript segment should have an id and version. When the Agent uses that evidence, the answer should point back to the reference instead of saying "based on the file" without detail.

Evidence governance also supports deletion. If a user deletes a file or retention expires, derived indexes and references should be removed or marked unavailable. Future runs should not silently use stale content.

Evaluation should include multimodal failure classes. File parsing may fail because of unsupported format, low OCR quality, table structure loss, or permission denial. Voice may fail because of ASR errors, speaker overlap, latency, or interruption handling. Classifying these failures helps the platform decide whether to improve parsers, UI guidance, model prompts, or operating policy.

## Chapter Recap

Multimodal and voice Agents need admission control, parser evidence, permission checks, retention rules, and audit trails. File upload should be asynchronous and stateful. Voice interaction needs interruption, confirmation, and transcript governance. The model should receive controlled references rather than unmanaged raw inputs. Production readiness depends on making multimodal evidence visible and recoverable.

## References

WebRTC. (n.d.). [WebRTC documentation](https://webrtc.org/).

OpenTelemetry. (n.d.). [Documentation](https://opentelemetry.io/docs/).

OWASP. (n.d.). [Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).
