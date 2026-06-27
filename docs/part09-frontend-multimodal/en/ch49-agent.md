# Chapter 49 Multimodal Input and Voice Agent

---

Multimodal and voice interfaces widen the Agent input boundary. Users may upload files, screenshots, charts, audio, video, or speak in real time. These inputs are useful because enterprise work is rarely pure text. They also introduce parsing errors, permission risks, evidence gaps, latency constraints, and audit questions. This chapter treats multimodal input as an admission and evidence problem. A file or voice stream should enter the Agent only after the platform knows its source, type, parsing status, permission boundary, retention policy, and relationship to the current task.

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

The product should define which multimodal inputs are accepted for each task. A financial analysis Agent may accept spreadsheets and charts but reject arbitrary executables. A legal review Agent may accept contracts but require stronger retention and review rules. A customer service Agent may accept images but should avoid storing unnecessary personal data. The UI should show parsing status and evidence quality. If a file is still parsing, the Agent should not pretend it has read it. If OCR confidence is low, the answer should either ask for clarification or mark the evidence as weak.

The boundary should also be visible in follow-up turns. When the user asks "use the document I uploaded earlier," the UI should show which document version is in scope. If a file expired or was deleted, the Agent should ask for a new upload instead of relying on stale embeddings. This prevents silent context drift, a common source of wrong answers in file-heavy workflows.

### 49.2.1 File, voice, and context-reference boundaries

Files, voice, and context references have different risks. Files may contain hidden metadata or sensitive fields. Voice may contain personal information and transcription errors. Context references may point to data the user can see in the product but the Agent is not allowed to use. The platform should convert each input into a governed reference. The model receives a controlled representation, while the original object remains in storage with retention and access rules. Reference objects should include enough metadata for review: uploader, task id, parser version, derived text version, permission scope, and retention state. The answer can then cite a file section, transcript segment, or screenshot region without exposing the raw object to every downstream component.

### 49.2.2 Admission conditions for multimodal input entering the Agent

An input should enter the Agent only after basic checks pass: supported type, size limit, malware scan where needed, user permission, parser availability, retention policy, and task relevance. If a check fails, the UI should explain the failure and provide a safe fallback. Admission checks should run before expensive parsing whenever possible. Size, type, tenant, and user permission can be checked immediately. Parser availability and content quality are known later. Splitting these checks gives users faster feedback and gives operators clearer failure categories.

*Table 49-2: Multimodal input admission conditions. Source: Compiled by this book.*

| Condition | Why it matters |
| --- | --- |
| Supported type | Prevents unsafe or meaningless parsing |
| Permission | Keeps user-visible data separate from Agent-usable data |
| Parser status | Avoids answers based on incomplete extraction |
| Retention policy | Controls storage of sensitive originals |
| Task relevance | Reduces context pollution |

## 49.3 File upload and asynchronous parsing

File upload should be asynchronous. The frontend uploads the file, the backend creates a file object, and the parser pipeline extracts text, tables, images, metadata, and evidence spans. The Agent should receive references to parsed content only after the parser marks a version as ready. The UI should expose intermediate states: uploaded, scanning, parsing, parsed, failed, expired, or deleted. These states help users understand why a file is not yet available and help operators diagnose parser failures.

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

Voice Agent architecture usually contains capture, voice activity detection, ASR, dialogue runtime, TTS, playback, and interruption control. The Agent runtime should still remain the source of task state. ASR and TTS are interface services, not replacements for tool governance, approval, Trace, or evaluation. Latency matters because users perceive voice interaction as continuous. The system may need partial transcription, streaming model output, and streaming TTS. These optimizations should not hide uncertainty. Low-confidence ASR segments should be marked or confirmed before high-risk actions.

Voice architecture should keep task state separate from audio state. A user may interrupt playback without cancelling the task, or cancel the task without deleting the transcript. Treating every interruption as a task failure makes voice interaction brittle. Treating every spoken confirmation as a completed approval creates risk. Runtime should receive explicit control events from the voice layer.

