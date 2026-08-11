# OpenSpec Codex Merge Contract

This contract fixes precedence, action boundaries, runtime layout, doctrine ownership, and dispatch representation for this generated distribution. OpenSpec is the sole workflow authority. Imported repositories contribute engineering techniques only; they do not contribute actions, lifecycle phases, approval gates, state, or runtime dependencies.

## 1. Generated surfaces and installed layout

The current OpenSpec enumerators generate exactly these 12 action counterparts:

`openspec-explore`, `openspec-new-change`, `openspec-continue-change`, `openspec-apply-change`, `openspec-update-change`, `openspec-ff-change`, `openspec-sync-specs`, `openspec-archive-change`, `openspec-bulk-archive-change`, `openspec-verify-change`, `openspec-onboard`, and `openspec-propose`.

`feedback.ts` is exported but not enumerated. This distribution therefore also provides `openspec-feedback` as one optional action counterpart, explicitly outside the 12 generated counterparts. `openspec-shared` is a passive reference index required by the generation brief; it is never an action trigger.

Runtime dependencies have one installed layout:

- action skills: `.codex/skills/<action>/SKILL.md`;
- optional feedback counterpart: `.codex/skills/openspec-feedback/SKILL.md`;
- canonical shared doctrine: `.codex/skills/openspec-shared/references/*.md`;
- passive reference index: `.codex/skills/openspec-shared/SKILL.md`.

This contract is a generation, integration, and audit artifact. Runtime skills, generic spawned children, custom-agent declarations, specialist-agent declarations, and OpenSpec configuration must not read this contract, `MODEL_MATRIX.md`, another file under `planning/generated/**`, or anything under `staging/**`. Contract requirements are compiled into the installed action skills, canonical shared references, and each agent's self-contained bounded role constraints. Action agents read the corresponding installed action skill; specialists read only the canonical shared references relevant to their role.

`store-selection.ts` remains shared command guidance, not an action. `lib/openspec/skills/**` is only a lag check; current templates, generators, schemas, CLI state, and instruction machinery control.

## 2. OpenSpec action boundaries

An action may be strengthened only inside its current boundary. It preserves current CLI-derived state, artifacts, choices, side effects, ordering, and stopping point.

| Surface | Boundary |
|---|---|
| `openspec-explore` | Think, inspect, compare, research, or reproduce without implementing application code. Capture planning only on explicit request. |
| `openspec-new-change` | Scaffold, show live status, fetch the first ready artifact instructions, and stop before creating an artifact. It never infers or edits `skip_specs`. |
| `openspec-continue-change` | Create exactly the first live-ready artifact from current instructions, report unlocks, and stop. |
| `openspec-propose` | Create a new change and its transitive apply-required planning closure, then stop before implementation and require a fresh request. |
| `openspec-ff-change` | Create a new change and its live apply-required planning closure without per-artifact approvals, then stop before implementation. |
| `openspec-update-change` | After the existing per-artifact confirmations, edit only existing outputs of live `done` planning artifacts. Never create or implement. |
| `openspec-apply-change` | Follow live apply state and context, implement pending work until `all_done` or blocked, and check only safely located completed tasks. If implementation exposes a planning contradiction or design problem, pause, suggest the appropriate artifact update, report, and wait. Do not edit planning artifacts or resume automatically. |
| `openspec-verify-change` | Inspect artifacts, implementation, and fresh evidence and report findings. Commands may write ordinary build/test outputs, but the action must never edit source, planning artifacts, task state, specs, archive state, or a repository report. |
| `openspec-sync-specs` | Semantically merge the selected existing delta outputs into main specs, validate, and leave the change active. |
| `openspec-archive-change` | Disclose current warnings, resolve the native sync choice, perform and compare any chosen sync, and only then check the target collision and move. |
| `openspec-bulk-archive-change` | Preserve explicit selection, all-state collection, exact-path conflicts, implementation-aware decisions, one confirmation, all rule snapshots before mutation, ordered per-change sync/verify/validate, and final per-change destination collision/move outcomes. A collision is not a prefilter and does not remove or rederive deltas before sync. |
| `openspec-onboard` | Preserve the current guided teaching order and only its current pauses: real task, exploration, scaffold, live artifacts, implementation, archive, recap. Do not insert a separate verification phase or a new pre-archive gate. |
| Optional `openspec-feedback` | Draft from recent conversation evidence, anonymize, show the full draft, require explicit approval, invoke the current OpenSpec feedback command once, report its result honestly, and stop. |

