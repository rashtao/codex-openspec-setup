# Exact artifact and console templates

These templates are normative for the future product skills. Angle-bracketed
values are placeholders. Optional content is explicitly marked; every other
field and heading is required. Persisted paths are repository-relative and use
`/` separators.

The future `product-definition/assets/artifact-templates.md` owns the
identifier, discovery, baseline, and definition-console sections. The future
`product-delivery/assets/artifact-templates.md` owns the delivery, OpenSpec
handoff, and delivery-console sections. No installed shared package exists.

`schema_version: 1` is the only supported schema version. A different value
blocks the current action before mutation; product skills do not migrate
artifacts.

## Product bundle layout

This is the sole normative product bundle layout:

```text
docs/product/<product-id>/
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

Discovery and baseline exist before delivery. The first roadmap accepts the
current baseline. The roadmap and at most one direct-child active slice are
mutable delivery records. Archived slices are user-protected. There is no
product control-plane subtree.

## Identifier legend

Every discovery document begins with this legend:

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
| `REQ` | First-release baseline requirement |
```

Discovery and requirement identifiers use four digits, such as `FACT-0001`
and `REQ-0042`. Scan existing artifacts and the manifest requirement index,
then allocate one above the greatest prior value. Never reuse an ID. A delivery
slice uses its separate three-digit filename sequence.

## Definition artifacts

### `discovery/map.md`

```markdown
# Discovery map — <product name>

## Identifier legend

<exact identifier legend table>

## First-release boundary

- Product: <one-sentence description or FOG-####>
- Intended outcome: <outcome or UNK-####>
- Explicit exclusions: <comma-separated OOS-* IDs or `none recorded`>

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
| 11 | Failure handling and product recovery | <status> | <IDs or `none`> | <IDs or `none`> |
| 12 | Exclusions, assumptions, and unknowns | <status> | <IDs or `none`> | <IDs or `none`> |

## Current frontier

- Latest incomplete round: <Round N or `none`>
- Independent questions ready now: <IDs and summaries or `none`>
- Dependent questions waiting: <questions and dependencies or `none`>
- Baseline readiness: <not-ready\|ready-with-unknowns\|ready>
- Rationale: <concise evidence-based explanation>

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
- Blocking impact: <none\|delivery-slice:<outcome>\|release>
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
- Intended slice: <candidate outcome or `not-yet-assigned` or `not-applicable`>
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
- Decided by: user
- Related IDs: <IDs or `none`>
```

Resolved unknowns stay in place. Their IDs are not converted into facts or
decisions; supporting facts and decisions receive their own IDs.

Every repeatable record section uses `None recorded` when empty. Example
records may repeat as needed and are not required during initialization.

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
- Supported claim: <narrow paraphrase>
- Limitations: <caveats or `none identified`>
```

Only `sources.md` may persist an HTTPS URL. No product artifact persists an
absolute local path.

### `discovery/interview-log.md`

```markdown
# Interview log — <product name>

## Identifier legend

<exact identifier legend table>

## Round 1 — <RFC3339 UTC>

### Questions asked

1. [<coverage area>] <question>
   - Recommendation: <answer and rationale, or `none`>
2. <repeat for three through five independent questions, or every ready question when fewer than three exist>

### Response

Unanswered
```

The latest round whose response is exactly `Unanswered` is the one incomplete
round. It is the only persisted signal that an answer is expected. Do not
append a second incomplete round.

Recording an answer replaces that response section with:

```markdown
### Response

Recorded at <RFC3339 UTC>

#### User response

<verbatim response supplied for this round>

#### Recorded outcomes

- Facts: <FACT-* or `none`>
- Decisions: <PDEC-* or `none`>
- Assumptions: <ASM-* or `none`>
- Unknowns: <UNK-* or `none`>
- Fog: <FOG-* or `none`>
- Exclusions: <OOS-* or `none`>
- Sources: <SRC-* or `none`>

#### Frontier change

- Newly ready: <questions or `none`>
- Waiting: <questions and dependencies or `none`>
- Baseline readiness: <not-ready\|ready-with-unknowns\|ready>
```

After recording, the round is immutable. A new round, if any, is appended after
all discovery artifacts have been updated.

## Baseline artifacts

### Requirement block

Every active requirement appears exactly once in a domain file or named
cross-domain section:

```markdown
### REQ-0042 — <neutral requirement title>

**Statement:** <desired first-release behavior>

**Release rationale:** <why the first usable release needs it>

**Acceptance signal:** <observable, intentionally high-level outcome>

**Domain:** <domain name or `Cross-domain`>

**Related requirements:** <REQ-* IDs or `None`>

**Source IDs:** <FACT-*, PDEC-*, ASM-*, or UNK-* IDs>

