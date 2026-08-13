# Generate the OpenSpec skill distribution for Codex CLI

## Objective

Regenerate from current local sources the complete OpenSpec skill distribution for this
repository. Preserve every current OpenSpec skill, action, alias, artifact, CLI state, and
action boundary. Strengthen those workflows with applicable engineering practices distilled
from OpenSpec Plus, `mattpocock/skills`, and `obra/superpowers` without introducing another
lifecycle or a runtime dependency on those projects.

Target Codex CLI and the GPT-5.6 model family. Treat protocol correctness, compatibility,
performance, memory use, concurrency, and resource lifecycle as correctness concerns when
they are relevant to a database connector or framework integration.

## Instruction precedence

Apply this precedence while generating:

1. System, safety, repository `AGENTS.md`, and explicit user constraints
2. Current official OpenAI documentation for Codex CLI, GPT-5.6, and skill format
3. The boundaries and deliverables in this prompt
4. Current local OpenSpec templates, generators, schemas, and CLI behavior
5. Imported engineering techniques

Use this runtime precedence in every generated action skill:

1. An explicit user instruction compatible with the current OpenSpec action
2. Current OpenSpec CLI state, schemas, generated instructions, artifact semantics, and
   action boundaries
3. Rules compiled from the generated merge contract
4. Action-specific generated rules
5. Imported engineering techniques

Never let a lower-priority source contradict a higher-priority source. When two requirements
at the same level conflict, prefer safety and user constraints, then explicit output
requirements, validation requirements, and workflow guidance. Record every material
resolution in `MERGE_MANIFEST.md`.

## Inputs and assumptions

Run this contract in Codex CLI with the root session on `gpt-5.6-sol` at `xhigh` reasoning.
Run from the repository root. Use these local source trees as read-only inputs, including
their uncommitted content:

- `lib/openspec` — authoritative for OpenSpec behavior
- `lib/openspec-plus`
- `lib/mattpocock`
- `lib/superpower`

Read the applicable `AGENTS.md` files before reading or acting within a covered directory.
Read `install.sh`, `tests/`, the current `release/openspec/config.yaml`, and the installed
Codex configuration and documentation before generating output. Use actual source files;
do not reconstruct any project from memory or fetch another version of it. Official OpenAI
documentation may be fetched only to verify current Codex, GPT-5.6, and skill requirements.

Record each source tree's commit, tag or version when available, dirty status, license, and
required attribution. Record `git status --short` before changing generated paths. Preserve
unrelated user work and never reset, revert, commit, or modify `lib/**`.

Ask only when a missing input or materially consequential ambiguity cannot be resolved from
the precedence above and an assumption would change public behavior, architecture, acceptance
criteria, security, interoperability, a destructive migration, or a major performance or
memory tradeoff. Ask the single highest-leverage blocking question, and do not bundle a
checklist of secondary questions into it; follow up one question at a time only as needed.
Otherwise make the narrowest reversible assumption, record it, and continue. Stop with a
precise blocker instead of inventing unavailable source, CLI syntax, tool fields, or OpenSpec
semantics.

## Boundaries

OpenSpec is the only runtime workflow. The generated distribution may make an action more
rigorous, but must not:

- add, rename, reorder, or replace OpenSpec lifecycle stages or artifact transitions;
- reinterpret OpenSpec CLI state or substitute an imported action for an OpenSpec action;
- require OpenSpec Plus, Matt Pocock, or Superpowers skills at runtime;
- add mandatory phase transitions or approval pauses absent from the current OpenSpec action;
- grant imported material authority over OpenSpec;
- commit, archive, branch, or create a worktree unless the current OpenSpec action and
  explicit user request authorize it;
- install packages or fetch dependencies during regeneration;
- use unsupported slash commands, foreign agent syntax, pseudo-tools, or invented dispatch
  parameters.

Imported repositories are source material only. Distill useful behavior; do not preserve
their names, structure, slogans, setup instructions, or user-facing orchestrators.