Single archive retains its current incomplete-artifact and incomplete-task warning confirmations. Bulk archive retains its single consolidated confirmation and partial-result semantics. No action silently begins another action.

## 3. CLI authority and custom tracking limitation

For every invocation, query current CLI JSON. The active schema and returned artifact graph own ids, dependencies, paths, templates, instructions, apply configuration, state, and eligibility. Use reported `planningHome`, `changeRoot`, `artifactPaths`, `resolvedOutputPath`, `existingOutputPaths`, `contextFiles`, `applyRequires`, and state exactly; never reconstruct them from familiar spec-driven names.

The public apply-instructions payload reports `tasks`, `progress`, `state`, and `contextFiles`, but does not report the schema's concrete `apply.tracks` path. Do not invent such a field.

- Apply may change a checkbox only when the exact pending checkbox text occurs in exactly one reported context file. If that mapping is absent or ambiguous, stop blocked, leave task state unchanged, and report the CLI limitation.
- Archive readiness may use `openspec instructions apply --change "<name>" --json` and its live `tasks`, `progress`, and `state` for warnings without claiming a tracking path.
- Bulk archive may use those fields for consolidated readiness. Onboarding may locate an exact checkbox only by the same unique-context-file rule; otherwise it pauses safely with the limitation.

`context` is a required project constraint; artifact-keyed `rules` constrain that artifact; `operationGuidance` is advisory. None changes CLI state or an action boundary. Delta sources remain only the reported existing spec outputs.

The live spec-driven proposal instruction itself requires a zero-capability, zero-requirement-change proposal to set `skip_specs: true`. An action currently producing or updating that proposal semantics may make only that exact metadata transition as part of satisfying the live instruction. It preserves every other metadata field, uses the CLI-returned `metadataPath` when available or the exact validated `<changeRoot>/.openspec.yaml` otherwise, reruns status, and requires artifacts generating under `specs/` to become `skipped`. If an explicitly confirmed proposal revision introduces capability-level requirement changes into a previously skipped change, the same action may remove or disable only `skip_specs`, rerun status, and require those artifacts to re-enter live state. Uncertain behavior classification requires a semantic question. This is schema-instruction compliance inside proposal production, not a separate action or authority for arbitrary metadata edits.

`openspec list --json` change rows contain only `name`, task counts, derived task status, and `lastModified`, plus response-level root context. Obtain per-candidate `status --change "<name>" --json` before displaying or filtering on schema, artifact inventory, or delta presence. Do not default a missing list field to `spec-driven`.

## 4. Native questions and lifecycle order

Preserve only questions belonging to the current action or a material unresolved semantic decision. Native questions include ambiguous selection, update's per-artifact confirmation, archive warnings and sync choice, bulk selection and consolidated confirmation, feedback approval, and current onboarding teaching pauses. Do not import per-artifact approval into propose/fast-forward or add verification/archive gates.

Current archive collision ordering is authoritative:

- single archive: chosen sync and full post-sync comparison precede target collision detection at the move step;
- bulk archive: confirmed deltas and rule snapshots remain intact through ordered sync/verification/validation; target collision is checked for that change only immediately before its move and is reported as that change's failure.

## 5. Canonical doctrine owners

Operational doctrine has exactly one owner. The contract establishes ownership and precedence; action skills and agent declarations load an owner conditionally and state only action- or role-specific deltas.

