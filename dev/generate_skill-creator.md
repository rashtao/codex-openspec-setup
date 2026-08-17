# Build the Codex Skill Workbench

## Objective

Implement a Codex-native skill named `codex-skill-creator`. Use OpenAI's installed
`skill-creator` as the semantic and structural baseline, and selectively incorporate the
strongest portable evaluation and iteration ideas from Anthropic's `skill-creator`.

This is an implementation task, not a comparison or proposal. Create the completed skill,
validate it, test every reusable script, exercise it in clean contexts, and report the
result.

## Paths and authority

Treat these paths as read-only sources:

- OpenAI baseline: `~/.codex/skills/.system/skill-creator`
- Anthropic evaluation source:
  `~/arango/skills/anthropics-skills/skills/skill-creator`

Create or update the skill at:

```text
.codex/skills/codex-skill-creator
```

Do not modify either source tree. If the destination exists, preserve intentional existing
work and incorporate it deliberately instead of replacing it blindly.

The destination is a fixed deliverable of this task, not a claim about Codex's current
auto-discovery locations. Do not relocate it when official authoring locations differ;
record that documentation difference in the final report.

Apply this precedence:

1. System, safety, applicable `AGENTS.md`, and explicit user constraints
2. Current official OpenAI documentation
3. This implementation contract
4. The installed OpenAI baseline
5. Portable Anthropic evaluation ideas
6. Existing destination content that does not conflict with higher-priority requirements

When current official documentation conflicts with local guidance, follow the official
documentation and record the discrepancy in the final report.

## Orchestration contract

Keep the root agent as a coordinator and final integrator. Delegate source-heavy discovery,
independent authoring, validation, and forward testing so the root context contains compact
contracts and findings rather than full source trees.

Use `gpt-5.6-sol` with `xhigh` reasoning and `fork_turns: "none"` for every subagent. Set all
three values explicitly on every dispatch; do not inherit conversation history, substitute
another model, or lower the effort. Before dispatching, verify that the installed Codex
environment supports the exact model, effort, and subagent mechanism. If it cannot enforce
`gpt-5.6-sol`, `xhigh`, or a fresh context, stop and report the compatibility blocker.

Follow these rules for every subagent:

- Start a fresh subagent for each role below; do not reuse a source auditor as an author or
  an author as a reviewer.
- Forbid recursive delegation and self-redispatch.
- Run no more than three subagents concurrently.
- Give each non-behavior agent only its role contract, the minimum source paths or reports
  it needs, its exact read/write boundary, and its required output schema. Give a forward-test
  behavior agent only its ordinary user task, the completed skill, applicable runtime
  instructions, and narrow filesystem boundaries.
- Pass file paths, raw artifacts, diffs, and evidence indexes instead of another agent's
  hidden reasoning or a verbatim source dump.
- Run independent read-only tasks concurrently. Run writers concurrently only when their
  destination paths are provably disjoint.
- Assign every repository path to at most one writer at a time. An agent that discovers a
  needed change outside its ownership must return an integration request instead of editing
  that path.
- Require concise reports with evidence paths and line numbers, decisions, uncertainties,
  and blockers. Store bulky logs and fixtures in a fresh temporary coordination directory
  outside the repository; return their paths rather than pasting them into the root context.
- Preserve subagent failures and unresolved findings. Do not silently redo a failed role in
  the root context or claim success from partial output.

Treat `read-only` as a role boundary unless the verified dispatcher can enforce it. Capture
a content-level repository snapshot before and after every read-only wave; `git status`
alone is insufficient because an already-modified path remains marked `M`. Reject any byte
change caused by a read-only agent.

Require every non-behavior subagent to return this result contract:

```text
STATUS: PASS | PARTIAL | BLOCKED
SCOPE: <read paths and owned write paths>
ARTIFACTS: <paths created or changed, or "none">
EVIDENCE: <source locations, commands, and material results>
DECISIONS: <bounded conclusions>
RISKS: <remaining uncertainty>
OUT_OF_SCOPE_CHANGES: none | <exact paths and reason>
NEXT_ACTION: <one concrete integration or repair action>
```

The root agent alone owns dispatch order, the frozen implementation contract, cross-file
integration, acceptance decisions, and the final report. It must not reread entire source
trees unless a subagent report identifies a specific unresolved ambiguity.

## Ordered workflow

### 1. Establish the baseline

Before editing:

1. Read every applicable `AGENTS.md` that covers the repository and destination, and every
   skill instruction the main Codex agent is required to load. Read the installed OpenAI
   baseline `SKILL.md` completely because it is the active authoring guidance; do not
   delegate interpreting skill instructions.
