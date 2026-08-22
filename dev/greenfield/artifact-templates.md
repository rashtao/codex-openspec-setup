# Exact artifact templates

These templates are normative for the future product skills. Angle-bracketed
values are placeholders. Optional fields are explicitly marked; all other
fields and headings are required. Persisted paths are always relative to the
repository root and use `/` separators.

## Product bundle layout

```text
docs/product/<product-id>/
  .workflow/
    state.yaml
    baseline-hashes.yaml
    handoffs/
      slice-003-propose.md
    receipts/
      baseline-review.yaml
      release-reconciliation.yaml

  discovery/
    map.md
    decisions.md
    sources.md
    interview-log.md

  baseline/
    manifest.yaml
    charter.md
    actors-and-journeys.md
    glossary.md
    domain-map.md
    qualities.md
    dependencies.md
    assumptions-and-questions.md
    decisions.md
    domains/
      <domain-id>.md

  delivery/
    roadmap.md
    traceability.yaml
    deviations.md
    decisions.md
    post-release.md
```

`.workflow/` is the control plane. Discovery is mutable until baseline
approval, baseline is immutable after approval, and delivery is mutable until
closure. `delivery/` is created by `roadmap`, not by discovery initialization.

## Identifier legend

Every discovery document begins with, or links to, this legend:

```markdown
## Identifier legend

| Prefix | Meaning |
|---|---|
| `FACT` | Confirmed repository, technical, product, or external fact |
| `PDEC` | Product decision made by the user |
| `ASM` | Explicit assumption accepted for planning |
| `UNK` | Precise known unknown, including an explicit deferral |
| `FOG` | Area not yet clear enough to formulate as a precise question |
| `OOS` | Explicitly out-of-scope subject |
| `SRC` | Evidence source supporting one or more facts |
| `REQ` | Frozen first-release baseline requirement |
| `SLICE` | Mutable vertical delivery slice |
| `DEV` | Accepted delivery deviation or emergent release requirement |
```

`FACT`, `PDEC`, `ASM`, `UNK`, `FOG`, `OOS`, `SRC`, `REQ`, and `DEV` IDs are
zero-padded to four digits. `SLICE` IDs are zero-padded to three digits so their
number is preserved directly in the deterministic change name. Canonical
examples are `FACT-0001`, `REQ-0042`, `SLICE-003`, and `DEV-0003`. Counters only
increase; an allocated ID is never reused.

## Discovery artifacts

### `discovery/map.md`

```markdown
# Discovery map — <product name>

## Identifier legend

<exact identifier legend table>

## First-release boundary

- Product: <one-sentence product description or `FOG-####`>
- Intended first-release outcome: <outcome or `UNK-####`>
- Explicit exclusions: <comma-separated `OOS-*` IDs or `none recorded`>

## Coverage map

| # | Area | Status | Evidence | Open frontier |
|---:|---|---|---|---|
| 1 | Goals and success conditions | <unassessed\|partial\|covered\|explicitly-deferred> | <IDs or `none`> | <IDs or `none`> |
| 2 | Actors and authority | <status> | <IDs or `none`> | <IDs or `none`> |
| 3 | Primary and exceptional journeys | <status> | <IDs or `none`> | <IDs or `none`> |
| 4 | Terminology and domain concepts | <status> | <IDs or `none`> | <IDs or `none`> |
| 5 | Functional capabilities | <status> | <IDs or `none`> | <IDs or `none`> |
| 6 | Data ownership and lifecycle | <status> | <IDs or `none`> | <IDs or `none`> |
| 7 | Cross-domain interactions | <status> | <IDs or `none`> | <IDs or `none`> |
| 8 | External dependencies | <status> | <IDs or `none`> | <IDs or `none`> |
| 9 | Security, privacy, and compliance | <status> | <IDs or `none`> | <IDs or `none`> |
| 10 | Performance, reliability, and operations | <status> | <IDs or `none`> | <IDs or `none`> |
| 11 | Failure handling and recovery | <status> | <IDs or `none`> | <IDs or `none`> |
| 12 | Exclusions, assumptions, and unknowns | <status> | <IDs or `none`> | <IDs or `none`> |

## Current frontier

- Next round: <integer>
- Independent questions ready now: <5–8 IDs/summaries, or all available>
- Dependent questions waiting: <IDs and dependencies, or `none`>
- Synthesis assessment: <not-recommended\|recommend-ask-user\|user-requested>
- Assessment rationale: <concise evidence-based explanation>

## Confirmed facts

### FACT-0001 — <title>

