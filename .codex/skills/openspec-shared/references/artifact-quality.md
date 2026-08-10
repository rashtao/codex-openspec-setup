# Artifact quality

Apply only the section matching the live artifact's semantics. The current OpenSpec instruction, template, context, rules, dependency artifacts, and resolved outputs control its structure and eligible content. Do not infer an artifact type from a familiar filename or create supporting notes, glossaries, or decision records unless the live instruction authorizes them.

## Every planning artifact

- Follow the live template exactly. Fill every required section; remove placeholders.
- Use repository and domain terminology consistently. Resolve vocabulary drift against authoritative artifacts and code.
- Trace each statement to user intent, a completed dependency, repository evidence, or an explicit supported decision. Exclude speculative scope.
- Keep artifacts mutually coherent. Surface a material contradiction instead of silently weakening a higher-precedence source.

## Intent or proposal

- State the problem, why it matters, desired outcomes, cohesive scope or capabilities, explicit non-goals, and impact.
- Describe what must change, not implementation architecture, task sequencing, estimates, or milestones.
- Make each scope item trace to a present need. Split independent changes rather than hiding them in one proposal.
- Identify public-contract, integration, migration, security, and performance impact only where relevant; use the dedicated reference for the analysis.

## Behavioral specification

- Express observable outcomes, not implementation. Make every normative requirement unambiguous and testable.
- Cover material success, failure, permission, boundary, and edge behavior. Do not manufacture scenarios that add no obligation.
- Preserve the live OpenSpec requirement and scenario syntax. A modified requirement states the complete surviving obligation.
- Trace requirements to intent and keep terminology stable. Do not relax non-goals or leak design choices into behavior.

## Technical design

- Ground decisions in repository patterns and completed behavioral artifacts.
- For a consequential architecture decision, compare materially distinct viable approaches on assumptions, tradeoffs, reversibility, complexity, failure modes, and fit; record the selected decision, rationale, and relevant rejected alternatives only as the live template permits.
- Define boundaries, responsibilities, interfaces, state and data ownership, and failure propagation. Prefer substantial behavior behind a small stable interface and add a seam only where variation is real.
- Address errors, resources, concurrency, observability, testing seams, migration or rollout, security, compatibility, integration, and performance only when relevant. Avoid speculative abstraction and unrelated refactoring.
- Keep detailed requirements in behavioral artifacts and executable work items in task artifacts.

## Implementation tasks

- Group work as dependency-ordered vertical behavioral slices whose completion produces a verifiable outcome.
- Make each task trace to a requirement, design decision, or explicit stakeholder need. Cover every required behavior and consequential design decision; add no speculative work.
- State the outcome to deliver at requirement level, not scenario-by-scenario duplication or step-by-step implementation choreography. Preserve the live checkbox and section format exactly.
- Include the focused evidence and cleanup needed to prove the owning outcome without creating separate process-only tasks.

## Other artifact semantics

Check clarity, completeness, internal consistency, traceability, terminology, placeholders, and exact template compliance. Do not force the four lenses above onto a custom artifact whose live instruction defines different semantics.
