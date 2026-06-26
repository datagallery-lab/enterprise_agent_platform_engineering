# Part VIII Deployment and Infrastructure

Part VIII moves from platform design to production operation. The chapters in this part discuss how model services, GPU clusters, gateways, GitOps, IaC, and edge inference become controlled infrastructure instead of scattered deployment scripts.

## Goals of this part

After reading this part, readers should understand how enterprise Agent platforms reserve GPU resources, expose model services, govern multi-tenant access, and release infrastructure changes with rollback evidence. The focus is production control: isolation, quota, runtime evidence, repeatable rollout, and incident recovery.

## Chapters in this part

Chapter 43 discusses GPU scheduling and Kubernetes isolation. Chapter 44 explains model deployment and runtime verification. Chapter 45 treats the LLM gateway as a policy and evidence surface. Chapter 46 connects GitOps, IaC, edge inference, and rollback rehearsal.

## Reading advice

Read this part after Parts II and V if the main question is model serving and Agent runtime integration. Read it after Part VII if the main concern is how deployment evidence connects to Trace, SLO, and cost governance.

## Relationship to the whole book

Deployment is where platform promises become operational constraints. A model route, tool call, approval state, or report result is only credible when the underlying infrastructure can isolate tenants, record evidence, recover from failure, and make change history auditable.
