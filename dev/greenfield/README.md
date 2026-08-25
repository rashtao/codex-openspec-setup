# Greenfield product-workflow skill design

Status: design complete for review; not implemented.

This directory is the authoritative implementation contract for Codex skills
that discover a genuinely greenfield product, freeze its first-usable-release
baseline, and deliver that baseline through one focused OpenSpec change at a
time. Explicit decisions here supersede conflicting suggestions in
[`workflow.md`](workflow.md) or the earlier prompt.

## Design constraints

- Codex only; every user-facing product skill is explicit-invocation only.
- All product-agent dispatches use `fork_turns: "none"` and a complete evidence
  packet. The routed agents use `gpt-5.6-sol`.
- Existing external OpenSpec skills, agents, configuration, schemas, specs, and
  change conventions remain unchanged.
- External OpenSpec actions are invoked manually in fresh sessions. Product
  skills may print a prompt for them but never invoke them.
- The workflow supports one genuinely greenfield product and one repository.
- Discovery remains mutable until baseline approval. The approved baseline is
  frozen, with no refreeze or baseline v2.
- Delivery is the forward-only loop `roadmap → slice → external OpenSpec
  workflow → archive → repeat`.
- External OpenSpec verification remains the sole behavioral verification.

## Designed skill set

| Skill | Kind | Responsibility |
|---|---|---|
| `product-discovery` | User-facing action | Initialize discovery, run breadth-first interview rounds, and persist findings. |
| `product-baseline` | User-facing action | Synthesize, review, and approve the immutable first-release baseline. |
| `product-delivery` | User-facing action | Maintain requirement coverage, prepare one active slice, archive it after external OpenSpec completion, and report status. |
| `product-shared` | Passive support | Provide references, normative templates, assets, and a user-facing README. It has no scripts or user-facing mode. |

## Operational responsibilities

- The user protects frozen baseline files and archived slice files from edits.
- Roadmap coverage is optimistic: selecting a slice immediately declares its
  planned partial or complete coverage, before implementation occurs.
- One user and one Codex instance act as the single writer for product
  artifacts and OpenSpec changes.
- Before invoking `$product-delivery archive`, the user manually inspects
  `delivery/archive/` and attests that moving the active slice there is safe.
- Git or other user-owned history is the recovery mechanism for accidental
  edits, deletion, or filesystem conflict. The product workflow adds no repair
  or rollback mode.
- The user is responsible for roadmap correctness, scan completeness,
  implementation success, archived-slice immutability, OpenSpec archive
  correctness, canonical synchronization, suffix ambiguity, filesystem
  conflicts, and any corrective work.

## Document index

- [`skill-contracts.md`](skill-contracts.md) — package layout, trigger
  descriptions, modes, routing, and mutation boundaries.
- [`workflow-state.md`](workflow-state.md) — discovery and baseline state plus
  the forward-only delivery loop.
- [`artifact-templates.md`](artifact-templates.md) — normative persisted
  artifacts and console responses.
- [`integration-and-handoffs.md`](integration-and-handoffs.md) — fresh-context
  OpenSpec integration and name matching.
- [`discovery-and-baseline-validation.md`](discovery-and-baseline-validation.md)
  — discovery and baseline checks and stopping rules.
- [`test-plan.md`](test-plan.md) — description-boundary and behavioral tests.

## Non-goals

This design does not modify external OpenSpec, verify implementation at the
product layer, keep delivery ledgers, close or archive the product bundle,
coordinate concurrent writers, or add correction, abandonment, reopening,
rollback, locking, or delivery-repair workflows.
