---
name: openspec-plus-tdd
description: Mandatory strict test-driven development for implementing or fixing OpenSpec change tasks. Use whenever openspec-plus-apply is active, an implementer or fixer starts an OpenSpec task, or Codex writes tests or production code for OpenSpec requirements and scenarios. Enforces one-test-at-a-time RED-GREEN-REFACTOR, Gherkin acceptance coverage, scoped edits, and auditable evidence before task completion.
---

# Apply Strict TDD to OpenSpec Tasks

Use one atomic RED-GREEN-REFACTOR cycle for each behavior-changing test. The governing law is:

```text
NO PRODUCTION BEHAVIOR CHANGE WITHOUT A TEST THAT FIRST FAILS FOR THE INTENDED REASON
```

Do not batch tests, implement ahead of the current test, skip refactor assessment, hide failures, or broaden the slice.

## Integration with plus-apply

This skill governs implementation mechanics; `openspec-plus-apply` owns slicing, dispatch, reviews, gates, task checkboxes, and the final handoff.

- The plus-apply orchestrator tracks the active slice with `update_plan` and dispatches a delegated implementer or fixer through `spawn_agent` as `gpt-5.6-terra` with medium reasoning and `fork_turns: "none"`. The agent receives the absolute path to this file and must read it completely before editing.
- Main orchestrator, planning/design/specification, and review roles use `gpt-5.6-sol` with high reasoning and `fork_turns: "none"` when dispatched.
- This skill does not spawn agents. The plus-apply orchestrator uses `send_message` only for active-agent scope corrections, `followup_task` for a new pass on an idle implementer/fixer, and `wait_agent` for terminal results.
- In delegated mode, return `NEEDS_CONTEXT` or `BLOCKED` for ambiguity; the main agent asks the user directly. In inline mode, ask the user directly and wait.
- Never mark task checkboxes, edit planning artifacts, commit, or archive from this skill.

## Inputs and edit boundary

Require before editing:

- exact slice task text;
- relevant requirements and Gherkin scenarios;
- design paths and decisions;
- bounded affected source/test paths;
- applicable `AGENTS.md` files and every instruction document they reference;
- exact focused test and slice-gate commands;
- the session's baseline worktree status.

Read the design, project instructions, and affected files once before the first RED. Record the paths and relevant conventions in the implementer report. Follow all applicable rules; do not cherry-pick.

Preserve existing and unrelated changes. Edit only the approved affected paths, using `apply_patch` for manual edits. If another path is required, stop before editing it and return `NEEDS_CONTEXT` with the path and justification. Never reset or revert user work.

If a requirement or scenario is ambiguous, contradicts design, or requires changing a planning artifact, return `BLOCKED: fundamental`. Do not invent a contract.

## Plan the slice's test set

Before code, list:

1. Every relevant Gherkin scenario and its existing or intended acceptance test. Each scenario requires at least one faithful passing test; do not create a duplicate when adequate coverage already exists.
2. Additional unit, edge, helper, integration, or error-path tests justified by non-trivial branches, boundaries, and failure modes.
3. The exact focused command for each test.

Planning multiple tests is allowed; authoring them together is not. Work on one test only until its full cycle completes.

Prefer tests that exercise observable behavior. Use mocks, fakes, fixtures, or integration dependencies according to project conventions; avoid tests that prove only mock call sequences rather than outcomes.

## Per-test state machine

For each test that drives behavior—new, contract-updated, or already failing—complete every stage before beginning the next. An existing test that already fails for the intended product gap may serve as RED without being rewritten.

### 1. Checkpoint before

Record:

- test name, kind, source scenario or behavior, and file;
- relevant existing test names/count when meaningful;
- exact focused command;
- production paths this test may drive.

Do not write production code at this stage.

### 2. RED

Select one test only. Add it, update its contract expectation when the required behavior changed, or use an existing failing test that already exposes the gap. Run the focused command before any production edit.

A valid RED:

- fails because the required behavior is absent or wrong;
- reports an assertion or product-level failure consistent with the contract;
- may be a compile/type failure when the contract intentionally introduces a missing API or symbol.

An invalid RED comes from a typo, incorrect import path, broken fixture, unavailable unrelated service, timing or ordering nondeterminism in the test harness, or other test/setup defect. For timing, asynchronous, or flaky failures, follow `openspec-plus-debug` and wait on an observable condition instead of a fixed delay. Fix only the selected test or setup without adding production behavior, then rerun until the RED is valid. Never weaken a valid existing assertion merely to obtain GREEN.

Record the exact command and concise expected-failure evidence.

### 3. GREEN

