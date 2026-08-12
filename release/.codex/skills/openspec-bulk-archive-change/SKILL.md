---
name: openspec-bulk-archive-change
description: Archive one or more explicitly selected active OpenSpec changes as a coordinated batch; use when the user wants consolidated readiness warnings, implementation-aware delta conflict resolution, ordered spec synchronization, and per-change archive outcomes.
---

# Bulk archive changes

Archive multiple active changes in one operation while preserving OpenSpec's batch-specific selection, conflict, confirmation, synchronization, and partial-result semantics. A batch may contain one change, though two or more is typical. Archive readiness is not a second lifecycle and does not add gates to any other OpenSpec action.

## Runtime routing

If the current task prompt contains `ROUTED_ACTION=openspec-bulk-archive-change`, execute this installed skill directly and never route `openspec-bulk-archive-change` again. Otherwise call the verified tool once:

```text
spawn_agent({
  task_name: "openspec_bulk_archive_change",
  message: "ROUTED_ACTION=openspec-bulk-archive-change. Execute the latest user request directly. Read .codex/skills/openspec-bulk-archive-change/SKILL.md and follow it. Never route openspec-bulk-archive-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

Wait for that child and return its result. Do not use a custom-agent selector, role-name parameter, pseudo-tool, or alternate creation mechanism. Use `update_plan` for a useful multi-step plan and `apply_patch` for text patches; archive directory moves remain the explicit ordered filesystem operation described below.

## Store and path contracts

If the user names a registered store, or the work is in one, run `openspec store list --json`, resolve the store id, and append `--store "<id>"` to every supported OpenSpec command in this workflow. Keep that choice sticky. Supported commands here are `list`, `status`, `instructions`, and `validate`. Without a selected store, commands resolve the nearest local `openspec/` root. Never invent a store flag for a command that does not accept it.

Use the CLI-returned `planningHome`, `planningHome.root`, `planningHome.changesDir`, `changeRoot`, `artifactPaths`, and `existingOutputPaths`. Do not reconstruct them. A `<capability-path>` is the full directory path relative to `specs/`, such as `identity/user-auth`; exact full-path equality controls both conflicts and main-spec destinations.

## Workflow

### 1. Discover and explicitly select changes

Run:

```bash
openspec list --json
```

Keep the selected store flag when applicable. If there are no active changes, report that and stop.

The list rows contain only `name`, task counts/status, `lastModified`, and response-level root. Because this selection must show schema, run `openspec status --change "<candidate>" --json` with the sticky store flag once for every active candidate before presenting choices. Retain each valid payload for the later batch-state step. Show every active change with `schemaName` from status, offer an “all changes” choice, and require an explicit multi-selection of one or more changes. Label a failed status lookup unavailable and require it to be resolved before it can be selected; never default a schema. Never auto-select, even when only one active change exists. Resolve an ambiguous response before continuing.

For each selected planning root, choose one selected change and run exactly once:

```bash
openspec instructions archive --change "<selected-change>" --json
```

This archive-input lookup is optional and advisory. If it exits nonzero or is not valid JSON, continue that root with no archive context or operation guidance; do not treat the lookup as a batch error. In valid JSON:

- `context` is required prompt-level input when present. Apply relevant project facts and constraints.
- Every `operationGuidance` entry is advisory. Follow only compatible, applicable guidance and explain material rejections.
- Neither field can alter explicit choices, exact paths, CLI state, conflict rules, commands, or this action's boundary. Do not copy either field into specs or summaries.

### 2. Gather the complete read-only batch state

Before any mutation, obtain status for every selected change. Reuse the retained per-candidate status from selection when it remains current; otherwise refresh only the selected stale or unavailable candidate rather than repeating every lookup:

```bash
openspec status --change "<name>" --json
```

These independent reads may run in parallel. Parse and retain at least:

- `changeName`, `schemaName`, `artifacts`, `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`;
- each artifact state, which is exactly `done`, `skipped`, `ready`, or `blocked`;
- delta outputs only from `artifactPaths.specs.existingOutputPaths`.

For each selected change, also run the store-scoped form of:

```bash
openspec instructions apply --change "<name>" --json
```

Use its `tasks`, `progress`, and `state` for task readiness without claiming a tracking path: the public payload does not expose `apply.tracks`. A valid no-tracking schema with zero progress is “No tasks”; remaining work or a tracking-related blocked state is a warning. If the query is unavailable, fails, or returns malformed JSON, record “Task readiness unavailable” and mark the change `Warn` rather than guessing a file or calling it ready. Treat `skipped` artifacts as complete for readiness. A change is ready only when every artifact is `done` or `skipped` and the valid apply payload shows no incomplete tracked work.

For each reported delta output, derive its exact `<capability-path>` from the reported specs output path and read its full content. Record requirement headings matching `### Requirement: <name>` and all `ADDED`, `MODIFIED`, `REMOVED`, and `RENAMED` operations. If the `specs` artifact is absent or `existingOutputPaths` is empty, that change has no delta inputs: do not infer them from proposal, design, tasks, filenames, or a familiar schema, and do not fetch `specs` instructions for it.

