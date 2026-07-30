---
name: openspec-archive-change
description: Finalize and archive a completed OpenSpec change, with completion warnings, an explicit delta-spec sync decision, sync verification, and a safe CLI-driven move. Use when the user asks to archive or finalize an implemented OpenSpec change.
---

# Archive an OpenSpec Change

Archive one active change only after resolving its planning root, checking its artifacts and tasks, and deciding whether to sync its delta specs.

## Operating contract

- Treat archiving as a destructive transition: never infer a change when more than one candidate remains, never bypass a required confirmation, and never move a change while a sync is running.
- Use `update_plan` after selecting the change. Keep a short plan covering inspection, the sync decision, and the archive; update it as each stage completes.
- Ask the user direct, explicit questions and wait for the answer. Do not treat silence or an unrecognized answer as consent.
- Keep selection, user prompts, final verification, and the archive command in the main agent.
- Preserve `.openspec.yaml` and every other file under the change root.

## 1. Resolve the planning root and change

If the user names a store, or the work belongs to a registered standalone OpenSpec store, run `openspec store list --json`, resolve the exact store id, and add `--store <id>` to every applicable OpenSpec command below. Without a selected store, commands use the nearest local `openspec/` root. Keep the same root for the entire workflow.

Resolve the change name in this order:

1. Use an explicit name from the user.
2. Use an unambiguous change already established in the conversation.
3. Run `openspec list --json`; auto-select only when it returns exactly one active change.
4. Otherwise show the active changes, including their schema when available, and ask the user to choose.

If there are no active changes, report that and stop. Announce `Using change: <name>` and say that the user can name a different change to override it.

Load current archive inputs before the completion checks:

```bash
openspec instructions archive --change "<name>" --json
```

This lookup is advisory and optional. If it exits non-zero or returns invalid JSON, continue silently with no runtime context or operation guidance. On success:

- Apply relevant `context` as required project facts, conventions, and constraints.
- Consider every `operationGuidance` entry, but follow it only when compatible with this workflow, explicit user choices, resolved paths, CLI results, and command contracts.
- Report conflicts and preserve those controlling inputs. Do not derive replacement paths, skipped prompts, or new flags from context or guidance.
- Never copy context or guidance verbatim into specs, artifacts, or the final summary unless the user separately asks.

## 2. Inspect completion

Run:

```bash
openspec status --change "<name>" --json
```

