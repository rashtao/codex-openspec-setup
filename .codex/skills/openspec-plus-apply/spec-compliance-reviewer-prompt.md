# Spec-Compliance Reviewer Prompt

Run this review before code-quality review for each slice.

Dispatch with `spawn_agent` using:

- `model: "gpt-5.6-sol"`
- `reasoning_effort: "high"`
- `fork_turns: "none"`

Replace every all-caps brace token in the fenced body. Do not paraphrase the body. Re-review with `followup_task` on the same idle reviewer after fixes.

```text
Independently review OpenSpec change {CHANGE_NAME}, slice {SLICE_ID}
({SLICE_NAME}), for contract compliance. Work in:

{WORKING_DIRECTORY}

The worktree is shared. Do not edit files, run mutating commands, or trust the
implementer's conclusions. Read the actual artifacts and changed files yourself.

## Slice contract

Tasks:

{TASKS_TEXT}

Relevant requirements and Gherkin scenarios:

{RELEVANT_SPEC_TEXT}

Artifact paths to read completely where relevant to this slice:

{CONTEXT_ARTIFACT_PATHS}

Changed implementation/test paths to inspect:

{CHANGED_PATHS}

Implementer report, supplied as evidence to verify rather than truth:

{IMPLEMENTER_REPORT}

Session baseline for separating pre-existing work:

{BASELINE_STATUS}

Read every changed path directly. Use `git diff HEAD -- <exact paths>` as
supplemental evidence for tracked files, but remember that it omits untracked
files and may contain pre-existing user changes. Do not inspect unrelated paths.

## Required review

Build a concise evidence matrix with one row for every item below; do not merge
multiple contract items into one verdict:

1. Every task identifier: fulfilled, partial, or missing, with code/test evidence.
2. Every requirement: implemented or missing, with code evidence.
3. Every Gherkin scenario: mapped to a faithful passing acceptance test or missing.
4. Every proposal scope constraint/non-goal relevant to the slice: honored or
   violated.
5. Every relevant design decision and mandated file/component boundary: honored
   or violated.

Also identify changed behavior that cannot be traced to a slice task or relevant
scenario.

Classify blocking findings as:

- Task-Incomplete
- Missing-Requirement
- Missing-Scenario
- Out-of-Scope
- Design-Violation

Do not block on general naming taste, comments, decomposition, lint/format,
framework idioms, or AGENTS.md compliance unless an explicit design decision
makes the item part of the OpenSpec contract. Those belong to code-quality
review. Do not attempt to reconstruct temporal TDD history from the final diff;
the orchestrator validates the implementer's TDD evidence separately.

## Return contract

Return `STATUS: COMPLIANT` or `STATUS: ISSUES`.

For each issue include category, task/requirement/scenario identifier, exact
file:line or test name, observed evidence, expected contract, and impact. List
all blocking findings in one pass. If compliant, summarize the strongest
evidence and give counts for tasks, requirements, and scenarios reviewed.

Do not edit anything and do not include code-quality findings as blockers.
```
