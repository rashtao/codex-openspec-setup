---
name: openspec-propose
description: "Create a new OpenSpec change and generate every planning artifact transitively required for implementation in one accelerated, schema-driven workflow. Use when the user wants to turn a clear change idea into a complete proposal, specifications, design when applicable, and implementation tasks without starting implementation."
---

# Propose a Complete OpenSpec Change

Create one change, follow its active schema, and drive every implementation prerequisite through its owning planning skill. “One workflow” means continuous orchestration with pauses only for critical ambiguity, material user authority, or a mandatory child-skill decision; it does not weaken artifact analysis, validation, or independent reviews.

Never implement code, start apply, archive, commit, or delete an existing change from this workflow.

## Codex Orchestration Contract

Use `update_plan` from root selection through the final readiness gate. Keep exactly one step `in_progress`; after status is available, represent the required artifact set in dependency order and update it after every artifact.

An owning artifact skill may replace the shared plan with its own mandatory phases. Before entering it, retain the parent artifact-state ledger. After it returns, rebuild the parent plan from fresh status rather than assuming the previous plan survived.

Keep the main orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `high` reasoning. Implementer and fixer agents use `gpt-5.6-terra` with `medium` reasoning, but this planning-only workflow must not dispatch them.

Artifact-specific skills own their research, questions, writing, validation, and mandatory reviewer dispatch. Do not spawn duplicate artifact authors or reviewers from this orchestrator. When an owning skill dispatches:

- use `spawn_agent` with its required model/reasoning and `fork_turns: "none"` or a positive recent-turn count; model overrides cannot use a full-history fork;
- provide a complete bounded contract because agents do not inherit all context;
- use `send_message` for missing context or active-scope correction;
- use `followup_task` only for a genuinely new bounded assignment to an idle agent, never to repeat a single-shot review;
- use `wait_agent` for terminal results and inspect cited files and the shared worktree before accepting them.

Run artifacts sequentially. Their dependency and potential file overlap make parallel authoring unsafe.

## 1. Resolve Input and Planning Root

Run `openspec --version`. If unavailable, report that the CLI is required and stop without inventing installation steps.

Require a clear, cohesive change description. If the user provided only a name, ask what behavior or outcome should change. If the request clearly contains independent outcomes with separate release or validation stories, recommend the smallest first change and ask which to pursue before creating anything.

Derive a stable kebab-case name when none is supplied. Use an explicit user-supplied name unchanged unless the CLI rejects it. If the description supports several plausible names, ask one direct naming question; otherwise announce the derived name and proceed.

Resolve one root for the entire workflow:

- If the user names a registered store, run `openspec store list --json`, resolve its exact id, then run `openspec list --store <id> --json` to obtain that store's `root.path`. Retain `--store <id>` on every store-aware command.
- Otherwise run `openspec list --json` and use `root.path`.
- If no root exists, explain that a project must be initialized and ask permission. Only after approval run `openspec init . --tools codex --no-animation`, without `--force`, then require `openspec list --json` to resolve a root.

Read `<root.path>/openspec/config.yaml` or `config.yml` and applicable `AGENTS.md` files. Treat project context and rules as constraints for owning artifact skills, never text to copy into artifacts.

If the user explicitly requests a non-default schema, run `openspec schemas --json` from the resolved root path, verify the id, and pass `--schema <id>` when creating the change. Otherwise let the project default resolve.

## 2. Create or Safely Resume the Change

Run `openspec list --json` with the selected store flag and check for an exact active-name collision.

- No collision: create the change with `openspec new change "<name>" --json`, adding schema/store flags when applicable. Require valid JSON and a concrete returned change path.
- Collision: ask whether to choose a new name or resume the existing change. Recommend a new name when the existing intent is unclear. Do not overwrite, rename, or delete it.
- Resume selected: run status first and preserve every existing artifact. If all apply prerequisites already exist, skip directly to final validation. If the user wants to revise completed artifacts rather than fill missing ones, hand off to `openspec-update-change` instead of silently rewriting them.

Immediately run:

```bash
openspec status --change "<name>" --json
```

