---
name: openspec-verify-change
description: "Verify that an implemented OpenSpec change is complete, correct, coherent, and ready for archive using CLI-controlled task state, parsed delta requirements, source/test evidence, design alignment, and fresh project validation commands. Use when the user asks to verify, audit, review, or assess an OpenSpec implementation before archiving. This workflow is read-only and reports actionable findings without fixing them."
---

# Verify an Implemented OpenSpec Change

Produce an evidence-backed assessment across three dimensions:

- **Completeness**: planning artifacts, tracked tasks, requirements, scenarios, and expected deliverables are accounted for.
- **Correctness**: implementation and tests satisfy the observable behavior, and fresh required checks pass.
- **Coherence**: implementation follows approved design decisions and established project conventions without scope drift.

Verification is read-only. Do not edit code, tests, task checkboxes, planning artifacts, configuration, main specs, or Git state. Do not commit, archive, or invoke a fixer automatically.

## Codex Plan and Routing

Use `update_plan` with four phases and keep exactly one step `in_progress`:

1. resolve the change and authoritative inputs;
2. build traceability and inspect implementation;
3. run fresh validation and independent reviews;
4. synthesize the readiness report.

Keep the main orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `high` reasoning. Implementer and fixer agents use `gpt-5.6-terra` with `medium` reasoning, but this read-only workflow must not dispatch them. If the user asks to fix findings, hand off to `openspec-apply-change` and `openspec-plus-tdd` as a separate workflow.

For a non-trivial change, dispatch up to two independent read-only reviewers: one for requirement/scenario compliance and one for design/code-quality coherence. They may run in parallel because they never edit files. For a small change, perform the same checks inline.

When dispatching:

- use `spawn_agent` with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"` or a positive recent-turn count; model overrides cannot use a full-history fork;
- include working directory, selected store/change, exact artifact/source/test/project-instruction paths, read-only/no-commit scope, review rubric, evidence expectations, and return format;
- use `send_message` only for missing context or active-scope correction;
- use `followup_task` only for a genuinely new bounded review of newly discovered evidence after an agent is idle, never to ask a reviewer to fix files;
- use `wait_agent` for terminal results, then verify citations and conclusions against the shared filesystem.

If collaboration tools are unavailable, continue inline and state that no independent subagent pass was run. Never present an agent assertion as evidence without a path, line, test name, or command result.

## 1. Resolve the Change and Inputs

### Select one root and change

If the user names a registered store, run `openspec store list --json`, resolve the exact id, and retain `--store <id>` on every store-aware command. Otherwise use the nearest local OpenSpec root.

Resolve the change in this order:

1. explicit user-supplied name;
2. one unambiguous change established in conversation;
3. the only active change returned by `openspec list --json`;
4. otherwise show plausible changes with task progress and ask the user directly to choose.

If no active change exists, report that and stop. Announce `Using change: <name>` and say the user may name another change.

Run these commands with consistent roots:

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
openspec validate "<name>" --type change --strict --json --no-interactive
```

Add the store flag. Status and apply instructions must exit successfully and return valid JSON. From status, retain `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, and `artifacts`. From apply instructions, retain `state`, `progress`, `tasks`, `contextFiles`, the built-in `instruction`, and optional `references`, `context`, and `operationGuidance`.

For strict validation, retain valid JSON even when the command reports an invalid change. A non-zero exit, invalid JSON, or validation error is a CRITICAL planning-contract finding, but continue other read-only diagnosis when possible.

Treat CLI context/guidance as verification constraints, never artifact or report text to copy verbatim. Treat references as read-only upstream contracts and fetch only those relevant to the change.

### Classify planning state

- `state: "blocked"`: record a CRITICAL planning-completeness finding, identify missing prerequisites from status, and continue only with checks that remain meaningful. Never imply implementation readiness.
- `state: "ready"`: pending tracked tasks are CRITICAL completeness findings. Verification may continue to show additional defects, but the change is not ready for archive.
- `state: "all_done"`: task tracking claims completion; verify the claim against implementation and tests.

Artifact status is file-existence evidence only. Treat `done` and CLI `skipped` as structurally satisfied. For any other status, fetch that artifact's instructions. If the instruction explicitly makes it conditional and its conditions demonstrably do not apply, record `Conditionally absent` rather than a defect. Otherwise record the missing artifact as CRITICAL when it is an apply prerequisite or WARNING when it is advisory. Do not use `status.isComplete` alone.

### Read every concrete context file

Read every path in every `contextFiles` entry, plus relevant existing files from `artifactPaths`. Resolve only concrete paths; never read or write a glob-valued `resolvedOutputPath`. Read applicable `AGENTS.md`, the project files they reference, build manifests, test configuration, and CI definitions needed to identify authoritative checks.

Record `git status --short` before running project commands. If the root is not a Git repository, note that and continue with filesystem evidence. Existing changes may be unrelated and belong to the user. A dirty file is not proof that this change owns it; an empty diff is not proof that implementation is absent or committed.

## 2. Build Traceability and Inspect Implementation

### Use parsed requirements, not keyword guesses

When delta specs exist, run:

```bash
openspec show "<name>" --type change --json --deltas-only --no-interactive
```

Use the parsed capabilities, operations, requirements, and scenarios as the contract, while reading the raw delta files for requirement names and exact scenario text. For `skip_specs: true` or a schema without delta specs, derive verification outcomes from the proposal and tracked tasks and state that scenario-level verification is unavailable by design; report scenario totals as `N/A`, not zero coverage.

Build these evidence matrices:

1. **Task matrix**: task id/text, CLI completion state, implementation evidence, validation evidence, result.
2. **Requirement matrix**: capability and delta operation, normative requirement, production evidence, result.
3. **Scenario matrix**: scenario condition/outcome, faithful test name/path, exact focused or suite command, latest result.
4. **Design matrix**: material decision or constraint, implementation evidence, result; omit with an explicit conditional-design note when design was legitimately absent.

For ADDED and MODIFIED behavior, inspect the actual production paths and execution flow that deliver the outcome. For REMOVED behavior, verify the obsolete behavior is absent and migration/compatibility obligations are met. For RENAMED behavior, verify the new public name and any required compatibility treatment.

Every scenario must map to at least one faithful passing test. A test name or keyword hit alone is insufficient: inspect its setup, action, and assertions against the scenario. One test may cover multiple scenarios only when its assertions prove each branch. Skipped, disabled, quarantined, ignored, or vacuous tests do not count.

Inspect source and tests semantically. Cite exact file/line evidence and distinguish:

- **Confirmed**: direct code/test evidence plus a fresh passing command when executable.
- **Inferred**: strong structural evidence but no executed confirmation.
- **Unverified**: missing evidence, blocked command, ambiguous mapping, or inaccessible dependency.

Do not infer absence from unsuccessful keyword search. Search is discovery; a CRITICAL missing-behavior finding requires direct contradictory evidence, absent required paths/interfaces after scoped inspection, a failing faithful test, or an explicitly unmapped contract.

### Check design and scope coherence

For each material design decision, inspect whether implementation follows the selected boundaries, data flow, failure handling, dependency choices, security constraints, compatibility strategy, and rollout/migration obligations. Flag behavior that implements scope outside the proposal/spec or silently weakens a non-goal.

Review affected code against applicable project conventions: naming, ownership, layering, error handling, security, tests, observability, and maintainability. Do not nitpick stylistic preferences or propose unrelated refactors.

Temporal RED/GREEN history cannot be reconstructed from a final tree. Use implementation reports, session evidence, or commit history only when available. If absent, report TDD process evidence as unverified; do not fabricate it or treat its absence alone as proof that final behavior is incorrect.

## 3. Run Fresh Validation and Reviews

### Discover and run authoritative gates

Derive exact commands from `AGENTS.md`, build manifests, test configuration, CI, and documented project scripts. Run:

1. focused tests that prove each mapped scenario when supported;
2. the relevant cumulative test suite;
3. applicable lint, non-mutating format check, type-check, build, schema, and integration checks.

Do not invent flags or use mutating formatters as verification. Ask the user before a command that needs unavailable credentials, external service mutation, production access, or materially expanded authority. If a required gate cannot run, record it as Unverified and explain the blocker.

Capture exact commands, exit status, concise failure evidence, skipped-test counts, and relevant warnings. After commands, run `git status --short` again and report unexpected generated or modified files; do not delete or revert them.

- An in-scope failure is CRITICAL.
- A failure of uncertain ownership is CRITICAL verification blockage until classified.
- A proven pre-existing unrelated failure is a WARNING with baseline evidence, not something to hide or fix here.

### Independent reviewer contracts

The requirement/scenario reviewer checks every matrix row against proposal, parsed deltas, actual source, faithful tests, and fresh command results. It returns missing behavior, divergent behavior, unmapped or weak scenarios, and unsupported task completion claims.

The design/code-quality reviewer checks design adherence, scope boundaries, project instructions, error/failure behavior, security/compatibility obligations, and material maintainability issues. It must separate contractual defects from advisory quality observations.

Require each reviewer to return:

```text
Status: Approved | Issues Found | Blocked

Findings:
- [CRITICAL|WARNING|SUGGESTION] [dimension] [file:line or command evidence] — [impact] — [specific next action]

Coverage:
- [what was checked and what could not be checked]
```

Reviewers are read-only. The main orchestrator reconciles disagreements against controlling artifacts and fresh evidence. Do not lower severity merely because a finding is inconvenient, and do not elevate uncertainty into a confirmed defect.

## 4. Synthesize Readiness

Use these severities:

- **CRITICAL**: blocks an archive recommendation—invalid or incomplete required planning, pending tasks, missing/divergent required behavior, scenario without faithful passing coverage, failing in-scope gate, material design contradiction, or unresolved verification blockage.
- **WARNING**: material risk that does not yet prove contract failure—qualified uncertainty, proven unrelated baseline failure, advisory artifact absence, or non-blocking pattern deviation.
- **SUGGESTION**: optional maintainability or clarity improvement with no contract or gate impact.

Every finding needs a dimension, confidence, evidence, impact, and specific next action. Do not recommend “review this” without naming what must be checked or changed.

Report:

```markdown
## Verification Report: <change>

| Dimension | Result | Evidence summary |
|---|---|---|
| Completeness | PASS/FAIL/UNVERIFIED | ... |
| Correctness | PASS/FAIL/UNVERIFIED | ... |
| Coherence | PASS/FAIL/UNVERIFIED | ... |

Task progress: <complete>/<total>
Requirements: <confirmed>/<total>, <inferred>, <unverified>
Scenarios: <passing-covered>/<total>, <unverified>
Fresh gates: <passed>/<run>; <blocked or skipped count>
```

Then list findings by severity, commands and outcomes, skipped checks with reasons, independent-review coverage, and the exact affected paths.

Final assessment:

- Any CRITICAL finding: `Not ready to archive.`
- No critical findings but warnings: `Verification passed with documented risks; review them before choosing to archive.`
- No CRITICAL or WARNING findings and all required gates ran: `Verified and ready to archive.` Suggestions may remain.

Do not archive automatically. If fixes are needed, point to the exact planning skill for artifact defects or to `openspec-apply-change` for implementation/test defects, and tell the user to rerun verification afterward.
