# Validation, stopping, and recovery

## Deterministic support commands

The passive shared skill will own four deterministic helpers. They support the
user-facing skills but do not define new user modes and never repair data.

```text
python3 .codex/skills/openspec-product-shared/scripts/validate_bundle.py \
  --product <product-id> --phase <phase> --format json

python3 .codex/skills/openspec-product-shared/scripts/hash_baseline.py \
  <candidate|freeze|check> --product <product-id> --format json

python3 .codex/skills/openspec-product-shared/scripts/render_handoff.py \
  --product <product-id> --slice <SLICE-id> --format json

python3 .codex/skills/openspec-product-shared/scripts/inspect_openspec_delivery.py \
  --product <product-id> --slice <SLICE-id> --format json
```

These are installed-runtime paths; their source counterparts live under
`release/.codex/skills/openspec-product-shared/`. The helpers accept only a
product ID, slice ID, enumerated operation, and output format. They derive all
paths from the repository root; callers cannot pass an arbitrary product root
or archive path.

Exit codes are exact:

| Code | Meaning |
|---:|---|
| `0` | Requested check passed or deterministic render completed |
| `2` | Contract validation failed; structured diagnostics emitted |
| `3` | Required artifact or OpenSpec state is missing or ambiguous |
| `4` | Integrity/hash mismatch |
| `5` | Unsupported phase, schema version, or unsafe path |
| `10` | Unexpected internal failure; no mutation may be assumed |

Every helper emits one JSON object:

```json
{
  "schema_version": 1,
  "ok": false,
  "operation": "validate_bundle",
  "product": "<product-id>",
  "phase": "<phase-or-null>",
  "observed": {},
  "errors": [
    {
      "code": "BASELINE_HASH_MISMATCH",
      "path": "docs/product/<product-id>/baseline/charter.md",
      "expected": "<digest>",
      "actual": "<digest>",
      "message": "Frozen baseline file bytes changed."
    }
  ],
  "warnings": [],
  "suggested_next_step": "<one safe explicit invocation or manual instruction>"
}
```

Diagnostics are stable data; prose console output is rendered from them. A
helper never allocates an ID, changes lifecycle state, edits an OpenSpec
artifact, or reconstructs missing mutable state.

## Common validation rules

All mutating product modes validate these invariants before writing:

1. The current working directory resolves one local repository containing
   `openspec/config.yaml` or `openspec/config.yml`.
2. The product ID is lowercase kebab-case and the derived path remains below
   `docs/product/` after normalization.
3. At most one non-archived product bundle exists.
4. YAML parses with no duplicate keys and has exactly the supported schema
   version.
5. Required artifacts, keys, headings, enum values, and value types match the
   templates.
6. Persisted local paths are repository-relative, normalized, non-escaping,
   and point to the intended product/OpenSpec roots. No local absolute path,
   `..`, `~`, platform drive prefix, or `file:` URI is accepted.
7. IDs match their prefix, are unique, do not exceed their recorded high-water
   mark, and are not reused after a tombstone or historical reference.
8. Every artifact reference resolves and every referenced ID exists in its
   owning ledger.
9. Phase, condition, slice readiness, slice execution, and artifact existence
   agree.
10. No unrecognized active OpenSpec change exists for a transition that
    requires a clear change set.

Read-only `status` reports violations but never normalizes or fixes them.

## Phase-specific validation

### Discovery initialization

Initialization is allowed only for a genuinely greenfield product. It reads
repository structure and blocks on any of:

- durable application behavior rather than empty scaffolding or an explicitly
  disposable prototype;
- any canonical capability under `openspec/specs/`;
- any active change under `openspec/changes/`;
- any archived change under `openspec/changes/archive/`;
- another non-archived directory under `docs/product/`;
- an existing destination for the requested product ID.

Repository metadata, development tooling, empty scaffolding, a disposable
prototype explicitly marked as disposable, and the installed OpenSpec release
files do not by themselves make the product brownfield. Ambiguous evidence is
listed and requires user resolution; the skill does not delete or reinterpret
it.

### Discovery interview and synthesis

An interview response is persisted only when it maps to the currently awaiting
round or the explicit invocation contains the complete answer in a new
session. The skill validates that every outcome was recorded and that coverage
references exist before incrementing the round.

Synthesis stops if:

- any `FOG-*` remains;
- an unknown lacks an explicit baseline treatment;
- discovery artifacts contradict each other without a product decision;
- required discovery files or ID counters are inconsistent.

The user may synthesize with `UNK-*` entries of any risk. The synthesizer must
preserve their stated included/excluded treatment rather than silently answer
them.

### Baseline review and approval

Review verifies the exact artifact contracts, traceability, internal
coherence, and repository-relative paths. It writes `status: issues` and stops
when any check fails; it never edits the candidate.

Approval stops unless:

- the current phase is `baseline-reviewed`;
- the receipt status is `approval-ready`;
- every receipt file digest and aggregate digest matches the current draft;
- manifest status is `draft`;
- there is no active OpenSpec change;
- no release-blocking unknown appears in the draft;
- all referenced discovery IDs exist.

The invocation itself is approval. On success the final frozen files are
hashed. Any later mismatch is an unconditional hard stop; there is no repair,
accept-drift, refreeze, or baseline-v2 path.

### Roadmap and handoff

Roadmap creation and revision require valid frozen hashes. `next` additionally
requires:

- no active OpenSpec change;
- no selected, active, or archived-unreconciled slice;
- at least one `ready` slice;
- all dependencies of a ready slice are `delivered`;
- the expected change identity is unused by active and archived OpenSpec state;
- every scoped requirement/deviation exists;
- exactly one recommended slice, or explicit user choice among materially
  different ready candidates.

Handoff rendering validates the output before publishing it. It rejects a
missing prompt section, an absolute local path, scope outside the chosen slice,
an invalid baseline hash, a missing coverage intent, or a digest collision.

### Active and archived reconciliation

Active reconciliation requires the exact expected active name, required
proposal traceability block, unchanged handoff digest, and valid baseline.

Archived reconciliation requires exactly one matching terminal archive as
defined in `integration-and-handoffs.md`, no active change, explicit archived
traceability, existing canonical spec paths, and enough final archived text to
support all ledger effects. It trusts OpenSpec proposal/verification/archive
for behavioral correctness and performs no code/test check.

The corresponding archived change is detected even if mutable product state
incorrectly claims that the slice is merely selected or active. Its existence
forbids removal, reset, recreation, reopening, or reuse of that slice/change
identity.

### Closure

`close` checks every condition in `workflow-state.md`, including terminal
requirement/deviation dispositions and valid frozen hashes. An unresolved
unknown blocks only if the baseline included it as release-blocking; an
explicitly excluded/deferred unknown may remain in the final receipt.

Closure uses a recoverable two-stage transition:

1. validate and write the complete reconciliation receipt;
2. set phase `release-ready` and record the exact destination;
3. atomically rename the product bundle to
   `docs/product/archive/YYYY-MM-DD-<product-id>-first-release/`;
4. set phase `closed` at the destination;
5. print the manual post-release review/promotion hint.

The destination must not already exist. If the rename fails, the bundle remains
`release-ready` at its source and the same `close` invocation may retry. If the
rename succeeds but the final state write fails, a retry detects the exact
destination and matching receipt, then performs only the final state update.
It never merges with or overwrites an existing archive.

The final hint names the physical archived path, for example:

```text
Review `docs/product/archive/YYYY-MM-DD-<product-id>-first-release/delivery/post-release.md`.
If any item should become durable product documentation, promote it manually in
a separate explicit change; nothing was promoted automatically.
```

Closed-bundle validation treats pre-close product paths in the frozen manifest,
hashes, and delivery history as historical logical paths. It uses the recorded
source-to-destination mapping for lookup without changing those artifacts or
recomputing the aggregate with new path strings.

## Stopping rules

Every mode has one primary outcome and then stops:

| Mode | Stops after |
|---|---|
| `discovery init` | Empty discovery/control artifacts exist and the next interview invocation is printed |
| `discovery interview` | One complete round is recorded and the next questions or synthesis choice is printed |
| `baseline synthesize` | One complete draft is written, or gaps are reported |
| `baseline review` | One review receipt bound to the current candidate is written |
| `baseline approve` | The current reviewed draft is frozen and hashed |
| `delivery roadmap` | The mutable slice frontier is written |
| `delivery next` | One slice handoff is sealed and the proposal packet is printed |
| `delivery reconcile` | One live transition is recorded and exactly one next packet is printed, or a structural blocker is reported |
| `delivery close` | The complete bundle is archived and the review/promotion hint is printed |
| Any `status` | Evidence and one suggested next step are printed; no artifact changes |

No product action proceeds into a manually named OpenSpec action, selects the
next slice automatically after delivery, or performs more than one interview
round.

## Hard-stop report contract

A hard stop must identify all evidence needed to understand and correct the
problem:

```text
Stopped: <stable error code> — <short explanation>

Product: <product-id>
Phase: <phase>
Requested mode: <mode>
Observed files/state:
- <repo-relative path and relevant value>

Expected contract:
- <specific invariant>

No changes made by this invocation:
- <confirmed mutation boundary>

Safe recovery:
1. <manual or explicit-skill step>
2. <follow-up step>

Suggested next step: <exact explicit invocation, or `none until repaired`>
```

Reports include every conflicting active change, duplicate archive match,
missing ID, malformed ledger entry, and changed baseline file; they do not stop
after the first discoverable error when further read-only checks are safe.

## Expected failure and recovery behavior

