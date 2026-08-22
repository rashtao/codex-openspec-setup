# OpenSpec integration and fresh-context handoffs

## Integration boundary

The product workflow coordinates existing OpenSpec actions without modifying or
calling them. Contact points are manual and explicit:

| Product state | User opens a fresh session and invokes | Result consumed by product workflow |
|---|---|---|
| Slice `selected` | `$openspec-propose` | One deterministic active change |
| Slice `change-active` | `$openspec-apply-change` | Implemented tasks and code |
| Apply complete | `$openspec-verify-change` | User-visible behavioral verification result |
| Verification accepted by user | `$openspec-archive-change` | Synced canonical specs and one terminal archive |
| Archive present | `$openspec-product-delivery reconcile` | Structural ledger update |

`$openspec-update-change` is manually available when the active plan needs
correction. `$openspec-explore` is optional for focused investigation. Product
skills never recommend or invoke bulk creation, bulk archival, fast-forward,
onboarding, registered-store, or separate sync workflows.

Existing files under `release/.codex/skills/openspec-*`, their agents, and
`release/openspec/config.yaml` are outside the mutation boundary. Their own
routing and `fork_turns` settings remain unchanged.

This is workflow-level coordination, not tamper-resistant enforcement. The
user remains responsible for invoking the named action in a clean session and
following the printed packet.

## Deterministic change identity

The selected slice owns exactly one expected change name:

```text
SLICE-003 — Customer completes initial onboarding
→ slice-003-customer-completes-initial-onboarding
```

Derivation is exact:

1. render the numeric ID as three decimal digits;
2. lowercase the title;
3. transliterate ASCII where deterministic, otherwise remove the character;
4. replace each run of non-alphanumeric characters with one hyphen;
5. trim hyphens;
6. truncate the slug to 48 characters at the last complete hyphen-separated
   token;
7. reject an empty or colliding name instead of inventing a suffix.

The sealed identity is never renamed or reused. A correction after archive is
a new slice with a new ID and change name.

## Sealed proposal handoff

`next` writes exactly one immutable handoff:

```text
docs/product/<product-id>/.workflow/handoffs/slice-003-propose.md
```

The exact template is:

````markdown
---
schema_version: 1
kind: openspec-product-slice-proposal-handoff
product: "<product-id>"
release: "first-usable-release"
slice: "SLICE-003"
expected_change: "slice-003-<slug>"
created_at: "<RFC3339 UTC>"
baseline_hashes: "docs/product/<product-id>/.workflow/baseline-hashes.yaml"
baseline_aggregate_sha256: "<64 lowercase hexadecimal characters>"
roadmap: "docs/product/<product-id>/delivery/roadmap.md"
traceability: "docs/product/<product-id>/delivery/traceability.yaml"
---

# Proposal handoff — SLICE-003

## Selected outcome

- Outcome: <independently demonstrable outcome>
- Demonstration: <end-to-end demonstration>
- Main risk: <risk reduced>
- Dependencies satisfied: <SLICE-* IDs or `none`>

## Baseline requirements in scope

### REQ-0001 — <title>

- Coverage intent: <partial|complete>
- Source: docs/product/<product-id>/baseline/<file>.md#<anchor>
- Statement: <verbatim baseline statement>
- Release rationale: <verbatim baseline rationale>
- Acceptance signal: <verbatim baseline signal>
- Assumptions: <ASM-* IDs or `None`>

## Accepted deviations in scope

### DEV-0001 — <title>

- Source: docs/product/<product-id>/delivery/deviations.md#<anchor>
- Statement: <verbatim accepted deviation statement>
- Acceptance evidence: <repo-relative archived change path>

Use `None` when no accepted deviation is in scope.

## Explicit exclusions

- <behavior that is adjacent but outside this slice>

## Copy-paste prompt for a fresh Codex session