Modify only the declared generated and staging paths. Build under `staging/`, validate there,
then publish the accepted result to:

```text
release/.codex/skills/<one directory per discovered OpenSpec skill>/
release/.codex/skills/openspec-shared/
release/.codex/agents/<one custom agent per discovered action>.toml
release/.codex/agents/opsx-*.toml
release/openspec/config.yaml
planning/generated/MERGE_CONTRACT.md
planning/generated/MODEL_MATRIX.md
planning/generated/MERGE_MANIFEST.md
planning/generated/AUDIT_REPORT.md
planning/generated/BEHAVIOR_EVAL.md
```

Do not publish generation-only reports into runtime skill directories. Do not retain any
runtime reference to `staging/**` or `planning/generated/**`.

## Ordered workflow

### 1. Verify sources, discovery, and runtime contracts

Perform these read-only tasks before writing:

1. Inspect OpenSpec skill templates and generators, including
   `lib/openspec/src/core/templates/`,
   `lib/openspec/src/core/shared/skill-generation.ts`,
   `lib/openspec/src/core/shared/skill-paths.ts`,
   `lib/openspec/src/core/shared/skill-content-equivalence.ts`,
   `lib/openspec/schemas/`, CLI instruction machinery, and `lib/openspec/skills/`.
2. Treat templates and generators as authoritative. Treat `lib/openspec/skills/*` as
   generated output that may lag; record discrepancies.
3. Dynamically enumerate every skill, action, optional action, alias, artifact type, CLI
   call, parsed field, state, and action boundary. Do not hard-code the surface or resurrect
   removed actions.
4. Inspect the installed Codex CLI and current official OpenAI guidance. Verify the custom
   agent schema, model and reasoning fields, sandbox fields, supported reasoning efforts,
   the expected `update_plan` and `apply_patch` tool names, and the exact subagent dispatch
   mechanism. Use only verified names and one dispatch mechanism everywhere. If the installed
   build cannot express a required agent or sandbox contract, stop and report the
   compatibility blocker.
5. Locate the installed `skill-creator` resources. Use its `init_skill.py`,
   `generate_openai_yaml.py`, and `quick_validate.py` workflows instead of recreating their
   behavior. If they are unavailable, stop and identify the missing requirement.
6. Read packaging tests and verify the required installed layout before generation.

The following names are orientation only: `openspec-explore`, `openspec-propose`,
`openspec-new-change`, `openspec-continue-change`, `openspec-ff-change`,
`openspec-update-change`, `openspec-apply-change`, `openspec-verify-change`,
`openspec-sync-specs`, `openspec-archive-change`, `openspec-bulk-archive-change`, and
`openspec-onboard`.

### 2. Freeze the merge contract

Dispatch one fresh `merge-policy-architect` subagent using `gpt-5.6-sol` at `xhigh`
reasoning, or `high` only if the verified CLI rejects `xhigh`. Give it read-only access and
only the verified runtime contract, OpenSpec templates/generators/schemas/CLI semantics, the
four source indexes, `install.sh`, and the current OpenSpec config.

Require the architect to return a complete contract to the orchestrator. Because its sandbox
is read-only, the orchestrator writes the returned content to
`staging/global/MERGE_CONTRACT.md`. Do not start rewrite agents until that file exists and
defines:

- OpenSpec authority, artifact sources of truth, per-action boundaries, canonical terms,
  precedence, and forbidden substitutions;
- one question and semantic-gate policy;
- one evidence-first implementation policy;
- one performance and memory policy;
- one connector and framework-integration policy;
- one version-specific primary-source research policy;
- one diagnosis protocol with the distribution's only failure counter;
- one independent review and verification policy;
- one delegation, concurrency, write-conflict, and dispatch policy;
- task completion, archive readiness, and model routing;
- the apply-only task locator chain: exact unchecked text in reported `contextFiles` first;
  live task `id` to disambiguate duplicates; then, only if verified, one guarded literal
  path from schema-declared `apply.tracks`; otherwise stop blocked without changing task
  state. Other actions, including onboarding, use only their current primary locator.

