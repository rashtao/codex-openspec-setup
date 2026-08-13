# Regenerate ALL OpenSpec skills for Codex CLI + GPT-5.6

You are the **merge orchestrator**. Your job is to regenerate, from scratch, a complete
OpenSpec skill distribution for this repository: every OpenSpec skill and every optional
OpenSpec action found in the local OpenSpec checkout, hardened with engineering
disciplines distilled from OpenSpec Plus, mattpocock/skills, and obra/superpowers.

This is a **generation task**. Output is disposable and will be regenerated whenever any
upstream source changes. Never hand-preserve previous generated behaviour.

Target runtime: **Codex CLI only**, GPT-5.6 model family. This project develops **database
connectors and framework integrations**: protocol correctness, performance and memory
efficiency are first-class correctness concerns.

## 0. Non-negotiable objective

**OpenSpec is the one and only workflow.** The generated system may make an OpenSpec
action markedly more rigorous. It MUST NOT:

- introduce a second lifecycle, or rename/reorder OpenSpec's artifact sequence;
- replace OpenSpec change management or reinterpret OpenSpec CLI state;
- substitute another framework's action for an OpenSpec action;
- require the user to invoke OpenSpec Plus, mattpocock, or Superpowers skills at runtime;
- add mandatory phase transitions or approval pauses that the current OpenSpec action
  does not itself require;
- grant any imported source authority over OpenSpec.

Imported repositories are **source material to distil**, never runtime dependencies.
If an imported rule conflicts with current OpenSpec behaviour, modify or discard it.

**The final generated set MUST be free of internal contradictions.** A single stated rule
with one owner beats three nearly identical rules.

## 1. Source trees (read-only)

- `lib/openspec` — authoritative workflow
- `lib/openspec-plus`
- `lib/mattpocock`
- `lib/superpower`

Never modify anything under `lib/**`. Never fetch other versions; the local trees are
authoritative for this run, including any dirty working-tree content.

Before rewriting anything, record for the manifest: each tree's commit hash, tag/version
if any, dirty status, and license terms.

Use the actual files. Do not rely on recollection of these projects.

## 2. Discover the OpenSpec surface dynamically

Do NOT hard-code a skill list.

1. Read the skill **templates and generators** (e.g. `lib/openspec/src/core/templates/`,
   `src/core/shared/skill-generation.ts`, `skill-paths.ts`, `skill-content-equivalence.ts`)
   plus `lib/openspec/schemas/`, the CLI instruction machinery, and `lib/openspec/skills/`.
2. Treat **templates/generators as the source of truth**; `lib/openspec/skills/*` is
   generated output that may lag. Where they differ, follow the templates and note it.
3. Enumerate: every skill, every command/action (including optional ones and aliases),
   every artifact type, every CLI call and parsed field, and every documented action
   boundary.
4. Cover **every** skill/action present in this checkout. Include newly appeared ones
   automatically. Do not resurrect ones that disappeared.

For orientation only (NOT authoritative): `openspec-explore`, `openspec-propose`,
`openspec-new-change`, `openspec-continue-change`, `openspec-ff-change`,
`openspec-update-change`, `openspec-apply-change`, `openspec-verify-change`,
`openspec-sync-specs`, `openspec-archive-change`, `openspec-bulk-archive-change`,
`openspec-onboard`.

## 3. Verify the Codex runtime contract before writing any dispatch syntax

Determine, from the locally installed Codex CLI and its configuration/docs (and, as a
local sample, `lib/superpower/.codex-plugin/`):

- the exact custom-agent/subagent configuration format and field names;
- accepted `model_reasoning_effort` values — **if `xhigh` is not accepted by this build,
  use `high`** and record the substitution;
- the exact subagent dispatch mechanism and its parameters;
- the planning tool (`update_plan`) and patch tool (`apply_patch`) names.

Record the verified contract in the merge contract. **Every generated skill must use one
single verified dispatch mechanism.** Never invent tool names. Never emit pseudo-tools
(`todowrite`, generic "question tool", "skill tool"), slash commands, or Claude/OpenCode/
Cursor/Windsurf/Gemini agent syntax.

## 4. Repository packaging constraints (hard)

Read `install.sh` and `tests/` before generating. The distribution MUST satisfy:

- skills live in `release/.codex/skills/openspec-*/`;
- **every** such directory contains a real `SKILL.md`;
- **no symlinks anywhere** in `release/.codex/skills/**` or `release/openspec/**`;
- `release/openspec/config.yaml` exists and is valid;
- shared references must live inside an `openspec-*` skill directory, otherwise the
  installer will not ship them.
- runtime files under `release/.codex/skills/**`, `release/.codex/agents/**`, and `release/openspec/**` must not
  read from `staging/**` or `planning/generated/**`; those trees contain generation and
  audit artifacts, not installed runtime dependencies.

Therefore create `release/.codex/skills/openspec-shared/` holding all shared references plus a
**passive** `SKILL.md` that is only a reference index — it defines no workflow, no gates,
and no authority, and states that it is never invoked as an action.

Also regenerate `release/openspec/config.yaml`. It currently contains mandatory rules that invoke
unavailable imported skills. Those skills will not exist.
Repoint each rule at the corresponding shared reference path, keeping the rule's force and
the file's existing comment structure.

Build everything under `staging/` first; publish to the final locations only after all
audits pass.

## 5. Phase A — freeze the global merge contract (before any parallel work)

Dispatch one isolated subagent:

**`merge-policy-architect`** — model `gpt-5.6-sol`, effort `xhigh` (or `high` per §3),
sandbox read-only.

Inputs: OpenSpec templates/generators/schemas/CLI semantics; the skill indexes of all four
repositories; `install.sh`; `release/openspec/config.yaml`; the verified Codex runtime contract.

Output: `staging/global/MERGE_CONTRACT.md`, unambiguously defining:

1. OpenSpec authority and per-action boundaries
2. artifact source-of-truth rules
3. question/semantic-gate policy
4. evidence-first implementation policy
5. performance & memory policy
6. connector/framework-integration policy
7. external research policy (primary sources, version-pinned)
8. diagnosis-before-fix policy, with exactly ONE failure counter
9. independent review/verification policy and its axes
10. subagent delegation policy and the single verified dispatch mechanism
11. concurrency / write-conflict policy
12. task-completion criteria
13. archive-readiness rules
14. model routing (§9)
15. canonical terminology every skill must use
16. precedence rules
17. forbidden workflow substitutions and forbidden vocabulary

### Required precedence (lower may never contradict higher)

1. Explicit user instruction compatible with the current OpenSpec action
2. Current OpenSpec CLI state, schemas, generated instructions, artifact semantics, boundaries
3. `MERGE_CONTRACT.md`
4. Action-specific generated rules
5. Imported engineering techniques

No rewrite subagent may start before this file exists. The contract is a generation,
integration, and audit authority; it is never a target-project runtime dependency.

## 6. Doctrine to encode exactly once

### 6.1 Evidence-first implementation (replaces all three TDD doctrines)

- **Behaviour/bug change** — prefer a failing executable test before the production fix
  whenever intended behaviour can reasonably be expressed as one.
- **Bug fix** — reproduce and minimise before fixing; fix the cause, not the symptom.
- **Refactor** — establish characterisation evidence of current behaviour first.
- **Performance/memory** — establish a reproducible baseline measurement first; record
  environment and workload; rerun the same measurement plus correctness tests after.
- **Connectors/integrations** — where unit tests cannot represent protocol or framework
  behaviour, use the narrowest useful contract/integration test or reproducible fixture.
  Do not substitute mocks for necessary integration evidence to satisfy a slogan.
- **Genuinely inapplicable cases** — state the alternate verification evidence explicitly.

The principle is **evidence before claims**, not ritual. Never emit an unconditional
"never write production code before a test" rule.

Never mask a failure with skips, todo markers, disabled tests, narrowed filters,
suppressed output, or weakened assertions. Remove diagnostic instrumentation before
returning.

### 6.2 Diagnose-before-fix

One protocol: gather evidence → isolate the failing boundary by instrumenting each
boundary once → state ONE hypothesis with its supporting evidence and its falsifying
observation → fix the cause → verify with a fresh command. Wait on observable conditions,
never fixed delays. Validate at each boundary, not only the outermost. On the **third**
failed cycle for the same failure, stop, return a blocked status with the evidence trail,
and escalate to the owning planning artifact. **Exactly one counter exists across the
whole distribution.**

### 6.3 Performance & memory