```text
$openspec-propose

Create exactly one planning-only OpenSpec change for the selected greenfield
product delivery slice described below. This is a fresh session: do not rely on
any prior conversation.

Repository root: the current working directory
Product bundle: docs/product/<product-id>
Slice: SLICE-003
Required change name: slice-003-<slug>
Sealed handoff: docs/product/<product-id>/.workflow/handoffs/slice-003-propose.md
Frozen baseline hashes: docs/product/<product-id>/.workflow/baseline-hashes.yaml

Before creating anything:
1. Confirm that no active OpenSpec change exists.
2. Validate the frozen baseline hashes.
3. Read the complete sealed handoff.
4. Read the current code and canonical `openspec/specs/` needed to refine only
   this slice.
5. Read only the baseline requirement paths and accepted deviation paths named
   in the sealed handoff. Do not broaden discovery or read unrelated baseline
   material.

Create exactly `slice-003-<slug>` using the installed OpenSpec schema. Produce
every artifact required for apply, including detailed behavioral requirements,
scenarios, design, and tasks. Keep the outcome vertical and independently
demonstrable. Slice-level refinements belong in this change. Newly discovered
release behavior may also be proposed here, but it must be explicit so later
product reconciliation can record it as a deviation.

Compute the lowercase SHA-256 of the exact sealed handoff file. The proposal
must preserve the schema's existing headings and append this traceability block
under `## Impact`, replacing the digest placeholder with that computed value:

### Product delivery traceability

- Product bundle: `docs/product/<product-id>`
- Delivery slice: `SLICE-003`
- Baseline requirements: `REQ-0001`, <other IDs or `none`>
- Accepted deviations: <DEV-* IDs or `none`>
- Sealed handoff: `docs/product/<product-id>/.workflow/handoffs/slice-003-propose.md`
- Handoff SHA-256: `<computed 64-character lowercase SHA-256>`

Do not implement application code, apply tasks, verify behavior, sync canonical
specs, archive the change, select another slice, or edit any file under
`docs/product/<product-id>/baseline/`. If the required change name cannot be
used, another active change exists, the baseline hash fails, or the requested
scope cannot form one coherent change, stop and report the evidence.

After the proposal is complete, print this suggested next step exactly:
`$openspec-product-delivery reconcile`
```
````

The handoff's own digest is deliberately absent from its frontmatter and prompt
values because a file cannot contain its own ordinary SHA-256. After writing
the complete immutable file, `next` computes its SHA-256 and records it in
`.workflow/state.yaml` and `delivery/traceability.yaml`. The fresh proposal
session independently computes the same file digest and writes the concrete
value to `proposal.md`; reconciliation compares it with state and traceability.
The stored prompt is therefore complete and directly copy-pasteable without a
self-referential substitution.

## Active-change reconciliation

After proposal, `$openspec-product-delivery reconcile` uses the local OpenSpec
CLI and filesystem to establish all of the following:

- exactly one active change exists;
- its name equals the sealed expected change;
- its `proposal.md` includes the exact product, slice, baseline requirement,
  accepted deviation, handoff path, and handoff digest references;
- the handoff digest still matches the stored immutable file;
- the baseline hashes still pass.

On success it changes the slice from `selected` to `change-active` and prints
the apply packet. It does not judge proposal quality; that belongs to the
manually invoked OpenSpec proposal workflow and its schema validation.

If the active name or traceability is wrong, reconciliation stops. Before any
archive exists, the user must manually remove the incorrect slice bookkeeping
and active change, record the removal in `delivery/decisions.md`, and run
`roadmap`/`next` again with a newly allocated slice ID and change name. Product
skills print these instructions but never delete either artifact.

## Exact fresh-session console packets

These packets are generated from live state and printed, not persisted as
receipts. Each is self-contained and uses only repository-relative paths.

### Apply

```text
$openspec-apply-change slice-003-<slug>

Implement only the active OpenSpec change `slice-003-<slug>` in the current
repository. This is a fresh session: do not rely on prior conversation.

Product bundle: docs/product/<product-id>
Delivery slice: SLICE-003
Active change: openspec/changes/slice-003-<slug>
Sealed handoff: docs/product/<product-id>/.workflow/handoffs/slice-003-propose.md

Follow the installed OpenSpec apply workflow and the live change artifacts.
Do not edit the frozen product baseline, select another slice, sync canonical
specs, or archive the change. If implementation exposes a planning conflict,
stop so the user can invoke `$openspec-update-change slice-003-<slug>` in a
fresh session.

When apply reports complete, the suggested next fresh-session step is:
`$openspec-verify-change slice-003-<slug>`
```

### Update, when apply reports a planning contradiction

```text
$openspec-update-change slice-003-<slug>

Update only the existing planning artifacts for `slice-003-<slug>` to address
the following reported contradiction:
<verbatim contradiction and evidence>

This is a fresh session. Preserve the product traceability block, the expected
change identity, and the slice outcome recorded in
`docs/product/<product-id>/.workflow/handoffs/slice-003-propose.md`. Do not edit
the frozen baseline or implementation. If resolving the contradiction changes
first-release behavior, make that behavior explicit in the proposal/spec so
product reconciliation can record it after archive.
```

### Verify

```text
$openspec-verify-change slice-003-<slug>

