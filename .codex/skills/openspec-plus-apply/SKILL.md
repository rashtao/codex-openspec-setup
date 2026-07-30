---
name: openspec-plus-apply
description: Mandatory implementation-loop orchestration for an OpenSpec change. Use whenever openspec-apply-change is active, `openspec instructions apply` is invoked for implementation, or Codex is asked to implement, apply, execute, or resume an OpenSpec change. Enforces strict TDD, dependency-safe slicing, Codex subagent routing, ordered reviews, validation gates, and schema-aware tracked or untracked completion.
---

# Orchestrate OpenSpec Implementation

Own the implementation and final-review portion of `openspec-apply-change`. The vanilla skill owns change/store selection, status and apply-instruction lookup, context loading, and the final user-facing handoff. Do not repeat those stages unless their outputs are missing or stale.

## Non-negotiable invariants

- Read and follow `openspec-plus-tdd` before any test or production edit. No production code without a test observed failing for the intended reason; complete RED, GREEN, and REFACTOR for one test before starting the next.
- Cover every slice-relevant Gherkin scenario with at least one acceptance test. Never skip, disable, suppress, or comment out a failing test.
- Do not edit proposal, specification, or design artifacts from this loop. Stop and route a discovered planning defect to the appropriate OpenSpec planning skill.
- Do not mark a tracked task or untracked outcome complete until its implementation, ordered reviews, and slice gates pass.
- Run spec-compliance review before code-quality review. A report from the implementer is evidence to inspect, not proof.
- Any production/test edit after a review or gate invalidates every affected passed result. Re-establish spec compliance, then code quality, then the focused gate before relying on whole-change evidence.
- Read and follow `openspec-plus-debug` after any failed review or gate. Do not make a second fix attempt for the same failure without stating one root-cause hypothesis, its supporting evidence, and the observation that would falsify it.
- Treat the third failed correction cycle already counted for a slice or whole change as an architectural escalation. Stop before a fourth fix and route the evidence to `openspec-plus-design`, `openspec-plus-spec`, or `openspec-plus-proposal`, according to ownership.
- Do not commit, archive, invoke `openspec-verify-change`, or modify unrelated code.
- Continue between slices without routine confirmation. Pause only for ambiguity, missing authority, an artifact defect, an unrecoverable blocker, or the failure cap below.

## Codex coordination contract

Use `update_plan` to show four stages: preflight, dependency plan, slice implementation, and whole-change verification. Keep exactly one stage `in_progress`.

Use subagent mode by default. Use inline mode only when collaboration tools are unavailable or the user explicitly requests it.

All agents share the worktree but not conversation context. Protect the main context by passing paths and bounded excerpts rather than reading affected source files in the orchestrator.

### Routing and lifecycle

- Keep the active root agent as orchestrator. If orchestration itself must be delegated, use `spawn_agent` with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`.
- Any planning, design, or specification recovery agent must also use `gpt-5.6-sol`, high reasoning, and `fork_turns: "none"`; normally stop and return the defect to the corresponding planning skill instead of spawning it from this implementation loop.
- Dispatch every implementer and fixer with `model: "gpt-5.6-terra"`, `reasoning_effort: "medium"`, and `fork_turns: "none"`.
- Dispatch every spec-compliance, code-quality, and whole-change reviewer with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`.
- Explicit model overrides require `fork_turns: "none"` or a positive integer. Always use `"none"` here to avoid leaking the main conversation and to make each contract self-contained.
- Use `send_message` only to correct scope or supply missing data to an active agent. Use `followup_task` for a new fix or re-review pass after that agent is idle; it retains the model selected at spawn. Use `wait_agent` until every required agent reaches a terminal result. Never interpret idleness or a partial message as completion.
- Before accepting a report, inspect the shared worktree, confirm the returned paths stay in scope, and verify the reported commands and outcomes.

### Prompt resources

Resolve these files relative to this `SKILL.md`, read the selected file completely immediately before dispatch, and copy only its fenced prompt body verbatim. Replace every placeholder and no other text.

- `implementer-prompt.md`: initial implementation; its boundaries also govern fixer follow-ups.
- `spec-compliance-reviewer-prompt.md`: contract review for one slice.
- `code-quality-reviewer-prompt.md`: quality and project-instruction review after spec compliance passes.
- `final-review-prompt.md`: cross-slice review before the cumulative gate.

Do not reconstruct or paraphrase a resource prompt. A `followup_task` may be shorter, but it must repeat the exact failed findings, allowed paths, relevant validation commands, and unchanged prohibition on commits and planning-artifact edits.

## Phase 0: Preflight

### Validate vanilla inputs

Require the current outputs of:

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Require valid JSON and consistent change/store roots. From the apply response, retain `state`, `tasks`, `progress`, `contextFiles`, the built-in `instruction`, optional `references`, optional `context`, and optional `operationGuidance`.

