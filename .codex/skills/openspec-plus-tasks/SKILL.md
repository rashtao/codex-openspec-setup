---
name: openspec-plus-tasks
description: Create, update, review, or refine an OpenSpec task artifact as dependency-ordered vertical slices with verifiable outcomes, requirement-level traceability, exact template formatting, and independent compliance review. Use whenever `openspec instructions tasks` is invoked or an OpenSpec task checklist is being discussed or changed.
---

# OpenSpec Plus Tasks

Turn approved planning artifacts into an implementation checklist. Each numbered group must be one end-to-end vertical slice, and completing the group must produce a plainly verifiable outcome. Keep tasks at requirement or stakeholder-outcome level; specifications hold scenarios and the design holds implementation details.

## Non-negotiable boundaries

- Do not write the task artifact before completing schema resolution and vertical-slice discovery.
- Do not read source code. If proposal/spec/design artifacts do not ground a task boundary, report the planning gap instead of reverse-engineering implementation.
- Do not write implementation code, test code, TDD sequencing, exact shell commands, expected command output, estimates, or commit instructions.
- Do not group by technical layer or phase. Database, API, UI, CLI, tests, documentation, and configuration belong inside the vertical slice whose outcome they enable.
- Do not invent sections or nesting absent from the CLI template.
- Run exactly one independent compliance review after a write. Apply its blocking findings inline; do not dispatch a second review.
- Never commit changes.

Use `update_plan` for three phases and keep one step `in_progress` while work remains:

1. resolve change, schema, template, and inputs;
2. discover and confirm vertical slices;
3. write, validate, and independently review.

## Codex routing and delegation

Keep the main orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `reasoning_effort: high`. This planning workflow does not normally use implementers. If an exceptional bounded mechanical fixer is dispatched, use `gpt-5.6-terra` with `reasoning_effort: medium`; it may apply an already-decided edit but must not choose task boundaries, and the main planning agent must inspect its patch.

For delegated research or review:

- Call `spawn_agent` with `fork_turns: "none"`, the required model and reasoning effort, a bounded task name, and a complete `message` contract. A model override cannot use a full-history fork.
- Include working directory, exact files to read, read/write scope, questions, evidence requirements, and return format. Agents share the worktree but do not inherit context with `fork_turns: "none"`.
- Use `send_message` only to add missing context or correct an active agent's scope. Use `followup_task` only for a distinct bounded assignment to an idle agent, never to repeat the single-shot compliance review.
- Use `wait_agent` to collect results. Inspect cited files and the shared worktree before accepting an agent report.

## Modes

Use guided mode by default. Accelerated mode activates only when the user explicitly asks to fast-forward, skip questions, keep momentum, or create artifacts without review pauses. “Continue”, “next”, “proceed”, or “yes” alone do not activate it.

- Guided mode asks one direct question at a time for unresolved slice boundaries, always with a recommendation and rationale.
- Accelerated mode derives boundaries from approved artifacts, records material assumptions in task wording where useful, and pauses only when ambiguity could change coverage, dependency order, or multiple groups.
- Both modes perform discovery, ordering, validation, and the single-shot independent review.

If the user requested discussion or review only, remain read-only. Review an existing task artifact under the Phase 3 reviewer contract and report findings without applying them. Do not write until explicitly asked.

## Phase 1: Resolve change, template, and inputs

### Select the planning root and change

Use the store and change already selected by the surrounding OpenSpec workflow when available. If the user names a registered store, run `openspec store list --json`, resolve its exact id, and append `--store <id>` to all store-aware commands below.

Resolve the change from explicit input or unambiguous conversation context. Otherwise run `openspec list --json`, auto-select only when exactly one active change exists, and ask the user directly when several remain.

Run and require valid JSON with successful exit status:

```bash
openspec status --change "<name>" --json
openspec instructions tasks --change "<name>" --json
```

From status, use `schemaName`, `changeRoot`, `artifactPaths`, and `actionContext`; do not guess paths. Stop if the schema has no task artifact or if its status is blocked/skipped without explicit CLI authorization.

From instructions, retain:

- `artifactId`, which must identify the schema artifact mapped below
- `resolvedOutputPath` and `existingOutputPaths`
- `template`, the exact structural authority
- `instruction`, `context`, and `rules`, which constrain behavior but are not artifact content
- `dependencies`, including completion state and relative paths or globs
- optional `references`, `skipped`, and `warning`

Run `openspec schema which <schemaName> --json` from the selected project/store root, read `schema.yaml` in the returned schema directory, and resolve the literal non-null `apply.tracks` path beneath `changeRoot`. The value must be a safe relative concrete path with no glob metacharacters. Stop if tracking is absent/null, escapes `changeRoot`, or cannot be mapped to this task artifact; a schema without tracking uses instruction-driven apply and has no tracked checklist to create here.

If `skipped` is true, report the warning and do not create the artifact. For each dependency:

- if `skipped` is true, treat it as intentionally absent rather than missing;
- if incomplete, stop and identify the prerequisite artifact;
- otherwise resolve its path beneath `changeRoot`, expand any glob, and read every concrete match.

Read every dependency match and record its artifact id. Read the proposal's concrete `artifactPaths.<id>.existingOutputPaths` entries when a proposal artifact is present even if it is not a direct dependency. Read relevant referenced-store specs only as read-only upstream contracts and identify what influenced the checklist.

Use exactly one task target: `changeRoot/<apply.tracks>`. Require the current task artifact's schema `generates` pattern and CLI `resolvedOutputPath` to accept that literal path. If the artifact is glob-backed, select or create only this tracked literal file; block if the schema cannot map it safely. When the file exists, require it in `existingOutputPaths`. Do not preserve, edit, aggregate, or count other glob matches as task-tracking files.

Record every completed task's source path, id, description, and original bullet marker. Never change `[x]` back to `[ ]`, normalize `-` versus `*`, drop completed work, or renumber or repurpose it silently. If revised planning invalidates completed tasks, report that implementation and planning may be inconsistent and ask the user how to reconcile them.

Read all applicable `AGENTS.md` files and referenced project documentation for naming and planning conventions. Read task artifacts from other changes only for checklist naming conventions, never as scope evidence. Never read source files.

Parse the returned template, including any required metadata fields. The template controls syntax; this skill controls vertical-slice semantics. Do not copy CLI context, rules, or template comments into the completed artifact.

## Phase 2: Discover vertical slices

Reuse slice decisions and dependency ordering already established in recent conversation. Do not ask for resolved or safely discoverable information.

### Slice contract

For each candidate group:

1. State one sentence describing the end-to-end outcome that becomes externally or operationally verifiable when every task in the group is complete.
2. Include every layer and supporting activity needed for that outcome in the same group.
3. Trace each task to a spec requirement, an actionable design obligation, or—when specs are intentionally skipped—a proposal/stakeholder outcome.
4. Keep each task small enough for one focused work session while operating at requirement level, not one task per Gherkin scenario.
5. State WHAT is delivered. Use an inline file path only when it materially orients the implementer; leave signatures, fields, wiring choreography, data layouts, and test cases to design/specification and implementation.

If no verifiable outcome can be stated, merge or re-slice the group. Do not create standalone groups for setup, dependencies, tests, documentation, configuration, polish, refactoring, or rollout mechanics unless that group itself is the change's independently verifiable outcome.

Order groups so every prerequisite is delivered by an earlier group. Within a group, order tasks by dependency without encoding RED-GREEN-REFACTOR steps.

In guided mode, ask one direct question for each genuinely ambiguous boundary. Include the recommended boundary and why. Stop and wait; resolve follow-on branches before continuing. In accelerated mode, choose the best artifact-supported boundary unless ambiguity would alter multiple groups or omit coverage.

Before completing Phase 2, verify:

- every applicable requirement and actionable design obligation maps to at least one task;
- every task has one traceable source and no speculative scope;
- every group has a one-sentence verifiable outcome and is dependency ordered;
- all template metadata and CLI rules have been collected;
- design open questions that could change the checklist are resolved with the user.

## Phase 3: Write, validate, and review

### Write