The merge contract is generation and audit authority, not a runtime dependency.

### 3. Generate each skill in isolated context

After the contract is frozen, dispatch one fresh `merge-skill-rewriter` subagent per
discovered skill. Use `gpt-5.6-sol` at `high` reasoning and restrict writes to that skill's
staging directory. Run independent rewrites concurrently only when their write scopes are
disjoint.

Give each rewriter only:

1. `MERGE_CONTRACT.md`;
2. the authoritative source for its action and the minimum CLI/schema context needed to
   preserve all calls, parsed fields, state handling, context precedence, and guidance;
3. only imported excerpts mapped to that action;
4. the shared-reference names and load contracts, not their full contents;
5. its model route and the verified dispatch contract.

Do not give a rewriter another worker's output. Require it to initialize and write
`staging/release/.codex/skills/<skill-name>/` and return a rewrite report. Save that report
as `staging/reports/skills/<skill-name>/REWRITE_REPORT.md`, containing preserved behavior,
imported and rejected concepts, conflict resolutions, required shared references and load
reasons, action boundary, runtime model, and uncertainties. Reject any edit outside its
assigned directory.

For every optional action or actionable surface without a one-to-one skill, dispatch a fresh
`merge-action-rewriter` with the same isolation rules using `gpt-5.6-sol` at `high`. Have it
return an isolated action patch and report; let the orchestrator merge that patch into the
owning staged skill after checking its boundary. Create a separate skill only when current
OpenSpec exposes the action independently. Do not duplicate an action already covered by a
skill.

### 4. Generate shared references and configuration

Dispatch `merge-reference-editor` with `gpt-5.6-sol` at `high`, the merge contract, rewrite
reports, and only needed source excerpts. Create a compact canonical set under
`staging/release/.codex/skills/openspec-shared/references/`, normally:

- `evidence-first.md`
- `performance-memory.md`
- `integration-correctness.md`
- `debugging.md`
- `review.md`
- `research.md`
- `subagents.md`

Keep `debugging.md` as the exact owner of the failure counter; rename another reference only
when a clearer name improves routing. Place each doctrine in exactly one reference and fix
staged links mechanically. Create a passive `openspec-shared/SKILL.md` that only indexes
references, defines no workflow or gate, and cannot be implicitly invoked. Use
`agents/openai.yaml` with
`policy.allow_implicit_invocation: false` for that skill.

Dispatch `merge-codex-config-author` with `gpt-5.6-terra` at `high` to create, from the
verified schema:

- one custom-agent file per discovered action that runs the corresponding installed skill,
  has explicit name, description, instructions, model, effort, and sandbox, and forbids
  self-redispatch;
- all specialist agents in the model matrix below, each loading only relevant canonical
  references;
- `staging/release/openspec/config.yaml`, preserving its comment structure and rule force
  while replacing unavailable imported-skill invocations with installed shared references;
- `staging/MODEL_MATRIX.md` with every action and agent route.

Runtime agents must be self-contained. They must not read the merge contract, model matrix,
generation reports, `planning/generated/**`, or `staging/**`.

### 5. Audit, evaluate, and integrate

Dispatch `merge-cross-skill-auditor` with `gpt-5.6-sol` at `xhigh` and read-only access.
Give it authoritative OpenSpec definitions, all staged runtime output, reports, and the merge
contract. Require a contradiction matrix covering workflow authority, action boundaries,
artifact sources of truth, question policy, evidence and completion rules, implementation
versus exploration, artifact updates, concurrency, delegation, performance, integration
research, diagnosis and failure counters, review independence, model routing, sandbox and
write permissions, archive readiness, and git/worktree policy. Classify findings as BLOCKER,
MAJOR, MINOR, or NOTE. Treat a softer duplicate that defeats a hard rule as a contradiction.
The orchestrator writes its returned report to
`staging/AUDIT_REPORT.md`.

