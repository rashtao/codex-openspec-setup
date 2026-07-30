---
name: openspec-sync-specs
description: Compare selected OpenSpec change delta specs with their main specs, or merge them when writes are explicitly requested, without archiving the change. Use when the user or archive workflow asks Codex to compare, assess, sync, apply, or reconcile delta specifications with main specifications while preserving unrelated requirements and scenarios.
---

# Sync OpenSpec Delta Specs

Compare selected change deltas with main specs, and when explicitly authorized apply them as an idempotent, store-aware semantic merge. Edit only the selected main spec targets. Never archive, move, rename, or modify the active change from this workflow.

## Operating contract

- Discover delta inputs from the concrete `existingOutputPaths` of the status-reported artifact or artifacts that own files beneath `<changeRoot>/specs/`. Retain each exact artifact id; never assume it is `specs` or discover extra deltas outside status output.
- Preserve a caller-supplied subset exactly; never widen it to every delta.
- Read every selected delta and current main target before planning any write.
- Preserve main-spec content, requirement order, scenarios, and non-requirement sections not changed by a delta.
- Stage and inspect every selected merge before writing any target. A failure in one capability blocks the whole batch.
- Keep the change active. Do not run archive or edit delta specs to make a merge pass.
- Use `apply_patch` for all writes and never commit.

Use `update_plan` for three phases: resolve and validate inputs; prepare all merges; apply, validate, and verify. Keep one step `in_progress` while work remains.

## Codex routing and delegation

Keep the main orchestrator and every planning, design, specification, comparison, or review agent on `gpt-5.6-sol` with `reasoning_effort: high`. A delegated merge implementer or fixer uses `gpt-5.6-terra` with `reasoning_effort: medium`.

Run directly unless delegation materially helps a large merge. If delegated:

- Call `spawn_agent` with `fork_turns: "none"`, the required model and reasoning effort, and a bounded task name. Model overrides cannot use a full-history fork.
- Supply the working directory, selected store/root, change name/root, exact read-only delta paths, exact writable main targets, operation plan, artifact-rule snapshots, validation commands, prohibition on archive/change edits/commits, and required return fields: status, files changed, operations applied, checks run, warnings, and unresolved mismatches.
- Use `send_message` only for missing context or scope correction. Use `followup_task` only for a distinct bounded repair after inspecting a terminal result.
- Use `wait_agent` until the agent returns a terminal result. An archive caller must not move the change while sync or repair work is running.
- Inspect the shared worktree and rerun verification in the main agent; never accept a report alone.

Use `gpt-5.6-sol` high for any separate read-only semantic reviewer. Use `gpt-5.6-terra` medium for an agent that edits main specs or repairs a failed merge.

## Comparison versus write mode

Default to read-only comparison mode when the user asks to compare, assess, review, or explain reconciliation without explicitly authorizing writes. Also use it when the request is ambiguous: ask whether to apply the staged merge, and make no write unless the answer is explicit. Continue through Phases 1 and 2, report the staged per-capability operations, conflicts, validation findings, and whether each target is already synced, then stop before `apply_patch`.

Enter write mode only when the user explicitly asks to sync, apply, update main specs, or perform reconciliation as a mutation, or when the archive workflow supplies the user's explicit sync choice. The selected mode does not weaken input validation or semantic comparison.

## Phase 1: Resolve and validate inputs

### Select the root and change

Reuse the store and change selected by a calling archive workflow. Otherwise, if the user names a registered store, run `openspec store list --json`, resolve its exact id, and append `--store <id>` to every store-aware command below. Keep that root for the whole operation.

Resolve the change from explicit input or unambiguous conversation context. Otherwise run `openspec list --json`, auto-select only when exactly one active change has delta specs, and ask the user directly when several candidates remain. Announce `Using change: <name>` and allow the user to name a different change.

Run and require zero exit status plus valid JSON:

```bash
openspec status --change "<name>" --json
```

Record `schemaName`, `planningHome.root`, `changeRoot`, `artifactPaths`, `artifacts`, and `actionContext`. Stop if the returned change/root differs from the selection.

Build the owned delta set dynamically:

1. For every artifact id, inspect only its concrete `existingOutputPaths` and retain files strictly beneath `<changeRoot>/specs/`.
2. Record each path with its exact artifact id. Reject a path claimed by multiple artifacts, a non-concrete or unreadable path, any path outside the specs root, or an existing file under that root that cannot be assigned unambiguously from status output.
3. Honor a status-reported `skipped` specification artifact when `skip_specs: true` is active. If any delta file coexists with that marker, stop on the conflict rather than treating the artifact as empty.

If the owned set is empty, report `No delta specs` and stop without fetching artifact instructions or writing. Do not assume a specification artifact id.

If the caller supplied path/artifact-id pairs, paths, or capability ids, normalize them against the owned set and select only exact, unambiguous matches. Reject a mismatched artifact id, missing, outside-root, duplicate, or empty selection. Archive-supplied exclusions are authoritative.