2. Capture a content-level pre-edit baseline outside the repository: `git status --short`,
   complete staged and unstaged binary diffs, and an inventory plus SHA-256 hashes for
   untracked files. Also inventory the destination and hash both source trees. Use this
   baseline to distinguish task changes from unrelated work and to prove preservation.
3. Create a fresh temporary coordination directory outside the repository for reports,
   fixtures, logs, and clean-context outputs.
4. Verify one current Codex subagent dispatch mechanism and the exact
   `gpt-5.6-sol`/`xhigh` route.

Then dispatch the first three fresh read-only agents concurrently. Dispatch the fourth as
soon as a concurrency slot is available:

#### `openai-baseline-auditor`

Read the OpenAI `SKILL.md` completely and inspect every file in the OpenAI baseline. Report:

- its authoring workflow, progressive-disclosure structure, and degrees of freedom;
- the contracts implemented by `init_skill.py`, `generate_openai_yaml.py`, and
  `quick_validate.py`;
- `agents/openai.yaml` and frontmatter requirements;
- validation, forward-testing, resource-planning, and instruction-style rules;
- source license, notices, and attribution obligations;
- an evidence index of relevant source files and line ranges.

#### `anthropic-evaluation-auditor`

Read the Anthropic `SKILL.md` completely. Inspect only resources relevant to intent and
success criteria, test-case design, with-skill versus baseline evaluation, objective and
subjective grading, benchmark aggregation, blind comparison, description-trigger testing,
benchmark analysis, and the evaluation viewer. Report:

- vendor-neutral concepts worth retaining;
- product-specific mechanics that must be omitted or rewritten for Codex;
- portable script, schema, and viewer candidates with their dependencies;
- source license, notices, and attribution obligations;
- an evidence index without copying large source passages.

Include Anthropic's `agents/grader.md`, `agents/comparator.md`, and `agents/analyzer.md` in
this review, but treat them as source material rather than Codex agent definitions. Place
any retained procedures in evaluation references, not under `agents/`.

#### `codex-compatibility-auditor`

Check the installed Codex behavior and current official documentation, including:

- <https://learn.chatgpt.com/docs/build-skills>
- <https://learn.chatgpt.com/docs/import>

Verify the current skill layout, `SKILL.md` frontmatter, `agents/openai.yaml`, local skill
distribution, plugin distribution, the subagent dispatch mechanism, model/effort fields,
and whether a reliable skill-activation signal is documented and locally observable.
Report verified facts with official links or local command evidence. Do not infer an
automated trigger detector from undocumented behavior.

#### `destination-preservation-auditor`

If the destination exists, read its `SKILL.md` completely, inventory all files, inspect its
Git status and diff, and classify existing content as intentional work, generated
placeholder, or uncertain. Report the exact content that must be preserved and any conflict
requiring an explicit merge decision. If it does not exist, report that fact and do no
further work.

Each auditor must write a compact structured report in the temporary coordination directory
and return the standard result contract with that report path under `ARTIFACTS`. Keep the
inline fields compact and put detailed evidence in the report.

### 2. Freeze the implementation contract

After all discovery reports are complete, dispatch a fresh read-only
`skill-merge-architect`. Give it this prompt, the four report paths, and no full source tree
unless one report cites an unresolved ambiguity that requires a narrow source read.

Require it to produce a frozen implementation contract containing:

- the selected output tree and the reason for every optional file;
- a requirement-to-file ownership map;
- interfaces between `SKILL.md`, references, scripts, schemas, and static viewers;
- the lightweight and deep-evaluation workflows;
- retained, adapted, omitted, and rewritten source concepts;
- source-attribution and licensing decisions;
- exact per-path preservation or merge decisions for every existing destination file;
- exact writer path ownership with no overlap;
- deterministic validation commands; three exact user-like forward-test prompts with every
  seed input; and predeclared objective and qualitative success criteria for each case,
  stored separately so behavior agents never receive the criteria;
- open questions or blockers that make implementation unsafe.

Reject a contract that includes dead automation, an untestable asset, duplicated guidance,
an unsupported Codex mechanism, or overlapping writers. Do not begin authoring until the
contract is accepted and frozen.

### 3. Scaffold and author in isolated contexts

If the destination does not exist, initialize it once with the installed OpenAI baseline's
`init_skill.py`. Use that script only for scaffolding, then use `apply_patch` for manual
edits. If the destination exists, do not reinitialize it.

After scaffolding, dispatch up to three writers concurrently only when the architect
confirmed their path sets are disjoint:

Give every writer the frozen per-path preservation decisions and only the destination-audit
evidence relevant to its owned files. Require it to preserve the identified intentional
content and stop with an integration request when an owned path remains uncertain.

#### `skill-core-author`

Own only these approved files:

- `SKILL.md`
- `LICENSE.txt`
- `agents/openai.yaml`
- `references/openai_yaml.md`

Give this writer the frozen contract, the OpenAI audit, the compatibility audit, and only
the exact baseline files needed for its paths. Require it to keep the OpenAI workflow
recognizable and link every approved reference directly from `SKILL.md`.

#### `skill-evaluation-reference-author`

Own only the approved subset of:

- `references/evaluation.md`
- `references/eval-schemas.md`
- `references/description-testing.md`

Give this writer the frozen contract, the Anthropic audit, the compatibility audit, and only
the exact source files approved for adaptation. Require each reference to own a distinct
topic and participate in the core workflow without duplicating `SKILL.md`.

#### `skill-tooling-author`

Own only the approved subset of:

- `scripts/init_skill.py`
- `scripts/generate_openai_yaml.py`
- `scripts/quick_validate.py`
- `scripts/aggregate_benchmark.py`
- `scripts/generate_review.py`

Give this writer the frozen contract, both source audits, the compatibility audit, and only
the exact source scripts approved for retention or adaptation. Require documented command
interfaces, meaningful exit codes, no unnecessary dependency, and an execution test for
every included script.

If the frozen contract includes a complete viewer, dispatch a fresh
`skill-viewer-author` after the schema-producing writer finishes. Own only the approved
subset of:

- `assets/eval-viewer.html`
- `assets/trigger-eval-review.html`

Give the viewer writer only the frozen interface contract, the approved source asset, and
the evaluation schema. Require a documented, headless validation path. Omit the viewer when
its schema, consumption path, or static validation cannot be completed.

Every writer must use `apply_patch`, edit only its assigned files, and return a concise file
manifest, source-attribution notes, tests it ran, and any cross-owner integration request.
No writer may edit or delete another writer's output.

After all writers finish, require the root agent to inspect their diffs and returned
artifacts, then resolve declared integration requests with narrow patches. Do not broaden a
writer's scope retroactively.

### 4. Audit and test independently

Dispatch these fresh agents concurrently after integration:

- `skill-static-auditor`: read-only; compare the completed destination with this contract,
  the frozen implementation contract, and all four discovery reports. Check semantic
  coverage, progressive disclosure, duplicated guidance, Codex-native adaptation,
  licensing, attribution, stale branding, placeholders, and source-tree integrity. Return
  severity-ranked findings with file and line evidence; do not fix them.
- `skill-test-runner`: read-only for repository files and writable only in its temporary
  fixture directory. Run every deterministic validation and smoke test below, inspect
  generated artifacts, and return commands, exit statuses, concise observations, and log
  paths; do not fix failures.

If either agent reports a failure, dispatch a fresh `skill-remediator` with write access
only to the affected destination files. Give it the relevant finding, frozen contract,
affected files, and narrowly relevant source evidence. Rerun the affected independent audit
or test afterward. Stop and report the evidence if the same failure recurs without new
information; do not loop or hide it.

### 5. Run lightweight clean-context forward tests

After deterministic checks pass, dispatch three fresh behavior agents concurrently. Give
each agent read-only access to the completed `codex-skill-creator`, a separate writable
temporary workspace, and one user-like task produced by the architect:

1. Create a focused instruction-only skill.
2. Create a skill that justifies a reusable script or reference and execute its script.
3. Handle an underspecified update to a seeded existing skill, making only narrow justified
   assumptions, preserving intentional content, and comparing against its pre-edit snapshot.

Prompt each behavior agent as an ordinary user would, for example:
`Use $codex-skill-creator at <path> to <task>`. Do not tell it the intended implementation,
suspected weakness, expected answer, grading criteria, or conclusions from earlier agents.
Do not give it the orchestration result contract. Do not let behavior agents share
workspaces or see one another's outputs.

Let each behavior agent complete the task naturally. Have the root capture its raw output,
changed files, validation logs, and final response in the case directory, plus timing and
token data only when the environment exposes them. Then dispatch a fresh read-only
`forward-test-reviewer` with the raw case artifacts, the task-local success criteria, and no
author reports. Require it to separate objective assertions from qualitative findings and
to identify regressions, missing evidence, and quality/cost concerns. Require an explicit
`PASS`, `FAIL`, or `BLOCKED` verdict for every case with criterion-by-criterion evidence; any
unmet required criterion fails the case.