Dispatch `merge-behavior-evaluator` with `gpt-5.6-sol` at `high` and read-only access. Test
an ordinary feature, bug fix, refactor, performance regression, memory or resource leak,
connector protocol defect, framework-version incompatibility, ambiguous architecture,
implementation discovery that invalidates design, bulk archive conflict, and every newly
discovered action. Compare generated behavior with current OpenSpec semantics; treat any
lifecycle change as MAJOR or BLOCKER. The orchestrator writes the returned report to
`staging/BEHAVIOR_EVAL.md`.

If either report contains a BLOCKER or MAJOR, dispatch `merge-final-integrator` with
`gpt-5.6-sol` at `xhigh`, write access only to affected staged paths, and only the contract,
relevant authoritative sources, staged output, and findings. Resolve identified issues
without adding methodology, then rerun affected audits and checks. Stop with the remaining
evidence if the same failure recurs without new information; do not loop or hide findings.

### 6. Publish accepted output

Publish atomically only after every required audit and deterministic check passes. Replace
only declared generated targets, use explicit paths, and abort if an existing path contains
user-owned work that the generation baseline cannot distinguish. Do not use broad recursive
deletion.

Move the accepted runtime output to `release/` and generation provenance to
`planning/generated/`. Rewrite and validate relative links after moving reports. Runtime
behavior must remain unchanged if `planning/generated/` is removed.

## Skill authoring contract

Apply current official Codex and `skill-creator` requirements to every generated skill:

- Use a lowercase, digit, and hyphen name under 64 characters; make the directory match it.
- Create a real `SKILL.md` with YAML frontmatter containing only `name` and `description`.
- Front-load the description with the job and trigger terms. Keep it concise and at most
  1,024 characters. State when the skill should and should not trigger; keep all trigger
  guidance in the description.
- Write the body in imperative language. Keep it focused on one action, under 500 lines, and
  free of generic explanations, slogans, duplicated doctrine, and a redundant "when to use"
  section.
- Keep the minimum authoritative OpenSpec procedure in the body: purpose and hard boundary,
  CLI/state procedure, decision rules, applicable invariants, conditional reference loads,
  delegation constraints, completion criteria, and reporting contract.
- Link each optional reference directly from `SKILL.md` and state exactly when to read it.
  Put a table of contents in any reference longer than 100 lines. Do not duplicate material
  between `SKILL.md` and references.
- Prefer instructions. Add a script only for repeated deterministic behavior or required
  external tooling; execute every added script against representative input. Add an asset
  only when it is consumed in generated output. Remove unused placeholders and empty resource
  directories.
- Generate `agents/openai.yaml` deterministically with quoted
  `interface.display_name`, `interface.short_description`, and
  `interface.default_prompt`; keep the short description between 25 and 64 characters and
  make the default prompt mention `$<skill-name>`. Add icons, colors, dependencies, or
  invocation policy only when the source requires them.
- Do not add `README.md`, changelogs, installation guides, quick references, generation
  reports, or other auxiliary files to a skill.
- Use installed-layout references only. Never reference `lib/**`, staging, generation
  reports, or an imported skill at runtime.

Shared references must live inside `openspec-shared`; the installer does not ship loose
references. Every directory matching `release/.codex/skills/openspec-*` must contain a real
`SKILL.md`. Do not create symlinks anywhere under `release/.codex/skills/**` or
`release/openspec/**`.

## Engineering doctrine to distill

Encode each rule below once in its canonical owner and load it conditionally.

### Evidence before claims

- For behavior or bug changes, prefer a failing executable test before production changes
  when intended behavior can reasonably be tested.
- Reproduce and minimize bugs before fixing causes. Establish characterization evidence
  before refactoring.
- Establish a reproducible baseline, environment, and workload before a performance or
  memory change; rerun the same measurement and correctness tests afterward.
- Use the narrowest useful contract or integration test when mocks cannot represent protocol
  or framework behavior. State alternate evidence when executable testing is inapplicable.
- Never obtain a pass by skipping, disabling, filtering out, suppressing, or weakening a
  relevant check. Remove diagnostic instrumentation before completion.

### Diagnose before fixing

