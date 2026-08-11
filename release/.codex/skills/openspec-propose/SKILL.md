---
name: openspec-propose
description: "Create a new OpenSpec change and every planning artifact transitively required for apply, in one planning-only pass. Use when the user asks to propose, plan, specify, design, or task a new change; wants a complete implementation-ready change from a build/fix request; asks to generate all proposal artifacts at once; or names openspec-propose."
---

# OpenSpec Propose

Create one new change and all planning artifacts in the live apply-required closure. This action plans only. A request such as “build,” “implement,” or “fix” authorizes the proposal, not application-code edits or apply. After planning is complete, report the result and stop; applying it requires a fresh user request.

## Action routing

Use exactly one routing hop.

- If the current task prompt contains `ROUTED_ACTION=openspec-propose`, execute this installed skill directly. Never route `openspec-propose` again.
- Otherwise call:

```text
spawn_agent({
  task_name: "openspec_propose_action",
  message: "ROUTED_ACTION=openspec-propose. Execute the latest user request directly. Read .codex/skills/openspec-propose/SKILL.md and follow it. Never route openspec-propose again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "xhigh"
})
```

The parent waits for that child and returns its result. Never dispatch by selector, agent type, role name, imported runtime, or self-reference. Never substitute a command invocation for this native routing call.

## Authority and tools

The order of authority is: compatible explicit user instruction; live OpenSpec CLI state, active schema, artifact instructions and templates; this skill; conditional engineering references. Surface contradictions instead of weakening the higher authority.

Use `update_plan` for the working plan when the action has multiple artifact steps. Its callable shape is:

```text
update_plan({
  explanation?: "brief reason for this plan or update",
  plan: [
    { step: "concrete step", status: "pending" | "in_progress" | "completed" }
  ]
})
```

Keep at most one step `in_progress`. Use `apply_patch` for every artifact-file edit; pass it a standard patch as free-form input. Do not invent a todo tool or a patch wrapper. Create only necessary parent directories when an instruction resolves a glob to a new nested output.

## Shared references: load only for these exact reasons

Shared references are relative to this skill. Load one only when its condition is true, and apply it as technique under the authority order above.

- `../openspec-shared/references/artifact-quality.md`: load while drafting or assessing intent, behavioral specification, technical design, implementation-task, or unknown custom artifacts. Use only the section matching the live artifact semantics and template.
- `../openspec-shared/references/api-semver.md`: load when the change can affect public API or externally observable compatibility.
- `../openspec-shared/references/performance-memory.md`: load when performance or memory can plausibly change or a quantitative claim is needed.
- `../openspec-shared/references/integration-correctness.md`: load when the change crosses an integration or version-sensitive boundary.
- `../openspec-shared/references/research.md`: load when repository evidence is insufficient or exact external-version behavior matters.
- `../openspec-shared/references/review.md`: load when a high-consequence artifact merits independent, read-only assessment.
- `../openspec-shared/references/subagents.md`: load before any optional delegation or concurrency decision.

No shared reference changes the artifact graph, adds an approval, or authorizes implementation.

## 1. Resolve intent, name, store, and schema