- Claim: <atomic fact>
- Kind: <repository\|technical\|product\|external>
- Evidence: <SRC-* IDs, repository-relative paths, or user statement>
- Confidence: <high\|medium\|low>
- Related IDs: <IDs or `none`>

## Assumptions

### ASM-0001 — <title>

- Assumption: <atomic statement>
- Rationale: <why planning can proceed this way>
- Risk if false: <impact>
- Validation need: <future evidence or `none`>
- Blocking impact: <none\|slice:<SLICE-* or description>\|release>
- Related IDs: <IDs or `none`>

## Known unknowns

### UNK-0001 — <title>

- Status: <open\|deferred\|resolved>
- Baseline treatment: <included-assumption\|excluded-deferred-to-slice\|excluded-deferred-to-future-change\|excluded-out-of-scope>
- Unknown: <precise unanswered question>
- Why it matters: <impact>
- Evidence so far: <IDs or `none`>
- Risk: <high\|medium\|low>
- Owner: <user\|product team\|delivery slice\|external party\|unknown>
- Intended slice: <SLICE-* or `not-yet-assigned` or `not-applicable`>
- Resolution: <answer and evidence, or `unresolved`>
- Related IDs: <IDs or `none`>

## Fog

### FOG-0001 — <title>

- Area: <what is unclear>
- Why no precise question exists yet: <reason>
- Next probe: <question or investigation>
- Related IDs: <IDs or `none`>

## Out of scope

### OOS-0001 — <title>

- Exclusion: <what is excluded>
- Horizon: <first-release\|product>
- Rationale: <why>
- Approved by: user
- Related IDs: <IDs or `none`>
```

Resolved unknowns stay in place; their IDs are not converted into facts or
decisions. New supporting facts or decisions receive their own IDs.

### `discovery/decisions.md`

```markdown
# Product decisions — <product name>

## Identifier legend

<exact identifier legend table>

## Decisions

### PDEC-0001 — <decision title>

- Status: <accepted\|superseded>
- Decision: <what the user decided>
- Rationale: <why>
- Alternatives considered: <list or `none recorded`>
- Consequences: <scope, requirement, or risk impact>
- Decided by: user
- Decided at: <RFC3339 UTC>
- Superseded by: <PDEC-* or `not-applicable`>
- Related IDs: <IDs or `none`>
```

### `discovery/sources.md`

```markdown
# Discovery sources — <product name>

## Identifier legend

<exact identifier legend table>

## Sources

### SRC-0001 — <source title>

- Kind: <repository\|primary-external\|user-provided>
- Locator: <repository-relative path, HTTPS URL, or `user statement in round N`>
- Accessed at: <RFC3339 UTC>
- Supports: <FACT-* IDs>
- Supported claim: <narrow paraphrase of what this source establishes>
- Limitations: <caveats or `none identified`>
```

Only this artifact may persist an HTTPS URL. It must never persist local
absolute filesystem paths.

### `discovery/interview-log.md`

This file is append-only during discovery.

```markdown
# Interview log — <product name>

## Round 1 — <RFC3339 UTC>

### Questions asked

1. [<coverage area>] <question>
   - Recommendation: <answer and rationale, or `none`>
2. <repeat for all questions>

### User response

<verbatim response supplied for this round>

### Recorded outcomes

- Facts: <FACT-* or `none`>
- Decisions: <PDEC-* or `none`>
- Assumptions: <ASM-* or `none`>
- Unknowns: <UNK-* or `none`>
- Fog: <FOG-* or `none`>
- Exclusions: <OOS-* or `none`>
- Sources: <SRC-* or `none`>

### Frontier change

- Newly ready: <questions or `none`>
- Waiting: <questions and dependencies or `none`>
- Synthesis assessment: <not-recommended\|recommend-ask-user\|user-requested>
```

## Baseline artifacts

### Requirement block

Every requirement appears exactly once, in either a domain file or a named
cross-domain section. The exact block is:

```markdown
### REQ-0042 — <neutral requirement title>

**Statement:** <desired first-release behavior>

**Release rationale:** <why the first usable release needs it>

**Acceptance signal:** <observable, intentionally high-level outcome>

**Domain:** <domain name or `Cross-domain`>

**Related requirements:** <REQ-* IDs or `None`>

**Source IDs:** <FACT-*, PDEC-*, ASM-*, UNK-* IDs>

**Assumptions:** <ASM-* IDs or `None`>
```

Requirements do not contain priorities, implementation plans, Given/When/Then
scenarios, OpenSpec change IDs, or delivery status.

### `baseline/manifest.yaml`

```yaml
schema_version: 1
product:
  id: "<product-id>"
  name: "<product-name>"
