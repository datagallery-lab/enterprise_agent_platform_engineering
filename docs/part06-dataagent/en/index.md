# Part VI DataAgent Core Deep Dive

## Goals of this part

Part VI follows one DataAgent mainline: from product boundary and question framing, through semantic-layer linking and secure NL2SQL, into Python analysis, chart/report generation, and ecosystem selection. The goal is to show how data analysis Agents become governed task systems rather than isolated Text-to-SQL demos.

## Chapters in This Part

- [Chapter 32 DataAgent Product Forms](ch32-dataagent.md) - Product boundaries; four forms; problem understanding and task planning
- [Chapter 33 Semantic Layer Engineering](ch33.md) - Metrics definitions, schema linking, trustworthy context
- [Chapter 34 NL2SQL Engineering](ch34-nl2sql.md) - Stepwise generation and large database pruning; secure execution and business explanation
- [Chapter 35 Text-to-Pandas / Text-to-Python](ch35-text-to-pandas-text-to-python.md) - Python sandbox; SQL + Python collaboration
- [Chapter 36 Data Analysis, Visualization, and Reporting](ch36.md) - Insights, charts, reports; output quality evaluation
- [Chapter 37 DataAgent Benchmarking and Ecosystem](ch37-dataagent.md) - Open source/commercial benchmarking; selection; Part VI summary

**Unified Case Study**: A multi-business-line company in East China experiences GMV decline -> inquiry -> analysis -> report run chain (spanning six chapters starting from Chapter 32).

The modules below represent the unfolding order of DataAgent capabilities in the mini-platform across Part VI chapters.

## Part VI Mini-Platform Module Map

| Module Path                    | Responsibility                    | Main Chapters |
|-------------------------------|---------------------------------|---------------|
| `agents/data_agent/`           | AgentSpec, Question Framework    | 32-33         |
| `infra/semantic_layer/`        | Metrics, Views, Definition Parsing | 33          |
| `tools/sql_executor/`          | Read-only SQL, validation, execution | 34         |
| `tools/python_sandbox/`        | Analysis sandbox                 | 35            |
| `tools/chart_renderer/`        | Chart specifications             | 36            |
| `agents/data_agent/templates/`| Report templates                 | 36            |

Platform Run / Registry / HITL bases are detailed in **Part V** (`core/runtime/` etc.; reference [Chapters 22-30](../../part05-agent-capabilities/en/ch22-agent-runtime.md)).

## Part VI Capability Overview (At a Glance)

| Chapter | Summary in One Sentence          |
|---------|---------------------------------|
| **32**  | DataAgent is not NL2SQL; four product forms |
| **33**  | Foundations of definitions and linking  |
| **34**  | Secure SQL and self-healing           |
| **35**  | Python analysis sandbox               |
| **36**  | Insights, charts, reports, and output evaluation |
| **37**  | Ecosystem benchmarking, selection, and continuous improvement |
