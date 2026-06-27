# Chapter 42 SLO Management, Rate Limiting, and System Resilience

---

This chapter discusses SLO management, rate limiting, and system resilience, explaining how task-level service objectives, error budgets, degradation, checkpoints, and capacity strategies support stable operation. An Agent's SLO cannot simply copy the P99 latency of a web service: a single task may span multiple steps, invoke several tools, and wait for human approval. The SLO target must be defined along the task flow instead of per individual request. This chapter explains how to derive task-level SLOs from user promises, how to use error budgets to guide release cadence, and how rate limiting, degradation, and checkpoints help preserve core tasks during overload.

An Agent being able to answer questions doesn't mean it's ready for release. Teams need to determine whether a Monday morning traffic spike is really a traffic incident or a sign of goal misalignment; whether SLOs inferred from user expectations can be reproduced; and whether metrics expanded along the task chain can inform release, rate limiting, degradation, and optimization decisions.

## 42.1 Monday Morning Peak Is Not a Traffic Incident but a Goal Mismatch

At 9 AM Monday, the sales team starts generating weekly business reports. Each sales manager expects DataAgent to read sales data, explain anomalies, generate charts, and produce a briefing document for the regional manager. Early in production, the platform treated this flow as a normal synchronous request: the frontend sends one request; the backend launches models, queries databases, renders charts, generates documents, and returns everything at once.

Normally, this pipeline looks fine. Real faults occur during peak load: model services queue requests; database queries time out; chart rendering processes backlog; users see no progress and keep clicking "Regenerate." The entry request amplifies into many downstream tasks, and retries further overload downstream. The platform may not be completely down, even returning HTTP 200s, but users get no report and the business is effectively unavailable.

The root cause of such incidents is not "too much traffic" alone, but the platform failing to translate user expectations into engineering goals. Users may not demand a full PPT in 10 seconds, but they do want to see within 10 seconds that the task is accepted with current progress and expected completion time. Users accept queuing for the full report but not losing a task when refreshing the page. Users accept summaries during peak with a detailed version later, but not a system that bypasses permission checks to speed up.

### 42.1.1 SLO Is more than "System Must Be Stable"

SLO stands for Service Level Objective-a set of measurable, alertable, reviewable, and release-influencing targets, more than slogans. For example:

*Table 42-1: SLO targets aligned with user expectations and observability. Source: This book.*

| Objective       | User Expectation                              | Observability                                |
|-----------------|-----------------------------------------------|----------------------------------------------|
| Timely first response | User knows the task has started, not a blank page. | 95% of interactive tasks show progress or clarification within 5 seconds. |
| Final deliverable | User ultimately receives usable results, more than "processing." | Financial analysis tasks succeed at least 98% of the time. |
| Acceptable quality | Outputs are not rushed but error-prone summaries. | Core regression test pass rate above threshold; no online quality degradation. |
| No security compromises | Permissions, data masking, and approvals upheld even at peak or degraded modes. | High-risk tasks have zero unauthorized access. |
| Controllable cost | System does not maintain apparent success via infinite retries. | Average cost per successful task stays within budget. |

Traditional web service SLOs typically focus on availability, latency, and error rate. Agent platforms are far more complex: interface success ≠ Run success, Run success ≠ answer quality, fast generation may omit high-risk evidence. Enterprise Agent stability should be defined as: **users safely complete quality tasks within acceptable time and cost**. SLOs should span across gateways, runtime, models, tools, artifacts, and observability systems-more than entry services. Otherwise, the platform risks gaps between "technically available" and "business unavailable."

### 42.1.2 SLOs Target "Tasks," Not "Requests"

Granularity is the biggest source of misjudgment in Agent operations. One user click might trigger a Run, which contains multiple Steps, each possibly invoking models, tools, human approvals, artifact writes, and evaluation callbacks. Counting availability only by HTTP requests misses many real failures. For example, a weekly report task: an accepted request means only the platform accepted the task; successful SQL means data was retrieved; successful PPT generation means the artifact was produced. Only if these steps are chained correctly with proper permissions, scope, and cost is the task complete. Thus, Agent SLOs should be keyed on `run_id` instead of request ID. Chapter 38's Trace, Step, Checkpoint, and Artifact are the foundation of SLO calculation.

## 42.2 Deriving SLOs from User Promises: Define Scenarios First, Then Metrics

Not all Agents should share the same SLO. Interactive Q&A, long-running analysis, backend batch jobs, approval flows, and report generation all have different wait semantics and risks. Treating all as "user requests" results in vague or ineffective metrics.

### 42.2.1 Different Scenarios Have Different Wait Semantics