release: "first-usable-release"
status: "<draft|frozen>"
created_at: "<RFC3339 UTC>"
frozen_at: null # RFC3339 UTC after approval
approval:
  method: null # explicit-skill-invocation after approval
  approved_at: null # RFC3339 UTC after approval
  review_receipt: null # repo-relative path after review
  reviewed_candidate_sha256: null # digest after review
highest_requirement_id: 0
files:
  - "docs/product/<product-id>/baseline/actors-and-journeys.md"
  - "docs/product/<product-id>/baseline/assumptions-and-questions.md"
  - "docs/product/<product-id>/baseline/charter.md"
  - "docs/product/<product-id>/baseline/decisions.md"
  - "docs/product/<product-id>/baseline/dependencies.md"
  - "docs/product/<product-id>/baseline/domain-map.md"
  - "docs/product/<product-id>/baseline/domains/<domain-id>.md"
  - "docs/product/<product-id>/baseline/glossary.md"
  - "docs/product/<product-id>/baseline/manifest.yaml"
  - "docs/product/<product-id>/baseline/qualities.md"
requirements:
  - id: "REQ-0001"
    path: "docs/product/<product-id>/baseline/domains/<domain-id>.md"
    heading: "REQ-0001 — <title>"
integrity:
  algorithm: "sha256"
  hashes_file: null # docs/product/<product-id>/.workflow/baseline-hashes.yaml after approval
```

`files` and `requirements` are lexically sorted by repository-relative path and
ID respectively. Domain-file entries repeat once per actual domain. Approval
changes only the approval/freeze fields and then hashes the final manifest.

### Baseline Markdown skeletons

`baseline/charter.md`:

```markdown
# First usable release charter — <product name>

## Release goal
## Intended outcomes
## Success conditions
## Included scope
## Non-goals
## Usability boundary
## Cross-domain requirements
<zero or more exact requirement blocks>
```

`baseline/actors-and-journeys.md`:

```markdown
# Actors and journeys — <product name>

## Actors and authority
### <Actor name>
- Goals:
- Authority:
- Constraints:

## Primary journeys
### <Journey name>
- Actors:
- Trigger:
- Outcome:
- Capability path:
- Related requirements:

## Exceptional journeys
### <Journey name>
- Failure or exception:
- Required recovery outcome:
- Related requirements:

## Cross-domain journey requirements
<zero or more exact requirement blocks>
```

`baseline/glossary.md`:

```markdown
# Glossary — <product name>

## Canonical terms

### <Term>
- Definition:
- Distinguish from:
- Related domains:
- Source IDs:
```

`baseline/domain-map.md`:

```markdown
# Domain map — <product name>

## Boundary principle

Domains are product responsibility hypotheses, not predetermined code,
deployment, service, team, or storage boundaries.

## Domains

### <Domain name> (`<domain-id>`)
- Purpose:
- Owns:
- Does not own:
- Actors and outcomes:
- Interactions:
- Source IDs:

## Cross-domain interactions
### <Interaction name>
- Participating domains:
- Information or authority exchanged:
- Failure responsibility:
- Related requirements:
```

`baseline/domains/<domain-id>.md`:

```markdown
# <Domain name>

## Purpose and boundary
## Actors and outcomes
## Requirements
<one or more exact requirement blocks>
## Business rules and invariants
## Dependencies and exceptional cases
## Exclusions
## Unresolved questions
```

`baseline/qualities.md`:

```markdown
# Quality requirements — <product name>

## Security
## Privacy
## Accessibility
## Performance
## Reliability
## Operability
## Compliance
## Retention
## Recovery

Each section contains zero or more exact requirement blocks. A section with no
first-release requirement says `No additional first-release requirement` and
links the supporting `OOS-*`, `UNK-*`, or decision IDs.
```

`baseline/dependencies.md`:

```markdown
# Dependencies — <product name>

## External systems
### <Dependency>
- Purpose:
- Contract assumption:
- Owner:
- Failure impact:
- Related requirements:
- Source IDs:

## Organizational dependencies
<same fields>

## Dependency requirements
<zero or more exact requirement blocks>
```

`baseline/assumptions-and-questions.md`:

```markdown
# Assumptions and known unknowns — <product name>

## Accepted assumptions
### <ASM-* — title>
- Baseline effect:
- Validation need:
- Blocking impact:
- Related requirements:

## Included known unknowns
### <UNK-* — title>
- Baseline treatment:
- Validation need:
- Intended delivery slice:
- Related requirements:

## Explicitly excluded unknowns
### <UNK-* — title>
- Exclusion treatment:
- Reason:
- Intended future locus:

## Release-blocking unknowns

