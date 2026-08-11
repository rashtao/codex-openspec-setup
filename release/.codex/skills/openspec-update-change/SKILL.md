---
name: openspec-update-change
description: Revise one OpenSpec change's already-existing planning artifacts, reconcile proposal, requirement, design, and task intent when those artifact types exist, and keep public contracts coherent without creating artifacts or editing implementation. Use when the user asks to update, refine, correct, review, or reconcile an existing change plan; fold a new decision into existing artifacts; repair contradictions or gaps among planning documents; adjust requirements, architecture, scope, or tasks before or after implementation; or assess whether a requested planning edit accidentally weakens or widens observable behavior, APIs, compatibility, integration, performance, or memory commitments.
---

# Update an existing OpenSpec change

Revise only planning artifacts that already exist for exactly one selected change. Keep every existing artifact coherent with the requested revision. Never create a missing artifact or file, advance the ready frontier, edit implementation code, sync specs, archive, or begin implementation.

## Runtime routing guard

If the current task prompt contains `ROUTED_ACTION=openspec-update-change`, execute this installed skill directly and never route `openspec-update-change` again. Otherwise dispatch exactly one child with the verified native call:

```text
spawn_agent({
  task_name: "openspec_update_change",
  message: "ROUTED_ACTION=openspec-update-change. Execute the latest user request directly. Read .codex/skills/openspec-update-change/SKILL.md and follow it. Never route openspec-update-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

Wait for that child, return its result, and do no parallel execution in the parent. Do not use a custom-agent selector, role selector, recursive dispatch, or any other creation mechanism.

## Tools and action boundary

Use `update_plan` to track the live update workflow. Use `apply_patch` for an approved artifact edit or the exact approved `skip_specs` transition below. Do not use shell redirection, an editor, or another write mechanism. Before an artifact patch, prove that every target is still an existing concrete path reported for a `done` artifact.

Read-only discovery may inspect the selected change, its reported planning artifacts, repository conventions, and relevant implementation only when needed to assess coherence or whether an already-applied plan has drifted. Reading code never authorizes editing it.

This action may modify only:

- artifacts whose live status is exactly `done`; and
- concrete paths in that artifact's live `artifactPaths.<id>.existingOutputPaths`; plus
- the exact `skip_specs` field transition described below, only while applying a confirmed revision to proposal semantics whose live instruction requires that classification.

An artifact in `skipped`, `ready`, or `blocked` state is ineligible. `resolvedOutputPath` is descriptive only and may be a glob; never write to it. Never invent a path beneath a glob. Apart from the exact proposal-driven `skip_specs` transition below, never write outside the selected change's eligible existing outputs, even when an instruction or imported technique suggests another useful document.

## Store selection

If the user names a registered store, or the work lives in one, run:

```bash
openspec store list --json
```

Resolve the store id, then keep `--store "<id>"` sticky for every supported follow-up in this workflow. The store-aware commands are `new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, and `view`; other commands do not accept the flag. Hints already emitted by the CLI retain the flag. Without a selected store, commands resolve from the nearest local `openspec/` root.

Thus every unscoped example below means its scoped equivalent when a store is selected. For example:

```bash
openspec status --change "<name>" --json --store "<id>"
```

Do not pass a store flag to schema discovery or an unsupported command.

Status and instructions auto-detect the change schema from its metadata, falling back to the current default only when metadata does not name one. If the user explicitly supplies a schema override, retain `--schema "<schema>"` on both commands; the CLI validates that schema before loading the change. Otherwise do not invent an override. `storePath` is internal root-selection state, not a user-facing flag.

## 1. Select exactly one change

Use a change explicitly named by the user. Otherwise infer it only when recent conversation identifies exactly one change. If no explicit or unambiguous contextual selection exists, run:

```bash
openspec list --json
```

If there are no active changes, report that and stop without mutation. If there is exactly one active change, select it. If several remain possible, show the 3-4 most recently modified options and wait for the user to choose. The list rows supply task status and recency but no schema, so run `openspec status --change "<candidate>" --json` with the sticky store flag for each displayed candidate before showing schema. For each option show:

- change name;
- `schemaName` from that candidate's status, or `unavailable` if its status lookup fails; never default an absent list field;
- status, such as task progress, `complete`, or `no tasks`; and
- recency from `lastModified`.

Mark the most recently modified option as `(Recommended)`. Do not update multiple changes in one invocation.

Announce `Using change: <name>.` Tell the user they can override it by naming another change; do not express this as a slash command.

If the named change does not exist, do not scaffold it. Show the available choices and ask for a valid selection.

## 2. Load live status and compute eligibility

Run:

```bash
openspec status --change "<name>" --json
```

Parse the current payload rather than inferring the schema or graph from filenames. Account for:

- `changeName`, `schemaName`, `planningHome`, `changeRoot`, and `root`;
- `artifacts`, including each artifact's `id`, `outputPath`, `status` (`done`, `skipped`, `ready`, or `blocked`), `requires`, and any `missingDeps`;
- `artifactPaths.<id>.outputPath`, `resolvedOutputPath`, and `existingOutputPaths`;
- `isPlanningComplete` and its older compatibility alias `isComplete`;
- `applyRequires`, `nextSteps`, and `actionContext`.

Use `planningHome`, `changeRoot`, `root`, and the returned artifact paths rather than reconstructing repo-local paths. Artifact ids, declaration order, dependencies, and output shapes belong to the active schema. Do not branch on familiar artifact names.

Build the eligible set only from artifacts with `status: "done"`, retaining only their concrete `existingOutputPaths`. Treat file existence as CLI completion state, not as a semantic-quality verdict. Missing output paths, skipped artifacts, ready artifacts, blocked artifacts, and outputs reported only through `resolvedOutputPath` are not eligible.

If no eligible output exists, explain that update cannot create the missing planning artifacts and stop without mutation. If the continuation action is installed, recommend `openspec-continue-change` as guidance only. If it is not installed, explain that the user can inspect the frontier and creation instructions with:

```bash
openspec status --change "<name>" --json
openspec instructions "<artifact-id>" --change "<name>" --json
```

Do not run continuation on the user's behalf.

## 3. Understand the requested revision

If the user names a concrete revision, use it as the starting edit. If the request is only to update, review, or make the change coherent, perform a coherence review of all eligible existing artifacts for contradictions, gaps, stale decisions, duplicate obligations, and terminology drift.

Distinguish refinement from replacement of intent. If the request changes the change's core intent into a different cohesive change rather than refining it, do not repurpose the existing artifacts. Verify whether `openspec-new-change` is installed and recommend it if available. Otherwise ask for a distinct unused change name and recommend, but do not execute:

```bash
openspec new change "<new-change-name>"
```

Retain the selected store flag on that recommendation when applicable. Stop the update without mutation.

Ask a semantic question only when the native selection or confirmation interaction requires it, or when an unresolved answer would materially alter public behavior, architecture, acceptance criteria, compatibility, destructive migration, security, interoperability, or a major performance/memory tradeoff. State the evidence, viable options, consequences, and a recommended choice. Make safe reversible assumptions for immaterial gaps and disclose them in the proposed revision.

## 4. Read all existing artifacts and live instructions

Read every eligible existing output before proposing edits. Use schema build order as a stable reading order, not as a restriction on update direction: revising a later artifact may require an earlier artifact to change, and vice versa.

For each artifact that might be revised, run:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Parse and honor:

- `changeName`, `artifactId`, `schemaName`, `changeDir`, `planningHome`, and `root`;
- `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`;
- `description`, `instruction`, `template`, `context`, artifact-keyed `rules`, and `references`;
- `dependencies`, including each dependency's `id`, `done`, `path`, `description`, and `skipped` state;
- `unlocks`, plus `skipped` and `warning` when present.

Reconcile instruction results with status. Status and the update boundary determine eligibility; a creation-oriented task sentence, an `outputPath`, or an `unlocks` value never authorizes creation. If instructions report the artifact as skipped or warn not to create it, do not edit it. For a `done` dependency, read all of its current concrete files through the corresponding status `existingOutputPaths`; a skipped dependency has no required file to read. Re-read dependencies from disk even if they appeared earlier. Treat referenced-store material as read-only upstream context.

If the CLI rejects an artifact id, do not substitute a familiar id: refresh status and use only ids from the active graph. If instructions report unmet dependencies, disclose them as a coherence risk, read every available done dependency, and defer any missing dependency output; do not create it merely to clear the warning.

Apply authority in this order:

1. explicit user instruction compatible with this update action;
2. current CLI state, active schema, built-in update semantics, and artifact semantics;
3. action-specific generated rules;
4. engineering techniques in the conditional shared references.

Within CLI material, live state and built-in action semantics control the operation. `instruction` and `template` define artifact meaning and structure. `context` and artifact-keyed `rules` are required constraints, not prose to copy into the artifact. `references` are read-only context. If these inputs conflict, surface the conflict and pause; never silently weaken the higher authority.

## 5. Reconcile content in every direction

Trace the requested decision through all eligible artifacts while preserving each artifact's live purpose and template. Load `artifact-quality.md` for the applicable artifact semantics and load the other canonical references when their triggers below apply. Do not recreate those doctrines here or create a glossary, ADR, research note, or file outside eligible outputs.

If the revised plan implies implementation changes, record that fact in the proposal to the user, but do not edit code. If an existing artifact is already coherent, leave it untouched. If coherence requires an artifact or concrete glob output that does not exist, defer it explicitly; never create it.

