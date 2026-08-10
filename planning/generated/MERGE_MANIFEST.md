# OpenSpec Codex distribution merge manifest

Generated: 2026-08-10T17:33:24+02:00 (Europe/Madrid)

This distribution was regenerated from the current local source trees. OpenSpec is the sole workflow authority. Imported repositories supplied engineering techniques only; no generated runtime file depends on or invokes them.

## Source snapshot

| Source | Commit | Version/tag | State | License and attribution |
|---|---|---|---|---|
| `lib/openspec` | `d57889664cab4f2f061d236ec3ff82a5578701bb` | `v1.8.0` | clean | MIT; Copyright (c) 2024 OpenSpec Contributors |
| `lib/openspec-plus` | `b46c6c20402391c62ba5f9747ef65ee758de43c4` | no reachable tag (`b46c6c2`) | clean | MIT; Copyright (c) 2026 sudokar |
| `lib/mattpocock` | `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e` | `v1.2.3` | clean | MIT; Copyright (c) 2026 Matt Pocock |
| `lib/superpower` | `3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9` | `v6.2.0` | clean | MIT; Copyright (c) 2025 Jesse Vincent |

All source trees were treated as read-only. The generated text is a compact distillation rather than substantial copied source text; the source identities and license terms are retained here for provenance.

## Runtime contract

Verified against locally installed `codex-cli 0.147.0`, its installed model catalog and official local documentation:

- custom-agent declarations use TOML fields `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, and `sandbox_mode`;
- the single action/specialist creation mechanism is `spawn_agent` with `task_name`, `message`, optional `fork_turns`, `model`, and `reasoning_effort`;
- a model/effort override uses bounded context (`fork_turns: "1"`) for action routing or clean context (`fork_turns: "none"`) for specialists; full-history forks with overrides are forbidden;
- planning and patch tools are `update_plan` and `apply_patch`;
- accepted efforts used here are `medium`, `high`, and `xhigh`;
- `gpt-5.6-sol` and `gpt-5.6-terra` accept `xhigh`, so no reasoning-effort substitution was made;
- `[agents].max_concurrent_threads_per_session = 3` provides bounded concurrency and does not make parallel writing the default.

The agent TOMLs declare selectable roles; runtime action skills use the verified callable `spawn_agent` contract and do not pretend a TOML filename is a dispatch selector.

## Discovered OpenSpec surface and generated counterparts

The generator in `lib/openspec/src/core/shared/skill-generation.ts` enumerates 12 skills. The current template machinery also exports feedback as an optional actionable surface that is not in that generated list. Store selection is shared CLI guidance, not a separate action. `openspec-shared` is packaging-only and passive.

| Kind | Current OpenSpec surface | Generated counterpart |
|---|---|---|
| generated skill | `explore` | `.codex/skills/openspec-explore/SKILL.md` |
| generated skill | `propose` | `.codex/skills/openspec-propose/SKILL.md` |
| generated skill | `new-change` | `.codex/skills/openspec-new-change/SKILL.md` |
| generated skill | `continue-change` | `.codex/skills/openspec-continue-change/SKILL.md` |
| generated skill | `ff-change` | `.codex/skills/openspec-ff-change/SKILL.md` |
| generated skill | `update-change` | `.codex/skills/openspec-update-change/SKILL.md` |
| generated skill | `apply-change` | `.codex/skills/openspec-apply-change/SKILL.md` |
| generated skill | `verify-change` | `.codex/skills/openspec-verify-change/SKILL.md` |
| generated skill | `sync-specs` | `.codex/skills/openspec-sync-specs/SKILL.md` |
| generated skill | `archive-change` | `.codex/skills/openspec-archive-change/SKILL.md` |
| generated skill | `bulk-archive-change` | `.codex/skills/openspec-bulk-archive-change/SKILL.md` |
| generated skill | `onboard` | `.codex/skills/openspec-onboard/SKILL.md` |
| optional action | `feedback` | `.codex/skills/openspec-feedback/SKILL.md` |
| passive package index | shared doctrine references | `.codex/skills/openspec-shared/SKILL.md` and `references/*.md` |

Generated counts: 12 authoritative generated counterparts, 1 optional action counterpart, 1 passive shared index, 13 action-agent declarations, and 9 specialist-agent declarations.

No previous `planning/generated/MERGE_MANIFEST.md` existed, so this run has no earlier generated baseline to diff. The current source snapshot establishes the regeneration baseline; no legacy generated behavior was preserved for its own sake.

## Action model matrix

| Action and action agent | Model | Effort | Sandbox |
|---|---|---|---|
| `openspec-explore` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-propose` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `openspec-new-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-continue-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-ff-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-update-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-apply-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-verify-change` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `openspec-sync-specs` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-archive-change` | `gpt-5.6-terra` | `high` | `workspace-write` |
| `openspec-bulk-archive-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-onboard` | `gpt-5.6-terra` | `medium` | `workspace-write` |
| `openspec-feedback` | `gpt-5.6-terra` | `high` | `read-only` |

`openspec-verify-change` permits workspace writes only for ordinary build/test outputs; it forbids authored repository edits.

## Specialist model matrix

| Specialist | Model | Effort | Sandbox |
|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | `high` | `read-only` |
| `opsx-docs-researcher` | `gpt-5.6-terra` | `high` | `read-only` |
| `opsx-slice-implementer` | `gpt-5.6-terra` | `high` | `workspace-write` |
| `opsx-debugger` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `opsx-test-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-api-compat-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | `xhigh` | `read-only` |

The slice implementer deliberately uses `gpt-5.6-terra` at `high`, not the earlier repository contract's medium effort, because connector slices can involve concurrency, resource lifetimes, and conversion edge cases.

## Imported concepts and destinations

| Source | Distilled concepts | Canonical generated destinations |
|---|---|---|
| OpenSpec Plus | structured discovery; proposal quality; testable specifications; alternatives and tradeoffs; structural fidelity; vertical/outcome-shaped tasks; artifact-aware apply evidence; independent review orchestration | action-specific decision rules; `artifact-quality.md`; `evidence-first.md`; `review.md`; conditional delegation in apply/verify |
| mattpocock/skills | vertical slices; deep modules behind small stable interfaces; design-it-twice; minimized reproduction; hypothesis and boundary instrumentation; independent code/spec review; primary-source research; useful domain modeling | `artifact-quality.md`; `evidence-first.md`; `debugging.md`; `review.md`; `research.md`; relevant planning/apply actions |
| obra/superpowers | root-cause tracing; condition-based waiting; defense in depth; verification before completion; requesting/receiving review discipline; safe parallel-subagent hygiene | `debugging.md`; `evidence-first.md`; `review.md`; `subagents.md` |

Canonical shared owners are `artifact-quality.md`, `evidence-first.md`, `api-semver.md`, `performance-memory.md`, `integration-correctness.md`, `debugging.md`, `review.md`, `research.md`, and `subagents.md`. Action skills load them only when their subject is relevant.

## Deliberately rejected concepts

- Imported lifecycle controllers, orchestrators, setup/update skills, and user-facing alternatives to OpenSpec change management.
- Standalone Plus runtime skills and every instruction requiring invocation of an imported skill.
- Unconditional test-first slogans; the distribution instead owns one evidence-before-claims discipline.
- Imported brainstorming/planning/execution/branch-finishing workflows, universal questionnaires, routine per-artifact approval gates, and automatic apply/archive transitions.
- Mandatory worktrees, branches, commits, publishing, or branch-finishing behavior.
- Multiple retry/debug counters, duplicate review doctrines, motivational/marketing prose, vendor-specific tool syntax, slash commands, and pseudo-tools.
- Mocks used as substitutes for protocol/integration evidence when real boundary evidence is necessary.

## Global conflict resolutions

- OpenSpec templates, generators, schemas, live CLI payloads, and action boundaries override lagging generated skills and every imported technique.
- Action routing was changed from invalid full-history model overrides and unselectable role-name assumptions to one verified, bounded `spawn_agent` route with explicit model/effort and a nonrecursive action marker.
- Apply, onboard, archive, and bulk-archive ordering was restored to current OpenSpec semantics; imported review rigor remains within native readiness and reporting boundaries.
- Proposal-producing actions implement the schema-required, narrowly contained `skip_specs` forward/inverse metadata transition; `new-change` still stops before producing the proposal and never infers it.
- List consumers obtain schema/artifact state from per-change status rather than fields absent from `list --json`; onboarding runs root-sensitive schema discovery in the selected store root.
- Feedback is an optional read-only action; the 12 generated skills remain exactly the current generator surface.
- Shared doctrine was deduplicated to one owner per concern, including exactly one diagnosis failure counter in `debugging.md`.
- Reviewers receive artifacts, diffs, criteria, and raw evidence rather than an implementer's reasoning transcript. Parallel writers require demonstrably disjoint ownership.
- Runtime skills do not depend on the planning contract file, staging paths, agent TOML activation, or imported repositories.

## Audit and evaluation disposition

- Fresh contradiction audit: **PASS**, 0 BLOCKER, 0 MAJOR, 2 MINOR, 0 NOTE.
- Fresh behavioral evaluation: **ACCEPTABLE**, 0 BLOCKER, 0 MAJOR, 1 MINOR, 3 NOTE.
- Shared minor: verify's ambiguous multi-candidate filter cannot reliably identify a custom-schema implementation-task artifact from status alone. Explicit selection and post-selection verification remain correct.
- Audit-only minor: nine staging-only rewrite reports have stale shared-reference inventories. Runtime reference links and conditional loads are correct; rewrite reports are not published.
- Behavioral notes: the public tracking-path limitation is handled safely; verify's wider sandbox is restricted to build/test outputs; feedback is optional rather than a resurrected generated action.

No BLOCKER or MAJOR finding remains.

## Deterministic checks and tests

Passed:

- 12/12 generated OpenSpec skills have exactly one counterpart; optional feedback and passive shared are categorized separately.
- 14/14 staged `SKILL.md` files have YAML frontmatter containing only `name` and `description` and pass the local skill validator.
- 22/22 agent TOMLs parse and contain explicit recognized GPT-5.6 model, accepted effort, sandbox, and required declaration fields.
- The OpenSpec YAML and Codex fragment TOML parse; bounded concurrency is 3.
- Every runtime link resolves; every agent points to a real generated skill; all action routes use the single bounded dispatch mechanism; no recursive route is present.
- Exactly one numeric diagnosis failure counter exists; shared TDD/debug/review doctrine is not duplicated.
- No runtime invocation of imported sources, unavailable Plus skills, foreign agent syntax, slash commands, pseudo-tools, `.claude` output, or generated symlink exists.
- Current OpenSpec CLI names, flags, parsed fields, artifact names, action ordering, and multi-artifact boundaries were checked against this checkout.
- `bash -n install.sh`, `git diff --check`, and a clean-destination installer exercise against a local generated release archive pass.

The repository has no top-level `tests/` directory, so the requested root test suite does not exist and could not be run. `lib/openspec/node_modules` is absent, and no package installation was authorized or performed; upstream OpenSpec's dependency-backed suite was therefore not run. These are recorded limitations, not passing test claims.

## Publication inventory

- `.codex/skills/openspec-*/SKILL.md`
- `.codex/skills/openspec-shared/references/*.md`
- `.codex/agents/openspec-*.toml`
- `.codex/agents/opsx-*.toml`
- `.codex/config.toml.fragment`
- `openspec/config.yaml`
- `planning/generated/MERGE_CONTRACT.md`
- `planning/generated/MODEL_MATRIX.md`
- `planning/generated/MERGE_MANIFEST.md`
- `planning/generated/AUDIT_REPORT.md`
- `planning/generated/BEHAVIOR_EVAL.md`

No user configuration was overwritten, no source tree under `lib/**` was changed, and no commit was created.