## 49.5 Real-time voice interaction control

Real-time voice interaction needs controls for interruption, barge-in, silence timeout, confirmation, and handoff. If the user interrupts, the system should cancel or pause the current generation and record the transition. If the Agent needs approval, voice UI should make the approval boundary explicit instead of treating spoken "yes" as a universal authorization. Voice confirmation should be risk-aware. Low-risk preferences can be accepted through voice. High-risk actions such as sending a quote, updating a record, or approving a refund should require stronger identity and decision records.

Real-time voice also needs recovery paths. If ASR confidence drops, the system can repeat the recognized phrase, switch to text confirmation, or escalate to a human. If TTS fails, the session can continue in text mode. If network latency becomes high, the UI should show that the Agent is still listening or processing instead of leaving the user uncertain.

## 49.6 Multimodal permissions and audit trail

Multimodal permission is more complex than chat permission. A user may upload a file they can view but cannot share with a model. A screenshot may contain unrelated personal data. An audio recording may include another person's voice. The platform should record input source, uploader, access scope, parser version, derived references, and deletion state. Audit records should avoid storing more than necessary. Store ids, hashes, parser versions, confidence, and evidence references. Store raw files or audio only when policy permits and the business purpose is clear.

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

Every multimodal input should produce evidence references that the answer can cite. A spreadsheet cell, OCR span, screenshot region, audio timestamp, or transcript segment should have an id and version. When the Agent uses that evidence, the answer should point back to the reference instead of saying "based on the file" without detail. Evidence governance also supports deletion. If a user deletes a file or retention expires, derived indexes and references should be removed or marked unavailable. Future runs should not silently use stale content.

Evaluation should include multimodal failure classes. File parsing may fail because of unsupported format, low OCR quality, table structure loss, or permission denial. Voice may fail because of ASR errors, speaker overlap, latency, or interruption handling. Classifying these failures helps the platform decide whether to improve parsers, UI guidance, model prompts, or operating policy.

## 49.8 Multimodal task recovery and cost control

Multimodal tasks need recovery design more than text tasks. File parsing may run for minutes. Voice sessions may be interrupted by the network. Video frame extraction may wait in a queue. OCR may require a person to confirm key fields. When a user leaves the page and returns later, the system should show the state of each input object: whether the original file still exists, whether the parsed version is ready, which spans entered context, which evidence needs renewed authorization, and which tool calls already happened. If the frontend stores only conversation text, recovery cannot explain which image, audio timestamp, or table cell supported a conclusion.

Recovery design should separate task state from input state. The task may fail while file parsing succeeds. The voice connection may drop while transcript segments remain usable. A user may cancel one answer without deleting the uploaded file. Runtime should record these states separately. On recovery, the frontend should load the task snapshot, then related input objects and evidence references, and then subscribe to later events. The user can continue from the failed position without uploading the same file again or restating context. For customer-service recordings, invoice recognition, and business-analysis screenshots, this behavior directly affects production usability.

Multimodal input can also expand cost quickly. OCR, ASR, video frame extraction, multimodal embeddings, and visual model calls are heavier than text processing. The platform should control cost at admission time: limit file size and page count, choose parsing depth by task type, reuse parsed versions, avoid parsing the same file repeatedly across sessions, and send large files into asynchronous queues. The frontend should tell users what the system is processing instead of describing all waiting time as Agent thinking. Operations views should separate parsing cost, model cost, storage cost, and human review cost. Otherwise teams only see a rising model bill and cannot tell which input form caused it.

Cost control should not weaken evidence quality. Skipping OCR confidence, table structure, audio timestamps, or parser versions may save money during processing and create larger audit cost later. A better policy is risk-based parsing. Low-risk image Q&A can use lightweight extraction. High-risk invoices and contracts should keep field-level evidence. Real-time voice assistants may retain only transcript and confirmation records. Dispute-resolution scenarios may retain original audio under stricter policy. Different tasks need different evidence, so parsing depth should follow task risk.