Run and parse the JSON result even when validation reports invalid:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
```

Always block on invalid metadata, a `skip_specs: true` conflict, unreadable inputs, or findings attributable to a selected delta. For a narrowed selection, findings attributable only to explicitly excluded deltas do not widen or block the selected sync; report them as excluded-delta warnings. Report unrelated proposal/artifact findings separately. If a finding cannot be mapped confidently to a selected or excluded source, stop rather than ignore it.

### Resolve capabilities and main targets

For each selected delta path:

1. Require a concrete readable `spec.md` beneath `<changeRoot>/specs/`, not directly in that root or inside a dot-directory.
2. Derive the capability id from its directory path relative to `<changeRoot>/specs/`; preserve nested ids such as `platform/session-layout`.
3. Set the target to `<planningHome.root>/openspec/specs/<capability-id>/spec.md`.
4. Require lexical and resolved paths to remain inside their expected roots. If a symlink resolves outside the selected planning root, stop.

Reject two selected deltas that resolve to the same capability or target.

### Load each specification-artifact rule snapshot once

For every distinct artifact id represented by the selection, use exactly one rule snapshot. If an archive caller supplied snapshots, require each to identify the same change/root and its exact artifact id and to contain `rules` as an array or omit it. Reuse them without another lookup.

For each artifact id without a caller-supplied snapshot, run once:

```bash
openspec instructions <spec-artifact-id> --change "<name>" --json
```

Stop before any main-spec write on non-zero status, invalid JSON, wrong change/root/artifact id, `skipped: true`, or malformed rules. Omitted `rules` means none. Associate each snapshot only with deltas owned by that artifact. Rules constrain the content and form of rebuilt main specs; they cannot alter selected paths, roots, CLI gates, or workflow steps, and their text must not be copied into specs or summaries.

## Phase 2: Prepare every merge

Read every selected delta and existing main target. Capture the exact original content and a checksum for each existing target; record non-existent targets separately. Do not write yet.

Parse real Markdown structure only—ignore apparent headers inside fenced code blocks or HTML comments. Main specs must contain no delta-operation headers, and every requirement must live beneath one `## Requirements` section. Stop on an invalid main structure.

Preflight each delta before applying operations:

- Require at least one ADDED, MODIFIED, REMOVED, or RENAMED operation.
- Reject duplicate requirement names within an operation section.
- Reject a requirement present in conflicting sections.
- Reject duplicate rename sources or targets, an ADDED name colliding with a rename target, and a REMOVED name colliding with a rename source, including case/whitespace near-misses.
- When a rename and modification affect the same requirement, require MODIFIED to use the new name.

Apply operations in this order to the staged main content:

1. **RENAMED**
   - Source exists and target does not: rename the header, preserving the whole block.
   - Source absent and target present: treat as already synced unless a case/whitespace near-miss source remains.
   - Both absent, or both present: stop with a conflict.
2. **REMOVED**
   - Existing exact requirement: remove its whole block.
   - Absent exact requirement: treat as already synced with a warning; a case/whitespace near-miss is an error.
3. **MODIFIED**
   - Require the exact requirement after rename/removal processing.
   - Treat the delta block as the complete replacement. Require every current scenario, including duplicate-name multiplicity, to remain in the delta; otherwise stop and report that the delta must be refreshed.
   - Identical normalized content is already synced; otherwise replace the whole block.
4. **ADDED**
   - Absent requirement: append it after existing requirements.
   - Identical existing block: already synced.
   - Existing block with different content: stop; do not silently reinterpret ADDED as MODIFIED.

For a new main capability, require at least one ADDED operation. MODIFIED or RENAMED is an error; REMOVED is a warned no-op. Create:

```markdown
# <capability-id> Specification

## Purpose
<safe delta Purpose verbatim, otherwise the exact fallback below>

## Requirements

<ADDED requirement blocks>
```

The fallback is `TBD - created by archiving change <name>. Update Purpose after archive.` Use a delta `## Purpose` only to seed a new capability. Existing main Purpose is authoritative; warn when a differing delta Purpose is ignored. If a new Purpose is empty, only comments/code, structurally unsafe, or too brief for strict validation, use the fallback and report it.

Preserve original main requirement ordering where possible, append new requirements deterministically, preserve all unrelated sections, and normalize only line endings/spacing needed for valid structure. Introduce no delta headers or placeholders other than the explicit new-capability Purpose fallback; preserve and report any unrelated placeholder that already existed instead of silently rewriting it.

Apply each delta owner's artifact rules to its staged result. Before any write, verify every selected delta has one staged target and every staged target still has the checksum captured at read time. A concurrent change blocks the batch.

## Phase 3: Apply, validate, verify, and report

In comparison mode, report the complete staged operation/no-op summary and any conflicts, state that no files were changed, and stop here. Do not call `apply_patch`, dispatch an editing agent, or imply that synchronization occurred.

In write mode, apply all staged edits with `apply_patch`. Then validate every affected capability:

```bash
openspec validate "<capability-id>" --type spec --strict --json --no-interactive
```

Append the selected store flag. If any validation fails, restore every existing target from its captured content and delete each newly created target with `apply_patch`, but only if the files still match this workflow's staged writes; otherwise stop and report the concurrent-change conflict instead of overwriting it.

After validation, independently re-read every selected delta and main target and verify:

- ADDED blocks are present exactly.
- MODIFIED descriptions and scenarios match the complete delta block and unrelated requirements remain.
- REMOVED requirements are absent.
- RENAMED requirements exist only under the new name.
- Existing Purpose and unrelated sections are preserved.
- Reapplying the same operations would produce no diff.

For a complex merge, this semantic verification may be delegated read-only to `gpt-5.6-sol` high using the Codex contract above, but the main agent must inspect its evidence. Any mismatch triggers the same guarded rollback and blocks success.

Report:

- change, schema, selected root, and selected versus intentionally excluded deltas;
- each capability and target created/updated/already synced;
- counts of added, modified, removed, renamed, and no-op operations;
- ignored existing-capability Purpose values, already-removed warnings, and new Purpose placeholders;
- validation and semantic verification results;
- exact files changed.

Finish with `Specs synced; change remains active`. Do not archive or start implementation automatically.

## Success criteria

Comparison succeeds with an exact caller-selected delta set, valid inputs, a complete staged semantic result, and no writes. Write-mode success additionally requires an explicitly authorized all-or-nothing batch, no lost main-spec content, strict validation for every affected capability, semantic verification of every operation, and an idempotent second application.
