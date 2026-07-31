---
name: openspec-bulk-archive-change
description: Safely archive several OpenSpec changes in one confirmed batch, including completion checks, implementation-aware resolution of overlapping delta specs, verified spec synchronization, and per-change outcome reporting. Use when the user asks to bulk archive, batch archive, or finalize multiple parallel changes.
---

# Bulk Archive OpenSpec Changes

Archive one or more explicitly selected changes from one OpenSpec root. Resolve overlapping delta specs from implementation evidence, synchronize only the accepted deltas, verify them, and let the OpenSpec CLI move each change.

## Operating contract

- Keep the main orchestrator and every planning, design, specification analysis, conflict investigation, or review role on `gpt-5.6-sol` with `reasoning_effort: high`.
- Use `gpt-5.6-terra` with `reasoning_effort: medium` for every delegated implementer or fixer.
- Keep root selection, user questions, confirmation, final verification, and every archive command in the main agent.
- Never auto-select changes, infer consent, edit a delta to make it pass, or commit.
- Preserve every file under each `changeRoot`, including `.openspec.yaml`.
- Treat a batch as one root/store. If the request spans roots, run a separate selection and confirmation for each root.
- Use `update_plan` after selection. Track inspection, conflict resolution, confirmation/preflight, synchronization, archiving, and reporting.

## Codex delegation

Run directly unless bounded delegation materially helps. When dispatching:

- Call `spawn_agent` with `fork_turns: "none"`, an explicit model and reasoning effort, a unique task name, and a complete contract. A model override cannot use a full-history fork.
- Give the working directory, selected root/store, exact read paths, exact writable paths, allowed operations, acceptance checks, no-commit rule, and required return evidence.
- A conflict investigator or semantic reviewer is read-only and uses `gpt-5.6-sol` with high reasoning.
- A spec-merge implementer or fixer may edit only the named main specs and uses `gpt-5.6-terra` with medium reasoning. It must not archive, move, rename, or edit an active change.
- Use `send_message` only to supply missing context or correct scope while an agent is active. After inspecting a terminal result, use `followup_task` only for a distinct bounded repair.
- Use `wait_agent` until a terminal result. Inspect the shared worktree and rerun checks in the main agent; never archive from an agent report alone.

## 1. Resolve the root and select changes

If the user names a registered standalone store, run `openspec store list --json`, resolve its exact id, and add `--store <id>` to every store-aware command. Otherwise use the nearest local OpenSpec root. Keep that selection for the whole batch.

Run:

```bash
openspec list --json
```

Add the store flag when selected. Require zero exit status and valid JSON. If no active changes exist, report that and stop.

Obtain each candidate's schema with `openspec status --change "<name>" --json`; do not assume `openspec list` includes it. Show every active change with its schema and ask the user to choose one or more. Include `All changes`, but never choose it automatically. Wait for an exact, unambiguous answer.

After selection, start `update_plan`. Load current archive inputs once for the selected root using any selected change:

```bash
openspec instructions archive --change "<name>" --json
```

This lookup is advisory. If it exits non-zero or returns invalid JSON, continue silently without runtime context or operation guidance. On success:

- Apply relevant `context` as required project facts, conventions, and constraints across the batch.
- Consider every `operationGuidance` entry, but follow it only when compatible with explicit user choices, resolved paths, CLI results, and this workflow.
- Report conflicts and preserve the controlling input. Do not derive replacement paths, skipped questions, or flags from context or guidance.
- Do not copy context or guidance verbatim into specs, changes, or the final summary unless separately requested.

## 2. Inspect every selected change

Refresh status for each selection:

```bash
openspec status --change "<name>" --json
```