Add only the smallest production change that makes the current valid test pass. Do not implement future tests, add unrequested flexibility, or refactor adjacent code.

Rerun the current test and previously green slice tests. If a valid test still fails, fix production. If investigation shows the test misstates the contract, correct the test and re-establish a valid RED before production work continues.

After a second failed attempt on the same test, read and follow `openspec-plus-debug` before another fix. State one root-cause hypothesis with supporting and falsifying evidence; every resulting production fix still requires a valid RED and this GREEN stage.

Require no new in-scope warnings, deprecations, skipped tests, or suppressed failures. Preserve and report unrelated baseline noise instead of modifying unrelated code.

Record the exact command and passing evidence.

### 4. REFACTOR

Always assess the code introduced by the current GREEN against project conventions, clarity, duplication, coupling, naming, and responsibility.

- If no change is needed, record the reason.
- If refactoring is needed, change only approved paths, add no behavior, and rerun the current plus previously green tests after each refactor step.
- If a refactor breaks tests, undo only that refactor's owned edits with `apply_patch`; never reset the worktree or discard pre-existing changes.

Record the action and fresh green evidence.

### 5. Checkpoint after

Record the resulting test name/count when meaningful, changed paths, RED evidence, GREEN evidence, and refactor outcome. Only then start the next test.

Inspect the worktree after commands that may generate or update files. An unexpected path is not implicit permission to keep it; stop and request a scope expansion before further edits.

## Edge cases

### A new test passes immediately

Do not manufacture failure by corrupting or temporarily deleting production code.

1. Verify that the test faithfully exercises the contract and is not vacuous.
2. Determine whether the behavior already exists in the baseline.
3. If behavior exists, keep the useful coverage, record `RED not applicable: pre-existing behavior; no production change driven`, record the passing command as baseline/GREEN evidence, complete the test-code refactor assessment and checkpoint, and do not claim a RED-GREEN production cycle for it.
4. If the task requires a production change, select the next missing or incorrect behavior and write a test that exposes that gap.

The iron law governs production changes: an already-passing coverage or characterization test cannot authorize new production code.

### A baseline or unrelated test fails

Determine whether the slice introduced the failure.

- Introduced or in-scope: fix it before continuing.
- Pre-existing, unrelated, or outside approved paths: do not modify unrelated code. Record the command and evidence, then return `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED` as appropriate to the controlling gate.

Never hide either kind of failure with skip/todo/disable markers, test filters that omit required coverage, output suppression, or weakened assertions.

### No viable automated test harness

Return `BLOCKED` with the missing harness or authority and the smallest concrete next step. Do not silently substitute manual verification and claim TDD completion.

### Existing production was written before RED during this pass

Stop. If the premature code consists only of this agent's current, clearly isolated edits, remove those edits with `apply_patch`, preserve all baseline work, and restart from RED. If ownership is uncertain or edits overlap user work, return `NEEDS_CONTEXT` instead of deleting anything.

## Implementation principles

- Think before coding: state assumptions; ambiguity blocks edits.
- Simplicity first: implement only what the current failing test requires.
- Surgical changes: every changed line traces to the slice and approved paths.
- Goal-driven execution: the current test is the only implementation target until its cycle completes.
- Code as documentation: prefer clear names, focused units, and obvious structure. Add comments only for genuinely non-obvious algorithms, external constraints, or counter-intuitive tradeoffs after refactoring cannot make them clear.
- Keep tests readable and behavior-focused. Do not leave commented-out code, TODO, or FIXME markers introduced by the slice.

## Slice completion

Before returning `DONE` or `DONE_WITH_CONCERNS`, verify:

- every relevant scenario maps to a faithful passing acceptance test;
- every production behavior change was driven by a valid RED;
- every test authored or used to drive behavior was handled sequentially and completed GREEN plus REFACTOR assessment;
- all added granular tests pass;
- no relevant test is skipped, disabled, suppressed, or weakened;
- changed paths remain in scope and no planning artifact changed;
- exact focused and slice-gate commands ran freshly, with outcomes recorded.

Return the status and evidence required by the plus-apply implementer contract: files/instructions read, conventions applied, changed paths, tests in execution order, scenario mapping, per-test RED/GREEN/refactor evidence, gate results, and concerns or blockers. Completion without this temporal evidence is not valid.

## Compact example

```text
Test: rejects an expired token
Before: 3 relevant tests; focused command recorded
RED: assertion expected Unauthorized, received success
GREEN: added the minimal expiry check; current and prior tests pass
REFACTOR: no change needed; branch is clear and non-duplicative
After: 4 relevant tests; paths and command results recorded

Only now begin the next test.
```
