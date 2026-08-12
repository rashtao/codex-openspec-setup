# Phase H behavioral evaluation

## Verdict

**ACCEPTABLE for Phase H.** The staged distribution preserves the current OpenSpec lifecycle across the representative scenarios and actions. Added engineering rigor remains conditional and does not introduce a second workflow, unconditional verification gate, extra archive gate, or implicit transition into another action.

| Severity | Count |
|---|---:|
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 1 |
| NOTE | 3 |

The acceptance requirement of zero BLOCKER and zero MAJOR findings is met.

## Evaluation basis and method

This was a fresh, read-only behavioral walk-through of the current authority and current staging. The previous `staging/BEHAVIOR_EVAL.md` and `staging/AUDIT_REPORT.md` were not used as inputs.

Authority inspected:

- current generated surface in `lib/openspec/src/core/shared/skill-generation.ts:59-105`;
- current workflow templates under `lib/openspec/src/core/templates/workflows/` and their generated counterparts under `lib/openspec/skills/`;
- current schema and proposal instruction in `lib/openspec/schemas/spec-driven/schema.yaml:15-71`;
- current status, instruction, list, new-change, store, schema-discovery, metadata-marker, validation, archive, and feedback code;
- staged `MERGE_CONTRACT.md`, all 13 action counterparts, all shared references, all action/specialist agent declarations, `MODEL_MATRIX.md`, and the staged OpenSpec config.

Because the evaluator was constrained to read-only operation except for this report, action mutations were not executed. Each scenario was instead traced through the exact commands, parsed fields, decisions, permitted writes, stop conditions, and ordering stated by the staged skill, then compared with the current template and CLI implementation.

The current enumerator exposes exactly 12 generated actions (`explore`, `new`, `continue`, `apply`, `update`, `ff`, `sync`, `archive`, `bulk-archive`, `verify`, `onboard`, and `propose`). The current exported-but-unenumerated feedback template is covered by the thirteenth, explicitly optional `openspec-feedback` counterpart. `openspec-shared` remains passive. Generated counts: 12 authoritative generated counterparts, 1 optional action counterpart, 1 passive shared index, 13 action-agent declarations, and 8 specialist-agent declarations.

## Control-plane invariants

### CLI fields and dynamic schema state

PASS.

- Staged actions use the live `status --json` graph and preserve `planningHome`, `changeRoot`, `artifactPaths`, `outputPath`, `resolvedOutputPath`, `existingOutputPaths`, `applyRequires`, artifact states, and dependency edges rather than reconstructing familiar spec-driven paths.
- `openspec list --json` is correctly treated as containing only `name`, task counts, derived task status, `lastModified`, and response-level root. Current code confirms that shape at `lib/openspec/src/core/list.ts:141-150`. Actions obtain per-candidate `status --json` before showing schema or filtering on artifact/delta inventory; no staged action defaults a missing list field to `spec-driven`.
- The public apply payload is correctly treated as exposing `contextFiles`, `tasks`, `progress`, `state`, and `missingArtifacts`, but not the concrete `apply.tracks` path. Current CLI construction confirms the private tracking lookup and public payload split at `lib/openspec/src/commands/workflow/instructions.ts:381-470`.
- `context` is treated as a required project constraint, artifact-keyed `rules` constrain the relevant artifact or sync output, `operationGuidance` remains advisory, and referenced-store material remains read-only.

### Registered stores and schema-discovery working directory

PASS.

The registered-store trace is bounded and store-aware:

1. Resolve only a registered id through `openspec store list --json` and retain its root.
2. Keep `--store <id>` sticky only on commands that support it.
3. Never pass `--store` to `openspec schemas`.
4. Run `openspec schemas --json` with its working directory set to the selected planning root. This matters because current schema discovery uses `process.cwd()` (`lib/openspec/src/commands/workflow/schemas.ts:22-28`).
5. Use the returned `planningHome.root`, `planningHome.changesDir`, `changeRoot`, and artifact paths for every later read or write.
6. Stop on an invalid/unavailable selected store rather than silently falling back to the local root.

