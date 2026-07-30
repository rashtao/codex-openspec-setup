---
name: openspec-plus-proposal
description: "Mandatory intent-level workflow for an OpenSpec proposal. Use whenever Codex is about to create, update, review, refine, or discuss a proposal artifact, or after `openspec instructions proposal` is requested. Elicit the problem, outcomes, scope, capability deltas, exclusions, and impact; enforce template and project rules; and run an independent proposal review without drifting into design, specifications, or implementation."
---

# Produce an Intent-Level OpenSpec Proposal

Create a lean proposal that establishes why a cohesive change is needed and what changes at a high level. Keep architecture, detailed requirements, scenarios, task breakdowns, estimates, and implementation choices in their downstream phases.

## Non-Negotiable Boundary

- Understand the problem before defining scope.
- Separate desired outcomes from proposed solutions. Preserve a user-mandated technical constraint only when it materially defines scope, and label it as a constraint rather than designing around it.
- Include no speculative capability. Every in-scope item must trace to a stated need, stakeholder, or required compatibility boundary.
- Keep related capabilities together when they serve one outcome. Split independent outcomes that could be delivered and evaluated separately.
- Do not write while a scope decision remains unresolved in normal guided mode.
- Never edit implementation code, design, specifications, or tasks from this workflow.

Use `update_plan` for the three phases below. Keep exactly one phase `in_progress` and update it as work advances:

1. resolve context and template;
2. discover and confirm intent;
3. write and independently review.

## Codex Routing

Keep the main proposal orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `high` reasoning. This workflow never dispatches implementer or fixer agents; those roles belong to implementation workflows and use `gpt-5.6-terra` with `medium` reasoning.

The independent reviewer is mandatory after a write. Launch it with `spawn_agent`, `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"` (or a positive recent-turn count). Model overrides cannot use a full-history fork.

## 1. Resolve Context and Template

### Select the planning root and change

If the user names a registered store, run `openspec store list --json`, resolve its exact id, and add `--store <id>` to every store-aware command below. Otherwise let the CLI resolve the nearest local OpenSpec root.

Resolve the change name from explicit input or unambiguous conversation context. If it remains ambiguous, run `openspec list --json`, show the plausible active changes, and ask the user directly to choose. Do not create a change in this skill and do not guess.

Run:

```bash
openspec status --change "<name>" --json
openspec instructions proposal --change "<name>" --json
```