The first platform version can start with a multimodal input ledger. The ledger records input id, source, uploader, task, parser version, derived text version, evidence references, retention window, cost category, and deletion state. Agent answers, multimodal evaluation, permission audit, and cost analysis all read from this ledger. With it, multimodal capability becomes recoverable, auditable, and operable instead of staying as a loose combination of an upload control and a model endpoint.

## 49.9 Operating review for multimodal workloads

Operating review for multimodal workloads should inspect input quality, parsing quality, user behavior, and business outcome together. Input quality includes file size, page count, format, resolution, recording noise, and video length. Parsing quality includes OCR confidence, table-structure retention, ASR word errors, speaker separation, and timestamp accuracy. User behavior includes repeated uploads, cancelled parsing, fallback to text, manual correction, and rejected confirmation cards. Business outcome includes whether tickets were created correctly, invoices entered review, and reports cited the right regions. Looking only at final model answers misses problems that happened earlier in the multimodal chain.

The review should also separate input problems from platform problems. A blurry receipt may call for better capture guidance. Clear receipts of the same type failing often point to parser or template issues. Voice confirmations that are often rejected may come from low ASR confidence or from confirmation cards that fail to explain the impact of the action. Multimodal operations should assign these issues to the right owners: product owns upload guidance and confirmation interaction, platform owns the input ledger and evidence references, model or parsing teams own OCR, ASR, and visual understanding, and security owns retention, masking, and deletion. Once ownership is clear, multimodal features move from upload and recognition toward sustained operations.

The first version can start with a small metric set: parsing failure rate, human confirmation rate, repeated upload rate, missing evidence-reference rate, raw-input deletion delay, and parsing cost per task. The metrics do not need to be numerous, but each should trigger an action. High parsing failure points to input quality and parser review. High confirmation rate points to risk classification and confirmation copy. Repeated uploads suggest knowledge-base ingestion or file reuse. Deletion delay points to derived-object cleanup. This keeps the chapter focused on engineering operations instead of only listing file, image, and voice capabilities.

## 49.10 Multimodal quality samples and human correction

Multimodal Agent review should separate input quality from model output. File parsing failure, speech-recognition errors, missing OCR fields, incorrect screenshot cropping, and unclear file permissions can all distort the final answer. If review only inspects the model response, teams may misread parsing issues as reasoning issues. The platform should preserve quality samples from the parsing stage: original file type, parser version, recognized text, confidence, human correction, permission label, and later usage.

Human correction is a strong data source for multimodal chains. When users fix speech transcripts, add image descriptions, select document pages manually, or redraw screenshot regions, they show where the system is unstable. These corrections should return to OCR, ASR, file parsing, evidence citation, and evaluation sets instead of serving only the current session. For high-risk scenarios, the platform should ask users to confirm key fields before multimodal material is cited, such as contract amount, customer name, date, and approval comment.

Quality samples should also affect cost policy. Large-file parsing, long-audio transcription, and batch image OCR can consume substantial resources. If parsing quality is low, sending the result to a model only expands cost and error. The platform can set quality gates: low confidence asks for human confirmation, large files move to async processing, repeated uploads reuse parsing results, and sensitive files without permission are blocked. Multimodal entry points then become reliable data sources instead of unstable noise inside model context.

## 49.11 Replay and correction for multimodal entry points

Multimodal tasks need replay. After voice, screenshots, PDFs, spreadsheets, and images enter an Agent, the system should keep input references, parser versions, recognition results, user corrections, tool calls, and final artifacts. Replay does not mean keeping every raw object without limits. It means being able to explain what the system saw, how it interpreted the input, and where the user corrected it when a dispute appears. If only the final answer remains, OCR mistakes, transcription errors, screenshot cropping mistakes, and file-version mistakes all blur together.