Relevant-change planning identifies hot paths, expected workload, allocation and resource
risks, latency/throughput, concurrency, buffering/batching, connection and pool lifecycle,
backpressure, caching, serialization/conversion cost, benchmark/profile strategy, and any
existing regression thresholds. Quantitative claims require measurement; prefer
representative benchmarks over toy microbenchmarks. Diagnose suspected regressions before
optimising. Never trade away correctness or resource cleanup without explicit
justification. This is **not** ceremony for changes that cannot plausibly affect
performance.

### 6.4 Connector / framework integration

When relevant, reason explicitly about supported server/framework/runtime versions,
protocol semantics, transactions, connection lifecycle, pooling, cancellation, timeouts,
retries and idempotency, streaming, backpressure, thread/async safety, resource cleanup,
error mapping, type and value conversion, nullability, timezone/encoding/locale, feature
negotiation, optional dependencies, dependency version bounds, framework lifecycle hooks,
observability, compatibility matrices, and test-environment realism. Never assume a
dependency's behaviour from memory when the exact version matters — inspect pinned
versions, source, changelogs, or version-specific primary documentation.

## 7. What to import, and what to reject

The architect must read the actual current files before fixing wording. These mappings are
architectural intent, not copy instructions.

**OpenSpec Plus** — dynamically inspect its source skills `openspec-plus-proposal`, `spec`, `design`, `tasks`, `apply`, `tdd`, then merge their
strengthening *directly into the owning OpenSpec action*: structured discovery, proposal
quality, unambiguous and testable specifications, alternatives and tradeoffs in design,
structural fidelity, vertical implementation slices, outcome-shaped tasks, implementation
gates, artifact-aware evidence practices, and its subagent/review orchestration for apply.
**Critical adaptation:** do not preserve a Plus confirmation gate where it would conflict
with the current OpenSpec action. An action whose purpose is to produce several planning
artifacts in one invocation must not become a per-artifact approval lifecycle. Convert
those pauses into semantic gates that fire only on materially consequential unresolved
choices (public behaviour, architecture, acceptance criteria, destructive
migration, security, interoperability, major perf/memory tradeoff).
**Do not emit standalone `openspec-plus-*` skills.** Their content becomes shared
references owned by OpenSpec actions.

**mattpocock/skills** — distil from `engineering/tdd` (+ `tests.md`, `mocking.md`),
`engineering/diagnosing-bugs`, `engineering/codebase-design` (+ `DEEPENING.md`,
`DESIGN-IT-TWICE.md`), `engineering/code-review`, `engineering/research`, and
`engineering/domain-modeling` where useful. Keep: vertical slices; deep modules behind
small stable interfaces; design-it-twice; minimising the reproduction before forming a
fix; hypothesis-and-instrumentation diagnosis; independent code and spec review;
primary-source research for external behaviour.
**Reject** anything that becomes a competing lifecycle or user-facing orchestrator,
including `to-spec`, `to-tickets`, `implement`, `wayfinder`, `triage`, `prototype`,
`grill-me`, `ask-matt`, and all setup skills.

**obra/superpowers** — distil from `systematic-debugging` (incl. root-cause-tracing,
condition-based-waiting, defense-in-depth), `verification-before-completion`, the
requesting/receiving code-review discipline, and its parallel-subagent hygiene.
**Reject as runtime controllers** `using-superpowers`, brainstorming, `writing-plans`,
`executing-plans`, `subagent-driven-development`, branch-finishing lifecycle, and anything
else replacing OpenSpec's lifecycle. Do not impose worktree or branch management globally;
a worktree is only a local concurrency technique when the task and project policy justify
it. **Never commit or archive on the user's behalf outside OpenSpec's own semantics.**

## 8. Deduplicate aggressively

Consolidate: all TDD variants → one evidence-first discipline; all debugging variants →
one diagnosis protocol; all review variants → one review protocol with specialised axes;
all planning-question heuristics → one question policy; all parallel-agent advice → one
delegation/concurrency policy.

A source skill is **not entitled to remain recognisable**. Preserve useful behaviour, not
source structure. Delete slogans, motivational prose, "Bottom Line / Key Principles /
Real-World Impact" sections, installation and update instructions, marketing language,
generic AI advice, repeated examples, and performative rituals. The readers are capable
models: write compact declarative contracts, decision tables, and precise imperatives.

