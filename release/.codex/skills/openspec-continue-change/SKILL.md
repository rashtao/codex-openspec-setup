---
name: openspec-continue-change
description: Continue an existing OpenSpec change by resolving its registered store and change, inspecting live planning status, and creating exactly the first ready planning artifact from the active schema's instructions. Use when the user asks to continue, advance, progress, resume, or create the next artifact for a change, including when they name a change or registered store, ask what is ready next, or want one more planning artifact produced without implementing code.
---

# Continue an OpenSpec change

Create exactly one planning artifact: the first artifact currently reported as `ready`. The live OpenSpec CLI and active schema own the artifact graph, paths, content, and stopping point.

## One-hop action routing

If the current task prompt contains `ROUTED_ACTION=openspec-continue-change`, execute this installed skill directly and never route the same action again.

Otherwise, dispatch exactly one child with:

```text
spawn_agent({
  task_name: "openspec_continue_change",
  message: "ROUTED_ACTION=openspec-continue-change. Execute the latest user request directly. Read .codex/skills/openspec-continue-change/SKILL.md and follow it. Never route openspec-continue-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

The parent does no duplicate action work; it waits for the child and relays the result. Do not use any other new-agent dispatch form. Existing-agent coordination is not a substitute for this guard.

## Authority and tools

Apply this precedence:

1. Explicit user instructions that fit this action.
2. Current CLI state, active-schema semantics, and live artifact instructions.
3. This skill's action-specific guidance.
4. Optional engineering techniques and shared references.

Surface a conflict instead of weakening the higher authority. Use `update_plan` only when a short plan materially improves visibility. Use `apply_patch` for direct artifact writes. Do not implement application code, edit another planning artifact, sync specs, archive, or continue into a second ready artifact.

## 1. Resolve the planning root and change

If the user names a registered store, or the change lives in one, run `openspec store list --json`, resolve a valid store id, and retain `--store "<id>"` on every supported follow-up in this action: `list`, `status`, and `instructions`. Without a selected store, operate from the nearest local OpenSpec planning root. Never guess a store path or pass the store flag to an unsupported command.

Resolve the change as follows:

- Use an explicitly supplied change name.
- Otherwise use an unambiguous change named in the conversation.
- Otherwise, obtain `openspec list --json` from the resolved planning root. Auto-select only when exactly one active change exists.
- If selection remains ambiguous, ask the user. `list --json` supplies name, task counts/status, and `lastModified`, but no schema. For the three or four candidates to display, run `openspec status --change "<candidate>" --json` with the sticky store flag and use its `schemaName`; if a candidate status lookup fails, label schema unavailable rather than defaulting it. Present those fields and mark the most recently modified option as recommended. Do not make per-candidate status calls when the display needs only list-provided names/progress.

Announce `Using change: <name>` and say that the user can name a different change to override it. This selection question is part of the action; do not add routine artifact approval gates.

## 2. Read live status

Run:

```bash
openspec status --change "<name>" --json
```

Append the selected store flag when applicable. Parse the returned `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `nextSteps`, `actionContext`, `applyRequires`, ordered `artifacts`, and `root`. For every artifact retain its `id`, `outputPath`, `status`, `requires`, and any `missingDeps`; for every `artifactPaths` entry retain `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`. Preserve artifact states exactly as `done`, `skipped`, `ready`, or `blocked`. A skipped artifact satisfies graph completion without a file; never look for or create its output.

Use `isPlanningComplete` when present. Use legacy `isComplete` only when `isPlanningComplete` is absent.

- If planning is complete, report the schema and final status, explain that implementation may be requested next and archival belongs after implementation and tracked work, then stop.
- Otherwise select the first entry in the returned `artifacts` order whose status is `ready`. Do not sort, infer an order, or choose a familiar artifact name.
- If none is ready, report the blocked status and every reported `missingDeps`, suggest checking the schema/change state, and stop without writing.

Use `planningHome`, `changeRoot`, and the selected artifact's `artifactPaths` entry exactly. Do not reconstruct a change path from repository conventions.

## 3. Load the first ready artifact's instructions

Run:

```bash
openspec instructions <artifact-id> --change "<name>" --json
```

Append the selected store flag when applicable. Parse every returned field and use it according to its role:

- `changeName`, `artifactId`, `schemaName`, `changeDir`, `planningHome`, and `root` confirm identity and scope; a contradiction with status is a state conflict to surface.
- `outputPath` is the schema pattern; `resolvedOutputPath` is the write authority; `existingOutputPaths` records concrete outputs that already exist. Never invent or widen paths.
- `description` and `instruction` define the artifact's purpose and content. `template` defines its output structure. Follow both; if they conflict materially, stop and surface the conflict.
- `context` and the artifact-keyed `rules` are required constraints. Apply them, but never copy them or wrapper tags into the artifact.
- `dependencies` is the complete direct dependency input. Retain each dependency's `id`, `done`, `path`, `description`, and any `skipped` flag. Re-read every file in the matching status `artifactPaths[<dependency-id>].existingOutputPaths` for each completed, non-skipped dependency, even if it was read earlier in the conversation. A dependency with `skipped: true` has no file to read. A dependency reported missing, or a completed dependency with no reported existing output, is a state conflict; do not draft through it.
- `references` is read-only upstream context. Consult relevant entries without editing them or treating them as outputs.
- `unlocks` is a prospective hint. The fresh status after the write is authoritative about what actually became ready.
- `skipped` prohibits creation. Show `warning`, refresh status, and reconcile the frontier; never create the skipped output. If a different artifact is then the first ready entry, it may be the single artifact for this invocation.
- `warning` must be reported and obeyed; it is not permission to weaken status or the action boundary.

