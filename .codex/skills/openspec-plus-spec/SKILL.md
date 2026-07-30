---
name: openspec-plus-spec
description: "Mandatory behavior-contract workflow for OpenSpec specification artifacts. Use whenever Codex creates, updates, reviews, refines, or discusses change delta specs, or after `openspec instructions spec` or `openspec instructions specs` is requested. Derive testable requirements and scenarios from the approved proposal, align with any existing design and main specs, preserve OpenSpec delta semantics, validate through the CLI, and run an independent compliance review without drifting into implementation."
---

# Produce Valid OpenSpec Delta Specifications

Define observable behavior precisely enough to guide tests and implementation. Specifications describe what the system must do, not its internal architecture, libraries, file layout, or execution plan.

## Non-Negotiable Rules

- Read the approved proposal before analysis. It is authoritative for goals, scope, exclusions, and capability ids.
- Read an existing design when present. It may constrain boundaries but cannot silently add or remove behavior.
- Do not write until guided analysis is confirmed and the drift check passes.
- Every normative requirement must be measurable or testable and follow the CLI-provided grammar.
- Never invent speculative requirements or resolve a proposal/design conflict inside the spec.
- Never edit proposal, design, tasks, main specs, or implementation code from this workflow.
- After a write, require strict CLI validation and exactly one independent compliance review.

Use `update_plan` with four phases and keep exactly one step `in_progress`:

1. resolve schema, paths, and inputs;
2. analyze behavior and resolve ambiguity;
3. check alignment and plan delta operations;
4. write, validate, and independently review.

## Codex Coordination and Routing

Keep the main orchestrator and every planning, design, specification, research, or review agent on `gpt-5.6-sol` with `high` reasoning. This workflow does not dispatch implementers or fixers; those roles belong to implementation workflows and use `gpt-5.6-terra` with `medium` reasoning.

For every delegated research or review task:

- Call `spawn_agent` with `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"` or a positive recent-turn count. Model overrides cannot use a full-history fork.
- Include the working directory, store/change, exact paths, a read-only/no-commit boundary, the question or rubric, required evidence, and return format.
- Use `send_message` only for missing context or scope correction while an agent is active. Use `followup_task` only for a genuinely new bounded assignment to an idle research agent, never to repeat the single-shot compliance review.
- Use `wait_agent` to collect terminal results and verify cited evidence before relying on it.

If mandatory reviewer dispatch is unavailable or terminates without reviewing, report the workflow blocked. A root-agent self-review is not an independent substitute.

## Interaction Modes

Use guided mode by default. Accelerated mode activates only when the user explicitly asks to fast-forward, skip questions, keep momentum, or generate artifacts without routine pauses. Ordinary continuation such as “continue,” “proceed,” or “yes” does not activate it.

- Guided mode asks only unresolved questions, one at a time, and requires confirmation before writing.
- Accelerated mode performs the same evidence gathering, completeness analysis, alignment checks, validation, and independent review. Convert safe assumptions into explicit requirements or scenarios and pause when ambiguity could change scope, security, compatibility, failure behavior, or a delta operation.

If the user asks only to discuss or review specifications, remain read-only. Analyze the requested concerns and review existing delta files, but do not edit without explicit authorization.

## Phase 1: Resolve Schema, Paths, and Inputs

### Select the root, change, and artifact

If the user names a registered store, run `openspec store list --json`, resolve the exact id, and retain `--store <id>` on every store-aware command. Otherwise let OpenSpec resolve the nearest local root.

If the user wants only conceptual specification advice and no change exists, remain read-only and discuss the behavior-contract principles relevant to their question. Do not fabricate schema instructions or a review result. If they want an artifact, ask them to select or create a change through the appropriate OpenSpec workflow first.

Resolve the change from explicit input or unambiguous conversation context. If needed, run `openspec list --json` and ask the user directly to choose among plausible changes. Do not create or guess a change.

Run:

```bash
openspec status --change "<name>" --json
```

Use `schemaName`, `planningHome`, `changeRoot`, `artifactPaths`, `actionContext`, `artifacts`, and `nextSteps` from valid JSON.

If a surrounding workflow supplied an exact selected artifact id and fetched instruction contract, require that the id exists in this fresh status, the contract reports the same id/schema/change root, and its output paths agree with `artifactPaths.<id>`. Stay on that artifact even when the schema has other specification-producing artifacts; do not silently rediscover or switch ids.

Otherwise identify the specification artifact id from the active schema—commonly `specs`, sometimes `spec`—using its instruction, template, dependency role, and output contract rather than the id alone. If several artifacts can produce delta specs and the user's target does not select exactly one, show the candidates and ask directly; do not merge their contracts. Stop when the selected artifact is blocked. If it reports `skipped` because `skip_specs: true`, report that the change declares no spec-level behavior and do not create files; contradictory proposal capabilities must return to `openspec-plus-proposal`.

