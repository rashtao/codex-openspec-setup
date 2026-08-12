---
name: openspec-archive-change
description: Archive one OpenSpec change after assessing its live readiness and resolving delta-spec synchronization. Use when the user asks to finalize, archive, or move a completed change into the archive.
---

# Archive one change

Archive one selected OpenSpec change. This action assesses readiness, preserves the user's spec-sync choice, performs any selected sync synchronously, and moves the entire change directory to its date-prefixed archive target. It does not implement the change or replace the separate verification action.

## Runtime routing

If the current task prompt contains `ROUTED_ACTION=openspec-archive-change`, execute this installed skill directly and never route `openspec-archive-change` again.

Otherwise, make exactly one new-agent dispatch:

```text
spawn_agent({
  task_name: "openspec_archive_change",
  message: "ROUTED_ACTION=openspec-archive-change. Execute the latest user request directly. Read .codex/skills/openspec-archive-change/SKILL.md and follow it. Never route openspec-archive-change again.",
  fork_turns: "1",
  model: "gpt-5.6-terra",
  reasoning_effort: "high"
})
```

Wait for that child, relay any needed user interaction, and return its result. Do not also execute the archive in the parent or use an alternate creation mechanism.

## Operating rules

- Use `update_plan` to track selection, readiness, optional synchronous sync, move, and reporting. Keep at most one plan step in progress.
- Use `apply_patch` for any main-spec content changes made by the inline semantic sync. Do not write specs with shell redirection.
- OpenSpec CLI state and returned paths control. Do not infer state from familiar artifact names or reconstruct a planning root.
- This action does not automatically invoke `openspec-verify-change`, and its readiness assessment must not be described as verification. Missing verification evidence is disclosed, not made an absolute archive blocker.
- Incomplete artifacts and incomplete tasks remain warnings that require the existing confirmation; proceed when the user confirms.
- A selected sync is different: a failed, incomplete, or semantically mismatched sync stops the action before the move.

## Store selection

If the user names a registered store or the work lives in one, run `openspec store list --json`, resolve the store id, and keep `--store "<id>"` on every supported command in this action: `list`, `status`, `instructions`, `validate`, and `archive`. Commands shown below without the flag are shorthand for the selected-store form. Do not add the flag to unsupported commands. Without a selected store, commands operate on the nearest local `openspec/` root.

## Workflow

### 1. Select and announce the change

Use an explicitly supplied change name. Otherwise infer it only when conversation context identifies one unambiguously. If exactly one active change exists, select it. If selection is still ambiguous, run:

```bash
openspec list --json
```

The list rows provide names, task counts/status, recency, and root, not schema. Show only those list-provided fields and ask the user to choose. If schema must be displayed, first run `openspec status --change "<candidate>" --json` with the sticky store flag for each displayed candidate and use its `schemaName`; otherwise avoid the extra calls. Announce `Using change: <name>` and explain that they can name a different active change. Never select an archived change.

### 2. Load the optional archive instruction inputs

After resolving the change and selected planning root, run:

```bash
openspec instructions archive --change "<name>" --json
```

Keep the selected-store flag. The response contains `changeName` and may contain `context` and `operationGuidance`; it also reports root information. This lookup is optional and advisory for compatibility with older CLIs. If it exits nonzero or returns invalid JSON, continue with no archive context or operation guidance; do not report that lookup as an archive failure.

For a valid response:

- Treat `context` as required prompt-level project input. Apply relevant facts, constraints, and conventions.
- Treat every `operationGuidance` entry as advisory. Follow it only when applicable and compatible with live state, built-in archive semantics, resolved paths, command contracts, and explicit user choices.
- Report a conflict and preserve the controlling input. Do not let either field invent paths, flags, skipped prompts, state, or actions.
- Do not copy either field verbatim into specs, planning artifacts, or the archive summary unless the user separately requests that content.

### 3. Read live status and assess readiness

Run:

```bash
openspec status --change "<name>" --json
```