Interactive Q&A emphasizes first response: users accept initial info retrieval and answer supplementation but won't tolerate seconds of silence. Here SLOs split into first response (user sees system working) and final answer (task completion). Long-running tasks emphasize recoverability: CFO reports, batch contract analysis, multi-round financial attribution may take minutes or longer. Users might not watch the page but need queryable progress, failure reasons, and retries that don't redo completed side effects. Backend batch jobs emphasize deadlines and cost: 500 store summaries generated overnight don't need sub-second responsiveness but must finish by 8 AM without busting retry budgets. Approval flows emphasize permissions, audit, and human confirmation. Refunds, emails, writes, and status changes require safety above latency.

*Table 42-2: Wait semantics and SLO focus by scenario. Source: This book.*

| Scenario           | What Users Really Care About           | SLO Should Focus On                                  |
|--------------------|---------------------------------------|-----------------------------------------------------|
| Interactive Analysis | Fast progress display; usable final answer | First response, final completion time, task success rate, quality sampling |
| Long-running Reports | Persistent state; explainable failures | Queryable progress, checkpoint recovery, artifact traceability, notification reliability |
| Backend Batch      | Low-cost completion by deadline       | Throughput, deadline adherence, average cost, retry cost |
| High-risk Approval | No privilege escalation or bypass    | Permission hit rate, approval integrity, audit completeness, zero security violations |

This table illustrates the design sequence: first understand how users wait, then decide what the system promises. Otherwise, platforms risk imposing unrealistic second-level latencies on long jobs or dangerous retries on high-risk actions.

### 42.2.2 Separate Objectives from Guardrails

An effective SLO contains both objectives and guardrails. Objectives express what the platform optimizes; guardrails declare boundaries no optimization can break. For example, latency can be reduced by switching to a smaller model, but if quality sampling drops sharply, stability is not improved. Cost can be cut by limiting context, but if success criteria are missed, task success rate is a false positive. Here is an example for an interactive financial analysis Agent:

```yaml
slo:
  name: finance_dataagent_interactive
  scope:
    agent_id: dataagent_finance
    task_type: interactive_analysis
  objectives:
    monthly_availability: ">= 99.9%"
    first_response_p95_ms: 5000
    final_answer_p95_ms: 60000
    run_success_rate: ">= 98%"
    average_cost_per_successful_run_usd: "<= 0.20"
  guardrails:
    safety_violation_rate: "0"
    regression_set_pass_rate: ">= 97%"
    judge_score_p50: ">= 0.80"
    human_handoff_rate: "<= 5%"
```

The key is the structure: `objectives` are service promises to meet; `guardrails` are boundaries that cannot be compromised. For platform managers, this enables SLOs to govern product promises and release controls; for engineers, it maps to metric collection, alerts, and gateway policies; for AI researchers, it clarifies model optimization must balance score, quality, safety, and cost jointly.

### 42.2.3 Boundaries of SLI, SLO, and SLA

Service Level Indicator (SLI) is the actual measured value, e.g. "financial analysis task success rate was 98.6% over past 7 days." Service Level Objective (SLO) is an internal commitment, e.g. "success rate no less than 98%." Service Level Agreement (SLA) is a formal customer/business contract that may involve compensation or compliance.

One can view it as: SLI shows what's happening now; SLO indicates if targets are met; SLA governs external commitments. Internal Agent platform building typically starts with stable SLI collection, then uses SLOs to drive governance, and finally packages mature capabilities into SLAs. Premature SLAs without understanding failure causes turn into organizational problems.

## 42.3 Metrics Must Expand Along the Task Chain

After designing SLOs, the next step is making targets observable. Agent platforms can't just monitor entry request volume and HTTP errors because real problems hide inside Runs and Steps. In the Monday peak incident, entry service may stay alive, but model queues, SQL tools, chart rendering, and document generation become backlogged.

### 42.3.1 Latency Is Not a Single Number

Agent latency breaks into at least four segments:

1. Entry acceptance to first response - determines if users feel the system responds.
2. First response to final answer - judges interactive task usability.
3. Internal downstream calls - identifies whether slowness is in model, DB, retrieval, code execution, or artifact generation.
4. Queue wait time - evaluates capacity and prioritization strategies.

Looking only at total latency hides causes. A 60-second task might spend 50 seconds generating model output, or queue 45 seconds then 15 seconds executing. The first calls for model routing or caching; the second calls for capacity and queue policy. SLO dashboards should enable drill-down from task latency to step latency and further to model, tool, approval, and artifact writes.

### 42.3.2 Success Rates Should Be Layered

Entry success ≠ task success. A Run may succeed after 5 SQL retries, increasing cost and latency. Platforms should observe task success rate, key step success, tool success, retry rate, timeout rate, degradation rate, and human takeover rate. The following hierarchy provides a minimal metrics map:

*Table 42-3: Example success rate metrics by layer and main purpose. Source: This book.*

