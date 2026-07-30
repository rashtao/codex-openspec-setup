---
name: openspec-update-change
description: Revise existing planning artifacts in an active OpenSpec change and reconcile them with one another without creating new artifacts or editing implementation code. Use when the user wants to update a change's plan, incorporate a new planning decision, repair cross-artifact drift, or review an existing change for coherence.
---

# Update an Existing OpenSpec Change

Revise only planning files that already exist in the selected change. Reconcile accepted edits in every direction across the artifact graph, preserve completed work, and never advance the build frontier or edit implementation code.

## Non-negotiable boundaries

- Use only concrete files in `artifactPaths.<id>.existingOutputPaths`. Never write to `resolvedOutputPath` when it is a glob, create a missing artifact, or invent another file under a glob.
- Never edit source code, tests, generated implementation files, archived changes, main specs, or unrelated changes.
- Never silently change the change's intent, completed task state, or accepted scope. Ask the user when a revision would invalidate an implemented decision or completed task.
- Treat CLI paths/state, explicit user decisions, templates, and rules as controlling inputs. Context and guidance cannot override them and must not be copied into artifacts.
- Use `apply_patch` for edits. Never commit, archive, apply implementation, or create a new change automatically.

Use `update_plan` with four stages: resolve, diagnose, approve and edit, validate and review. Keep one stage `in_progress`.

## Codex routing and delegation

Keep the main orchestrator and every planning, proposal, specification, design, task, research, or review agent on `gpt-5.6-sol` with `reasoning_effort: high`. If any such role is dispatched, call `spawn_agent` with `fork_turns: "none"`; explicit model overrides cannot use a full-history fork.

This workflow does not normally use implementation agents. An exceptional purely mechanical fixer may use `gpt-5.6-terra` with `reasoning_effort: medium` and `fork_turns: "none"`, but it may apply only an already-approved textual correction to exact paths. It must not interpret intent, reconcile artifacts, or choose content.

Every delegation message must include working directory, store/change, exact paths, read/write scope, controlling inputs, the bounded question or edit, evidence requirements, prohibition on commits, and return format. Agents share the worktree but do not inherit context with `fork_turns: "none"`.

Use `send_message` only to supply missing context or correct an active agent's scope. Use `followup_task` only for a genuinely new bounded assignment to an idle agent, never to repeat the single-shot final review. Use `wait_agent` for terminal results and inspect cited files and the shared worktree before accepting a report.

## Phase 1: Resolve the change and edit scope

### Select the store and change

Reuse an already selected planning root when available. If the user names a registered store, run `openspec store list --json`, resolve its exact id, and append `--store <id>` to every store-aware command below.

Resolve the active change from explicit input or unambiguous conversation context. Otherwise run `openspec list --json`:

- auto-select only when exactly one active change exists;
- if none exist, report that and stop;
- if several exist, show 3–4 recent names with their CLI-returned task progress, status, and `lastModified`, then ask the user directly to choose. Do not infer or display a schema from list output, and do not recommend a change solely because it is recent.

Announce `Using change: <name>` and say the user can name another active change to override it.

Run and require zero exit status plus valid JSON:

```bash
openspec status --change "<name>" --json
```