`None` is required for an approval-ready baseline.
```

`baseline/decisions.md`:

```markdown
# Baseline product decisions — <product name>

## Decisions
### <PDEC-* — title>
- Decision:
- Baseline consequence:
- Related requirements:
- Source record: docs/product/<product-id>/discovery/decisions.md#<anchor>
```

## Control-plane artifacts

### `.workflow/baseline-hashes.yaml`

```yaml
schema_version: 1
algorithm: "sha256"
product: "<product-id>"
frozen_at: "<RFC3339 UTC>"
root: "docs/product/<product-id>/baseline"
files:
  - path: "docs/product/<product-id>/baseline/<file>"
    sha256: "<64 lowercase hexadecimal characters>"
aggregate:
  canonical_input: "<file-sha256><two spaces><repo-relative-path><LF>, sorted by path"
  sha256: "<64 lowercase hexadecimal characters>"
```

Hashes operate on exact file bytes. The aggregate is SHA-256 over UTF-8 lines
of the documented canonical form. Every baseline file, including the frozen
manifest, appears exactly once. The hashes file is outside the baseline and
does not hash itself.

### `.workflow/receipts/baseline-review.yaml`

```yaml
schema_version: 1
product: "<product-id>"
reviewed_at: "<RFC3339 UTC>"
status: "<approval-ready|issues>"
candidate:
  algorithm: "sha256"
  canonical_input: "<file-sha256><two spaces><repo-relative-path><LF>, sorted by path"
  aggregate_sha256: "<64 lowercase hexadecimal characters>"
  files:
    - path: "docs/product/<product-id>/baseline/<file>"
      sha256: "<64 lowercase hexadecimal characters>"
checks:
  template_compliance: "<pass|fail>"
  requirement_identity: "<pass|fail>"
  source_traceability: "<pass|fail>"
  terminology_consistency: "<pass|fail>"
  contradiction_and_duplicate_scan: "<pass|fail>"
  journey_and_domain_coherence: "<pass|fail>"
  unknown_treatment: "<pass|fail>"
  repository_relative_paths: "<pass|fail>"
issues:
  - code: "<stable-code>"
    location: "<repo-relative-path or artifact ID>"
    message: "<actionable problem>"
warnings:
  - "<non-blocking observation>"
```

For an approval-ready receipt, every check is `pass` and `issues` is `[]`.
Warnings never hide a failed check.

Before approval, each new review atomically replaces this latest-candidate
receipt. After approval it is retained unchanged as the receipt named by the
frozen manifest; no later review is allowed.

## Delivery artifacts

### `delivery/roadmap.md`

```markdown
# First-release delivery roadmap — <product name>

## State legend

- Readiness `candidate`: plausible, not on the immediate frontier.
- Readiness `ready`: dependencies are satisfied and selection is allowed.
- Readiness `blocked`: a named dependency or decision prevents selection.
- Execution `unstarted`: no sealed handoff exists.
- Execution `selected`: a proposal handoff is sealed.
- Execution `change-active`: the deterministic OpenSpec change exists.
- Execution `archived`: a matching archive exists; reconciliation is pending.
- Execution `delivered`: structural reconciliation succeeded.
- Execution `invalidated`: the slice cannot continue and its ID is retired.

## Frontier

- Recommended next slice: <SLICE-* or `ambiguous` or `none`>
- Ready alternatives: <SLICE-* IDs or `none`>
- Rationale: <risk/dependency explanation>

## Slices

### SLICE-001 — <outcome title>

- Outcome: <independently demonstrable user/system outcome>
- Covers: <REQ-* IDs>
- Accepted deviations: <DEV-* IDs or `none`>
- Coverage intent: <REQ-0001=partial, REQ-0002=complete>
- Depends on: <SLICE-* IDs or `none`>
- Blockers: <IDs/reasons or `none`>
- Demonstration: <observable end-to-end demonstration>
- Main risk: <risk reduced>
- Readiness: <candidate|ready|blocked>
- Execution: <unstarted|selected|change-active|archived|delivered|invalidated>
- Expected OpenSpec change: <slice-001-slug or `not-created`>
- OpenSpec archive: <repo-relative archive path or `not-archived`>
- Canonical specs: <repo-relative paths or `not-reconciled`>
- Handoff: <repo-relative path or `not-sealed`>
- Notes: <coarse future note or current-slice detail>
```

The roadmap may change ordering, dependencies, detail, and readiness, but never
reuses a `SLICE-*` ID or alters the historical identity of a selected slice.

### `delivery/traceability.yaml`

```yaml
schema_version: 1
product: "<product-id>"
requirements:
  - id: "REQ-0001"
    disposition: "<pending|implemented|superseded|unimplemented-with-reason>"
    coverage:
      - slice: "SLICE-001"
        change: "slice-001-<slug>"
        extent: "<partial|complete>"
        archive: null
        canonical_specs: []
    reason: null
    approval_archive: null
    replacement_ids: []
