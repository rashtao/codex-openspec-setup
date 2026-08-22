# Validation test plan for the future skills

## Test philosophy

The implementation is accepted only with clean-room, repository-level forward
tests. Tests exercise the public skill invocations and inspect persisted
artifacts; they do not pass merely because a final response contains expected
words.

Every scenario records:

- immutable case ID and prompt;
- fixture tree and SHA-256 digest manifest;
- model, reasoning effort, Codex/host version, and available-skill inventory;
- transcript and material output artifacts;
- before/after hashes for protected existing release files;
- deterministic assertions and any semantic reviewer rubric;
- `pass`, `fail`, or `invalid`, with infrastructure errors preserved.

Unless a case explicitly tests continuation of an awaiting interview response,
each invocation begins in a clean session. Product-agent routing evidence must
show `gpt-5.6-sol`, exactly one dispatch, and `fork_turns: "none"`. Manually
invoked existing OpenSpec skills begin in their own fresh host sessions and are
allowed to use their unchanged internal routing.

## Proposed test assets

A future implementation adds test data without changing existing OpenSpec
skills:

```text
release/.codex/skills/openspec-product-shared/evals/
  description-cases.json
  forward-cases.json
  fixtures/
    empty-greenfield/
    brownfield-code/
    active-change/
    frozen-drift/
    archived-happy-path/
    archived-emergent-scope/
    corrupt-ledger/
  structured/
    suite.json
    run-index.json
```

Generated transcripts, run manifests, grading manifests, and benchmark output
belong in an ignored run directory, never in a frozen fixture.

## Description-boundary tests

Frontmatter selection is explicit-only. Therefore prompts submitted without a
`$skill-name` token are all `near_miss`, even when the topic resembles the
workflow. This suite tests false-positive resistance, not trigger recall.
Explicit resolution and valid-mode behavior are tested separately by forward
cases.

Representative immutable cases are:

| Case | Prompt without an explicit skill token | Expected |
|---|---|---|
| `DESC-DISC-001` | “Help me brainstorm users and requirements for a new app.” | Do not select discovery |
| `DESC-DISC-002` | “Interview me breadth-first about this greenfield product.” | Do not select discovery |
| `DESC-DISC-003` | “Explore whether this idea is worth building.” | Prefer ordinary conversation or `openspec-explore`, not product discovery |
| `DESC-BASE-001` | “Turn these notes into a comprehensive product requirements document.” | Do not select baseline |
| `DESC-BASE-002` | “Review this requirements baseline for contradictions.” | Do not select baseline without the explicit invocation |
| `DESC-BASE-003` | “Freeze these docs so nobody changes them.” | Do not select baseline |
| `DESC-DEL-001` | “Break this feature into vertical slices.” | Do not select delivery |
| `DESC-DEL-002` | “Propose and implement the next OpenSpec change.” | Select the applicable existing OpenSpec action, not product delivery |
| `DESC-DEL-003` | “Reconcile canonical specs with what shipped.” | Do not select delivery without the explicit invocation |
| `DESC-SHARED-001` | “Use openspec-product-shared to validate my product.” | Passive package refuses a user-facing action and points to a public skill |

Additional held-out cases use casual, abbreviated, and artifact-focused wording
without copying development phrases. Labels and rationales are frozen before
execution. Each case runs manually in a clean session using only the
frontmatter description as the selection contract.

Activation is `selected`, `not_selected`, or `unknown` only when supported by a
documented host signal. Without such a signal it remains `unknown`; output
behavior is graded separately. No activation accuracy/precision claim is made
from inferred behavior.

Explicit invocation tests include every valid mode, a missing mode, an unknown
mode, a misspelled product skill, and an explicit passive-shared invocation.
A valid explicit public invocation must reach its skill; invalid modes must
stop with usage and perform no fallback action.

## Deterministic schema and helper tests

For each artifact template, test:

- minimal valid instance;
- fully populated valid instance;
- missing required key/heading;
- duplicate YAML key;
- unsupported `schema_version`;
- invalid enum and incorrectly typed value;
- duplicate, malformed, reused, or counter-exceeding ID;
- dangling ID and path references;
- POSIX absolute path, Windows drive path, `file:` URI, `~`, `..`, and symlink
  escape;