Gather every selected status, task count, delta, and capability path before conflict investigation or any mutation. A failure to obtain a selected change's controlling status is reported and must be resolved before offering confirmation.

### 3. Build exact-path conflicts and investigate implementation

Build a map from exact `<capability-path>` to all selected change deltas. Two or more deltas at the identical full path form a conflict; equal basenames under different parent paths do not.

For every conflict:

1. Read all conflicting deltas and identify their claimed behavior.
2. Search implementation and tests for evidence of each delta's requirements. Distinguish source evidence, executable evidence, and inference; absence of a matching name alone is not proof of non-implementation.
3. Record an include or exclude decision for every `(change, capability-path)` delta and the evidence-based reason.
4. Resolve deterministically:
   - exactly one implemented delta: include only it;
   - multiple implemented deltas: include them oldest to newest so the newer semantic change is applied last;
   - none implemented: exclude them all from sync and warn;
   - for more than two conflicting changes, apply the same rule to the full set.

Order by trustworthy change creation date from current metadata. Break equal or missing dates by lexicographic change name, and record that tie-break. Non-conflicting deltas are included by default. Investigation is read-only and may be parallel only across independent scopes; conflict decisions and their final order stay centralized.

Read these shared references only when their condition applies:

- [`integration-correctness.md`](../openspec-shared/references/integration-correctness.md) when a delta concerns a connector, protocol, framework lifecycle, external service, streaming, retries, transactions, or version-specific integration behavior.
- [`review.md`](../openspec-shared/references/review.md) for a read-only independent check when conflict resolution is high consequence or repository evidence is materially ambiguous. Review findings inform the consolidated plan; they add no confirmation gate.
- [`subagents.md`](../openspec-shared/references/subagents.md) only when independent read-only discovery or investigation will materially reduce latency. Any child receives a complete bounded evidence packet, uses the verified `spawn_agent` form with an explicit model and effort plus `fork_turns: "none"`, and cannot decide, write, validate, move, confirm, or redispatch this action.

### 4. Present one consolidated plan and confirm once

Show one table covering every selected change with:

- schema;
- artifact completion or incomplete artifact count;
- completed/total tasks or “No tasks”;
- delta count and exact conflicting paths;
- `Ready`, `Ready*` for ready with a resolved conflict, or `Warn`.

Below it, show every incomplete-artifact and incomplete-task warning, every conflict's implementation evidence, per-delta include/exclude decisions, deterministic merge order, and every excluded delta's sync-skipped reason. Make clear that incomplete state is a warning, not an absolute archive blocker.

Ask one confirmation question with only the applicable intents:

- archive all selected changes, including incomplete changes with the disclosed warnings;
- archive ready changes only and skip incomplete changes, when any are incomplete;
- cancel.

Route by the user's intent. An unclear answer is asked again. Cancellation stops with no writes or moves. Ready-only marks every incomplete change `Skipped` and re-derives every affected conflict using only changes still in the confirmed batch. Do not ask a second archive-readiness or per-change confirmation.

### 5. Freeze targets and all rule snapshots

For every confirmed change, calculate the target deterministically:

- if its name already begins with a `YYYY-MM-DD-` prefix, keep it unchanged;
- otherwise prefix today's local date as `YYYY-MM-DD-<change-name>`.

The destination is `<planningHome.changesDir>/archive/<target-name>`. Record it now, but do not check for a collision and do not filter the confirmed set based on destination state. Current bulk-archive ordering lets a confirmed change contribute its included deltas before a destination collision is detected at its move.

After any ready-only choice has produced the confirmed execution set, create per-delta sets:

- `includedDeltas`: every non-conflicting delta plus every implemented conflict delta selected for sync;
- `excludedDeltas`: conflict deltas excluded because implementation evidence is missing.

