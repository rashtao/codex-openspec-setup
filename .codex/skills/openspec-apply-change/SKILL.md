---
name: openspec-apply-change
description: Implement or continue an OpenSpec change from tracked tasks or an untracked apply instruction. Use when Codex needs to apply a change, execute pending tasks, implement an instruction-defined outcome, or resume partial implementation.
---

# Apply an OpenSpec Change

Implement one OpenSpec change from its tracked tasks or, for a schema without task tracking, from its apply instruction and planning artifacts. Keep implementation scoped to the selected change and continue until complete or genuinely blocked.

## Store and change selection

If the user names a registered OpenSpec store, or the work clearly belongs to one, run `openspec store list --json`, resolve the store id, and append `--store <id>` to every `openspec list`, `status`, and `instructions` command below. Otherwise, let OpenSpec resolve the nearest local `openspec/` root.

Resolve the change name in this order:

1. Use the name supplied by the user.
2. Infer an unambiguous name from the conversation.
3. Run `openspec list --json`; auto-select only when exactly one active change exists.
4. If multiple changes remain possible, ask the user directly to choose from the returned names. Do not guess.

Announce `Using change: <name>` and state that the user can name a different change to override it.

## Codex orchestration contract

Use `update_plan` for this multi-step workflow. Keep exactly one step `in_progress` while work remains, then mark every step completed.

The main orchestrator, planning/design/spec agents, and all review agents use `gpt-5.6-sol` with `reasoning_effort: high`. Implementer and fixer agents use `gpt-5.6-terra` with `reasoning_effort: medium`.

For each delegated task:

- Call `spawn_agent` with `fork_turns: "none"`, the required model and reasoning effort, and a bounded task name.
- Put the complete delegation contract in `message`: working directory; change and slice/task identifiers; exact artifact and source paths to read; allowed edit scope; acceptance criteria; validation commands; prohibition on commits; and the required return fields (`status`, files changed, checks run, failures or blockers).
- Use `send_message` only to supply missing context or correct an active agent's scope. Use `followup_task` when an idle agent must perform a new bounded pass.
- Use `wait_agent` to collect results, remaining responsive with concise progress updates during long waits. Inspect the shared worktree and validation evidence before accepting an agent's report.
- Delegate only independent, well-bounded work. Before parallel dispatch, prove there are no dependency or file collisions and obtain user approval. Otherwise run tasks sequentially. If subagents are unavailable, execute inline with the same gates.

## Workflow

### 1. Inspect status

Run:

```bash
openspec status --change "<name>" --json
```

Read `schemaName`, `planningHome`, `changeRoot`, `actionContext`, and artifact status. Determine which artifact owns the task list instead of assuming `tasks.md` for every schema.

Run `openspec schema which <schemaName> --json` from the selected project/store root, read the returned schema directory's `schema.yaml`, and retain the literal `apply.tracks` value. Treat a non-null value as one relative file path beneath `changeRoot`, never as a glob or set of files; block if it contains glob metacharacters, escapes `changeRoot`, or cannot be mapped safely to a schema artifact. A missing or null `apply.tracks` selects untracked apply mode.

### 2. Load apply instructions

Run:

```bash
openspec instructions apply --change "<name>" --json
```

Parse:

- `state`, progress, pending tasks, and the built-in `instruction`
- `contextFiles`, whose keys and paths vary by schema
- optional `references`, which indexes read-only upstream stores
- optional `context`, which is required project input when present
- optional `operationGuidance`, which is advisory when present

Handle the state before editing code:

- `blocked`: report the missing artifacts. Use `openspec status --change "<name>" --json` to identify the next artifact and `openspec instructions <artifact-id> --change "<name>" --json` to obtain its creation instructions. Ask the user whether to create or update the planning artifact; do not bypass the blocked state.
- `all_done`: in tracked mode, report the complete progress and suggest that the user ask to archive the change. Do not archive automatically.
- `ready`: continue.

In untracked mode OpenSpec 1.7.0 returns `ready` with zero tasks and does not transition to `all_done`. Treat the built-in instruction plus the applicable existing artifacts as the implementation outcome. If that outcome is not bounded and verifiable, ask the user to clarify it before editing.

Treat `context` and applicable `operationGuidance` as prompt-level constraints, not as completion evidence. The user's explicit choice, CLI-controlled state, and built-in instruction take precedence. Report conflicts; do not silently override controlling inputs. Never copy runtime context or guidance into code or planning artifacts unless the user separately requests it.