deviations:
  - id: "DEV-0001"
    type: "<emergent-requirement|supersession|unimplemented-with-reason>"
    disposition: "<pending|implemented|superseded|unimplemented-with-reason>"
    statement: "<accepted delivered or disposition statement>"
    originating_slice: "SLICE-001"
    approval_archive: "openspec/changes/archive/YYYY-MM-DD-slice-001-<slug>"
    coverage:
      - slice: "SLICE-001"
        change: "slice-001-<slug>"
        extent: "complete"
        archive: "openspec/changes/archive/YYYY-MM-DD-slice-001-<slug>"
        canonical_specs:
          - "openspec/specs/<capability>/spec.md"
    replacement_ids: []
slices:
  - id: "SLICE-001"
    expected_change: "slice-001-<slug>"
    handoff: "docs/product/<product-id>/.workflow/handoffs/slice-001-propose.md"
    handoff_sha256: "<64 lowercase hexadecimal characters>"
    archive: null
    execution: "selected"
```

An entry becomes `implemented` only when at least one coverage record has
`extent: complete`, a matching archive, and at least one canonical spec path.
Several `partial` records never implicitly become complete.

### `delivery/deviations.md`

```markdown
# Accepted delivery deviations — <product name>

## DEV-0001 — <title>

- Type: <emergent-requirement|supersession|unimplemented-with-reason>
- Status: <accepted|delivered>
- Statement: <new behavior or terminal disposition>
- Original requirement: <REQ-* or `not-applicable`>
- What changed or was discovered: <concise evidence>
- First-release impact: <impact>
- Replacement behavior: <REQ-* or DEV-* IDs, or `none`>
- Originating slice: <SLICE-*>
- Approval evidence: <repo-relative archived OpenSpec change path>
- Canonical specs: <repo-relative paths or `not-applicable`>
- Related IDs: <IDs or `none`>
```

There is no pre-archive deviation mode. The archived change is the approval
evidence, and reconciliation creates this record from the difference between
the sealed handoff and the final archived change.

### `delivery/decisions.md`

```markdown
# Delivery decisions — <product name>

## <RFC3339 UTC> — <title>

- Decision: <roadmap, recovery, or technical coordination decision>
- Context: <why it was needed>
- Consequences: <effect>
- Evidence: <artifact IDs and repository-relative paths>
- Related IDs: <REQ-*, DEV-*, SLICE-* or `none`>
```

### `delivery/post-release.md`

```markdown
# Post-release candidates — <product name>

These notes are outside the frozen first-release baseline and are not delivery
obligations unless accepted through an archived OpenSpec change and recorded as
a `DEV-*`.

## Candidate — <title>

- Idea: <future behavior, documentation, or improvement>
- Origin: <SLICE-*, archive path, or user statement>
- Why deferred: <reason>
- Suggested durable destination: <repo-relative path or `undecided`>
- Related IDs: <IDs or `none`>
```

### `.workflow/receipts/release-reconciliation.yaml`

```yaml
schema_version: 1
product: "<product-id>"
release: "first-usable-release"
reconciled_at: "<RFC3339 UTC>"
status: "complete"
baseline:
  hashes_file: "docs/product/<product-id>/.workflow/baseline-hashes.yaml"
  aggregate_sha256: "<64 lowercase hexadecimal characters>"
counts:
  requirements:
    implemented: 0
    superseded: 0
    unimplemented_with_reason: 0
  deviations:
    implemented: 0
    superseded: 0
    unimplemented_with_reason: 0
slices:
  - id: "SLICE-001"
    change: "slice-001-<slug>"
    archive: "openspec/changes/archive/YYYY-MM-DD-slice-001-<slug>"
    canonical_specs:
      - "openspec/specs/<capability>/spec.md"
checks:
  no_active_changes: "pass"
  baseline_integrity: "pass"
  terminal_dispositions: "pass"
  archive_linkage: "pass"
  canonical_spec_paths: "pass"
  slice_terminal_states: "pass"
unresolved_excluded_unknowns:
  - "UNK-0001"
post_release_notes: "docs/product/<product-id>/delivery/post-release.md"
archive_destination: "docs/product/archive/YYYY-MM-DD-<product-id>-first-release"
```

`unresolved_excluded_unknowns` may be non-empty. Any accepted requirement or
deviation that is not terminal makes this receipt impossible to issue.