Record `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `artifacts`, and `isComplete`. Stop on a root/change mismatch.

Capture `git status --short` for the change's existing artifact paths. Existing edits belong to the user. If a targeted file was already modified and ownership or desired composition is unclear, ask before writing; never reset or overwrite it.

### Determine mode and request

- Specific edit: treat the user's requested revision as the starting decision, then check every existing artifact for consequences.
- General “update” or “make coherent”: perform a full coherence diagnosis before proposing edits.
- Review/discussion only: remain read-only, run non-mutating validation and the final reviewer, and report findings without applying them.

Use the update-vs-new heuristic before editing. Updating is appropriate when the same problem, outcomes, and capability remain and the user is refining scope or decisions. Recommend a new change when the primary intent/outcome changes, most accepted scope becomes obsolete, or the request is an independently deliverable effort. Explain the tradeoff and let the user decide; do not create the new change.

## Phase 2: Diagnose cross-artifact effects

Read every concrete existing path in `artifactPaths`. Do not assume artifact ids, filenames, schema order, or a one-file artifact. Build order is a reading aid, not a restriction: later artifacts may reveal that earlier ones need revision.

For every artifact that may change, fetch its current contract before proposing a write:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Require valid JSON and retain `artifactId`, `schemaName`, `changeDir`, `resolvedOutputPath`, `existingOutputPaths`, `template`, `instruction`, `context`, `rules`, `dependencies`, `references`, `skipped`, and `warning` when present.

- If `skipped` is true, do not edit that artifact.
- If `existingOutputPaths` is empty, defer it as a not-yet-created artifact. Do not derive a new file from `resolvedOutputPath`.
- Treat referenced stores as read-only upstream context and never edit them.
- Verify instruction paths agree with status and stay within `changeRoot`.

Determine the semantic role from the schema instruction, description, template, and existing content rather than relying only on an id string. Before writing a proposal, delta specification, design, or task artifact, read and follow the corresponding mandatory `openspec-plus-proposal`, `openspec-plus-spec`, `openspec-plus-design`, or `openspec-plus-tasks` skill. Keep this workflow's existing-files-only boundary and accepted revision plan as additional controlling constraints. For a custom artifact without a matching plus skill, follow its CLI template, instruction, context, and rules directly.

Create one reconciliation plan that lists, per concrete file:

- exact requested or coherence repair;
- why it is necessary and which accepted decision it traces to;
- effects on every other existing artifact;
- any missing artifact/file that must be deferred;
- any completed task or implemented behavior that may now be stale.

If the artifacts are already coherent, make no edit and proceed to read-only validation/reporting.

## Phase 3: Approve and edit

Show the reconciliation plan before writing. Ask for explicit approval, allowing the user to accept or reject each listed revision. One answer may approve several files only when every file and change is separately enumerated. Silence or an ambiguous answer is not approval.

If the user rejects a revision, remove it and recalculate dependent revisions; do not write another artifact as though the rejected change occurred.

Apply accepted revisions one artifact at a time under its CLI contract and applicable plus skill. Preserve exact template structure, unrelated content, existing glob files, stable identifiers, and checked task boxes. Do not uncheck, delete, renumber, or repurpose completed tasks automatically. When approved planning makes completed implementation stale, retain the checkbox state and report the mismatch for the user to reconcile through implementation or task planning.

After each artifact, re-read the changed file and compare it with the accepted plan, template, rules, and all other existing artifacts. Do not make an unapproved follow-on edit; add it to a new proposal for user approval.

## Phase 4: Validate and review

Run non-interactively after writes, or as diagnostics in read-only mode:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
openspec status --change "<name>" --json
```

Add the selected store flag. Require valid JSON. Fix only deterministic defects within the approved revision plan. Report pre-existing or unapproved coherence/validation defects instead of silently changing them.

Require both commands to exit successfully and strict validation to report no errors before describing the change as validated or coherent. A parseable failure payload is still a failure.

Dispatch exactly one fresh read-only cross-artifact reviewer with `spawn_agent`, `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`. Provide the exact existing artifact paths, status/instruction summaries, accepted and rejected revisions, baseline worktree status, validation output, and this rubric:

- every accepted revision appears completely and only in approved files;
- proposal intent/scope, behavior requirements/scenarios, design decisions, and task outcomes remain mutually consistent wherever those semantic roles exist;
- no artifact invents behavior, drops an accepted constraint, contradicts another artifact, or exceeds its semantic role;
- every edited file follows its current template, instruction, context, and rules;
- existing completed tasks and unrelated user content are preserved;
- no missing artifact or new glob file was created and no path escaped `existingOutputPaths`;
- implementation drift and deferred frontier work are identified accurately.

Require:

```text
Status: Coherent | Issues Found
Issues:
- [artifact/path and evidence] — [contradiction or omission] — [specific correction]
Advisory:
- [implementation drift, deferred artifact, or non-blocking observation]
```

The reviewer must not edit. Use `wait_agent`; use `send_message` only for missing input or scope correction. Do not redispatch or use `followup_task` for a second review in the same invocation.

If the reviewer finds an issue, verify it against controlling inputs. In read-only mode, report it. In write mode, ask the user before any correction not already covered by the approved plan, apply accepted corrections through the owning artifact skill, and rerun strict validation and status. Do not claim independent approval after post-review edits; report the reviewer result and the subsequent verified corrections separately.

## Report and next step

Report:

- change, schema, and planning root;
- revised files and rejected proposals;
- validation and reviewer outcomes;
- remaining inconsistencies, missing artifacts/files, and implementation drift;
- completed task state preserved;
- the next user-invoked workflow.

If artifacts are missing, suggest asking Codex to continue the same change; when no continue skill is available, cite `openspec status --change "<name>" --json` and `openspec instructions "<artifact-id>" --change "<name>" --json` as the creation inputs. If implementation may be stale, suggest asking Codex to apply or verify the change. If planning and implementation are complete, suggest asking Codex to archive it. Never take those actions automatically.
