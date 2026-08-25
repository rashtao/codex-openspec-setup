# Greenfield product-workflow skill design

Status: design complete for review; not implemented.

This directory is the authoritative implementation contract for Codex skills
that discover a genuinely greenfield product, freeze its first-usable-release
baseline, and deliver that baseline through one focused OpenSpec change at a
time. `workflow.md` is a historical, non-normative summary. This README and the
indexed documents are the authoritative implementation contract.

## Design constraints

- Codex only; all four product packages enforce explicit-only activation with
  `agents/openai.yaml` and retain frontmatter exclusions as defense in depth.
- All top-level product-action dispatches use `fork_turns: "1"`; the routed
  child may use only the latest user turn, and persisted artifacts remain the
  authority for pending interactions and product facts. Public product modes
  use the deterministic GPT-5.6 route table in `skill-contracts.md`; every
  status mode uses `gpt-5.6-luna` at `low` effort and performs zero writes.
- Every public product skill uses an exact `ROUTED_ACTION=<skill-name>` guard
  to enforce one-hop routing.
- Only `roadmap` and `slice` may use bounded read-only specialists;
  product-action rerouting and delegated writes are forbidden.
- Existing external OpenSpec skills, agents, configuration, schemas, specs, and
  change conventions remain unchanged.
- `product-shared` ships no assets; installed normative templates live in
  `references/artifact-contracts.md`.
- External OpenSpec actions are invoked manually in fresh sessions. Product
  skills may print a prompt for them but never invoke them.
- Product-workflow test assets remain under `dev/greenfield/test/`; none are
  published under `release/`.
- The workflow supports one genuinely greenfield product and one repository.
- Discovery remains mutable until baseline approval. The approved baseline is
  frozen, with no refreeze or baseline v2.
- Asked interview rounds and delivery previews are persisted in the product
  control plane before the workflow waits for a response or confirmation.
- Delivery is the forward-only loop `roadmap → slice → external OpenSpec
  workflow → archive → repeat`.
- External OpenSpec verification remains the sole behavioral verification.

## Designed skill set

| Skill | Kind | Responsibility |
|---|---|---|
| `product-discovery` | User-facing action | Initialize discovery, run breadth-first interview rounds, and persist findings. |
| `product-baseline` | User-facing action | Synthesize, review, and approve the immutable first-release baseline. |
| `product-delivery` | User-facing action | Maintain requirement coverage, prepare one active slice, archive it after external OpenSpec completion, and report status. |
| `product-shared` | Passive support | Provide passive references, including normative artifact templates and operating assumptions. It has no scripts, assets, custom agent, or user-facing mode. |

## Operational responsibilities

The normative trust assumptions belong to the
[`product-shared/references/operating-assumptions.md` contract](skill-contracts.md#product-sharedreferencesoperating-assumptionsmd-contract).

## Document index

- [`skill-contracts.md`](skill-contracts.md) — package layout, trigger
  descriptions, modes, routing, and mutation boundaries.
- [`workflow-state.md`](workflow-state.md) — discovery and baseline state plus
  the forward-only delivery loop.
- [`artifact-templates.md`](artifact-templates.md) — normative persisted
  artifacts, console responses, and the sole product bundle layout.
- [`integration-and-handoffs.md`](integration-and-handoffs.md) — fresh-context
  OpenSpec integration, name matching, and the sole normative proposal prompt.
- [`discovery-and-baseline-validation.md`](discovery-and-baseline-validation.md)
  — discovery and baseline checks and stopping rules.
- [`test-plan.md`](test-plan.md) — description-boundary and behavioral tests.
- [`workflow.md`](workflow.md) — historical, non-normative design summary.

## Non-goals

This design does not modify external OpenSpec, verify implementation at the
product layer, keep delivery ledgers, close or archive the product bundle,
coordinate concurrent writers, or add correction, abandonment, reopening,
rollback, locking, or delivery-repair workflows.
