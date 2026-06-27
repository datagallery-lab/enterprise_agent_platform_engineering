# Enterprise Agent Platform Engineering

This book is for teams building enterprise-grade Agent platforms. It covers the engineering system behind production Agents: data foundations, model inference, knowledge engineering, Agent Runtime, tool ecosystems, evaluation, deployment, frontend interaction, security, compliance, and organizational governance.

The English edition follows the same structure as the Chinese edition and focuses on stable technical chapters and case-review methods backed by explicit evidence standards.

## Edition Entry Points

| Edition | Entry |
| --- | --- |
| Chinese | Available from the site language switcher |
| English | [Start with Part I](../../part01-overview/en/index.md) |

## Front Matter

| Page | Purpose |
| --- | --- |
| [Abbreviations](abbreviations.md) | Defines common abbreviations and the terminology used in this book |
| [Preface](preface.md) | Explains the platform-engineering viewpoint and release boundary |
| [Acknowledgements](acknowledgements.md) | Acknowledgements page |
| [Front Matter Guide](front-matter-guide.md) | Gives reading paths by role and problem type |
| [Contributors](contributors.md) | Contributors page |

## Quick Navigation

| Part | Topic |
| --- | --- |
| [Part I Overview and Platform Perspective](../../part01-overview/en/index.md) | Agent fundamentals, platform boundaries, AI-native business systems, and the full-book map |
| [Part II Models and Inference](../../part02-model-inference/en/index.md) | Model selection, local inference, inference optimization, structured output, and customization |
| [Part III Data Infrastructure](../../part03-data-infra/en/index.md) | Ingestion, lakehouse, OLAP, streaming, orchestration, quality, metadata, and metrics |
| [Part IV Vectors, Retrieval, and Knowledge Engineering](../../part04-vector-knowledge/en/index.md) | Embeddings, reranking, vector databases, document parsing, RAG, and knowledge engineering |
| [Part V Agent Capabilities](../../part05-agent-capabilities/en/index.md) | Runtime, Tool Registry, MCP, Planner, Workflow, Memory, multi-agent systems, and protocols |
| [Part VI DataAgent Deep Dive](../../part06-dataagent/en/index.md) | Semantic layer, NL2SQL, Python analysis, visualization, reporting, and ecosystem comparison |
| [Part VII Observability, Evaluation, and Cost](../../part07-observability-eval/en/index.md) | Trace, offline evaluation, online evaluation, cost governance, and SLOs |
| [Part VIII Deployment and Infrastructure](../../part08-deployment/en/index.md) | GPU scheduling, model deployment, LLM Gateway, GitOps, and edge inference |
| [Part IX Frontend, Interaction, and Multimodality](../../part09-frontend-multimodal/en/index.md) | Conversational UI, Generative UI, multimodal input, and voice Agents |
| [Part X Security, Compliance, and Organization](../../part10-security-org/en/index.md) | Security, Guardrails, regulation, organization, and platform evolution |
| [Part XI Case Methodology](../../part11-cases/en/index.md) | Case admission, review, and platform consolidation standards |

## Reading Paths

| Role | Recommended Path |
| --- | --- |
| AI platform leader / CTO | Part I -> Part V -> Part VI -> Part X |
| Architect | Part I -> Part II -> Part III -> Part IV -> Part V -> Part VIII |
| Data intelligence engineer | Part III -> Part IV -> Part VI -> Part VII |
| AI application developer | Part II -> Part V -> Part IX -> mini-platform |
| Security / compliance owner | Part I -> Part VII -> Part X |

## Local Validation

```bash
bash scripts/check_all.sh
python -m mkdocs build --strict --clean --site-dir /tmp/enterprise-agent-book-site
```

The first command checks chapter structure, terminology, sensitive information, and mini-platform tests. The second command verifies that the web-book project can build in strict mode. Together, they cover the main local quality gates before a submission.
