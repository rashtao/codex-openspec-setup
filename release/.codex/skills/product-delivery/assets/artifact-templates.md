# Exact artifact and console templates

These templates are normative for `product-delivery`. Angle-bracketed values are
placeholders. Optional content is explicitly marked; every other field and
heading is required. Persisted paths are repository-relative and use `/`
separators.

`schema_version: 1` is the only supported schema version. A different value
blocks the current action before mutation; product skills do not migrate
artifacts.

## Delivery artifacts

### `delivery/roadmap.md`

```markdown
# First-release delivery roadmap — <product name>

## Coverage

| Requirement | Declared coverage |
|---|---|
| REQ-0001 | NOT DELIVERED |
| REQ-0002 | PARTIALLY DELIVERED (slice-001-customer-starts) |
| REQ-0003 | DELIVERED (slice-001-customer-starts, slice-002-customer-finishes) |

## Candidate slices

### Candidate — <outcome title>

- Outcome: <independently demonstrable user or system outcome>
- Likely requirements: <only uncovered or partial REQ-* IDs>
- Sequencing rationale: <why this outcome should occur now>
```

The coverage table contains every active baseline requirement exactly once and
uses only:

```text
NOT DELIVERED
PARTIALLY DELIVERED (<comma-separated canonical slice names>)
DELIVERED (<comma-separated canonical slice names>)
```

Candidate headings are unnumbered. Candidate entries contain no execution or
readiness fields. The first roadmap sets every row to `NOT DELIVERED`;
subsequent `roadmap` invocations preserve coverage values.

### Active and archived `delivery/slice-NNN-short-slug.md`

`````markdown
---
schema_version: 1
kind: product-delivery-slice
product: "<product-id>"
name: "slice-NNN-short-slug"
created_at: "<RFC3339 UTC>"
roadmap: "docs/product/<product-id>/delivery/roadmap.md"
---

# <Outcome title>

## Outcome

<One independently demonstrable product outcome.>

## Requirement coverage

| Requirement | Coverage declared by this slice | Rationale |
|---|---|---|
| REQ-0001 | partial | <precise remaining boundary> |
| REQ-0002 | complete | <why the whole baseline obligation is included> |

Only `partial` and `complete` are allowed. Requirements already declared
`DELIVERED (...)` in the pre-selection roadmap do not appear.

## In scope

- <behavior included in this one change>

## Out of scope

- <adjacent behavior excluded from this change>

## Planning context

- Baseline: <relevant requirement paths and concise context>
- Archived product slices: <paths and implications, or `none`>
- Canonical OpenSpec specs: <paths and implications, or `none`>
- Archived OpenSpec changes: <paths and implications, or `none`>
- Current code: <paths and implications, or `none`>

## Proposal prompt

```text
<fully rendered normative OpenSpec proposal handoff>
```
`````

`archive` moves this file without changing it, so the archived form uses the
same template.

## Normative OpenSpec proposal handoff

Render every placeholder before persisting and printing this prompt:

`````text
$openspec-propose

Create exactly one planning-only OpenSpec change for the greenfield product
delivery slice below. This is a fresh session; derive context from the named
repository artifacts and do not rely on prior conversation.

Required change name: slice-NNN-short-slug
Product bundle: docs/product/<product-id>
Accepted baseline: docs/product/<product-id>/baseline/manifest.yaml
Active product slice:
docs/product/<product-id>/delivery/slice-NNN-short-slug.md

Read the entire active product slice, the current code, and the canonical
`openspec/specs/` needed to plan this outcome. Create exactly
`slice-NNN-short-slug` using the installed OpenSpec schema. Produce every
planning artifact required by that schema, including detailed behavioral
requirements, scenarios, design, and tasks. Preserve the slice's in-scope and
out-of-scope boundaries and keep it vertical and independently demonstrable.

Do not implement code, apply tasks, verify behavior, synchronize canonical
specs, archive the change, create another change, or edit anything under
`docs/product/<product-id>/`. If the required name cannot be used or the
outcome cannot form one coherent change, stop and report the evidence.

After proposal creation, the user runs the external workflow for exactly
`slice-NNN-short-slug`:

`$openspec-apply-change slice-NNN-short-slug`
`$openspec-verify-change slice-NNN-short-slug`
`$openspec-archive-change slice-NNN-short-slug`

Then run:
`$product-delivery archive`
`````

The product skill prints this handoff but never invokes it. External OpenSpec
actions run in fresh sessions and retain their own contracts.

## Exact console envelopes

Every response uses the four common sections in this order. The action-specific
section appears between `Summary` and `Next`.

```text
<Action>: <done|needs-input|blocked>

Changed:
- <repository-relative path and operation, or `none`>

Summary:
- <action-specific result>

<Action-specific section>

Next:
<exact skill invocation or external OpenSpec step>
```

Use `done` when the action completed or delivery is already complete,
`needs-input` when a user answer or product decision is required, and
`blocked` when repository evidence or a workflow gate prevents the action.
List every actual changed path; never claim a write from response text alone.

### Roadmap

```text
Roadmap: <done|needs-input|blocked>

Changed:
- `docs/product/<product-id>/delivery/roadmap.md` (<created|replaced>)
<or `- none`>

Summary:
- <initial roadmap created and baseline accepted, roadmap candidates revised, or gate>

Candidates:
1. <outcome> — <likely REQ-* IDs> — <sequencing rationale>
<repeat, or `- none`>

Next:
<$product-delivery slice, $product-definition baseline, or $product-delivery roadmap>
```

### Slice

`````text
Slice: <done|needs-input|blocked>

Changed:
- `docs/product/<product-id>/delivery/slice-NNN-short-slug.md` (created)
- `docs/product/<product-id>/delivery/roadmap.md` (replaced)
<or `- none`>

Summary:
- <slice name and outcome, delivery complete, no coherent slice, or gate>

Coverage:
- REQ-0001: partial — <precise remaining boundary>
- REQ-0002: complete — <why the full obligation is included>
<repeat, or `- none`>

Proposal:
```text
<complete rendered normative OpenSpec proposal handoff>
```
<or `none` without a code fence>

Next:
<$openspec-propose using the proposal above, $product-delivery roadmap, Delivery complete., or one exact external OpenSpec step>
`````

On successful creation, `Next` is:

```text
$openspec-propose using the proposal above in a fresh session
```

### Archive

```text
Archive: <done|needs-input|blocked>

Changed:
- `<source>` → `<destination>` (moved unchanged)
<or `- none`>

Summary:
- <slice archived unchanged, missing OpenSpec archive, destination conflict, or gate>

Archive:
- Source: <repository-relative path or `none`>
- Destination: <repository-relative path or `none`>
- OpenSpec archives: <matching direct-child basenames or `none`>

Next:
<$product-delivery slice, $product-delivery archive, one exact external OpenSpec step, or Delivery complete.>
```

When the matching OpenSpec archive is absent, `Next` is the exact external
step `$openspec-archive-change <slice-name>`; the summary says to invoke
`$product-delivery archive` after that external action succeeds. A successful
move uses `$product-delivery slice` while any roadmap row remains uncovered
or partial, and `Delivery complete.` otherwise.

