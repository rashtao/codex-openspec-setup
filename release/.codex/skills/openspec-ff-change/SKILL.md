---
name: openspec-ff-change
description: Create a brand-new named OpenSpec change and fast-forward every planning artifact in the live apply-required dependency closure in one invocation. Use when the user asks to fast-forward, generate all implementation-ready artifacts, plan a new change end to end, create everything needed before implementation, or avoid stepping through artifacts one at a time; do not use to continue or overwrite an existing change, update existing artifacts, or implement code.
---

# OpenSpec Fast-Forward Change

Create one new change, produce every applicable planning artifact required before apply, and stop at the implementation boundary.

## Runtime role guard

If the current task prompt contains `ROUTED_ACTION=openspec-ff-change`, execute this installed skill directly and never route `openspec-ff-change` again. Otherwise make exactly one dispatch:

```text
spawn_agent({
  task_name: "openspec_ff_change",
  message: "ROUTED_ACTION=openspec-ff-change. Execute the latest user request directly. Read .codex/skills/openspec-ff-change/SKILL.md and follow it. Never route openspec-ff-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

Relay the child result. Do not also execute the action in the parent.

Do not invent another agent-creation mechanism or a custom-agent selector. Use `update_plan` for the live artifact checklist and `apply_patch` for artifact edits.

## Authority and boundary

Authority descends in this order:

1. The user's explicit request, when compatible with this action.
2. Current OpenSpec CLI state, the active schema, and the current artifact instructions.
3. This skill.
4. Conditional shared engineering references.

The CLI-reported active schema and artifact graph are dynamic. Never infer them from filenames, familiar artifact names, a remembered spec-driven workflow, or generated skill prose.

This action may:

- resolve a registered store when applicable;
- create exactly one new named change;
- create missing planning artifacts in the apply-required closure at their live resolved outputs;
- ask only for missing input or a material semantic decision that cannot safely be inferred.

This action must not:

- reuse, continue, overwrite, repair, or update an existing named change;
- create artifacts outside the apply-required closure;
- add approval after each artifact or pause for routine drafting choices;
- implement application code, run apply, sync specs, archive, commit, publish, or start any later action;
- edit project glossary or decision-record files merely because a drafting technique mentions them.

If the requested name already exists, stop without changing it. Tell the user to continue that change in a separate request or choose a new name.

## Input, store, and schema

The input must identify what to build or fix and may supply a kebab-case change name. If intent is missing, ask this open-ended question and wait:

> What change do you want to work on? Describe what you want to build or fix.

Derive a concise kebab-case name from a description. If a supplied name is invalid, ask for a valid kebab-case name; do not silently normalize an explicit name and do not call `new change` yet.

### Store selection

If the user names a registered store or the work lives in one, run:

```bash
openspec store list --json
```

Resolve the exact registered store id from that output. If no entry matches or multiple entries plausibly match, ask the user to select one. If discovery fails or its JSON is malformed, report the diagnostic and stop rather than guessing.

After selection, append `--store "<id>"` to every store-aware command in this action: `new change`, `status`, and `instructions`. Keep the same id on every follow-up. Without a selected store, omit the flag and let the CLI use the nearest local OpenSpec root.

`openspec schemas` does not accept `--store`. If schema discovery is requested for a selected store, run it with the working directory set to that store's resolved planning root and do not add a store flag.

### Schema selection

Use the default schema by omitting `--schema` unless the user explicitly names another schema. If the user asks to see or choose workflows, run:

```bash
openspec schemas --json
```

Parse each returned schema's `name`, `description`, `artifacts`, and `source`, present the live choices, and obtain the user's selection before creating the change. If schema listing fails, is malformed, or does not contain a requested schema, report that result and stop. Pass `--schema "<schema>"` only for an explicitly selected non-default schema. Never pass a store flag to `schemas`.

After creation, omit `--schema` from `status` and `instructions`; those commands auto-detect the active schema from change metadata. A caller-supplied override must not replace the schema recorded for this new change.

## Execution

### 1. Track the action

Start an `update_plan` checklist covering change creation, live graph discovery, each artifact in the computed closure, and final status. Update it as work advances. The checklist is visibility, not an alternate source of artifact state.

### 2. Create the new change

Run exactly one of these forms, adding the sticky store flag when selected:

```bash
openspec new change "<name>" --json
openspec new change "<name>" --json --schema "<schema>"
```

On success, parse:

- `change.id`
- `change.path`
- `change.metadataPath`
- `change.schema`
- `root`

Require `change.id` to equal the requested name. Retain the returned locations and schema as evidence, but use the next live status as the graph authority.

On JSON failure, `change: null`, a non-success `status`, a missing required field, or a nonzero command result, preserve and report the CLI diagnostic. In particular:

- an existing-name or existing-path diagnostic means refuse overwrite and stop;
- an invalid name means ask for a different kebab-case name before any retry;
- an unknown schema means present the live schema choices only if the user wants to choose another;
- root/store resolution failure, permission failure, or any other creation failure means stop without claiming the change exists.

Do not pass removed or internal options such as `--initiative`, `--areas`, or `--store-path`. Do not pass `--description` merely to create a README or `--goal` merely to duplicate artifact content; the requested output is the planning-artifact closure.

### 3. Read live status and compute the apply-required closure

Run, with the sticky store flag when selected:

```bash
openspec status --change "<name>" --json
```

Parse and retain every status contract field:

- `changeName`, `schemaName`, `planningHome`, `changeRoot`, `root`
- `artifactPaths`, including each artifact's `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`
- `applyRequires`
- `artifacts`, including each artifact's `id`, `outputPath`, exact `status`, `requires`, and any `missingDeps`
- `nextSteps`, `actionContext`, `isPlanningComplete`, and `isComplete`

Artifact state is exactly `done`, `skipped`, `ready`, or `blocked`. It describes expected-file existence and dependency readiness, not semantic quality.

Compute the apply-required closure by starting with every id in `applyRequires` and recursively following every current `requires` edge. Follow edges even from an artifact already marked `done`: a done output does not prove its prerequisites exist. Reject malformed state, unknown dependency ids, or a cyclic graph as a CLI/schema contradiction and stop with the evidence.

Use active-schema declaration order as the stable tie-break while topologically ordering the closure. Leave every artifact outside the closure alone. If `applyRequires` is empty, the closure is empty and no planning artifact is created.

### 4. Load conditional shared guidance only when relevant

Before drafting an affected artifact, read only the shared references whose exact condition applies:

- `../openspec-shared/references/artifact-quality.md` when drafting or assessing an intent, behavioral specification, technical design, implementation-task, or unknown custom artifact; use only the section matching its live semantics.
- `../openspec-shared/references/api-semver.md` when the change can affect a public API, configuration contract, protocol/wire behavior, observable errors, lifecycle semantics, extension points, or any other externally relied-on behavior.
- `../openspec-shared/references/performance-memory.md` when the change can plausibly affect latency, throughput, allocation, buffering, batching, caching, concurrency, backpressure, connection/resource lifetime, or memory use.
- `../openspec-shared/references/integration-correctness.md` when the change touches a connector, framework integration, external service, protocol, transaction, retry/idempotency behavior, streaming, cancellation, version compatibility, or value conversion.
- `../openspec-shared/references/research.md` when repository evidence is insufficient or the exact dependency, protocol, framework, runtime, or supported-version behavior matters.
- `../openspec-shared/references/review.md` when a high-consequence artifact merits independent, read-only assessment.
- `../openspec-shared/references/subagents.md` only when considering a narrowly scoped read-only specialist or independent high-consequence review that can materially improve the artifact; do not delegate trivial reads or artifact ownership.

Apply loaded guidance as constraints inside this action. It cannot introduce another lifecycle, another output, or a confirmation ritual.

### 5. Create artifacts in dependency order

Continue until every id in the closure is terminal for this invocation: CLI state `done`, CLI state `skipped`, or deliberately skipped because that artifact's current `instruction` explicitly makes it conditional and its predicate does not apply.

For each pass through the ordered closure:

1. Leave `done` artifacts unchanged, but retain their `requires` edges in the closure.
2. Treat `skipped` as satisfied. It means the change metadata intentionally suppresses that artifact; its files must not exist. Never create an output for it.
3. For every missing artifact whose non-skipped, non-conditional predecessors are satisfied, request current instructions.
4. Ordinarily handle `ready` artifacts first. A `blocked` artifact may proceed only when every reported missing dependency was deliberately skipped under its own current conditional instruction or is CLI-skipped. Dependencies enable ordering; a deliberately skipped conditional dependency is not a permanent gate.
5. After every creation, rerun JSON status and recompute states, paths, and the closure before selecting the next artifact. Creation can unlock later artifacts, and files can change between reads.

Get an artifact's instructions with the sticky store flag when selected:

```bash
openspec instructions <artifact-id> --change "<name>" --json
```

Parse and use every returned instruction contract field:

- `changeName`, `artifactId`, `schemaName`, `changeDir`, `planningHome`, and `root`
- `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`
- `description`, `instruction`, and `template`
- `context` and artifact-keyed `rules`
- `references`
- `dependencies`, including each dependency's `id`, `done`, `path`, `description`, and optional `skipped`
- `unlocks`
- optional `skipped` and `warning`

Cross-check the ids, schema, and change directory against current status. A mismatch, unknown artifact, missing template, unresolved output, template-load failure, schema/config failure, malformed JSON, or command failure is blocking; report it and stop rather than drafting from memory.

If `skipped: true` or a do-not-create `warning` is returned, do not write the artifact. Recheck status and record it as CLI-skipped.

Before drafting, re-read every available completed dependency from its current concrete paths. Prefer `artifactPaths[dependency-id].existingOutputPaths` for concrete files; do not guess through a glob. A dependency marked `skipped` has no file to read. Also inspect any current project or referenced-store context identified by the returned instruction payload. Do not rely on conversation memory because files may have changed.

Evaluate conditionality only from that artifact's current `instruction`. Skip only when the instruction explicitly says to create the artifact only under stated conditions and none of those conditions applies. Record the exact predicate and why it was false, tell the user in progress output, and do not reconsider that skip later in the invocation. Never infer that a required artifact is optional merely from its familiar name. In particular, no behavioral-delta artifact may be skipped by judgment when status does not report it `skipped`.

If a non-conditional dependency is missing, return to that dependency. If no artifact can progress and at least one missing dependency is neither CLI-skipped nor deliberately conditional-skipped, stop and report the frontier, states, and `missingDeps` rather than writing out of order.

Use `instruction` and `template` as the requested semantics and structure. Apply `context`, `rules`, and `references` as constraints, never as text to copy into the artifact. Do not emit configuration wrapper blocks or instructional comments as artifact content. If `instruction` directs a particular creation command or installed skill, follow that directive only within this action's output and approval boundary; if it conflicts with the boundary or is unavailable, surface the conflict and stop.

Write only to `resolvedOutputPath`, except for the exact live-proposal `skip_specs` transition below. When it is a glob, use the instruction to choose each concrete path, preserve the full capability path, and ensure every path remains within the reported change root. Use `apply_patch`. If an intended output appeared or changed concurrently, re-read status and the file and do not overwrite it blindly.

After writing, verify the intended concrete output exists, then rerun JSON status. Do not claim creation merely because a patch command returned successfully. Show brief progress such as `Created <artifact-id>`.

When the artifact's live `instruction` is the proposal/intent instruction requiring an explicit no-spec declaration, its metadata consequence is part of producing that artifact. Classify from repository evidence and the proposal; if whether any requirement-level behavior changes is materially uncertain, ask one focused semantic question. When the proposal establishes zero new or modified capabilities and no spec-level behavior change, use the `change.metadataPath` returned by creation when available, otherwise resolve exactly `<changeRoot>/.openspec.yaml`; require the exact basename and prove the canonical target remains within canonical `changeRoot`. Parse the YAML mapping and use `apply_patch` to set only `skip_specs: true`, preserving every other field. Rerun status and require every artifact whose normalized `outputPath` begins `specs/` to be `skipped` with no existing output. If the proposal instead introduces capability-level requirements while metadata already sets `skip_specs: true`, require explicit confirmation of that classification, remove the key or change only it to `false`, rerun status, and require those artifacts to re-enter a non-skipped live state. Stop and report unsafe paths, invalid metadata, conflicting spec outputs, or a status mismatch. This is live proposal-instruction compliance, not another artifact, lifecycle step, or authority for another metadata edit.

### 6. Draft with proportional rigor

Every artifact must follow its current instruction and template and stay within the current change. When `artifact-quality.md` applies, load it and use only its matching section instead of recreating that doctrine here. The active schema always controls exact output form.

For a material unresolved choice that would change public behavior, compatibility, architecture, acceptance criteria, destructive migration, security, interoperability, or a major performance/memory tradeoff, state the evidence and consequences and ask one focused question. Then continue the same fast-forward invocation after the answer. Make safe, reversible assumptions for immaterial gaps and record material assumptions in the relevant artifact. Do not request per-artifact approval.

If a planning artifact is high-consequence and independent review would materially improve it, load `review.md` and `subagents.md` and follow their canonical contracts. The artifact writer remains the single owner; review adds no approval gate.

### 7. Finish at the planning boundary

Re-run JSON status and confirm every closure id is `done`, `skipped`, or on the invocation's recorded deliberate-conditional-skip list. Then show the final human-readable status, with the sticky store flag when selected:

```bash
openspec status --change "<name>"
```

If either final status call fails, report the last known state and the failure; do not claim readiness. Do not require artifacts outside the apply-required closure to be complete.

Summarize:

- change name, active schema, and CLI-reported `changeRoot`;
- each artifact created and a brief description;
- every CLI-skipped or deliberately conditional-skipped artifact and its exact reason;
- any assumptions, loaded conditional guidance, unavailable checks, or unresolved findings;
- the fresh final-status result.

Only when the closure is terminal, state: `All artifacts needed for implementation are ready.` Explain that implementation requires a fresh, separate apply request. Stop without implementing anything.

## Error and stop conditions

Stop with concrete diagnostics when any of these occurs:

- missing intent or a material semantic decision requires user input;
- store or schema selection is missing or ambiguous;
- the name is invalid, the name/path already exists, or change creation fails;
- CLI JSON is malformed or required fields contradict each other;
- the active graph has unknown edges, a cycle, or a stuck non-conditional frontier;
- current instructions, template, dependency context, or resolved output cannot be obtained safely;
- a directive would write outside the reported eligible output or cross this action boundary;
- a concurrent edit would be overwritten;
- an artifact write or post-write existence/status check fails;
- final status cannot substantiate readiness.

Report what succeeded, what did not, current paths/states, and the safe next action. Never convert partial work into a success claim and never continue into implementation.