`new-change`, `ff-change`, `propose`, and `onboard` all preserve this root-sensitive schema-discovery behavior. Read/update/apply/sync/archive/verify actions retain the selected id throughout their supported CLI calls.

### Routing, forks, and markers

PASS.

- All 13 action counterparts have a nonrecursive `ROUTED_ACTION=<action>` guard and exactly one top-level action route with explicit model, explicit effort, and `fork_turns: "1"`.
- The routed message tells the generic child to execute the latest request directly, read the installed action skill, and never route the same action again. The parent waits and does not duplicate work.
- Specialist examples use explicit GPT-5.6 routes and `fork_turns: "none"` with a complete evidence packet. They do not claim that a task label or TOML read activates a custom role.
- All 13 custom action declarations carry the matching routed marker. The eight specialist declarations forbid spawning and self-redispatch. `openspec-shared` has no route.
- Write-capable roles are restricted to action/implementation work; reviewers and researchers are read-only. `openspec-verify-change` has workspace-write only for ordinary build/test outputs and explicitly forbids authored source, artifact, task, spec, archive, Git, configuration, or report changes.

## Representative change scenarios

| Scenario | Expected staged behavior | Result |
|---|---|---|
| Ordinary feature | `propose` or `ff-change` creates one new change, computes the transitive `applyRequires` closure from live edges, writes applicable artifacts in dependency order, and stops before code. Behavioral capability changes produce delta specs. A conditional design is skipped only when its own live instruction says its predicate is false. | PASS |
| Pure refactor | The live proposal has zero new/modified capabilities. The producing action sets only `skip_specs: true`, reruns status, requires every `specs/`-generating artifact to become `skipped` with no output, continues the remaining apply-required closure, and stops before implementation. Apply establishes characterization evidence before structural edits. | PASS |
| Implementation-only bug fix | When the intended contract is unchanged and the defect merely violates it, the proposal uses zero capabilities and the same forward `skip_specs` transition. Apply reproduces and minimizes, obtains defect-sensitive evidence, diagnoses the cause, fixes it, reruns fresh evidence, and checks a task only after proof. If the intended requirement itself changes, this is no longer implementation-only and the inverse transition/spec path applies. | PASS |
| Implementation-only performance regression | With no requirement-level behavior change, specs are skipped through the schema-required marker. Planning/apply still load performance guidance when relevant. Apply records environment, representative workload, and baseline, diagnoses before optimizing, then reruns the same measurement plus correctness evidence. Quantitative improvement is not claimed without measurement. | PASS |
| Implementation-only memory/resource leak | With unchanged externally observable requirements, specs are skipped. Apply uses the single debugging protocol and resource-lifetime/performance evidence, including ownership, cleanup, retention, and relevant concurrency boundaries. Temporary instrumentation is removed before completion. | PASS |
| Connector protocol defect | A restoration of an existing protocol contract may remain implementation-only and use `skip_specs`; a changed wire/transaction/error/lifecycle obligation requires capability/spec changes. Apply selects the narrowest realistic contract/integration evidence rather than using a mock as proof of real protocol behavior. | PASS |
| Framework version incompatibility/upgrade | An internal compatibility repair with no changed support contract may use `skip_specs`; a changed supported-version matrix, lifecycle hook, configuration contract, or observable behavior requires specs. Planning/apply inspect pinned versions and version-matched primary sources when repository evidence is insufficient. | PASS |
| Ambiguous architectural change | Explore/proposal/design compare materially viable approaches and ask only when the unresolved answer changes architecture, behavior, compatibility, acceptance criteria, destructive migration, security, interoperability, or a major performance/resource tradeoff. Routine per-artifact approval is not imported into propose/fast-forward. | PASS |
| Implementation invalidates the design | Apply identifies the exact artifact statement, repository fact, and consequence, then stops without editing planning artifacts or silently coding around the contradiction. It recommends the separate update action. Update edits only confirmed existing `done` outputs; apply resumes only on a fresh request with fresh instructions. | PASS |

### Schema-required `skip_specs` forward and inverse transition

PASS.