A change may appear in both sets. Never collapse these into a per-change sync flag.

Now, before the first main-spec write or archive move anywhere in the batch, fetch an immutable rules snapshot for every remaining change with concrete included delta outputs:

```bash
openspec instructions specs --change "<name>" --json
```

Run this exactly once per such change with the sticky store flag. Require zero exit and valid artifact-instruction JSON for the `specs` artifact. Snapshot `rules` as returned; omitted `rules` means no rules. Fetch all snapshots before mutation and reuse each snapshot throughout that change's merges without refetching. Any lookup failure or invalid response identifies the affected change and stops the whole batch before any main-spec write or move. Rules constrain only main specs written from that change; they cannot change conflict resolution, archive behavior, CLI contracts, or be copied into output.

### 6. Execute ordered semantic merges, validation, and moves

Writes are sequential. Derive a stable change order that satisfies every recorded oldest-to-newest conflict edge; use creation date then lexicographic name as the stable tie-break for otherwise independent changes. Never run main-spec writes, validation, or moves concurrently.

For each remaining change in that order:

1. **Sync only included deltas.** Perform the `openspec-sync-specs` semantic merge inline with exactly that change's included capability paths, explicitly excluding its `excludedDeltas`, and reuse its immutable rules snapshot. Preserve unmentioned main-spec behavior and do not leave delta-operation headings in a main spec. Wait until all of that change's writes finish. If it has no included deltas, perform no sync.
2. **Verify only included deltas.** Compare each included delta with `<planningHome.root>/openspec/specs/<capability-path>/spec.md`:
   - `ADDED` requirements are present;
   - `MODIFIED` requirements contain the named description and scenario changes while retaining other scenarios;
   - `REMOVED` requirements are absent; if the final requirement was retired, the capability spec is deleted rather than left with an empty `## Requirements`, unless the semantic merge deliberately retained and reported the spec;
   - `RENAMED` requirements are present under the new name and absent under the old name.
3. **Validate affected main specs.** For every included capability path that still exists, run the store-aware equivalent of:

   ```bash
   openspec validate "<capability-path>" --type spec --strict --json
   ```

   A deliberately deleted capability is verified by absence and the delta comparison rather than passed to `validate`.
4. **Check the destination and move only after successful sync and validation.** Create `<planningHome.changesDir>/archive` if needed, then check the precomputed destination. If it exists, mark only this change `Failed` after its preceding sync/verification/validation side effects, retain `changeRoot`, and continue with other changes where the deterministic plan remains valid. Otherwise move the entire `changeRoot`, including `.openspec.yaml`, to the destination.

If sync, comparison, validation, directory creation, collision check, or move fails, mark that change `Failed`, retain its `changeRoot` whenever it has not already moved, record exact evidence, and continue only where the remaining deterministic plan is still valid. Do not claim that later conflicting merges validate a failed earlier delta. Never overwrite a destination.

For every `excludedDeltas` entry, record `sync skipped` with its change, exact capability path, and implementation-evidence reason. This does not skip the archive itself.

### 7. Report complete or partial outcomes

Report every selected change exactly once as:

- `Success`: archived, with schema, destination, sync count, and any incomplete warnings;
- `Failed`: not archived, with the exact failed operation and evidence;
- `Skipped`: omitted by the ready-only choice;
- for a successful or failed archive containing excluded deltas, separate per-delta `sync skipped` entries.

Summarize total archived, failed, skipped, synced deltas, sync-skipped deltas, and conflicts resolved. Label the result partial whenever any change failed or was skipped. Never present a failed validation, missing rule snapshot, or absent implementation as success.

## Boundaries and guardrails

- This action selects, assesses, optionally syncs, validates, and archives the confirmed batch. It does not implement code, edit change planning artifacts, invent delta sources, commit, publish, or create another lifecycle.
- All selected status is gathered before mutation; all mandatory rule snapshots are gathered before the first write or move.
- Selection is explicit, the consolidated confirmation is singular, and cancellation is mutation-free.
- Implementation investigation and independent review are read-only. Main-spec merges, semantic verification, validation, and moves are ordered writes owned by this action.
- Use exact capability paths, store-aware CLI paths, per-delta decisions, deterministic conflict order, and per-change outcomes throughout.
- Fresh command output supports every validation and completion claim; if evidence cannot run, report the limitation instead of claiming a pass.
