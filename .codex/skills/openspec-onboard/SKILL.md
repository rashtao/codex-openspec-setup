---
name: openspec-onboard
description: "Teach OpenSpec by guiding the user through one complete, real change in their codebase: select and explore a small task, create schema-defined planning artifacts, implement with tests, verify, and archive. Use when the user asks for OpenSpec onboarding, a first guided workflow, or a narrated end-to-end example."
---

# Onboard with a Real OpenSpec Change

Guide the user through one complete OpenSpec cycle while doing useful work in the current codebase. Teach the reason for each phase, perform the real operation, and show its result. Keep narration concise and never substitute a simulated example for repository evidence.

## Operating Contract

- Use `update_plan` for the end-to-end workflow. Keep exactly one step `in_progress`, preserve the plan across user pauses, and update it after every phase.
- Explain a phase immediately before acting and summarize the concrete result immediately afterward. Pause only for a real choice, authorization, approval required by an owning skill, or a blocker.
- Prefer a small task that can traverse the full cycle without hiding the workflow in implementation complexity. Let the user choose a larger task after explaining the tradeoff.
- Respect repository instructions, the selected OpenSpec root, dirty worktree content, and existing user changes. Never commit.
- Never guess schema order, artifact names, file paths, validation commands, or archive paths. Use current CLI JSON.
- If the user stops, leave all work intact and provide the exact change name, current status, and a natural-language way to ask Codex to resume.

## Codex Agent Routing

Keep the main onboarding orchestrator on `gpt-5.6-sol` with `high` reasoning. Delegate only after the user explicitly requests or approves subagents and only for bounded work that the owning phase permits.

- Route planning, design, specification, research, and review agents to `gpt-5.6-sol` with `high` reasoning.
- Route implementer and fixer agents to `gpt-5.6-terra` with `medium` reasoning.
- With `spawn_agent`, set `fork_turns` to `"none"` or a positive number because model overrides cannot use a full-history fork. Supply the working directory, selected root/store, change name, exact inputs, allowed edit scope, acceptance criteria, checks, no-commit rule, and required return evidence.
- Use `send_message` for missing context or scope corrections and `wait_agent` to collect results. Inspect the shared worktree and check output before accepting a report.
- Do not parallelize dependent tasks or tasks that can touch the same files. If delegation is not explicitly authorized, execute inline with the same gates.

The artifact, apply, verification, and archive skills below may impose stricter delegation rules. Their rules take precedence within their phase.

## 1. Preflight and Root Selection

Run `openspec --version`. If it is unavailable, report that the OpenSpec CLI is required and stop; do not invent installation instructions.

Resolve one planning root and retain it for the entire tutorial:

1. If the user names a registered store, run `openspec store list --json`, resolve the exact id, and add `--store <id>` to every store-aware command.
2. Otherwise run `openspec list --json`. Use its `root.path`; do not assume the current directory is the root.
3. If no root exists, explain that onboarding needs an initialized project and ask whether to initialize the current project for Codex. Only after approval, run:

   ```bash
   openspec init . --tools codex --no-animation
   ```

   Do not use `--force`. Re-run `openspec list --json` afterward and require a valid root.

Read `<root.path>/openspec/config.yaml` or `config.yml` when present. Treat `context`, artifact `rules`, and operation guidance as constraints for the owning phase, not content to copy into artifacts or narration. Read applicable repository instruction files before scanning or editing.

Also record:

```bash
git status --short
git log --oneline -10
```

A missing Git repository is not fatal. Existing changes belong to the user; do not overwrite or revert them.

Briefly tell the user the cycle ahead: choose a task, explore, create a change, build its schema-defined artifacts, implement, verify, and archive. Do not promise a duration.

## 2. Select a Small Real Task

If the user already supplied a task, investigate that task directly. Otherwise use `rg --files` and focused `rg` searches to find two to four evidence-backed candidates. Exclude generated, vendored, dependency, build, and VCS directories.

Useful signals include:

- a scoped TODO or FIXME;
- a testable validation or error-handling gap;
- a small function with missing scenario coverage;
- a debug artifact in production code;
- a clear inconsistency with a nearby established pattern.

Do not present speculative defects as facts. For each candidate, show its location, likely scope, why it is suitable for onboarding, and the evidence found. Ask one direct question: which candidate should the tutorial use, or what small task does the user prefer?

If the selection is broad, propose the smallest independently valuable slice. Explain that a larger choice will make the tutorial longer, then honor the user's decision.

## 3. Demonstrate Exploration

Follow `openspec-explore` for a short read-only investigation of the selected task:

- trace the relevant code and tests;
- identify the current behavior, desired outcome, constraints, and likely impact;
- use a diagram or table only when it materially clarifies the system;
- surface unknowns instead of inventing answers.

Summarize the result and propose a unique kebab-case change name. Before creating anything, ask the user to confirm both the task boundary and change name. This is the first intentional mutation checkpoint.

## 4. Create the Change

Run `openspec list --json` with the selected store flag, if any, and ensure the proposed name does not collide with an active change. If it collides, ask for a different name; do not reuse or delete the existing change.

After confirmation, run:

```bash
openspec new change "<name>" --json
openspec status --change "<name>" --json
```

Add `--store <id>` when applicable. Require zero exit status and valid JSON. Use the returned `planningHome`, `changeRoot`, `schemaName`, `artifactPaths`, `artifacts`, `actionContext`, and `nextSteps`. Never create directories or placeholder artifacts manually, and never show a hardcoded folder tree.

