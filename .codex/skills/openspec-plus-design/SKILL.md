---
name: openspec-plus-design
description: Create, update, review, or refine an OpenSpec design artifact with explicit alternative analysis, user-owned decisions, template fidelity, and independent compliance review. Use whenever `openspec instructions design` is invoked or an OpenSpec design document is being discussed or changed.
---

# OpenSpec Plus Design

Produce an architecture-level design that follows the selected OpenSpec schema, approved proposal, any existing specification, and project conventions. Explore viable alternatives before convergence, obtain explicit user decisions, build the design incrementally, then write and review the artifact.

## Non-negotiable rules

- Do not write the design artifact before Phases 0-3 complete in either mode.
- In normal mode, do not collapse alternative selection or all design concerns into one approval.
- Keep design at HOW: architecture, boundaries, integration, data flow, failure handling, testing structure, and rollout. Detailed requirements, scenarios, task breakdowns, code, estimates, and work plans belong elsewhere.
- Align with the proposal and every existing spec. If they conflict or are materially incomplete, stop and ask the user which planning artifact to revise.
- In authoring mode, run exactly one independent compliance review after writing and apply its blocking findings inline. In review/discussion-only mode, run the same single review against the existing artifact and report findings without edits. Never dispatch a second review.
- Never commit changes.

## Modes

Use normal mode unless the user explicitly asks to fast-forward, skip questions, keep momentum, create all artifacts without review stops, or equivalent. Ordinary continuation such as “continue”, “next”, or “yes” does not enable fast-forward.

Fast-forward mode changes only interaction cadence:

- Select the strongest supported approach after doing project and artifact research.
- Generate the design concerns end-to-end without approach or per-concern approval stops.
- For a new library, select the recommended candidate only when evidence is decisive; record the comparison and tradeoffs. Pause for the user if license, security, compatibility, or architectural risk remains material.
- Still run schema resolution, project-context research, self-review, and the independent compliance review.
- Pause when proposal/spec ambiguity could change behavior or architecture.

Review/discussion-only mode is read-only and takes precedence over both authoring modes. If the user asks only to discuss or review a design, inspect the existing artifact and controlling inputs; skip authoring-only approach selection, library approval, and concern acceptance; run non-mutating validation when an artifact exists; dispatch the single-shot reviewer under Phase 4.3; and report findings without applying them. If no design exists, discuss the architecture from available evidence and state that artifact validation and review are unavailable; do not fabricate either result. Never write merely because this skill triggered. Enter authoring only when the user explicitly asks to create, update, or refine the design, or after presenting the exact proposed edits and receiving approval.

## Codex coordination and routing

Use `update_plan` with Phases 0-4 and keep one step `in_progress` while work remains.

The main orchestrator and every planning, design, specification, research, or review agent use `gpt-5.6-sol` with `reasoning_effort: high`. This workflow does not normally need implementation agents. If an exceptional bounded mechanical fixer is dispatched, use `gpt-5.6-terra` with `reasoning_effort: medium`; it may apply an already-decided edit but must not make design choices, and the main design agent must inspect its patch.

For every delegated research or review task:

- Call `spawn_agent` with `fork_turns: "none"`, the required model and reasoning effort, a bounded task name, and a complete `message` contract.
- Include the working directory, exact paths to read, allowed edit scope (normally read-only for reviewers), questions to answer, required evidence, and return format. Agents share the worktree; never assume context inheritance.
- Use `send_message` only to provide missing context or correct an active agent's scope. Use `followup_task` only for a new bounded assignment to an idle agent, never to repeat the single-shot compliance review.
- Use `wait_agent` to collect results and inspect cited files and the shared worktree before accepting them.

## Inputs and precedence

OpenSpec permits proposal → spec → design or proposal → design → spec.

Use this precedence:

1. Explicit user decisions
2. CLI-controlled schema, paths, dependency state, and template
3. Approved proposal and existing specs
4. CLI `context`, `instruction`, and `rules`
5. Applicable project instructions and established code patterns

Treat CLI `context` and `rules` as prompt constraints, not artifact content. Treat referenced stores as read-only upstream context; fetch only relevant specs and identify any upstream contract that influences the design. Stop and surface any conflict among controlling inputs rather than silently choosing one.

## Phase 0: Resolve schema and template

Use the change and store already selected by the surrounding OpenSpec workflow. If no change is selected, infer an unambiguous name from conversation; otherwise run `openspec list --json`, auto-select only when exactly one change exists, and ask the user directly when several remain. If the user names a registered store, resolve its id with `openspec store list --json` and retain `--store <id>` on `list` and `instructions` commands.

