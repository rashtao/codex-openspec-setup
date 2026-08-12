---
name: openspec-verify-change
description: Verify an OpenSpec change implementation against its live planning artifacts and fresh evidence. Use when the user wants a read-only assessment of completeness, correctness, test strength, design coherence, compatibility, integration, or readiness before archiving.
---

# Verify an OpenSpec change

Inspect the selected change, implementation, and available fresh evidence, then report findings. The action's sandbox permits ordinary build/test outputs so fresh commands can run, but verification remains semantically read-only: do not fix or edit source, planning artifacts, task state, main specs, archive state, Git state, configuration, or a repository report. Do not use workspace-write permission for any authored project change.

## Route once

If the current task prompt contains `ROUTED_ACTION=openspec-verify-change`, execute this installed skill directly and never route `openspec-verify-change` again.

Otherwise, call exactly:

```text
spawn_agent({
  task_name: "openspec_verify_change",
  message: "ROUTED_ACTION=openspec-verify-change. Execute the latest user request directly. Read .codex/skills/openspec-verify-change/SKILL.md and follow it. Never route openspec-verify-change again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "xhigh"
})
```

Wait for that child and return its result. Do not use an agent selector, role-name parameter, pseudo-tool, or any other creation mechanism. Do not dispatch another action-role child from the routed role.

## Select the planning root and change

Accept an optional change name. If the user names a registered store, or the work is in one, run:

```bash
openspec store list --json
```

Resolve the registered store id and append `--store "<id>"` to every supported follow-up command in this workflow. Treat the selection as sticky. Without a selected store, commands use the nearest local `openspec/` root. Do not pass a store flag to a command that does not support it.

Select the change in this order:

1. Use the explicitly supplied name.
2. Otherwise infer a name only when the conversation identifies it unambiguously.
3. Otherwise run `openspec list --json` with the sticky store flag when applicable. Use only its names, task counts/status, `lastModified`, and response-level root. Auto-select only when exactly one active change exists.
4. If more than one candidate remains, run `openspec status --change "<candidate>" --json` with the sticky store flag for every candidate before using schema or artifact inventory. Ask the user to select from candidates whose status reports an implementation-task artifact, include `schemaName` from that status, and use list task counts to mark incomplete work as `(In Progress)`. Report a candidate status failure as unavailable rather than guessing or defaulting its schema. Do not make these per-candidate calls when selection needs only list-provided names/progress.

Always announce `Using change: <name>` and say that the user can rerun this action with another change name to override the selection. Do not emit a slash invocation.

## Load live state

