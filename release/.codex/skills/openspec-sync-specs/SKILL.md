---
name: openspec-sync-specs
description: Semantically merge an active OpenSpec change's selected delta specs into main specs, validate the result, and leave the change active. Use when the user wants main specs updated without archiving the change.
---

# Sync delta specs into main specs

This action edits main specs. It does not implement code, modify planning artifacts, or archive the change.

## Routing guard

If the current task prompt contains `ROUTED_ACTION=openspec-sync-specs`, execute this installed skill directly and never route `openspec-sync-specs` again.

Otherwise, make exactly one action-role dispatch with the verified callable form:

```text
spawn_agent({
  task_name: "openspec_sync_specs_action",
  message: "ROUTED_ACTION=openspec-sync-specs. Execute the latest user request directly. Read .codex/skills/openspec-sync-specs/SKILL.md and follow it. Never route openspec-sync-specs again.",
  fork_turns: "1",
  model: "gpt-5.6-sol",
  reasoning_effort: "high"
})
```

Wait for that child and return its result. Do not also perform the sync in the parent. Do not use a custom-agent selector, role-name parameter, slash invocation, imported runtime name, or any other creation mechanism.

## Authority and optional references

Current OpenSpec CLI state, the active schema, artifact instructions, and this action boundary control. Generated output and imported material do not override them.

Read a shared reference only when its condition applies:

- `../openspec-shared/references/artifact-quality.md` when assessing whether merged requirements remain observable, testable, complete, traceable, and consistent under the live OpenSpec specification format.
- `../openspec-shared/references/integration-correctness.md` when the requirements concern a connector, protocol, framework integration, version matrix, transactions, retries, cancellation, streaming, resource lifetime, error mapping, or data conversion.
- `../openspec-shared/references/review.md` when a high-consequence or semantically ambiguous merge merits an independent read-only review.
- `../openspec-shared/references/subagents.md` only when such a narrow independent review or bounded read-only investigation is actually delegated. Follow its verified dispatch and non-overlapping-write rules.

Do not load or invoke imported skills at runtime. Their useful techniques are already incorporated below.

## 1. Select one active change and root

The user may supply a change name and may narrow the sync to an explicit subset of delta paths.

If no change name is supplied:

1. Use an unambiguous change already named in the conversation.
2. Otherwise auto-select the only active change, if exactly one exists.
3. Otherwise run `openspec list --json`. Its rows provide names, task counts/status, and recency, not artifact or delta fields. Run `openspec status --change "<candidate>" --json` with the sticky store flag for every candidate before filtering, and ask the user to choose among only those whose status reports concrete existing outputs for an artifact whose normalized `outputPath` begins `specs/`. Report unavailable candidate status rather than guessing delta presence. If only names/progress are shown and no delta filter is used, avoid the extra calls.

Announce `Using change: <name>` and state that supplying another change name overrides the selection. Do not emit a slash-command example.

If the user named a registered store, or the work is known to live in one, run `openspec store list --json`, resolve its registered id, and use `--store "<id>"` on every store-aware command in this action. The selection is sticky. The commands used here that accept it are `list`, `status`, `instructions`, and `validate`; `store list` itself does not take it. Without a store, commands resolve the nearest local OpenSpec root.

Run:

```bash
openspec status --change "<name>" --json [--store "<id>"]
```

The brackets show an optional flag; do not pass literal brackets. Treat non-zero exit or invalid JSON as a stop condition and report it.

Parse the returned `planningHome.root` and `artifactPaths.specs.existingOutputPaths`. Main specs are rooted at `<planningHome.root>/openspec/specs/`; never replace that with a guessed repository path. A selected store's planning home may be outside the caller's checkout.

## 2. Freeze the eligible delta set

`artifactPaths.specs.existingOutputPaths` is the only source of eligible delta files. Do not scan a familiar change directory, infer paths from another artifact, or reconstruct expected outputs.