| Layer        | Indicator Examples                          | Main Purpose                             |
|--------------|--------------------------------------------|----------------------------------------|
| Entry layer  | Acceptance success rate, rate limit rejection, tenant concurrency usage | Judge if gateway protects system      |
| Run layer    | Run success rate, cancel rate, retryable failure rate, terminal failure rate | Judge if tasks truly complete         |
| Step layer   | Model call success rate, tool success rate, artifact write success rate      | Locate bottlenecks and responsibility |
| Quality layer| Regression pass rate, online sampling scores, user feedback, human takeover rate | Prevent fast but low-quality outputs  |
| Risk layer   | Unauthorized intercepts, data masking hits, approval integrity, audit completeness | Ensure degradation/retry respects safety|
| Cost layer   | Cost per success, cost ratio of failures, cache savings, tenant cost        | Prevent high cost masking superficial success |

This table is a starting point. In production, each metric must be tied to `tenant_id`, `agent_id`, `run_id`, `trace_id`, model versions, prompt versions, tool versions, and semantic layer versions. Otherwise, metrics indicate "worsening" but never explain "why."

### 42.3.3 Dashboards Can Aggregate but Gates Cannot Be Averaged

Management dashboards can show overall state such as "healthy," "attention," or "danger." However, engineering governance must not rely solely on averages because risks differ in nature. Latency, cost, cache hit rates suit trend monitoring; security leaks, unauthorized writes, and cross-tenant accesses are gate conditions that must block release or upgrade immediately upon violation.

For example, if a version reduces P95 latency from 60s to 35s and cuts cost by 20% but introduces a single unauthorized safety violation in a safety test set, it cannot scale to production despite "overall faster and cheaper." Conversely, slight latency increases with stable quality, permissions, and cost may be acceptable depending on business needs. Thus, mature dashboards first expose layered metrics, then show aggregated views. Aggregation reveals trends; traces locate root causes; gates decide release feasibility.

## 42.4 Error Budgets Govern Release Cadence

Error budgets come from site reliability engineering. Simply put, if a service has a monthly SLO of 99.9%, then the remaining 0.1% is allowable failure budget in that period. This is not encouragement to fail, but a computable boundary between rapid iteration and stable reliability.

### 42.4.1 Agent Error Budgets Cover More Than Availability

Agent platforms have multiple budgets: availability budget, latency budget, task failure budget, quality degradation budget, cost overrun budget. Safety budget is usually zero-no unauthorized access, data leak, or unapproved high-risk actions allowed. For example, a financial DataAgent gets 100,000 interactive tasks per week with a 98% success SLO, allowing up to 2,000 task failures weekly. If by Wednesday 1,800 failures have been consumed, future releases must tighten controls. Launching a new planner prompt that looks marginally better offline then is risky because remaining budget can't absorb fluctuations. The task failure budget can be expressed as: $
Budget_{failure} =
N_{runs} \times (1 - SLO_{success})
$

Severity can be weighted: normal model timeouts count as 1 failure, report format errors as 2, sending duplicate emails or leaking permissions as high-risk failures handled by safety gates. This prevents treating all failures equally. In enterprises, 100 timeouts are not equivalent to 1 leak but naive averaging hides this.

### 42.4.2 Budgets Turn Release Governance from Feelings into Rules

With sufficient error budget, teams release normally, experiment, try new models. Rapid budget consumption calls for suspending non-essential changes, prioritizing fixes. Exhausted budget triggers freeze, only stability patches allowed. This beats vague "just feels unstable, hold releases" and is healthier than halting all innovation "for stability."

*Table 42-4: Error budget states and corresponding platform actions and release strategies. Source: This book.*

| Budget State  | Platform Action                           | Release Strategy                    |
|---------------|-----------------------------------------|-----------------------------------|
| Sufficient    | Normal monitoring, allow experiments    | Low-volume canary, routine releases|
| Rapidly Consumed | Drill down failures, cluster root causes | Pause high-risk changes, fix stability|
| Exhausted     | Trigger postmortem, tighten rate limiting and degradation | Only stability patch releases allowed|

Combining error budgets with Chapter 39 regression tests clarifies release gates: new versions must meet offline quality, online budget tolerance, and key safety sample success. Versions passing benchmarks but exhausting error budget should not scale; budget-sufficient but regression-failing versions also should not release. At this point, SLO specifies "what we promise," metrics reveal "how to detect deviation," and error budgets answer "when to tighten." The next step is runtime strategy: how the platform stops issues from escalating in real time.

## 42.5 Rate Limiting, Circuit Breaking, and Degradation Are Three Defense Lines

Back to the Monday peak: failure spread because downstream tasks amplified entry requests, failures amplified via retries. System resilience is not about all downstream always healthy but about manageable degradation, slowdown, and failure so the platform continues serving controllably. Each defense corresponds to an amplification mechanism: rate limiting controls entry amplification to stop infinite requests; circuit breakers isolate unhealthy downstream services to prevent continued overload; degradation handles capacity shortfall, providing acceptable fallbacks when full capacity is unavailable. Their order differs, but all aim to localize faults.