Map every approved slice and task to the returned template and single concrete target file. Preserve the template's heading order, checkbox syntax, numbering convention, and required metadata. Preserve existing completed checkbox state and stable identifiers.

Use `apply_patch` to write only the literal tracked target resolved above. Do not add custom Files, Dependencies, Notes, Acceptance, or similar sections unless the dynamic template explicitly requires them. Do not include code, commands, commit messages, scenario-by-scenario tests, or placeholders.

Re-read the artifact and verify that all approved slices remain represented with their original specificity; concision must not erase behavior, constraints, or coverage.

Run:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
openspec instructions apply --change "<name>" --json
```

Append the selected store flag when applicable. Fix task-attributable validation failures before review. Report unrelated pre-existing validation failures separately rather than hiding them. Count task and completed checkboxes in the one tracked file and require the apply response's `tasks` and `progress` to match exactly; a mismatch is a blocking schema/tracking error.

### Single-shot compliance review

Dispatch one fresh, read-only reviewer with `spawn_agent`, `fork_turns: "none"`, `model: "gpt-5.6-sol"`, and `reasoning_effort: "high"`. Substitute every placeholder in this complete message:

```text
You are the independent reviewer for an OpenSpec task artifact. Read every
input completely and verify that the checklist is ready for implementation.
Do not edit files.

Working directory: <WORKING_DIRECTORY>
Tasks: <TASKS_PATH>
Proposal: <PROPOSAL_PATH_OR_NONE>
Planning dependencies: <DEPENDENCY_IDS_PATHS_AND_INTENTIONAL_SKIPS>
Specifications: <SPEC_PATHS_OR_INTENTIONALLY_SKIPPED_OR_NONE>
Design: <DESIGN_PATHS_OR_NONE>
Template:
<TEMPLATE_CONTENT>
OpenSpec instruction: <INSTRUCTION_OR_NONE>
OpenSpec project context: <CONTEXT_OR_NONE>
OpenSpec task rules: <RULES_OR_NONE>
Applicable project instructions: <PROJECT_INSTRUCTION_PATHS>
Completed tasks before this edit: <SOURCE_PATH_IDS_AND_DESCRIPTIONS_OR_NONE>

Check every category with cited evidence:

- Slice discipline: each numbered group delivers one sentence-worthy,
  end-to-end verifiable outcome; groups are neither technical layers nor
  setup/test/docs/polish phases and are dependency ordered.
- Task discipline: tasks are focused-session, requirement-level outcomes—not
  individual Gherkin scenarios, process gates, or TDD steps. They state WHAT;
  implementation choreography remains in design or code discovery.
- Coverage and traceability: every applicable spec requirement and actionable
  design obligation maps to a task; when specs are intentionally skipped,
  proposal/stakeholder outcomes are covered; no speculative task exists.
- Format and terminology: exact template structure and checkbox numbering,
  consistent artifact terminology, no unauthorized section or nesting, code,
  command, commit instruction, estimate, placeholder, or expected output.
- Existing progress: every previously completed task remains checked and is
  neither dropped nor silently repurposed.

Report only findings that could lose coverage, misorder implementation,
corrupt progress, violate the template, or mislead an implementer. Keep wording
polish advisory.

Return exactly:
Status: Approved | Issues Found
Issues:
- [Category]: [finding] — [evidence and impact]
Recommendations:
- [optional non-blocking improvement]
```

Use `wait_agent` for the result. If the active reviewer lacks an input, use `send_message` once to provide it. Do not re-dispatch or use `followup_task` for a second compliance pass.

For `Approved`, finish. For `Issues Found`, fix every blocking issue inline while preserving completed task state, then re-run task-attributable validation. Do not re-dispatch; the review is intentionally single-shot.

Report the task path, slice outcomes, task count, preserved completed count, validation result, reviewer outcome, applied fixes, and advisory recommendations. Do not start implementation automatically.

## Success criteria

The workflow succeeds when each group is a dependency-ordered vertical slice with a verifiable outcome, every task is focused and traceable at requirement level, all approved coverage and prior completion state survive exact-template writing, validation has no task-attributable failures, and the independent review completes exactly once.