- CRLF/LF and exact-byte hash behavior;
- unsorted manifest/hash records;
- extra, missing, or changed frozen-baseline file;
- zero, one, and multiple matching archives;
- invalid calendar-date archive prefix;
- nested and suffixed archive near misses;
- `partial` coverage that never silently becomes `complete`.

Each helper is tested for exit code, JSON schema, stable diagnostic code,
complete error enumeration, and zero writes on failure. Repeat identical runs
against identical bytes and assert byte-identical deterministic outputs after
normalizing only documented timestamps.

## Forward workflow scenarios

### `FWD-001` — Initialize a genuinely empty product

Setup: OpenSpec is installed, application directories are empty scaffolding,
canonical specs and change history are empty, and `docs/product/` has no active
bundle.

Invocation:

```text
$openspec-product-discovery init parcel-tracker
```

Expected:

- one `gpt-5.6-sol` routed agent with `fork_turns: "none"`;
- exact state and four discovery files are created;
- no baseline, delivery, OpenSpec change, or application file is created;
- phase is `discovery` and counters are zero;
- console prints the exact interview invocation.

### `FWD-002` — Refuse a brownfield repository

Setup: a functioning order endpoint and one canonical spec already exist.

Expected: `init` reports both evidence paths, makes no product bundle, does not
offer to convert/delete them, and explains that the workflow is greenfield
only. Repeat with an archived OpenSpec change but no code and expect the same
block.

### `FWD-003` — Breadth-first interview with explicit unknowns

Setup: initialized parcel-tracker bundle. The user answers eight independent
questions, decides the first-release actor, says “I don’t know” about carrier
retention, defers accessibility testing to a slice, and excludes paid billing.

Expected:

- one round is appended verbatim;
- `PDEC-*`, `UNK-*`, `ASM-*` if accepted, and `OOS-*` receive unique IDs;
- retention has a precise unknown treatment;
- paid billing is excluded rather than weakly prioritized;
- no dependent follow-up appears in the same round;
- the next frontier spans multiple coverage areas.

### `FWD-004` — User requests synthesis early

Setup: several coverage rows remain partial, all uncertainties are precise
`UNK-*` or `OOS-*`, and no `FOG-*` exists.

Invocation:

```text
$openspec-product-baseline synthesize
```

Expected: synthesis is allowed, excluded unknowns remain excluded, included
assumptions remain visible, uncovered behavior is not invented, and the draft
reports its limitations. A paired fixture with one `FOG-*` must block without
writing a baseline.

### `FWD-005` — Fresh synthesis cannot use conversation-only facts

Setup: the acting parent conversation contains a material product preference
that is absent from discovery artifacts.

Expected: the routed packet has `fork_turns: "none"`; the synthesized baseline
does not contain that preference; it either reflects persisted evidence or
reports a gap. Transcript inspection confirms the child was not instructed to
recover parent context.

### `FWD-006` — Review and stale-digest approval

Setup: a valid draft first produces an approval-ready receipt. Then one draft
sentence changes before approval.

Expected: `approve` detects the candidate digest mismatch, leaves manifest
`draft`, writes no frozen hashes, and prints `review` as the next step. After a
new passing review, explicit approval freezes and hashes all baseline files,
including the final manifest.

### `FWD-007` — Frozen baseline drift blocks delivery

Setup: approved baseline, then change one byte in `charter.md` and remove a
domain file.

Expected: `roadmap`, `next`, `reconcile`, and `close` each stop; the report lists
both changed and missing files with expected/actual evidence; no delivery or
OpenSpec artifact changes; no repair/refreeze option is offered.

### `FWD-008` — Any active change blocks slice selection

Setup: valid frozen baseline and an unrelated `openspec/changes/fix-logging/`.

Expected: `next` lists the active change and does not select a slice, seal a
handoff, or suggest that product delivery may coexist with it.