**Assumptions:** <ASM-* IDs or `None`>
```

Do not put priorities, implementation plans, Given/When/Then scenarios,
OpenSpec change IDs, or delivery status in a baseline requirement.

### `baseline/manifest.yaml`

```yaml
schema_version: 1
product:
  id: "<product-id>"
  name: "<product-name>"
  release: "first-usable-release"
timestamps:
  created_at: "<RFC3339 UTC>"
  updated_at: "<RFC3339 UTC>"
artifacts:
  - path: "docs/product/<product-id>/baseline/actors-and-journeys.md"
    kind: "actors-and-journeys"
  - path: "docs/product/<product-id>/baseline/assumptions-and-questions.md"
    kind: "assumptions-and-questions"
  - path: "docs/product/<product-id>/baseline/charter.md"
    kind: "charter"
  - path: "docs/product/<product-id>/baseline/decisions.md"
    kind: "decisions"
  - path: "docs/product/<product-id>/baseline/dependencies.md"
    kind: "dependencies"
  - path: "docs/product/<product-id>/baseline/domain-map.md"
    kind: "domain-map"
  - path: "docs/product/<product-id>/baseline/domains/<domain-id>.md"
    kind: "domain"
  - path: "docs/product/<product-id>/baseline/glossary.md"
    kind: "glossary"
  - path: "docs/product/<product-id>/baseline/manifest.yaml"
    kind: "manifest"
  - path: "docs/product/<product-id>/baseline/qualities.md"
    kind: "qualities"
requirements:
  - id: "REQ-0001"
    status: "active"
    path: "docs/product/<product-id>/baseline/domains/<domain-id>.md"
    heading: "REQ-0001 — <title>"
    source_ids: ["PDEC-0001", "FACT-0002"]
  - id: "REQ-0002"
    status: "retired"
    path: null
    heading: null
    source_ids: []
```

`artifacts` is sorted by path and contains one entry per actual baseline
file; domain entries repeat per domain. `requirements` is sorted by ID. Every
active entry resolves to one exact requirement block, and its `source_ids`
match that block. Retired entries preserve identity without owning a block.
`created_at` survives refresh; `updated_at` records the latest completed
baseline write. The manifest contains no lifecycle, delivery, or user-decision
metadata.

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
links the supporting OOS-*, UNK-*, or PDEC-* IDs.
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

<UNK-* entries or `None`>
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
- Likely requirements: <only uncovered or partial REQ-* IDs>
- Sequencing rationale: <why this outcome should occur now>
```

The coverage table contains every active baseline requirement exactly once and
uses only:

```text
NOT DELIVERED
PARTIALLY DELIVERED (<comma-separated canonical slice names>)
DELIVERED (<comma-separated canonical slice names>)
```

Candidate headings are unnumbered. Candidate entries contain no execution or
readiness fields. The first roadmap sets every row to `NOT DELIVERED`;
subsequent `roadmap` invocations preserve coverage values.

### Active and archived `delivery/slice-NNN-short-slug.md`

`````markdown
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
`DELIVERED (...)` in the pre-selection roadmap do not appear.

## In scope

- <behavior included in this one change>

## Out of scope

- <adjacent behavior excluded from this change>

## Planning context

- Baseline: <relevant requirement paths and concise context>
- Archived product slices: <paths and implications, or `none`>
- Canonical OpenSpec specs: <paths and implications, or `none`>
- Archived OpenSpec changes: <paths and implications, or `none`>
- Current code: <paths and implications, or `none`>

## Proposal prompt

```text
<fully rendered normative OpenSpec proposal handoff>
```
`````

`archive` moves this file without changing it, so the archived form uses the
same template.

## Normative OpenSpec proposal handoff

Render every placeholder before persisting and printing this prompt:

`````text
$openspec-propose

Create exactly one planning-only OpenSpec change for the greenfield product
delivery slice below. This is a fresh session; derive context from the named
repository artifacts and do not rely on prior conversation.

Required change name: slice-NNN-short-slug
Product bundle: docs/product/<product-id>
Accepted baseline: docs/product/<product-id>/baseline/manifest.yaml
Active product slice:
docs/product/<product-id>/delivery/slice-NNN-short-slug.md

Read the entire active product slice, the current code, and the canonical
`openspec/specs/` needed to plan this outcome. Create exactly
`slice-NNN-short-slug` using the installed OpenSpec schema. Produce every
planning artifact required by that schema, including detailed behavioral
requirements, scenarios, design, and tasks. Preserve the slice's in-scope and
out-of-scope boundaries and keep it vertical and independently demonstrable.

Do not implement code, apply tasks, verify behavior, synchronize canonical
specs, archive the change, create another change, or edit anything under
`docs/product/<product-id>/`. If the required name cannot be used or the
outcome cannot form one coherent change, stop and report the evidence.

After proposal creation, the user runs the external workflow for exactly
`slice-NNN-short-slug`:

`$openspec-apply-change slice-NNN-short-slug`
`$openspec-verify-change slice-NNN-short-slug`
`$openspec-archive-change slice-NNN-short-slug`

Then run:
`$product-delivery archive`
`````

