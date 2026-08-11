---
name: openspec-onboard
description: Guide a first-time or learning user through a complete OpenSpec change on a small real codebase task, with explanations, current teaching pauses, live artifact creation, implementation, and archive. Use when the user asks for onboarding, a tutorial, a guided tour, or help learning the full OpenSpec workflow by doing real work.
---

# OpenSpec guided onboarding

Teach the user the current OpenSpec workflow by completing one small, real change in their codebase. Explain each stage briefly, do the real work, and preserve the marked pauses. This action is intentionally more interactive than ordinary OpenSpec actions; its teaching pauses do not become gates in any other action.

## Runtime routing

If the current task prompt contains `ROUTED_ACTION=openspec-onboard`, execute this installed skill directly and never route `openspec-onboard` again. Otherwise call:

```text
spawn_agent({
  task_name: "openspec_onboard",
  message: "ROUTED_ACTION=openspec-onboard. Execute the latest user request directly. Read .codex/skills/openspec-onboard/SKILL.md and follow it. Never route openspec-onboard again.",
  fork_turns: "1",
  model: "gpt-5.6-terra",
  reasoning_effort: "medium"
})
```

Then stop doing the action yourself. Wait for that child and relay its result. Do not add dispatch parameters or use any creation mechanism other than `spawn_agent`.

Use `update_plan` to track this multi-turn journey and `apply_patch` for file edits.

## Source of truth and store selection

OpenSpec CLI state controls the journey. Never infer the artifact graph, artifact state, paths, or archive target from familiar filenames. The current default schema commonly teaches proposal, specs, design, and tasks, but use only artifact ids, order, dependencies, instructions, and paths returned for this change.

If the user names a registered store, or the work is in one, run:

```bash
openspec store list --json
```

Resolve the registered store id and retain the matching `stores[].root` from this payload. Append `--store "<id>"` to every supported store-aware command used below: `new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, and `view`. Keep that store sticky for the whole journey and preserve it in command-provided follow-up hints. Do not pass it to commands that do not accept it. Without a selected store, work from the nearest local `openspec/` root.

Every unscoped store-aware command below is shorthand for the same command with the selected `--store "<id>"` appended.

## 1. Preflight and welcome

Check the CLI before doing anything else:

```bash
# Unix/macOS
openspec --version 2>&1 || echo "CLI_NOT_INSTALLED"
# Windows PowerShell
# if (Get-Command openspec -ErrorAction SilentlyContinue) { openspec --version } else { echo "CLI_NOT_INSTALLED" }
```

If it is not installed, explain that OpenSpec CLI must be installed first and stop gracefully. Do not begin a simulated tutorial.

Otherwise welcome the user and set expectations:

```text
## Welcome to OpenSpec!

I'll guide you through a complete change cycle using a small, real task in this codebase. We'll choose and explore the task, create a change, build the planning artifacts reported by OpenSpec, implement the work, and archive the finished record.