Treat `references` as read-only upstream context. Fetch only specs relevant to the selected tasks or untracked outcome using the CLI-provided command, identify them when they influence implementation, and never edit their stores from this workflow.

### 3. Read all context

Read every concrete path in `contextFiles`. Follow the CLI output rather than assuming proposal, spec, design, or task filenames. In tracked mode, require the returned task checkboxes to come from the one literal `apply.tracks` file. In untracked mode, create no tracking file and edit no checkbox.

Also read applicable project instructions and the build configuration needed to discover lint, format, test, type-check, and build commands.

Before implementation, show the schema and CLI instruction. In tracked mode also show `N/M tasks complete` and a compact pending-task overview; in untracked mode show the single instruction/artifact-defined outcome and state that no checkbox progress exists.

### 4. Implement pending tasks

Read and follow `openspec-plus-apply` before writing any test or production code; it owns the implementation loop and final review. Read and follow `openspec-plus-tdd` before code is written, whether work is delegated or inline. If either mandatory skill cannot be loaded, state that limitation and apply the fallback below without weakening its gates.

Fallback loop for each pending task/dependency-safe slice, or for the single bounded outcome slice in untracked mode:

1. Identify the exact acceptance scenarios, affected files, dependencies, and scoped validation commands.
2. Implement with strict RED-GREEN-REFACTOR: first add one test and verify it fails for the intended reason; add the minimum production code to pass; rerun it; assess refactoring; then proceed to the next test. Cover every applicable Gherkin scenario.
3. Run a spec-compliance review with `gpt-5.6-sol` high. Fix every blocking contract issue with `gpt-5.6-terra` medium and re-review.
4. Only after spec compliance passes, run an independent code-quality review with `gpt-5.6-sol` high. Fix blocking issues with `gpt-5.6-terra` medium, then restart at spec-compliance review before repeating code-quality review.
5. Run the task/slice lint, format, test, and other applicable checks. Never skip, disable, or ignore a failure.
6. After all reviews and checks pass, in tracked mode immediately replace only `[ ]` with `[x]` on each corresponding checkbox in the CLI-identified tracking file, preserving its `-` or `*` marker, whitespace, identifier, and text. In untracked mode, do not create or modify a checkbox.
7. Continue without asking for routine confirmation.

Any production or test edit invalidates passed reviews and gates for the affected scope. Restart the ordered spec-compliance review, code-quality review, and full slice gate before marking progress. Count any blocking review or failed gate as one failed correction cycle for that slice; stop on the third total failed cycle rather than maintaining separate retry budgets per stage.

Pause and ask the user directly only when requirements are ambiguous, implementation exposes a planning defect, a failure remains blocked after systematic diagnosis, required authority is missing, or the user interrupts. Do not edit proposal/spec/design artifacts from the implementation loop; hand the issue to the appropriate OpenSpec planning workflow.

### 5. Verify and report

After all tracked checkboxes are complete, or after the untracked outcome slice passes, run a whole-change review with `gpt-5.6-sol` high and then the cumulative lint, format, test, type-check, and build gates applicable to all changed files. Any production or test fix at this stage invalidates the affected slice evidence and both whole-change results: rerun that slice's spec-compliance review, code-quality review, and full slice gate before rerunning the whole-change review and cumulative gate. Count every blocking review or failed gate in this repair sequence against one shared whole-change correction counter and stop on the third total failure. Do not claim completion without fresh passing evidence. Do not commit, archive, or invoke a separate verification workflow automatically.

On success, report:

- change and schema
- tracked `N/N` progress and tasks completed in this session, or the completed untracked outcome and `no checkbox tracking`
- files changed
- checks run and their outcomes
- that the change is ready to archive

On pause, report the same current progress plus the concrete blocker, evidence, recommended next planning or implementation action, and how to resume by asking Codex to apply the same change again.

## Guardrails

- Keep changes minimal and traceable to the selected task or untracked outcome.
- Read every CLI-provided context file before implementation.
- Never mark a task complete while relevant tests or checks fail or are skipped.
- Never treat `context` or `operationGuidance` as proof of completion.
- Preserve CLI-controlled blocked/ready/all-done behavior; successful untracked apply remains `ready` and is established by fresh review and validation evidence instead of a nonexistent checkbox transition.
- Never guess through an ambiguous requirement or silently change planning artifacts.
- Never commit or archive unless the user explicitly requests that separate action.