Correction should stay close to the original evidence. If the transcript is wrong, the user should be able to correct it and rerun later steps. If table parsing is wrong, the user should be able to mark columns or cell ranges. If image recognition is wrong, the user should be able to select an area or add a note. Once correction records enter Trace, the platform can see which parsers, file types, and business scenarios fail often. Multimodal quality then improves from real tasks and from offline samples, with production corrections carrying the stronger signal.

A first multimodal platform version can keep a minimum replay record: input artifact id, parser version, recognized text, user correction, downstream tool calls, and output artifact. For sensitive content, the raw file can be stored under restricted access while Trace keeps references and redacted summaries. Multimodal entry points reduce user effort, but they also introduce more interpretation errors. Replay and correction decide whether those errors can be fixed over time.

## 49.12 Task-tier acceptance for multimodal input

Multimodal input should be accepted by task risk tier. Voice transcription for meeting notes, screenshot recognition for troubleshooting, scanned contracts for clause review, and invoice images for finance processing tolerate errors differently. A recognition error in meeting notes may be a wording issue. The same kind of error in finance or legal work can lead to wrong payment, wrong filing, or wrong risk judgment.

Acceptance material should record input type, parser version, human-correction rate, wrong fields, downstream tool calls, and business impact. Low-risk tasks can allow later user editing. High-risk tasks should require confirmation on key fields such as amount, party, date, contract clause, and approval target. The product boundary of multimodal capability should be tied to these confirmation points. The fact that the system can recognize content does not mean it can execute automatically.

A first version can set a default treatment for each input type. Voice produces a draft first. Screenshots enter troubleshooting context first. Contracts and invoices enter review state first. After enough samples are stable, the platform can open more automated actions gradually. Multimodal entry points then reduce input effort while keeping the caution required by production systems.

## 49.13 Dataset construction for multimodal acceptance

Multimodal acceptance needs a dataset, not a few impressive examples. The dataset should include clean inputs, noisy inputs, partial inputs, unsupported formats, permission-denied files, low-confidence parses, and cases where the correct action is to ask for human confirmation. A finance invoice set, for example, should contain clear images, tilted photos, missing tax fields, repeated uploads, currency ambiguity, and samples where OCR confidence is high but the business rule still requires review.

The dataset should preserve layered labels. One label describes input quality, another describes parser quality, another describes evidence quality, and another describes task outcome. This separation prevents a common mistake: blaming the model for a wrong answer when the real defect came from missing table structure or a clipped screenshot. It also helps teams choose the right fix. Some failures need better capture guidance, some need a parser upgrade, some need a stricter permission check, and some need a clearer confirmation card.

Multimodal acceptance datasets should also include deletion and retention cases. A file may expire before a later Run, a user may withdraw consent for audio retention, or a derived embedding may need removal after the source document is deleted. If these cases are absent, the platform may pass functional tests while failing compliance operations. The acceptance dataset should therefore store expected cleanup behavior together with expected extraction behavior.

A first version can build small datasets for three frequent workloads: document upload, screenshot troubleshooting, and voice confirmation. Each dataset should be connected to Trace samples and user correction records. As production traffic grows, real corrections can replace synthetic cases. This keeps multimodal quality grounded in actual work instead of model demos.

## 49.14 Privacy and retention policy for multimodal data

Multimodal input often contains more private information than text. A screenshot may include customer names, internal system URLs, browser bookmarks, and an unrelated chat window. A voice recording may contain bystander speech, meeting background, and discussion that was not meant for the Agent. A scanned document may bring signatures, national identifiers, contract numbers, and handwritten notes into the same upload. The platform should not treat these inputs only as richer context. They are data assets that need classification, cropping, masking, and retention control before they become model context.

Privacy policy should start at the upload entry point. Before upload, the UI can ask users to confirm material type and sensitivity level. After upload, the file can enter an isolation area where parsers extract metadata, page numbers, audio segments, screenshot regions, and confidence scores before the system decides what reaches the model. For screenshots and images, the platform can prefer user-selected regions and restrict access to the original file. For voice, it can retain transcript and required timestamps while applying shorter retention to raw audio. For scanned documents, it can authorize structured fields, evidence coordinates, and original-file access separately. The model then receives controlled references instead of an unmanaged raw file.