### `FWD-009` — Ambiguous ready frontier waits for the user

Setup: two materially different ready slices with satisfied dependencies.

Expected: `next` presents both, recommends one with rationale, waits for an
explicit choice, and allocates/seals nothing before that choice. A fixture with
one unambiguous ready slice selects it directly.

### `FWD-010` — Sealed proposal handoff is fresh-context complete

Setup: selected slice covers two requirements, one partially and one
completely, plus one accepted deviation.

Expected:

- deterministic change ID and immutable handoff are produced;
- state and traceability store the handoff SHA-256;
- the handoff includes verbatim scoped statements and the full proposal prompt;
- every persisted local path is repository-relative;
- prompt orders the new session to read current code/canonical specs but only
  named baseline/deviation material;
- proposal traceability block includes the console-rendered actual handoff
  digest;
- no active OpenSpec change is created;
- the console suggests manual `$openspec-propose`.

### `FWD-011` — Happy manual OpenSpec loop and reconciliation

Setup: run the printed proposal in a clean session, then product reconcile,
then printed apply, verify, and synchronized archive packets in separate clean
sessions. The archive is a direct child named with the expected date/change and
the canonical spec exists.

Expected:

- active reconcile transitions `selected → change-active`;
- product workflow creates no verification receipt and reruns no tests;
- final reconcile transitions `change-active/archived → delivered`;
- coverage and canonical paths are recorded;
- the archive remains byte-identical;
- the next slice is not selected automatically.

### `FWD-012` — Emergent release behavior becomes a deviation

Setup: final archived proposal/spec explicitly includes a notification retry
requirement absent from the sealed handoff.

Expected: reconcile allocates `DEV-*` type `emergent-requirement`, cites the
archive as approval evidence, updates the original slice/ledger, leaves the
sealed handoff and frozen baseline unchanged, and does not ask for a second
approval.

### `FWD-013` — Archived supersession or omission is terminal evidence

Setup: an archived change explicitly replaces one baseline requirement and
records why another is intentionally unimplemented.

Expected: reconcile creates the corresponding `supersession` and
`unimplemented-with-reason` deviation records, links replacement/evidence, and
assigns terminal dispositions. Without explicit archived rationale the same
fixture blocks rather than inferring intent.

### `FWD-014` — Invalid archive can never be reopened

Setup: matching archive exists but its proposal lacks the handoff digest and a
referenced canonical spec path does not exist.

Expected: reconcile reports every mismatch, does not edit/move/delete the
archive, does not restore it to active changes, and instructs creation of a new
corrective slice/change. The original IDs remain terminal and retired.

### `FWD-015` — Corrupt mutable ledger before archive

Setup: selected slice has a malformed traceability entry and its expected
active change exists; no corresponding archive exists.

Expected: product actions make no repair or deletion, report all affected IDs
and paths, and print the full manual pre-archive cleanup/tombstone/recreation
protocol. After user-simulated cleanup, the next slice ID is greater than the
retired one.

### `FWD-016` — Close with an explicitly excluded unknown

Setup: hashes pass, no active changes exist, all accepted `REQ-*` and `DEV-*`
entries are terminal, slices are delivered, and one unknown remains
`excluded-deferred-to-future-change`.

Expected: `close` succeeds, receipt lists the unknown, bundle moves to the exact
dated archive path, final state is `closed`, and the console tells the user to
review and explicitly promote useful content from `delivery/post-release.md`.
Nothing is promoted automatically.

### `FWD-017` — Matching archive overrides stale mutable execution label

Setup: slice state says `change-active`, the active directory is absent, and
exactly one structurally valid corresponding archive exists.

Expected: reconcile detects the archive by naming convention, treats the
identity as terminal, performs structural reconciliation, and never suggests
recreating or removing it.

### `FWD-018` — Wrong active change before archive requires retirement

Setup: sealed handoff expects `slice-004-export-audit-log`, but the only active
change is `slice-004-export-logs`; neither is archived.

Expected: reconcile does not attach, rename, or edit the wrong change. It emits
the detailed pre-archive cleanup instructions, requiring a tombstone and a new
slice ID/change identity.

