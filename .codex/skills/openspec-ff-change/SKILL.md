---
name: openspec-ff-change
description: "Fast-forward an OpenSpec change through every planning artifact required for implementation. Use when the user wants to create or safely resume a change and generate its proposal, delta specs, design when applicable, and tasks in one accelerated, schema-driven workflow without starting implementation."
---

# Fast-Forward an OpenSpec Change

Create one change and drive every transitive apply prerequisite to readiness. Keep the full analysis, validation, and review gates of each artifact-owning skill; accelerated mode removes only routine approval pauses.

Do not implement code, start apply, archive, commit, delete a change, or rewrite an existing completed artifact from this workflow.

## Codex Orchestration

Run the main orchestrator on `gpt-5.6-sol` with `reasoning_effort: high`. Use `update_plan` from root selection through the final readiness gate, keep exactly one step `in_progress`, and maintain an artifact-state ledger outside child-agent results.

Create artifacts sequentially because they have dependency and file overlap. Delegate a selected standard artifact to one owning planning agent with:

- `spawn_agent`
- `fork_turns: "none"` or a positive recent-turn count, never a full-history fork with a model override
- `model: "gpt-5.6-sol"`
- `reasoning_effort: "high"`

Give the agent a bounded, self-contained contract: working directory, selected store and change, exact artifact id, complete instruction contract, concrete dependency paths, user intent, accelerated-mode directive, allowed edit scope, and required return evidence. Tell it to load and follow the artifact-owning skill. The owning skill controls its research, questions, write, validation, and single independent review; do not dispatch duplicate authors or reviewers.

Use `send_message` only to supply missing context or correct an active agent's scope. Use `followup_task` only for a distinct bounded task to an idle agent, never to repeat a single-shot review. Use `wait_agent` for terminal results, then inspect cited files and fresh CLI state before accepting the result.

All planning, design, specification, research, and review agents use `gpt-5.6-sol` with high reasoning. Implementer and fixer roles use `gpt-5.6-terra` with medium reasoning, but this planning-only workflow must not dispatch an Implementer. A mechanical Fixer is allowed only when an owning skill explicitly permits it; it cannot make planning decisions, and the owning planning agent must inspect its patch.

If child-agent dispatch is unavailable, execute the owning skill inline under the same `gpt-5.6-sol`/high routing and preserve the same handoff and review boundaries.

## 1. Resolve Input and Planning Root

Run `openspec --version`. If unavailable, report that the OpenSpec CLI is required and stop.

Require a clear change description. If the user supplied only a name or the outcome is materially ambiguous, ask directly what they want to build or fix and wait. Derive a stable kebab-case name when none is supplied; keep an explicit user name unless the CLI rejects it.

Resolve one root for the entire workflow:

- If the user names a registered store, run `openspec store list --json`, resolve the exact id, and retain `--store <id>` on every store-aware command.
- Otherwise run `openspec list --json` and use its `root.path`.
- If no root resolves, explain that OpenSpec must be initialized and ask permission before running `openspec init . --tools codex --no-animation`. Never use `--force`.

Read the resolved root's `openspec/config.yaml` or `config.yml` and every applicable `AGENTS.md`. Treat project context and rules as constraints, never artifact content.

If the user explicitly requests a schema, verify it with `openspec schemas --json` and add `--schema <id>` to `new change`. Otherwise use the configured default.

## 2. Create or Safely Resume the Change

Run `openspec list --json` with the selected store flag and check for an exact active-name collision.

- With no collision, run `openspec new change "<name>" --json`, adding schema/store flags when applicable. Require zero exit status, valid JSON, and a concrete returned path.
- On collision, ask whether to resume it or choose another name. Never overwrite, rename, or delete it.
- When resuming, preserve completed artifacts. If the user wants to revise them, route to `openspec-update-change` rather than silently editing them.

Run:

```bash
openspec status --change "<name>" --json
```

