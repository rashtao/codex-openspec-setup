> Status: Historical, non-normative summary. The authoritative contract is [`README.md`](README.md) and its indexed documents.

# Greenfield product workflow — design summary

## Objective

Understand the complete first usable release well enough to establish coherent
requirements and domain boundaries, then deliver it through small,
independently verifiable OpenSpec changes created one at a time.

```text
Frozen product baseline
Desired first-release behavior
        │
        │ choose one coherent uncovered subset
        ▼
Active product slice
Optimistic coverage declaration and proposal prompt
        │
        │ external propose → apply → verify → archive
        ▼
Archived product slice
Return to the remaining roadmap coverage
```

Canonical `openspec/specs/` remains the external OpenSpec description of
implemented behavior. The product roadmap is only a declared coverage view; it
does not become a second behavioral specification.

## Agreed constraints

- Product horizon: first usable release.
- Repository topology: one code repository.
- Product authority: the user is the sole decision-maker.
- Normative interview-round sizing belongs to
  [`workflow-state.md`](workflow-state.md#breadth-first-discovery).
- The baseline becomes immutable after approval; there is no baseline v2.
- Product slices never modify the baseline.
- OpenSpec changes are created one at a time, immediately before implementation.
- Product artifacts live under `docs/product/`, outside OpenSpec specs and
  changes.
- The product workflow does not implement, verify, synchronize, or archive an
  OpenSpec change.
- The product workflow ends in the `delivery` phase. It neither closes nor
  relocates the product bundle.

## Repository structure

The canonical product bundle layout is defined only by
[`artifact-templates.md`](artifact-templates.md#product-bundle-layout).

The external OpenSpec integration roots are:

```text
openspec/
  specs/                          # Current implemented behavior
  changes/<focused-change>/       # Next unit of work
  changes/archive/                # Completed changes
```

Discovery is mutable until baseline approval. The baseline is user-protected
after approval. The roadmap and one active slice are mutable delivery inputs;
archived slice records are user-protected. External OpenSpec directories follow
their own established workflow.

## Discovery artifacts

The baseline contains:

- `charter.md`: release goal, outcomes, success conditions, scope, non-goals,
  and usability boundary;
- `actors-and-journeys.md`: actors, authority, and primary and exceptional
  end-to-end journeys;
- `glossary.md`: canonical terminology and important distinctions;
- `domain-map.md`: candidate product responsibilities, boundaries, and
  interactions;
- `domains/<domain>.md`: domain purpose, actors, requirements, rules,
  dependencies, exceptional cases, exclusions, and unresolved questions;
- `qualities.md`: security, privacy, accessibility, performance, reliability,
  operability, compliance, retention, and product recovery requirements;
- `dependencies.md`: external and organizational dependencies, ownership, and
  contract assumptions;
- `assumptions-and-questions.md`: accepted assumptions, known unknowns,
  assessment needs, and blocking impact;
- `decisions.md`: product decisions and rationale.

Cross-domain journeys and qualities remain separate from domain documents so
they are neither duplicated nor lost. Domains are product responsibility
hypotheses, not predetermined code, service, deployment, team, or storage
boundaries.

## Breadth-first interview

Each round:

1. reads the current discovery map;
2. identifies all independent questions on the current frontier;
3. Normative interview-round sizing belongs to
   [`workflow-state.md`](workflow-state.md#breadth-first-discovery).
4. includes a recommended answer when evidence supports one;
5. persists the asked round with the `pending-response` markers and awaiting
   state before returning the questions;
6. waits for the complete response;
7. records the response verbatim with decisions, assumptions, facts, sources,
   unknowns, fog, and exclusions;
8. clears the pending round and recalculates the frontier.

Questions that depend on another open answer wait for a later round. Findings
are classified as confirmed fact, user product decision, accepted assumption,
precise known unknown, fog that is not yet a precise question, or out of scope.

The skill asks the user for product preferences, investigates repository or
technical facts, researches material external facts from primary sources, and
persists issues unknowable before implementation as assumptions or explicit
deferrals. When the user says “I don’t know,” the skill determines whether the
issue is researchable, safely assumable, suitable for a slice, deferred to a
future OpenSpec change, release-blocking, or out of scope.

## Discovery coverage

Breadth-first discovery covers:

1. goals and success conditions;
2. actors and authority;
3. primary and exceptional journeys;
4. terminology and domain concepts;
5. functional capabilities;
6. data ownership and lifecycle;
7. cross-domain interactions;
8. external dependencies;
9. security, privacy, and compliance;
10. performance, reliability, and operations;
11. failure handling and product recovery;
12. exclusions, assumptions, and unknowns.

Normative discovery-coverage rationale belongs to
[`discovery-and-baseline-validation.md`](discovery-and-baseline-validation.md#discovery-interview).

## Fresh-context synthesis and review

The synthesizer reads only persisted discovery and state. It normalizes
terminology, identifies domains and capability boundaries, separates domain and
cross-cutting requirements, assigns neutral `REQ-*` identifiers, detects
duplicates and contradictions, creates all baseline documents, and reports
gaps without inventing answers.

A fresh review checks structure, schema, traceability, terminology, duplicates,
contradictions, journeys, domain coherence, unknown treatment, and persisted
path form. Review writes either an `issues` or `approval-ready` receipt and
changes only the manifest's receipt-path control field. An `issues` receipt
leaves the phase at `baseline-draft`; an `approval-ready` receipt changes it to
`baseline-reviewed`. Later discovery changes clear the manifest-owned receipt
path and return the phase to `baseline-draft`.

The explicit approve invocation attests that the approval-ready candidate was
not changed and freezes it. Approval records the receipt and timestamp. The
workflow stores no content-binding value and performs no later frozen-byte
check.

## Baseline requirements

Requirements use neutral identifiers such as `REQ-0042`; identity does not
encode domain, priority, or roadmap position.

```markdown
### REQ-0042 — Self-service account recovery

**Statement:** Account owners can recover access without administrator
assistance.

**Release rationale:** First-release customers must not depend on an operator
for routine recovery.

**Acceptance signal:** A locked-out account owner can complete the supported
recovery journey.

**Domain:** Identity

**Related requirements:** REQ-0017, REQ-0063

**Source IDs:** PDEC-0004, ASM-0007

**Assumptions:** ASM-0007
```

Baseline requirements are comprehensive product obligations, not
implementation-ready OpenSpec scenarios. Every included requirement is
necessary for the first usable release. Post-release ideas remain outside the
baseline.

## Roadmap decomposition

`delivery/roadmap.md` has two parts:

- a row for every baseline requirement, using only `NOT DELIVERED`,
  `PARTIALLY DELIVERED (slice names)`, or `DELIVERED (slice names)`;
- unnumbered candidate slices containing an independently demonstrable outcome,
  likely uncovered or partial requirements, and sequencing rationale.

Candidate slices are coarse and revisable. They contain no execution or
readiness state. Slices should cut vertically through the product and may touch
several domains.

Normative first-candidate sequencing belongs to
[`workflow-state.md`](workflow-state.md#roadmap).

Every roadmap write requires a control-plane preview and same-session
confirmation. The preview changes no delivery artifact. While a slice is
active, only candidates may be revised.

## Incremental OpenSpec loop

For each slice:

1. ensure no active product slice and no active OpenSpec change exists;
2. read the prioritized candidate-scope budget defined by
   [`integration-and-handoffs.md`](integration-and-handoffs.md#what-slice-may-read);
3. choose only uncovered or partially covered requirements;
4. persist and display a preview of the canonical
   `slice-NNN-short-slug`, precise coverage, boundaries, planning context,
   proposal prompt, and roadmap change;
5. after same-session approval, write the exact persisted active slice and
   roadmap targets, clear the pending preview, and immediately declare the
   planned roadmap coverage;
6. run the printed `$openspec-propose` prompt in a fresh session;
7. independently apply, verify, and archive that exactly named OpenSpec change;
8. invoke `$product-delivery archive` to move the unchanged product slice;
9. repeat until full declared coverage.

Immediate roadmap updates are deliberately optimistic. External OpenSpec owns
detailed requirements, scenarios, design, tasks, implementation, verification,
canonical spec synchronization, and its own archive.

## Completion

If every roadmap row declares `DELIVERED (...)`, both `slice` and `status`
print exactly:

```text
Delivery is complete.
```

No completion receipt, final delivery state, product-bundle move, or
post-release promotion follows.

## Existing approaches retained

- OpenSpec's specs-versus-changes distinction remains authoritative for current
  behavior versus the next delta.
- `openspec-explore` remains useful for focused investigation but does not
  replace whole-release discovery.
- Breadth-first frontiers and explicit fog support discovery.
- Domain modeling contributes terminology and boundary discipline.
- Tracer-bullet planning contributes vertical, independently demonstrable
  slices.