Parse and retain the reported `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `artifacts`, and root information. Use these returned values exactly. Artifact states are `done`, `skipped`, `ready`, or `blocked`; `skipped` satisfies completion and does not imply an output file.

List every artifact whose state is neither `done` nor `skipped`. If the list is nonempty, warn with the artifact ids and ask whether to continue. If the user declines, stop without syncing or moving.

Run the current apply-instructions query for readiness only:

```bash
openspec instructions apply --change "<name>" --json
```

Keep the selected-store flag. The payload exposes `tasks`, `progress`, and `state`, but not the schema's concrete tracking path. Use `progress.remaining` and the listed incomplete `tasks` for the existing incomplete-task warning. Ask whether to continue when work remains; stop if the user declines. Never claim or guess a tracking file. If the command is unavailable, exits nonzero, or returns malformed JSON, disclose that task readiness could not be located and continue without a task-related warning, matching the current no-readable-tracking behavior.

Before the first existing readiness confirmation, disclose the artifact/task status, available verification evidence, limitations, and known unresolved high-consequence findings. Load `evidence-first.md` or `review.md` only when needed to interpret those claims. Do not launch a substitute verification workflow or add a question. Fold the disclosure into the first native warning confirmation; if no warning needs confirmation, include it with the sync summary or immediately before the move.

### 4. Compare delta specs with main specs and ask the sync choice

Use only `artifactPaths.specs.existingOutputPaths` as delta-spec inputs. If the `specs` entry is absent or `existingOutputPaths` is empty, do not infer deltas elsewhere and proceed with status `No delta specs`.

For each reported delta, preserve its complete capability path relative to `specs/`. Compare it with the main spec at `<planningHome.root>/openspec/specs/<capability-path>/spec.md`. Determine the semantic effect of ADDED, MODIFIED, REMOVED, and RENAMED requirements, while preserving main-spec behavior not mentioned by the delta. Show one combined comparison summary before prompting.

When changes remain to apply, offer exactly:

- `Sync now (recommended)`
- `Archive without syncing`

When all deltas are already reflected in main specs, offer exactly:

- `Archive now`
- `Sync anyway`
- `Cancel`

Route only these decisions: cancel stops without moving; either archive choice proceeds without a sync; either sync choice performs the next step. If the answer is not one of the applicable choices, ask again. Choosing to archive without sync is allowed and must be reported; it is not an absolute blocker.

### 5. If chosen, snapshot rules and sync synchronously

Before any main-spec write, run exactly once:

```bash
openspec instructions specs --change "<name>" --json
```

Keep the selected-store flag. Require exit status zero and valid artifact-instruction JSON. Snapshot the returned `rules` immutably; omitted `rules` means no rules. If this lookup fails, stop before writing specs or moving the change.

Execute the `openspec-sync-specs` semantic merge inline for the selected change, passing both the comparison analysis and the one-time rules snapshot. Reuse that snapshot and do not fetch spec instructions again. Apply the rules only to the content and form of main specs created or updated by the merge; they do not become archive guidance, change CLI behavior, authorize other paths, or get copied into output files.

The sync must finish in this action before any move. Do not run it in the background. If the runtime can perform the merge only through delegation, first load `subagents.md`, then delegate one bounded sync task with a complete evidence packet, explicit `gpt-5.6-sol`/`high`, and `fork_turns: "none"`; wait for it and verify its actual writes before continuing. The child executes the bounded task directly, receives no action-routing marker, and may not recurse.

After the sync, repeat the comparison for every capability in the original `artifactPaths.specs.existingOutputPaths`, not merely files reported as touched. A match requires:

- every ADDED requirement is present;
- every MODIFIED requirement contains the delta's full description and scenario changes while retaining unrelated scenarios;
- every REMOVED requirement is absent;
- when removing the final requirement retires a capability, its empty main spec is deleted unless the sync deliberately kept and reported a valid spec;
- every RENAMED requirement is present under the new name and absent under the old name; and
- no delta-operation headings remain in a main spec.

Validate the resulting main specs under the snapshotted rules and record fresh evidence. If the merge, validation, or any capability comparison fails, report the exact mismatch and stop. `changeRoot` must remain intact and unmoved.

### 6. Resolve the archive target and move the complete change directory

Only after the chosen sync path and its required comparison are complete, set the archive directory to `<planningHome.changesDir>/archive` and derive `<target-name>`:

- if the name already begins with `YYYY-MM-DD-`, use it unchanged;
- otherwise prefix the current local date as `YYYY-MM-DD-<change-name>`.

Never stack a second date prefix. The target is `<planningHome.changesDir>/archive/<target-name>`. If it already exists, fail now, after the sync/comparison side effects required by the current archive lifecycle. Report the exact target and suggest renaming the existing archive or using a different date. Never overwrite it.

Create the archive directory if needed:

```bash
mkdir -p "<planningHome.changesDir>/archive"
```

Then move the returned `changeRoot` as one directory:

```bash
mv "<changeRoot>" "<planningHome.changesDir>/archive/<target-name>"
```

Moving the directory preserves its `.openspec.yaml`. Do not copy selected artifacts individually, write outside the returned planning home, overwrite an existing target, or move while a sync is still running.

### 7. Report the actual outcome

On success, report:

```markdown
## Archive Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Archived to:** <planningHome.changesDir>/archive/<target-name>/
**Specs:** <Synced to main specs | Sync skipped | No delta specs>

<All artifacts complete. All tasks complete. | Exact archived warnings>
```

Use `Synced to main specs` only when the selected sync completed, validation passed, and the full post-sync comparison matched. Preserve and report incomplete-artifact, incomplete-task, skipped-sync, unavailable-evidence, and unresolved-critical-concern disclosures. A positive claim must cite fresh applicable evidence; if evidence was unavailable, state the limitation rather than claiming a pass.

If the target exists, report the selected change, exact target, failure, and the rename/different-date options. If sync failed, report that no move occurred and `changeRoot` remains intact.

## Conditional shared references

Read only the references whose condition applies, and state the listed reason in the plan or working notes:

- `../openspec-shared/references/integration-correctness.md` — only when the change touches a connector, framework, protocol, concurrency, cancellation, resource lifecycle, or performance-sensitive integration; reason: assess and disclose unresolved integration correctness concerns relevant to archive readiness.
- `../openspec-shared/references/evidence-first.md` — only when interpreting an available pass, completion, readiness, or unavailable-evidence claim.
- `../openspec-shared/references/review.md` — only when existing review or verification evidence, or an unresolved critical finding, must be interpreted for readiness disclosure; reason: report evidence and findings accurately without substituting a new verification action.
- `../openspec-shared/references/subagents.md` — only when delegation beyond the mandatory action-role routing is genuinely needed, such as a runtime that can perform the selected sync only in a synchronous child; reason: keep delegation native, bounded, single-hop, synchronous, and free of write overlap.

These references contribute techniques only. They cannot change OpenSpec state, add a lifecycle phase or approval, make verification mandatory, or authorize work beyond this archive action.