This usually takes about 15–20 minutes for a genuinely small task. Let's find one.
```

If the user asks only for a command reference or wants to skip the tutorial, give the quick reference under **Graceful exits** and stop.

## 2. Choose a real task

Inspect the repository for small, concrete improvement opportunities. Check repository guidance first, then look for:

- `TODO`, `FIXME`, `HACK`, or `XXX` comments in code;
- missing or swallowed error handling;
- behavior without corresponding tests;
- unsafe or overly broad types;
- stray debug logging or debugger statements;
- missing input validation;
- recent work that suggests a small unfinished edge.

Also inspect recent history when available:

```bash
# Unix/macOS
git log --oneline -10 2>/dev/null || echo "No git history"
# Windows PowerShell
# git log --oneline -10 2>$null; if ($LASTEXITCODE -ne 0) { echo "No git history" }
```

Present three or four specific candidates with location, realistic scope, and why each is suitable for a first cycle. Include an option for the user to propose something else, then **pause for their choice**. If no useful candidate exists, ask what small thing they have been meaning to add or fix.

If the chosen task is likely multi-day or spans a major feature, explain that a smaller vertical slice makes the full cycle easier to learn. Offer a concrete smaller slice, another candidate, or the option to continue anyway. This is a soft guardrail: respect an informed choice to continue.

## 3. Demonstrate exploration

Once a task is selected, say that exploration is where OpenSpec users investigate before committing to a direction. Spend only a minute or two reading the relevant code and tests. Summarize the current behavior, likely change surface, and material considerations. Draw a small ASCII diagram only when it clarifies the behavior.

Do not edit application code or planning artifacts during this demonstration.

Conclude with:

```text
This is the kind of thinking the openspec-explore action supports: inspecting and comparing before implementation. Now we can create a change to hold the work.
```

**Pause for acknowledgement before creating anything.** If the user stops here, there is no change to resume; exit without pressure.

## 4. Create the change

Explain that a change is the named container for the planning and implementation record. Derive a descriptive kebab-case name from the chosen task and tell the user the name before using it. Use the default schema by omitting `--schema` unless the user explicitly requests a schema. If they ask what schemas exist, resolve the authoritative root first. For a registered store, use its retained `stores[].root` or run `openspec context --json --store "<id>"` and use the returned `root.path`; then run `openspec schemas --json` with the working directory set to that exact root. For an unscoped local root, use `root.path` from `openspec context --json` when available. Never pass unsupported `--store` to `schemas`. Explain the returned options and let the user choose.

Create the real change:

```bash
openspec new change "<name>"
```

Add `--schema "<schema>"` only when the user chose a non-default schema. If the name is invalid, obtain a valid kebab-case name. If it already exists, do not overwrite it: ask whether to resume that change or use a new name.

Then obtain live state:

```bash
openspec status --change "<name>" --json
```

Use `planningHome`, `changeRoot`, `artifactPaths`, the schema name, artifact states, and `nextSteps` exactly as returned. Show the real `changeRoot` and current artifact sequence. Do not claim that proposal, design, specs, tasks, or any other output already exists unless live state says it does.

Explain that artifact state is one of `done`, `skipped`, `ready`, or `blocked`. A skipped artifact satisfies the graph without creating an output; a done artifact means its expected output exists, not that its content has passed semantic review.

## 5. Build the live planning artifacts

Repeat this sequence until status reports planning complete. Preserve declaration order when more than one artifact is ready, but never invent an artifact id or assume the default graph.

1. Run `openspec status --change "<name>" --json`.
2. Select the first artifact whose live status is `ready`.
3. Run:

   ```bash
   openspec instructions <artifact-id> --change "<name>" --json
   ```

4. Read every completed dependency file reported by the instructions, re-reading it from disk even if seen earlier. Honor `instruction`, `template`, `context`, artifact-keyed `rules`, `dependencies`, `references`, `warning`, `unlocks`, `skipped`, and `resolvedOutputPath`. Context and rules constrain the draft; do not copy them into the artifact.
5. Explain what this artifact contributes, draft it from the chosen real task and current repository evidence, and write only to the returned `resolvedOutputPath`. If that path is a pattern, choose concrete outputs exactly as the live instruction requires. The only companion write is the proposal-specific `skip_specs` transition below when its live instruction requires it.
6. Re-run status, show what became `done` or `skipped`, and explain what was unlocked.

If there is no ready artifact and planning is not complete, explain the reported blockers and stop until they are resolved. Never create a blocked or skipped artifact.

### Teaching the current default artifacts

Use the following explanations and acknowledgement points only when the live artifact id and instructions correspond to them.

#### Proposal

Explain that the proposal captures why the change matters and what changes at a high level. Research existing main specs before classifying capabilities. For the current spec-driven template, draft the returned structure with concise `Why`, `What Changes`, `Capabilities`, and `Impact` sections.

Capability paths are relative to `specs/`. Reuse the exact existing path for modified capabilities. For a new capability, use kebab-case for newly introduced path segments and follow the project's existing organization. List a modified capability only when requirements change, not for an implementation-only edit. If no behavior-level capability changes, follow the live instruction for explicitly opting out; do not invent requirements merely to satisfy validation.

Show the complete draft without saving it and ask, “Does this capture the intent? I can adjust it before we save.”

**Pause for approval or feedback.** Revise until approved, then write it to the live `resolvedOutputPath` and explain that this is the change's “why” record.

When this proposal's live instruction requires the explicit no-spec declaration, classify from repository evidence and the approved proposal. If whether any requirement-level behavior changes remains materially uncertain, ask the focused semantic question before saving metadata. For an approved proposal with zero new or modified capabilities and no spec-level behavior change, locate metadata using a CLI-returned `metadataPath` when available, otherwise resolve exactly `<changeRoot>/.openspec.yaml`; require the exact basename and prove the canonical target remains within canonical `changeRoot`. Parse the YAML mapping and use `apply_patch` to set only `skip_specs: true`, preserving every other field. Rerun status and require every artifact whose normalized `outputPath` begins `specs/` to report `skipped` with no existing output. If an approved proposal instead introduces capability-level requirements while metadata already sets `skip_specs: true`, make that inverse only after the approved semantics are explicit: remove the key or change only it to `false`, rerun status, and require those artifacts to re-enter a non-skipped live state. Stop and report any unsafe path, invalid metadata, conflicting spec output, or state mismatch. This is part of the current proposal teaching step and adds no phase, pause, or arbitrary metadata permission.

#### Specs

Explain that specs define observable behavior in precise, testable requirements and scenarios—not implementation structure. Create one concrete delta file per capability required by the approved proposal and live instructions.

For the current spec-driven format:

- use only the applicable operation sections: `ADDED`, `MODIFIED`, `REMOVED`, or `RENAMED Requirements`;
- write normative requirements with SHALL or MUST;
- give every requirement at least one `#### Scenario:` using WHEN/THEN and any needed AND clauses;
- for a new capability, include the requested `Purpose` of sufficient substance; do not add it to an existing-capability delta;
- for `MODIFIED`, copy the entire existing requirement block and edit the full updated behavior;
- for `REMOVED`, include the required reason and migration; for `RENAMED`, use the required FROM/TO format.