## 9. Model routing (authoritative; upstream model advice is discarded)

Every action and every subagent MUST have an explicit model and explicit reasoning effort.
Never rely on inherited defaults.

| Action | Model | Effort |
|---|---|---|
| `openspec-explore` | `gpt-5.6-sol` | high |
| `openspec-propose` | `gpt-5.6-sol` | xhigh |
| `openspec-new-change` | `gpt-5.6-sol` | high |
| `openspec-continue-change` | `gpt-5.6-sol` | high |
| `openspec-ff-change` | `gpt-5.6-sol` | high |
| `openspec-update-change` | `gpt-5.6-sol` | high |
| `openspec-apply-change` | `gpt-5.6-sol` | high |
| `openspec-verify-change` | `gpt-5.6-sol` | xhigh |
| `openspec-sync-specs` | `gpt-5.6-sol` | high |
| `openspec-archive-change` | `gpt-5.6-terra` | high |
| `openspec-bulk-archive-change` | `gpt-5.6-sol` | high |
| `openspec-onboard` | `gpt-5.6-terra` | medium |

Rules for actions not in that table: `sol`/`xhigh` for final independent verification,
multi-change conflict reasoning, high-consequence compatibility synthesis;
`sol`/`high` for design, exploration, artifact synthesis, implementation orchestration;
`terra`/`high` for bounded semantic transformations, bounded research, implementation
slices against a stable spec; `terra`/`medium` only for low-ambiguity scaffolding and
guarded mechanical lifecycle operations.

Specialist runtime agents (all explicit):

| Agent | Model | Effort | Sandbox | Purpose |
|---|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | high | read-only | focused codebase/dependency/test discovery |
| `opsx-docs-researcher` | `gpt-5.6-terra` | high | read-only | version-specific primary-source research |
| `opsx-slice-implementer` | `gpt-5.6-terra` | high | workspace-write | one bounded vertical slice against fixed artifacts |
| `opsx-debugger` | `gpt-5.6-sol` | high | workspace-write | hard bugs, nondeterminism, concurrency, leaks, regressions |
| `opsx-test-reviewer` | `gpt-5.6-sol` | high | read-only | can these tests actually fail for the intended defect? |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | high | read-only | implementation vs proposal/spec/design/tasks |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | high | read-only | benchmark methodology, hot paths, allocations, evidence |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | xhigh | read-only | high-consequence cross-artifact consistency |

Note the deliberate deviation from this repository's earlier contract: the implementer/
fixer role runs at **`gpt-5.6-terra` high**, not medium, because connector slices involve
concurrency, resource lifetimes, and conversion edge cases. Record this in the manifest.

Delegation is relevance-driven: never invoke every specialist unconditionally. Reviewers
receive artifacts, diffs, and evidence — never the implementer's reasoning transcript;
that independence is intentional. Parallelise read-only work freely; write in parallel
only when scopes are demonstrably disjoint, no shared file is touched twice, dependencies
do not force sequencing, and integration order is defined. Never create overlapping
implementers just to raise concurrency. No agent may dispatch itself.

## 10. Phase B — rewrite each skill in its own clean-context subagent

After `MERGE_CONTRACT.md` is frozen, dispatch **one fresh subagent invocation per
discovered skill**. Never let one subagent rewrite two skills.

**`merge-skill-rewriter`** — model `gpt-5.6-sol`, effort `high`, workspace-write confined
to that skill's staging directory.

Each invocation receives ONLY:

1. `MERGE_CONTRACT.md`
2. the current OpenSpec template/generated source for that one action, plus the CLI/schema
   context needed to preserve its exact semantics (every CLI call, parsed field, blocked/
   ready/all-done handling, precedence of context and guidance)
3. only the OpenSpec Plus sections mapped to that action
4. only the mattpocock source skills mapped to that action
5. only the Superpowers source skills mapped to that action
6. the shared-reference names and contracts (not their full text)
7. its assigned runtime model and the verified Codex dispatch contract

Do **not** give a worker other workers' output. This isolation is deliberate.

Each worker writes to `staging/release/.codex/skills/<skill-name>/`:

- `SKILL.md` — frontmatter with only the fields the Codex/OpenSpec schema allows
  (`name`, `description`; trigger-rich description; no emoji, no slogans), then:
  action purpose and hard boundary · minimum authoritative OpenSpec procedure ·
  decision rules · applicable invariants · **conditional** reference loads ·
  subagent delegation rules · completion and reporting contract
- any genuinely action-specific prompt/reference files (kept as separate files loaded
  just-in-time before dispatch, not inlined, so they stay out of orchestrator context)
- `REWRITE_REPORT.md`: OpenSpec behaviours preserved · concepts imported · concepts
  deliberately rejected · conflicts resolved · shared references required (with the exact
  reason each may be loaded) · action boundary · runtime agent and model · uncertainties

A worker MUST NOT touch another worker's directory.

Reference loading must be conditional and justified — e.g. `new-change` must not load the
performance reference; `apply-change` loads it only when tasks/design indicate
performance-sensitive work; `verify-change` loads the perf reference only when
relevant; `explore` loads research or debugging guidance based on the problem.

### Per-action enhancement guidance

- **explore** — focused investigation, domain modelling, alternatives, primary-source
  research, reproduction when investigating a defect, compatibility consequences,
  perf/memory hypotheses. Preserve its non-implementation boundary.
- **propose / artifact-producing actions** — structured discovery, explicit alternatives
  where a real choice exists, measurable nonfunctional goals
  where relevant, unknowns and risks, external-version assumptions. Never start implementing.
- **specs** — unambiguous behavioural requirements, testable scenarios,
  failure and error semantics, integration contracts, compatibility
  requirements, meaningful performance/resource requirements. No implementation detail
  unless it is part of the contract.
- **design** — alternatives and tradeoffs, deep-module/interface reasoning, resource and
  concurrency architecture, protocol/framework constraints, benchmark/profile design.
- **tasks** — vertical behavioural slices stating the observable result and how success is
  established, without pre-scripting every edit. Dedicated benchmark/compat tasks only
  when relevant.
- **apply** — evidence-first implementation, one coherent slice at a time,
  diagnosis-before-fix, project conventions, focused diffs, measurement
  for any performance claim, specialists only when useful, verification before any task is
  marked complete. Preserve OpenSpec's ability to update artifacts when implementation
  exposes a legitimate spec/design problem — never silently code around a contradiction.
  Emit a traceability comment immediately adjacent to every new class, method, or
  significant modified block, using the target file's native comment syntax (`//`, `#`,
  `<!-- -->`, `--`, `;`, etc.): `Change-Id: <change name> | Task: <task id>`, where the
  change name and task id come from the live apply status/instructions.
- **verify** — deliberately independent and rigorous across completeness, spec
  correctness, design coherence, test strength, integration
  compatibility, perf/memory evidence, and error/resource/concurrency paths. A "passes"
  claim requires fresh evidence whenever the environment permits verification.
- **sync / update** — preserve semantic intent; detect accidental weakening or widening of
  behavioural contracts.
- **archive** — never a substitute for verification; preserve current archive semantics;
  fold unresolved critical verification/compatibility concerns into the existing readiness
  check without inventing a second lifecycle.

## 11. Phase C — optional and non-skill actions

For every optional action, command template, or actionable surface not represented
one-to-one by a discovered skill directory, dispatch one fresh
**`merge-action-rewriter`** (`gpt-5.6-sol`, `high`, isolated staging write) under the same
contract and isolation rules. Do not skip an action because it is optional. Do not create
a duplicate action where a skill already fully covers it.

## 12. Phase D — shared references

Dispatch **`merge-reference-editor`** (`gpt-5.6-sol`, `high`, workspace-write) with
`MERGE_CONTRACT.md`, all `REWRITE_REPORT.md` files, and only the source excerpts needed.

Produce compact canonical references under
`staging/release/.codex/skills/openspec-shared/references/`, e.g. `evidence-first.md`,
`performance-memory.md`, `integration-correctness.md`, `debugging.md`, `review.md`,
`research.md`, `subagents.md` (rename where clearer). Each doctrine appears in exactly one
file, with exactly one owner. Then mechanically fix reference links in staged skills.
This stage must not change any OpenSpec action semantics.

Also produce the passive `openspec-shared/SKILL.md` reference index described in §4.

## 13. Phase E — Codex configuration and OpenSpec config

Dispatch **`merge-codex-config-author`** (`gpt-5.6-terra`, `high`, workspace-write) to
generate, using the schema verified in §3:

- one custom-agent file under `staging/release/.codex/agents/` for **every** discovered action,
  whose instructions tell it to execute the corresponding generated skill from disk and
  forbid self-redispatch. Contract requirements must already be embodied by that skill,
  its conditional shared references, and the agent's own bounded role constraints;
- all specialist agents from §9, loading only the canonical shared references relevant to
  their role and relying on their own complete bounded instructions for any role-specific
  constraint not owned by a shared reference;
- `staging/release/openspec/config.yaml` regenerated per §4;
- `staging/MODEL_MATRIX.md` listing every action and agent with its exact model and effort.

Each agent must explicitly set name, description, instructions, model, reasoning effort,
and an appropriate sandbox mode. The skill remains the authoritative action definition;
the agent exists to guarantee the model even when the parent session uses another one.
No agent instruction may read `MERGE_CONTRACT.md`, `MODEL_MATRIX.md`, another file under
`planning/generated/**`, or anything under `staging/**`. Contract compliance is compiled
into installed skills, canonical shared references, and self-contained agent constraints.

## 14. Phase F — contradiction audit (do not accept output before this)

Dispatch **`merge-cross-skill-auditor`** (`gpt-5.6-sol`, `xhigh`, read-only) with the
authoritative OpenSpec action definitions, `MERGE_CONTRACT.md`, every generated skill,
action, reference, agent config, the regenerated `release/openspec/config.yaml`, and all
`REWRITE_REPORT.md` files.

It must build a contradiction matrix across at least: OpenSpec workflow authority; action
boundaries; artifact source of truth; question/confirmation rules; evidence rules; task
completion; artifact updates during implementation; implementation vs exploration;
concurrency; subagent ownership; performance/memory; integration research;
debugging and failure counters; review independence; model routing; sandbox and write
permissions; archive readiness; git/worktree policy.

Look for: direct contradictions; softer wording elsewhere that defeats a hard rule;
circular delegation; duplicate authorities; conflicting always/never rules; incompatible
completion definitions; skills that accidentally invoke another methodology; missing new
OpenSpec actions; stale assumptions from older OpenSpec versions; more than one failure
counter; more than one dispatch mechanism.

Write `staging/AUDIT_REPORT.md`, classifying findings BLOCKER / MAJOR / MINOR / NOTE. Any
BLOCKER or MAJOR means the set is not acceptable.

## 15. Phase G — deterministic checks

Run mechanical checks in addition to the audit, and run the repository's existing
`tests/` suite:

1. every discovered OpenSpec skill has exactly one generated counterpart
2. every actionable OpenSpec surface is covered; no removed action resurrected
3. every action and every agent has an explicit GPT-5.6 model and explicit effort
4. all model names are in the GPT-5.6 family specified here
5. only reasoning-effort values accepted by the installed Codex build are used
6. no runtime dependency on, or instruction to invoke, `lib/openspec-plus`,
   `lib/mattpocock`, or `lib/superpower`; no `openspec-plus-*` skill names remain anywhere,
   including `release/openspec/config.yaml`, `README.md`, and `prompts/`
7. no foreign agent-platform syntax, slash commands, or pseudo-tools; no `.claude/` output
8. no recursive action-agent dispatch
9. every referenced file exists; every agent points at a real generated skill
10. read-only reviewer agents have no write access without a documented reason
11. all OpenSpec CLI names, flags, and artifact names match the current checkout
12. no copied phase gate alters the semantics of `propose`, fast-forward, or any other
    multi-artifact action
13. no duplicated TDD/debug/review doctrine remains; exactly one failure counter
14. packaging: `release/.codex/skills/openspec-*/SKILL.md` present for every skill directory, no
    symlinks, valid YAML frontmatter everywhere, `release/openspec/config.yaml` valid
15. `install.sh` and `tests/` still succeed against the generated tree
16. no runtime skill, agent, or OpenSpec configuration references `staging/**` or
    `planning/generated/**`; generated planning documents remain removable provenance

Search explicitly for stale or vendor-specific terms and inspect every hit rather than
deleting blindly.

## 16. Phase H — behavioural evaluation