## Fresh-context packet checks

For every routed product action, capture the child creation call and assert:

- `fork_turns` is the exact string `"none"`;
- model is exactly `gpt-5.6-sol`;
- effort matches `skill-contracts.md`;
- the message names the action, mode, verbatim current request, current working
  directory semantics, and product root or states it is unresolved;
- it tells the child which `SKILL.md` to read;
- it forbids rerouting and further children;
- it does not refer to “above,” “the earlier discussion,” or inaccessible
  parent facts.

For every printed manual OpenSpec packet, start a new session with only that
text and the fixture repository. The action must be resolvable without the
original product-workflow transcript. Assert that all local paths in the packet
and resulting product/OpenSpec linkage are repository-relative.

## Existing OpenSpec preservation checks

Before each mutating forward test, hash every pre-existing path under:

```text
release/.codex/skills/openspec-*/**
release/.codex/agents/openspec-*.toml
release/openspec/config.yaml
```

After the test, compare path inventory, file mode, symlink target, and bytes.
Any addition inside, removal from, or change to a pre-existing OpenSpec skill
directory is a failure. New product skill/agent paths are evaluated separately.

Also assert that product skills never directly dispatch an existing OpenSpec
action and never modify `openspec/changes/`, `openspec/specs/`, application
code, or frozen baseline files.

## Structured candidate-versus-baseline evaluation

Because cross-session state, immutable evidence, and archive reconciliation are
fragile, the implemented skill set receives a small structured development
evaluation in addition to forward tests.

Use the version `1.0` `suite.json`, `run-index.json`, `run.json`,
`grading.json`, and `benchmark.json` contracts from `codex-skill-creator`.
Freeze the suite before its first run. Changing a prompt, fixture, criterion,
configuration, or digest creates a new suite ID.

The initial suite contains three materially different cases:

1. `EVAL-001-discovery-unknowns` — classify a mixed interview response without
   inventing decisions or erasing explicit deferrals;
2. `EVAL-002-frozen-drift` — refuse delivery and enumerate all integrity
   evidence without writes;
3. `EVAL-003-archive-emergence` — structurally reconcile a valid archive,
   allocate an emergent `DEV-*`, and preserve baseline/handoff/archive bytes.

Each case precommits deterministic criteria for file/schema/state/hash outcomes
and model-judge criteria for whether reports are sufficiently actionable and
do not claim behavioral verification. Artifact presence alone is not a
sufficient criterion.

Compare exactly one normalized candidate configuration with a `no_skill`
baseline. Candidate and baseline receive identical substantive prompts and
fixture bytes; the sole intervention is the candidate's explicit skill
invocation/availability, which is omitted or disabled for the baseline and
recorded in provenance. Each matched pair uses:

- independent clean contexts;
- the same `gpt-5.6-sol` model and exposed settings within that case;
- the same authorized tools and workspace setup;
- no access to the other arm's outputs or grades;
- at least two repetitions during development, with every attempt indexed.

Executor errors and invalid runs remain in manifests and denominators. Missing
token/duration telemetry is `null`, never estimated. Graders cite transcript or
artifact evidence for each verdict. Aggregate deltas are candidate minus
baseline only for matched pairs.

Use development results to revise instructions, then freeze the candidate
digest before opening held-out cases. A held-out case that influences a change
becomes development history and is replaced. With only three cases, conclusions
are explicitly limited to development evidence; they do not claim production
trigger rates, reliability, causality, or statistical significance.

## Acceptance gate

Implementation is ready for user review only when:

- all deterministic template/helper tests pass;
- all forward scenarios pass in clean fixtures;
- no existing OpenSpec file changes;
- every routed product packet proves `fork_turns: "none"` and
  `gpt-5.6-sol`;
- no product-level behavioral verification or verification receipt appears;
- description evidence is reported without inferred activation claims;
- structured evaluation has no unexplained candidate regression on a critical
  criterion and all invalid/error runs remain visible;
- the generated console output always ends in one safe suggested next step or a
  detailed stop report.
