# Whole-Change Reviewer Prompt

Run this review after every slice passes and before the cumulative gate.

Dispatch with `spawn_agent` using:

- `model: "gpt-5.6-sol"`
- `reasoning_effort: "high"`
- `fork_turns: "none"`

Replace every all-caps brace token in the fenced body. Do not paraphrase the body. Re-review with `followup_task` on the same idle reviewer after fixes.

```text
Independently review the complete implementation of OpenSpec change
{CHANGE_NAME}, schema {SCHEMA_NAME}, as one integrated change. Work in:

{WORKING_DIRECTORY}

Every slice has already passed spec-compliance and code-quality review. Focus on
cross-slice behavior and cumulative quality. The worktree is shared; do not edit
files or run mutating commands.

## Inputs to read

OpenSpec artifacts:

{CONTEXT_ARTIFACT_PATHS}

Applicable AGENTS.md files and referenced project instructions:

{PROJECT_INSTRUCTION_PATHS}

All implementation/test paths changed by this apply session:

{ALL_CHANGED_PATHS}

Session baseline:

{BASELINE_STATUS}

Read every listed changed path and applicable instruction document. Use
`git diff HEAD -- <exact paths>` as supplemental evidence for tracked files;
read untracked files directly and distinguish pre-existing work. Do not inspect
or report unrelated changes.

## Required review

Assess the whole change with concrete path/line evidence:

1. Cross-slice integration: compatible interfaces, types, error contracts,
   lifecycle/order assumptions, shared state, and end-to-end test coverage.
2. Cumulative consistency: one concept uses one name and representation across
   slices; file/component boundaries remain coherent.
3. Cross-slice refactoring: duplicated logic, missed shared units, superseded or
   dead code, naming drift, and newly visible code smells.
4. Whole-change scope and simplicity: all changes trace to tasks; no cumulative
   scope creep, speculative features, premature abstractions, or unrelated edits.
5. Project-instruction compliance: evaluate every applicable instruction and
   cite its source for each failure.
6. Artifact gaps revealed by integration: unspecified interfaces, contradictory
   task boundaries, missing scenarios, or design decisions that code should not
   guess. Report these separately; do not propose silently fixing an artifact
   gap in code.

This is not a replacement for `openspec-verify-change` and must not invoke it.
Per-slice contract alignment has already been reviewed; revisit it only when a
cross-slice interaction exposes a concrete contradiction or missing behavior.

## Severity and return contract

- Critical: broken integration, regression, security defect, or mandatory rule
  failure that prevents completion.
- Important: cross-slice inconsistency, maintainability problem, cumulative
  scope/complexity, or applicable project-instruction violation.
- Minor: non-blocking observation.

Return:

STATUS: READY_FOR_GATE | NEEDS_FIXES | ARTIFACT_BLOCKED

Strengths:
- evidence-backed cross-slice strengths

Critical:
- issue — file:line — impact — concrete fix

Important:
- issue — file:line — impact — concrete fix

Minor:
- observation — file:line

Project instructions checked:
- source and PASS/FAIL summary

Artifact gaps:
- evidence — affected artifact (proposal/spec/design/tasks) — why code cannot
  safely decide

Use NEEDS_FIXES for Critical/Important code findings and ARTIFACT_BLOCKED when a
planning gap must be resolved first. List all findings in one pass. Do not edit
anything.
```
