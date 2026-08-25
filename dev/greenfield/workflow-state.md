# Workflow and state transitions

## Primary lifecycle

```text
absent
  └─ discovery:init → discovery
       └─ baseline:synthesize → baseline-draft
            ├─ discovery changes → baseline-draft, review invalidated
            └─ baseline:review → baseline-reviewed
                 └─ baseline:approve → baseline-frozen
                      └─ delivery:roadmap → delivery
                           └─ delivery:slice
                                → external OpenSpec workflow
                                → delivery:archive
                                → delivery:slice
```

Primary phase values are exactly:

```text
discovery
baseline-draft
baseline-reviewed
baseline-frozen
delivery
```

Temporary conditions exist only for discovery and baseline:

```text
none
awaiting-interview-response
awaiting-discovery-choice
awaiting-baseline-approval
```

Delivery has no control-state fields or lifecycle conditions. It derives its
position from `delivery/roadmap.md`, canonical active slice filenames, and the
allowed OpenSpec directory names.

## Product control state

The exact `.workflow/state.yaml` template is:

```yaml
schema_version: 1

product:
  id: "<product-id>"
  name: "<product-name>"
  release: "first-usable-release"
  root: "docs/product/<product-id>"

phase: "discovery"
condition: "none"

discovery:
  next_round: 1
  awaiting_round: null
  synthesis_recommended: false

baseline:
  manifest: "docs/product/<product-id>/baseline/manifest.yaml"
  review_receipt: null

blockers: []

highest_allocated_ids:
  FACT: 0
  PDEC: 0
  ASM: 0
  UNK: 0
  FOG: 0
  OOS: 0
  SRC: 0
  REQ: 0

created_at: "<RFC3339 UTC>"
last_transition_at: "<RFC3339 UTC>"
```

Discovery and requirement identifiers are monotonically allocated and never
reused. Rejection, merging, supersession, or invalidation may leave gaps.

The user is responsible for single-writer operation and avoiding concurrent
edits. No product workflow mechanism coordinates competing instances.

## Initialization

`product-discovery init` requires a lowercase kebab-case product ID and an
installed local release containing `openspec/config.yaml` or
`openspec/config.yml`.

Initialization allows repository metadata, build and development tooling,
empty scaffolding, disposable prototypes explicitly identified as disposable,
and the installed OpenSpec release distribution. It stops when evidence shows:

- durable application behavior;
- canonical specs under `openspec/specs/`;
- active or archived OpenSpec delivery history;
- another non-archived product bundle.

Ambiguous code is reported rather than silently classified. Initialization
never installs OpenSpec, deletes files, or converts a brownfield repository.
On success it creates `.workflow/state.yaml` and the four discovery documents,
then prints `$product-discovery interview`. It creates no baseline or delivery
artifact.

## Breadth-first discovery

Each interview round:

1. reads the persisted discovery map;
2. identifies every independent question on the current frontier;
3. selects approximately five to eight questions spanning different product
   areas;
4. includes a recommended answer when evidence supports one;
5. waits for the complete user response;
6. immediately records decisions, facts, assumptions, unknowns, fog, sources,
   and exclusions;
7. recalculates the frontier.

Questions whose answers depend on another open question wait for a later round.
When the user says “I don’t know,” the skill classifies the issue as
researchable, safely assumable, deferred to a delivery slice, deferred to a
future OpenSpec change, excluded from the release, or still too vague and
therefore `FOG-*`.

External research is allowed only for material external facts. It uses primary
sources, records the access date and narrowly supported claim, and never
decides a product preference. Approval-gated or paid research requires user
approval.

## Discovery stopping rule

When discovery appears sufficient, the skill asks:

> Discovery appears sufficient to draft the first-release baseline. Would you
> like another interview round, or should the baseline skill synthesize a draft
> now?

This recommendation is not a hard coverage gate. The user may request synthesis
earlier and may retain explicit unknowns regardless of risk. Synthesis requires
every unresolved area to be expressible as `UNK-*` or `OOS-*`; any remaining
`FOG-*` stops synthesis.

## Baseline draft, review, and approval

### Synthesis

The routed synthesis agent receives no conversation history and reads only:

```text
docs/product/<product-id>/discovery/**
docs/product/<product-id>/.workflow/state.yaml
```

It does not read application code, OpenSpec artifacts, the original
conversation, or a previous draft as a source of truth. It normalizes
terminology, identifies domain responsibility hypotheses, separates domain and
cross-cutting requirements, allocates `REQ-*` IDs, detects duplicates and
contradictions, and writes a complete `status: draft` baseline. It reports
gaps rather than inventing answers.

### Review

The fresh reviewer reads all discovery and candidate-baseline artifacts and
never repairs the baseline. A passing review requires:

- exact artifact-template and schema compliance;
- unique requirement IDs and one owning location per requirement;
- complete source traceability;
- terminology consistency;
- no unresolved duplicate or contradictory requirements;
- coherent actor journeys and domain responsibilities;
- explicit treatment of every retained unknown;
- repository-relative persisted paths.

Issues produce a receipt with `status: issues`, preserve the draft, and return
identified gaps to discovery. A passing review writes `status: approval-ready`.

### Approval

`product-baseline approve` requires a current review receipt with
`status: approval-ready`. Its invocation is both user approval and user
attestation that the reviewed draft was not changed afterward. The skill does
not bind the receipt to file bytes.