Require a zero exit status and valid JSON. Record `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, and `artifacts`. Stop if the reported change or root differs from the selection.

Treat artifact statuses `done` and `skipped` as complete. List every other artifact status as a warning.

Resolve task tracking from the selected schema, not from an artifact id. From `planningHome.root`, run `openspec schema which <schemaName> --json`, require a concrete schema directory, and read its `schema.yaml`. When `apply.tracks` is absent or null, record `No tracked task file` and omit the task warning. Otherwise require `apply.tracks` to be one literal relative file path, resolve it beneath `changeRoot`, and require both its lexical and resolved path to remain inside `changeRoot`. Read that exact file and count the top-level checkbox forms OpenSpec 1.7.0 parses: `-` or `*`, followed by `[ ]`, `[x]`, or `[X]`. A missing, unreadable, glob-valued, absolute, escaping, or otherwise unresolvable declared tracker blocks the workflow before any `--yes` archive command; do not let `--yes` suppress the CLI's task safeguard.

If artifacts or tasks are incomplete, combine them into one warning and ask whether to archive anyway. Stop unless the user explicitly confirms. Retain the warning counts for the final summary.

## 3. Assess delta-spec sync state

Discover delta-spec inputs dynamically from `artifactPaths`:

1. For each artifact id, inspect only its concrete `existingOutputPaths` and retain paths strictly beneath `<changeRoot>/specs/`.
2. Require every retained path to be a concrete readable delta-spec file and record the exact owning artifact id. If one path is claimed by multiple artifacts, an output escapes the specs root, or a file under the specs root cannot be assigned unambiguously, stop.
3. Treat an artifact whose status is `skipped` by `skip_specs: true` as intentionally empty. If the marker and any delta file coexist, stop on the conflict.

If no owned delta paths remain, record `No delta specs` and continue without a sync prompt. Do not assume the artifact id is `specs`.

For each concrete delta path:

1. Derive its path relative to `<changeRoot>/specs/`.
2. Compare it with the main spec at `<planningHome.root>/openspec/specs/<same-relative-path>`.
3. Determine the outstanding ADDED, MODIFIED, REMOVED, and RENAMED operations. Preserve main-spec content and scenarios not named by the delta.

Show one combined comparison summary before asking:

- If work remains: `Sync now (recommended)`, `Archive without syncing`, or `Cancel`.
- If every delta is already applied: `Archive now`, `Sync anyway`, or `Cancel`.

Route only an exact, unambiguous answer. `Cancel` stops without moving the change. An unknown answer requires another question.

## 4. Sync and verify when selected

Before any selected sync writes a main spec, run once for each distinct owning specification artifact id:

```bash
openspec instructions <spec-artifact-id> --change "<name>" --json
```

Require a zero exit status and valid artifact-instruction JSON whose `artifactId` matches the requested id. Omitted `rules` means no rules. Retain one immutable rule snapshot per artifact id. Apply a snapshot only to main specs sourced from that artifact; rules cannot alter roots, paths, prompts, CLI checks, or archive behavior, and their text must not be copied into output files.

Load and follow the `openspec-sync-specs` skill for the selected change and all concrete delta paths, supplying each path's exact artifact id, the comparison, and the already-fetched rule snapshots. The sync must reuse those snapshots and must not fetch artifact instructions again.

Run the sync directly unless delegation materially helps with a large merge. If delegating:

- Use `spawn_agent` with `model: "gpt-5.6-terra"`, `reasoning_effort: "medium"`, and `fork_turns: "none"` for the sync implementer or fixer.
- Give it the resolved root/store, change name and root, exact delta and main-spec paths, comparison, rule snapshots, and this boundary: it may edit only the selected main specs and must not archive, move, rename, or edit the change.
- Require a return containing files changed, operations applied, checks run, and any unresolved mismatch.
- Use `send_message` only for missing context or scope correction while the agent is active. After a terminal result, use `followup_task` for a bounded repair pass on the idle agent, then `wait_agent` for the new terminal result. Do not continue to archiving on a partial update or merely because the agent is idle.

If a separate read-only comparison or final semantic review is delegated, call `spawn_agent` with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`. Any dispatched main orchestration, planning, design, specification, or review role uses that same routing; implementation and repair roles use `gpt-5.6-terra` at medium reasoning with `fork_turns: "none"`.

After the sync completes, independently re-read every retained owned delta path and its main target. Verify:

- ADDED requirements are present.
- MODIFIED descriptions and scenarios are present while unrelated scenarios remain intact.
- REMOVED requirements are absent.
- RENAMED requirements exist under the new name and not the old name.

Also validate each affected capability with `openspec validate "<capability>" --type spec --json`, using the selected store flag. If the sync failed, semantic verification differs, or validation fails, report the exact mismatch and stop. The active change must remain unmoved.

## 5. Archive through the CLI

Use the CLI for validation, collision checking, date-prefix handling, store-aware paths, and the move. Never replace this with `mkdir`, `mv`, or direct filesystem deletion.

- After `Sync now`, `Sync anyway`, or `Archive now` for already-synced deltas, run:

  ```bash
  openspec archive "<name>" --yes --json
  ```

  The prior semantic verification guarantees that the CLI merge is idempotent.

- After `Archive without syncing`, run:

  ```bash
  openspec archive "<name>" --skip-specs --yes --json
  ```

- With no delta specs, run `openspec archive "<name>" --yes --json`.

Add the selected store flag. Do not pass `--no-validate`. `--yes` is allowed only because all workflow confirmations have already occurred; it must not substitute for them.

Require a zero exit status, valid JSON, and a non-null `archive` result. On failure, report the CLI diagnostic and stop. In particular, do not rename or delete an existing archive target automatically.

## 6. Report the result

Lead with `Archive complete` and include:

- change name and schema;
- the exact archived path returned by the CLI;
- spec outcome: synced and verified, already synced, sync skipped by user, or no delta specs;
- any incomplete-artifact or incomplete-task warnings accepted by the user.

Do not claim specs were synced unless post-sync semantic verification and validation passed.
