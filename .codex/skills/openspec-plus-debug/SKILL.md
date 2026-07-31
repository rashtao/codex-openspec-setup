---
name: openspec-plus-debug
description: Reactive failure diagnosis for an OpenSpec implementation. Use when a failed RED validation, failed GREEN, blocking review finding, or failed slice or cumulative gate requires root-cause evidence before another fix. Enforces boundary isolation, one-hypothesis discipline, condition-based waiting, defense-in-depth validation, and architectural escalation without replacing openspec-plus-tdd.
---

# Diagnose OpenSpec Implementation Failures

Diagnose one observed failure before changing behavior. Gather evidence, isolate the failing boundary, test one hypothesis, then fix the cause and verify through `openspec-plus-tdd`.

## Integration and routing

Use this skill reactively. `openspec-apply-change` continues to own slicing, correction-cycle accounting, ordered reviews, gates, task checkboxes, and handoff. `openspec-plus-tdd` continues to own every test and production edit; a cause-level fix still requires a valid RED followed by GREEN and REFACTOR.

This skill spawns no agents. The `gpt-5.6-terra` medium implementer or fixer reads it on demand after a failure. In inline mode, the orchestrator reads and follows it directly. Keep all existing routing unchanged: use `gpt-5.6-sol` high for orchestration, planning, and review; use `gpt-5.6-terra` medium for implementation and fixing; always dispatch with `fork_turns: "none"`.

## Inputs and boundaries

Require:

- the exact failing command and complete relevant output;
- the expected behavior and the observed symptom;
- the bounded affected source and test paths;
- applicable project instructions, specifications, and design decisions;
- the session baseline and current diff;
- the owning slice or whole-change correction-cycle state from `openspec-apply-change`.

Edit only the bounded affected paths and use `apply_patch` for manual edits. Preserve pre-existing and unrelated work; never reset, revert, overwrite, or absorb it. If evidence points outside the approved paths, return `NEEDS_CONTEXT` before editing.

Never mark task checkboxes, edit planning artifacts, commit, archive, or change review or gate ordering. Never mask a failure with skip, todo, disable, or comment-out markers, narrowed test filters, output suppression, weakened assertions, or replacement commands that omit required coverage. Remove all temporary instrumentation before returning.

## Four-phase diagnostic contract

Complete the phases in order for one failure.

### 1. Gather evidence

Read the complete error, stack trace, command, relevant diff, and recent in-scope changes. Reproduce with the narrowest exact command that preserves the failure. Record whether reproduction is deterministic; if it is not, collect observations without guessing.

For timing, asynchronous, or flaky failures, wait on an observable condition rather than a fixed delay. Poll fresh state with a bounded timeout and a diagnostic timeout message. Observe the event, state transition, output, resource, or count the contract actually requires; never substitute elapsed time for that condition.

### 2. Isolate the failing boundary

Map the path from the initiating input to the symptom. At each component boundary, inspect or temporarily instrument input, output, configuration propagation, and relevant state. Run once to determine the earliest boundary where expected and observed values diverge. Then investigate only the component that owns that boundary.

Trace a bad value or state backward through callers until its original source is identified. Do not fix the deepest location merely because it reports the error. Keep instrumentation narrowly scoped and remove it before returning.

### 3. Form and test one hypothesis

State exactly one hypothesis in this form:

```text
Hypothesis: <cause> because <supporting evidence>.
Falsified by: <specific observation>.
```

Test it with the smallest diagnostic observation or temporary instrumentation that varies one cause without changing behavior. Do not combine speculative fixes. If falsified, remove the instrumentation, add the result to the evidence trail, return to phase 1, and state one new hypothesis. Do not stack another change on an unverified hypothesis.

### 4. Fix the cause and verify

Before changing production behavior, establish or re-establish one valid RED under `openspec-plus-tdd`. Apply only the smallest cause-level fix needed for that RED, then complete GREEN and REFACTOR. Rerun the exact focused command and every affected gate required by `openspec-apply-change`; stale or partial results are not verification.

Where invalid data or state crosses multiple relevant boundaries, add the contract-appropriate validation at each boundary rather than only at the outermost entry point. Drive each behavior-changing validation through its own sequential TDD cycle. Keep checks proportional to the specification and approved scope; do not invent new behavior.

If the fix fails, preserve its command and result in the evidence trail and return to phase 1. Use the existing slice or whole-change correction-cycle count owned by `openspec-apply-change`; do not create a second counter. When the third failed fix for the same failure reaches that existing cap, stop before a fourth attempt and return `BLOCKED: fundamental`. Name the owning planning skill:

- `openspec-plus-design` for an architectural or technical-structure defect;
- `openspec-plus-spec` for a behavior-contract defect;
- `openspec-plus-proposal` for an intent, scope, or outcome defect.

Include the evidence trail and the planning question that must be resolved.

## Return contract

Return exactly one status: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`. Categorize `BLOCKED` as `context`, `too-large`, or `fundamental`.

Include:

- symptom and exact reproduction command/result;
- boundary isolated and the evidence that isolates it;
- each hypothesis attempted, its supporting evidence, falsifying observation, and result;
- root cause;
- valid RED evidence and the cause-level fix;
- removed instrumentation;
- fresh verification commands and results;
- remaining concerns, needed context, or architectural escalation and owning planning skill.

Return `DONE` only when the cause is established, the fix completed the TDD cycle, temporary instrumentation is removed, and fresh required verification passes.
