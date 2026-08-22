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
                           ├─ delivery:next → selected slice
                           ├─ manual OpenSpec proposal → change-active
                           ├─ manual apply/verify/archive → archived
                           ├─ delivery:reconcile → delivered
                           └─ all obligations terminal
                                └─ delivery:close
                                     → release-ready → closed
```

Primary phase values are exactly:

```text
discovery
baseline-draft
baseline-reviewed
baseline-frozen
delivery
release-ready
closed
```

Temporary conditions are separate from primary phases:

```text
none
awaiting-interview-response
awaiting-discovery-choice
awaiting-baseline-approval
awaiting-slice-choice
active-change
reconciliation-blocked
awaiting-promotion-choice
```

`blockers` carries concrete evidence and safe user action. A blocker is not a
new lifecycle phase.

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
  hashes: null

delivery:
  current_slice: null
  expected_change: null
  sealed_handoff: null
  sealed_handoff_sha256: null

closure:
  source: null
  destination: null
  receipt: null
  closed_at: null

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
  SLICE: 0
  DEV: 0

created_at: "<RFC3339 UTC>"
last_transition_at: "<RFC3339 UTC>"
```

Identifiers are monotonically allocated and never reused. Rejection, deletion,
merging, supersession, or invalidation may leave gaps.

There is intentionally no concurrency revision or long-lived lock. The user is
responsible for running one Codex instance and avoiding concurrent edits.

## Initialization

`discovery init` requires a lowercase kebab-case product ID and an installed
local release with `openspec/config.yaml`.

Initialization allows:

- repository metadata;
- build and development tooling;
- empty scaffolding;
- disposable prototypes explicitly identified as disposable;
- the installed OpenSpec release distribution.

It blocks when evidence shows:

- durable application behavior;
- canonical specs under `openspec/specs/`;
- active or archived OpenSpec delivery history;
- another non-archived product bundle.

Ambiguous code is reported to the user instead of being silently classified.
Initialization never installs OpenSpec, deletes files, or converts a brownfield
repository into a greenfield one.

On success it creates `.workflow/state.yaml` and the four discovery documents,
then stops and prints the explicit `interview` invocation. It does not create a
draft baseline or roadmap.

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

When the user says “I don’t know,” the skill classifies the issue as one of:

- researchable;
- safely assumable;
- deferred to a delivery slice;
- deferred to a future OpenSpec change;
- excluded from the release;
- still too vague and therefore `FOG-*`.

External research is allowed only for material external facts. It uses primary
sources, records access date and the exact supported claim, and never decides a
product preference. Approval-gated or paid research requires user approval.

## Discovery stopping rule

The agent asks the user when it judges that discovery is sufficient:

> Discovery appears sufficient to draft the first-release baseline. Would you
> like another interview round, or should the baseline skill synthesize a draft
> now?

This recommendation is not a hard coverage gate. The user may request synthesis
earlier and may retain explicit unknowns regardless of risk.

Synthesis requires every unresolved area to be expressible as `UNK-*` or
`OOS-*`. A remaining `FOG-*` blocks synthesis because the excluded matter is not
precise enough for informed approval.

## Baseline draft and review

### Synthesis

The routed synthesis agent receives no conversation history and may read only:

```text
docs/product/<product-id>/discovery/**
docs/product/<product-id>/.workflow/state.yaml
```

It must not read application code, current OpenSpec artifacts, the original
conversation, or a previous draft as a source of truth.

It normalizes terminology, identifies domain responsibility hypotheses,
separates domain and cross-cutting requirements, allocates `REQ-*` IDs, detects
duplicates and contradictions, and writes a complete `status: draft` baseline.
It reports gaps rather than inventing answers.

### Review

The fresh reviewer reads discovery and the candidate baseline. It never repairs
the baseline itself.

A passing review requires:

- exact artifact-template compliance;
- unique requirement IDs and one owning location per requirement;
- source traceability;
- terminology consistency;
- no unresolved duplicate or contradictory requirements;
- coherent actor journeys and domain responsibilities;
- explicit treatment of every retained unknown;
- repository-relative paths only.