### 42.5.1 Rate Limiting Protects Entry and Fairness

Rate limiting controls the rate of incoming requests. Common strategies include per-user concurrency limits, per-tenant QPS caps, Agent-type limits, long task queue caps, and deduplication of duplicate requests. For Agents, rate limiting prevents crashes and enforces fairness in multi-tenant environments.

Repeated clicks are a classic amplification source. Users clicking "Regenerate" multiple times should not create identical tasks repeatedly. Instead, the platform can return the existing `run_id` based on task fingerprint. This protects downstream and improves user experience by showing progress for the same task, avoiding conflicting competing tasks.

### 42.5.2 Circuit Breaking Isolate Unhealthy Downstream

Circuit breakers isolate clearly unhealthy downstream systems. For example, if the SQL tool times out repeatedly, forwarding requests only increases queues and failures; or if a model service experiences latency spikes, gateway should temporarily stop routing to it, then probe with low volume after cooldown.

Circuit breaking is not a failure end but a protective intermediate state, emitting explainable feedback and alternative paths. For example, during SQL tool circuit break, interactive tasks can respond "data query service busy, switched to asynchronous"; report tasks output cached summaries first; high-risk writes stop and wait for manual intervention.

### 42.5.3 Degradation Provides Alternatives but Must Not Bypass Security

Degradation supplies acceptable fallback when full capabilities are unavailable. During peaks, the platform can first return text summaries and core charts; detailed PPT generation is deferred; context length reduced to recent dialogue and key summaries; non-essential tools disabled; synchronous tasks converted to async; high-risk actions switched to manual approval. Degradation has a bottom line: no security bypass. Primary SQL connection timeout cannot auto-switch to an unpermissioned fallback; when large models are down, small models cannot perform actions originally requiring manual approval. Stability mechanisms that violate permissions, masking, and approval cause incidents themselves. A gateway protection policy might be configured as:

```yaml
protection_policy:
  rate_limit:
    per_user_concurrent_runs: 3
    per_tenant_qpm: 500
    duplicate_task_window_seconds: 300
  circuit_breaker:
    sql_executor:
      open_when_error_rate_gt: 0.30
      window: 2m
      cool_down: 5m
    model_primary:
      open_when_p95_latency_gt_ms: 30000
      window: 5m
      cool_down: 3m
  degradation:
    high_load:
      disable_optional_tools: ["chart_beautify", "ppt_theme_render"]
      max_context_tokens: 12000
      prefer_async: true
    policy_sensitive:
      mode: read_only
      require_human_approval: true
```

Configurations are superficial; priorities underneath matter most: protect safety first, then capacity, and finally sacrifice non-high-risk experience within explainable bounds. This order must not be reversed.

## 42.6 Long-Running Tasks Must Leave Single HTTP Request Lifecycles

Many Agent tasks take longer than seconds. Report generation, batch ticket analysis, multi-round queries, and human approvals may last minutes or hours. Binding these tasks to single HTTP connections risks state confusion from page refresh, network drop, or service restarts. This also underpins degradation strategies: "switch to async," "generate PPT later," "await human approval" require independent task models detached from page connections. Otherwise, degradation is just frontend messaging while backend still loses tasks, duplicates execution, or fails silently.

### 42.6.1 State Machines Are more than Progress Bar Decorations

Long tasks should have independent `run_id`, state machine, checkpoints, and progress query interfaces. After submission, frontend receives `run_id` and polls or gets push updates. Runtime writes checkpoints after key steps for recoverability. A long task state machine could look like:

```text
submitted -> queued -> running -> waiting_approval -> running -> succeeded
                              \-> failed_retryable -> queued
                              \-> failed_terminal
                              \-> cancelled
```

The key distinction is between `failed_retryable` and `failed_terminal`. Retryable failures include model timeout, transient network issues, temporary downstream unavailability; terminal failures include permission denied, invalid parameters, or missing data. Agents must distinguish these to avoid useless retries or duplicate side effects.

### 42.6.2 Checkpoints Record the "Facts Needed to Resume"

Checkpoints don't store all intermediate content but facts needed to resume: steps completed, which tool calls produced side effects, which artifacts written, where to continue next, and what permissions or data versions to reverify. Sending email, writing database, creating tickets are not naturally idempotent. Idempotency means repeating an operation multiple times does not cause duplicated side effects. For these steps, platforms use `idempotency_key` so recovery logic can tell if the step already executed.

```json
{
  "run_id": "run_report_042",
  "step_id": "step_send_report",
  "tool": "email.send",
  "idempotency_key": "run_report_042:step_send_report:v1",
  "status": "succeeded",
  "artifact_refs": ["ppt_report_042"],
  "checkpoint_id": "ckpt_042_006",
  "resume_from": "step_notify_user"
}
```