Show the actual spec and briefly point out how its scenarios can drive tests. Save only to the concrete path or paths resolved from the live output pattern.

#### Design

Explain that design captures how to implement the behavior, including consequential choices and trade-offs. Follow the returned template and instruction. Keep a small change's design proportionate, but include the sections the live template calls for; do not use a canned abbreviated document in place of them.

Resolve now any question that would change behavior, architecture, or task breakdown. Ask the user only for a material semantic decision. Truly deferrable unknowns may remain as open questions when the live instruction permits them.

Show the design before saving and briefly connect its decisions to the approved proposal and specs. Save it to the live `resolvedOutputPath`.

#### Tasks

Explain that the task artifact is the implementation checklist consumed by apply. Read all reported spec and design dependencies first. Resolve any design question that would change the implementation plan.

For the current spec-driven format, group tasks under numbered headings and use exactly `- [ ] X.Y ...` for every tracked task. Make tasks small, dependency-ordered, behaviorally coherent, and verifiable. Include relevant test or other evidence work rather than treating verification as an afterthought.

Show the complete draft and ask whether the user is ready to implement this plan.

**Pause for confirmation.** Incorporate feedback, save to the live `resolvedOutputPath`, re-run status, and explain that planning is complete only if the CLI reports it complete.

For any other live artifact, teach its purpose from its returned description and instruction. Do not force proposal/specs/design/tasks terminology onto another schema, and do not add extra approval gates.

## 6. Implement the real change

Explain that apply turns the planning record into code and that task completion is backed by observable evidence.

Get the live apply state:

```bash
openspec instructions apply --change "<name>" --json
```

Obey `state` exactly:

- `blocked`: report `missingArtifacts`, missing or empty tracking work, contradictions, or other stated blockers; do not implement around them.
- `all_done`: do not reimplement; proceed to archive.
- `ready`: read every path in every `contextFiles` entry, honor required project `context`, treat `operationGuidance` as advisory, and work through incomplete tasks.