The current proposal instruction requires every zero-capability, zero-requirement-change change to set `skip_specs: true` (`lib/openspec/schemas/spec-driven/schema.yaml:24-30`). Current status normalizes `./specs/...`, marks unfinished `specs/`-generating artifacts skipped, and makes them satisfy the graph (`lib/openspec/src/core/artifact-graph/instruction-loader.ts:281-296`).

The staged producing/updating actions (`continue`, `propose`, `ff`, explicit explore capture, onboarding proposal step, and update) implement the same narrow transition:

- act only while producing or revising proposal/intent semantics under the live instruction;
- use `change.metadataPath` when creation returned it, otherwise validate exactly `<changeRoot>/.openspec.yaml`;
- parse YAML and preserve all fields except `skip_specs`;
- forward: set only `skip_specs: true`, rerun status, require normalized `specs/` outputs to be `skipped`, and require no existing spec output;
- inverse: only after confirmed semantics introduce capability-level requirement changes, remove the key or set only it to `false`, rerun status, and require the spec artifacts to re-enter a non-skipped live state;
- stop on invalid metadata, unsafe path, existing conflicting spec output, or state mismatch.

`new-change` correctly never performs this transition because it stops before proposal creation. `update-change` may perform the inverse only as part of the already confirmed proposal revision and still cannot create the now-ready spec artifact; continuation remains a separate action.

## Action boundary and write/stop evaluation

| Action | Authorized writes and required stop | Result |
|---|---|---|
| `openspec-explore` | No code implementation. No capture unless explicitly requested; requested planning capture uses live artifact eligibility and paths. Ends at analysis/capture, not apply. | PASS |
| `openspec-new-change` | Creates only the scaffold (plus explicitly requested scaffold metadata), shows live status and first-ready instructions, then stops before artifact creation. It never infers `skip_specs`. | PASS |
| `openspec-continue-change` | Creates exactly the first live-ready artifact and only the narrow proposal metadata companion when required. Refreshes status and stops after one artifact. | PASS |
| `openspec-propose` | Creates a new change and its transitive apply-required planning closure. No routine artifact approvals and no implementation. Requires a fresh apply request. | PASS |
| `openspec-ff-change` | Same live closure boundary without per-artifact approval; never continues/overwrites an existing change and stops before implementation. | PASS |
| `openspec-update-change` | Serial, per-artifact preview/confirmation; writes only current `done` artifacts at current concrete `existingOutputPaths`, plus the confirmed proposal marker transition. Never creates a missing/glob output or edits code. | PASS |
| `openspec-apply-change` | Implements coherent pending slices, verifies them, and checks a task only through the unique-context-file rule. Stops at `all_done`, a CLI block, a material decision, third failed diagnosis cycle, unsafe overlap, unavailable required evidence, or artifact contradiction. It never edits planning, syncs, or archives. | PASS |
| `openspec-verify-change` | Runs fresh inspection/tests but makes no authored project edit. Reports findings and stops; never fixes or archives. | PASS |
| `openspec-sync-specs` | Semantically merges exactly the selected `existingOutputPaths` subset into main specs under one immutable rules snapshot, validates, and leaves the change active. | PASS |
| `openspec-archive-change` | Preserves warning confirmations and native sync choice. Any chosen sync and full comparison/validation precede the destination-collision check and move. | PASS |
| `openspec-bulk-archive-change` | Explicit selection, complete pre-mutation state, exact-path conflicts, one consolidated confirmation, all needed rules snapshots before writes, then ordered per-change sync/verify/validate and immediate-before-move collision handling. Reports partial results. | PASS |
| `openspec-onboard` | Preserves real task -> exploration -> scaffold -> live artifacts -> implementation -> direct tutorial archive -> recap and only the current teaching pauses. It adds no separate verification phase or pre-archive gate. | PASS |
| `openspec-feedback` | Drafts only from recent conversation, anonymizes, shows the complete draft, requires fresh explicit approval after revisions, invokes `openspec feedback` once, reports the true outcome, and stops. | PASS |

## Focused edge traces

### Custom tracking schema