- If the `specs` entry is missing or `existingOutputPaths` is empty, report that there are no delta specs to sync and stop before fetching artifact instructions or writing a main spec.
- By default, select every complete path value in `existingOutputPaths`.
- A caller may instead supply an explicit list of complete entries from `existingOutputPaths`. Copy and compare those absolute values verbatim. For example, the caller may select the complete entry ending in `/specs/billing/invoices/spec.md`.
- If any requested entry is not an exact member of `existingOutputPaths`, report it and stop; never silently drop it.
- If the caller's explicit list is empty, report that there is nothing to sync and stop without writing.
- Freeze this selected list for the entire action. Never widen it back to all existing outputs. Unselected delta files and their corresponding main specs remain untouched.

For each selected delta, derive `<capability-path>` from its complete path beneath the change's `specs/` directory, preserving all nested segments. Examples include `user-auth` and `identity/user-auth`. Resolve its main file only as `<planningHome.root>/openspec/specs/<capability-path>/spec.md`.

## 3. Obtain one immutable specs-rule snapshot

Do this before the first main-spec write:

- If an inline archive caller supplied a valid, current response from `openspec instructions specs --change "<name>" --json` for the same change and selected root, reuse it and do not fetch again.
- Otherwise run that command once, adding the sticky `--store "<id>"` only when a store was selected.
- If the command exits non-zero or its output is not valid artifact-instruction JSON for the selected change's `specs` artifact, report the error and stop before any main-spec write. Do not reinterpret failure as an absent ruleset.
- A valid response may omit `rules`; that means no artifact-specific rules are configured and the semantic merge continues.

Freeze the returned `rules` array for this action. Rules constrain only the content and form of main specs produced by the selected merge. They cannot alter the selected root, eligible delta paths, CLI checks, or action boundary. Do not copy `rules`, `context`, `instruction`, `template`, or other instruction-envelope text into a main spec or the summary. The delta-producing instruction and template do not replace the main-spec format.

## 4. Read and model each selected merge

Before changing a capability, read its complete delta and its current main spec when the latter exists. Model requirements by exact requirement heading, retain their existing order, and distinguish requirement body, scenarios, and fenced examples. Do not copy a delta file over a main spec.

Delta specs can contain these operations:

- `## ADDED Requirements`
- `## MODIFIED Requirements`
- `## REMOVED Requirements`
- `## RENAMED Requirements`, using `FROM:` and `TO:`

A new-capability delta may also begin with `## Purpose`. REMOVED blocks can carry `Reason` and `Migration` intent; those fields explain the removal and are not main-spec requirement content.

Before writing, compare the current and intended behavioral contracts. Detect accidental weakening or widening, including:

- loss of an unmentioned guarantee, scenario, error condition, permission, constraint, or interoperability behavior;
- acceptance of inputs, actors, states, or outcomes not authorized by the delta;
- stronger restrictions or new public behavior not expressed by the delta;
- vocabulary drift that changes the identity of a domain concept or requirement;
- an apparent scenario deletion hidden inside a partial MODIFIED block.

An explicit delta may intentionally change public behavior. The check prevents accidental change; it does not preserve behavior the delta clearly removes or modifies. If the intended contract still has a material ambiguity affecting behavior, compatibility, security, architecture, acceptance criteria, destructive migration, interoperability, or a major performance/resource tradeoff, present the concrete ambiguity and consequences and ask the user. Make a safe, reversible assumption only for immaterial gaps and record it.

## 5. Apply semantic operations

Apply each operation idempotently and preserve everything the selected deltas do not mention.

### ADDED

- If the requirement is absent from the main spec, add the complete requirement block under the single `## Requirements` section.
- If a requirement with that heading already exists, update it to the delta's intended content as an implicit MODIFIED operation; do not duplicate it.

### MODIFIED

- Find the matching main requirement.
- Apply the complete updated body and every scenario that the delta changes or adds.
- A MODIFIED block represents the whole surviving requirement. Preserve main scenarios and content not mentioned by the delta; do not let a partial block silently delete them.
- Changes may alter the requirement description, alter existing scenarios, or add scenarios. Maintain unrelated requirement order and content.
- If no matching main requirement exists, stop that capability and report the contradiction rather than silently treating MODIFIED as ADDED.