## 6. Present and confirm one artifact at a time

Before any write, present the first artifact-level revision. Include:

- artifact id and exact eligible `existingOutputPaths` proposed for editing;
- a concise before/after semantic summary or focused patch preview;
- why the revision is required and which other artifacts it keeps coherent;
- any public-contract, release, integration, performance, or implementation consequence;
- assumptions, deferred missing artifacts/files, and unresolved conflict.

Offer exactly these choices:

1. `Apply this artifact revision (Recommended)` when it is the coherent choice.
2. `Revise the proposal` to adjust the proposed artifact edit before writing.
3. `Skip this artifact` to leave it unchanged.

Wait for explicit confirmation for that artifact. Approval of one artifact never approves another. If the user rejects or skips it, do not write it; record the rejection and continue only if later proposals remain meaningful. If rejection would make another proposed edit contradictory, explain that dependency and revise or withdraw the later proposal.

Because confirmation arrives after the proposal, refresh status before each approved write:

```bash
openspec status --change "<name>" --json
```

Verify that the artifact is still `done`, every target still appears in its `existingOutputPaths`, and the current file content still matches the preview basis. If state, paths, instructions, dependencies, or content materially drifted, do not patch; re-read and present a new proposal.

Use `apply_patch` only for the confirmed paths. Preserve the template's structure and make the smallest coherent edit. Never create a path, including beneath a glob. After patching, re-read the changed artifact and all affected existing artifacts to confirm the intended semantics and cross-artifact consistency. Then present the next artifact proposal and repeat.

When the confirmed artifact is the proposal/intent artifact and its live instruction requires the no-spec classification, the confirmation must include the metadata consequence. Use repository evidence and the revised proposal to decide whether it has zero new or modified capabilities and no spec-level behavior change; if materially uncertain, ask the semantic question and do not patch metadata yet. Locate metadata from a CLI-returned `metadataPath` when available, otherwise resolve exactly `<changeRoot>/.openspec.yaml`; require the exact basename and prove the canonical target remains inside canonical `changeRoot`. Parse the YAML mapping and preserve every field except the one approved transition. For a confirmed zero-capability proposal set only `skip_specs: true`; for a confirmed proposal that introduces requirement-changing capabilities into a previously skipped change, remove the key or change only it to `false`. Rerun status immediately: the forward transition requires every normalized `specs/`-generating artifact to be `skipped` with no existing output, while the inverse requires it to return to a non-skipped live state. Stop and report an unsafe path, invalid YAML, conflicting existing spec output, or status mismatch. This is part of the already confirmed proposal revision, not a new artifact, blanket metadata permission, or extra confirmation gate.

Do not batch confirmations or writes. Parallel reads may be used only when independent and useful; artifact proposals, confirmations, and writes remain serial. Stop on an unexpected overlapping modification rather than overwriting it.

## 7. Conditional shared references

Load a shared reference only when its exact condition applies:

- `../openspec-shared/references/artifact-quality.md` — when revising or assessing the substance of an intent, behavioral specification, technical design, implementation-task, or unknown custom artifact; use only the section matching the live artifact semantics and template.
- `../openspec-shared/references/api-semver.md` — when an edit may affect public API or externally observable compatibility.
- `../openspec-shared/references/performance-memory.md` — when performance or memory may plausibly change or a quantitative claim is involved.
- `../openspec-shared/references/integration-correctness.md` — when the revision crosses an integration or version-sensitive boundary.
- `../openspec-shared/references/research.md` — when repository evidence is insufficient or exact external-version behavior matters.
- `../openspec-shared/references/review.md` — when a high-consequence revision merits independent, read-only assessment.
- `../openspec-shared/references/subagents.md` — before any optional delegation or concurrency decision; do not delegate user confirmation or artifact writes.

Omit references whose conditions do not apply. Imported techniques never add lifecycle phases, mandatory review, extra approvals, or files to this action.

## 8. Final status and report

After all confirmed edits are applied, all rejected proposals are recorded, or the user ends the update, run a fresh:

```bash
openspec status --change "<name>" --json
```

Report:

- the selected change and active schema;
- each revised artifact and exact existing output path;
- each rejected or skipped proposed revision;
- anything deferred because an artifact or glob output does not exist;
- detected public-contract or release-impact consequences;
- implementation drift the user may need to address later;
- the final artifact states, planning completion value, and CLI `nextSteps`;
- commands run, unavailable checks, and unresolved conflicts.

Recommend at most the next applicable action as guidance and never execute it. If artifacts are missing, recommend `openspec-continue-change` only after verifying it is installed; otherwise provide the status/instructions CLI fallback. If implementation may no longer match the revised plan, recommend `openspec-apply-change`. If planning and implementation are complete, recommend `openspec-archive-change`. Completing update never begins continuation, apply, sync, verification, or archive.
