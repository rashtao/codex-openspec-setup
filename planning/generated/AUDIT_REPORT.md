# Phase F fresh contradiction audit

Date: 2026-08-10  
Result: **PASS** — the staged set has no BLOCKER or MAJOR finding.

## Finding counts

| Severity | Count |
|---|---:|
| BLOCKER | 0 |
| MAJOR | 0 |
| MINOR | 2 |
| NOTE | 0 |

The acceptance rule is satisfied because BLOCKER and MAJOR are both zero. The two MINOR findings are bounded metadata/discovery defects; neither changes OpenSpec lifecycle semantics, authorizes an unsafe write, or defeats an action boundary.

## Findings

### MINOR-01 — Verify cannot reliably identify an implementation-task artifact for a custom schema

[openspec-verify-change/SKILL.md](skills/openspec-verify-change/SKILL.md) correctly obtains `status --json` for every ambiguous candidate before using schema or artifact inventory. It then filters the choices to candidates whose status “reports an implementation-task artifact.” The current status artifact record exposes only `id`, `outputPath`, `status`, `requires`, and optional `missingDeps`; it has no artifact semantic-role field. The schema artifact definition likewise has an arbitrary id, output path, description, template, instruction, and dependencies, but no standardized “implementation-task” role.

Consequently, this filter can only recognize a custom schema by guessing from an id/path or other convention that the same skill forbids. A valid custom-schema change can be omitted from the ambiguous-selection menu even though verification itself would work after explicit selection by reading the live apply payload and every `contextFiles` entry.

This is MINOR, not MAJOR: explicitly named, conversationally unambiguous, and sole active changes bypass this filter; no write or lifecycle transition occurs during the faulty branch; and the selected-change verification path remains schema-aware. Resolve it by either showing all status-readable candidates without semantic-role filtering or by resolving the active schema/apply tracking semantics explicitly before applying a filter. Continue using per-candidate status for `schemaName` and artifact inventory.

Evidence: [verify selection](skills/openspec-verify-change/SKILL.md), [status payload type](../lib/openspec/src/core/artifact-graph/instruction-loader.ts), and [schema artifact type](../lib/openspec/src/core/artifact-graph/types.ts).

### MINOR-02 — Nine rewrite reports have stale shared-reference inventories

The runtime skills contain valid relative links and correct conditional load reasons, but the corresponding `REWRITE_REPORT.md` inventories were not refreshed after those links were added. The mismatches are:

| Rewrite report | Runtime reference(s) omitted from report |
|---|---|
| [archive-change](skills/openspec-archive-change/REWRITE_REPORT.md) | `evidence-first.md` |
| [continue-change](skills/openspec-continue-change/REWRITE_REPORT.md) | `artifact-quality.md` |
| [explore](skills/openspec-explore/REWRITE_REPORT.md) | `artifact-quality.md` |
| [ff-change](skills/openspec-ff-change/REWRITE_REPORT.md) | `artifact-quality.md`, `review.md` |
| [onboard](skills/openspec-onboard/REWRITE_REPORT.md) | `evidence-first.md`, `debugging.md` (the report currently says none) |
| [propose](skills/openspec-propose/REWRITE_REPORT.md) | `artifact-quality.md`, `review.md` |
| [sync-specs](skills/openspec-sync-specs/REWRITE_REPORT.md) | `artifact-quality.md` |
| [update-change](skills/openspec-update-change/REWRITE_REPORT.md) | `artifact-quality.md` |
| [verify-change](skills/openspec-verify-change/REWRITE_REPORT.md) | `artifact-quality.md` |

The generation brief requires each rewrite report to list every shared reference and the exact reason it may load. This is a documentation/provenance mismatch only: the current runtime skills load the canonical owners conditionally and do not contain broken links. Refresh the nine report inventories from their matching `SKILL.md` files.

## Contradiction matrix

