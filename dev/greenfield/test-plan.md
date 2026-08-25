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

Every top-level product-action dispatch inherits only the latest user turn.
Routed product-agent evidence must show exactly one dispatch, `fork_turns:
"1"`, and the exact model and effort from the mode route table. A same-session
response or confirmation is accepted only against matching persisted pending
state. Existing external OpenSpec actions run in separate fresh sessions and
retain their own behavior.

## Test assets

Future fixtures and case manifests live under the development-only
`dev/greenfield/test/product-workflow/` root. No product-workflow test asset is
stored under `release/` or inside an installed skill package.

```text
dev/greenfield/test/product-workflow/
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
  runs/                              # ignored transcripts and run outputs
```

Generated transcripts and run outputs belong in the ignored
`dev/greenfield/test/product-workflow/runs/` directory.
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
  state beyond the two pending-confirmation conditions and
  `.workflow/pending-delivery.yaml`, completion receipt, product-bundle archive
  transition, or product-level completion phase;
- every top-level product-action route uses `fork_turns: "1"`, and no product
  action treats older inherited conversation as product evidence;
- the pending-delivery schema, target counts and order, condition mapping, and
  exact interview pending markers match the normative templates;
- an interview round selects three through eight ready questions when at least
  three are ready, selects every ready question when fewer than three are
  ready, and spans product areas whenever more than one area is ready;
- at most one product bundle exists, with no archive exception;
- discovery and requirement identifiers use four digits while the separate
  delivery slice sequence intentionally accepts only `001` through `999`;
- only the repository-local `openspec/` root is resolved, and no registered
  standalone store is discovered, selected, or passed as a selector;
- every unsupported product-artifact `schema_version` stops the current action
  before mutation, and no product skill infers or performs a schema migration;
- no `README.md` or other undeclared auxiliary file exists inside an
  implemented product skill package;
- `product-shared/SKILL.md` contains the exact operating-assumptions index
  entry;
- the package layout, shared frontmatter description, and skill table do not
  promise a user-facing README;
- `product-shared/references/operating-assumptions.md` contains all six required
  operational trust contracts;
- every product package contains exactly one `agents/openai.yaml` with only the
  specified `interface` and `policy` mappings and their required keys;
- every interface display name, short description, and default prompt exactly
  matches `skill-contracts.md`;
- every short description is between 25 and 64 characters inclusive, and every
  default prompt contains its package's exact `$<skill-name>` token;
- every `policy.allow_implicit_invocation` value is boolean `false`; omission,
  string `"false"`, and boolean `true` fail;
- `.workflow/state.yaml` has no `discovery.synthesis_recommended`,
  `baseline.review_receipt`, or `highest_allocated_ids.REQ` field;
- only `discovery/map.md` owns the synthesis assessment, and only
  `baseline/manifest.yaml` owns the review-receipt path and `REQ-*` high-water
  mark;
- the complete normative `$openspec-propose` prompt appears exactly once under
  `integration-and-handoffs.md` → `Normative proposal prompt`;
- the active-slice template contains the exact proposal-prompt cross-reference
  and no copied prompt body;
- the complete product bundle tree appears exactly once under
  `artifact-templates.md` → `Product bundle layout`;
- `workflow.md` and `workflow-state.md` contain the exact bundle-layout
  cross-references and no duplicated product subtree;
- the README document index names the sole bundle-layout and proposal-prompt
  owners;
- the exact historical-status banner is the first line of `workflow.md`, and
  the README names that file as historical and non-normative;
- the normative first-candidate sequencing rule appears only in
  `workflow-state.md`, and the normative twelve-area rationale appears only in
  `discovery-and-baseline-validation.md`;
- no product-workflow fixture, case manifest, transcript, run output, test
  runner, or other test-only asset exists anywhere under `release/`;
- every public mode resolves to exactly one model, effort, and write posture;
  all models are GPT-5.6, only synthesis and review use `xhigh`, and every
  status uses `gpt-5.6-luna` with `low` effort;
- all three standalone `.toml` blocks use `gpt-5.6-sol`, `high`, and
  `workspace-write`, and contain the exact status no-write sentence;
- each public product `SKILL.md` contains its exact rendered marker guard before
  its spawn form, and the marker exactly matches frontmatter `name`;
- `product-shared` contains no routing guard or dispatch;
- `product-shared` contains no `assets/` directory, every implemented path is
  declared in its exact package layout, and no package sentence promises an
  asset or separate template directory;
- `product-shared/references/artifact-contracts.md` is the only installed owner
  of product-workflow artifact templates;
- the old validation document is absent and
  `discovery-and-baseline-validation.md` is present;
- no delivery repair, abandonment, reopening, rollback, lock, transaction,
  emergent-obligation, enabling-slice, or filesystem-hardening mode exists.

