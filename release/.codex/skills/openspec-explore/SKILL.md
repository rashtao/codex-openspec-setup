---
name: openspec-explore
description: Explore vague ideas, requirements, domain language, architecture, alternatives, codebase behavior, defects, performance concerns, integrations, or version-specific questions before or during an OpenSpec change; use for thinking, investigation, comparison, research, reproduction, or clarification without implementing application code.
---

# Purpose and hard boundary

Be a curious, evidence-grounded thinking partner. Inspect the repository, existing planning artifacts, behavior, and external primary sources when relevant; model systems, compare viable alternatives, reproduce defects, surface risks, and recommend a direction when asked. Prefer compact tables or diagrams when relationships are otherwise hard to see.

This action does not implement application code, fix defects, or perform an implementation task. It has no fixed sequence, required conclusion, or mandatory output. Do not auto-capture insights. Create or modify an OpenSpec planning artifact only when the user explicitly asks; if capture is for a new change, scaffold it through the CLI first. If the user asks for implementation, explain the boundary and stop at analysis or planning capture.

# Minimum authoritative OpenSpec procedure

## Route once

If the current task prompt contains `ROUTED_ACTION=openspec-explore`, execute this installed skill directly and never route `openspec-explore` again. Otherwise dispatch exactly one child and let it execute the action:

```text
spawn_agent({
  task_name: "openspec_explore_action",
  message: "ROUTED_ACTION=openspec-explore. Execute the latest user request directly. Read .codex/skills/openspec-explore/SKILL.md and follow it. Never route openspec-explore again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

`task_name` is only a task label, not a role selector. Do not invent a custom selector. The parent waits and returns the child's result without also executing the action.

## Resolve store and context

1. If the user names a registered standalone store or the work lives in one, run `openspec store list --json`, resolve the registered store id, and make `--store "<id>"` sticky for this invocation. Append it to every applicable `new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, or `view` call. Other commands do not accept it. Preserve the flag from CLI hints. Without a selected store, commands resolve the nearest local `openspec/` root.
2. At the start, run `openspec list --json` with the sticky store flag when applicable. Parse only active change `name`, `completedTasks`, `totalTasks`, derived task `status`, `lastModified`, and response-level `root.path`. The rows do not contain schema or artifact fields. If exploration needs to display or filter candidates by schema or artifact inventory, first run `openspec status --change "<candidate>" --json` for each affected candidate with the sticky store flag; skip those extra calls when list names/progress are enough.
3. From the resolved `root.path`, read `openspec/config.yaml`, falling back to `openspec/config.yml`; skip this when neither exists. Treat `context` as project background and artifact-keyed `rules` as constraints only for the artifact they govern. Never copy either into conversation or an artifact.
4. When declared referenced stores are relevant to the question, run `openspec context --json` with the sticky store flag. Parse `root`, `members`, and `status`; distinguish available members from unavailable ones and report diagnostics rather than assuming cross-store context is readable. Do not use `--code-workspace` during ordinary exploration: it writes a file. If the user explicitly requests that file, use `--code-workspace "<path>"`; use `--force` only with explicit overwrite permission.

## Explore without capture

If no change is relevant, continue conversationally. If an existing change is named or clearly relevant:

1. Run `openspec status --change "<name>" --json` with the sticky store flag.
2. Parse `changeRoot`, `artifactPaths`, and `actionContext`. Read only existing artifact files reported by `artifactPaths.<artifact>.existingOutputPaths` for context.
3. Refer to those artifacts naturally. Offer, but never pressure or automatically perform, a capture when a requirement, design decision, scope, work item, or assumption crystallizes.

Offer capture against the live artifact ids, descriptions, instructions, and existing outputs. Do not map an insight to a familiar spec-driven filename when the active schema reports different semantics. This offer is not permission to write.

## Capture only what the user requests

For capture into a new change:

1. Run `openspec new change "<name>"` with the sticky store flag. Never create a change directory by hand; the scaffold creates required metadata such as `.openspec.yaml`.
2. Run `openspec status --change "<name>" --json` with the sticky store flag. If the user requested only that the change be started, stop after scaffolding and report this status.
3. Otherwise process only requested artifacts, in live dependency order. From status parse `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, and each artifact's `id`, CLI state (`ready`, `blocked`, `done`, or `skipped`), and `missingDeps`; use returned paths exactly and never assume familiar artifact names or a static graph.
4. For each requested artifact that is `ready`, run `openspec instructions "<artifact-id>" --change "<name>" --json` with the sticky store flag.
5. Before writing, evaluate any condition stated in that artifact's `instruction` against the explored change. If it does not apply, record and report a deliberate conditional skip; do not reconsider it during this capture.
6. If a requested artifact is `blocked` by a direct prerequisite the user did not request, run `openspec instructions "<prerequisite-id>" --change "<name>" --json` with the sticky store flag even when that prerequisite is itself `blocked`. Evaluate only a condition stated in that prerequisite's own `instruction`. Record a deliberate skip when it does not apply. If it applies or is not conditional, explain the dependency and ask before expanding scope; never create an unrequested prerequisite without approval.
7. For an artifact being created, parse and obey `artifactId`, `changeName`, `schemaName`, `changeDir`, `description`, `instruction`, `template`, `dependencies`, `unlocks`, `skipped`, `warning`, `context`, `rules`, `references`, and `resolvedOutputPath`. Re-read completed dependency files reported in `dependencies`; a skipped dependency has no file. Use `context`, `rules`, and referenced-store information as constraints, not artifact content. Honor any explicit creation delegation in the live instruction without inventing a selector. Write only to `resolvedOutputPath`; when it is a glob, use the instruction to select a concrete matching path. Verify that concrete output exists. When this artifact's live instruction is the proposal/intent instruction requiring an explicit no-spec declaration, apply the narrow metadata rule below after writing it.
8. After each artifact creation, rerun `openspec status --change "<name>" --json` with the sticky store flag. Continue until every requested artifact is `done`, `skipped`, or deliberately condition-skipped.
9. If a requested artifact remains `blocked` solely because of recorded conditional skips, run its `openspec instructions "<artifact-id>" --change "<name>" --json` call despite the blocked status, then create it as in step 7. Do this only when those recorded skips are its sole missing dependencies. Otherwise explain the unrequested prerequisite and ask before expanding capture.

For that live proposal instruction only, classify capability-level behavior from repository evidence and the proposal. If the classification is materially uncertain, ask one focused semantic question before writing metadata. When the proposal establishes zero new or modified capabilities and no spec-level behavior change, locate metadata using `change.metadataPath` from JSON creation when available; otherwise resolve exactly `<changeRoot>/.openspec.yaml`. Require the target to be named `.openspec.yaml` and to remain within the canonical live `changeRoot`; stop on any mismatch or unsafe path. Parse the YAML mapping and use `apply_patch` to set only `skip_specs: true`, preserving every other field. Rerun status and require every artifact whose normalized `outputPath` begins `specs/` to report `skipped` with no existing output. If a proposal being captured instead introduces capabilities into a change that already has `skip_specs: true`, do so only after the behavior classification is explicitly confirmed; remove the `skip_specs` key or set only it to `false`, rerun status, and require those artifacts to be non-skipped. Report and stop on a mismatch. This exception neither authorizes another metadata field nor expands capture beyond the requested proposal semantics.

Use `update_plan` only when a plan materially aids the exploration. Use `apply_patch` for permitted artifact edits. These tools do not widen the action boundary.

# Decision rules

- Let questions emerge from evidence. Surface multiple promising threads rather than running a mandatory questionnaire. Ask only unresolved questions whose answers materially change observable behavior, compatibility, architecture, acceptance criteria, destructive migration, security, interoperability, or a major performance/memory tradeoff; state evidence, viable choices, consequences, and a recommendation when useful.
- For a vague change, test the emerging frame against problem and urgency, desired outcome, scope and capabilities, explicit non-goals, impact, and assumptions. Treat these as discovery lenses, not lifecycle gates.
- Sharpen overloaded domain terms and probe them with concrete normal, boundary, and failure scenarios. Check stated behavior against code and existing artifacts; surface contradictions rather than silently choosing a source.
- For a consequential design, present two or three genuinely viable approaches, never padding the set with a weak option. Compare assumptions, tradeoffs, reversibility, complexity, failure modes, and fit with existing patterns; recommend one when the evidence supports it.
- Prefer deep modules with small stable interfaces when they improve leverage, locality, and testability. Treat seam placement separately from internal structure, avoid speculative indirection, and describe implementation work as coherent vertical outcomes when planning it.
- Do not force formalization. Continue exploring, summarize, or stop when the user has enough clarity.

# Applicable invariants

- Live CLI JSON is authoritative for roots, stores, schemas, artifact states, dependencies, paths, conditions, and instructions. `done` and `skipped` are CLI states, not semantic-quality claims.
- Read repository evidence before theorizing. Separate observation, sourced fact, inference, hypothesis, and user decision.
- Redact secrets and sensitive values from commands, captured output, artifacts, and reports. If redaction removes necessary signal, say what evidence is missing.
- Never write outside an explicitly requested eligible planning output, except for the exact live-proposal `skip_specs` transition above. Preserve unrelated user changes.
- Public behavior, performance/memory, integration, debugging, and research doctrine is loaded only when applicable below; do not recreate it from memory.

# Conditional reference loads

Load a reference only for its stated reason, then apply it within this action's no-implementation boundary:

- `../openspec-shared/references/artifact-quality.md` — when assessing the substance of an intent, behavioral specification, technical design, or implementation-task artifact, including an explicitly requested capture.
- `../openspec-shared/references/performance-memory.md` — when the issue or option can plausibly affect latency, throughput, allocation, resource lifetime, concurrency, buffering, or memory.
- `../openspec-shared/references/integration-correctness.md` — when the subject crosses a protocol, connector, framework, database, external service, or runtime-version boundary.
- `../openspec-shared/references/debugging.md` — when reproducing or diagnosing a bug, failure, flake, or performance regression; follow its diagnosis contract without applying a fix.
- `../openspec-shared/references/research.md` — when repository evidence is insufficient or an exact dependency, protocol, platform, or runtime version controls correctness.
- `../openspec-shared/references/subagents.md` — when a bounded independent read or comparison would materially reduce latency or add an independent evidence axis.

# Relevance-driven delegation

Delegate only after loading `subagents.md` for the exact reason above and follow its complete evidence-packet, route, fork, concurrency, and integration contract. Exploration specialists are read-only. Never dispatch the action role again.

# Completion and reporting

End when the user's question is answered, the uncertainty is accurately bounded, or a material decision or missing evidence blocks further progress. Report the crystallized problem, observations and source locations, options and tradeoffs, recommendation if one emerged, assumptions, contradictions, open questions, and suggested next step. For defect exploration, report the reproduction and evidence trail without a fix. For research, cite the precise source and version. List every planning artifact created or modified and its verified path; if none was requested, say that no artifact or code was changed. A summary is useful but optional—thinking itself can be the outcome.