1. Establish what cohesive change the user wants. If there is no usable request, ask: “What change do you want to work on? Describe what you want to build or fix.” Derive a concise kebab-case name when the user supplies only a description.
2. Resolve only unknowns whose answers would materially change public behavior, API or release compatibility, architecture, acceptance criteria, destructive migration, security, interoperability, or a major performance/memory tradeoff. State the decision, evidence already found, viable consequences, and a recommendation. For immaterial gaps, make a safe reversible assumption and record it in the applicable artifact. Do not ask for per-artifact confirmation.
3. If the request actually contains independent changes, keep the proposed change cohesive: narrow to the requested shared outcome or ask which materially different scope is intended. Do not create multiple changes without explicit authorization.
4. If the user names a registered store or the work is known to live in one, run `openspec store list --json`, resolve the exact registered id, and make `--store "<store-id>"` sticky on every supported command in this action. Store-aware commands include `new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, and `view`. Do not pass `--store` to `schemas`. Without a selected store, use the nearest local OpenSpec root.
5. Use the configured default schema unless the user explicitly names another schema. If the user asks what workflows/schemas exist:
   - run `openspec context --json` from the current working directory, adding the sticky `--store` when selected;
   - parse `root.path`, `members`, and `status` from the result;
   - run `openspec schemas --json` with the working directory set to `root.path`; parse each returned schema's `name`, `description`, `artifacts`, and `source`, and let the user choose;
   - only when context reports `no_openspec_root` and no store was explicitly selected, run `openspec schemas --json` from the current working directory;
   - do not use that fallback for an invalid, missing, or unavailable store, an unreadable registry, or another context failure. Report the diagnostic and fix from `status` instead.

`openspec context` also supports `--code-workspace <path>` and `--force`, but this action does not request an editor workspace. `--store-path` is removed; never use it.

## 2. Create exactly one new change

Use JSON so creation state and the resolved root are explicit:

```bash
openspec new change "<name>" --json
```

For an explicitly selected schema, add `--schema "<schema-name>"`. Add the sticky `--store "<store-id>"` when applicable. Do not add `--schema` merely because the default schema is familiar.

The command also accepts `--description <text>` and `--goal <text>`. Use them only when the user explicitly supplies those separate metadata values and their extra README/metadata output is intended; the planning artifacts remain authoritative. Never pass removed `--initiative`, `--areas`, or `--store-path` options.

Parse:

- `change.id`, `change.path`, `change.metadataPath`, and `change.schema`;
- `root`, including the resolved root path and store identity when present.

Treat the returned `change.path` as the change root; do not reconstruct it. The command validates a missing or invalid kebab-case name, removed options, root/store selection, and an explicitly named schema. In JSON failure it returns `change: null`, a structured `status` entry, and a failing exit code. Do not proceed from a failure payload.

If the name already exists, do not overwrite or adopt it. Tell the user to continue that existing change with the corresponding continue action or choose a new name. If the user must choose, stop until they do. If creation partially succeeds but its JSON cannot be trusted, inspect with scoped read-only CLI commands; never issue a second create blindly.

## 3. Query the live artifact graph

Run:

```bash
openspec status --change "<name>" --json
```

Add the sticky store flag when selected. Normally omit `--schema` so the CLI reads the created change metadata; use `--schema "<schema-name>"` only for an explicit compatible override.

Parse every relevant field:

- `changeName`, `schemaName`, `planningHome`, `changeRoot`, `nextSteps`, and `actionContext`;
- `artifactPaths`, keyed by artifact id, with `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`;
- `isPlanningComplete` and compatibility alias `isComplete`;
- `applyRequires`;
- the full `artifacts` array in returned order, including each `id`, `outputPath`, `status`, `requires`, and `missingDeps` when blocked;
- `root`.

Artifact state is exactly `done`, `skipped`, `ready`, or `blocked`. Status is chiefly output-existence state, not a semantic-quality verdict. A `done` artifact still contributes all of its live `requires` edges.

Compute the apply-required closure from this payload, never from remembered artifact names:

1. Seed the set with every id in `applyRequires`.
2. For every id in the set, add every id in its current `requires` array; repeat to a fixed point.
3. Preserve returned artifact/declaration order as the stable tie-break while respecting dependency order.
4. If an id is missing from `artifacts`, an edge is cyclic, or no eligible artifact can make progress, stop and report the schema/CLI contradiction with the relevant fields.
5. Leave every artifact outside the closure untouched.

Do not mistake `applyRequires` for the whole required set. Do not infer completion from a downstream file: its transitive dependencies remain required even if it already reads `done`.

`status` without `--change` returns `{ changes: [], message, root }` when no changes exist and otherwise errors with the available names. A missing or invalid change, root/store failure, or explicit-schema failure is not permission to guess a path or graph.

## 4. Produce the closure in dependency order

Maintain a plan whose items are the live closure, plus the final status check. Re-run JSON status after every artifact write or deliberate conditional skip, then recompute the closure and remaining order from the returned edges.

For each not-yet-satisfied artifact whose dependencies are satisfied, prefer one whose status is `ready`; use returned order to break ties. Run:

```bash
openspec instructions "<artifact-id>" --change "<name>" --json
```

Add the sticky store flag when selected. As with status, omit `--schema` unless applying an explicit compatible override.

Parse:

- `changeName`, `artifactId`, `schemaName`, `changeDir`, `planningHome`, and `root`;
- `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`;
- `description`, `instruction`, and `template`;
- `context`, artifact-keyed `rules`, and read-only `references`;
- `dependencies`, each with `id`, `done`, `path`, `description`, and optional `skipped`;
- `unlocks`;
- optional `skipped` and `warning`.

Before drafting, re-read every completed dependency file identified by `dependencies` from disk, even when it appeared earlier in the conversation. A skipped dependency has no file to read. Also honor the returned `actionContext` and relevant referenced-store facts without treating references as writable outputs.

Apply content authority in this order:

1. live state and this action's planning-only boundary;
2. the active artifact's `instruction` and `template`;
3. returned project `context` and artifact-specific `rules` as constraints;
4. applicable shared-reference techniques.

Never copy `context`, `rules`, or wrapper tags into the artifact. Preserve the template's structure and fill it with concrete content. The instruction supplies schema-specific semantics even when the artifact id looks familiar.

If `skipped: true` or the warning says the artifact is skipped, do not create its output. It is satisfied with no files. Report the warning and continue.

If the artifact instruction itself makes the output conditional, decide from the condition and available evidence. When false, record the exact condition and evidence, report the deliberate skip, and never reconsider it during this invocation. A skipped status is distinct from a deliberate conditional skip.

Ordinarily, do not create a `blocked` artifact. A conditional dependency is the one exception preserved by the live workflow: when that dependency was deliberately skipped and is the only reason a required downstream artifact remains blocked, fetch the downstream instructions, re-read every existing dependency, and create it cautiously. Dependencies enable ordering; an instruction-declared conditional artifact does not become a permanent gate.

If `instruction` delegates artifact creation, follow that live instruction using only an actually available callable mechanism that does not violate this action. Do not invoke a foreign skill, slash command, or pseudo-tool. Verify the resulting eligible output. Otherwise:

- resolve a concrete path from `resolvedOutputPath`; for a glob, choose only paths authorized by `instruction` and the user's capability set;
- never write outside `resolvedOutputPath`/`artifactPaths` eligibility, except for the exact live-proposal `skip_specs` transition below;
- use `apply_patch` to add the artifact or make an authorized in-progress correction;
- verify the concrete file exists, then re-run status and confirm it appears in `existingOutputPaths` or reaches the expected state.

When the artifact's live `instruction` is the proposal/intent instruction requiring an explicit no-spec declaration, its metadata consequence is part of producing that artifact. Classify from repository evidence and the proposal; if whether any requirement-level behavior changes is materially uncertain, ask one focused semantic question. When the proposal establishes zero new or modified capabilities and no spec-level behavior change, use the `change.metadataPath` returned by creation when available, otherwise resolve exactly `<changeRoot>/.openspec.yaml`; require the exact basename and prove the canonical target remains within canonical `changeRoot`. Parse the YAML mapping and use `apply_patch` to set only `skip_specs: true`, preserving every other field. Rerun status and require every artifact whose normalized `outputPath` begins `specs/` to be `skipped` with no existing output. If the proposal instead introduces capability-level requirements while metadata already sets `skip_specs: true`, require explicit confirmation of that classification, remove the key or change only it to `false`, rerun status, and require those artifacts to re-enter a non-skipped live state. Stop and report unsafe paths, invalid metadata, conflicting spec outputs, or a status mismatch. This is live proposal-instruction compliance, not another artifact, lifecycle step, or authority for another metadata edit.

If a supposedly new output appears or changes unexpectedly while you are working, stop rather than overwrite another writer. If instructions name an unknown artifact, omit a template, fail template loading, report an invalid artifact with its valid ids, or contradict status/output paths, report the exact error and do not improvise a file.

Continue until every artifact in the recomputed closure is `done`, `skipped`, or one deliberate instruction-authorized conditional skip. File existence alone is insufficient: perform the applicable quality checks below before calling an artifact complete.

## 5. Conditional artifact quality

When a live artifact has intent, behavioral-specification, technical-design, implementation-task, or other planning semantics, load `artifact-quality.md` and use only its matching section under the current instruction and template. Load the other canonical references only when their triggers in the earlier list apply. Do not recreate those contracts here, infer a familiar artifact role from a filename, add an output, or add an approval gate.

## 6. Final state and stopping point

Run the final human-readable command:

```bash
openspec status --change "<name>"
```

Add the sticky store flag when selected. Then report:

- change name, `changeRoot`, planning home/store, and active schema;
- artifacts created, with resolved paths and one-line purpose;
- artifacts already done, status-skipped, or deliberately conditionally skipped, including exact reasons;
- the transitive apply-required closure and whether all of it is satisfied;
- material assumptions, unavailable checks, warnings, contradictions, or remaining questions;
- the final status command and material result.

Only say “All artifacts needed for implementation are ready” when every id in the live closure is satisfied under the rules above. Otherwise report the precise blocker and stop without implementation.

End by saying the artifacts are ready for review and that applying this change requires a fresh request. Do not suggest a slash command, start apply, edit project code, sync specs, archive, commit, publish, or perform any other action.