Verify the implementation of `slice-003-<slug>` against its live OpenSpec
planning artifacts using fresh evidence. This is a fresh session: do not rely
on prior conversation.

Product bundle: docs/product/<product-id>
Delivery slice: SLICE-003
Active change: openspec/changes/slice-003-<slug>

Follow the installed read-only OpenSpec verification workflow. Do not repair
code or planning artifacts, edit the frozen baseline, archive the change, or
write a product-level verification receipt. Report findings to the user. The
user decides whether to update/apply again or proceed to archive.
```

### Archive

```text
$openspec-archive-change slice-003-<slug>

Archive exactly `slice-003-<slug>` after the user has accepted its separate
verification result. This is a fresh session: do not rely on prior
conversation.

Product bundle: docs/product/<product-id>
Delivery slice: SLICE-003
Active change: openspec/changes/slice-003-<slug>

Follow the installed OpenSpec archive workflow. Choose and complete canonical
spec synchronization; do not archive without syncing applicable delta specs.
Do not override incomplete artifacts/tasks or a failed sync. Do not edit the
frozen product baseline or product delivery ledger.

After archive succeeds, print this suggested next fresh-session step:
`$openspec-product-delivery reconcile`
```

### Product reconciliation

```text
$openspec-product-delivery reconcile

Reconcile the currently selected slice for the product bundle at
`docs/product/<product-id>`. This is a fresh session: derive all facts from the
persisted product state and live local OpenSpec filesystem. Do not rely on any
prior conversation.
```

`status` prints the currently applicable packet. It never executes the named
OpenSpec action.

## Archive identity and structural reconciliation

For expected change `<change-id>`, a corresponding archive is exactly one
direct child of `openspec/changes/archive/` whose basename matches:

```regex
^[0-9]{4}-[0-9]{2}-[0-9]{2}-<change-id>$
```

The date prefix must be a valid calendar date. Recursive descendants, suffixed
copies, similarly named changes, and archived registered stores do not match.
Zero or multiple matches are errors.

An archive match is terminal. The reconciler never restores, reopens, moves,
renames, edits, or recreates it. It checks only structure and traceability:

1. the frozen baseline hash set is valid;
2. no active OpenSpec change exists;
3. the archive name matches the sealed expected identity;
4. archived `proposal.md` contains the sealed handoff path/digest, slice ID,
   relevant `REQ-*` IDs, and any prior `DEV-*` IDs;
5. final archived proposal/spec artifacts make every behavior beyond the sealed
   handoff explicit;
6. referenced canonical paths under `openspec/specs/` exist;
7. each ledger terminal disposition has support in the archived change.

It does not inspect code, execute tests, infer verification success, or create
a product verification receipt. The user-authorized OpenSpec archive is
treated as evidence that the separate OpenSpec proposal and verification were
accepted.

## Emergent behavior and terminal dispositions

The sealed handoff is never rewritten to match the archive. During structural
reconciliation the product skill compares it with the final archived planning
artifacts:

- slice-level elaboration that does not change first-release behavior remains
  ordinary OpenSpec refinement;
- new first-release behavior becomes `DEV-*` type `emergent-requirement`;
- replacement of a baseline obligation becomes `DEV-*` type `supersession`;
- an intentionally omitted baseline obligation becomes `DEV-*` type
  `unimplemented-with-reason`.

The archived change is sufficient user approval evidence for these records, so
the reconciler does not ask again. It allocates IDs, writes
`delivery/deviations.md`, updates the original slice and traceability ledger,
and marks structurally supported coverage. Requirements become implemented
only through an explicit `complete` coverage record.

If final behavior cannot be classified from explicit archived text, the archive
is terminal but reconciliation blocks. Recovery is a new corrective slice and
new OpenSpec change; the old archive and original handoff remain unchanged.

## One-change gate

At ordinary product preflight, any active OpenSpec change blocks:

- initialization when it proves prior delivery history;
- baseline approval;
- roadmap selection;
- sealing another handoff;
- final release closure.

During reconciliation, the one matching expected active change is allowed only
to advance `selected` to `change-active` or report the next manual action. Any
other active change blocks with all discovered names and paths. The workflow
does not attempt to coordinate parallel Codex instances or recover an active
change created after preflight; the user is responsible for avoiding that race.
