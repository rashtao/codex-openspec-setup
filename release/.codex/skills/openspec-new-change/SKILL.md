---
name: openspec-new-change
description: Scaffold a named OpenSpec change and expose its first live ready artifact instructions. Use when the user wants to start a new feature, fix, refactor, tooling, documentation, or other structured change, choose an OpenSpec workflow schema or registered store, or see what the first planning artifact would require without creating that artifact yet.
---

# Start a new OpenSpec change

## Purpose and hard boundary

Create only the OpenSpec change scaffold, inspect its live artifact state, fetch the instructions for the first artifact whose status is `ready`, report the result, and stop.

This action does not create or edit a planning artifact, write to an artifact `outputPath` or `resolvedOutputPath`, implement code, sync specs, validate or archive the change, or continue into another OpenSpec action. A README created with `--description` is additional content rather than the ordinary scaffold, so do not infer that flag from the user's prose. Completion of this action always stops before artifact creation, even when the first instructions are complete and unambiguous.

## One-hop action routing

Run this guard once, before the procedure:

- If the current task prompt contains `ROUTED_ACTION=openspec-new-change`, execute this installed skill directly. Never route `openspec-new-change` again.
- Otherwise, make exactly one dispatch with `spawn_agent({ task_name, message, fork_turns, model, reasoning_effort })`, using `task_name: "openspec_new_change"`, `fork_turns: "1"`, `model: "gpt-5.6-sol"`, and `reasoning_effort: "high"`. The message must be: `ROUTED_ACTION=openspec-new-change. Execute the latest user request directly. Read .codex/skills/openspec-new-change/SKILL.md and follow it. Never route openspec-new-change again.` Wait for that child and return its result; do not repeat its work locally.
- Never replace `spawn_agent` with a custom-agent selector or another creation mechanism, and never allow an action agent to dispatch itself.

## Authoritative procedure

### 1. Establish the requested change

The request must communicate what the user wants to build or fix. If it does not, ask the open-ended question: “What change do you want to work on? Describe what you want to build or fix.” Do not scaffold until the intent is understood well enough to name the change.

Use a name explicitly supplied by the user, or derive a concise kebab-case name from their description. A valid candidate consists of lowercase words or digits separated by single hyphens, with no spaces, underscores, uppercase letters, or leading or trailing hyphen; the CLI remains final authority. If an explicit name is not kebab-case, ask for a valid name rather than silently changing it. If a derived name would be materially ambiguous, present the proposed name and ask; otherwise proceed with the safe derived name.

### 2. Resolve the registered store, if any

A store is a standalone OpenSpec repository registered on the machine. If the user names a store or the work is known to live in one, run:

```bash
openspec store list --json
```

Resolve the registered store id from that output. If no entry matches, or multiple entries make the intended store ambiguous, stop and ask the user to select a registered id. Do not guess or accept an arbitrary filesystem path. Once selected, append `--store "<id>"` to every store-aware command in this procedure: `openspec new change`, `openspec status`, and `openspec instructions`. Keep the same id on every follow-up. Without a selected store, omit `--store`; the commands resolve the nearest local OpenSpec root.

If store listing exits nonzero or returns malformed JSON, report the exact failure and stop. Do not fall back to an unscoped root after the user selected a store.

Do not pass `--store` to `openspec schemas`; it does not accept that flag. When schema discovery is needed for a selected store, run it with the working directory set to the resolved store's planning root.

### 3. Resolve the schema

Use the resolved root's default schema by omitting `--schema` unless the user explicitly requests another workflow schema.

If the user asks to show, compare, or choose workflows, run this from the resolved planning root:

```bash
openspec schemas --json
```

Parse each returned schema's `name`, `description`, `artifacts`, and `source`, show the choices, and obtain the user's selection. `openspec schemas` accepts `--json`; it does not accept `--store`. If the user names a specific schema, pass it directly and let `openspec new change` validate it against the resolved root. Never infer the active graph from the bundled `spec-driven` example.

If schema discovery exits nonzero, returns malformed JSON, or returns no schemas, report that state and stop without scaffolding.

### 4. Scaffold exactly once

Run the JSON form so the resolved identifiers and paths can be parsed:

```bash
openspec new change "<name>" --json
```

Add `--schema "<schema>"` only for an explicitly selected non-default schema. Add the sticky `--store "<id>"` only when a registered store was selected. Flag order is not semantic. The complete ordinary invocation surface used by this action is therefore the required `<name>`, `--json`, optional `--schema <name>`, and optional `--store <id>`.

The CLI also registers `--description <text>` and `--goal <text>` on `new change`. Do not infer either from the user's change description: `--description` creates a `README.md`, while `--goal` adds goal metadata. Use one only when the user explicitly requests that exact scaffold metadata/content and doing so remains within this action. `--store-path`, `--initiative`, and `--areas` are not substitutes: the latter two are removed and deliberately error, and store selection is by registered `--store <id>`.

Parse and retain:

- `change.id`, `change.path`, `change.metadataPath`, and `change.schema`;
- the complete `root` object returned by the CLI.

The successful schema is `change.schema`, including when the default was selected by omission. The authoritative change location is `change.path`; do not reconstruct it.

Handle every scaffold branch before continuing:

- A nonzero exit, malformed JSON, a missing/null `change`, or returned error `status` means scaffolding did not succeed. Report the CLI's exact error and stop.
- A missing name or CLI name-validation failure means ask for a valid kebab-case name and stop this attempt.
- If the change already exists, do not overwrite or modify it. Report its existence and direct the user to the continue-change action or a new name.
- If the schema is unknown, report the exact validation error. Offer schema discovery only if it helps the user choose; do not silently fall back to the default.
- A root/store resolution error, including an unregistered store, stops the action. Do not retry against another root.
- Errors for removed `--initiative` or `--areas`, or unsupported `--store-path`, are surfaced as-is and are not translated into another workflow.