Dispatch **`merge-behavior-evaluator`** (`gpt-5.6-sol`, `high`, read-only) to walk
representative scenarios: ordinary feature; bug fix; refactor; performance regression;
memory/resource leak; connector protocol defect; framework version incompatibility;
ambiguous architectural change;
implementation discovery that invalidates the design; bulk archive with conflicting
changes; any newly discovered action.

For each relevant action, compare the generated behaviour with current OpenSpec behaviour.
Added rigour is acceptable; **any change to the underlying lifecycle semantics is MAJOR or
BLOCKER**. Write `staging/BEHAVIOR_EVAL.md`.

## 17. Phase I — central resolution and publication

Independent workers never negotiate with each other. If audits report BLOCKER or MAJOR
findings, dispatch **`merge-final-integrator`** (`gpt-5.6-sol`, `xhigh`, workspace-write)
with the contract, the relevant OpenSpec sources, the staged output, `AUDIT_REPORT.md`,
and `BEHAVIOR_EVAL.md`. It may edit staged files only to resolve identified cross-cutting
issues and must introduce no new methodology. Re-run §14 and §15 afterwards. Repeat only
until no BLOCKER or MAJOR remains. Never hide unresolved findings.

Then publish atomically:

    release/.codex/skills/<one dir per discovered OpenSpec skill>/SKILL.md (+ action-specific files)
    release/.codex/skills/openspec-shared/SKILL.md
    release/.codex/skills/openspec-shared/references/*.md
    release/.codex/agents/<one per action>.toml
    release/.codex/agents/opsx-*.toml
    release/openspec/config.yaml
    planning/generated/MERGE_CONTRACT.md
    planning/generated/MODEL_MATRIX.md
    planning/generated/MERGE_MANIFEST.md
    planning/generated/AUDIT_REPORT.md
    planning/generated/BEHAVIOR_EVAL.md

Adapt names only where current OpenSpec or Codex conventions require it. Keep provenance
out of runtime skills — centralise it in the manifest. Do not commit. Do not install
anything via package managers.

The files under `planning/generated/` are published for regeneration provenance and audit
review only. Removing them from a target installation must not change skill, action-agent,
specialist-agent, or OpenSpec runtime behaviour. Mechanically rewrite and validate relative
links when moving reports from their staging directories to `planning/generated/`.

`MERGE_MANIFEST.md` records: timestamp; each source repo's commit/version/dirty state;
every discovered skill and action; every generated counterpart; exact model and effort per
action and per agent; the mapping from imported source concepts to generated destinations;
concepts deliberately rejected and why; global conflict-resolution decisions; any
reasoning-effort substitution made under §3; the implementer-effort deviation noted in §9;
licenses and required attributions; audit and behaviour-evaluation results. If substantial
source text was retained rather than distilled, preserve the attribution notices the
inspected licenses require.

## 18. Regeneration semantics

This prompt is rerun whenever OpenSpec or any source collection changes. Derive everything
from the current `lib/**`; detect added, removed, and renamed skills; regenerate mappings,
the model matrix, and all checks; diff the new manifest against the previous one and report
meaningful upstream-driven behaviour changes. Never preserve old generated behaviour merely
because it existed. Never edit upstream trees.

## 19. Final report

Report concisely: source commits used; skills and optional actions discovered; generated
counts; the action model matrix; the specialist matrix; imported concepts by source;
concepts rejected; contradictions found and how they were resolved; deterministic-check and
test status; behavioural-evaluation status; remaining MINOR/NOTE findings; the exact output
paths; and a reminder to restart Codex. Do not claim success while any BLOCKER or MAJOR
finding remains.

## 20. Operating principles

OpenSpec owns the workflow. Other collections contribute techniques, never lifecycle
authority. Local source beats remembered behaviour. One skill rewrite = one clean-context
subagent. Cross-skill policy is frozen before parallel rewriting. Audits happen after
isolated rewrites. One canonical rule beats three near-duplicates. Performance claims
require measurement. Hard bugs are diagnosed before fixes are guessed. Subagents help only
when their responsibility is
narrow. Parallel reads are cheap; conflicting parallel writes are not. Every action and
every subagent has an explicit GPT-5.6 model and effort. The generated skills must be
compact enough to help the model rather than bury it.

Begin by inventorying the four source trees, verifying the Codex runtime contract, and
discovering the OpenSpec action surface. Do not rewrite any skill until
`staging/global/MERGE_CONTRACT.md` exists.