These are inventory and text-contract assertions, not executable-helper tests.

## Description-boundary tests

`policy.allow_implicit_invocation: false` is the primary explicit-only
enforcement mechanism. The frontmatter descriptions and the following
near-miss cases test defense in depth and semantic routing quality; they are not
the sole activation control. Prompts without a `$skill-name` token are
`near_miss`, even when their topic resembles the workflow.

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
product skill, and explicit passive-shared invocation. These cases verify both
policy enforcement and descriptive defense in depth. Invalid modes print usage
and write nothing.

Activation is `selected`, `not_selected`, or `unknown` only when supported
by a documented host signal. Output behavior is graded separately.

## Discovery and baseline artifact tests

For each discovery, baseline, state, review-receipt, and pending-delivery
template, test:

- minimal and fully populated valid instances;
- missing required key or heading;
- duplicate YAML key;
- unsupported `schema_version`, which stops before every write and never
  triggers inferred or automatic migration;
- invalid enum or value type;
- duplicate, malformed, reused, or counter-exceeding ID;
- dangling ID and path reference;
- absolute local path, drive path, `file:` URI, home shorthand, parent
  traversal, and symlink escape;
- unsorted manifest records;
- structural, schema, traceability, terminology, journey/domain, contradiction,
  duplicate, unknown-treatment, and repository-relative-path review failures.

Also test every valid and invalid combination of phase, condition,
`discovery.awaiting_round`, interview pending markers, pending-delivery action,
target count, target order, target operation, and target path.
For baseline review state, test a draft with a null receipt path, a draft with
an `issues` receipt, a reviewed baseline with an `approval-ready` receipt, and
every invalid phase/path/status permutation.

There are no approved-baseline byte-comparison cases. Approval tests the
presence and status of the review receipt and the user's attestation.

## Forward discovery and baseline scenarios

### `FWD-001` — Initialize a genuinely empty product

Invoke:

```text
$product-discovery init parcel-tracker
```

Expect one routed agent, exact state and four discovery files, phase
`discovery`, seven zero-valued discovery ID counters, no `REQ` counter, no
baseline/delivery/OpenSpec/application write, and the exact interview
invocation. Pair this with a repository that has only a registered standalone
OpenSpec store and no repository-local `openspec/config.yaml` or
`openspec/config.yml`: initialization stops with zero writes and never inspects
or selects the registered store.

### `FWD-002` — Refuse a brownfield repository

Use a fixture with a functioning endpoint and canonical spec, then one with
only archived OpenSpec history. `init` lists all evidence, creates no bundle,
and does not offer deletion or conversion. Pair these with a fixture containing
another product bundle under `docs/product/`; `init` rejects the second bundle
with no archive exception and writes nothing.

### `FWD-003` — Breadth-first interview with explicit unknowns

Exercise two ready-frontier shapes before continuing: with ten independent
ready questions, expect a cross-area selection of three through eight; with two
ready questions, expect both. Before the user answers, expect the complete
asked round with `Response status: pending-response`, every exact `PENDING
RESPONSE` marker, `condition: awaiting-interview-response`, and the matching
`awaiting_round`. The user then answers every selected independent question,
decides a first-release actor, says “I don’t know” about carrier retention,
defers accessibility assessment to a slice, and excludes paid billing. Expect
the same round to be `recorded` with the response verbatim, unique IDs, precise
unknown treatment, explicit exclusion, no dependent same-round follow-up, a
cross-area next frontier, an advanced `next_round`, and no remaining pending
marker. Pair the same-session response with a new-session explicit invocation
containing the complete answer; both must map only to the persisted awaiting
round. Assert that the frontier accounts for all twelve breadth categories and
preserves an explicitly deferred category as covered by valid evidence and
treatment rather than classifying its uncertainty as missing coverage.

### `FWD-004` — User requests synthesis early

Allow synthesis when several rows remain partial but every uncertainty is a
precise `UNK-*` or `OOS-*`. Preserve included and excluded treatments and do
not invent behavior. Assert that only `discovery/map.md` owns the synthesis
assessment and state has no duplicate flag. A paired fixture with one `FOG-*`
writes no baseline.

### `FWD-005` — Fresh synthesis ignores conversation-only facts

Put a material preference only in a conversation turn older than the explicit
synthesis invocation. The child route uses `fork_turns: "1"`; the baseline
excludes that preference and reports a gap if persisted evidence is
insufficient. The inherited latest turn is used only to parse the invocation.

### `FWD-006` — Structural review and validate-then-trust approval