Require zero exit status and valid JSON. Use `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, and `schemaName` from status rather than assuming repo-local paths. Stop if the schema has no `proposal` artifact or if its status is blocked/skipped in a way the instruction does not authorize.

From the instruction response, record:

- `template`: structural authority;
- `instruction`: content and capability-classification guidance;
- `rules`: artifact-specific constraints when present;
- `context`: project facts and conventions when present;
- `resolvedOutputPath` and `existingOutputPaths`: concrete proposal location and current-file state.

Treat context and rules as constraints, never text to copy into the proposal. Require the resolved path to be concrete and inside the CLI-reported allowed edit scope. A proposal is normally singular; if the path is a glob or ambiguous, stop and report the invalid contract rather than inventing a file.

Read all applicable `AGENTS.md` files, relevant project documentation, and existing proposals for domain terminology and established scope language. Read the current proposal when it exists. Inspect source or tests only when needed to verify a factual current-behavior or impact claim; do not derive architecture or implementation plans from that inspection.

List existing main capabilities with:

```bash
openspec list --specs --json
```

With a store, add its flag. Use exact existing capability names when classifying modified behavior. Read or show only the main specs relevant to a claimed modification, using `openspec show "<capability>" --type spec --json --no-interactive` when helpful. Never infer that a capability is new merely because its name was not guessed correctly.

### Choose interaction mode

Use guided mode by default. Accelerated mode activates only when the user explicitly asks to fast-forward, skip questions, keep momentum, or create artifacts without review pauses. Ordinary words such as “continue,” “proceed,” or “yes” do not activate it.

- Guided mode asks only unresolved questions and requires scope confirmation before writing.
- Accelerated mode extracts answers from the request and prior conversation, states material assumptions in the appropriate template sections, and pauses only when ambiguity would change scope, capability classification, breaking-change status, or `skip_specs` eligibility.

If the user requested discussion or review only, remain read-only. Analyze the relevant questions and review an existing proposal when one is present, but do not write until the user explicitly asks for an edit. For a review-only request, skip the write step and dispatch the reviewer under the Phase 3 contract, then report findings without applying them.

## 2. Discover and Confirm Intent

Reuse facts already established in recent conversation and artifacts. Never ask the user to repeat a resolved answer or to provide a fact that can be discovered safely.

Cover these lenses, plus any additional information required by the resolved template:

1. **Problem and why now** — current pain or opportunity, affected actor, consequence of doing nothing.
2. **Desired outcome** — observable improvement without prescribing its implementation.
3. **Scope and capabilities** — high-level behavior added, changed, removed, or explicitly preserved.
4. **Non-goals** — adjacent work excluded to prevent scope creep.
5. **Impact** — affected users, workflows, APIs, dependencies, systems, or code areas at an appropriate confidence level.

In guided mode, ask one concise direct question at a time. Include a recommended answer and short rationale when there is a meaningful choice. Follow dependent branches before advancing; do not batch unrelated decisions.

### Keep the change cohesive

When the request spans several areas, distinguish multiple related capabilities from independent changes. Decompose only when an area has a distinct outcome, release boundary, or validation story. Explain the proposed split and ask which change to pursue first; do not create sibling changes automatically.

### Classify capability deltas

Use the CLI instruction and existing main specs as the authority:

- **New capability**: behavior with no matching main capability; use a stable kebab-case id.
- **Modified capability**: requirements of an existing main capability change; use its exact id and state the behavioral delta.
- **No spec-level behavior change**: pure refactor, tooling, or documentation work may declare `skip_specs: true`; never invent a requirement merely to satisfy validation.

Do not classify implementation-only changes as modified capabilities. Mark a breaking change exactly as the template instruction requires.

Identify specification artifacts dynamically from status before changing `skip_specs`: inspect each `artifactPaths.<id>.outputPath`, `resolvedOutputPath`, and concrete `existingOutputPaths`; retain the exact artifact id for every artifact whose outputs target `<changeRoot>/specs/`. When an output contract is ambiguous, fetch `openspec instructions <artifact-id> --change "<name>" --json` and require its id and paths to agree. Stop if a concrete file beneath the specs root has no unique owning artifact.

If no capability delta is legitimate, explain why the change is behavior-neutral and ask the user to confirm `skip_specs: true`. Require every dynamically identified specification artifact's `existingOutputPaths` to be empty; if delta files already exist, do not delete them here—report the contradiction for the cross-artifact update workflow. After confirmation, add the boolean to `<changeRoot>/.openspec.yaml` with `apply_patch`, preserving all metadata. Do not assume the specification artifact id is `specs`.

If requirements do change while `skip_specs` is true, surface the conflict and obtain confirmation before removing or setting the marker false. Never leave the marker alongside delta specs, and never create or delete spec files from this skill. Re-run status and proposal instructions after changing metadata because it changes the artifact graph.

### Confirm before writing

In guided mode, summarize the problem, outcome, in-scope capabilities, exclusions, impact, breaking-change status, and capability classification. Ask the user to confirm the shared understanding. Do not treat silence as approval.

Before advancing, verify:

- every template section has enough substance;
- every scope item traces to a need;
- no independent change is bundled in;
- capability ids agree with existing main specs;
- every instruction and applicable rule can be satisfied;
- no unresolved decision belongs in the proposal.

## 3. Write and Independently Review

### Write the proposal

Use the template's headers, order, and comments as the structural contract. Replace instructional placeholders with concise content; do not add a standard section the active template does not define. Preserve confirmed substance and specificity while editing for coherence—do not copy conversational fragments verbatim or inflate the artifact with the discovery transcript.

Keep detailed acceptance behavior in specs and technical approach in design. Record exclusions within the most appropriate template section when no dedicated non-goals section exists. Use `apply_patch` to create or update only the concrete proposal path. Preserve unrelated user edits when revising an existing file.

After writing, verify the file exists, contains no template placeholders, and matches the template structure. Re-run:

```bash
openspec status --change "<name>" --json
```

Require the proposal artifact to report `done`. Do not start downstream artifacts from this skill.

### Dispatch the mandatory reviewer

Call `spawn_agent` once with a unique task name and the routing above. The complete delegation message must include:

- repository working directory and selected store/change;
- exact proposal path;
- resolved template, instruction, and applicable rules;
- a read-only constraint and prohibition on commits;
- the review rubric and required return format below.

Use `send_message` only to correct scope or supply missing input while the reviewer is active. Use `wait_agent` until it returns a terminal result. Do not use `followup_task` for a second review after fixes; it is only appropriate if an idle agent must perform a genuinely new bounded task. Inspect the returned evidence before accepting it.

If subagent dispatch is unavailable, or the reviewer terminates without performing the review, report that the mandatory independent review is blocked. Do not substitute a root-agent self-review or claim approval.

Reviewer rubric:

- problem and urgency are clear;
- outcomes are distinct from solutions;
- scope is cohesive and each item traces to a need;
- exclusions prevent material ambiguity where applicable;
- new/modified capabilities use correct ids and classification;
- breaking changes are marked as instructed;
- impact claims are supported and appropriately qualified;
- no design, detailed requirements, scenarios, tasks, sequencing, estimates, or speculative technology leaked in;
- every template section is present in order with no placeholder;
- instruction and rules are satisfied;
- terminology is consistent.

Require this response:

```text
Status: Approved | Issues Found

Issues:
- [category] [proposal evidence] — [why it misleads a downstream phase] — [specific correction]

Advisory:
- [optional non-blocking observation]
```

Calibrate issues to downstream correctness, not stylistic preference. The reviewer must not edit files.

### Apply findings once

If approved, present the proposal for user review. If issues are found, verify each against the template, instruction, rules, and confirmed intent; apply valid corrections inline with `apply_patch`, then present the result. Do not redispatch the reviewer after fixes during the same invocation.

If a finding exposes unresolved user intent rather than a document defect, ask the user directly before changing it. Do not let a reviewer choose product scope.

## Final Report

Report:

- change name, schema, and concrete proposal path;
- whether the proposal was created, updated, or reviewed without edits;
- new and modified capability ids, or confirmed `skip_specs` state;
- reviewer status and corrections applied;
- downstream artifacts that may now be stale and need cross-artifact reconciliation;
- any unresolved decision;
- next artifact(s) reported by fresh `openspec status` output.

Success requires confirmed intent in guided mode, template/rule compliance, coherent capability classification, a placeholder-free artifact when writing, one independent review, and no leakage into downstream phases.
