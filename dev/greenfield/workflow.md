# Greenfield OpenSpec workflow — handoff summary

  ## Objective

  Understand the complete first usable release well enough to establish coherent requirements and domain boundaries, while implementing it through small, independently verifiable OpenSpec changes created one at a time.

  The workflow preserves three distinct meanings:

  Product baseline
  Desired behavior for the first usable release
          │
          │ select and refine a subset
          ▼
  Active OpenSpec change
  The next independently implementable outcome
          │
          │ apply → verify → archive
          ▼
  Canonical OpenSpec specs
  Current implemented behavior

  A separate delivery ledger maps the baseline to changes and canonical specs. It is an index and progress record, not another source of requirements.

  ## Agreed constraints

  - Product horizon: first usable release.
  - Repository topology: one code repository.
  - Product authority: the user is the sole decision-maker.
  - Interview style: breadth-first rounds of approximately 5–8 independent questions.
  - The baseline becomes immutable after approval.
  - No baseline v2 will be created.
  - Delivery discoveries never modify the baseline.
  - A requirement may be superseded or left unimplemented only after explicit user approval.
  - OpenSpec changes are created one at a time, immediately before implementation.
  - Artifacts live under docs/product/, not openspec/specs/, openspec/changes/, or experimental openspec/work/.
  - The skill must not be written until its workflow and contract are agreed.

  ## Repository structure

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
        identity.md
        accounts.md
        billing.md
        notifications.md

    delivery/
      roadmap.md
      traceability.yaml
      deviations.md
      decisions.md

  openspec/
    specs/                          # Current implemented behavior
    changes/<focused-change>/       # Next unit of work
    changes/archive/                # Completed changes

  Mutability rules:

  - discovery/: mutable during requirements discovery.
  - baseline/: immutable after user approval.
  - delivery/: mutable throughout implementation.
  - openspec/specs/: updated through the normal OpenSpec archive lifecycle.
  - Active change: mutable only for its own implementation scope.

  ## Discovery artifacts

  The final baseline should include:

  - charter.md
      - release goal, intended outcomes, success conditions, scope, non-goals and usability boundary.

  - actors-and-journeys.md
      - actors, their goals and major end-to-end journeys.

  - glossary.md
      - canonical product terminology and important distinctions.

  - domain-map.md
      - candidate domains/capabilities, responsibilities, boundaries and interactions.

  - domains/<domain>.md
      - domain purpose and boundary;
      - actors and outcomes;
      - high-level requirements;
      - business rules and invariants;
      - dependencies and exceptional cases;
      - exclusions and unresolved questions.

  - qualities.md
      - security, privacy, accessibility, performance, reliability, operability, compliance, retention and recovery requirements.

  - dependencies.md
      - external systems, organizational dependencies, ownership and contract assumptions.

  - assumptions-and-questions.md
      - accepted assumptions, known unknowns, validation needs and blocking impact.

  - decisions.md
      - product decisions and rationale.

  Cross-domain journeys and qualities remain separate from domain documents so they are neither duplicated nor lost between domains.

  Domain boundaries are product responsibility hypotheses, not predetermined code or service boundaries.

  ## Breadth-first interview

  Each round should:

  1. Read the current discovery map.
  2. Identify all independent questions on the current frontier.
  3. Ask approximately 5–8 questions spanning different product areas.
  4. Include a recommended answer when evidence supports one.
  5. Wait for the user’s complete response.
  6. Record decisions, assumptions and unknowns immediately.
  7. Recalculate the frontier.

  Questions whose answers depend on another open question wait for a later round.

  The discovery map classifies findings as:

  - confirmed fact;
  - product decision;
  - assumption;
  - known unknown;
  - fog—not yet clear enough to formulate as a precise question;
  - out of scope.

  The agent must distinguish:

  - Product decisions: ask the user.
  - Repository or technical facts: investigate directly.
  - External facts: research and present evidence.
  - Issues unknowable before implementation: record an assumption, spike or slice-level question.
  - Material deviations during delivery: always ask the user.

  If the user answers “I don’t know,” the agent determines whether the issue is researchable, safely assumable, suitable for a risk-reduction slice, release-blocking or out of scope.

  ## Discovery coverage

  The breadth-first process must cover:

  1. goals and success conditions;
  2. actors and authority;
  3. primary and exceptional journeys;
  4. terminology and domain concepts;
  5. functional capabilities;
  6. data ownership and lifecycle;
  7. cross-domain interactions;
  8. external dependencies;
  9. security, privacy and compliance;
  10. performance, reliability and operations;
  11. failure handling and recovery;
  12. exclusions, assumptions and unknowns.

  “Complete discovery” does not mean eliminating all uncertainty. It means:

  - the first-release boundary is explicit;
  - every important actor has end-to-end journeys;
  - journeys map to candidate capabilities;
  - domain responsibilities and interactions are coherent;
  - material cross-cutting concerns are covered;
  - assumptions and dependencies are visible;
  - no unresolved question silently blocks baseline approval;
  - remaining implementation questions are explicitly deferred to appropriate slices.

  ## Fresh-context synthesis

  After discovery, a fresh context or organizing agent reads only the persisted discovery/ artifacts—not the original conversation.

  It:

  1. normalizes terminology;
  2. identifies domains and capability boundaries;
  3. separates domain and cross-cutting requirements;
  4. assigns stable requirement IDs;
  5. detects duplicates, contradictions and missing journey coverage;
  6. creates the baseline documents;
  7. reports gaps back to discovery instead of inventing answers;
  8. presents the complete baseline for user approval;
  9. marks manifest.yaml as frozen.

  ## Baseline requirements

  Requirements receive neutral IDs such as REQ-0042. IDs must not encode domain, priority or roadmap position because those can change.

  Suggested format:

  ### REQ-0042 — Self-service account recovery

  **Statement:** Account owners can recover access without administrator
  assistance.

  **Release rationale:** First-release customers must not depend on an
  operator for routine recovery.

  **Acceptance signal:** A locked-out account owner can complete the supported
  recovery journey.

  **Domain:** Identity

  **Related requirements:** REQ-0017, REQ-0063

  **Assumptions:** The user controls at least one verified recovery channel.

  Baseline requirements are comprehensive but not implementation-ready OpenSpec requirements. Their acceptance signals are intentionally less detailed than Given/When/Then scenarios.

  All included requirements are presumed necessary for the first usable release. Post-release ideas belong outside the baseline rather than receiving weak priorities.

  ## Roadmap decomposition

  delivery/roadmap.md contains candidate vertical slices, not pre-created OpenSpec changes.

  Each slice records:

  - stable slice ID;
  - independently demonstrable outcome;
  - baseline requirement IDs covered;
  - dependencies and blockers;
  - principal risk reduced;
  - readiness;
  - execution state;
  - eventual OpenSpec change ID, initially empty.

  Example:

  ## SLICE-003 — Customer completes initial onboarding

  - Outcome: A newly registered customer reaches a usable account
  - Covers: REQ-0012, REQ-0014, REQ-0029
  - Depends on: SLICE-001
  - Demonstration: Complete onboarding in a clean environment
  - Readiness: candidate
  - Main risk: Account and organization ownership
  - OpenSpec change: not created

  Domains organize product knowledge. Slices organize delivery.

  Slices should cut vertically through the system and may touch several domains. Only the immediate roadmap frontier should be detailed; later slices remain coarse and revisable.

  The first slice should generally be a walking skeleton or a high-risk end-to-end path.

  ## Incremental OpenSpec loop

  For every slice:

  1. Start a clean planning context.
  2. Read current code and canonical openspec/specs/.
  3. Read only the relevant baseline requirements and accepted deviations.
  4. Explore and refine that slice against the implemented system.
  5. Create exactly one focused OpenSpec change.
  6. Reference baseline requirement and deviation IDs in proposal.md.
  7. Produce detailed behavioral requirements, scenarios, design and tasks.
  8. Apply the change.
  9. Verify implementation against the change.
  10. Archive it so its deltas update canonical specs.
  11. Update the delivery ledger.
  12. Recalculate the roadmap frontier.
  13. Select the next slice.

  A baseline requirement may require multiple changes, and one change may cover several related baseline requirements. Mapping is many-to-many.

  ## Delivery discoveries and deviations

  The baseline is never edited during implementation.

  Discoveries are classified as:

  - Slice-level refinement: capture in the active OpenSpec change.
  - Baseline requirement invalidated: ask the user whether to mark it superseded or unimplemented with reason.
  - Emergent release requirement: ask the user, assign a deviation ID and implement through a normal OpenSpec change.
  - Post-release idea: record outside the active first-release baseline.
  - Technical decision: capture in the active change design or an appropriate durable architecture decision.

  Terminal baseline dispositions are:

  - implemented;
  - superseded;
  - unimplemented-with-reason.

  Before either of the last two is assigned, the agent must show:

  - the original requirement;
  - what was discovered;
  - impact on the first usable release;
  - recommended disposition;
  - replacement behavior, if applicable;

  and obtain explicit user approval.

  Emergent requirements receive IDs such as DEV-0003; they do not receive new baseline requirement IDs.

  ## Completion and archival

  The first-release baseline is complete when:

  - every baseline requirement has a terminal disposition;
  - every accepted emergent requirement has a terminal disposition;
  - implemented entries reference archived changes and canonical specs;
  - superseded and unimplemented entries contain reasons and recorded user approval;
  - no release-blocking unknown remains;
  - a reconciliation report confirms that canonical OpenSpec specs describe the delivered release.

  Then archive the temporary product bundle under:

  docs/product/archive/<date>-<product-id>-first-release/

  Durable artifacts that remain useful—especially the glossary or product charter—may be promoted to permanent product documentation rather than archived.

  ## Existing approaches to borrow from

  - OpenSpec’s specs versus changes distinction remains authoritative for current behavior versus the next delta.
  - openspec-explore is useful for focused exploration but is too unconstrained to guarantee whole-release discovery by itself.
  - Wayfinder contributes the destination, breadth-first frontier, fog-of-war and decision-map concepts.
  - Domain-modeling contributes terminology discipline and boundary probing.
  - Tracer-bullet planning contributes vertical, independently demonstrable slices.
  - Superpowers-style single comprehensive design documents should not be used for the entire release because they encourage a monolithic specification and implementation plan.

