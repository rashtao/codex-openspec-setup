# Discovery and baseline validation

This contract covers only discovery and baseline. Delivery behavior is defined
normatively in `workflow-state.md`, `artifact-templates.md`, and
`integration-and-handoffs.md`; it has no separate validation, repair, or
corrective subsystem.

## Validation mechanism

The public skills read the normative templates and inspect artifacts directly.
`product-shared` provides references, including normative artifact templates,
only. It contains no executable helpers, assets, or user-facing documentation
file.

All mutating discovery and baseline modes check these invariants before writing:

1. The working directory is one local repository containing
   `openspec/config.yaml` or `openspec/config.yml`.
2. The product ID is lowercase kebab-case and the derived bundle is below
   `docs/product/`.
3. At most one product bundle exists.
4. YAML parses without duplicate keys and uses the schema version defined by
   `artifact-templates.md`.
5. Required artifacts, keys, headings, enum values, and value types match the
   normative templates.
6. Persisted local paths are repository-relative, use `/` separators, remain
   under the intended product or OpenSpec root, and contain no absolute path,
   parent traversal, home shorthand, drive prefix, or `file:` URI.
7. Discovery IDs match their prefixes, are unique, do not exceed the
   corresponding `.workflow/state.yaml` high-water mark, and are not reused.
   Requirement IDs are unique, match `REQ-*`, do not exceed
   `baseline/manifest.yaml` → `highest_requirement_id`, and are not reused.
8. Every artifact and ID reference resolves to its owning artifact.
9. Phase, condition, `discovery.awaiting_round`, pending interview marker,
   manifest-owned review-receipt path and receipt status,
   `.workflow/pending-delivery.yaml` action and targets, and artifact existence
   agree. `baseline-draft` has either a null receipt path or a named `issues`
   receipt, never a named `approval-ready` receipt. `baseline-reviewed` has a
   named `approval-ready` receipt.

Read-only status reports violations and never normalizes or fixes them. Every
discovery or baseline `status` invocation performs zero writes regardless of
the selected agent's sandbox; it does not update timestamps, persist
diagnostics, create artifacts or run outputs, or spawn a specialist.

## Discovery initialization

Initialization is allowed only for a genuinely greenfield product. It reads
repository structure and stops on any of:

- durable application behavior rather than empty scaffolding or an explicitly
  disposable prototype;
- any canonical capability under `openspec/specs/`;
- any active change under `openspec/changes/`;
- any archived change under `openspec/changes/archive/`;
- another product bundle under `docs/product/`;
- an existing destination for the requested product ID.

Repository metadata, development tooling, empty scaffolding, an explicitly
disposable prototype, and installed OpenSpec release files do not by themselves
make the product brownfield. Ambiguous evidence is listed for the user;
`init` does not delete or reinterpret it.

## Discovery interview

Before returning questions, the skill appends the complete asked round with
`Response status` set to `pending-response`, writes every exact `PENDING
RESPONSE` marker, sets `condition` to `awaiting-interview-response`, and sets
`discovery.awaiting_round` to that round number.

An interview response is persisted only when it maps to that currently awaiting
round or when an explicit invocation in a new session contains the complete
answer for it. A response without a product-skill token is accepted only as the
immediately following same-session response. Before advancing the round, the
skill confirms:

- the state names exactly one round carrying every pending marker;
- the complete user response is recorded verbatim;
- every extracted fact, decision, assumption, unknown, fog item, exclusion, and
  source has a valid unique ID;
- every recorded outcome appears in the round's outcome list;
- coverage and frontier references exist;
- dependent questions were not pulled into the current breadth-first round.

The same write changes the response status to `recorded`, replaces all pending
markers, clears `discovery.awaiting_round`, advances `discovery.next_round`,
and sets the next valid condition. Completed rounds are immutable.

Product recovery remains one of the required domain coverage areas. It is
ordinary product subject matter, not a product-workflow repair mechanism.

The twelve coverage rows owned by `artifact-templates.md` are required breadth
categories because together they make the release boundary explicit, cover
actor journeys and functional capabilities, establish coherent domain
responsibilities, expose cross-cutting qualities and external dependencies,
and require a precise treatment for every remaining uncertainty. Coverage does
not require certainty; an area may remain explicitly deferred with valid
evidence and treatment.

## Synthesis

Synthesis stops if:

- any `FOG-*` remains;
- an unknown lacks an explicit baseline treatment;
- discovery artifacts contradict each other without a user product decision;
- a required discovery file or ID counter is inconsistent.

