# Part I Overview and Platform Perspective

> 4 chapters · The opening part of the book, responsible for establishing a shared vocabulary, a platform perspective, and a reading map.

Part I does not immediately enter a specific framework, a codebase, or a product. It first answers four more fundamental questions:

1. What exactly is an Agent, and where are the boundaries between Agent, RAG, Copilot, and Workflow?
2. Why do enterprises ultimately need a platform, rather than a set of fragmented intelligent projects?
3. What is an AI-native business system, and how is it different from adding AI features to legacy systems?
4. Why are the later chapters organized in this order, and how should different readers use the book?

Together, these four chapters serve as the book's opening overview. They do not rush into implementation details. Instead, they pursue three goals:

- Clarify concepts and boundaries first;
- Then raise the perspective to enterprise platforms and business systems;
- Finally provide a map of the book and a set of reading paths.

## Relationship Between the Four Chapters

| Chapter | Question it answers | How it prepares the next chapter |
|---|---|---|
| [Ch.01 The Nature of Agents: From Conversational Assistants to Task Execution Systems](ch01-agent.md) | What counts as an Agent, and why an enterprise enters a new problem space once a system begins to "do things" | Prepares Ch.02 by explaining why platform boundaries emerge |
| [Ch.02 The Boundary of an Enterprise Agent Platform](ch02-agent.md) | What kind of platform an enterprise is actually building, and how platform, application, and framework responsibilities differ | Prepares Ch.03 by explaining what kind of business system the platform ultimately serves |
| [Ch.03 AI-Native Business Systems: Agents Reshape Enterprise Software](ch03-ai-agent.md) | Why AI-native systems are not "just another chat box," but a change in business-system form | Prepares Ch.04 by explaining why the book needs an architecture map |
| [Ch.04 Book Map: Platform Reference Architecture and Reading Paths](ch04.md) | The architecture map, chapter dependencies, reader paths, and platform-building roadmap for the book | Leads readers into the later technical chapters |

## How to Read This Part

If you are encountering enterprise Agent platforms for the first time, read the four chapters in order. They are designed as a progressive argument.

If you already have project experience, you can also jump according to your current concern:

| Current concern | Read first |
|---|---|
| Which requirements deserve to become Agents | Ch.01 |
| Your team is debating what "platform" really means | Ch.02 |
| You want to judge which businesses are suitable for AI-native transformation | Ch.03 |
| You want a quick map of the book and the later roadmap | Ch.04 |

After finishing Part I, readers should have at least three abilities:

- Distinguish different types of large-model systems;
- Re-evaluate enterprise AI projects from a platform perspective;
- Understand why each later technical topic exists.

With these three abilities, the chapters on models, data, knowledge, Runtime, evaluation, security, and frontend experience in Part II and beyond will no longer feel like isolated knowledge points. They will gradually assemble into a complete engineering map for enterprise Agent platforms.
