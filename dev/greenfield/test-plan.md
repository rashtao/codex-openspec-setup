# Test plan for the future product skills

## Test philosophy

Acceptance uses clean-room, repository-level forward tests. Tests invoke the
public skills and inspect persisted artifacts; expected response text alone is
not sufficient when an action should write.

Every scenario records:

- stable case ID and exact prompt;
- fixture path inventory and relevant file contents;
- model, reasoning effort, host version, and available-skill inventory;
- transcript and material output artifacts;
- version-control diff and file inventory before and after;
- deterministic assertions and any semantic review rubric;
- `pass`, `fail`, or `invalid`, preserving infrastructure errors.

Except for an immediately pending interview response or same-session preview
confirmation, every invocation starts in a clean session. Routed product-agent
evidence must show `gpt-5.6-sol`, exactly one dispatch, and
`fork_turns: "none"`. Existing external OpenSpec actions run in separate
fresh sessions and retain their own behavior.

## Test assets

Future fixtures and case manifests live outside the installed skill packages,
for example:

```text
release/test/product-workflow/
  description-cases.json
  forward-cases.json
  fixtures/
    empty-greenfield/
    brownfield-code/
    discovery-unknowns/
    baseline-draft/
    baseline-approved/
    delivery-roadmap/
    active-product-slice/
    active-openspec-change/
    archived-openspec-change/
```

Generated transcripts and run outputs belong in an ignored run directory.
Installed `product-shared` remains passive and contains no test runner.

## Static contract audits

Run scoped searches over `dev/greenfield/**` and later over the implemented
product packages to assert:

- every product-owned skill, agent, artifact kind, invocation, and routed action
  uses `product-*`;
- no legacy product-owned identifier remains;
- no executable helper, script directory, content-binding algorithm, content
  identity field, baseline-byte manifest, or test-fixture content identity
  remains;
- external actions keep their existing names:
  `$openspec-propose`, `$openspec-apply-change`,
  `$openspec-update-change`, `$openspec-verify-change`, and
  `$openspec-archive-change`;
- delivery artifacts are limited to `roadmap.md`, zero or one canonical active
  slice, and canonical direct-child archived slices;
- there is no delivery ledger, separate slice identifier family, accepted
  delivery-deviation identity, persisted proposal packet, delivery control
  state, completion receipt, product-bundle archive transition, or product-level
  completion phase;
- the old validation document is absent and
  `discovery-and-baseline-validation.md` is present;
- no delivery repair, abandonment, reopening, rollback, lock, transaction,
  emergent-obligation, enabling-slice, or filesystem-hardening mode exists.

These are inventory and text-contract assertions, not executable-helper tests.

## Description-boundary tests

Frontmatter selection is explicit-only. Prompts without a `$skill-name` token
are `near_miss`, even when their topic resembles the workflow.

| Case | Prompt without an explicit skill token | Expected |
|---|---|---|
| `DESC-DISC-001` | “Help me brainstorm users and requirements for a new app.” | Do not select discovery |
| `DESC-DISC-002` | “Interview me breadth-first about this greenfield product.” | Do not select discovery |
| `DESC-DISC-003` | “Explore whether this idea is worth building.” | Prefer ordinary conversation or `openspec-explore` |
| `DESC-BASE-001` | “Turn these notes into a comprehensive product requirements document.” | Do not select baseline |
| `DESC-BASE-002` | “Review this requirements baseline for contradictions.” | Do not select baseline |
| `DESC-BASE-003` | “Freeze these docs so nobody changes them.” | Do not select baseline |
| `DESC-DEL-001` | “Break this feature into vertical slices.” | Do not select delivery |
| `DESC-DEL-002` | “Propose and implement the next OpenSpec change.” | Select the applicable external OpenSpec action, not product delivery |
| `DESC-DEL-003` | “Archive this completed OpenSpec change.” | Select the external OpenSpec archive action |
| `DESC-SHARED-001` | “Use product-shared to validate my product.” | Passive package refuses a user-facing action and points to a public skill |

Held-out cases vary phrasing without copying design prose. Explicit invocation
tests cover every valid mode, a missing mode, an unknown mode, a misspelled
product skill, and explicit passive-shared invocation. Invalid modes print usage
and write nothing.

Activation is `selected`, `not_selected`, or `unknown` only when supported
by a documented host signal. Output behavior is graded separately.

## Discovery and baseline artifact tests

For each discovery, baseline, state, and review-receipt template, test:

