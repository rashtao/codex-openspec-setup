---
name: openspec-explore
description: Explore an idea, problem, architecture, or OpenSpec change without implementing it. Use when the user wants a thinking partner to investigate the codebase, clarify requirements, compare approaches, surface risks, or reason through a change before or during planning.
---

# Explore an OpenSpec Change

Act as a curious, grounded thinking partner. Follow useful threads rather than forcing a fixed workflow, and let conclusions emerge at the pace the evidence supports.

## Boundary

Exploration is read-only by default.

- Read files, search the repository, inspect history, and run non-mutating diagnostic commands.
- Do not write production code, tests, configuration, or other implementation files.
- Do not create or edit OpenSpec artifacts merely because a decision emerges. Offer to capture it and wait for explicit authorization.
- When the user explicitly asks to create, update, review, or refine an OpenSpec artifact, follow the applicable OpenSpec planning skill and its approval/review rules. Those skills own artifact-writing procedure; do not duplicate or bypass it here.
- If the user asks to implement or fix code, explain that implementation is outside explore mode and offer the appropriate proposal, update, or apply workflow.

## Ground the Conversation

Inspect only as much context as the question needs.

1. Resolve the OpenSpec root when project or change context matters.
   - If the user names a registered store, run `openspec store list --json`, resolve its id, and retain `--store <id>` on every store-aware follow-up command.
   - Otherwise run `openspec list --json`. Its `root.path` identifies the resolved project root.
   - If no OpenSpec root exists, continue with ordinary read-only exploration. Do not initialize OpenSpec unless the user asks.
2. Read `<root.path>/openspec/config.yaml` or `config.yml` when present. Treat `context` as project background. Apply `rules.<artifact-id>` only when that artifact becomes relevant; do not repeat configuration text to the user.
3. When a change is relevant, run:

   ```bash
   openspec status --change "<name>" --json
   ```

   With a store, add `--store <id>`. Use `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext` from the response instead of guessing paths or scope. Read existing artifacts only from `artifactPaths.<id>.existingOutputPaths`; never treat a glob-valued `resolvedOutputPath` as a concrete file.
4. Read relevant repository instructions and trace the actual code, tests, dependencies, and history before making codebase-specific claims.

If several changes could match, show a short list from `openspec list --json` and ask the user directly which one they mean. Do not silently select among plausible candidates.

## Explore Effectively

Choose techniques that fit the conversation:

- Clarify ambiguous goals, constraints, actors, and success conditions.
- Challenge assumptions and distinguish evidence from inference.
- Map existing architecture, integration points, ownership, and data flow.
- Compare credible options with context-specific tradeoffs.
- Surface risks, unknowns, migration concerns, and useful spikes.
- Recommend a direction when asked, including why it fits and what could change the recommendation.

Ask concise, natural questions rather than running an interview script. If an answer is required before useful progress is possible, ask it directly and stop. If the question is non-blocking, state the assumption and continue with read-only investigation.

Use `update_plan` only when a substantial investigation has three or more meaningful steps or parallel tracks. Keep exactly one step in progress and update it as evidence changes. Do not create a ceremonial plan for a short discussion.

Use a compact diagram, table, or timeline only when it makes relationships materially easier to understand. Prefer prose for simple conclusions.

## Optional Delegation

Delegate only when the user explicitly requests subagents or parallel agent work and there are bounded, independent read-only tracks. Otherwise explore directly.

Use this Codex-native contract:

1. Keep the main explorer/orchestrator on `gpt-5.6-sol` with `high` reasoning.
2. Launch planning, design, specification, research, or review agents with `spawn_agent`, explicitly selecting `gpt-5.6-sol` and `high` reasoning. Because model overrides are incompatible with a full-history fork, set `fork_turns` to `"none"` or to a positive number of recent turns and include every required input in the task. Give each agent:
   - one concrete question;
   - exact repository/change scope;
   - a read-only constraint;
   - authoritative inputs to inspect;
   - a concise evidence-backed deliverable.
3. Use `send_message` for relevant discoveries and `wait_agent` to collect results. Reconcile disagreements against source files before presenting a conclusion.
4. Route implementer and fixer agents to `gpt-5.6-terra` with `medium` reasoning. Never launch those agents from explore mode; use that route only after handing work to the appropriate implementation workflow.

Do not ask agents to edit the same artifact, repeat the same investigation, or make decisions that require the user's judgment.

## Capture Decisions Deliberately

When an insight becomes stable, identify the likely destination without assuming the schema:

- scope, motivation, or capability boundaries commonly belong in a proposal;
- architecture and technical choices commonly belong in a design;
- observable requirements and scenarios commonly belong in specifications;
- implementation work commonly belongs in tasks.

Confirm the actual artifact ids and build order from `openspec status --change "<name>" --json`. If the user wants to capture the insight, transition to the applicable planning skill:

- proposal: `openspec-plus-proposal`
- design: `openspec-plus-design`
- specifications: `openspec-plus-spec`
- tasks: `openspec-plus-tasks`
- cross-artifact revision of an existing change: `openspec-update-change`, plus every applicable artifact-specific skill

Before any artifact write, obtain its current template, dependencies, and rules through the owning workflow, normally with:

```bash
openspec instructions <artifact-id> --change "<name>" --json
```

Add `--store <id>` when applicable. Preserve the user's exploratory momentum: offer the transition once, then continue exploring if they decline.

## Finish Naturally

There is no mandatory output. When useful, end with a compact synthesis:

- what is now understood;
- the leading option and key tradeoff, if one emerged;
- unresolved questions or evidence gaps;
- the next planning or investigation step, if the user wants one.

Never imply that implementation or artifact changes occurred when the session remained read-only.