Also require the vanilla workflow's resolved literal `apply.tracks` value. A non-null value selects tracked mode and must be one safe concrete path beneath `changeRoot`; a missing or null value selects untracked mode.

- `blocked`: report missing artifacts and return control to the vanilla workflow. Do not implement.
- `all_done`: in tracked mode, report current progress and return control. Do not archive.
- `ready`: continue.

Require that every concrete path in `contextFiles` has already been read by the vanilla skill. In tracked mode, require one task-tracking path equal to literal `apply.tracks`; do not expand it as a glob or aggregate multiple files. In untracked mode, require zero returned tasks and derive one bounded, verifiable outcome from the built-in instruction and applicable artifacts; do not create a tracking artifact. If these inputs are absent or ambiguous, stop and tell the user to ask Codex to apply or clarify the named change so the vanilla workflow can reload them.

### Protect existing work

Capture `git status --short` before dispatch. Existing and unrelated changes belong to the user. If a planned slice overlaps an already-modified path and the ownership of those edits is unclear, ask the user before editing. Do not reset, revert, or overwrite them.

### Discover exact project instructions and gates

Locate applicable `AGENTS.md` files and every instruction document they reference. These are the project-instruction paths passed to implementers and quality reviewers.

Inspect build manifests, applicable `AGENTS.md`, and project documentation to determine exact commands for:

- focused tests during RED/GREEN and slice verification;
- lint and format checks, distinguishing check-only commands from mutating formatters;
- type-check, build, schema, or other required checks;
- cumulative final verification.

Record complete runnable commands; do not append guessed file arguments, `--filter`, or other unsupported flags. Use the narrowest supported command for a slice and the complete relevant suite for the final gate. Ask the user directly once if a required command remains ambiguous.

## Phase 1: Build the slice graph

In tracked mode, create cohesive slices from the CLI task list and single tracking file. In untracked mode, create one synthetic slice for the instruction/artifact-defined outcome. Do not assume a particular Markdown heading shape or schema.

For every pending task/slice, record:

- exact task identifiers and text, or `untracked` plus the bounded outcome;
- relevant requirements and Gherkin scenarios;
- expected source and test paths, inferred from artifacts and repository layout;
- dependencies on other slices;
- exact focused validation commands.

Use `rg --files`, `test -e`, and `git status --short -- <path>` to classify paths. Absence from `git log` does not prove a file is missing. Treat any shared or uncertain path as a collision.

Slices may run in parallel only when their dependency closures and write sets are disjoint. Show the proposed group and ask the user directly whether to run it in parallel or sequentially. If the answer is absent or ambiguous, use sequential execution. Dispatch no more agents than available collaboration slots, and wait for every implementer in a parallel group before starting reviews.

Update the plan with the final dependency order and slice names.

## Phase 2: Execute each slice

### 1. Dispatch or implement

For subagent mode, fill `implementer-prompt.md` with:

- `{WORKING_DIRECTORY}`, `{CHANGE_NAME}`, `{SCHEMA_NAME}`, `{SLICE_ID}`, `{SLICE_NAME}`;
- `{TASKS_TEXT}` and `{RELEVANT_SPEC_TEXT}` as bounded verbatim artifact excerpts;
- `{DESIGN_PATHS}`, `{AFFECTED_PATHS}`, `{PROJECT_INSTRUCTION_PATHS}` as exact paths;
- `{TDD_SKILL_PATH}` as the absolute path to the sibling `openspec-plus-tdd/SKILL.md`;
- `{DEBUG_SKILL_PATH}` as the absolute path to the sibling `openspec-plus-debug/SKILL.md`;
- `{ACTION_CONTEXT}` and `{RUNTIME_CONSTRAINTS}` from the controlling CLI inputs;
- `{BASELINE_STATUS}` and `{GATE_COMMANDS}`.

Spawn a fresh `gpt-5.6-terra` medium implementer with `fork_turns: "none"`. The agent may edit only the bounded implementation/test paths; it must not edit the tracking or planning artifacts.

Handle its status:

- `DONE`: continue after verifying its report and paths.
- `DONE_WITH_CONCERNS`: resolve correctness or scope concerns before review; otherwise retain them for reviewers.
- `NEEDS_CONTEXT`: supply the specific missing input with `followup_task`. After three consecutive context requests, stop and ask the user.
- `BLOCKED`: provide missing context when available; split a too-large slice into dependency-safe tasks; route a fundamental artifact problem to planning. Do not retry without changing the contract. Implementers and fixers remain `gpt-5.6-terra` medium; do not promote an implementation role to a review model.