Retention policy should cover derived artifacts as well. OCR text, embeddings, summaries, transcripts, thumbnails, VLM descriptions, and human correction records may continue to contain sensitive information. After the source file is deleted, the platform should know which derived objects must be removed, which audit records may remain, and which report artifacts need an "evidence unavailable" mark. Deleting only the original object from storage is not enough if vector indexes, caches, and historical answers still contain content. A multimodal platform needs a deletion path that connects source file, parser version, citation span, embedding, artifact, and Trace.

A first version can classify multimodal data into three risk bands. Low-risk material can use short-term cache and automatic parsing. Medium-risk material should use controlled parsing and sampling. High-risk material should require confirmation, masking, and short retention by default. This classification will not cover every regulatory detail on day one, but it gives product, platform, security, and compliance teams one operating language. Multimodal input lowers user effort and brings complex material into Agent tasks inside an auditable boundary.

This policy also affects evaluation. Acceptance samples should include privacy failures: screenshots with unrelated windows, audio with bystander speech, scans with personal identifiers, and documents whose source files are deleted after indexing. The expected result may be cropping, masking, rejection, human review, or deletion propagation. Without these samples, the model may appear capable while the platform remains unsafe for real enterprise material.

## 49.15 Confirmation boundaries for real-time voice tasks

Real-time voice interaction can make users believe that "the system understood me" means "the system may act." In enterprise workflows, that assumption is risky. Transcripts are affected by noise, accent, interruption, multiple speakers, and omitted context. A user may mix a question, suggestion, and authorization in one spoken sentence. The platform should not treat the live transcript as final intent, especially for actions with side effects such as payment, approval, export, deletion, outbound calls, or ticket closure.

Confirmation boundaries should follow action risk. Low-risk questions can be answered during the conversation, while the transcript remains part of evidence. Medium-risk actions should repeat key fields such as object, amount, time, scope, and recipient. High-risk actions should become structured confirmation cards and require explicit approval. If a user says, "send this report to the team," the system should identify which artifact "this report" means, what recipient group "the team" refers to, whether sensitive fields are included, and whether approval is required. Missing fields should trigger clarification instead of guessing from recent context.

Voice confirmation also has to handle interruption and cancellation. A user may interrupt while the Agent is restating an action, or say "never mind" before execution. The platform should separate voice turn, confirmation state, and execution state: listening, pending confirmation, confirmed, executing, cancelled, and failed. Only a structured action in confirmed state should reach a tool. If network delay causes the user to hear an old state, `run_id` and action version should still prevent duplicate execution. Real-time experience can be fluid, but side-effecting actions need a stable state machine.

A first version can limit voice Agents to read-only Q&A, draft generation, and low-risk operations. Actions that write to external systems can become text confirmation cards or human approvals. This does not reduce the value of the voice entry point. It builds trust: voice accelerates expression, while business-state changes still have visible confirmation and audit evidence.

## 49.16 User recovery for multimodal parsing failures

Multimodal entry points should treat parsing failure as a recoverable flow. Wrong page detection, shifted OCR table columns, missing words in speech transcription, incorrect screenshot selection, and low-confidence image evidence should not push the task straight to failure or leave the model to guess. The frontend should show the failure location and let the user reselect pages, correct fields, confirm a speech segment, select an image region, or switch to text input. The recovery action should remain inside the same Run so later Trace can explain why the result changed.

Recovery should also control cost. Re-parsing a large file, retranscribing long audio, or reprocessing an image can consume substantial resources. The platform can rerun only the segment changed by the user and keep unchanged parts bound to the old artifact. It can also mark low-confidence fields as waiting for confirmation instead of rerunning the whole input. Users can then repair mistakes while the system avoids repeated OCR, ASR, and model calls after one parsing failure.

