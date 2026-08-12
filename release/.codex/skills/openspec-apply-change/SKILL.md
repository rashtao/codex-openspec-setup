---
name: openspec-apply-change
description: Implement or continue incomplete tasks from an OpenSpec change. Use when the user asks to apply a change, start implementation, resume implementation, or work through its task list.
---

Implement an OpenSpec change from its live apply instructions. Continue through coherent implementation slices until the CLI reports `all_done` or the work is genuinely blocked.

## One-hop action routing

Before any other action step:

- If the current task prompt contains `ROUTED_ACTION=openspec-apply-change`, execute this installed skill directly. Never route `openspec-apply-change` again.
- Otherwise, call exactly one child with:

```text
spawn_agent({
  task_name: "openspec_apply_change",
  message: "ROUTED_ACTION=openspec-apply-change. Execute the latest user request directly. Read .codex/skills/openspec-apply-change/SKILL.md and follow it. Never route openspec-apply-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

Use `wait_agent` to await that child and return its result. Do not also execute the apply workflow locally. No agent may dispatch itself.

## Precedence and action boundary

Resolve conflicts in this order: the user's compatible instruction; current OpenSpec CLI state, schema, instructions, and artifact semantics; this skill; optional engineering techniques. Surface a conflict instead of weakening the controlling source.

This action may implement incomplete work and safely check completed tasks. When implementation reveals a planning or design contradiction, pause, suggest updating the appropriate artifact, report the issue, and wait for guidance. Do not edit a planning artifact or resume automatically from this action. Never silently code around the contradiction, create unrelated artifacts, sync specs, archive the change, commit, publish, or begin another OpenSpec action.

Use `update_plan` when the work has multiple meaningful steps and `apply_patch` for file edits. Keep the plan about the current apply work, not a second lifecycle.

## 1. Resolve the planning root and change

If the user names a registered store or the change lives in one, run:

```bash
openspec store list --json
```

Resolve the store id and append `--store "<id>"` to every supported command in this action. The selection is sticky. Without a selected store, commands use the nearest local OpenSpec root.

Choose the change in this order:

1. Use the name the user supplied.
2. Otherwise use an unambiguous change named in the conversation.
3. Otherwise, if exactly one active change exists, select it.
4. Otherwise run the following command and ask the user to select from its result:

```bash
openspec list --json
```

With a selected store, the last command is:

```bash
openspec list --json --store "<id>"
```

Announce `Using change: <name>` and say that the user can name a different change to override it.

## 2. Read live status

Run:

```bash
openspec status --change "<name>" --json
```

With a selected store, run:

```bash
openspec status --change "<name>" --json --store "<id>"
```

Parse and retain every returned control and scope field: `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths` (`outputPath`, `resolvedOutputPath`, and `existingOutputPaths`), `nextSteps`, `actionContext`, `isPlanningComplete`, `isComplete`, `applyRequires`, `artifacts` (`id`, `outputPath`, `status`, `requires`, and any `missingDeps`), and `root`. Do not reconstruct paths or infer the active schema from familiar filenames.

The status payload does not expose the schema's `apply.tracks` path. Never invent a tracking-path field or assume a particular artifact id or filename.

## 3. Obtain and obey apply instructions

Run:

```bash
openspec instructions apply --change "<name>" --json
```

With a selected store, run:

```bash
openspec instructions apply --change "<name>" --json --store "<id>"
```

Parse and retain `changeName`, `changeDir`, `schemaName`, `contextFiles`, `progress` (`total`, `complete`, and `remaining`), `tasks` (`id`, `description`, and `done`), `state`, `missingArtifacts`, `instruction`, `references`, optional `context`, optional `operationGuidance`, and `root`.

Keep the inputs distinct:

- `state`, `missingArtifacts`, `contextFiles`, `tasks`, `progress`, and `instruction` are CLI-controlled apply inputs.
- `context` is a required project constraint.
- `operationGuidance` is advisory and applies only where compatible with controlling inputs.
- `references` is read-only upstream context. Do not mutate a referenced store as part of this action.

Neither `context` nor `operationGuidance` proves completion or permits bypassing a CLI state. Do not copy either into code or planning artifacts unless the user separately requests that content.

Handle the state exactly:

- `blocked`: report `missingArtifacts`, the CLI instruction, and the relevant status facts, then stop without implementing. Recommend the `openspec-continue-change` action. If that skill is unavailable and precise next-artifact guidance is useful, rerun status and inspect the first live `ready` artifact with:

  ```bash
  openspec instructions "<artifact-id>" --change "<name>" --json
  ```

  Append the sticky store flag when selected. This fallback is read-only guidance; do not create the artifact from this apply action.
- `all_done`: report the fresh progress and suggest the archive action. Do not run it.
- `ready`: continue below. Do not turn advisory guidance, apparent file contents, or remembered state into another state.

## 4. Load all implementation context

Read every concrete path in every array under `contextFiles` before planning or changing code. Also inspect applicable repository instructions, build metadata, nearby implementation, tests, and established local patterns needed for the current work. Treat `actionContext` as the edit boundary and use the reported `changeRoot` and paths exactly.

Summarize the schema, current `complete/total` progress, pending task descriptions, and the dynamic `instruction`. Do not claim that planning artifacts are semantically sound merely because status calls them `done`; their contents are the implementation contract and may still expose a contradiction.

## 5. Route conditional engineering guidance

Load a shared reference only for the exact reason below, then follow it without restating its doctrine here:

- `../openspec-shared/references/evidence-first.md` — when selecting evidence for a behavior change, bug fix, refactor, or an implementation where executable evidence may be unavailable.
- `../openspec-shared/references/performance-memory.md` — when the slice can plausibly affect latency, throughput, allocation, buffering, concurrency, or resource usage.
- `../openspec-shared/references/integration-correctness.md` — when a connector, protocol, external system, framework lifecycle, transaction, streaming, cancellation, retry, conversion, or compatibility boundary is involved.
- `../openspec-shared/references/debugging.md` — when reproducing or diagnosing a bug, failing test, nondeterminism, leak, regression, or unexpected implementation failure.
- `../openspec-shared/references/review.md` — before requesting or acting on an independent implementation review.
- `../openspec-shared/references/research.md` — when repository evidence is insufficient and exact dependency, protocol, framework, or runtime behavior matters.
- `../openspec-shared/references/subagents.md` — before any specialist dispatch, parallel read, or parallel implementation decision.

Omit references whose trigger is absent.

## 6. Implement one coherent slice

Choose the smallest pending vertical slice that produces one observable outcome. It may fulfill one task or a tightly coupled set of tasks; preserve the CLI task order where dependencies require it. Establish explicit file and behavior boundaries before editing.

Load and follow the applicable canonical references from step 5 before choosing evidence or making a claim. Implement the minimum complete outcome supported by the artifacts and project conventions, within a focused diff.

If implementation exposes an artifact or design contradiction, stop coding around it. Identify the exact artifact text, observed repository fact, and consequence; suggest the appropriate artifact update; report the pause; and wait for user guidance. Do not edit the artifact or resume within this invocation merely because a correction appears safe. Resume apply only after the separately authorized artifact update has occurred and fresh apply instructions have been obtained.

If a failure requires diagnosis, load and follow the shared debugging reference.

## 7. Use specialists only when they add value

The action agent remains responsible for understanding the change, resolving integration, and deciding task completion. Do not delegate a trivial local read. Use only native `spawn_agent({ task_name, message, fork_turns?, model?, reasoning_effort? })`; use `send_message`, `followup_task`, `interrupt_agent`, `list_agents`, and `wait_agent` only for existing-agent coordination.

Every specialist spawn must explicitly set the route from this matrix, use `fork_turns: "none"`, and include the complete objective, scope, relevant artifacts, repository constraints, raw evidence, applicable shared-reference requirements, expected result, and no-recursion instruction in the message. Do not claim that reading a custom-agent TOML activates a role:

| Specialist | Model | Effort | Use only for |
|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | `high` | Focused codebase, dependency, or test discovery |
| `opsx-docs-researcher` | `gpt-5.6-terra` | `high` | Version-specific primary-source research |
| `opsx-slice-implementer` | `gpt-5.6-terra` | `high` | One bounded vertical slice with a fixed file and behavior scope |
| `opsx-debugger` | `gpt-5.6-sol` | `high` | A hard defect, nondeterminism, concurrency issue, leak, or regression |
| `opsx-test-reviewer` | `gpt-5.6-sol` | `high` | Whether tests can fail for the intended defect or behavior |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | `high` | Task and implementation compliance with authoritative artifacts |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | `high` | Performance or memory methodology and measurement evidence |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | `xhigh` | High-consequence cross-artifact and cross-slice consistency |

Parallelize independent reads when useful. Parallel writes are allowed only for dependency-independent slices with disjoint file scopes and a defined integration order. Stop a writer that encounters an unexpected overlapping modification.

Give an independent reviewer the authoritative artifact paths or contents, relevant diff, repository standards, and raw verification evidence. Never give it the implementer's reasoning transcript. Review is read-only; the action agent evaluates findings against repository reality and owns any fixes.

## 8. Verify, then check tasks

After the slice is implemented:

1. Remove temporary instrumentation and inspect the focused diff.
2. Run fresh, applicable focused tests and static/build checks for the changed scope. Run any required integration, compatibility, or performance evidence under the conditions identified earlier.
3. Evaluate any relevant independent findings and fix confirmed Critical or Important issues; push back with evidence on incorrect findings.
4. Rerun the affected verification after the last change.
5. Only after the canonical evidence contract supports completion, search the reported `contextFiles` for the exact unchecked checkbox text matching the live pending task description. Change `- [ ]` to `- [x]` only when exactly one reported context file contains exactly one such checkbox. If there is no exact match, more than one match, or the context mapping is otherwise ambiguous, stop blocked without changing task state and report that the current CLI exposes task state but not the configured tracking path.

Do not batch-check unverified work. An unavailable command is not a pass: record the limitation and alternate evidence, and leave any task unchecked when its completion criteria are not established.

## 9. Refresh and continue

Immediately rerun the same store-scoped `openspec instructions apply --change "<name>" --json` command after checking a task or coherent set of tasks. Treat the fresh output as authoritative, reread any changed or newly reported context file, and handle the new state:

- `ready`: show fresh progress and continue with the next pending coherent slice without asking for routine permission.
- `all_done`: stop successfully and report completion.
- `blocked`: stop and report the blocker with the fresh CLI evidence.

Also stop when the user interrupts, a required semantic decision is unresolved, the environment prevents required evidence, an overlapping writer makes the edit scope unsafe, or the debugging contract reaches its blocked condition.

## 10. Report the action result

On `all_done`, report the change, schema, fresh `complete/total` progress, tasks completed in this invocation, files and artifacts changed, commands or measurements run with material results, specialist findings addressed, unavailable checks, and remaining concerns. Suggest the archive action without invoking it.

On a block or pause, report the same known facts plus the exact cause, unchecked work, evidence trail, and what input or artifact correction is required to resume. Never claim the whole change passes from a partial command or a specialist's report.