When no verified caller-supplied contract is available, run the exact artifact id:

```bash
openspec instructions <spec-artifact-id> --change "<name>" --json
```

When a verified caller-supplied contract is available, reuse it instead of fetching a different artifact contract. In both cases require the contract's `artifactId` to equal `<spec-artifact-id>` before reading or writing any delta.

Record:

- `schemaName`, `changeDir`, `outputPath`, `resolvedOutputPath`, and `existingOutputPaths`;
- `template`, the baseline structure and placeholder grammar;
- `instruction`, the authoritative delta, path, and scenario rules;
- `context` and `rules` when present;
- `dependencies`, including completion and paths;
- optional `references`, `skipped`, and `warning`.

Treat context and rules as constraints, never artifact text. Treat references as read-only upstream contracts and fetch only those relevant to the selected capabilities. Stop on missing dependencies or path/scope contradictions.

### Read authoritative planning inputs

Resolve every completed dependency path beneath `changeDir`, expanding CLI-returned globs to concrete files. Read the approved proposal and all existing delta paths from `artifactPaths.<spec-artifact-id>.existingOutputPaths`. Read every existing design path reported by status, even when design is not a direct dependency, because a design-first workflow must remain behaviorally aligned.

Read applicable `AGENTS.md` files and relevant domain documentation. Do not copy project instructions into specs.

From the proposal, build the exact expected capability set and classification. Compare it with:

```bash
openspec list --specs --json
```

For every modified capability, require an exact existing main-spec id and read `<planningHome.root>/openspec/specs/<capability>/spec.md`. A proposed new capability must not silently collide with a main spec. If proposal classification is missing or wrong, stop and return to `openspec-plus-proposal`.

Derive one concrete delta path per capability from the instruction. In the default schema this is `<changeRoot>/specs/<capability>/spec.md`; custom schemas must follow their own instruction. A glob-valued `resolvedOutputPath` is a pattern, never a writable file.

### Ground current behavior only when necessary

Proposal, design, main specs, and user decisions are the default behavioral sources. Do not read implementation code in the main spec-agent context.

When a requirement explicitly depends on undocumented current behavior, dispatch a bounded read-only research agent with this contract: inspect only named source/test paths; report externally observable inputs, outputs, state changes, errors, side effects, and evidence locations; omit internal algorithms, data structures, and implementation recommendations. Use the result only to ground current behavior and terminology.

## Phase 2: Analyze Behavior and Resolve Ambiguity

Maintain a decision ledger containing accepted requirements, scenario branches, constraints, terminology, and explicitly rejected alternatives. Reuse recent user answers and artifact facts; never ask the user to repeat resolved information or answer discoverable questions.

### Extract and test requirements

For each capability:

1. Extract behavior implied by the proposal and any existing design.
2. For a modified capability, compare against its main spec and identify the exact behavioral delta.
3. Normalize each normative requirement into an observable statement using `SHALL` or `MUST` when the active instruction requires it. Use weaker terms only when intentionally non-normative.
4. Check completeness across applicable actors, normal flow, invalid or missing input, permissions, security/privacy, integration boundaries, concurrency, retry, partial failure, reliability, compatibility, and measurable non-functional constraints.
5. Remove speculative behavior that does not trace to proposal scope or a present stakeholder need.

For every gap or ambiguous term that affects behavior, ask one concise direct question in guided mode. Provide concrete options when helpful, mark the recommended answer, and give a short rationale. Resolve dependent decisions before moving on; do not batch unrelated questions.

### Define parseable scenarios

Follow the exact scenario grammar returned by the CLI. For the default spec-driven schema:

```markdown
#### Scenario: Descriptive name
- **WHEN** an observable event or condition occurs
- **THEN** an observable outcome occurs
- **AND** an additional observable outcome occurs
```

- Use exactly four hashes for each scenario header.
- Keep each keyword step on its own Markdown bullet line.
- Use `WHEN` and `THEN`; add `AND` only when it improves clarity. Use other keywords only if the active instruction explicitly allows them.
- Every requirement needs at least one scenario. Add positive, negative, failure, permission, and edge scenarios when distinct applicable branches exist; do not manufacture redundant variants.
- Keep implementation names, algorithms, libraries, internal calls, and test mechanics out of steps.
- Express non-functional behavior as measurable normative requirements with a validation scenario when the instruction requires scenarios for every requirement.

If a requirement cannot be expressed as observable scenarios, it is still ambiguous or belongs in design/tasks rather than the spec.

### Confirm guided analysis

In guided mode, present a compact summary by capability: normative requirements, scenario branches, error/edge decisions, external constraints, and any intentional exclusion. Ask the user to confirm shared understanding; silence is not approval.

Before continuing, ensure every template/instruction requirement has substance and every applicable rule is satisfied.