Issues produce a non-approval receipt, preserve the draft for inspection, and
return the identified gaps to discovery.

### Approval

`approve` requires a current `approval-ready` receipt whose candidate digest
matches the current draft exactly. Its explicit invocation is the user's
approval.

Approval:

1. changes `manifest.yaml` from `draft` to `frozen`;
2. records approval metadata;
3. writes SHA-256 hashes for every baseline file, including the final manifest;
4. changes the primary phase to `baseline-frozen`.

There is no reopening, editing, refreezing, or baseline v2.

## Roadmap and slice selection

`roadmap` requires a valid frozen baseline. The roadmap is mutable planning and
does not require independent approval.

Slices are vertical and independently demonstrable. The first slice should be a
walking skeleton or a high-risk end-to-end path. Only the immediate frontier is
detailed; later slices remain coarse.

`next`:

1. validates the frozen baseline hashes;
2. checks that no active OpenSpec change exists;
3. calculates the ready frontier;
4. selects an unambiguous ready slice, or presents a recommendation and waits
   when materially different candidates are ready;
5. derives `slice-<NNN>-<slug>` as the expected OpenSpec change name;
6. seals the proposal handoff;
7. stops without creating an OpenSpec change;
8. prints a complete repository-relative prompt for a fresh session.

The user is responsible for avoiding an unexpected active change after the
handoff is sealed. The design adds no concurrency/race recovery mechanism.

## Slice state vocabulary

Roadmap entries carry independent readiness and execution fields.

```text
Readiness: candidate | ready | blocked
Execution: unstarted | selected | change-active | archived |
           delivered | invalidated
```

- `candidate`: plausible but not on the immediate frontier.
- `ready`: dependencies are satisfied and selection is allowed.
- `blocked`: a named dependency or decision prevents selection.
- `unstarted`: no sealed handoff exists.
- `selected`: a proposal handoff is sealed.
- `change-active`: the deterministic OpenSpec change exists.
- `archived`: the matching archive exists but ledger reconciliation has not
  completed.
- `delivered`: structural reconciliation succeeded.
- `invalidated`: the slice cannot continue and its ID remains retired.

## Delivery progression

The normal sequence is:

```text
product delivery next
→ manual openspec-propose
→ product delivery reconcile
→ manual openspec-apply-change
→ manual openspec-verify-change
→ manual openspec-archive-change
→ product delivery reconcile
```

The manually invoked OpenSpec verification is trusted as the sole behavioral
verification. Product reconciliation neither persists nor repeats it.

Emergent behavior may be added directly to the OpenSpec proposal/specification.
At archive reconciliation, the archived change itself is approval evidence.
The reconciler allocates `DEV-*`, updates the slice and ledger, and leaves the
original sealed handoff unchanged.

## Release closure

`close` requires:

- frozen baseline hashes still valid;
- no active OpenSpec changes;
- every `REQ-*` in a terminal disposition;
- every accepted `DEV-*` in a terminal disposition;
- implemented entries linked to archives and canonical specs;
- superseded and unimplemented entries linked to archived approval evidence;
- every relevant slice delivered or explicitly invalidated;
- no structural blocker.

Allowed terminal dispositions are:

```text
implemented
superseded
unimplemented-with-reason
```

Explicitly excluded `UNK-*` entries may remain unresolved and do not block
closure.

On success, `close` writes the release-reconciliation receipt, marks state
closed, and moves:

```text
docs/product/<product-id>/
→ docs/product/archive/YYYY-MM-DD-<product-id>-first-release/
```

It then prints a hint to review and explicitly promote useful content from the
archived `delivery/post-release.md`. Nothing is promoted automatically.

`product.root` and pre-close artifact references remain historical logical
paths; frozen files are never rewritten merely because the bundle moved.
`closure.source` records that logical root and `closure.destination` records the
dated physical location. A closed-bundle validator maps the source prefix to
the destination only for resolving file existence, while byte hashes and their
canonical logical-path aggregate remain unchanged.

There is no `abandoned` phase. Before baseline freeze the user may manually
remove the bundle. After freeze, an incomplete product remains in its current
phase until it satisfies closure.