If a failure is prompt- or skill-level, remediate only the affected files and rerun only the
failed case with a fresh behavior agent and workspace. Then dispatch a fresh reviewer with
only the rerun artifacts and the unchanged frozen criteria; do not reuse contaminated
context or earlier grading conclusions. Stop and report the evidence if the same failure
recurs without new information. The three lightweight cases are required validation, not
the optional deep benchmark suite described by the skill.

Do not launch a costly benchmark matrix, open a browser, modify live systems, or require
external credentials for this build. If a required clean-context case would cross one of
those boundaries, do not run it. Treat the build as incomplete, and include the exact
proposed prompt and blocker in the final report.

## Skill design requirements

Preserve these OpenAI baseline strengths:

- concise, high-signal instructions and progressive disclosure;
- appropriate degrees of freedom;
- Codex-native `agents/openai.yaml`;
- `init_skill.py`, `generate_openai_yaml.py`, and `quick_validate.py`;
- explicit planning of scripts, references, and assets;
- imperative instruction style;
- execution tests for every added script;
- clean-context forward testing without answer leakage;
- no unnecessary documentation or placeholder files.

Incorporate these portable Anthropic concepts:

- Capture inputs, expected outputs, edge cases, dependencies, and success criteria.
- Create two or three representative prompts before evaluation.
- Compare a new skill with no-skill behavior and an updated skill with a snapshot of its old
  version during deep evaluation.
- Isolate artifacts by iteration and test case.
- Use objective assertions only for objectively verifiable behavior; use human qualitative
  review for subjective output quality.
- Record timing and token data when the environment exposes them.
- Aggregate pass rates, timing, token usage, variance, and per-case results.
- Analyze non-discriminating assertions, flaky cases, regressions, and quality/cost
  tradeoffs.
- Support blind A/B comparison when independent Codex agents or sessions are available.
- Test descriptions with realistic should-trigger prompts and difficult near-miss
  should-not-trigger prompts.
- Use separate training and held-out cases while optimizing descriptions.
- Iterate from raw outputs, grading evidence, and human feedback.

Define two evaluation levels:

1. **Default lightweight workflow:** understand concrete examples, plan reusable resources,
   initialize and author the skill, validate it, exercise two or three representative
   prompts, and iterate on obvious failures.
2. **Optional deep-evaluation workflow:** use only when the user requests it or the skill is
   complex, fragile, consequential, or difficult to assess. Create structured cases, run
   with-skill and baseline variants in clean contexts, grade objective assertions, present
   subjective outputs for human review, aggregate and analyze results, perform blind
   comparison when useful, and iterate without leaking conclusions into later runs.

Keep the default workflow efficient; do not impose a benchmark suite on ordinary skill
creation.

## Codex-native adaptation rules

Do not copy Anthropic product mechanics unchanged. Specifically:

- Do not use `.claude/commands`, invoke `claude -p`, depend on `CLAUDECODE`, or parse
  Claude-specific stream events.
- Remove Claude.ai, Cowork, `present_files`, and Claude-branded viewer behavior.
- Do not assume Markdown files under `agents/` are Codex subagent definitions.
- Do not ship Anthropic scripts that cannot run in Codex.
- Do not create automated Codex trigger detection from guessed or undocumented behavior.
  Implement it only if official documentation and a local experiment establish a reliable
  activation signal; otherwise document a clean-session manual procedure.
- Use skill folders for local authoring and the current Codex plugin mechanism for broader
  distribution. Do not use `.skill` packaging as the primary Codex mechanism.

Place Codex UI metadata, invocation policy, and MCP dependencies in `agents/openai.yaml`,
not in `SKILL.md` metadata. Keep `SKILL.md` frontmatter limited to `name` and `description`,
and use the unique name `codex-skill-creator` so it cannot collide with the built-in
`skill-creator`.

## Output guidance

Use this tree as guidance, omitting optional files when the frozen contract shows that they
would be incomplete, redundant, or unused:

```text
codex-skill-creator/
├── SKILL.md
├── LICENSE.txt
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── init_skill.py
│   ├── generate_openai_yaml.py
│   ├── quick_validate.py
│   ├── aggregate_benchmark.py
│   └── generate_review.py
├── references/
│   ├── openai_yaml.md
│   ├── evaluation.md
│   ├── eval-schemas.md
│   └── description-testing.md
└── assets/
    ├── eval-viewer.html
    └── trigger-eval-review.html
```