Explain that the change is the planning container and that its active schema determines which artifacts are required and in what order.

## 5. Build Artifacts in Schema Order

Repeat until every artifact required for apply is `done` or explicitly `skipped`:

1. Run `openspec status --change "<name>" --json` and select the next `ready` artifact according to the returned graph and `nextSteps`. If none is ready, report the blocking dependencies rather than forcing progress.
2. Run `openspec instructions <artifact-id> --change "<name>" --json`. Require valid JSON and obey its dependencies, template, instruction, rules, and path contract.
3. Load and follow the owning Codex skill before discussing or writing a standard artifact:
   - `proposal` → `openspec-plus-proposal`
   - `design` → `openspec-plus-design`
   - `specs` or specification artifacts → `openspec-plus-spec`
   - `tasks` → `openspec-plus-tasks`
4. For a custom artifact id, follow the CLI-provided instruction and template. Do not force it into a standard artifact shape.
5. Let the owning skill control discovery, direct user questions, approvals, writing, and review. During onboarding, add only a one-sentence explanation of that artifact's role.
6. Re-run status and show what advanced before moving on.

Use concrete paths returned by the CLI. Existing files come from `artifactPaths.<id>.existingOutputPaths`. A glob-valued `resolvedOutputPath` is a pattern, not a writable file; let the artifact instruction and owning skill derive each concrete output.

Do not skip an artifact because the change is small. Honor schema-declared `skipped` status, but never manufacture it. Do not use a fast-forward path unless the user explicitly asks to stop the guided artifact walkthrough.

When apply prerequisites are complete, validate the change without interactive prompts:

```bash
openspec validate "<name>" --type change --strict --json --no-interactive
```

If validation fails, return the issue to the owning artifact skill and revalidate. Do not begin implementation with invalid planning artifacts.

## 6. Implement with the Apply Workflow

Show the ready implementation scope from:

```bash
openspec instructions apply --change "<name>" --json
```

Ask the user directly whether to begin implementation. After confirmation, load and follow these skills in order:

1. `openspec-apply-change` for selection, context loading, status handling, and overall apply control;
2. `openspec-plus-apply` for the implementation loop and reviews;
3. `openspec-plus-tdd` before any test or production code is written.

Do not reproduce a weaker implementation loop in onboarding. Every applicable specification scenario must receive test coverage, production code must follow strict per-test RED-GREEN-REFACTOR, relevant checks must pass, and task checkboxes may be marked complete only after their owning gates pass.

Keep tutorial narration light: identify the current task, relate one important choice to the artifacts, and report the gate result. If implementation reveals a planning defect, stop and return to the applicable planning skill; never silently rewrite an artifact from the implementation phase.

## 7. Verify Before Archive

After apply reports all tasks complete, load and follow `openspec-verify-change`. Treat it as read-only review. Show the user its completeness, correctness, and coherence result.

If critical issues remain, do not archive. Route planning defects back to the relevant planning skill and implementation defects back through the apply/TDD workflow. Fixer agents, when explicitly authorized, use `gpt-5.6-terra` with `medium` reasoning; final compliance review uses `gpt-5.6-sol` with `high` reasoning.

Ask the user whether to proceed to archive only when verification has no unresolved critical issue.

## 8. Archive Safely

After explicit confirmation, load and follow `openspec-archive-change`. That skill owns:

- incomplete-artifact and task warnings;
- the explicit delta-spec sync, skip, or cancel decision;
- semantic sync verification and spec validation;
- the CLI archive command and collision handling;
- the exact archive path reported from JSON.

Do not call `openspec archive` directly from onboarding and do not infer the archive path. Archiving is a separate, potentially destructive transition, not an automatic consequence of implementation.

## 9. Recap

After a successful archive, summarize the actual cycle completed:

1. exploration clarified the task;
2. the change captured planning state;
3. schema-defined artifacts captured intent, requirements, design, and work where applicable;
4. apply implemented the tasks with tests and reviews;
5. verification checked implementation against artifacts;
6. archive handled spec synchronization and preserved the decision record.

Report the change name, schema, archived path, spec-sync outcome, implementation checks, and any warnings the user explicitly accepted.

Distinguish Codex skills from shell commands in the reference:

| Codex skill | Purpose |
|---|---|
| `openspec-explore` | Investigate without implementing |
| `openspec-propose` | Create a fully planned change |
| `openspec-apply-change` | Implement an existing change |
| `openspec-verify-change` | Review implementation against artifacts |
| `openspec-archive-change` | Resolve spec sync and archive safely |

| OpenSpec CLI command | Purpose |
|---|---|
| `openspec list --json` | Resolve the root and list active changes |
| `openspec status --change "<name>" --json` | Inspect schema and artifact state |
| `openspec instructions <artifact> --change "<name>" --json` | Obtain authoritative artifact guidance |
| `openspec validate "<name>" --type change --strict --json --no-interactive` | Validate the change |

## Graceful Pause or Reference-Only Request

If the user pauses, run status and report the selected root/store, change name, completed and next artifact or task, current validation state, and any uncommitted files changed during onboarding. Tell them to ask Codex to continue onboarding that exact change. Do not claim that merely rerunning a shell command will restore conversational approvals.

If the user wants only a reference, skip all mutations and show the two compact reference tables above. Ask whether they want to start a guided cycle; do not pressure them.
