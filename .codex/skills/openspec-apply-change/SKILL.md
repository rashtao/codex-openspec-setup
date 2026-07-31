---
name: openspec-apply-change
description: Implement or continue an OpenSpec change from tracked tasks or an untracked apply instruction. Use when Codex needs to apply a change, execute pending tasks, implement an instruction-defined outcome, or resume partial implementation. Mandatory implementation-loop orchestration for an OpenSpec change. Enforces strict TDD, dependency-safe slicing, Codex subagent routing, ordered reviews, validation gates, and schema-aware tracked or untracked completion.
---

# Apply an OpenSpec Change

<!-- Source: openspec-apply-change intro; merged-workflow ownership note -->

Implement one OpenSpec change from its tracked tasks or, for a schema without task tracking, from its apply instruction and planning artifacts. Keep implementation scoped to the selected change and continue until complete or genuinely blocked.

This skill owns the full apply workflow. Ignore any legacy `openspec-plus-apply` skill if it is still discoverable.

<!-- Source: legacy implementation-loop Non-negotiable invariants; unique openspec-apply-change guardrail -->

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
- If `openspec-plus-tdd` cannot be loaded, state that limitation and execute Phase 2 inline without weakening its TDD, review, validation, invalidation, failure-cap, or reporting gates.
- Pause if the user interrupts.
- Keep changes minimal and traceable to the selected task or untracked outcome.

<!-- Source: merged legacy implementation-loop Codex coordination contract and openspec-apply-change Codex orchestration contract -->

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
- Use a bounded task name for every `spawn_agent` call.
- Put the complete delegation contract in `message`: working directory; change and slice/task identifiers; exact artifact and source paths to read; allowed edit scope; acceptance criteria; validation commands; prohibition on commits; and the required return fields (`status`, files changed, checks run, failures or blockers).
- Use `send_message` only to correct scope or supply missing data to an active agent. Use `followup_task` for a new fix or re-review pass after that agent is idle; it retains the model selected at spawn. Use `wait_agent` until every required agent reaches a terminal result, remaining responsive with concise progress updates during long waits. Never interpret idleness or a partial message as completion.
- Before accepting a report, inspect the shared worktree, confirm the returned paths stay in scope, and verify the reported commands and outcomes.
- Delegate only independent, well-bounded work.

<!-- Source: legacy implementation-loop Prompt resources; paths resolve from the merged skill -->

### Prompt resources

Resolve these files relative to this `SKILL.md`, read the selected file completely immediately before dispatch, and copy only its fenced prompt body verbatim. Replace every placeholder and no other text.

- `implementer-prompt.md`: initial implementation; its boundaries also govern fixer follow-ups.
- `spec-compliance-reviewer-prompt.md`: contract review for one slice.
- `code-quality-reviewer-prompt.md`: quality and project-instruction review after spec compliance passes.
- `final-review-prompt.md`: cross-slice review before the cumulative gate.

Do not reconstruct or paraphrase a resource prompt. A `followup_task` may be shorter, but it must repeat the exact failed findings, allowed paths, relevant validation commands, and unchanged prohibition on commits and planning-artifact edits.

<!-- Source: merged openspec-apply-change steps 1-3 and legacy implementation-loop Phase 0 -->

## Phase 0: Acquire the change and run preflight

### Store and change selection

If the user names a registered OpenSpec store, or the work clearly belongs to one, run `openspec store list --json`, resolve the store id, and append `--store <id>` to every `openspec list`, `status`, and `instructions` command below. Otherwise, let OpenSpec resolve the nearest local `openspec/` root.

Resolve the change name in this order:

1. Use the name supplied by the user.
2. Infer an unambiguous name from the conversation.
3. Run `openspec list --json`; auto-select only when exactly one active change exists.
4. If multiple changes remain possible, ask the user directly to choose from the returned names. Do not guess.

Announce `Using change: <name>` and state that the user can name a different change to override it.

### Inspect status and tracking

Run:

```bash
openspec status --change "<name>" --json
```

Require valid JSON and consistent change/store roots. Read `schemaName`, `planningHome`, `changeRoot`, `actionContext`, and artifact status. Determine which artifact owns the task list instead of assuming `tasks.md` for every schema.

Run `openspec schema which <schemaName> --json` from the selected project/store root, read the returned schema directory's `schema.yaml`, and retain the literal `apply.tracks` value. Treat a non-null value as one relative file path beneath `changeRoot`, never as a glob or set of files; block if it contains glob metacharacters, escapes `changeRoot`, or cannot be mapped safely to a schema artifact. A missing or null `apply.tracks` selects untracked apply mode.

### Load apply instructions

Run:

```bash
openspec instructions apply --change "<name>" --json
```

Require valid JSON and consistent change/store roots. Retain:

- `state`, progress, pending tasks, and the built-in `instruction`
- `contextFiles`, whose keys and paths vary by schema
- optional `references`, which indexes read-only upstream stores
- optional `context`, which is required project input when present
- optional `operationGuidance`, which is advisory when present

Handle the state before editing code:

- `blocked`: report the missing artifacts. Use the status output to identify the next artifact and `openspec instructions <artifact-id> --change "<name>" --json` to obtain its creation instructions. Ask the user whether to create or update the planning artifact; do not bypass the blocked state.
- `all_done`: in tracked mode, report the complete progress and suggest that the user ask to archive the change. Do not archive automatically.
- `ready`: continue.

In untracked mode OpenSpec 1.7.0 returns `ready` with zero tasks and does not transition to `all_done`. Treat the built-in instruction plus the applicable existing artifacts as the implementation outcome. Require zero returned tasks and derive one bounded, verifiable outcome; do not create a tracking artifact. If that outcome is not bounded and verifiable, ask the user to clarify it before editing.

Treat `context` and applicable `operationGuidance` as prompt-level constraints, not as completion evidence. The user's explicit choice, CLI-controlled state, and built-in instruction take precedence. Report conflicts; do not silently override controlling inputs. Never copy runtime context or guidance into code or planning artifacts unless the user separately requests it.

Treat `references` as read-only upstream context. Fetch only specs relevant to the selected tasks or untracked outcome using the CLI-provided command, identify them when they influence implementation, and never edit their stores from this workflow.

### Read context and display the implementation scope

Read every concrete path in `contextFiles`. Follow the CLI output rather than assuming proposal, spec, design, or task filenames. In tracked mode, require the returned task checkboxes to come from the one literal `apply.tracks` file; do not expand it as a glob or aggregate multiple files. In untracked mode, create no tracking file and edit no checkbox.

Before implementation, show the schema and CLI instruction. In tracked mode also show `N/M tasks complete` and a compact pending-task overview; in untracked mode show the single instruction/artifact-defined outcome and state that no checkbox progress exists.

### Protect existing work

Capture `git status --short` before dispatch. Existing and unrelated changes belong to the user. If a planned slice overlaps an already-modified path and the ownership of those edits is unclear, ask the user before editing. Do not reset, revert, or overwrite them.

### Discover exact project instructions and gates

Locate and read applicable `AGENTS.md` files and every instruction document they reference. These are the project-instruction paths passed to implementers and quality reviewers.

Inspect build manifests and project documentation, and use the already-read applicable `AGENTS.md` files to determine exact commands for:

- focused tests during RED/GREEN and slice verification;
- lint and format checks, distinguishing check-only commands from mutating formatters;
- type-check, build, schema, or other required checks;
- cumulative final verification.

Record complete runnable commands; do not append guessed file arguments, `--filter`, or other unsupported flags. Use the narrowest supported command for a slice and the complete relevant suite for the final gate. Ask the user directly once if a required command remains ambiguous.

<!-- Source: legacy implementation-loop Phase 1 -->

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

<!-- Source: legacy implementation-loop Phase 2; authoritative replacement for the openspec-apply-change fallback loop -->

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

<!-- Source: legacy implementation-loop Phase 3 -->

## Phase 3: Whole-change verification

After all tracked checkboxes are complete, or the untracked outcome slice passes:

1. Fill `final-review-prompt.md` with all artifact paths, project-instruction paths, changed paths, and the session baseline.
2. Spawn a fresh `gpt-5.6-sol` high reviewer with `fork_turns: "none"`.
3. On Critical or Important findings, count one failed whole-change correction cycle and fix through a `gpt-5.6-terra` medium fixer. Rerun each affected slice's spec-compliance review, code-quality review, and full slice gate in that order, then restart at step 1. Stop on the third total failed whole-change correction cycle.
4. Run the exact cumulative lint, format-check, test, type-check, build, and other required commands. On failure, count one failed whole-change correction cycle and route it to a terra medium fixer that reads and follows `openspec-plus-debug` before editing. Rerun each affected slice's spec-compliance review, code-quality review, and full slice gate in that order, then restart at step 1 and rerun the full cumulative gate. Every blocking result in this Phase 3 repair/re-review sequence uses the same whole-change counter; on its third total failure, stop and escalate architecturally to the owning planning skill as required by the invariants.
5. Re-run `openspec instructions apply --change "<name>" --json` with the same store flag. Require valid JSON. In tracked mode require `state: "all_done"` and complete progress. In untracked mode require `state: "ready"`, zero tasks, and unchanged instruction/context roots; completion is established by the passed outcome review and cumulative gates, not a checkbox state transition.

Do not use a mutating formatter as completion evidence without following it with its check command or a clean diff inspection. Do not claim success from stale results.

<!-- Source: merged legacy implementation-loop Handoff and openspec-apply-change step 5 -->

## Report to the user

On success, report:

- change name and schema
- fresh tracked `N/N` progress and tasks completed in this session, or the completed instruction/artifact-defined outcome with `no checkbox tracking`
- changed paths
- review outcomes and exact gate commands/results
- retained non-blocking concerns
- that the change is ready to archive and the user can request archiving separately

On pause, report:

- change name and schema
- current tracked progress and tasks completed in this session, or the current untracked outcome with `no checkbox tracking`
- changed paths
- review outcomes and exact gate commands/results
- retained non-blocking concerns
- the concrete blocker and evidence
- the appropriate planning or implementation action
- that the user can resume by asking Codex to apply the same change again