The product skill prints this handoff but never invokes it. External OpenSpec
actions run in fresh sessions and retain their own contracts.

## Exact console envelopes

Every response uses the four common sections in this order. The action-specific
section appears between `Summary` and `Next`.

```text
<Action>: <done|needs-input|blocked>

Changed:
- <repository-relative path and operation, or `none`>

Summary:
- <action-specific result>

<Action-specific section>

Next:
<exact skill invocation or external OpenSpec step>
```

Use `done` when the action completed or delivery is already complete,
`needs-input` when a user answer or product decision is required, and
`blocked` when repository evidence or a workflow gate prevents the action.
List every actual changed path; never claim a write from response text alone.

### Discover

```text
Discover: <done|needs-input|blocked>

Changed:
- `<path>` (<created|updated>)
<repeat for each changed discovery file, or `- none`>

Summary:
- Product: <product-id or unresolved>
- Recorded: <round number and outcome IDs, or `none`>
- Coverage: <covered count>/12; <partial count> partial; <deferred count> explicitly deferred

Questions:
1. [<coverage area>] <question>
   Recommendation: <answer and rationale, or `none`>
<repeat, or `- none`>

Next:
<$product-definition discover, $product-definition discover <product-id>, $product-definition baseline, or $product-delivery roadmap>
```

When questions are present, `Next` is
`$product-definition discover`; the user includes the complete answers with
that invocation. When no question remains, `Next` is
`$product-definition baseline`.

### Baseline

```text
Baseline: <done|needs-input|blocked>

Changed:
- `<path>` (<created|replaced|removed>)
<repeat for every changed baseline file, or `- none`>

Summary:
- <baseline created or refreshed and self-review passed, precise missing decision, or gate>

Counts:
- Active requirements: <integer>
- Retired requirement IDs: <integer>
- Included unknowns: <integer>
- Excluded unknowns: <integer>
- Release-blocking unknowns: <integer>
- Self-review repairs: <integer>

Next:
<$product-delivery roadmap or $product-definition discover>
```

### Roadmap

```text
Roadmap: <done|needs-input|blocked>

Changed:
- `docs/product/<product-id>/delivery/roadmap.md` (<created|replaced>)
<or `- none`>

Summary:
- <initial roadmap created and baseline accepted, roadmap candidates revised, or gate>

Candidates:
1. <outcome> — <likely REQ-* IDs> — <sequencing rationale>
<repeat, or `- none`>

Next:
<$product-delivery slice, $product-definition baseline, or $product-delivery roadmap>
```

### Slice

`````text
Slice: <done|needs-input|blocked>

Changed:
- `docs/product/<product-id>/delivery/slice-NNN-short-slug.md` (created)
- `docs/product/<product-id>/delivery/roadmap.md` (replaced)
<or `- none`>

Summary:
- <slice name and outcome, delivery complete, no coherent slice, or gate>

Coverage:
- REQ-0001: partial — <precise remaining boundary>
- REQ-0002: complete — <why the full obligation is included>
<repeat, or `- none`>

Proposal:
```text
<complete rendered normative OpenSpec proposal handoff>
```
<or `none` without a code fence>

Next:
<$openspec-propose using the proposal above, $product-delivery roadmap, Delivery complete., or one exact external OpenSpec step>
`````

On successful creation, `Next` is:

```text
$openspec-propose using the proposal above in a fresh session
```

### Archive

```text
Archive: <done|needs-input|blocked>

Changed:
- `<source>` → `<destination>` (moved unchanged)
<or `- none`>

Summary:
- <slice archived unchanged, missing OpenSpec archive, destination conflict, or gate>

Archive:
- Source: <repository-relative path or `none`>
- Destination: <repository-relative path or `none`>
- OpenSpec archives: <matching direct-child basenames or `none`>

Next:
<$product-delivery slice, $product-delivery archive, one exact external OpenSpec step, or Delivery complete.>
```

When the matching OpenSpec archive is absent, `Next` is the exact external
step `$openspec-archive-change <slice-name>`; the summary says to invoke
`$product-delivery archive` after that external action succeeds. A successful
move uses `$product-delivery slice` while any roadmap row remains uncovered
or partial, and `Delivery complete.` otherwise.