Long task reliability combines multiple mechanisms: queues buffer requests; heartbeats detect executor liveness; checkpoints enable recovery; idempotency keys prevent duplicate side effects; timeouts prevent indefinite hangs; human approvals block risky auto-continuations. Together, they change "page waits for result" into "task can queue, resume, and explain."

### 42.6.3 Progress Feedback Is Also Part of Stability

Just showing "processing" is not enough to decide system health. Better feedback tells which phase the task is in, if user action is needed, if degradation is active, and expected delivery. For example: "Querying latest financial data," "Waiting for finance manager approval," "Charts generated, PPT queued," "SQL service busy, switched to async." These states improve frontend experience and reduce duplicate submissions-users aware progress is ongoing won't click repeatedly; users knowing failure is terminal won't spawn useless retries. Stability partly comes from making users understand system status.

## 42.7 Capacity Planning Must See Step Amplification Effects

Agent platform capacity planning must consider more than entry QPS. One entry request expands into multiple model calls, tool calls, retrievals, artifact writes, and observability writes. In the Monday peak incident, the entry was "a batch of users generating weekly reports" but each report triggers data queries, charts, document generation, quality sampling, and trace writes, making downstream pressure far exceed entry load.

Earlier discussions focused on protective systems during incidents; capacity planning addresses reducing frequent triggers of protective mechanisms. Rate limiting, circuit breakers, and degradation do not replace capacity building. If the system relies on degradation for long-term availability, it signals a need to rethink SLOs, task classification, or resource provisioning.

### 42.7.1 Estimating Real Workload from Entry Traffic

A rough formula estimates workload: $
Workload =
QPS_{entry}
\times AvgStepsPerRun
\times AvgCallsPerStep
\times RetryFactor
$ If entry QPS is 10, each run averages 6 steps, each step averages 1.5 downstream calls, and retry amplification factor is 1.2, downstream call volume reaches 108 QPS. This excludes token length, query complexity, artifact size, and evaluation sampling. Real capacity planning must unfold these multiplicative effects or online pressure will always exceed stress test results.

### 42.7.2 Different Resources Have Different Bottlenecks

Model services focus on token throughput, concurrency, GPU memory, cache hit rate, and queue length. Tool executors manage SQL, code sandboxing, browser tasks, and external API quotas. Queues monitor backlog, priority inversion, and executor heartbeats. Storage handles writes of traces, logs, artifacts, and evaluation results. Evaluation systems avoid user task preemption by online judges.

*Table 42-5: Major bottlenecks and SLO-related signals by resource domain. Source: This book.*

| Resource Domain | Major Bottlenecks                    | SLO-Related Signals                       |
|-----------------|-----------------------------------|------------------------------------------|
| Model Services  | Token throughput, concurrency, queue, cache hit rate | Model call latency, timeout rate, token cost per task |
| Tool Executors  | SQL queries, code sandboxes, external API quotas | Tool success rate, retry rate, circuit breaker count |
| Queue Systems  | Backlog, priority inversion, executor heartbeats | Queue wait time, deadline achievement, cancellation rate |
| Storage Systems | Writes for traces, logs, artifacts, evaluation results | Write latency, object read failures, audit completeness |
| Evaluation Systems | Online sampling and offline regression resource contention | Sampling latency, evaluation cost, gate delay |

Cache hit rates also affect capacity. Falloff in prompt prefix cache, semantic cache, or artifact cache causes sudden model throughput drops or tool call surges. Thus, caching is a cost optimization (Chapter 41) and key to capacity and SLO.

### 42.7.3 Elastic Scaling Scope

Many teams first scale model instances during peaks, but bottlenecks often lie in tools, queues, or storage. Scaling models alone when SQL pools, chart renderers, object storage, or trace writes lag can worsen downstream overload. More reliable scaling divides by task types: prioritize interactive tasks for first response and clarifications; scale executors for long tasks based on queue backlog; expand render pools for report generation; deprioritize offline evaluations and batch jobs during peaks. Capacity means allocating scarce resources under SLO constraints to most business-high-risk tasks, more than scaling all resources together.

## 42.8 Stability Engineering Must Form an Operational Feedback Loop

Enterprise stability is more than just "no downtime." For Agent platforms, stability encompasses service availability, latency control, task completion, quality preservation, cost containment, risk interception, and incident reviewability.

### 42.8.1 Observability, Evaluation, Cost, and SLO Must Be Connected

Chapter 38's observability reveals how a single task proceeds; Chapter 39's offline evaluations define quality boundaries over fixed tasks; Chapter 40's online evaluation monitors quality shifts on real users; Chapter 41's cost governance explains economics of tokens, caches, and retries; this chapter translates these signals into service promises and release rules. Without traces, incidents cannot be reviewed; without benchmarks, fixes cannot be validated; without online sampling, real degradations go undetected; without cost governance, retry storms can self-amplify under peak loads; without SLOs, teams don't know when to release or freeze.