Keep the `SKILL.md` body below 500 lines and preferably substantially shorter. Keep the core
authoring workflow there; move detailed schemas, grading procedures, viewer instructions,
and trigger-test methodology into directly linked references. Explain when each reference
must be read, avoid duplicated guidance, and put every trigger condition in the frontmatter
description. Make the description distinguish ordinary creation and updates, validation and
forward testing, and optional benchmarks and trigger optimization.

Write instructions in imperative form. Explain important constraints without overusing
`ALWAYS` or `NEVER`. Do not add a README, changelog, installation guide, quick-reference
file, unused directory, or placeholder.

Create `agents/openai.yaml` with:

- a clear display name such as `Codex Skill Workbench`;
- a 25-64 character short description;
- a concise default prompt that explicitly mentions `$codex-skill-creator`;
- no icons, brand color, dependencies, or optional fields unless genuinely required.

## Evaluation tooling and licensing

Port only vendor-neutral tooling that the completed workflow uses and tests.
`aggregate_benchmark.py` may be adapted when its input and output schemas are documented and
it has no Claude runtime dependency. Include a static evaluation viewer only when it works
headlessly with documented workflow output and no unnecessary third-party dependency.

For description testing, preserve realistic positive cases, difficult near-miss negative
cases, and train/held-out separation. Do not port `run_eval.py`, `run_loop.py`, or
`improve_description.py` unchanged. If a reliable Codex-native runner cannot be verified,
document the procedure instead of shipping dead automation.

The source projects are expected to contain Apache-2.0 license files; verify that evidence
before relying on it. Preserve applicable licenses and any required attribution or
modification notices. Inspect each source for `NOTICE` or other attribution files. Add a
concise source/modification notice to a substantially adapted script when required, but do
not invent legal claims or extra documentation.

## Deterministic validation

The `skill-test-runner` must, at minimum:

1. Run the new `quick_validate.py` against `codex-skill-creator`.
2. Run `init_skill.py` in its fresh temporary directory.
3. Validate the generated sample skill.
4. Exercise `generate_openai_yaml.py` and inspect the generated YAML.
5. Run `--help` or an equivalent smoke test for every CLI script.
6. If benchmark aggregation is included, create a minimal fixture and verify its generated
   JSON and Markdown.
7. If a review generator or viewer is included, create a minimal fixture and verify the
   generated review and static HTML.
8. Run Python syntax checks without leaving build artifacts in the repository.
9. Search completed runtime files for `Claude`, `claude`, `Cowork`, `.claude`,
   `CLAUDECODE`, and `present_files`; inspect every match and accept only intentional
   attribution or compatibility documentation.
10. Confirm the output contains no placeholders, `TODO` markers, unused files, dead code, or
    broken relative links.
11. Compare source hashes with the pre-edit snapshot and prove neither source changed.
12. Run `git diff --check`. Compare the final worktree with the captured status, staged and
    unstaged binary diffs, and untracked-file hashes. Confirm that every task-introduced
    repository change is under the requested destination and that every pre-existing
    unrelated byte remains intact.

Use temporary directories for all fixtures, generated examples, logs, and evaluation
artifacts. Do not leave them in the repository.

## Acceptance criteria

The work is complete only when:

- the new skill exists at `.codex/skills/codex-skill-creator`;
- both source trees are unchanged and intentional pre-existing destination work is
  preserved;
- the result remains recognizably based on OpenAI's Codex `skill-creator`;
- it adds Anthropic's strongest portable evaluation practices without an unverified Claude
  runtime dependency;
- its default workflow is lightweight and deep evaluation is conditional and progressively
  disclosed;
- `agents/openai.yaml` is current, valid, and consistent with `SKILL.md`;
- every included script and asset participates in a documented workflow and passes its
  tests;
- the skill, an initialized sample, and all three lightweight forward-test cases pass; an
  unrun or `BLOCKED` case leaves the build incomplete;
- no audit contains an unresolved BLOCKER or MAJOR finding;
- no unnecessary documentation, dead code, placeholders, stale branding, or temporary
  artifacts remain.

## Final report

Report:

1. The created path and resulting file tree.
2. The subagent roles used, their exact model/effort, and how context and write ownership
   were isolated.
3. Which OpenAI elements were retained.
4. Which Anthropic elements were incorporated.
5. Which Anthropic components were omitted or rewritten and why.
6. Current-documentation differences discovered, with official links.
7. Validation and smoke-test commands with results.
8. The three clean-context prompts and their results, or the exact blocker for any prompt
   that could not run.
9. Limitations, especially around automatic Codex trigger detection.
10. A concise `git diff --stat`.

Do not commit the changes.