The user may synthesize with `UNK-*` entries of any risk. The synthesizer
preserves each included or excluded treatment and never silently answers it.
It reads only discovery and state, writes the full draft baseline, and reports
gaps rather than inventing product behavior.

## Baseline review

Review reads all discovery and draft baseline artifacts and checks:

- template and schema compliance;
- unique requirement identity and one owning location per requirement;
- source traceability from every requirement to discovery evidence;
- canonical terminology;
- contradiction and duplicate handling;
- coherent actor journeys and domain responsibilities;
- explicit treatment of every retained unknown;
- repository-relative persisted paths;
- `None` under release-blocking unknowns.

Review never repairs requirement or narrative content. It writes `status:
issues` if any check fails, changes only `manifest.approval.review_receipt` to
the receipt path, and leaves the phase at `baseline-draft`. A passing review
writes `status: approval-ready`, changes only that same manifest field, and
changes the phase to `baseline-reviewed`. The receipt identifies the product,
manifest, time, check results, issues, and warnings but carries no
content-binding value.

Any later discovery change resets `manifest.approval.review_receipt` to `null`
and changes the phase to `baseline-draft`. A new synthesis also initializes the
field to `null`. An unreferenced receipt may remain as non-authoritative
history.

## Baseline approval

Approval stops unless:

- the phase is `baseline-reviewed`;
- the current receipt says `approval-ready`;
- the manifest says `draft`;
- no active OpenSpec change exists;
- the draft contains no release-blocking unknown;
- every referenced discovery ID exists.

The explicit invocation attests both approval and that the reviewed candidate
was not changed after review. The skill trusts that attestation and does not
compare file content with the receipt.

On success, approval:

1. changes the manifest to `status: frozen`;
2. records the approval method, time, and receipt path;
3. changes the primary phase to `baseline-frozen`;
4. prints `$product-delivery roadmap`.

No action after approval checks frozen file content. The user owns preservation
of frozen baseline artifacts.

## Discovery and baseline stopping rules

| Mode | Stops after |
|---|---|
| `product-discovery init` | Discovery/control artifacts exist and `$product-discovery interview` is printed |
| `product-discovery interview` | One round is recorded and the next questions or synthesis choice is printed |
| `product-discovery status` | Evidence and one next invocation are printed; no writes occur |
| `product-baseline synthesize` | One complete draft is written, or gaps are reported |
| `product-baseline review` | One structural review receipt is written |
| `product-baseline approve` | The approval-ready draft is frozen |
| `product-baseline status` | Evidence and one next invocation are printed; no writes occur |

No discovery or baseline action proceeds into a delivery or external OpenSpec
action, performs more than one interview round, or edits application code.

## Stop report

A discovery or baseline stop includes:

```text
Stopped: <stable error code> — <short explanation>

Product: <product-id or unresolved>
Phase: <phase or absent>
Requested action: <skill and mode>
Observed evidence:
- <repository-relative path and relevant value>

Expected contract:
- <specific invariant>

No changes made by this invocation.
Suggested next step: <one exact explicit invocation or manual user action>
```

When further read-only inspection is safe, the report enumerates all relevant
conflicts instead of stopping after the first.

## Expected discovery and baseline failures

| Failure | Required behavior | User-owned next step |
|---|---|---|
| Repository is not genuinely greenfield | Stop before creating a bundle and list durable code/spec/change/archive evidence | Use a different workflow or prepare a genuinely new repository |
| External research is unavailable or approval-gated | Persist a precise `UNK-*`; never invent a fact | Supply evidence, authorize research, defer, or exclude |
| User leaves an issue unknown | Persist the precise uncertainty and its treatment | Continue discovery, synthesize with explicit treatment, or resolve later |
| Review finds gaps | Write an `issues` receipt, name it from the manifest, preserve the draft, and leave the phase at `baseline-draft` | Add discovery evidence or decisions, synthesize again, and review |
| Approval receipt is not approval-ready | Stop without changing the manifest | Invoke `$product-baseline review` |
| User changed the draft after review | Approval invocation must not be used because its attestation would be false | Invoke `$product-baseline review` on the current draft |
| An active OpenSpec change exists during approval | Stop and list its direct-child name | Complete the external OpenSpec work, then retry approval |

## External OpenSpec preservation rule

Future implementation and tests compare the path inventory, modes, symlink
targets, and version-control diff for:

```text
release/.codex/skills/openspec-*/**
release/.codex/agents/openspec-*.toml
release/openspec/config.yaml
```

Any addition, removal, or modification in those external OpenSpec-owned paths
is a failure. Only the four new `product-*` skill directories and the three
new product agent files named in `skill-contracts.md` may be added by the
future implementation.