### 5. Query the live artifact status

After successful scaffolding, run:

```bash
openspec status --change "<name>" --json
```

Append the same `--store "<id>"` when selected. Do not pass `--schema`: status auto-detects the active schema from the new change's metadata, and overriding it could misrepresent the scaffold.

For this action, the status call uses required `--change <name>`, `--json`, and optional sticky `--store <id>`. Although the command can accept `--schema <name>`, deliberately omit it here. Do not use the unsupported hidden `--store-path` route.

Parse and retain the returned `changeName`, `schemaName`, `planningHome`, `changeRoot`, ordered `artifacts`, `artifactPaths`, `nextSteps`, `isPlanningComplete`, and `root` whenever present. For every artifact, retain its `id`, exact `status`, and any `missingDeps` or other returned path/state data. The only artifact states are `done`, `skipped`, `ready`, and `blocked`.

Treat the ordered `artifacts` array as the live artifact sequence. Compute completed count from `status == "done"`; exclude `status == "skipped"` from the denominator and report skipped count separately. Use `planningHome`, `changeRoot`, and all returned paths exactly.

If status exits nonzero, is malformed, refers to a different change/schema/root than the scaffold response, or contains an unknown state, report the contradiction and stop. If it reports no artifacts, report that live state and stop. If it already reports planning complete, report it and stop; do not create or fetch a completed artifact. Otherwise select the first artifact in returned order whose state is exactly `ready`. Never choose a familiar id by memory. If none is ready, report each blocked artifact and its returned `missingDeps`, note any skipped artifacts, and stop.

### 6. Fetch only the first ready artifact's instructions

For the selected ready artifact id, run:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Append the same sticky `--store "<id>"` when selected. Omit `--schema` so the change metadata remains authoritative.

For this action, the instructions call uses required `<artifact-id>`, required `--change <name>`, `--json`, and optional sticky `--store <id>`. Although the command can accept `--schema <name>`, deliberately omit it here. Do not use the unsupported hidden `--store-path` route.

Parse and retain all returned instruction data, including `artifactId`, `changeName`, `schemaName`, `changeDir`, `outputPath`, `resolvedOutputPath`, `description`, `instruction`, `template`, `context`, artifact-keyed `rules`, `dependencies`, `unlocks`, `references`, `skipped`, `warning`, and `root` whenever present. For each dependency retain its id, path, completion/skipped state, and description as returned. `context` and `rules` are constraints; they are not content to copy. `references` are read-only upstream context. Do not read dependency files or draft the output in this action.

If the command fails, JSON is malformed, the returned artifact/change/schema/root differs from the selected live state, `skipped` is true, or any dependency is unexpectedly unmet for an artifact status that was `ready`, report the exact error or contradiction and stop. Do not try a later artifact. Otherwise display or concisely reproduce the returned `description`, `instruction`, and `template`, plus the resolved output location for orientation only. Do not write there.

### 7. Stop

Stop immediately after reporting the first ready artifact instructions. A request to draft or create that artifact is a fresh continue-change action; it is not permission to cross this action's stopping point.

## Decision rules

- Ask only when intent, an explicit invalid name, store selection, schema selection, or another unresolved choice would materially change the scaffold. Make safe reversible assumptions for immaterial wording.
- Live CLI state and the active schema outrank this prose. Surface conflicts rather than weakening the CLI result.

## Applicable invariants

- Never hard-code artifact ids, file names, dependency edges, or the current bundled `spec-driven` sequence. That schema is an example, not runtime authority.
- Treat `done`, `skipped`, `ready`, and `blocked` literally. `skipped` satisfies graph calculations without implying an output file; file existence is not a semantic-quality verdict.
- Use returned `planningHome`, `changeRoot`, `artifactPaths`, `outputPath`, and `resolvedOutputPath` exactly. Never reconstruct or normalize them into guessed repo-local paths.
- Do not use `apply_patch` to create or modify a planning artifact in this action. If a task plan is genuinely useful, maintain it only with `update_plan`; this short scaffold normally does not need one.
- Do not infer, set, remove, or disable `skip_specs`. That semantic decision belongs only to an action actually producing or revising a proposal under a live instruction; this action still stops after scaffolding and first-ready instructions.

## Conditional reference loads

New-change is a short, sequential scaffold and normally must not delegate discovery or writing. Do not load shared specialist guidance by default.

Only if an unusually complex, materially useful read-only subtask cannot be handled directly should you first read `../openspec-shared/references/subagents.md`, then follow it.

## Delegation

Normal execution uses no specialists. If the conditional reference has been loaded and specialist delegation is materially justified, give the specialist a narrow read-only assignment. It must not scaffold a second change, create an artifact, or choose workflow state. Parallel writing is never useful here. This conditional specialist rule does not change the mandatory one-hop action-role guard, and the routed action role must never redispatch itself.

## Completion and reporting

Report:

- the created `change.id`, authoritative `change.path`, `change.metadataPath`, and selected registered store if any;
- the resolved `change.schema`/`schemaName` and live artifact sequence in returned order, including skipped or blocked states;
- actual progress as done/non-skipped total, with skipped count separately;
- the first ready `artifactId`, its `resolvedOutputPath`, dependencies, unlocks, warning if present, and its returned description/instruction/template;
- the exact commands run and their material results, including unavailable or failed checks;
- that only the scaffold was created, no planning artifact was created or edited, and the action has stopped.

If the action stops on an error or live-state contradiction, report the error, what was and was not created, and the next user decision required. Never claim success from remembered or inferred output.