In inline mode, the main agent reads `openspec-plus-tdd/SKILL.md` completely, then the project instructions and affected files, and follows the same boundaries, TDD cycle, reports, and gates. If reviewers cannot be dispatched, perform the two resource-prompt criteria as ordered self-checks, still enforcing the three-failure cap.

### 2. Verify implementer evidence

Confirm that:

- all returned changed paths are expected or explicitly justified;
- no proposal/spec/design/tracking artifact was edited;
- each applicable scenario has a named test;
- the report contains one-test-at-a-time RED/GREEN evidence and a refactor assessment for every added test;
- focused commands passed without skipped tests or suppressed failures.

Missing temporal TDD evidence is a blocking implementer concern; request a corrected report or redo before review. Do not invent evidence from the final diff.

### 3. Run spec-compliance review

Fill `spec-compliance-reviewer-prompt.md` and spawn a fresh `gpt-5.6-sol` high reviewer with `fork_turns: "none"`. Pass exact artifact/source paths and the implementer report. The reviewer independently reads actual files and returns evidence for every task, requirement, scenario, scope boundary, and design decision.

On blocking findings, count one failed slice correction cycle, send a `followup_task` to the original implementer with the exact findings and bounded paths, and wait for its terminal report. Every production/test edit invalidates all slice review and gate evidence: restart at spec-compliance review, then code-quality review, then the complete slice gate. Stop on the third total failed correction cycle for the slice.

### 4. Run code-quality review

Only after spec compliance passes, fill `code-quality-reviewer-prompt.md` and spawn a fresh `gpt-5.6-sol` high reviewer with `fork_turns: "none"`.

On Critical or Important findings, count one failed slice correction cycle and fix through the `gpt-5.6-terra` medium implementer/fixer. Minor findings are non-blocking unless a project instruction makes them mandatory. After any production/test edit, restart at spec-compliance review; do not resume directly at code-quality review.

### 5. Run the slice gate and mark tasks

Run the exact slice commands discovered in Phase 0. A failure counts one failed slice correction cycle and returns to the implementer/fixer with the complete command and output. Require the fixer to read and follow `openspec-plus-debug` before editing. After any production/test fix, restart at spec-compliance review, then code-quality review, then rerun the whole slice gate. On the third total failed correction cycle for the slice, stop and escalate architecturally to the owning planning skill as required by the invariants.

Only after both reviewers and the gate pass, in tracked mode use `apply_patch` to replace only `[ ]` with `[x]` on this slice's exact checkboxes in the CLI-identified tracking file. Preserve each original `-` or `*` marker, whitespace, identifier, and text; re-read the changed lines. In untracked mode, edit no checkbox. Continue immediately to the next dependency-ready slice, or to whole-change verification after the untracked slice.

## Phase 3: Whole-change verification

After all tracked checkboxes are complete, or the untracked outcome slice passes:

1. Fill `final-review-prompt.md` with all artifact paths, project-instruction paths, changed paths, and the session baseline.
2. Spawn a fresh `gpt-5.6-sol` high reviewer with `fork_turns: "none"`.
3. On Critical or Important findings, count one failed whole-change correction cycle and fix through a `gpt-5.6-terra` medium fixer. Rerun each affected slice's spec-compliance review, code-quality review, and full slice gate in that order, then restart at step 1. Stop on the third total failed whole-change correction cycle.
4. Run the exact cumulative lint, format-check, test, type-check, build, and other required commands. On failure, count one failed whole-change correction cycle and route it to a terra medium fixer that reads and follows `openspec-plus-debug` before editing. Rerun each affected slice's spec-compliance review, code-quality review, and full slice gate in that order, then restart at step 1 and rerun the full cumulative gate. Every blocking result in this Phase 3 repair/re-review sequence uses the same whole-change counter; on its third total failure, stop and escalate architecturally to the owning planning skill as required by the invariants.
5. Re-run `openspec instructions apply --change "<name>" --json` with the same store flag. Require valid JSON. In tracked mode require `state: "all_done"` and complete progress. In untracked mode require `state: "ready"`, zero tasks, and unchanged instruction/context roots; completion is established by the passed outcome review and cumulative gates, not a checkbox state transition.

Do not use a mutating formatter as completion evidence without following it with its check command or a clean diff inspection. Do not claim success from stale results.

## Handoff

Return control to `openspec-apply-change` with:

- change name and schema, plus fresh tracked `N/N` progress or `untracked` mode;
- tasks completed in this session, or the completed instruction/artifact-defined outcome with no checkbox edits;
- changed paths;
- review outcomes and exact gate commands/results;
- retained non-blocking concerns.

If paused, include current progress, the concrete blocker and evidence, the appropriate planning/fix action, and that the user can resume by asking Codex to apply the same change again. If complete, say it is ready to archive and let the user request archiving separately.
