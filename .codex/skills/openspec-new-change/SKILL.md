---
name: openspec-new-change
description: Start a new OpenSpec change using the experimental artifact workflow. Use when the user wants to scaffold a named feature, fix, or modification, inspect its schema-defined artifact sequence, and stop before creating the first planning artifact.
---

# Start a new OpenSpec change

Create only the change scaffold, inspect the workflow, and return the first artifact's instructions. Do not create any planning artifact.

## Codex execution

- Run this short, mutating workflow in the main Codex orchestrator. When model routing is configurable, use `gpt-5.6-sol` with high reasoning for orchestration, planning, or review. Do not dispatch an Implementer or Fixer: implementation is outside this skill.
- Use `update_plan` when progress tracking is useful; keep at most one step in progress.
- Ask blocking questions directly and wait for the answer.

## Workflow

### 1. Resolve the planning root

If the user names a registered standalone store, or the work clearly belongs to one:

1. Run `openspec store list --json`.
2. Resolve one exact store id and root. Ask the user if the match is missing or ambiguous.
3. Retain `--store <id>` on `openspec list`, `openspec new change`, `openspec status`, and `openspec instructions`.

Otherwise, let OpenSpec use the nearest local `openspec/` root. Keep the same root for the entire workflow.

### 2. Resolve the change name

Accept either a change name or a description:

- If neither is clear, ask: "What change do you want to work on? Describe what you want to build or fix." Stop until the user answers.
- Derive a concise kebab-case name from a description, for example `add user authentication` becomes `add-user-auth`.
- If the user supplied an explicit invalid name, do not silently rename it. Explain that change ids may contain only lowercase letters, numbers, and single hyphen separators, must not begin or end with a hyphen, and have a 200-character maximum. Ask for a valid name.
- Do not proceed until the intended change is understood.

### 3. Resolve the schema

Use the configured default schema by omitting `--schema` unless the user explicitly requests another schema.

- If the user asks to see workflows, run `openspec schemas --json` from the resolved planning root, present the available schemas, ask them to choose, and wait.
- If the user names a schema, verify its exact id in `openspec schemas --json` from that root. Ask for a valid choice when it is absent or ambiguous.
- Add `--schema "<schema-id>"` to `openspec new change` only for an explicitly selected non-default schema.

`openspec schemas` does not accept `--store`; for a selected store, set the command's working directory to the root returned by `openspec store list --json`.

### 4. Check for a collision and create the scaffold

Run:

```bash
openspec list --json
openspec new change "<name>" --json
```

Add the retained store flag to both commands and the explicit schema flag to `new change` when applicable.

If `list` already contains the exact name, do not run `new change`; report its location and suggest asking Codex to continue that change. Also handle a creation-time collision this way. Do not overwrite, delete, or manually create a change directory.

Require `new change` to exit successfully and return valid JSON. Record the returned change id, path, root, and schema.

### 5. Inspect status and the first ready artifact

Run:

```bash
openspec status --change "<name>" --json
```

Add the store flag when selected. Require successful, valid JSON and verify that its `changeName`, `changeRoot`, and planning root agree with the created change. Use `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `artifacts`, and `nextSteps` from the response; never assume artifact ids, order, or repository-relative paths.

Select the first `ready` artifact in the returned schema order. If none is ready, report the statuses and blockers and stop.

Fetch its authoritative contract:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Add the store flag. Require successful, valid JSON and verify that `changeName`, `artifactId`, `schemaName`, `changeDir`, and output paths agree with status. Retain its `instruction`, `template`, dependencies, and output path for the handoff.

### 6. Stop

Do not write the first artifact or advance the workflow. Return:

- change name and `changeRoot`;
- selected schema and artifact sequence with current completion count;
- first ready artifact id and output path;
- its instruction and template;
- "Ready to create the first artifact? Describe what this change is about and I'll draft it, or ask me to continue."

On any CLI failure, root mismatch, invalid JSON, or inconsistent contract, stop and report the evidence instead of guessing paths or repairing state manually.