Use one protocol: gather evidence; instrument each relevant boundary once; isolate the
failure; state one hypothesis, its supporting evidence, and a falsifying observation; fix
the cause; verify with a fresh command. Wait on observable conditions, not fixed delays. On
the third failed cycle for the same failure, stop blocked with the evidence trail and
escalate to the owning planning artifact. This is the distribution's only numeric failure
counter and belongs only in `openspec-shared/references/debugging.md`.

### Performance, memory, and integrations

When relevant, cover hot paths, workload, allocation and resource risks, latency,
throughput, concurrency, buffering, batching, connection and pool lifecycle, backpressure,
caching, serialization and conversion, profiling strategy, and existing thresholds. Require
measurements for quantitative claims and preserve correctness and cleanup.

For connectors and integrations, inspect applicable server, framework, runtime, and
dependency versions. Cover protocol semantics, transactions, pooling, cancellation,
timeouts, retry/idempotency, streaming, backpressure, thread or async safety, cleanup, error
mapping, conversions, nullability, timezone/encoding/locale, feature negotiation, optional
dependencies, version bounds, lifecycle hooks, observability, compatibility matrices, and
test realism. Use pinned source, changelogs, or version-specific primary documentation when
exact behavior matters.

## Import mapping

Read current files before distilling them.

- From OpenSpec Plus, map proposal, spec, design, tasks, apply, TDD, and review strengths
  directly into their owning OpenSpec actions. Convert imported confirmation pauses into
  semantic questions only for unresolved consequential choices. Do not create
  `openspec-plus-*` skills.
- From `mattpocock/skills`, use relevant parts of TDD, diagnosing bugs, codebase design,
  deep modules, design-it-twice, code review, research, and domain modeling. Reject its
  competing orchestrators, including `to-spec`, `to-tickets`, `implement`, `wayfinder`,
  `triage`, `prototype`, `grill-me`, `ask-matt`, and setup skills.
- From Superpowers, use relevant systematic-debugging, root-cause-tracing,
  condition-based-waiting, defense-in-depth, verification-before-completion, code-review,
  and parallel-agent hygiene. Reject `using-superpowers` and runtime controllers for
  brainstorming, planning, plan execution, subagent-driven development, branch finishing,
  and global worktree policy.

Consolidate all TDD variants into the evidence policy, debugging variants into the diagnosis
protocol, review variants into the review reference, question heuristics into the question
policy, and parallel-agent advice into the delegation policy.

## Action-specific requirements

- `explore`: investigate, model the domain, compare real alternatives, research exact
  versions, reproduce defects, and consider compatibility and performance consequences;
  never implement.
- Proposal and artifact-producing actions: use structured discovery, explicit alternatives
  for real choices, relevant measurable nonfunctional goals, risks, unknowns, and external
  version assumptions; never implement.
- Specs: define unambiguous behavioral requirements, testable scenarios, failure and error
  semantics, integration contracts, compatibility, and meaningful resource requirements;
  omit implementation detail unless contractual.
- Design: record alternatives and tradeoffs, interface and deep-module reasoning, resource
  and concurrency architecture, protocol constraints, and benchmark or profile design.
- Tasks: define vertical behavioral slices with observable outcomes and evidence; add
  benchmark or compatibility tasks only when relevant.
- Verify: independently check completeness, spec correctness, design coherence, test
  strength, compatibility, performance and memory evidence, and error/resource/concurrency
  paths. Require fresh executable evidence when the environment permits it.
- Sync and update: preserve semantic intent and detect accidental weakening or widening.
- Archive: preserve current archive semantics, never substitute for verification, and fold
  critical unresolved verification or compatibility concerns into existing readiness checks
  without adding a lifecycle.

### Apply

Preserve current OpenSpec apply semantics and add these constraints:

- Implement one coherent vertical slice at a time using evidence-first work,
  diagnosis-before-fix, focused diffs, and relevant specialists. Update an OpenSpec artifact
  when implementation exposes a genuine contradiction; never silently code around it.