## Phase 3: Check Alignment and Plan Delta Operations

Re-read the proposal, accepted decision ledger, existing design, relevant main specs, and existing delta files. Stop on any contradiction, scope expansion, relaxed exclusion, or design-imposed behavior absent from the proposal. Route intent changes to `openspec-plus-proposal` and architecture conflicts to `openspec-plus-design`; do not paper over them in a delta spec.

Build a per-file operation plan using the instruction as authority:

- `ADDED Requirements`: new requirements, including requirements in a new capability.
- `MODIFIED Requirements`: changed existing behavior. Copy the complete main requirement block, preserve all still-valid scenarios, edit it to the full desired state, and keep the requirement name an exact match.
- `REMOVED Requirements`: include every required reason and migration field.
- `RENAMED Requirements`: use the required old/new name form and reserve it for name-only changes. Pair it with the appropriate behavioral operation when behavior also changes, if the instruction permits.

For a new capability, include the required `## Purpose` content and minimum substance. Do not add a delta Purpose section for an existing capability. Never edit a main spec to change its Purpose from this workflow.

Check that each proposal capability has exactly one intended concrete delta file, no operation is duplicated or contradictory, and every accepted in-scope behavioral decision maps to a requirement or scenario. Do not write yet if the operation plan is incomplete.

## Phase 4: Write, Validate, and Independently Review

### Write concrete delta files

Use `apply_patch` to create or update only the planned concrete paths. Preserve unrelated user-authored operations in existing files. Follow the returned template grammar and every allowed delta section from the instruction; remove unused placeholders and do not add arbitrary headings.

Preserve the decision ledger's full behavioral specificity while editing for coherent specification prose. Do not copy the discovery transcript verbatim. Each scenario must retain the accepted condition, trigger, outcome, and distinct failure or edge branch.

Re-read every written file against the operation plan and decision ledger. Fix missing accepted behavior, contradictory scenarios, placeholder text, partial MODIFIED blocks, and terminology drift before validation.

### Require parser and semantic validation

Run:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
openspec show "<name>" --type change --json --deltas-only --no-interactive
```

Add the selected store flag. Require zero exit status, valid JSON, and no validation errors. Confirm the parsed deltas contain every intended capability, operation, requirement, and scenario. Fix deterministic document defects inline; if validation exposes unresolved intent or an upstream conflict, stop and ask the user or return to the owning planning skill.

For review-only requests, run these non-mutating checks against existing deltas and include failures in the findings.

### Dispatch one mandatory compliance reviewer

In write mode, dispatch only after successful validation. In read-only review mode, dispatch even when validation fails so the user receives semantic findings alongside parser errors; such a review cannot return an overall approved outcome until the CLI errors are resolved.

Dispatch one fresh read-only reviewer for all selected delta files with `spawn_agent` and the required `gpt-5.6-sol`/high routing. Provide:

- working directory, store/change, and exact delta paths;
- proposal, existing design, and relevant main-spec paths;
- template, instruction, context, rules, and decision ledger;
- validation and parsed-delta output;
- the following rubric and return contract.

Reviewer rubric:

- each requirement traces to proposal scope and preserves exclusions;
- design alignment introduces no new behavior or contradiction;
- new/modified capability ids and concrete paths are correct;
- delta operation choice is correct, with complete MODIFIED blocks and required REMOVED/RENAMED metadata;
- new-capability Purpose is present and substantive; existing-capability delta has no Purpose;
- normative statements are unambiguous, measurable, and implementation-independent;
- every requirement has correctly formatted scenarios and applicable positive, negative, failure, permission, and edge branches;
- scenarios describe observable behavior using the CLI-required Markdown grammar;
- template, instruction, context, rules, and terminology are satisfied;
- there are no placeholders, internal implementation choices, tasks, estimates, or speculative requirements.

Require:

```text
Status: Approved | Issues Found

Issues:
- [category] [file and evidence] — [downstream impact] — [specific correction]

Advisory:
- [optional non-blocking observation]
```

The reviewer must not edit files. Use `wait_agent`; use `send_message` only for missing context or scope correction. Do not redispatch or use `followup_task` for another compliance pass after fixes.

### Apply findings once and finish

If issues are found, verify them against the controlling inputs and apply every valid blocking correction inline. Ask the user before changing unresolved product behavior; a reviewer cannot choose scope. Do not redispatch during the same invocation.

After corrections, rerun both strict validation and parsed-delta inspection. Do not claim approval when either fails. Re-run `openspec status --change "<name>" --json` and require the specification artifact to be `done` unless the request was read-only review.

Report the change/schema, concrete files created or updated, capabilities and delta operations, key resolved decisions, validation result, reviewer result and fixes, downstream artifacts that may now be stale, and fresh next steps. Do not automatically start design, tasks, or implementation.
