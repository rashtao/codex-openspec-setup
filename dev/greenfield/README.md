# Greenfield product workflow

Status: design contract for two future Codex skills.

This directory defines a small, user-controlled workflow for discovering one
greenfield product, establishing its first-release baseline, and delivering it
through one external OpenSpec change at a time.

```text
$product-definition discover
→ $product-definition baseline
→ $product-delivery roadmap
→ $product-delivery slice
→ external OpenSpec propose → apply → verify → archive
→ $product-delivery archive
→ repeat
```

## Principles

- The two skills run only when explicitly invoked.
- Run Codex CLI with GPT-5.6 Sol. High reasoning suits ordinary actions;
  xhigh is recommended for baseline synthesis. The skills neither select nor
  enforce a model or reasoning level.
- Each invocation performs one named action directly. It does not route work,
  spawn agents, run scripts, or maintain a workflow state machine.
- Mutating actions write their final artifacts immediately. Git provides
  history and recovery.
- The user owns scope, implementation, review, corrections, archive judgment,
  and protection of accepted product artifacts.
- Persisted artifacts are the only cross-session context. Progress follows
  their presence and the latest incomplete interview round.
- The first creation of `delivery/roadmap.md` accepts the current baseline for
  delivery. Definition actions stop after that file exists.
- Roadmap coverage is an optimistic planning declaration made when a slice is
  created. It is not evidence of implementation or verification.
- Product skills never invoke or mutate the external OpenSpec workflow.

## Boundaries

The workflow assumes one product, one repository, one user, and one writer.
Initialization is for a genuinely greenfield repository with a local OpenSpec
configuration. Product artifacts live under `docs/product/<product-id>/`.
OpenSpec continues to own detailed change requirements, scenarios, designs,
tasks, implementation, verification, canonical specifications, and its change
archive.

There is no product action for status, repair, rollback, reopening, locking,
implementation, verification, or baseline versioning. Once delivery starts,
the user makes any necessary corrections directly and relies on Git for
recovery.

## Authoritative documents

- [`skill-contracts.md`](skill-contracts.md) defines the two packages, five
  actions, action inputs, completion criteria, and mutation boundaries.
- [`artifact-templates.md`](artifact-templates.md) defines the exact product
  artifacts, console envelopes, and external OpenSpec handoff.
- [`test-plan.md`](test-plan.md) defines structural and behavioral acceptance.

These four files are the complete greenfield design. No historical workflow,
standalone state, validation, routing, or integration document is normative.

## Deferred simplifications

The following ideas remain future options and are not part of this revision:

- retain only `REQ-*` identifiers and remove discovery-level identifiers;
- merge discovery documents or baseline documents if their granularity proves
  costly;
- remove the product-side archive action and rely only on OpenSpec archives;
- replace named actions with natural-language intent after the workflow is
  stable.