- Treat `ready` with zero tasks as one bounded untracked outcome derived from live
  instructions and reported artifacts. Ask if it cannot be bounded. Create no tracking file
  or checkbox, establish completion with evidence, and terminate without waiting for a state
  transition.
- Capture `git status --short` once as the session baseline. Preserve unrelated work and ask
  before editing an already modified path whose ownership is unclear.
- Read applicable `AGENTS.md` files, referenced instructions, and build manifests. Record
  exact focused-test, lint/format-check, type-check/build, and full-verification commands.
  Distinguish check-only commands from mutating formatters; never append guessed flags.
- In tracked mode, locate the exact unchecked text in reported `contextFiles`; use the live
  task `id` to resolve duplicate text. Change only `[ ]` to `[x]`, preserving marker,
  indentation, identifier, and text. Never invent an apply/status tracking-path field.
- Only if primary locators fail and the verified CLI exposes
  `schema which <schemaName> --json`, resolve a literal `apply.tracks` path beneath
  `changeRoot` from the selected store or context root and run the root-sensitive schema
  lookup from that resolved root. Never pass an unsupported `--store`, accept a glob or path
  escape, or treat this fallback as a work precondition or payload field. If one target is
  not established, stop blocked without changing task state and report the CLI limitation.
  Do not apply this fallback to another action.
- Treat production or test edits after review or a passing check as invalidating affected
  evidence. Re-establish affected independent review, then rerun affected checks. Treat a
  mutating formatter as evidence only after its check command or clean-diff inspection.
- Before reporting `all_done` for multiple slices, inspect the cumulative diff for
  interface/type/error compatibility, one name per concept, dead code, superseded code, and
  scope creep; rerun full verification. Use the final consistency reviewer only for
  high-consequence changes.
- Add an adjacent native-syntax comment to every new class, method, or significant modified
  block in a tracked slice: `Change-Id: <change name> | Task: <task id>`. Derive both values
  from live apply state. Do not fabricate an id in zero-task mode.
- Emit exactly `spec-compliance-reviewer-prompt.md`,
  `code-quality-reviewer-prompt.md`, and `final-review-prompt.md` beside the apply skill.
  Each packet must be read-only, nonrecursive, bounded, declare its model and effort, use an
  evidence matrix, verdicts, severity taxonomy, and exact `STATUS:` return section, and load
  shared references through
  `{SKILLS_DIRECTORY}/openspec-shared/references/<file>.md`. Load a packet only immediately
  before its conditional dispatch and replace only fenced-body placeholders.
- Route spec and code-quality review to `gpt-5.6-sol`/`high` and final consistency review to
  `gpt-5.6-sol`/`xhigh`. Treat code-quality review as a bounded ad hoc subagent task, not a
  standing role. Do not emit `implementer-prompt.md`; pass the slice implementer its bounded
  objective, artifacts, constraints, evidence, expected return, and no-recursion rule.

## Model and delegation contract

Set an explicit model and effort for every action, custom agent, specialist, reviewer packet,
and dispatched subagent. Never inherit a route. If the installed Codex build rejects `xhigh`,
substitute `high` consistently and record it in the manifest.

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

Route newly discovered actions by task shape: `sol`/`xhigh` for final independent
verification, multi-change conflict reasoning, or high-consequence compatibility synthesis;
`sol`/`high` for design, exploration, artifact synthesis, or implementation orchestration;
`terra`/`high` for bounded semantic transformations, research, or implementation slices;
`terra`/`medium` only for low-ambiguity scaffolding or guarded mechanical lifecycle work.

| Specialist | Model | Effort | Sandbox | Scope |
|---|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | high | read-only | focused code, dependency, and test discovery |
| `opsx-docs-researcher` | `gpt-5.6-terra` | high | read-only | version-specific primary-source research |
| `opsx-slice-implementer` | `gpt-5.6-terra` | high | workspace-write | one bounded vertical slice |
| `opsx-debugger` | `gpt-5.6-sol` | high | workspace-write | difficult bugs, nondeterminism, leaks, and regressions |
| `opsx-test-reviewer` | `gpt-5.6-sol` | high | read-only | test sensitivity to the intended defect |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | high | read-only | implementation versus OpenSpec artifacts |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | high | read-only | hot paths, allocations, and measurement quality |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | xhigh | read-only | high-consequence cross-artifact consistency |

