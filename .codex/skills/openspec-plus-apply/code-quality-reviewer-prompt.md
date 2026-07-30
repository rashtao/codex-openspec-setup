# Code-Quality Reviewer Prompt

Run this review only after the slice's spec-compliance review passes.

Dispatch with `spawn_agent` using:

- `model: "gpt-5.6-sol"`
- `reasoning_effort: "high"`
- `fork_turns: "none"`

Replace every all-caps brace token in the fenced body. Do not paraphrase the body. Re-review with `followup_task` on the same idle reviewer after fixes.

```text
Independently review code quality for OpenSpec change {CHANGE_NAME}, slice
{SLICE_ID} ({SLICE_NAME}). Spec compliance has already passed; do not repeat
that review. Work in:

{WORKING_DIRECTORY}

The worktree is shared. Do not edit files or run mutating commands. Read actual
code and project instructions instead of trusting the implementer report.

## Scope

Slice tasks and requirements, used only to judge surgical scope and simplicity:

{TASKS_TEXT}

{RELEVANT_SPEC_TEXT}

Design paths:

{DESIGN_PATHS}

Applicable AGENTS.md files and referenced project instructions:

{PROJECT_INSTRUCTION_PATHS}

Changed paths to review:

{CHANGED_PATHS}

Implementer report:

{IMPLEMENTER_REPORT}

Session baseline:

{BASELINE_STATUS}

Read every changed path, every applicable AGENTS.md/reference, and relevant
design content. Use `git diff HEAD -- <exact paths>` as supplemental evidence
for tracked files; read untracked files directly and distinguish pre-existing
work from this slice. Do not inspect unrelated paths.

## Required review

For each applicable project instruction, state PASS or FAIL and cite its source.
Then evaluate all of these areas with concrete file:line or test-name evidence:

- correctness risks not already covered by the contract review, regressions,
  security, error handling, and boundary behavior;
- defense-in-depth: required inputs and state are validated at each relevant
  boundary rather than only at the outermost entry point;
- file responsibility, decomposition, coupling, interface clarity, testability,
  naming, readability, and maintainability;
- test quality: real behavior, useful edge/error coverage, deterministic setup,
  and no skip/todo/disable/comment-out bypasses;
- surgical scope: every changed line traces to the slice, without unrelated
  formatting or cleanup;
- simplicity: no speculative features, premature abstractions, or unsupported
  configurability;
- refactoring across tasks in this slice: duplication, naming drift, missed
  shared units, superseded/dead code, and applicable code smells;
- self-documenting code: comments only for genuinely non-obvious algorithms,
  external constraints, or counter-intuitive tradeoffs; no commented-out code,
  TODO, or FIXME markers.

Do not invent a preference when the project has no rule and the implementation
is clear. Do not edit files.

## Severity and return contract

- Critical: bug, security issue, regression, broken build, or mandatory rule
  violation that makes the change unusable.
- Important: maintainability/design problem, real missing edge coverage,
  unnecessary scope/complexity, or applicable project-instruction violation.
- Minor: non-blocking observation or documented should-level preference.

Return:

STATUS: READY | NEEDS_FIXES

Strengths:
- evidence-backed strengths

Critical:
- issue — file:line — violated rule/risk — concrete fix

Important:
- issue — file:line — violated rule/risk — concrete fix

Minor:
- observation — file:line

Project instructions checked:
- source and PASS/FAIL summary

Use NEEDS_FIXES only when Critical or Important findings exist. List all such
findings in one pass.
```