These systems form an operational feedback loop: online traces support incident review and failure sample collection; failure samples feed offline regression sets; evaluation results and SLOs govern release gates; error budgets and cost dashboards determine whether to continue canary or shrink changes. This is a platform capability, not a documentation process. Every failure should feed samples; every fix validates regression; every release links to error budgets.

### 42.8.2 Alerts Must Point to Actionable Items

Alerts should monitor CPU or HTTP 500s and task success rates, P95 latency, quality sampling, failure costs, security violations, and error budget consumption. More importantly, alerts must be actionable: which tenant, which Agent, which version, which Step, which downstream system, which policy caused the issue.

Stability postmortems should avoid vague "model instability" and instead answer: what task classes failed; did failures concentrate on specific semantic layer versions; was a particular tool timeout root cause; was circuit breaking triggered; was degradation explainable; how much error budget was consumed; which samples need regression or stress set inclusion.

*Table 42-6: Postmortem fields and their necessity. Source: This book.*

| Postmortem Field              | Why Needed                                   |
|------------------------------|---------------------------------------------|
| `tenant_id`, `agent_id`, `run_id` | Confirm affected scope, prevent overgeneralization as "platform-wide" problem |
| Model, prompt, tool, semantic layer, policy versions | Determine if version changes caused issues  |
| Failed Step and error type   | Locate responsibility, avoid generic blame on model |
| SLO impact and error budget use | Decide freeze or degradation extension    |
| Regression sample identifiers | Ensure similar issues are not fixed only once and forgotten |

### 42.8.3 Stress Testing and Fault Injection Should Reflect Agent Tasks

Traditional stress tests hit only the entry interface; Agent stress tests simulate real task chains: peak traffic, growing context, downstream timeouts, cache misses, empty tool results, human approval backlogs, artifact storage slowdowns. Passing stress tests indicates only entry service capacity, not task completion. Fault injection adds value here: deliberately induce SQL tool timeouts, inflate model latency, drop cache hits to validate that rate limiting, circuit breakers, degradation, checkpoints, and error budgets truly work. Resilience is not a post-incident ability but a capability calibrated continuously by drills.

## 42.9 Case Replay: Report Generation Protection During Peak

Returning to the Monday report incident, the revamped platform first redefined scenario SLOs: interactive previews return progress and summary within 10 seconds; full PPT completes asynchronously and notifies within 30 minutes; zero safety violations; average cost per report within budget. Entry layer added rate limiting and deduplication: max 2 concurrent reports per user, tenant-wide concurrency limits, repeated clicks return existing `run_id` instead of creating new tasks. User anxiety clicks no longer amplify downstream pressure.

Execution layer converted report generation to long-running task: tasks queue, executors run asynchronously, frontend shows incremental progress, key steps write checkpoints. During peak, text summaries and core charts generated first; PPT beautification deferred; common weekly report data pre-materialized; metric explanations and schema go into cache; low-priority batch tasks yield to interactive runs. Downstream added circuit breakers and explainable degradation: if SQL tool timeout rate exceeded threshold, platform paused new report queries, returned "data query service busy, switched to async" instead of infinite retries. Failed traces entered regression and stress sets, requiring pressure tests before next release.

Operations integrated the incident into error budget governance: rapid failure budget depletion led to pausing non-essential report template changes and model routing experiments, allowing only stability fixes until pressure tests and regression passes restored capacity. This shifted incident handling from "firefighting" to "constraining subsequent changes." After revamp, users may not get full PPT faster, but the platform changed from "sync blocking, repeated requests, cascading timeouts" to "queueable, recoverable, degradable, explainable." This is system resilience: not every downstream must always work perfectly, but business continues controllably during downstream faults.

---

Resilience drills should become routine. Teams can simulate model-service timeout, vector-store unavailability, slow OLAP queries, approval-system disconnection, and object-storage write failure, then observe whether the Run enters the correct state, users see useful messages, and background tasks recover. Problems found in drills cost less than production incidents, and they also reveal when SLO targets are too optimistic. The practical value of SLOs is consistent behavior under pressure: users know where the task is, business owners know which commitments remain protected, SRE knows which link to restore first, and platform teams know which releases should pause.

SLO documents should also be readable by business teams. Business owners do not need every metric implementation, but they need to know how the system will trade off during peak periods: which tasks queue, which receive summaries first, which move to human handling, and which are rejected. When these expectations are written before an incident, every degradation event is less likely to be read as platform failure.

## 42.10 Business review for SLO changes