Require a zero exit status and valid JSON. Use `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `applyRequires`, `artifacts`, and `nextSteps`; never assume the default artifact names or paths.

If artifact work later pauses or fails, keep the created change intact and report its exact root and current next step. Do not clean it up automatically.

## 3. Compute the Required Artifact Set

Build a map from each `artifacts[]` id to its `requires[]` edges. Starting with every id in `applyRequires`, recursively include all dependencies. This transitive closure—not every schema artifact and not only the direct apply ids—is the required set.

If `applyRequires` or any `requires` edge names an artifact absent from the status graph, stop and report the invalid schema contract.

Track each required artifact as one of:

- `done`: concrete output already exists;
- `skipped`: status or instructions explicitly mark it skipped, such as specs under `skip_specs: true`;
- `conditional-skip`: its own instruction says it is optional and the stated applicability conditions are demonstrably false;
- `missing`: it must be created.

Never infer a skip from artifact size or convenience. Record the instruction evidence and reason for every conditional skip. A status of `done` proves file existence only, not semantic validity; final validation remains mandatory.

## 4. Create Required Artifacts in Dependency Order

Repeat until every artifact in the required set is `done`, `skipped`, or explicitly `conditional-skip`:

1. Refresh `openspec status --change "<name>" --json`.
2. Select a missing required artifact whose dependencies are satisfied by one of the three completed states above. Prefer the CLI's returned artifact order when several are eligible.
3. Fetch its contract:

   ```bash
   openspec instructions <artifact-id> --change "<name>" --json
   ```

4. Require valid JSON whose `artifactId` matches the selected id. Retain that exact id with the complete fetched contract: `schemaName`, `changeDir`, `template`, `instruction`, `context`, `rules`, `dependencies`, `outputPath`, `resolvedOutputPath`, `existingOutputPaths`, and optional `references`, `skipped`, and `warning`.
5. Re-read every completed concrete dependency from disk. Resolve paths beneath `changeDir`; expand returned globs, never write to one.
6. If status/instructions mark the artifact skipped, record it and create no file.
7. If the instruction makes it conditional, evaluate only its stated conditions against approved artifacts and project evidence. When none apply, record `conditional-skip` and the evidence; otherwise create it normally.
8. Determine the owning Codex skill from the selected artifact's instruction, template, dependency role, and output contract rather than its id alone. Load and follow it in accelerated mode for standard semantic roles:
   - proposal → `openspec-plus-proposal`
   - specification artifact that produces OpenSpec delta specs beneath `<changeRoot>/specs/` → `openspec-plus-spec`
   - design → `openspec-plus-design`
   - tasks → `openspec-plus-tasks`
9. Announce each owning skill when it begins. Tell it this is the explicitly accelerated all-artifacts flow. Pass the selected store/change, exact selected artifact id, complete fetched contract, and any conditional-skip ledger; the owning skill must stay on that artifact and let the workflow pause only under its documented accelerated-mode gates. This exact handoff is required when a custom schema has several artifacts with the same semantic role.
10. For a custom artifact with no owning skill, follow the dynamic instruction, template, context, and rules directly. Derive a new concrete filename from the instruction or explicit user choice only. Use `apply_patch`, preserve existing user content, and perform any validation/review mandated by that artifact contract.
11. After the owning workflow returns, inspect its evidence and shared files. Re-run status and require the artifact to be `done`, or retain the explicit skip record. Update the plan.

Do not bypass a genuinely missing dependency. The only exception is a downstream artifact whose unresolved CLI dependency is already recorded as `conditional-skip`: fetch its instructions, pass the skip ledger to its owning skill, and proceed only if the CLI returns a valid creation contract. The owning skill must treat only that recorded dependency as intentionally absent and still require every other dependency. This is a schema-authorized optional dependency, not permission to ignore arbitrary blocked state.

If no artifact is eligible while required items remain, report the dependency cycle, missing prerequisite, or unresolved conditional decision and stop.

## 5. Final Validation and Readiness Gate

After the artifact loop, run:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Add the store flag. Require successful exits and valid JSON.

- Validation must contain no errors. Return artifact-attributable failures to the owning planning skill, then rerun the gate. Do not hide unrelated pre-existing failures.
- Recompute the transitive required set from fresh status and ensure every member is `done`, `skipped`, or matches the retained conditional-skip evidence.
- Treat apply instructions as the readiness authority when conditional artifacts exist. `state: "ready"` means implementation can begin; `state: "all_done"` means no implementation tasks remain; `state: "blocked"` means planning is incomplete and must not be reported ready.
- Read every path in apply `contextFiles` and verify it remains within the selected change/root. Confirm task progress is internally consistent, but do not change checkboxes or implement.

Do not use `status.isComplete` alone: an intentionally omitted conditional artifact may remain `ready` while apply is validly ready.

## Final Report

Lead with the actual outcome and include:

- change name, schema, and `changeRoot`;
- artifacts created, already present, CLI-skipped, and conditionally skipped with reasons;
- artifact reviewers and validation outcomes reported by owning skills;
- strict validation result;
- apply state and task progress;
- any unresolved blocker or assumption.

When apply state is ready, say the change is ready for implementation and offer `openspec-apply-change` or a natural-language implementation request. Do not invoke it automatically. When interrupted, report the fresh status/next step and tell the user to ask Codex to continue proposing that exact change.