### REMOVED

- Remove the entire matching requirement block, including its scenarios and fenced examples.
- If the named requirement does not exist, make no change for that operation; idempotent re-runs must not invent work.
- Do not copy delta-only Reason or Migration text into the main spec.

If removals performed in this run would leave no requirement blocks, delete the entire main `spec.md` and remove its capability directory only once that directory is empty, and only when all of these conditions hold:

1. Removing requirements in this run left no requirement blocks.
2. The remaining file is well formed and still contains `## Purpose`.
3. The main spec was not already empty before this sync; if this run removed nothing, change nothing.
4. Every other nonblank line is accounted for as the title, Purpose, Requirements header, or a canonical requirement statement, scenario, or fenced example. Any other section blocks retirement.
5. The change's `.openspec.yaml` declares `retire_capabilities: true`.
6. The real `spec.md` path resolves inside the real planning-home specs root. Do not follow a capability-directory symlink to delete an external file.

If any condition fails, do not modify that capability. Stop its sync, name every blocking condition, and tell the user how to resolve it. Never write or leave an empty `## Requirements` section. If only `retire_capabilities: true` is missing, say so explicitly. Deletion also removes the capability's Purpose, so name that Purpose in the retirement report. Give a pasteable `git checkout` recovery command only when the deleted spec lived in the caller's checkout; otherwise give checkout-scoped recovery guidance.

### RENAMED

- Find the requirement named by `FROM:` and change only its heading to the `TO:` name, preserving its body, scenarios, examples, and position unless another explicit operation changes them.
- If `FROM:` is absent or `TO:` collides with a different existing requirement, stop that capability and report the contradiction rather than guessing.

### Purpose

- When a main spec already exists, its `## Purpose` is authoritative. Ignore a Purpose supplied by the delta and leave the main Purpose unchanged.
- When creating a new main spec, copy the delta's `## Purpose` body verbatim when present. Otherwise write a brief `TBD` Purpose placeholder and call it out in the final summary.
- Create a new main spec only for a genuinely new capability with ADDED requirements. A missing main spec paired only with MODIFIED, REMOVED, or RENAMED operations is a contradiction to report, not permission to fabricate a contract.

## 6. Preserve main-spec form

Every resulting main spec uses this shape:

```markdown
# <capability> Specification

## Purpose
Short description of what this capability does and why it exists.

## Requirements

### Requirement: New Feature
The system SHALL do something observable.

#### Scenario: Basic case
- **WHEN** an event occurs
- **THEN** an observable outcome follows
```

Main specs must never retain `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, or `## RENAMED Requirements`. Every requirement belongs beneath one `## Requirements` heading. Keep requirements behavioral, testable, precise, and implementation-independent. Preserve project terminology and include relevant error, permission, integration, and edge behavior when the delta expresses it; do not invent speculative requirements.

Show material changes as work proceeds. Keep writes limited to the selected capabilities' eligible main paths, plus an empty retired capability directory when its guarded removal is authorized. Do not edit delta files.

## 7. Validate and report

After all selected merges, run fresh validation against the resolved root:

```bash
openspec validate --specs [--store "<id>"]
```

Use only the sticky `--store` flag when applicable; do not invent a planning-root or schema flag. Read the complete result and exit status. If validation fails, report the issues and do not claim the sync succeeded. Do not mask failures with narrowed validation, suppressed output, skips, or weaker assertions.

On success, report:

- the selected change and exact delta subset used;
- each capability created, updated, or retired;
- requirements added, modified, removed, and renamed;
- every new main spec still carrying a TBD Purpose placeholder;
- for each retired capability, the deleted `spec.md`, its Purpose, and appropriate recovery guidance;
- the fresh validation command and material result;
- any assumptions, skipped deltas, limitations, or unresolved findings.

State that main specs are updated and the change remains active. Do not archive it or start another OpenSpec action.
