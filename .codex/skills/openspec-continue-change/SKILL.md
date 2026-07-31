---
name: openspec-continue-change
description: Continue an existing OpenSpec change by selecting it, resolving its active schema, and creating exactly the next ready planning artifact. Use when the user asks to continue, advance, or create the next artifact in an OpenSpec workflow.
---

# Continue an OpenSpec Change

Create exactly one next-ready planning artifact for an existing change. Treat the active schema and the CLI JSON contracts as authoritative; never assume standard artifact names or repo-relative paths.

## Codex coordination

Use `update_plan` for selection, status resolution, artifact creation, and verification. Keep exactly one step `in_progress` while work remains.

Keep the main orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `high` reasoning. If a bounded planning or review subagent is required, call `spawn_agent` with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"` or a positive recent-turn count. Include the working directory, selected store/change, exact paths, read/write scope, required evidence, and return format. Use `send_message` only to correct an active agent's scope or provide missing input, then `wait_agent` for its terminal result.

This planning workflow does not dispatch implementation agents. If a delegated workflow exceptionally requires an Implementer or Fixer, route that role to `gpt-5.6-terra` with `medium` reasoning and restrict it to the already-decided implementation or repair.

## 1. Resolve the store and change

If the user names a registered store or the work is known to live in one, run:

```bash
openspec store list --json
```

Resolve the exact store id and retain `--store <id>` on every store-aware follow-up. Otherwise omit the flag and let OpenSpec use the nearest local root.

Resolve the change name from explicit input or unambiguous recent context. Otherwise run:

```bash
openspec list --json
```

- Auto-select only when exactly one active change exists.
- If none exist, report that there is no change to continue and suggest the new-change workflow.
- If several exist, ask the user directly to choose. Show the 3–4 most recently modified entries with name, task status, and `lastModified`. Mark the most recent as recommended.
- Do not label a candidate's schema `spec-driven` merely because `openspec list` omits it. If schema is useful in the selection prompt, fetch each candidate's status and use its `schemaName`.
- If an explicitly named change is missing, report that error; do not silently choose another.

After selection, say `Using change: <name>` and mention that the user can name a different change on the next invocation.

## 2. Resolve status

Run and require successful exit status and valid JSON:

```bash
openspec status --change "<name>" --json
```

Use `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `artifacts`, `isComplete`, `nextSteps`, and `actionContext` from the response. Do not construct paths from convention. Honor `actionContext.allowedEditRoots` and every reported constraint.

If `isComplete` is true, show the final schema and progress, state that all planning artifacts are complete, suggest implementation or archive as appropriate, and stop without writing.

Otherwise select the first artifact in the returned `artifacts` array whose status is `ready`. Never bypass a blocked predecessor. If none is ready, report each blocking artifact and its `missingDeps`; run `openspec doctor --json` when useful, and stop without writing.

## 3. Obtain and execute the artifact contract

For the selected artifact id, run:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Require valid JSON and agreement with the selected change, schema, and artifact id. Retain:

- `template`, the structural contract;
- `instruction`, the artifact-specific content and path guidance;
- `context` and `rules`, which constrain the work but are not artifact content;
- `resolvedOutputPath` and `existingOutputPaths`;
- `dependencies`, `unlocks`, and optional `references`;
- optional `skipped` and `warning`.

If the response says the artifact is skipped, do not create it. Re-run status and select the next reported ready artifact. If status and instructions remain inconsistent, report the CLI contract error and stop.

Read every completed dependency file from disk, even if it was read earlier. Use the CLI-reported dependency paths and `artifactPaths` to resolve concrete files; a skipped dependency has no file. Read relevant references when the contract supplies them. Stop on a missing required dependency or a path outside the reported edit scope.

If `instruction`, `context`, or `rules` requires a named Codex skill, activate that skill and follow it instead of writing directly. Pass it the selected store, change, exact artifact id, and this resolved instruction contract. If the required skill is unavailable, report the blocker rather than bypassing it.

Otherwise create the artifact using `template` and `instruction`:

- Write only to the concrete `resolvedOutputPath`.
- When the path is a glob, derive each concrete output only from the schema instruction and change content; never write to the literal glob.
- Apply `context` and `rules` without copying their prompt blocks or template comments into the artifact.
- Ask the user directly before writing only when unresolved information would materially change the artifact. Reuse established context and make safe, explicit assumptions where the contract allows.
- Use `apply_patch` for file edits and preserve unrelated user changes.

Do not create any other ready artifact in this invocation.

## 4. Verify and report

Verify the expected concrete output file or files exist, then re-run:

```bash
openspec status --change "<name>" --json
```

Require the selected artifact to report `done` (or `skipped` when explicitly authorized). For glob-backed artifacts, verify the concrete outputs through `existingOutputPaths`; the literal glob is never evidence of completion.

Report:

- selected change and schema;
- artifact created and concrete path or paths;
- current artifact progress (`done` plus `skipped`, separately identified, out of total);
- artifacts newly `ready`;
- any delegated skill and its validation/reviewer result;
- prompt: `Want to continue? Ask me to continue or name the next action.`

Stop after this single artifact.