Run these current CLI calls, appending the sticky store flag when applicable:

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Do not infer the schema, artifact graph, or paths from familiar filenames. Parse the status payload fields `changeName`, `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `nextSteps`, `actionContext`, `isPlanningComplete`, `isComplete`, `applyRequires`, `artifacts`, and `root` when present. For each `artifactPaths` entry, preserve `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`. For each artifact, preserve `id`, `outputPath`, `status`, `requires`, and any `missingDeps`; artifact status is exactly `done`, `skipped`, `ready`, or `blocked`.

Parse the apply-instructions payload fields `changeName`, `changeDir`, `schemaName`, `contextFiles`, `progress`, `tasks`, `state`, `missingArtifacts`, `instruction`, `references`, `context`, `operationGuidance`, and `root` when present. Read every concrete path in every `contextFiles` entry, regardless of artifact id. Treat `context` as required project constraint, `operationGuidance` as advisory, and `references` as read-only upstream context. Never reconstruct artifact paths.

Preserve the apply-state meaning exactly:

- `blocked`: inspect all available artifacts and implementation, but report the exact missing artifacts, absent tracking file, or tracking file with no actionable tasks described by `instruction`. Do not create the missing content.
- `all_done`: task checkboxes report complete; independently verify that implementation and evidence support that claim. This state is not proof that verification passes.
- `ready`: incomplete implementation work may remain, or the schema may have no tracking file. Verify the actual `tasks`, `progress`, artifacts, diff, and evidence without changing them.

Skipped artifacts satisfy live dependency calculations without implying a file exists. A missing optional artifact narrows the applicable review; it does not authorize guessing its contents.

## Establish review inputs

Build an evidence packet before reaching conclusions:

- authoritative paths and live fields from both CLI payloads;
- full contents of every available context file;
- repository instruction and standards files that govern the changed code;
- the relevant working-tree/index diff and, when a reliable base is explicit or discoverable, the bounded historical diff and commit list;
- changed-file paths and nearby production/test code needed to understand behavior;
- raw outputs, exit codes, scope, environment, and workload for every verification command or measurement;
- explicit limitations, unavailable tools/services, and alternate evidence.

Do not treat an implementer summary, checked task, generated skill, keyword match, test name, or reviewer assertion as proof. Trace claims to artifacts, actual code, behavioral tests, and command output. Redact secrets and sensitive payloads from quoted evidence.

If no reliable historical base exists, say so and inspect the available working tree, index, current files, and task-to-code evidence. Do not invent a base or call the lack of a diff a pass.

## Load shared guidance only for an exact need

Read the following references only under the stated condition and record the reason in working notes:

- `../openspec-shared/references/artifact-quality.md` when assessing the substance, coherence, traceability, or template compliance of intent, behavioral specification, technical design, implementation-task, or unknown custom artifacts.
- `../openspec-shared/references/evidence-first.md` when selecting or interpreting commands needed for a pass, complete, fixed, or ready claim; reason: determine what fresh evidence supports each claim and how to report unavailable evidence.
- `../openspec-shared/references/review.md` when performing or dispatching independent review; reason: calibrate finding-oriented, read-only review and evidence handoff.
- `../openspec-shared/references/subagents.md` before any specialist dispatch; reason: apply the verified spawn form, context isolation, nonrecursive guard, and result-integration rules.
- `../openspec-shared/references/integration-correctness.md` when the change touches a connector, protocol, external service, framework hook, persistence boundary, or runtime-version contract; reason: assess real boundary semantics and integration evidence.
- `../openspec-shared/references/performance-memory.md` when the change plausibly affects latency, throughput, allocation, buffering, caching, pooling, serialization, or resource lifetime, or makes a quantitative claim; reason: evaluate baseline, workload, thresholds, and comparable measurements.
- `../openspec-shared/references/debugging.md` when fresh evidence fails, is flaky, or contradicts an artifact or prior claim and diagnosis is needed to classify the finding; reason: isolate the failing boundary and avoid speculative diagnosis. Remain read-only.
- `../openspec-shared/references/research.md` when repository evidence is insufficient and exact dependency, protocol, framework, or runtime behavior matters; reason: gather version-matched primary-source evidence and distinguish fact from inference.

Do not load references merely because they exist. Their guidance may strengthen verification but may not change this action's state, boundary, or stopping point.

## Verify applicable axes

Create a traceability map before judging the implementation. Use the loaded canonical artifact-quality, evidence, and review references rather than restating their general doctrine here.

### Completeness

- Use `contextFiles` and `tasks` dynamically; do not require familiar artifact ids.
- Compare the CLI's `progress` and `tasks` with any exact checkbox evidence found in reported context files. The payload has no tracking-path field; if the checkbox source cannot be located unambiguously, report the limitation rather than infer a file. Treat each CLI-reported incomplete actionable task as CRITICAL. A checked task is still subject to implementation verification.
- Map every behavioral requirement and scenario to implementation and tests. Treat a confirmed missing requirement implementation as CRITICAL.
- Check that the relevant proposal scope, spec requirements, design decisions, and task outcomes are represented without placeholders or unexplained omissions.
- Distinguish intentionally skipped or inapplicable artifacts from missing evidence.

### Spec correctness and test strength

Apply `artifact-quality.md` to the live behavioral artifacts and `evidence-first.md` to their implementation evidence. Report missing scenario evidence as `WARNING` unless it establishes a missing required implementation, which is `CRITICAL`.

### Artifact and design coherence

Apply `artifact-quality.md` and `review.md` across the live planning artifacts, implementation, and repository conventions. When implementation exposes an artifact gap, identify the owning artifact and future correction; never edit it in this action.

### Integration correctness

When relevant, load and apply `integration-correctness.md` and the evidence contract to the implemented boundary.

### Performance, memory, errors, resources, and concurrency

For applicable performance or memory concerns, load `performance-memory.md`. For applicable error, resource, or concurrency behavior at an integration boundary, load `integration-correctness.md`. Use `review.md` to scope the finding axis and do not invent a universal checklist.

### Fresh verification

Discover supported verification commands from repository evidence and apply `evidence-first.md` to their selection, freshness, scope, results, and limitations. Ordinary tool-generated build/test outputs are allowed; authored source, artifact, task, spec, archive, configuration, Git-state, and report changes remain forbidden. Do not install dependencies or mutate external systems unless separately authorized.

## Dispatch independent specialists selectively

Dispatch only when an axis is relevant and independent context materially improves confidence. Load `review.md` and `subagents.md` and follow their canonical handoff, independence, ownership, concurrency, and integration contracts.

Use only these verified calls with the listed explicit route, replacing every packet placeholder with the complete current evidence packet:

- Test strength: `spawn_agent({ task_name: "verify_tests", message: "Independently assess test strength for this bounded verification axis. Remain read-only, report findings only, and do not spawn agents. Complete packet: <objective; exact artifact/test/diff paths or contents; repository standards; raw commands, outputs, exits, scope, and limitations; expected return>.", fork_turns: "none", model: "gpt-5.6-sol", reasoning_effort: "high" })`
- Spec correctness and completeness: `spawn_agent({ task_name: "verify_spec", message: "Independently compare implementation and tests with every supplied planning artifact. Remain read-only, report findings only, and do not spawn agents. Complete packet: <objective; all artifact and implementation paths or contents; repository standards; raw evidence and limitations; expected return>.", fork_turns: "none", model: "gpt-5.6-sol", reasoning_effort: "high" })`
- Performance and memory: `spawn_agent({ task_name: "verify_perf_memory", message: "Independently assess the supplied performance or memory claim. Remain read-only, report findings only, and do not spawn agents. Complete packet: <objective; artifacts; diff; workload; environment; measurements; correctness evidence; limitations; expected return>.", fork_turns: "none", model: "gpt-5.6-sol", reasoning_effort: "high" })`
- Focused integration, error, resource, or concurrency discovery: `spawn_agent({ task_name: "verify_code", message: "Independently inspect the named bounded code question. Remain read-only, report evidence only, and do not spawn agents. Complete packet: <focused question; artifact and changed paths or contents; repository standards; raw evidence and limitations; expected return>.", fork_turns: "none", model: "gpt-5.6-terra", reasoning_effort: "high" })`
- High-consequence final synthesis across three or more applicable axes: `spawn_agent({ task_name: "verify_consistency", message: "Independently assess cross-artifact and cross-axis consistency. Remain read-only, report findings only, and do not spawn agents. Complete packet: <objective; every authoritative artifact; full relevant diff; prior findings; repository standards; raw evidence and limitations; expected return>.", fork_turns: "none", model: "gpt-5.6-sol", reasoning_effort: "xhigh" })`

Parallelize independent read-only reviews when useful. Do not summon every specialist, delegate a trivial local read, use an unlisted role, or use a specialist as an implementer. Validate every returned finding against the repository and raw evidence. A reviewer assertion alone is not a finding.

## Classify findings

Every issue must cite the artifact expectation, implementation/evidence location, concrete impact, and an actionable recommendation. Use code references such as `file.ts:123` where available.

- `CRITICAL` (must fix before archive): incomplete actionable tasks; confirmed missing requirement implementation; broken required behavior; or another confirmed correctness, security, compatibility, data-loss, integration, resource, or concurrency defect that makes archiving unsafe.
- `WARNING` (should fix): spec/design divergence; missing or unfaithful scenario evidence; unsupported compatibility or performance claim; significant repository-pattern deviation; or degraded verification that prevents a required claim.
- `SUGGESTION` (nice to fix): non-blocking pattern inconsistency, minor maintainability improvement, or low-confidence concern that warrants targeted follow-up.

Prefer SUGGESTION over WARNING and WARNING over CRITICAL when uncertainty remains. Do not dilute a confirmed severe defect. Separate an artifact defect from an implementation defect and recommend the correct future action without making the change.

## Report

Return clear Markdown in this structure:

```markdown
## Verification Report: <change-name>