A first version can define recovery protocols for three input classes: document recovery at page and field level, speech recovery at time-segment level, and image recovery at selected-region level. Each recovery records original parsing, user correction, rerun scope, and final evidence reference. Multimodal Agent reliability comes from a correctable input chain, not from one-shot recognition accuracy.

Multimodal recovery should also preserve user effort. When a twenty-page contract fails on one table, users should not have to upload the whole file again and repeat every correction. The parser should keep page-level and block-level references so the platform can rerun the affected part. When a voice transcript has one wrong name, the user should be able to correct the segment and continue from the confirmation step. When an image region is cropped incorrectly, the system should let the user redraw the region and reuse the rest of the evidence. This makes recovery practical for real work, where inputs are large and corrections happen under time pressure.

Cost control starts before model calls. The platform can inspect file type, size, page count, image resolution, audio duration, language, and data sensitivity before deciding the processing path. A low-risk screenshot may enter synchronous parsing. A large contract may move to async extraction with page sampling. A long recording may be transcribed in segments and ask for human confirmation before summary. A sensitive scan may require masking before any model call. These decisions should be visible to users, because waiting time and review requirements are part of the product experience.

The evidence model should separate raw input, parsed representation, user correction, and downstream artifact. Raw input may have short retention and restricted access. Parsed text may be available to the model. User correction may become stronger evidence than the original parser output. Downstream artifacts may cite only selected spans or time ranges. If the platform collapses these layers into one text blob, it cannot explain errors, comply with deletion requests, or reuse corrected evidence. Multimodal capability becomes dependable only when these layers remain distinct.

Voice interaction adds another operating concern: turn-taking. People interrupt, correct themselves, speak over others, or use pronouns that refer to the screen. A voice Agent should keep a structured turn record with transcript, confidence, speaker or channel, visible context, candidate action, confirmation state, and cancellation state. The system can answer low-risk questions quickly, but actions with side effects should wait for structured confirmation. This keeps real-time voice useful while preventing casual speech from being treated as final authorization.

Multimodal acceptance should include adversarial and messy inputs. Screenshots can contain hidden prompts, documents can include malicious instructions, audio can include another speaker giving a command, and images can include unrelated sensitive fields. These cases should not be left to security review alone. They belong in the same dataset as ordinary OCR, ASR, and visual understanding samples, because the parser, permission layer, model, and frontend must respond together. A clean benchmark may show recognition ability, but messy samples show whether the platform can operate.

For a first version, teams can define supported input patterns narrowly: approved document upload, selected screenshot region, short voice note, and structured confirmation for risky actions. Each pattern should state maximum size, parser route, retention policy, correction method, and escalation path. Narrow support is easier to explain and safer to operate than accepting every file, image, and audio input at once. As production corrections accumulate, the platform can expand support with evidence and clear admission rules.

## 49.17 Multimodal admission samples and messy-input tests

Multimodal capabilities should not be accepted only with clean samples. Real enterprise inputs often include hidden prompts in screenshots, handwritten notes in scans, old policy clauses in attachments, another speaker's command in audio, unrelated sensitive fields in images, and merged cells in tables. If acceptance samples cover only standard files, clean speech, and tidy screenshots, the platform overestimates recognition ability and underestimates safety and permission risk.

Admission samples should include ordinary samples, boundary samples, and adversarial samples. Ordinary samples verify OCR, ASR, VLM, and file parsing. Boundary samples test low confidence, missing pages, wrong pages, shifted tables, multiple speakers, and mixed languages. Adversarial samples test instruction injection inside files, hidden commands in images, side-channel voice commands, and unrelated sensitive content. Each sample should record expected parsing result, evidence allowed into context, content to crop or mask, user recovery path, and safety handling.

Messy-input testing should feed product admission. If one input class often needs human correction, the platform can mark it as limited support and require async parsing or confirmation. If one input class frequently carries sensitive fields, the upload entry should add confirmation and masking. If one voice task often triggers accidental actions, the voice entry should stay read-only or convert actions to confirmation cards. Admission policy should change with sample evidence instead of staying fixed after release.