- minimal and fully populated valid instances;
- missing required key or heading;
- duplicate YAML key and unsupported `schema_version`;
- invalid enum or value type;
- duplicate, malformed, reused, or counter-exceeding ID;
- dangling ID and path reference;
- absolute local path, drive path, `file:` URI, home shorthand, parent
  traversal, and symlink escape;
- unsorted manifest records;
- structural, schema, traceability, terminology, journey/domain, contradiction,
  duplicate, unknown-treatment, and repository-relative-path review failures.

There are no approved-baseline byte-comparison cases. Approval tests the
presence and status of the review receipt and the user's attestation.

## Forward discovery and baseline scenarios

### `FWD-001` — Initialize a genuinely empty product

Invoke:

```text
$product-discovery init parcel-tracker
```

Expect one routed agent, exact state and four discovery files, phase
`discovery`, zero ID counters, no baseline/delivery/OpenSpec/application write,
and the exact interview invocation.

### `FWD-002` — Refuse a brownfield repository

Use a fixture with a functioning endpoint and canonical spec, then one with
only archived OpenSpec history. `init` lists all evidence, creates no bundle,
and does not offer deletion or conversion.

### `FWD-003` — Breadth-first interview with explicit unknowns

The user answers eight independent questions, decides a first-release actor,
says “I don’t know” about carrier retention, defers accessibility assessment to
a slice, and excludes paid billing. Expect one verbatim round, unique IDs,
precise unknown treatment, explicit exclusion, no dependent same-round
follow-up, and a cross-area next frontier.

### `FWD-004` — User requests synthesis early

Allow synthesis when several rows remain partial but every uncertainty is a
precise `UNK-*` or `OOS-*`. Preserve included and excluded treatments and do
not invent behavior. A paired fixture with one `FOG-*` writes no baseline.

### `FWD-005` — Fresh synthesis ignores conversation-only facts

Put a material preference only in the parent conversation. The child packet
uses `fork_turns: "none"`; the baseline excludes that preference and reports a
gap if persisted evidence is insufficient.

### `FWD-006` — Structural review and validate-then-trust approval

A valid draft produces an `approval-ready` receipt with all checks passing and
no content-binding field. Change a draft sentence after review, then invoke
`$product-baseline approve`. The skill does not compare candidate content;
the invocation is treated as user attestation and freezes the draft. Pair this
with an `issues` receipt, which must stop approval without changing the
manifest.

### `FWD-007` — Approved baseline is trusted

After approval, change a baseline file in a fixture and invoke roadmap. The
delivery skill does not perform a frozen-byte comparison and proceeds from the
current user-protected artifacts. It does not claim to have detected or
accepted a baseline edit.

## Forward delivery scenarios

### `FWD-008` — Roadmap inputs and initial coverage

With complete discovery and frozen baseline artifacts, invoke
`$product-delivery roadmap`. Assert that it reads all and only those product
context inputs, initializes every `REQ-*` to `NOT DELIVERED`, and produces
unnumbered candidates with outcome, likely requirements, and sequencing
rationale. No candidate contains readiness or execution fields.

### `FWD-009` — Roadmap always waits for confirmation

For both first creation and later revision, the first response contains the
complete proposed change and writes nothing. Rejecting leaves the tree
unchanged. Same-session confirmation performs exactly the previewed write. A
confirmation in a new session does not authorize the earlier preview.

### `FWD-010` — Active-slice roadmap revision changes candidates only

With one active canonical slice and its already-declared partial and complete
coverage, revise the roadmap. The preview may reorder or replace unnumbered
candidates but preserves every coverage value declared by the active slice.

### `FWD-011` — Active product slice gates

One canonical delivery-root slice stops `slice` and points to finishing its
external workflow. Two canonical active slices are an error naming both. A
noncanonical delivery-root file is ignored.

### `FWD-012` — Active OpenSpec change gate

Any direct child such as `openspec/changes/fix-logging/` stops `slice` before
selection and no pending change contents are read. No product or OpenSpec file
is written.

### `FWD-013` — Proposed-name collisions

Derive the next number from the highest canonical active or archived product
slice plus one. Stop if the proposed name equals an active OpenSpec basename or
an external OpenSpec archive direct-child basename ends in
`-<proposed-name>`. Ignore noncanonical product delivery-root files. Do not
invent a suffix.

### `FWD-014` — Whole-system slice inputs and exclusions

Assert reads of the complete roadmap, whole frozen baseline, every canonical
archived product slice, canonical OpenSpec specs, archived OpenSpec changes, and
current code. Assert no discovery read and no pending OpenSpec change-content
read. The preview cites planning context from the allowed inputs.

### `FWD-015` — Slice confirmation and immediate roadmap coverage