PASS for implementation and readiness.

The staged apply action reads tasks/progress/state from `instructions apply --json`, reads every concrete `contextFiles` path, and never invents the hidden tracking path. After evidence supports a task, it searches only reported context files for the exact unchecked checkbox text and writes a check only when there is exactly one occurrence in exactly one file. No match, duplicate matches, or a tracking file outside reported context causes a safe block with task state unchanged. Archive and bulk archive likewise use the apply payload for readiness rather than assuming `tasks.md`.

### Single archive target collision

PASS.

The trace is: readiness warnings and confirmations -> delta comparison -> user sync choice -> one rules snapshot if syncing -> synchronous merge -> full original-delta comparison and validation -> derive archive target -> collision check -> move. A collision therefore occurs after any selected sync side effects, preserves `changeRoot`, and never overwrites the destination. This matches current OpenSpec ordering.

### Bulk conflicts and per-change collisions

PASS.

Conflicts use equality of the complete capability path, not basename. Implementation evidence drives include/exclude decisions; multiple implemented deltas apply oldest-to-newest. The user sees one consolidated plan and confirms once. A ready-only choice re-derives conflicts for the reduced set. Every required per-change rules snapshot is frozen before the first mutation. Writes are sequential. A destination collision is deliberately not a prefilter: it is checked only after that change's included deltas have been synced, compared, and validated; that change fails its move while later independent work may continue. Every selected change receives exactly one `Success`, `Failed`, or `Skipped` outcome and excluded deltas are reported separately.

### Feedback

PASS.

The optional counterpart stays outside the lifecycle. It uses recent-conversation evidence only, sanitizes title and body before display, displays the CLI-added prefix/footer effect, invalidates approval after any revision, and invokes only `openspec feedback <title> --body <body>`. The CLI-owned missing-label retry is not duplicated by the agent. Missing/unauthenticated `gh`, other failure, and uncertain outcome are reported without claiming submission.

## Findings

### BLOCKER

None.

### MAJOR

None.

### MINOR

#### M-1 — Verify candidate filtering cannot identify a custom tracking artifact from status alone

`staging/skills/openspec-verify-change/SKILL.md:43` says that, when several candidates exist, the action should ask among candidates whose status reports an “implementation-task artifact.” The current `status --json` payload reports artifact ids, output paths, states, and dependencies, but neither artifact descriptions nor the schema's `apply.tracks` path. For a custom schema whose tracked artifact is not recognizably named `tasks`, status alone cannot prove that classification.

Impact is limited to implicit multi-candidate selection: an explicitly named change proceeds correctly, and the later verification workflow uses the authoritative apply payload. Still, a custom-schema change could be omitted or included by guess during selection.

Recommended correction: during this candidate-filtering branch, either show all active candidates after per-candidate status, or query `openspec instructions apply --change <candidate> --json` and base any task-oriented label on its public `tasks`, `progress`, and `state`. Do not infer the tracking artifact or path.

### NOTE

#### N-1 — Public tracking-path limitation is handled safely

The lack of public `apply.tracks` is not hidden. Apply/onboarding refuse ambiguous checkbox writes, and archive/bulk use public progress/state for warnings.

#### N-2 — Verify's workspace-write sandbox is semantically read-only

The broader sandbox is justified solely by ordinary build/test outputs. Both the skill and custom-agent declaration explicitly prohibit authored project changes.

#### N-3 — Feedback is an optional thirteenth counterpart, not a resurrected generated action

The current enumerator still has 12 generated actions. Feedback is exported by current templates and exposed as one optional counterpart with no lifecycle transition.

## Final assessment

Across the required ordinary feature, pure-refactor, implementation-only bug/performance/leak/framework, connector, ambiguous design, invalid-design discovery, archive collision, bulk conflict, custom tracking, registered-store, feedback, and routing scenarios, the staged behavior preserves current OpenSpec state, questions, writes, stops, and ordering. Added evidence, performance, integration, diagnosis, research, review, and delegation rigor remains relevance-driven. There are no lifecycle-changing findings and no BLOCKER or MAJOR findings.