Run:

```bash
openspec instructions design --change "<name>" --json
```

Read and retain:

- `schemaName`, `changeDir`, `resolvedOutputPath`, and `existingOutputPaths`
- `template`, the structural authority for the artifact
- `instruction`, `context`, and `rules`
- `dependencies`, including relative paths or patterns and completion status
- optional `references`, `skipped`, and `warning`

If `skipped` is true, report the warning and do not create the artifact. If a dependency is missing, report it and stop; do not design against an incomplete prerequisite. Resolve each completed dependency's relative path beneath `changeDir`, expand any returned glob, and read every concrete match even if it was read earlier. Read any existing design draft as input, but do not overwrite it yet.

Parse all template headings and comments as information requirements. Later concerns must supply substance for every applicable template section. Write only to `resolvedOutputPath`, never a guessed relative path.

## Phase 1: Research and explore approaches

### Establish project context

Before proposing architecture:

1. Read all applicable `AGENTS.md` files and the project documents they reference.
2. Read the approved proposal from the CLI dependency paths.
3. Read every existing change spec under the change directory. If none exists, use proposal capabilities only and do not invent detailed requirements.
4. Read source files named by the artifacts and enough adjacent code to understand current patterns, integration seams, and similar implementations.
5. Incorporate architectural decisions and constraints already answered in the recent conversation; do not ask again.

Look up discoverable facts. Ask the user one direct question at a time only when a decision genuinely requires their preference or authority. Include the recommended answer and rationale, then stop and wait. Resolve dependent questions before generating approaches.

### Compare alternatives

In normal mode, produce two or three materially different viable approaches—two when only two real choices exist; never invent a weak option. For each include:

- name and core idea
- advantages and disadvantages
- complexity
- key assumptions
- alignment with proposal, existing specs, and project patterns

Recommend one approach and explain its accepted tradeoffs and why the others are weaker here. Mark Phase 1 complete.

## Phase 2: Select the direction and libraries

In normal mode, present all approaches in one direct selection question, mark the recommendation, and stop until the user chooses. The user owns the direction.

After selection, identify significant components that may need a new library. Prefer stable existing libraries over custom implementations. For each new or replacement library:

1. Compare two or three credible candidates using current official documentation, package metadata, maintenance, stability, license, security history, runtime/version compatibility, and existing dependencies.
2. Respect project-approved or rejected dependency lists.
3. Recommend one candidate with accepted tradeoffs and explain why custom code and other candidates are worse.
4. In normal mode, ask one direct approval question and wait before committing the dependency to the design. Already-used libraries do not need renewed approval.

Do not start Phase 3 until direction and all material dependency choices are resolved. Mark Phase 2 complete.

## Phase 3: Build design concerns

In normal mode, present one concern at a time. After each, ask directly: `Continue with this section (recommended), revise it, or revisit the design direction?` Stop and wait. Revise and re-present rejected concerns; if direction changes, return to Phase 2 and rebuild affected concerns.

Walk these concerns, skipping only those genuinely not applicable:

1. Architecture: shape, layers, boundaries, and external integration points.
2. Component structure: responsibilities and interfaces.
3. Data flow: movement, state location, and mutation ownership.
4. Error handling and failure modes: propagation, retry, partial failure, recovery, and observability.
5. Testing approach: architectural test boundaries, layers, environments, infrastructure, and hard-to-test areas that require design accommodation—not test cases or TDD ordering.
6. Migration and rollout when applicable: compatibility, deployment sequencing, rollback, and data transition.
7. Additional concerns: compare the prior concerns against every template section and the change's nature; add relevant security, performance, observability, resilience, compliance, or compatibility concerns.

Do not skip error handling or testing for a non-trivial change. Scale detail to complexity. Preserve useful tables, diagrams, flows, matrices, and other structured representations.

Before completing Phase 3:

- Map every concern to one or more template sections and ensure nothing applicable is unmapped.
- Verify every CLI rule and project constraint.
- Verify proposal/spec alignment and consistent terminology.
- Surface conflicts; never hide them behind a design choice.

Mark Phase 3 complete only after every required concern is approved in normal mode or fully developed in fast-forward mode.

## Phase 4: Write and review

### 4.1 Write the artifact

In review/discussion-only mode, skip Sections 4.1 and 4.2 and do not create or modify any file. When an existing design is under review, run `openspec validate "<name>" --type change --strict --json --no-interactive` with the selected store flag before Phase 4.3, retain the result as reviewer input, and report any failure rather than fixing it.

