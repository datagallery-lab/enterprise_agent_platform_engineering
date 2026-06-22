# Part VIII Deployment and Infrastructure

> Part Owner: Xuhong | Status: v0.6 Draft
> These four chapters form a complete chain **Scheduling → Service → Gateway → Delivery**.

## Chapters in This Section

| Chapter | Title                      | Core Responsibility     |
|---------|----------------------------|------------------------|
| [Chapter 43](ch43-gpu-kubernetes.md) | GPU Scheduling and Kubernetes | Where does compute power come from |
| [Chapter 44](ch44.md)                 | Model Deployment             | How the model runs            |
| [Chapter 45](ch45-llm.md)             | LLM Gateway and Multi-Tenancy | How requests enter            |
| [Chapter 46](ch46-gitops-iac.md)      | GitOps, IaC, and Edge Inference | How the whole set is delivered |

## Reading Recommendations

- **Architects:** Read from Chapter 43 through Chapter 46 in sequence for a comprehensive understanding of concepts and architecture.
- **AI Application Developers:** Focus on engineering examples in Chapters 44 and 45.
- **CTOs / Platform Leads:** Review the conceptual and architectural sections of each chapter with attention to ROI, compliance boundaries, and 3-year evolution.

## Relationship to the Whole Book

- Upstream: Part II Inference Engine (Chapters 6–7) provides the basis for runtime selection.
- Downstream: Part IX Frontend (Chapter 47) relies on stable APIs from gateways and model services.
- Cross-cutting: Part VII Cost/SLO (Chapters 41–42), Part X Security Isolation (Chapter 50).