| Axis | Result | Audit conclusion |
|---|---|---|
| OpenSpec authority and artifact source of truth | PASS | Current CLI status/instruction payloads, active schema, templates, context, rules, dependencies, and returned paths remain above generated technique. No staged skill substitutes a familiar static graph for live state. |
| `skip_specs` forward transition | PASS | Only actions producing or revising a proposal under a live instruction may set it. They require semantic classification, ask when materially uncertain, preserve every other YAML field, set only `skip_specs: true`, rerun status, and require every normalized `specs/` generator to be `skipped` with no output. |
| `skip_specs` inverse transition | PASS | The same proposal-scoped actions require explicit confirmed capability-level semantics before removing the key or setting only it to `false`, then rerun status and require the spec-generating artifacts to return to non-skipped state. Arbitrary metadata editing remains forbidden. |
| Metadata path containment | PASS | The transition uses creation JSON `change.metadataPath` when available or exactly `<changeRoot>/.openspec.yaml`, requires the exact basename, and requires canonical containment under canonical `changeRoot`; unsafe paths, invalid YAML, and post-transition state mismatches stop the action. The multi-artifact/revision paths also stop on conflicting spec outputs. |
| New-change stopping boundary | PASS | New-change scaffolds once, reads fresh status, fetches only the first ready artifact instructions, and stops without drafting an artifact or changing `skip_specs`. Removed flags are rejected and returned creation paths/schema are retained. |
| List payload and follow-up status | PASS with MINOR-01 | Skills treat list rows as name/task-count/status/recency plus response root only. Continue, update, archive, bulk, verify, sync, and explore obtain candidate status before schema/artifact/delta use and never default missing schema to `spec-driven`. Verify's semantic candidate filter remains the bounded custom-schema defect above. |
| Onboarding selected-store schema discovery | PASS | Onboard retains `stores[].root` (or `context --json` `root.path`) and runs `openspec schemas --json` with that exact root as cwd. It never passes unsupported `--store` to `schemas`; the unscoped path uses context `root.path` when available. |
| One-hop action routing | PASS | All 13 action skills use the same native `spawn_agent` mechanism, explicit GPT-5.6 model/effort, `fork_turns: "1"`, a `ROUTED_ACTION=<action>` marker, wait-and-relay behavior, and a direct-execution guard. No skill claims that a TOML name or file activates a child role. |
| Specialist forks and recursion | PASS | Specialists receive complete bounded packets, explicit model/effort, and `fork_turns: "none"`; their messages forbid recursion. Existing-agent coordination is not represented as another creation mechanism. Verify supplies concrete calls for its five reviewer forms. |
| Delegation and concurrency ownership | PASS | [subagents.md](skills/openspec-shared/references/subagents.md) uniquely owns generic dispatch, evidence-packet, concurrency, overlap, integration, and coordination rules. Action skills state only action-specific restrictions. The fragment bounds concurrency at three and does not make parallel writing the default. |
| Single archive lifecycle order | PASS | Archive reads advisory inputs and readiness before decisions; a selected semantic sync and full comparison/validation finish before destination collision is checked at the move step. Archive is not substituted for verification. |
| Bulk archive lifecycle order | PASS | Bulk preserves explicit selection, complete state collection, exact-path conflicts, implementation-aware decisions, one consolidated confirmation, all rule snapshots before mutation, ordered sync/verification/validation, and per-change collision immediately before move. Collision is not a prefilter. |
| Onboarding lifecycle | PASS | Onboard preserves the current teaching pauses, implements after the live planning graph, then invokes the current archive command directly. It adds neither a separate verify phase nor a new pre-archive sync/approval gate. |
| Propose/fast-forward boundaries | PASS | Both produce the live transitive apply-required planning closure and stop. Neither imports per-artifact approval or begins implementation; apply requires a fresh request. |
| Apply and planning contradictions | PASS | Apply obeys live apply state and context, checks only uniquely locatable tracked tasks after evidence, and pauses on a planning contradiction. It does not edit planning artifacts or automatically resume after suggesting an update. |
| Task completion and missing tracking path | PASS | The distribution does not invent a public `apply.tracks` response field. It uses `tasks`, `progress`, `state`, and `contextFiles`; checkbox writes require a unique exact match. `all_done`, `ready`, and `blocked` retain their current meanings. |
| Evidence and review independence | PASS | [evidence-first.md](skills/openspec-shared/references/evidence-first.md) owns pass/completion evidence and [review.md](skills/openspec-shared/references/review.md) owns independent findings. Reviewers receive artifacts, diffs, standards, and raw evidence rather than the implementer's private reasoning; implementers retain fixes. |
| Debugging and failure counters | PASS | [debugging.md](skills/openspec-shared/references/debugging.md) contains the distribution's sole numeric failure counter: stop on the third failed cycle for the same failure. No second retry/failure counter was found. |
| Performance/memory, integration, research | PASS | Each doctrine has one shared owner and is loaded conditionally. Action skills add only scope-specific triggers or consequences; none introduces a competing classification, measurement, integration, or sourcing authority. |
| Questions and confirmations | PASS | Questions are limited to action-native choices and material semantic uncertainty. Update retains per-artifact approval, archives retain their current confirmations, feedback requires approval, and onboarding retains teaching pauses; no imported universal questionnaire or extra lifecycle gate remains. |
| Models, efforts, and sandboxes | PASS | The model matrix matches all 21 agent TOMLs. Review/research specialists and feedback are read-only; writers are workspace-write. Verify's workspace-write exception is limited and documented for ordinary build/test outputs while authored repository edits remain forbidden. |
| Codex config contract | PASS | Local Codex CLI 0.147.0 exposes stable `multi_agent`; the callable contract accepts the staged `fork_turns`, `model`, and `reasoning_effort` fields. The agent declarations use the recognized name/description/developer-instructions/model/effort/sandbox fields, and `[agents].max_concurrent_threads_per_session = 3` matches the local config schema. |
| Generated, optional, and passive categorization | PASS | The current generator enumerates exactly 12 action skills. The staged set has those 12 plus exported-but-not-enumerated optional feedback. `openspec-shared` is a passive reference index with no routing guard, lifecycle, or action authority. |
| Feedback | PASS | Feedback is read-only until explicit draft approval, invokes the current command once, reports the actual result, and stops. It is correctly modeled as an optional action, not a generated counterpart. |
| Git/worktree policy | PASS | No action silently commits, branches, publishes, or creates a worktree. Sync's mention of Git checkout is a guarded recovery technique for a failed write, not a lifecycle substitution. |
| Config and runtime dependencies | PASS | The staged OpenSpec config replaces unavailable Plus invocations with mandatory conditional loads of installed shared references while preserving their force. Runtime files do not invoke imported Plus, mattpocock, or Superpowers skills. |
| Links and packaging | PASS with MINOR-02 | Runtime/shared links resolve, every `openspec-*` directory has a real `SKILL.md`, no staged skill/OpenSpec symlink exists, and YAML/TOML parse. Rewrite-report inventories have the non-runtime omissions listed above. |

## Mechanical evidence

- Authoritative generated counterparts: 12.
- Staged action skills: 13 (12 generated counterparts plus optional feedback).
- Passive shared skill indexes: 1.
- Action-agent TOMLs: 13; specialist TOMLs: 8.
- All 21 agent TOMLs contain `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, and `sandbox_mode` and parse successfully.
- All 14 staged `SKILL.md` frontmatters parse and contain only `name` and `description`; staged `release/openspec/config.yaml` parses.
- Staged skill/OpenSpec symlinks: 0.
- Shared doctrine owners: 8; numeric failure-counter owner hits: 1 (`debugging.md` only).
- All relative links in the staged runtime and generated supporting Markdown checked for this audit resolve.
- The staged config fragment parses and uses bounded concurrency (`3`).

## Final disposition

No staged runtime action contains a blocker or major cross-skill contradiction. Publication is acceptable under the stated Phase F gate, with MINOR-01 and MINOR-02 retained as explicit follow-up work rather than hidden or inflated into lifecycle failures.