Record that the slice implementer intentionally uses `terra`/`high`. Delegate only when a
bounded specialist improves reliability. Pass artifacts, diffs, and raw evidence, never an
implementer's hidden reasoning. Run read-only tasks concurrently when independent. Run
writes concurrently only for provably disjoint files with defined integration order. Never
create overlapping implementers, allow recursive dispatch, or let an agent dispatch itself.

## Validation and success criteria

Perform a static consistency pass for terminology, precedence, Markdown structure, Codex CLI
compatibility, skill triggering, progressive disclosure, paths, and current skill
requirements. Then run all of these checks against staging:

1. Compare dynamic discovery with generated skills and actions one-to-one; include new
   surfaces and exclude removed ones.
2. Run the installed official `quick_validate.py` on every generated skill folder. Fix every
   failure and rerun it. Validate every `agents/openai.yaml` against current field rules.
3. Verify every action, custom agent, specialist, and prompt packet has an accepted explicit
   GPT-5.6 route and one verified dispatch syntax.
4. Verify all OpenSpec CLI names, flags, fields, artifact names, states, and boundaries against
   current source.
5. Verify all references exist, are installed-layout relative, and load conditionally. Verify
   no runtime reference to `lib/**`, imported skills, `staging/**`, or
   `planning/generated/**`.
6. Search for foreign platform syntax, pseudo-tools, slash-command invocation, `.claude/`,
   `openspec-plus-*`, recursive action dispatch, copied phase gates, duplicate doctrine,
   multiple dispatch mechanisms, and multiple failure counters. Assert that `debugging.md`
   contains the only numeric retry/failed-cycle counter in generated runtime content. Inspect
   every match.
7. Verify apply's zero-task termination, primary checkbox locator, task-id disambiguation,
   guarded schema fallback, and exactly three reviewer packets with the declared routes and
   no implementer packet.
8. Verify packaging: real `SKILL.md` in every `openspec-*` skill directory, no symlinks,
   valid frontmatter and YAML, valid `release/openspec/config.yaml`, and no generation reports
   in runtime directories.
9. Run the repository's existing deterministic checks and `tests/` suite, including
   `install.sh` behavior against the staged tree. If a check assumes repository-root
   `release/` paths, assemble the staged result at those paths in an isolated temporary copy
   of the repository and run the unchanged check there. Do not publish early, weaken tests,
   or install packages to obtain a pass.
10. Confirm read-only agents cannot write, writers have bounded scope, no generated runtime
    agent reads provenance files, and removing planning provenance cannot change runtime.

Do not publish or claim success while any quick validation, required deterministic check, or
test fails, or while an audit contains BLOCKER or MAJOR findings. Report environment-caused
inability to run a required check as a limitation with the exact command and evidence.

## Manifest and final report

Create `MERGE_MANIFEST.md` with the timestamp; source commits, versions, dirty states,
licenses, and attributions; discovered and generated mappings; exact model routes; imported
concept destinations; deliberate rejections; semantic conflict resolutions; reasoning-effort
substitution; the slice-implementer route decision; previous-manifest differences; audit,
validation, test, and behavior-evaluation results. Preserve required notices when source text
is retained instead of distilled.

Report concisely:

- source revisions and discovered/generated counts;
- action and specialist model matrices;
- imported and rejected concepts;
- contradictions and semantic resolutions;
- quick-validation, deterministic-check, repository-test, and behavioral-evaluation status;
- remaining MINOR and NOTE findings or any blocker;
- exact published paths and a reminder to restart Codex.

Regenerate from the current sources on every run. Do not preserve obsolete generated behavior
because it existed previously. Begin with the read-only inventory and runtime-contract checks.