Write to `resolvedOutputPath` using the returned template headings, order, and comments as the structural contract. Apply `instruction`, `context`, and `rules`; do not copy those prompt inputs into the artifact.

Represent only the selected architecture. Briefly record rejected alternatives where they explain a decision, as the standard template requires, but do not mix rejected designs into the chosen system shape. Preserve the full specificity and useful structure of the approved concerns while reorganizing them into the template; do not flatten a table, diagram, flow, or matrix into weaker prose.

The completed artifact must cover the full approved selected-approach corpus, not the discarded exploration. Every abstraction must solve a present need.

### 4.2 Session-fidelity self-review

Re-read the written artifact and compare it with all selected-approach decisions, tradeoffs, rationales, constraints, integration details, approved concern content, template requirements, and user inputs from this session. List and fix every material omission or contradiction. Re-read after fixes. Do not proceed while context is missing.

### 4.3 Single-shot compliance review

Dispatch one fresh reviewer with:

- `spawn_agent`
- `fork_turns: "none"`
- `model: "gpt-5.6-sol"`
- `reasoning_effort: "high"`
- read-only scope

Substitute the concrete paths and template in this prompt; do not ask the reviewer to edit files:

```text
You are the independent reviewer for an OpenSpec design artifact. Read every
input completely and verify that the design is ready for user review.

Working directory: <WORKING_DIRECTORY>
Design: <DESIGN_PATH>
Proposal: <PROPOSAL_PATH>
Existing specs: <SPEC_PATHS_OR_NONE>
Template:
<TEMPLATE_CONTENT>
OpenSpec instruction: <INSTRUCTION_OR_NONE>
OpenSpec project context: <CONTEXT_OR_NONE>
OpenSpec design rules: <RULES_OR_NONE>
Applicable project instructions: <PROJECT_INSTRUCTION_PATHS>
OpenSpec validation result: <VALIDATION_RESULT_OR_NOT_RUN>

Check each category against cited evidence:

- Proposal alignment: every design decision traces to proposal scope and
  capabilities; non-goals remain intact.
- Spec alignment: every existing requirement is architecturally addressed;
  no contradiction or silent terminology redefinition. If no spec exists,
  ensure the design did not invent detailed requirements.
- Scope and level: architecture and integration only; no acceptance criteria,
  task lists, code, estimates, or execution work plan.
- Template and rules: exact template heading order, no missing applicable
  section, and all supplied/project constraints honored.
- Internal and terminology consistency.
- YAGNI: every abstraction, layer, and indirection serves a current need.
- Alternatives: the selected architecture is unambiguous; rejected options
  appear only as concise decision rationale, never as competing design.
- Testing strategy: architectural boundaries and infrastructure are present;
  specific tests, mocks, or implementation file plans are absent.
- Completeness: no TBD, TODO, placeholder, or materially empty section.

Calibrate findings: report only issues that could mislead review or cause a
downstream spec, task, or implementation error. Keep stylistic suggestions
advisory.

Return exactly:
Status: Approved | Issues Found
Issues:
- [Category]: [finding] — [evidence and impact]
Recommendations:
- [optional non-blocking improvement]
```

Use `wait_agent` for the result. If the active reviewer lacks context, use `send_message` once to provide it. Do not re-dispatch or use `followup_task` for another compliance pass.

If approved, continue. In authoring mode, if issues are found, fix every blocking item inline, preserving the approved design's density and structures. In review/discussion-only mode, report all blocking and advisory findings without applying them. Do not re-dispatch; the review is intentionally single-shot.

### 4.4 Finish

In authoring mode, re-read the final diff. In review/discussion-only mode, confirm the worktree was not changed by the workflow. Mark Phase 4 complete and present the design path, selected direction, important tradeoffs, validation result when run, reviewer outcome, and any advisory recommendations. Invite normal user review without automatically starting specifications, tasks, or implementation.

## Success criteria

Normal mode succeeds only when alternatives were compared, the user selected a direction, new dependencies were approved, every applicable concern was individually accepted, the artifact matches the dynamic template, and the single-shot reviewer completed. Fast-forward mode succeeds only when the same research, completeness, template, self-review, and independent-review gates pass without routine approval stops.

Review/discussion-only mode succeeds when the requested analysis, applicable non-mutating validation, and exactly one independent review of an existing artifact complete and all findings are reported without filesystem edits.