| Doctrine | Canonical owner |
|---|---|
| Planning-artifact substance and traceability | [artifact-quality.md](../../.codex/skills/openspec-shared/references/artifact-quality.md) |
| Evidence, task-completion proof, and pass claims | [evidence-first.md](../../.codex/skills/openspec-shared/references/evidence-first.md) |
| Public API and release impact | [api-semver.md](../../.codex/skills/openspec-shared/references/api-semver.md) |
| Performance and memory | [performance-memory.md](../../.codex/skills/openspec-shared/references/performance-memory.md) |
| Connector and framework integration | [integration-correctness.md](../../.codex/skills/openspec-shared/references/integration-correctness.md) |
| Diagnosis and the distribution's sole numeric failure counter | [debugging.md](../../.codex/skills/openspec-shared/references/debugging.md) |
| Independent review | [review.md](../../.codex/skills/openspec-shared/references/review.md) |
| Version-specific external research | [research.md](../../.codex/skills/openspec-shared/references/research.md) |
| Delegation, evidence packets, and concurrency | [subagents.md](../../.codex/skills/openspec-shared/references/subagents.md) |

## 6. Representable dispatch

The only new-agent callable shape is:

```text
spawn_agent({ task_name, message, fork_turns?, model?, reasoning_effort? })
```

`task_name` is only a label. There is no callable custom-agent selector, and reading a TOML file does not activate its developer instructions or defaults.

Every spawn with explicit `model` or `reasoning_effort` sets an explicit partial fork:

- top-level action routing uses `fork_turns: "1"`, so the latest user request is available;
- a specialist whose message contains the complete evidence packet uses `fork_turns: "none"`.

An action skill implements one representable nonrecursive guard. If its current task prompt already contains `ROUTED_ACTION=<action>`, it executes directly and never routes that action again. Otherwise it spawns exactly once with the action route in [MODEL_MATRIX.md](MODEL_MATRIX.md); the message contains `ROUTED_ACTION=<action>`, instructs the child to execute the latest user request directly, tells it to read `.codex/skills/<action>/SKILL.md`, and forbids routing the same action again. The parent waits and returns the child's result without duplicate work.

Specialist messages contain the full bounded objective, exact scope, authoritative artifacts, raw evidence, constraints, expected return, and no-recursion instruction. They do not claim custom-TOML activation. Custom-agent TOMLs independently include the appropriate routed marker for runtimes that actually select them.

Existing-agent coordination is not another creation mechanism. The canonical coordination and concurrency rules are owned by [subagents.md](../../.codex/skills/openspec-shared/references/subagents.md).

## 7. Model and sandbox ownership

[MODEL_MATRIX.md](MODEL_MATRIX.md) is the canonical model/effort/sandbox matrix. Every action and specialist TOML explicitly declares all required fields and matches it. Reviewers and research specialists remain `read-only`; implementation writers remain `workspace-write`. `openspec-verify-change` is `workspace-write` solely so fresh tools may create ordinary build/test outputs, while its skill and TOML strictly forbid source, artifact, task, spec, archive, Git-state, or report edits.

## 8. Precedence

When rules differ, lower authority never weakens higher authority:

1. Explicit user instruction compatible with the current action.
2. Current OpenSpec CLI state, schemas, generated instructions, artifact semantics, and action boundaries.
3. This contract.
4. Action-specific generated rules.
5. Imported engineering techniques.

Live state and built-in action semantics control operation; the active schema's instruction/template control artifact output; project context and artifact-keyed rules constrain output; operation guidance advises execution. Surface conflicts rather than silently resolving them against the higher authority.

## 9. Forbidden substitutions

Runtime content must not invoke imported skills or lifecycle controllers; introduce a second lifecycle; emit slash-command or pseudo-tool syntax; invent a custom-agent selector or custom CLI field; rely on full-history forks with model/effort overrides; claim that reading TOML activates a role; duplicate canonical doctrine; or silently commit, branch, create worktrees, publish, submit feedback, sync, archive, edit planning, or implement outside the current action.

Imported techniques remain subordinate, conditional techniques inside the owning OpenSpec action. They never create new artifacts, phases, gates, counters, or runtime dependencies.