SLO changes alter the promise users receive and the trade-offs the platform makes during peak load. Extending report completion from 10 minutes to 30 minutes may look like a queue-parameter change to engineers; for business teams, it may decide whether meeting materials arrive in time. Moving low-priority data questions to async execution may reduce cost; for frontline operations, it may slow same-day decisions. Platform teams should therefore bring business owners into SLO review. The review should focus on scenario promises: which tasks still guarantee first response, which may queue, which can return summaries first, which should fail with a clear reason, and which degradation paths must still preserve approval and audit.

Business review should use sample tasks instead of abstract metrics alone. The platform can take frequent conversations, long report generation, data queries, approval waits, external-system writes, and batch evaluation runs, then describe the user experience, backend state, cost change, and risk boundary after the SLO adjustment. If error budget drains quickly, business owners should understand the consequence: pausing template releases, limiting expensive queries, delaying model-routing experiments, or moving selected tasks to manual handling. If the relaxed SLO still fails to protect high-value work, the problem may sit in capacity, cache design, task decomposition, or downstream contracts. Changing the number will not repair those links.

SLO changes also need rollback conditions. Some adjustments reduce reported failure rate while pushing delay onto users. Some throttling policies protect infrastructure while blocking high-priority roles during peak periods. When publishing an SLO change, the platform should state observation window, affected users, allowed complaint threshold, replay samples, and recovery path. After business review approves the change, Trace, evaluation, cost governance, and alerting rules should be updated together. SLOs then become operating commitments that guide release and incident decisions, instead of numbers stored only in monitoring dashboards.

## 42.11 SLO and release freeze

SLO should shape release cadence as well as incident handling. When error budget burns too fast, long-task queues keep growing, human takeover rate becomes abnormal, or key tasks degrade frequently, the platform should freeze selected releases. The freeze does not have to stop every change. It can pause model-routing experiments, high-cost prompt templates, new tools entering the default candidate set, low-priority batch evaluation, or automatic write actions for high-risk tenants. The purpose is to bring the system back into an explainable operating range.

Freeze rules should be written before incidents. The platform should not decide during an outage which teams may release and which changes must wait. Each SLO should map to thresholds and actions. First-response breaches affect interaction, so frontend streaming policy and gateway routing may freeze first. Final-completion breaches affect reports and long tasks, so asynchronous queues and batch generation may be limited. Quality regression affects trust, so prompt and model experiments should pause. Cost-budget anomalies affect operations, so high-cost tasks and evaluation sampling should be limited. Release cadence then follows operating evidence.

Release freeze also needs business-facing explanation. Business teams need to know which requirements are affected, how long the freeze may last, what unlocks it, and whether an alternate path exists. If freeze is only an internal platform state, business teams will keep pushing releases and create exceptions. A better approach is to show freeze state on the release board, including protected tasks, consumed error budget, paused change types, and the next review time. SLO then becomes a shared operating commitment across teams.

A first version can define freeze policy for core paths: model gateway, Runtime, DataAgent, HITL, and report publication. Each freeze and unfreeze should leave Trace, alert, error-budget, and business-impact records. Over time, these records show which capabilities often push the system toward instability and help adjust capacity planning and product commitments. SLO helps the platform decide when to keep changing and when to stabilize operations first.

## 42.12 Release freeze after SLO breach

An SLO breach should trigger more than an alert. For enterprise Agents, repeated timeouts, rising error rate, high human takeover, abnormal cost, or a surge in safety blocks may show that the current version should not receive more traffic. The platform needs to connect SLO breaches with release cadence: some breaches pause new releases, some stop canary expansion, and some require rollback or human review.

Release freeze needs clear conditions. P95 latency above threshold for two hours, key-task success rate below the bar, failed safety samples, tenant cost exceeding budget, or abnormal human takeover can all trigger a freeze. During the freeze, teams can repair and verify, but they should not expand traffic or publish related capabilities. Lifting the freeze requires retest samples, online observation, and owner sign-off, not a short period of alert recovery.

A first version can add SLO gates to the release system. Each gate binds metric, threshold, affected scope, freeze action, and release condition. Trace, Eval, cost records, and security ledgers provide evidence together. SLO then moves from dashboard metric to platform release control, making reliability part of product cadence.

## 42.13 Business handling after SLO violations

After SLO management reaches production, a successful demo is not enough evidence. The platform needs stable fields for violation time, affected users, degradation policy, compensation action, incident sample, and review time, and those fields should connect to release records, Trace, evaluation samples, and incident notes. When a production issue appears, teams can follow one set of facts to understand scope, ownership, and repair order instead of stitching together model logs, business logs, and verbal explanations.

This evidence also connects the surrounding chapters. It links to Chapter 38 on Trace, Chapter 41 on cost governance, and Chapter 53 on operating rhythm: upstream capabilities provide assumptions, downstream capabilities consume the result, and governance capabilities preserve evidence and review decisions. If these materials do not share identifiers and versions, the production system splits apart. Business owners see user complaints, platform owners see system errors, and security or compliance teams see explanations written after the fact. That separation makes it hard to decide whether the issue came from data, model behavior, tool contracts, workflow state, or organizational ownership.

