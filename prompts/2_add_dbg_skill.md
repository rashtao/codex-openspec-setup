# Task: add the `openspec-plus-debug` skill

Create one new skill, `.codex/skills/openspec-plus-debug/SKILL.md`, and wire it into the
existing implementation loop with minimal edits. This setup targets **Codex CLI only**.

## Source material

Adapt `systematic-debugging` from https://github.com/obra/superpowers
(including its bundled `root-cause-tracing`, `defense-in-depth`, and
`condition-based-waiting` techniques). Fetch and read it first.

Extract only the **mechanics**:
- the 4-phase root-cause process (gather evidence → isolate the failing boundary →
  form one hypothesis → fix the cause, then verify);
- boundary tracing: instrument each component boundary once to locate WHERE it breaks,
  then investigate only that component;
- condition-based waiting: wait on an observable condition, never a fixed delay, for
  timing/async/flaky failures;
- defense-in-depth: validate at each boundary rather than only at the outermost one;
- the escalation rule: after 3 failed fixes, stop and question the architecture.

Discard everything else: Claude Code idioms (`Skill` tool, `superpowers:` namespace
prefixes, `Task`-tool subagents, `.claude/skills` paths, slash commands), plus all
"Bottom Line / Key Principles / Real-World Impact" prose, slogans, and persuasion
rituals. Write compact declarative contracts — the readers are capable models.

## Before writing, read these completely

- `prompts/init.md` — the authoring standard for this repo. Obey it.
- `.codex/skills/openspec-plus-apply/SKILL.md` — especially the "Non-negotiable
  invariants", "Codex coordination contract", Phase 2 step 5, and Phase 3 step 4.
- `.codex/skills/openspec-plus-tdd/SKILL.md` — especially the RED validity taxonomy
  and the GREEN stage.
- `.codex/skills/openspec-plus-apply/implementer-prompt.md` — copy its structure,
  tone, placeholder style, and status vocabulary.

Match the house style of these files exactly: YAML frontmatter with only `name` and
`description`, a trigger-rich description, imperative prose, no emoji, no slogans.

## Required properties of the new skill

1. **Scope**: failure diagnosis only. It is invoked *reactively*, after a failed RED
   validation, a failed GREEN, a blocking review finding, or a failed slice/cumulative
   gate. It never replaces `openspec-plus-tdd`, and every fix it produces still flows
   through the TDD cycle (a cause-level fix still needs a valid RED).
2. **Routing**: state that this skill spawns no agents. It is read by the
   `gpt-5.6-terra` medium implementer/fixer (and by the orchestrator in inline mode).
   Keep the existing routing contract intact: `gpt-5.6-sol` high for
   orchestrator/planning/review, `gpt-5.6-terra` medium for implementer/fixer, always
   `fork_turns: "none"`.
3. **Boundaries** — carry over from the sibling skills verbatim in intent:
   - edit only the bounded affected paths; use `apply_patch`;
   - never reset/revert the worktree or absorb pre-existing user work;
   - never mark task checkboxes, edit planning artifacts, commit, or archive;
   - never mask a failure with skip/todo/disable markers, narrowed test filters,
     output suppression, or weakened assertions;
   - instrumentation added to gather evidence must be removed before returning.
4. **Hypothesis discipline**: one stated hypothesis at a time, with the evidence that
   supports it and the observation that would falsify it. No speculative multi-fix
   attempts. Fix the cause, not the symptom.
5. **Escalation**: on the third failed fix for the same failure, stop and return
   `BLOCKED: fundamental` with the evidence trail, and name the owning planning skill
   (`openspec-plus-design` / `-spec` / `-proposal`) rather than attempting a fourth fix.
   Align this explicitly with the existing three-failed-correction-cycle cap in
   `openspec-plus-apply` — do not introduce a second, competing counter.
6. **Return contract**: reuse the existing status vocabulary
   (`DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`) and require an
   evidence trail: symptom, boundary isolated, hypothesis, cause, fix, fresh
   verification command and result.
7. Keep it roughly the length of `openspec-plus-tdd/SKILL.md` or shorter. Include at
   most one compact worked example.

## Wiring edits (minimal — do not restructure these files)

- `openspec-plus-apply/SKILL.md`:
  - add one invariant requiring the implementer/fixer to read and follow
    `openspec-plus-debug` after any failed review or gate, and forbidding a second fix
    attempt for the same failure without a stated root-cause hypothesis and its evidence;
  - add one invariant making the third failed correction cycle an architectural
    escalation to the owning planning skill;
  - reference the skill at the slice-gate failure point (Phase 2 step 5) and the
    cumulative-gate failure point (Phase 3 step 4).
- `openspec-plus-tdd/SKILL.md`:
  - in the invalid-RED list, add timing/ordering nondeterminism and point to
    `openspec-plus-debug` for condition-based waiting;
  - in the GREEN stage, require following `openspec-plus-debug` after a second failed
    attempt on the same test.
- `openspec-plus-apply/implementer-prompt.md`: add a `{DEBUG_SKILL_PATH}` placeholder
  next to `{TDD_SKILL_PATH}`, to be **read on demand only after a failure** (not
  up front — this keeps it out of the orchestrator context).
- `openspec-plus-apply/SKILL.md` Phase 2 step 1: add `{DEBUG_SKILL_PATH}` to the list
  of placeholders the orchestrator must fill.
- `openspec-plus-apply/code-quality-reviewer-prompt.md`: add defense-in-depth
  (boundary validation) as one bullet in the existing review areas. Do not add a
  new section.

## Constraints

- Minimal diffs. Preserve the exact semantics of all existing skills; add no
  competing authority over TDD, review ordering, gates, or completion claims.
- No new counters, no duplicated iron laws, no changes to model routing.
- Do not install anything via `npx`/package managers and do not create
  `.claude/` directories.
- Do not commit.

## Before finishing

1. Re-read every edited file and confirm frontmatter validity, that all cross-skill
   references resolve to real paths, and that `{DEBUG_SKILL_PATH}` is both produced by
   the orchestrator and consumed by the implementer prompt.
2. Report: files created/changed, the exact invariants added, and any place where the
   new skill could be read as overriding `openspec-plus-tdd` or the review ordering
   (there should be none).