### Summary
| Dimension | Status |
|---|---|
| Completeness | X/Y tasks; N requirements assessed |
| Correctness | M/N requirements covered; scenario/test evidence status |
| Coherence | Followed/Issues; applicable specialist axes |

### Evidence
- `<command>` — exit/result, scope
- DEGRADED: <unavailable command or missing evidence> — <reason and affected claim>
- Skipped axis: <axis> — <why it is not relevant>

### CRITICAL
- <finding, artifact expectation, file:line/evidence, impact, recommendation>

### WARNING
- <finding, artifact expectation, file:line/evidence, impact, recommendation>

### SUGGESTION
- <finding, file:line/evidence, recommendation>

### Final Assessment
<assessment>
```

Write `None.` for an empty severity section. State every skipped or degraded check and why.

Use the current final-assessment wording:

- With critical findings: `X critical issue(s) found. Fix before archiving.`
- With warnings only: `No critical issues. Y warning(s) to consider. Ready for archive (with noted improvements).`
- With no findings and sufficient fresh evidence: `All checks passed. Ready for archive.`
- With no confirmed findings but insufficient evidence, do not use a passing form; state `No confirmed issues, but verification is degraded: <reason>. Archive readiness is not established.`

Do not claim ready, complete, correct, fixed, passing, or compliant without fresh applicable evidence. End after reporting; do not begin fixes or archival work.