| Failure | Required behavior | Recovery |
|---|---|---|
| Repository is not genuinely greenfield | Stop before creating a bundle; list durable code/spec/change/archive evidence | Use another workflow or manually prepare a genuinely new repository; rerun `init` only after evidence is resolved |
| External research is unavailable or approval-gated | Preserve the issue as `UNK-*`; never invent a fact | User supplies evidence, authorizes the needed research, or explicitly defers/excludes the unknown |
| User leaves an issue unknown | Classify and persist the precise uncertainty and treatment | Continue discovery, synthesize with explicit deferral, or resolve in a later slice/change |
| Review finds gaps | Write an `issues` receipt and retain the draft | Return to discovery, record new evidence/decisions, rerun synthesis, then review again |
| Approval candidate digest is stale | Stop without changing manifest or hashes | Rerun review on the current draft, then invoke approve again |
| Frozen baseline hash differs | Stop every mutating delivery action and report every changed/missing/unexpected baseline file | Restore the exact approved bytes from user-controlled history; there is no workflow repair or refreeze |
| Any unrelated active OpenSpec change exists | Stop selection, approval, reconciliation, or closure and list all names | User completes/removes it through an appropriate manual OpenSpec process, then retries |
| Proposal has wrong name or linkage before archive | Stop; do not attach or rename it | Follow the pre-archive cleanup protocol below and recreate with a new slice/change ID |
| Matching archive exists with valid structure | Treat its identity as terminal even if mutable state is stale | Reconcile structurally; never reopen or recreate it |
| Matching archive lacks linkage, canonical specs, or clear disposition evidence | Stop with archive/path/linkage evidence | Create a new corrective slice and change; the archived change remains untouched |
| An archived change is unexpectedly edited, moved, duplicated, or removed | Stop and report all observed candidates and ledger references | Restore the exact terminal archive from user-controlled history; otherwise the workflow cannot reconcile it |
| Mutable roadmap/state/ledger is malformed, missing, or mutually inconsistent | Stop; never infer or reconstruct the intended state | Use the pre-archive cleanup protocol if no archive exists; otherwise use a corrective slice after repairing only from authoritative user-controlled history |
| Active change disappears before archive | Stop and retire the selected identity | Use the pre-archive cleanup protocol and allocate a new slice/change ID |
| Closure has pending accepted obligations | Stop and list each nonterminal REQ/DEV and its incomplete coverage | Deliver corrective/new slices or archive explicit terminal disposition evidence, then reconcile |
| Archive destination already exists | Stop without merge or overwrite | User resolves the conflicting destination; retry `close` |
| Final bundle move partially completes | Inspect only source, exact destination, receipt, and phase | Retry the idempotent close transition as described above |

## Pre-archive cleanup protocol

This protocol applies only when no corresponding archive exists. Product skills
do not perform any deletion. They stop and tell the user to:

1. preserve the stop report and identify the affected `SLICE-*`, expected
   change name, handoff, roadmap entry, traceability entry, and active
   `openspec/changes/<change-id>/` path;
2. confirm again that no direct-child matching archive exists;
3. manually remove the affected active OpenSpec change, affected slice entries,
   and its sealed handoff rather than attempting to repair or reuse them;
4. append a tombstone to `delivery/decisions.md` recording the retired slice
   ID, retired change name, removed paths, reason, timestamp, and the highest
   allocated counters that must be preserved;
5. correct the underlying mutable-state problem without lowering any counter;
6. rerun `roadmap`, allocate the next unused `SLICE-*`, and run `next` to create
   a new handoff and new deterministic change name.

The exact tombstone block is:

```markdown
## <RFC3339 UTC> — Retired pre-archive slice <SLICE-*>

- Decision: Retire and remove the pre-archive slice/change; never reuse either identity.
- Slice: <SLICE-*>
- Change: <change-id>
- Removed paths: <repo-relative paths>
- Reason: <corruption, mismatch, or disappearance evidence>
- Corresponding archive checked: none found
- Counters retained: SLICE=<integer>, DEV=<integer>
- Replacement: <new SLICE-* or `not-yet-created`>
```

If an archive exists, this protocol is forbidden regardless of whether the
archive is valid. The only forward path is structural reconciliation or a new
corrective slice.

## Explicitly unhandled races

There is no filesystem lock, revision compare-and-swap, or multi-agent lease.
The user is responsible for running one Codex instance and for not manually
creating or archiving a change between a product action's preflight and write.
If such a race is observed, the current action stops and reports it; the design
does not add recovery semantics beyond the applicable rules above.

## Preservation rule

Implementation and all future tests must take before/after hashes of:

```text
release/.codex/skills/openspec-*/**
release/.codex/agents/openspec-*.toml
release/openspec/config.yaml
```

Any change to an existing path is a release-blocking failure. Only the four new
skill directories and three new product-agent files named in
`skill-contracts.md` may be added by a future implementation.
