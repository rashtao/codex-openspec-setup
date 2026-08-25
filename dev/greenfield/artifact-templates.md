# Exact artifact templates

These templates are normative for the future product skills. Angle-bracketed
values are placeholders. Optional fields are explicitly marked; all other
fields and headings are required. Persisted paths are always relative to the
repository root and use `/` separators.

The future `product-shared/references/artifact-contracts.md` renders the
normative templates specified by this design contract. It is the only installed
owner of product-workflow artifact templates.

`schema_version: 1` is the only supported product-artifact schema version.
Encountering any other value stops the current product action before mutation.
Product skills never infer or perform an automatic schema migration.

## Product bundle layout

This section is the sole normative owner of the product bundle layout. Other
documents cross-reference it and do not restate any subtree.

```text
docs/product/<product-id>/
  .workflow/
    state.yaml
    pending-delivery.yaml             # optional while confirmation is pending
    receipts/
      baseline-review.yaml

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
    slice-NNN-short-slug.md
    archive/
      slice-NNN-short-slug.md
```

`.workflow/` is the control plane. Discovery is mutable until baseline
approval, the approved baseline and archived slices are user-protected, and the
roadmap plus one active slice support forward delivery. `delivery/` is created
by `roadmap`, not by discovery initialization.

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
```

Discovery and requirement identifiers are zero-padded to four digits.
Canonical examples are `FACT-0001` and `REQ-0042`. Counters only increase; an
allocated ID is never reused. A delivery slice number is a separate bounded
sequence, not an identifier in those namespaces. Its canonical filename uses
exactly three digits, `001` through `999`; this difference is intentional. A
requested slice number outside that range is rejected. Delivery slice identity
exists only in its canonical filename.

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
- Independent questions ready now: <3–8 IDs/summaries; every ready question when fewer than 3>
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
- Blocking impact: <none\|delivery-slice:<outcome description>\|release>
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
- Intended slice: <candidate outcome description or `not-yet-assigned` or `not-applicable`>
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

Completed interview rounds are immutable. Before questions are returned, append
the complete asked round, set `condition` to `awaiting-interview-response`, set
`discovery.awaiting_round` to its number, and write the exact pending markers.
Only that pending round may subsequently replace those markers with the
verbatim response, recorded outcomes, and frontier change.

```markdown
# Interview log — <product name>

## Round 1 — <RFC3339 UTC>

### Questions asked

1. [<coverage area>] <question>
   - Recommendation: <answer and rationale, or `none`>
2. <repeat for all questions>

### Response status

pending-response

### User response

PENDING RESPONSE

### Recorded outcomes

PENDING RESPONSE

### Frontier change

PENDING RESPONSE
```

Completing the pending round changes `Response status` to `recorded`, replaces
the three pending markers with exactly:

```markdown
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

The same write clears `discovery.awaiting_round`, advances
`discovery.next_round`, and sets the next valid condition.

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
```

`files` and `requirements` are lexically sorted by repository-relative path and
ID respectively. Domain-file entries repeat once per actual domain. This
manifest is the sole owner of the `REQ-*` high-water mark and review-receipt
path. Synthesis initializes `approval.review_receipt` to `null`. Review changes
only that field in the candidate manifest and writes the named receipt.
Discovery invalidation resets only that field. Approval changes the remaining
approval and freeze fields. The approve invocation attests that the
approval-ready draft was unchanged after review.

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

### `.workflow/receipts/baseline-review.yaml`

```yaml
schema_version: 1
product: "<product-id>"
manifest: "docs/product/<product-id>/baseline/manifest.yaml"
reviewed_at: "<RFC3339 UTC>"
status: "<approval-ready|issues>"
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
Warnings never hide a failed check. Each review replaces the latest receipt.
Approval retains it as the manifest's named receipt. The approve invocation is
the user's attestation that the draft was not changed after this review; the
receipt intentionally carries no content-binding value.

### `.workflow/pending-delivery.yaml`

This optional file exists only while a roadmap or slice confirmation is
pending. Its exact schema is:

```yaml
schema_version: 1
status: "pending-confirmation"
action: "<roadmap|slice>"
created_at: "<RFC3339 UTC>"
product_root: "docs/product/<product-id>"
targets:
  - path: "<repository-relative target path>"
    operation: "<create|replace>"
    content: |
      <complete exact target file content>
```

A roadmap preview has exactly one target at
`docs/product/<product-id>/delivery/roadmap.md`, using `operation: "create"`
when the roadmap is absent and `operation: "replace"` otherwise. A slice
preview has exactly two targets in order: the new canonical active-slice path
with `operation: "create"`, then the roadmap path with `operation: "replace"`.
Confirmation writes exactly `targets[].content`, then removes this file and
clears the pending condition. Rejection changes no delivery artifact, removes
this file, and clears the condition.

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
- Likely requirements: <only REQ-* rows that are not delivered or are partial>
- Sequencing rationale: <why this outcome should occur at this point>
```

The coverage table contains every baseline requirement exactly once and uses
only these forms:

```text
NOT DELIVERED
PARTIALLY DELIVERED (<comma-separated canonical slice names>)
DELIVERED (<comma-separated canonical slice names>)
```

Candidate headings are deliberately unnumbered. Candidate entries contain no
readiness, execution, dependency, blocker, expected-change, or completion
field. The initial roadmap sets every requirement to `NOT DELIVERED`.

### Active and archived `delivery/slice-NNN-short-slug.md`

````markdown
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
`DELIVERED (...)` in the pre-selection roadmap never appear here.

## In scope

- <behavior included in this one change>

## Out of scope

- <adjacent behavior excluded from this change>

## Planning context

- Frozen baseline: <relevant requirement paths and concise context>
- Archived product slices: <paths and implications, or `none`>
- Canonical OpenSpec specs: <paths and implications, or `none`>
- Archived OpenSpec changes: <paths and implications, or `none`>
- Current code: <paths and implications, or `none`>

## Proposal prompt
````

The content under `## Proposal prompt` is the fully rendered [normative proposal prompt](integration-and-handoffs.md#normative-proposal-prompt); this design cross-reference is not persisted.

The archived product slice uses this exact template because `archive` moves the
active file without changing it.

## Normative delivery console responses

### Roadmap preview

```text
Proposed roadmap change for `docs/product/<product-id>/delivery/roadmap.md`:
<complete proposed file or unified change>

Confirm in this session to write this roadmap. No delivery artifact has been
changed. Pending confirmation is stored in
`docs/product/<product-id>/.workflow/pending-delivery.yaml`.
```

### Slice preview

```text
Proposed active slice: `slice-NNN-short-slug`

Requirement coverage:
- REQ-0001: partial — <precise boundary>
- REQ-0002: complete — <precise boundary>

In scope:
- <item>

Out of scope:
- <item>

Planning context:
- <source and implication>

Proposal prompt:
<complete rendered prompt>

Roadmap change:
<complete proposed change>

Confirm in this session to write the active slice and roadmap update. No
delivery artifact has been changed. Pending confirmation is stored in
`docs/product/<product-id>/.workflow/pending-delivery.yaml`.
```

### No coherent slice

```text
Warning: the remaining uncovered or partial requirements do not form one
coherent vertical slice. No files were changed.

$product-delivery roadmap
```

### Missing same-name OpenSpec archive

```text
No archived OpenSpec change was found for `slice-NNN-short-slug`.
Complete and archive the OpenSpec change named `slice-NNN-short-slug`, then
retry `$product-delivery archive`.
```

### Successful product archive

```text
$product-delivery slice
```

### Delivery completion

```text
Delivery is complete.
```