Common production risks include records that capture only technical alerts, business owners not knowing impact scope, and degradation without user explanation. These risks are less visible during demos because demos usually exercise the successful path. Production users bring boundary cases, repeated requests, permission changes, and long-running state. The platform team should turn such failures into release samples. Some samples should block launch, some can be handled by degradation, and some require the business owner to accept the remaining risk with a review date.

SLO should connect user commitments with platform operation, and every violation should leave a business-readable handling record. The record can stay compact, but it should include time, version, owner, sample, action, and the next review condition. Without those fields, review remains informal experience. With them, one production issue can become material for later releases, evaluation suites, and training.

A first platform version can start with a small set of high-risk paths. Choose flows with high traffic, high business impact, or sensitive data, require an evidence package for each change, and then expand the practice to ordinary scenarios. This keeps the capability at the engineering level: runnable, explainable, and recoverable.
## 42.14 User communication in SLO reviews

SLO review should include user communication. The platform may know why latency, degradation, or cancellation happened, but users still need to understand the effect. For incidents with clear scope, product communication should state affected tasks, recovery state, whether users need to retry, whether existing artifacts remain trustworthy, and whether results will be reissued. The message should come from Trace and incident records instead of ad hoc guesses by operations staff.

User communication also calibrates SLO. If users care most about whether a report is trustworthy, improving response time alone has limited value. If users can wait but cannot accept unexplained failure, degradation policy should improve prompts and recovery paths first. A first version can include communication templates in SLO review so availability metrics and user experience use the same evidence.

## Chapter Recap

Agent SLOs focus on tasks, not individual requests. Enterprise platforms must promise "interface returns success," and that users safely complete quality tasks within acceptable time and cost. This goal must be decomposed into first response, final completion, task success, quality, safety, cost, and recoverability to enable governance. Rate limiting, circuit breaking, and degradation form three defense lines protecting the system. Rate limiting controls entry, circuit breaking isolates unhealthy downstream, degradation provides fallback capabilities. All must respect security: no degradation path bypasses permissions, masking, approval, or audit.

Long-running tasks and capacity planning distinguish Agent platforms from ordinary web services. Long tasks require state machines, checkpoints, idempotency keys, progress queries; capacity planning must account for step amplification, retry amplification, token throughput, tool bottlenecks, and cache hit rate. Ultimately, stability engineering must form a closed loop connected with Chapter 38's tracing, Chapter 39's regression evaluation, Chapter 40's online evaluation, and Chapter 41's cost governance. Key questions to self-check:

- Are SLOs defined separately for interactive tasks, long tasks, batch, and approval flows?
- Are entry success, Run success, Step success, quality, safety, and cost monitored separately?
- Can error budgets influence release, canary, freeze, and fix priorities?
- Are rate limiting, circuit breaking, and degradation policies tied to tenant, task type, and risk level?
- Do degradation paths still enforce permission, masking, approval, and audit?
- Do long tasks have state machines, checkpoints, idempotency, progress queries, and failure explanations?
- Does capacity planning consider step and retry amplification, token throughput, tool bottlenecks, and cache hit rates?
- Does incident review produce traces, regression samples, stress samples, and explicit fix actions?

Related chapters: [Chapter 22 Agent Runtime](../../part05-agent-capabilities/en/ch22-agent-runtime.md), [Chapter 30 HITL and Long Tasks](../../part05-agent-capabilities/en/ch30-human-in-the-loop.md), [Chapter 38 Agent Observability and Diagnostic](ch38-trace.md), [Chapter 39 Enterprise DataAgent Evaluation and Benchmark](ch39-dataagent-eval-benchmark.md), [Chapter 40 Online Evaluation, LLM-as-Judge, and Continuous Optimization](ch40-llm-as-judge.md), [Chapter 41 Cost Governance and Caching Optimization](ch41-cost-governance-cache.md), [Chapter 43 GPU Scheduling and Kubernetes](../../part08-deployment/en/ch43-gpu-kubernetes.md). Further engineering topics include: Service Level Objectives, error budgets, rate limiting, circuit breaking, backpressure, checkpoints, capacity planning, chaos engineering, long task scheduling, and multi-tenant isolation.

## References

Beyer, B. et al. (2016). [*Site Reliability Engineering*](https://sre.google/sre-book/table-of-contents/). O'Reilly.

Beyer, B. et al. (2018). [*The Site Reliability Workbook*](https://sre.google/workbook/table-of-contents/). O'Reilly.

Envoy Proxy. (n.d.). [Rate limit filter documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/rate_limit_filter).

Kubernetes. (n.d.). [Horizontal Pod Autoscaling documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).
