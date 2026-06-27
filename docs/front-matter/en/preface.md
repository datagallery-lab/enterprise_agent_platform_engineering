# Preface

When enterprises build Agent platforms, the easiest thing to underestimate is the system boundary itself. A demo Agent often needs only a model, a prompt, and a few tools. A production-grade enterprise Agent platform has to answer much harder questions: how tasks are defined, how tools are authorized, how data is interpreted, how execution is audited, how failures are recovered, and how cost and risk are governed over time.

This book is organized around those engineering questions. It focuses on interfaces, state, evidence, permissions, evaluation, and organizational collaboration inside enterprise systems. Models are only one layer. Data foundations, knowledge engineering, runtime, tool registration, observability, deployment, and security governance together determine whether an Agent can enter production. The DataAgent storyline also goes beyond NL2SQL into semantic layers, permissions, execution, explanation, evaluation, and human review.

The first Chinese release is structured from a platform-engineering point of view, and this English edition follows that same architecture. The opening sections establish the core language of Agent platforms and explain how models, data, retrieval, and runtime fit together. The middle sections use DataAgent as the main line, connecting semantic layers, NL2SQL, Python analysis, visualization, reporting, and evaluation into a deliverable path. The later sections return to observability, cost, deployment, security, compliance, and organizational evolution. Readers can move through the book linearly or use it as a reference during architecture reviews, solution design, and troubleshooting.

This edition focuses on technical chapters whose argument is stable enough to inspect and reuse. Business cases require source material, sanitization, and factual review, so the case section emphasizes admission rules and review standards rather than unsupported claims.

The aim is to help readers move from "building an Agent" to "building a governable platform capability," so that teams can keep shipping under real business constraints, real permissions, real data, and real failures.