Preview the canonical name, exact partial/complete coverage, boundaries,
planning context, complete proposal prompt, and complete roadmap change. Before
confirmation nothing changes. After same-session confirmation:

- one canonical active slice exists;
- its only external prompt begins with `$openspec-propose` and requires the
  exactly same change name;
- partial coverage becomes or extends
  `PARTIALLY DELIVERED (<slice names>)`;
- complete coverage immediately becomes `DELIVERED (<slice names>)`;
- no OpenSpec change or code is created.

### `FWD-016` — Delivered requirements cannot enter a slice

Use a roadmap mixing all three coverage forms. The preview may contain only
`NOT DELIVERED` or `PARTIALLY DELIVERED (...)` requirements. Any attempt to
include an already delivered requirement stops without writes.

### `FWD-017` — No coherent remaining slice

When the remaining eligible requirements cannot form one coherent vertical
outcome, expect a warning, no file change, and final output:

```text
$product-delivery roadmap
```

### `FWD-018` — Product archive uses suffix-only authorization

With one active `slice-004-export-audit-log.md`, provide multiple direct-child
OpenSpec archives whose basenames end in
`-slice-004-export-audit-log`. Make their contents incomplete, conflicting, or
unreadable to the product skill. Invocation attests manual destination
inspection; the skill does not inspect `delivery/archive/`, accepts the
multiple suffix matches, does not read OpenSpec archive contents, and moves the
active slice unchanged. It prints exactly `$product-delivery slice`.

### `FWD-019` — Archive errors

With no active canonical product slice, `archive` stops without inspecting the
destination. With one active slice and no matching external suffix, it reports
the expected canonical name and instructs the user to complete and archive that
OpenSpec change before retrying. Near matches do not authorize a move.

### `FWD-020` — Read-only delivery status

Test the first-match order:

1. missing roadmap → `$product-delivery roadmap`;
2. active slice → finish its external OpenSpec workflow, then
   `$product-delivery archive`;
3. uncovered or partial requirement → `$product-delivery slice`;
4. full declared coverage → exactly `Delivery is complete.`.

Every case has zero writes. Multiple active slices produce a named error.

### `FWD-021` — Completion creates nothing else

Invoke both `slice` and `status` on full declared coverage. Both print exactly
`Delivery is complete.`; `slice` creates nothing. Assert the product remains
in phase `delivery` and no completion receipt, final phase, bundle destination,
or additional product artifact appears.

## Routing and fresh-context checks

For every routed product action, assert:

- `fork_turns` is exactly `"none"`;
- model and effort match `skill-contracts.md`;
- the packet names the action, mode, verbatim request, working-directory
  semantics, product root or unresolved state, and exact `SKILL.md`;
- it forbids rerouting and further children;
- it contains no inaccessible parent-context reference.

For every printed external OpenSpec prompt, start a new session with only that
text and the fixture repository. The action must be resolvable without the
product-workflow transcript. Product skills must not directly dispatch it.

## External OpenSpec preservation checks

Before and after every mutating forward case, compare path inventory, file mode,
symlink target, and version-control diff for:

```text
release/.codex/skills/openspec-*/**
release/.codex/agents/openspec-*.toml
release/openspec/config.yaml
```

Any product-workflow modification inside these external OpenSpec-owned paths is
a failure. Also assert that product skills never modify application code,
`openspec/changes/`, `openspec/specs/`, or frozen baseline files.

## Structured candidate-versus-baseline evaluation

Run a small development evaluation because the workflow spans fresh contexts
and optimistic state. Compare the candidate product skills with a `no_skill`
baseline using identical substantive fixtures, model settings, tools, and clean
contexts. Keep attempts and infrastructure failures visible.

Use three materially different cases:

1. classify mixed discovery answers without inventing decisions or erasing
   deferrals;
2. perform approval-ready validate-then-trust approval without trying to bind
   the draft to the receipt;
3. create, externally complete, and suffix-authorize one slice while preserving
   the active slice content through its product archive move.

Criteria cite transcripts and resulting artifacts. Conclusions are limited to
this development evidence and make no production reliability claim.

## Acceptance gate

The future implementation is ready for review only when:

- all static contract, template, description, and forward cases pass;
- discovery and baseline behavior remains intact under the new names;
- every delivery preview and confirmation behaves as specified;
- archive authorization is suffix-only and does not inspect either archive
  content or the user-attested product destination;
- external OpenSpec-owned files remain unchanged;
- no removed product identifier, helper machinery, delivery ledger/control
  state, product-level verification, completion phase, or product-bundle
  archival behavior remains;
- each response ends with the required single next step or stop report.