Add the store flag. Require zero exit status and valid JSON. Retain `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `applyRequires`, `artifacts`, and `nextSteps`; never assume default artifact names or repository-relative paths.

If work later pauses or fails, keep the change intact and report its exact root and fresh next step.

## 3. Compute the Required Set

Map every `artifacts[]` id to its `requires[]` edges. Starting with every id in `applyRequires`, recursively include every dependency. This transitive closure is the required set; leave artifacts outside it unchanged.

Stop on an invalid schema contract when `applyRequires` or any `requires` edge names an artifact absent from the status graph.

Track each required artifact as:

- `done`: concrete output already exists;
- `skipped`: status or instructions explicitly skip it, such as specs under `skip_specs: true`;
- `conditional-skip`: its own instruction says it is optional and the applicability conditions are demonstrably false;
- `missing`: it must be created.

A `done` status proves file existence only; it does not satisfy missing dependencies or semantic validation. Never infer a skip from convenience. Record the instruction evidence and reason for every conditional skip.

Rebuild the `update_plan` artifact steps in dependency order whenever fresh status changes the ledger.

## 4. Create Missing Artifacts

Repeat until every required artifact is `done`, `skipped`, or `conditional-skip`:

1. Refresh status JSON.
2. Select a missing artifact whose dependencies are satisfied by those terminal states. Prefer CLI artifact order when several are eligible.
3. Fetch its exact contract:

   ```bash
   openspec instructions <artifact-id> --change "<name>" --json
   ```

4. Require valid JSON and an `artifactId` matching the selection. Retain `schemaName`, `changeDir`, `template`, `instruction`, `context`, `rules`, `dependencies`, `outputPath`, `resolvedOutputPath`, `existingOutputPaths`, and optional `references`, `skipped`, and `warning`.
5. Re-read every completed concrete dependency from disk, even if seen earlier. Resolve paths beneath `changeDir`; expand readable globs, but never write to a glob.
6. Honor explicit CLI skips without creating files. Evaluate a conditional artifact only against its own stated conditions and approved evidence.
7. Determine the owning skill from the instruction, template, dependency role, and output contract, not the id alone. Use these standard mappings when applicable:
   - proposal intent → `openspec-plus-proposal`
   - delta specs beneath `<changeRoot>/specs/` → `openspec-plus-spec`
   - technical design → `openspec-plus-design`
   - tracked implementation checklist → `openspec-plus-tasks`
8. Announce the owning skill, read its `SKILL.md`, and dispatch the bounded owner contract described above. State that this is the explicitly accelerated all-artifacts flow; the owner must remain on the selected artifact.
9. For a custom artifact without an owning skill, follow its dynamic contract directly. Derive a concrete output only from the instruction or explicit user choice, use `apply_patch`, preserve user content, and perform every mandated validation or review.
10. Inspect the returned evidence and shared worktree. Refresh status and require the artifact to be `done`, or retain its explicit skip record. Update the plan.

Do not bypass a genuinely missing dependency. If a downstream artifact remains CLI-blocked only because a dependency is an evidenced `conditional-skip`, fetch the downstream instructions and proceed only when the CLI still returns a valid creation contract. Pass the skip ledger to its owner; every other dependency remains mandatory.

If no artifact is eligible, report the dependency cycle, invalid prerequisite, or unresolved conditional decision and stop. Ask the user directly only when ambiguity could materially change scope, behavior, architecture, or task coverage.

## 5. Validate Readiness

Run with the selected store flag:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Require successful exits and valid JSON.

- Return artifact-attributable failures to the owning planning skill, then rerun the gate. Report unrelated pre-existing failures without hiding them.
- Recompute the required-set closure from fresh status and verify every member against the ledger.
- Use apply instructions as the readiness authority when conditional artifacts exist. `ready` means implementation can begin, `all_done` means no implementation tasks remain, and `blocked` means planning is incomplete.
- Read each concrete path in apply `contextFiles`, require it to remain inside the selected root/change, and verify task progress is internally consistent. Do not change task checkboxes.

Do not rely on `status.isComplete` alone because an intentionally omitted conditional artifact may remain `ready`.

## Final Report

Lead with the outcome and include:

- change name, schema, and `changeRoot`;
- artifacts created, already present, CLI-skipped, and conditionally skipped with reasons;
- owning-skill review outcomes and fixes;
- strict validation result;
- apply state and task progress;
- any blocker or material assumption.

When apply is ready, say the change is ready for implementation and offer `openspec-apply-change` or a natural-language implementation request. Never start implementation automatically.