Require zero exit status and valid JSON. Record `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `artifacts`, and the corresponding `lastModified` from the list result. Stop on any selected-name or root mismatch.

Treat artifact statuses `done` and `skipped` as complete. Record every other status as a warning.

### Resolve tracked tasks

Resolve tracking from the selected schema rather than assuming an artifact named `tasks`:

1. From `planningHome.root`, run `openspec schema which <schemaName> --json`. Schema commands do not take `--store`; using the selected planning root as the working directory preserves project-local schema resolution.
2. Require a concrete schema directory and read its `schema.yaml`.
3. If `apply.tracks` is absent or null, record `No tracked task file`.
4. Otherwise require one literal relative file path. Resolve it beneath `changeRoot`, and require both lexical and resolved paths to remain there.
5. Require the file to be readable. Count top-level checkbox lines beginning with `-` or `*` followed by `[ ]`, `[x]`, or `[X]`.

A missing, unreadable, absolute, glob-valued, escaping, or otherwise invalid declared tracker blocks that change from becoming ready. Record completed and total tasks.

### Discover owned delta specs

Do not assume an artifact id named `specs`. For every artifact id:

1. Inspect only its concrete `existingOutputPaths`.
2. Retain readable files strictly beneath `<changeRoot>/specs/` and record each exact owning artifact id.
3. Reject a path claimed by multiple artifacts, a non-concrete or escaping path, or a file under the specs root that cannot be assigned unambiguously from status.
4. If a specification artifact is `skipped` because `skip_specs: true`, require its owned delta set to be empty.

For every retained delta, derive the capability id from its path relative to `<changeRoot>/specs/`, preserving nested ids. Read the file and record its ADDED, MODIFIED, REMOVED, and RENAMED requirement names. An empty owned set means `No delta specs`; do not fetch specification-artifact instructions for it.

## 3. Resolve capability conflicts

Build `capability -> selected changes with an owned delta`. Two or more changes for one capability is a conflict.

For each conflict:

1. Read every conflicting delta completely.
2. Search source, tests, configuration, and migrations for concrete evidence that each delta's behavior is implemented. Requirement and scenario behavior matter more than coincidental names.
3. Record one inclusion or exclusion decision per change and capability, with evidence.
4. If exactly one delta is implemented, include it and exclude the others.
5. If several are implemented, include them in chronological order, older first.
6. If none is implemented, exclude all of them and warn.
7. If evidence is ambiguous or deltas are semantically incompatible, ask the user to decide; do not guess.

Use explicit creation metadata when available, otherwise a `YYYY-MM-DD-` change-name prefix, otherwise `lastModified` as a disclosed proxy. Break equal timestamps deterministically by change name.

Every non-conflicting owned delta is included. Keep decisions per delta: one change may have both `includedDeltas` and `excludedDeltas`.

## 4. Show status and confirm once

Show a consolidated table with change, schema, artifacts, tasks, delta count, conflicts, and status. Mark a change:

- `Ready` when artifacts are complete and the tracked task file is complete or absent.
- `Ready*` when it is ready and has a recorded conflict resolution.
- `Warn` when artifacts or tasks are incomplete or task tracking is invalid.

Below the table, show incomplete-work warnings and each conflict resolution, including sync order and exclusions.

Ask one direct question:

- archive every selected change, accepting shown warnings;
- archive only `Ready` and `Ready*` changes;
- cancel.

Match the answer by intent. An unknown answer requires another question. Cancel means no writes and no moves. For ready-only, record omitted changes as `Skipped`. If removing a change alters a conflict, recompute that conflict using only the confirmed set.

## 5. Preflight the confirmed batch

Before the first main-spec write or archive:

1. Rebuild `includedDeltas` and `excludedDeltas` for the confirmed set.
2. For every distinct owning artifact id represented by an included delta, fetch exactly once:

   ```bash
   openspec instructions <artifact-id> --change "<name>" --json
   ```

3. Require zero exit status and valid artifact-instruction JSON matching the change, root, and artifact id. Omitted `rules` means none. A failed or malformed lookup stops the entire batch before any write or move.
4. Keep each immutable rule snapshot with only the deltas owned by that artifact. Rules constrain rebuilt main specs; they cannot alter paths, conflict decisions, questions, CLI checks, or archive behavior.
5. Compute each expected archive target using the CLI's date rule: keep a leading `YYYY-MM-DD-` change name, otherwise prefix the current local date. If a target already exists, mark that change `Failed` before mutation and remove it from execution. Recompute affected conflicts.

Fetch any newly required rule snapshot introduced by recomputation before continuing. Never fetch the same change/artifact snapshot twice.

## 6. Synchronize and verify included deltas

Process confirmed changes in dependency-safe conflict order. For each change with included deltas:

1. Load and read the `openspec-sync-specs` skill completely, then follow it in write mode for exactly the included delta path/artifact-id pairs.
2. Supply the already-fetched comparison decisions and artifact-rule snapshots. The sync must not fetch those instructions again.
3. Explicitly exclude that change's `excludedDeltas`; never widen the selection.
4. Run synchronously. Do not archive or begin the next dependent conflict merge while sync or repair work remains active.
5. Independently re-read every included delta and main target at `<planningHome.root>/openspec/specs/<capability-id>/spec.md`.
6. Verify ADDED blocks are present, MODIFIED blocks and scenarios match without losing unrelated content, REMOVED requirements are absent, and RENAMED requirements exist only under the new name.
7. Validate every affected capability:

   ```bash
   openspec validate "<capability-id>" --type spec --strict --json --no-interactive
   ```

   Add the selected store flag.

If sync, semantic verification, or validation fails, mark the change `Failed` and leave its `changeRoot` active. Do not verify or sync excluded deltas. Report each excluded delta as `sync skipped` with its recorded reason; this does not skip the archive itself.

## 7. Archive each eligible change through the CLI

For a change whose included deltas are verified, or which has no included deltas, run:

```bash
openspec archive "<name>" --yes --json
```

Add `--skip-specs` whenever the change owns any delta specs. The workflow has already made and verified the per-delta sync decisions; this flag prevents the CLI from reapplying intentionally excluded deltas. For a change with no owned deltas, omit `--skip-specs`.

Add the selected store flag. Never pass `--no-validate`. `--yes` is valid only because the batch confirmation and incomplete-work warning were already handled.

Require zero exit status, valid JSON, and a non-null `archive` result. Record its exact `path`. On failure, record the CLI diagnostic, leave the change active, and continue with independent changes. If a failed change is an ordering predecessor for a remaining conflict merge, stop that dependent branch rather than applying a newer delta out of order.

Track:

- `Success`: archived path returned by the CLI;
- `Failed`: sync, verification, validation, dependency, or archive error;
- `Skipped`: omitted by the user's ready-only choice;
- `Sync skipped`: excluded delta with change, capability, and reason.

## 8. Report

Lead with `Bulk archive complete` or `Bulk archive complete (partial)`. Include:

- successful changes and exact archived paths;
- skipped changes and reasons;
- failed changes and actionable diagnostics;
- delta counts synced and sync-skipped;
- conflict resolutions and applied order;
- incomplete artifact/task warnings the user accepted;
- any main specs synchronized for a change whose later archive command failed.

Do not claim a change was archived unless its CLI result succeeded. Do not claim a delta was synced unless semantic verification and strict capability validation passed.
