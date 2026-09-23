---
name: openspec-shared
description: Passive index of conditional OpenSpec engineering references; never invoke as an action or use as a user-facing workflow.
---

# OpenSpec shared reference index

Never invoke this index as an action. It defines no workflow, gate, authority, routing, or agent dispatch. Action instructions load only the applicable reference for the stated purpose:

- [`artifact-quality.md`](references/artifact-quality.md) — when drafting or assessing the substance of an intent, behavioral specification, technical design, or implementation-task artifact.
- [`evidence-first.md`](references/evidence-first.md) — when choosing evidence for implementation or deciding whether a completion, pass, fixed, or readiness claim is supported.
- [`performance-memory.md`](references/performance-memory.md) — when latency, throughput, allocation, concurrency, buffering, caching, serialization, or resource lifetime may change, or a quantitative claim is made.
- [`integration-correctness.md`](references/integration-correctness.md) — when connector, protocol, framework, external-service, transaction, streaming, retry, cancellation, version, cleanup, error-mapping, or value-conversion semantics matter.
- [`debugging.md`](references/debugging.md) — when a bug, regression, leak, nondeterminism, failing check, or contradictory observation requires diagnosis.
- [`review.md`](references/review.md) — when an independent, read-only, finding-oriented assessment is warranted or review feedback must be evaluated.
- [`research.md`](references/research.md) — when repository evidence is insufficient or exact dependency, protocol, framework, server, or runtime versions can change the answer.
- [`subagents.md`](references/subagents.md) — before optional specialist delegation or any parallel-read or parallel-write decision.