A valid draft produces an `approval-ready` receipt with all checks passing and
no content-binding field, writes its path only to
`manifest.approval.review_receipt`, and changes the phase to
`baseline-reviewed`. Change a draft sentence after review, then invoke
`$product-baseline approve`. The skill does not compare candidate content; the
invocation is treated as user attestation and freezes the draft. Pair this with
an `issues` receipt: review writes its manifest-owned path, leaves the phase at
`baseline-draft`, and approval stops without changing the manifest. A discovery
change clears the path and returns any reviewed draft to `baseline-draft`.

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
rationale. Prefer a walking skeleton as the first candidate. When no coherent
walking skeleton exists, prefer the highest-risk coherent end-to-end path and
record the reason in its sequencing rationale. No candidate contains readiness
or execution fields.

### `FWD-009` — Roadmap always waits for confirmation

For both first creation and later revision, the first response contains the
complete proposed change. It changes no delivery artifact, writes the exact
one-target `.workflow/pending-delivery.yaml`, and sets
`awaiting-roadmap-confirmation`. Rejecting removes the preview and clears the
condition without changing the roadmap. Same-session confirmation writes
exactly the persisted target content, removes the preview, and clears the
condition. A confirmation in a new session does not authorize the earlier
preview; a fresh explicit roadmap invocation revalidates and replaces it.

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
invent a suffix. Accept three-digit boundary values `001` and `999`; reject
`000`, non-three-digit forms, and a next number of `1000`.

### `FWD-014` — Bounded slice inputs and exclusions

Assert the complete roadmap is read first and supplies the candidate
requirements. Assert full reads of baseline `charter.md`, `domain-map.md`, and
`glossary.md`, followed only by the candidate requirements' owning blocks.
Enumerate every canonical archived product-slice name, read only the five
highest-numbered slices in full, and read only frontmatter `name` plus the first
non-empty `## Outcome` line from older slices. Assert spec paths and capability
headings, archived-change basenames and artifact paths, and current-code paths
are indexed before only candidate-scope bodies are read. Any wider body read
must cite a named dependency from already loaded evidence. Assert no discovery,
pending OpenSpec change-content, default whole-baseline, whole-spec-store,
whole-archive, or whole-codebase body read. The preview cites planning context
from the allowed inputs.

### `FWD-015` — Slice confirmation and immediate roadmap coverage

Preview the canonical name, exact partial/complete coverage, boundaries,
planning context, complete proposal prompt, and complete roadmap change. Before
confirmation no delivery artifact changes; the exact two-target pending file
exists in active-slice-then-roadmap order and the condition is
`awaiting-slice-confirmation`. After same-session confirmation, the pending file
is absent, the condition is cleared, and:

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

1. pending preview → report its action and path, state that `status` cannot
   confirm it, and name the matching explicit action that regenerates it;
2. missing roadmap → `$product-delivery roadmap`;
3. active slice → finish its external OpenSpec workflow, then
   `$product-delivery archive`;
4. uncovered or partial requirement → `$product-delivery slice`;
5. full declared coverage → exactly `Delivery is complete.`.

Every case has zero writes. Multiple active slices produce a named error.

### `FWD-021` — Completion creates nothing else

Invoke both `slice` and `status` on full declared coverage. Both print exactly
`Delivery is complete.`; `slice` creates nothing. Assert the product remains
in phase `delivery` and no completion receipt, final phase, bundle destination,
or additional product artifact appears.

## Routing and fresh-context checks

For every routed product action, assert:

- an unmarked invocation dispatches exactly one product-action child, while an
  invocation with the matching `ROUTED_ACTION=<skill-name>` marker dispatches
  none and executes the installed skill directly;
- `fork_turns` is exactly `"1"`, exposing only the latest user turn;
- model, effort, and write posture exactly match the mode route table in
  `skill-contracts.md`;
- the packet names the action, mode, verbatim request, working-directory
  semantics, product root or unresolved state, and exact `SKILL.md`;
- it forbids every product-action reroute and every writer child;
- it treats only the explicit invocation, the response to the exactly persisted
  pending interview round, or the confirmation or rejection of the exactly
  persisted delivery preview as meaningful inherited context;
- it contains no reference to older or inaccessible parent context.

Reading or naming an agent `.toml` without the matching prompt marker does not
activate direct execution. No product action produces a second product-action
hop.

Discovery, baseline, archive, and status spawn no specialist. Optional roadmap
or slice specialists must first load
`.codex/skills/openspec-shared/references/subagents.md`, receive a complete
bounded packet, use `fork_turns: "none"`, `gpt-5.6-terra` with `high` effort,
remain read-only, return findings only, and never select scope, change state,
handle confirmation, write, route a product action, or spawn another agent.
The routed product-action child performs all selection, preview, confirmation,
state transition, and writing.

For discovery, baseline, and delivery status fixtures, assert
`gpt-5.6-luna`/`low` and an empty filesystem and version-control diff even when
the selected standalone declaration exposes `workspace-write`. Status does not
change timestamps, normalize invalid state, persist diagnostics, create a
control artifact or run output, or spawn any agent.

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