Within those fields, live status and built-in action semantics control whether work may proceed; `instruction` and `template` control the artifact; `context` and `rules` constrain it. This skill and optional references only strengthen quality where consistent with those sources.

If `instruction` explicitly delegates artifact creation to a callable skill or command, honor that live delegation only within this action and then verify the resolved outputs. If the named mechanism is unavailable, stop and report the blocker rather than substituting an invented runtime.

## 4. Draft only the resolved artifact

First understand the artifact semantically from `artifactId`, `description`, `instruction`, `template`, and dependencies. Do not classify it by filename alone and do not assume the active schema contains any familiar artifact type.

Ask a question only when an unresolved answer would materially change public behavior, API or release compatibility, architecture, acceptance criteria, destructive migration, security, interoperability, or a major performance/memory tradeoff. State the decision, evidence already available, viable choices, and consequences. For immaterial gaps, make a safe reversible assumption that fits the artifact and disclose it; do not introduce imported confirmation rituals.

Load `artifact-quality.md` when its condition below applies and use only its matching section. For other artifact semantics, follow the live purpose and structure. Do not create a glossary, ADR, research note, or any file outside the resolved artifact outputs.

### Conditional shared references

These are optional technique references, not lifecycle authorities. Load only the file whose condition is met for the live next artifact and current change; never load all by default:

- `../openspec-shared/references/artifact-quality.md` when the live next artifact is an intent, behavioral specification, technical design, implementation-task artifact, or unknown custom artifact needing the matching compact quality contract.
- `../openspec-shared/references/performance-memory.md` only when the change can plausibly affect performance, memory, allocation, concurrency, buffering, backpressure, or resource lifetime.
- `../openspec-shared/references/integration-correctness.md` only when the artifact concerns a connector, framework integration, protocol, external system, or version interoperability.
- `../openspec-shared/references/research.md` only when repository evidence is insufficient or an exact dependency, protocol, or runtime version materially affects the artifact.
- `../openspec-shared/references/subagents.md` only when a narrow read-only discovery, version-specific research, or materially different design comparison would benefit this artifact enough to justify delegation. Do not load it for the mandatory one-hop action-role guard, and never delegate the artifact write itself to overlapping writers.

Write exactly the output or outputs represented by `resolvedOutputPath`:

- For a concrete path, create only that file.
- For a glob or pattern, choose only the concrete path or paths required by the live `instruction`, `template`, dependencies, and change context, and keep every output within the reported pattern and `changeRoot`.
- Do not modify dependency files, `existingOutputPaths`, unrelated files, or another artifact. Do not create extra notes or review files.

Fill the live template; do not copy its instructional comments as unresolved placeholders. After writing, verify every intended concrete output exists at the resolved location and no output was written outside the eligible set.

If and only if this artifact's live `instruction` is the proposal/intent instruction that requires an explicit no-spec declaration, satisfy that instruction as part of this one-artifact invocation. Classify requirement-level behavior from repository evidence and the proposal; ask one focused semantic question if materially uncertain. When the proposal establishes zero new or modified capabilities and no spec-level behavior change, use a CLI-returned `metadataPath` if one is available, otherwise resolve exactly `<changeRoot>/.openspec.yaml`; require the exact basename and prove the canonical target remains within canonical `changeRoot`. Parse the YAML mapping and set only `skip_specs: true` with `apply_patch`, preserving every other field. Rerun status and require each artifact whose normalized `outputPath` begins `specs/` to be `skipped` with no existing output. If this proposal instead introduces capabilities while metadata already sets `skip_specs: true`, require explicit confirmation of that semantic classification, remove the key or change only it to `false`, rerun status, and require those artifacts to re-enter a non-skipped live state. Stop and report any unsafe path, invalid metadata, or state mismatch. This schema-required companion transition is not a second artifact or permission for any other metadata edit.

## 5. Recheck and stop

Run a fresh:

```bash
openspec status --change "<name>" --json
```

Append the selected store flag when applicable. Confirm that the created artifact is now `done` and use this fresh result to compute progress and identify newly `ready` artifacts. If the output exists but status does not advance, report the discrepancy rather than claiming completion.

Report:

- the created artifact and concrete output path or paths;
- the active schema;
- current completed/total progress, excluding skipped artifacts from the denominator and reporting the skipped count separately;
- artifacts that are now ready, distinguishing them from the earlier `unlocks` hint;
- assumptions, material limitations, and unavailable checks.

Invite the user to ask to continue or name the next desired action, then stop. Never create a second artifact in the same invocation.