A first version can define a narrow supported set: controlled document upload, user-selected screenshot region, short voice note, and structured confirmation for risky actions. Each input type states maximum size, parser route, retention policy, recovery method, and escalation path. Narrow support is easier to operate and easier for enterprise readers to reason about. Multimodal design is not about sending every input to a model; it is about letting complex inputs enter a task through evidence, permission, and recovery controls.

## 49.18 Task admission guidance for multimodal input

Multimodal entry points should explain admission rules before users upload. File size, page count, selected image region, audio duration, sensitive fields, supported formats, and processing time all affect task quality. If the platform waits until parsing fails before showing limits, users have already spent time and may have uploaded material that should not enter the platform. Admission guidance should appear before upload, recording, and screenshot selection, and it should change with tenant policy.

The guidance should help users decide. For contract scans, the system can state that page and field confirmation may be required. For screenshots, it can ask users to select the relevant region and avoid unrelated windows. For voice, it can state that high-risk actions will move to text confirmation. For sensitive material, it can state retention and masking behavior. The message should not be a long instruction page. It should tell users how to prepare material so the task needs less rework.

A first version can define an admission card for each input type: supported scope, maximum limit, processing method, user correction point, retention policy, and escalation path. The frontend displays the card, and the backend enforces the same policy. Multimodal entry points then reduce invalid parsing and help users understand platform boundaries before the task begins.

## 49.19 Task-admission checks for multimodal input

When task-admission checks for multimodal input reaches production, the platform needs a shared evidence standard for input type, file source, recognition confidence, user intent, privacy level, human review, and failure message. This standard is not paperwork for its own sake. It lets business, platform, data, security, and operations teams discuss the same facts. Without this material, incident review depends on memory and personal judgment. With it, the team can see which inputs were valid, which actions executed, which artifacts can still be used, and which results need correction or withdrawal.

This evidence should connect to Chapter 19 on OCR, Chapter 47 on UI, and Chapter 50 on security. The upstream chapters provide the capability base, downstream chapters consume the runtime result, and this chapter explains how the middle layer is verified. If a capability looks complete inside one chapter but cannot enter Trace, Eval, release records, or the compliance evidence package, the production system still has a break in the chain. Readers should treat cross-chapter interfaces as engineering contracts, not as a reading order.

Common risks include speech-recognition errors entering tool calls, images being overinterpreted, and attachments containing sensitive information without notice. A successful demo rarely exposes these problems because demo samples are usually clean, short, and direct. Real business traffic brings stale data, abnormal input, permission changes, user withdrawal, budget limits, and long-running state. If the platform does not turn those situations into samples and ledgers, later scenarios will hit the same class of issues again.

Speech-recognition errors entering tool calls should be turned into a tracked review item when it appears repeatedly. The operating record should at least state owner, version, sample, affected scope, action, and review time. It does not need to become a long process report, but it must be clear enough for a later maintainer to understand the decision. For high-risk capability, the record should also state which conditions allow wider use and which failures require degradation or withdrawal.

A first version can build this habit in a few representative scenarios. It is better to make high-traffic, high-risk, externally visible paths solid first, then copy the sample, ledger, and review method to related capabilities in other chapters. This makes the chapter read like engineering guidance: it explains how the capability is integrated, validated, operated, and retired.

## Chapter Recap

Multimodal and voice Agents need admission control, parser evidence, permission checks, retention rules, and audit trails. File upload should be asynchronous and stateful. Voice interaction needs interruption, confirmation, and transcript governance. The model should receive controlled references instead of unmanaged raw inputs. Production readiness depends on making multimodal evidence visible and recoverable.

## References

WebRTC. (n.d.). [WebRTC documentation](https://webrtc.org/). OpenTelemetry. (n.d.). [Documentation](https://opentelemetry.io/docs/). OWASP. (n.d.). [Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/).