Approval changes `manifest.yaml` from `draft` to `frozen`, records approval
metadata, and changes the primary phase to `baseline-frozen`. No later action
checks frozen baseline bytes. There is no reopening, editing, refreezing, or
baseline v2; preserving the frozen files is the user's responsibility.

## Delivery artifacts and identity

Delivery persists only:

```text
docs/product/<product-id>/delivery/
  roadmap.md
  slice-NNN-short-slug.md              # zero or one active file
  archive/
    slice-NNN-short-slug.md            # archived direct children
```

A canonical slice filename matches:

```regex
^slice-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$
```

The slice name is the filename without `.md`. There is no separate slice ID.
Files in the delivery root that do not match the pattern are ignored when
finding active slices or allocating the next number.

## Roadmap

`product-delivery roadmap` requires complete discovery and a frozen baseline.
For product context it reads every discovery and baseline artifact and no code,
canonical OpenSpec spec, or OpenSpec change. When revising an existing roadmap,
it may also read the roadmap, canonical active slice, and archived slice
records needed to preserve declarations already made.

The first roadmap:

- contains one coverage row for every `REQ-*`;
- initializes every row to `NOT DELIVERED`;
- contains unnumbered candidate slices with an outcome, likely uncovered or
  partial requirements, and sequencing rationale;
- contains no readiness, execution, dependency, blocker, or closure field.

Coverage values are exactly:

```text
NOT DELIVERED
PARTIALLY DELIVERED (<comma-separated canonical slice names>)
DELIVERED (<comma-separated canonical slice names>)
```

Every invocation shows the complete proposed roadmap change and waits for
same-session user confirmation before writing. While a canonical active slice
exists, `roadmap` may change candidate slices only. It never changes any
coverage already declared by that active slice.

Candidate slices are planning suggestions, not identities. They remain
unnumbered until `slice` materializes one.

## Slice

`product-delivery slice` follows this order:

1. Enumerate canonical active slice filenames in the delivery root. More than
   one is an error. One stops the action because it must finish and archive
   before another can be created.
2. Enumerate direct children of `openspec/changes/`, excluding the
   `archive` directory. Any active OpenSpec change stops the action; contents
   of pending changes are never read.
3. Read the entire roadmap. If every coverage row is `DELIVERED (...)`, create
   nothing and output exactly `Delivery is complete.`.
4. Read the whole frozen baseline, all canonical archived slice files, all
   canonical OpenSpec specs, all archived OpenSpec changes, and current code.
   Do not read discovery or pending OpenSpec change contents.
5. Find the highest number among visible canonical active and archived product
   slice filenames and add one. Render it as three digits.
6. Form a short lowercase hyphenated slug from the selected outcome. Reject an
   empty slug or a number above 999.
7. Stop if the proposed canonical name equals an active OpenSpec basename or if
   any direct child of `openspec/changes/archive/` has a basename ending in
   `-<proposed-canonical-name>`. Near matches that do not satisfy that suffix
   do not collide.
8. Form one coherent vertical slice using only requirements currently marked
   `NOT DELIVERED` or `PARTIALLY DELIVERED (...)`.

If no coherent slice can be formed, the skill warns, creates nothing, and
prints:

```text
$product-delivery roadmap
```

Otherwise it previews:

- the canonical `slice-NNN-short-slug` name;
- each requirement's precise `partial` or `complete` coverage;
- explicit in-scope and out-of-scope boundaries;
- planning context from baseline, archived slices, canonical specs, archived
  OpenSpec changes, and current code;
- the exact embedded `$openspec-propose` prompt;
- the complete roadmap change.

No file changes before same-session confirmation. On approval, the skill writes
the active slice and immediately applies the previewed roadmap coverage:
complete becomes `DELIVERED (...)`, while partial becomes or extends
`PARTIALLY DELIVERED (...)`. This is an optimistic declaration and does not
claim implementation has occurred.

The active slice contains exactly one proposal prompt requiring the external
OpenSpec change to use the identical canonical name. Proposal, apply, verify,
and OpenSpec archive then proceed independently through the existing external
workflow.

## Archive

Invoking `product-delivery archive` attests that the user manually inspected
`docs/product/<product-id>/delivery/archive/` and accepts the destination.
The skill does not list, read, or otherwise inspect that destination.

The action requires exactly one canonical active slice in the delivery root.
Its sole external archive check enumerates direct-child basenames under
`openspec/changes/archive/` and asks whether at least one ends in
`-<slice-name>`.

- Zero matches stops, reports the expected slice name, and tells the user to
  complete and archive that OpenSpec change before retrying.
- One or multiple suffix matches authorize the move. Prefix shape, date,
  ambiguity, active twins, archive contents, tasks, implementation,
  verification, canonical synchronization, and spec contents are not checked.

On authorization, the action moves the active slice file unchanged to
`delivery/archive/<same-filename>`. It does not alter the roadmap or any
content. After a successful move it always prints exactly:

```text
$product-delivery slice
```

## Status

`product-delivery status` is read-only and applies the first matching rule:

1. Missing roadmap: print `$product-delivery roadmap`.
2. One canonical active slice: identify it, tell the user to finish its
   external OpenSpec workflow, then print `$product-delivery archive`.
3. Any `NOT DELIVERED` or `PARTIALLY DELIVERED (...)` row: print
   `$product-delivery slice`.
4. Full declared coverage: print exactly `Delivery is complete.`.

Multiple canonical active slices are reported as an error. Noncanonical
delivery-root files do not affect the result.
