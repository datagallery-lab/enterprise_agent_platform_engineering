# Preface

When enterprises build Agent platforms, the most underestimated problem is not model capability. It is system boundary.

A demo Agent often needs only a model, a prompt, and a few tools. A production-grade enterprise Agent platform has to answer harder questions: how tasks are defined, how tools are authorized, how data is interpreted, how execution is audited, how failures are recovered, and how cost and risk are governed over time.

This book is organized around those engineering questions. It is not a single-framework tutorial, and it does not reduce DataAgent to NL2SQL. The book cares about interfaces, state, evidence, permissions, evaluation, and organizational responsibility. Models are one layer of the system; data foundations, knowledge engineering, runtime, tool registration, observability, deployment, and security governance decide whether Agents can enter production.

The first release uses a platform-engineering viewpoint. The early parts establish the shared language of Agent platforms and explain how models, data, retrieval, and runtime fit together. The middle parts use DataAgent as the main line, connecting semantic layers, NL2SQL, Python analysis, visualization, reporting, and evaluation into an end-to-end delivery path. The later parts return to observability, cost, deployment, security, compliance, and organizational evolution.

This book is still in its first-edition cleanup stage. Business cases, acknowledgements, and project-closure material that do not yet have verified source evidence are intentionally left blank. For chapters already in the body, the priority is to keep structure, figures, citations, code paths, and the web-book experience reviewable and reproducible.

The goal is to help readers move from "building an Agent" to "building a governable platform capability": not just a successful demo, but continuous delivery under real business constraints, real permissions, real data, and real failures.
