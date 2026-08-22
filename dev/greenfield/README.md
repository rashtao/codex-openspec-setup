# Greenfield OpenSpec product-workflow skill design

Status: design complete for review; not implemented.

This directory records the agreed design for Codex skills that discover a
genuinely greenfield product, freeze its first-usable-release baseline, and
deliver it through one focused OpenSpec change at a time.

The design is derived from [`./workflow.md`](./workflow.md) and
the subsequent knowns/unknowns interview. This directory is the authoritative
implementation contract: explicit decisions recorded here supersede conflicting
suggestions in the earlier prompt.

## Design constraints

- Codex only.
- Every user-facing product skill is explicit-invocation only.
- All new routed agents use `gpt-5.6-sol`.
- Every new product-agent dispatch uses `fork_turns: "none"` and a complete
  evidence packet.
- Existing files under `../release/.codex/skills/openspec-*`, matching existing
  OpenSpec agents, and `../release/openspec/config.yaml` remain unchanged.
- Existing OpenSpec actions are invoked manually in fresh sessions. Product
  skills print complete repository-relative prompts but never invoke an
  OpenSpec skill themselves.
- The workflow supports one genuinely greenfield product and one repository.
- The user is responsible for running only one Codex instance and for not
  creating an unexpected OpenSpec change between workflow actions.
- Product-level slice verification is deliberately absent. The manually
  invoked `openspec-verify-change` action is the sole behavioral verification.
- Product reconciliation is structural and traceability-oriented; it does not
  inspect implementation correctness or rerun tests.
- A frozen baseline is immutable. There is no refreeze and no baseline v2.
- An archived OpenSpec change is terminal and is sufficient approval evidence
  for its delivered emergent behavior and baseline dispositions.

## Designed skill set

| Skill | Kind | Responsibility |
|---|---|---|
| `openspec-product-discovery` | User-facing action | Initialize discovery, run breadth-first interview rounds, and persist findings. |
| `openspec-product-baseline` | User-facing action | Synthesize, review, and approve the immutable first-release baseline. |
| `openspec-product-delivery` | User-facing action | Build the roadmap, select slices, render handoffs, reconcile archives, and close the release. |
| `openspec-product-shared` | Passive support | Own schemas, templates, validators, hashing rules, and prompt-rendering contracts. |

## Document index

- [`skill-contracts.md`](skill-contracts.md) — scope, exact trigger descriptions,
  modes, routing, model settings, and package layout.
- [`workflow-state.md`](workflow-state.md) — phases, state transitions,
  interview behavior, approval gates, delivery progression, and closure.
- [`artifact-templates.md`](artifact-templates.md) — exact templates for every
  discovery, baseline, delivery, and control artifact.
- [`integration-and-handoffs.md`](integration-and-handoffs.md) — fresh-context
  prompt protocol, unchanged OpenSpec contact points, archive detection, and
  structural reconciliation.
- [`validation-and-recovery.md`](validation-and-recovery.md) — deterministic
  checks, stopping rules, expected failures, and recovery behavior.
- [`test-plan.md`](test-plan.md) — description-boundary cases, forward workflow
  scenarios, preservation checks, and candidate-versus-baseline evaluation.

## Non-goals

This design does not:

- create or modify the future skills;
- change OpenSpec schemas, skills, agents, or configuration;
- protect against a user intentionally bypassing the printed workflow;
- add a second verification layer around OpenSpec;
- support brownfield products, multiple active products, registered OpenSpec
  stores, or parallel Codex instances;
- automatically promote post-release material into permanent documentation.

## Design completeness

No unresolved workflow choice blocks future implementation. Unknown product
requirements are deliberately part of the runtime discovery model, not missing
skill-design decisions. Host capabilities that may vary by Codex version—such
as whether an activation receipt is exposed—are handled conservatively by the
test contract and never inferred.