For each coherent task or small vertical slice:

1. Announce the task in plain language.
2. Load `../openspec-shared/references/evidence-first.md` and apply its canonical evidence contract to this implementation work.
3. Implement the smallest coherent change, naturally connecting it to the relevant spec or design decision without narrating every line.
4. Run focused fresh verification. Never hide a failure by skipping, disabling, weakening, or narrowing away the relevant evidence.
5. Only after the canonical evidence contract supports completion, search every reported `contextFiles` path for the exact unchecked checkbox matching the live task description. Change it only when exactly one reported context file contains exactly one exact match. The CLI does not expose the configured tracking path; if the match is absent or ambiguous, pause safely without editing task state and report that limitation.
6. Re-run `openspec instructions apply --change "<name>" --json` and briefly report progress.

If implementation reveals a contradiction in a planning artifact, explain it and obtain the needed correction rather than silently coding around it. If diagnosis is required, load `../openspec-shared/references/debugging.md` and follow its diagnosis contract.

Continue until apply state is `all_done` or a real blocker remains. Keep narration light and remove temporary diagnostics before finishing.

## 7. Archive the change

After implementation tasks are complete, explain that archive preserves the change as decision history and may synchronize its delta specs into main specs. Then run the current tutorial command directly; do not insert a separate verification phase, sync-choice interaction, or pre-archive approval:

```bash
openspec archive "<name>" --yes
```

`--yes` answers the CLI confirmation prompts that cannot be answered from a tool call. Do not invent another flag or interaction.

Report the archive target exactly as the command returns it. Do not reconstruct it from the date or `planningHome`. Confirm that the code remains in the codebase and the planning record is preserved in history.

**Pause for the current post-archive teaching acknowledgement**, then continue to the recap.

## 8. Recap

End with a concise teaching recap tied to what actually happened:

1. explored a real problem;
2. created a named change;
3. produced each live planning artifact and explain its role;
4. implemented tracked work with evidence;
5. archived the decision record.

Mention that future work can use `openspec-propose` to create a fully planned change, `openspec-explore` for investigation, `openspec-apply-change` for implementation, `openspec-verify-change` for read-only assessment, and `openspec-archive-change` for archive. Present these as OpenSpec action names rather than CLI commands.

## Graceful exits

If the user pauses after a change exists, report its exact `changeRoot`, current artifact/task status, and the last completed step. Explain that later they can inspect it with:

```bash
openspec status --change "<name>" --json
```

They can then use `openspec-continue-change` for the next ready planning artifact or `openspec-apply-change` once apply is ready. Keep the selected store flag in the resume command. Never pressure the user to continue.

If the user asks only for a quick reference, provide:

- `openspec-propose`: create a change and all planning artifacts required for apply;
- `openspec-explore`: investigate without implementing;
- `openspec-apply-change`: implement from live apply instructions;
- `openspec-verify-change`: assess implementation against artifacts without editing;
- `openspec-archive-change`: resolve sync and archive one completed change;
- `openspec-new-change` and `openspec-continue-change`: create and advance a change one planning artifact at a time.

Then stop gracefully.

## Onboarding guardrails

- Follow explain → do → show → pause at the current teaching transitions: task choice, post-exploration acknowledgement, proposal approval when present, readiness to implement when a task artifact is present, and post-archive acknowledgement.
- Do not spread these onboarding pauses into other OpenSpec actions.
- Use a real task and real files; never simulate success.
- Do not skip the guided stages merely because the task is small, but let live schema state determine which planning artifacts exist.
- Ask additional questions only for material semantic decisions or a required user choice.
- Do not commit, publish, create branches or worktrees, submit external data, or start another OpenSpec action implicitly.
- Do not delegate guided teaching or implementation. The one-hop runtime routing above is the only onboarding dispatch.
- Completion means the real change was planned, implemented, archived through the current tutorial command, and recapped. Otherwise report the exact saved state and remaining work.
