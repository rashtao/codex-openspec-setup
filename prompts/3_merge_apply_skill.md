Merge the `openspec-plus-apply` skill into `openspec-apply-change`

Both skills run in the same agent context, so splitting them buys no context isolation
and costs a duplicated implementation loop, conflicting orchestration directives, a double
preflight, and a fragile hand-off. Merge them into one skill under
`.codex/skills/openspec-apply-change/`.

This setup is Codex CLI only. Use `update_plan`. Do not commit.

## Rules

- **Preserve the exact combined behavior** of today's `openspec-apply-change` →
  `openspec-plus-apply` chain. Add, remove, relax, or strengthen nothing: no rule,
  invariant, gate, review order, failure cap, model routing, or report field.
- **Keep wording verbatim** from the two sources. Rewrite only what the merge forces:
  section order, cross-skill references that become internal, and exact duplicates.
- Apply the minimal changes needed.
- Do not touch the workflow logic of any other skill — only its references.

## Steps

1. **Read** both `SKILL.md` files completely, plus every other file in
   `.codex/skills/openspec-plus-apply/`. List each distinct rule in both, marking
   duplicates; you'll need this for step 6.

2. **Move** every non-`SKILL.md` file from `.codex/skills/openspec-plus-apply/` into
   `.codex/skills/openspec-apply-change/`, keeping filenames. Do not inline them — they
   stay loaded just-in-time before dispatch. Update the merged skill's description of how
   they are resolved so it works from the new location.

3. **Write the merged `.codex/skills/openspec-apply-change/SKILL.md`**, keeping `name:
   openspec-apply-change` and extending its `description` to also cover what
   `openspec-plus-apply`'s described, reusing both originals' wording. Order:

   - intro from `openspec-apply-change`, plus a short note that this skill now owns the
     full apply workflow and any legacy `openspec-plus-apply` skill must be ignored;
   - `openspec-plus-apply`'s invariants verbatim, as the single source of truth, plus any
     `openspec-apply-change` guardrail not already covered there;
   - **one** merged orchestration/routing section. Where the two prescribe the same thing
     differently (notably the `update_plan` shape), adopt `openspec-plus-apply`'s more
     specific version and drop the other — never keep both. Union every distinct rule on
     subagent lifecycle, worktree sharing, context protection, inline fallback, and model
     plus reasoning-effort routing per role; each appears exactly once;
   - the prompt-resource contract from `openspec-plus-apply`, paths updated;
   - **one** acquisition-and-preflight section merging `openspec-apply-change` steps 1–3
     with `openspec-plus-apply` Phase 0. Include exactly once: change/store selection and
     its announcement; every CLI call and parsed field; tracked-vs-untracked determination;
     blocked/all_done/ready handling; context, guidance, and reference precedence; reading
     all context files, project instructions, and build config; the pre-implementation
     display; and all of `openspec-plus-apply`'s preflight validation assertions, existing-
     work baseline, and gate-command discovery. Convert its "the vanilla skill already did
     X" phrasings into direct requirements on this workflow, changing as few words as
     possible. Never run a command or read a file twice;
   - `openspec-plus-apply` Phases 1–3 unchanged and authoritative;
   - one final user-facing report merging `openspec-plus-apply`'s Handoff with
     `openspec-apply-change` step 5, keeping both the success and paused field lists and the
     resume instruction. Address the user directly — there is no outer skill left.

   **Delete `openspec-apply-change`'s 7-step fallback loop** and the sentence mandating
   `openspec-plus-apply`: its only trigger was that skill being unloadable, now unreachable.
   First diff it against Phase 2 rule by rule; carry anything unique into Phase 2 verbatim.

   Replace every internal `openspec-plus-apply` reference with the owning phase. Leave
   references to `openspec-plus-tdd`, `openspec-plus-debug` (including the subagent path
   placeholders and unloadable-skill handling), and the escalation skills unchanged.
   Renumber phases consistently. Mark each major section's source with an HTML comment.

4. **Delete** `.codex/skills/openspec-plus-apply/` after accounting for every file in it.

5. **Update references.** In `openspec/config.yaml`, remove the top-level `context:` block
   mandating `openspec-plus-apply`; leave every `rules:` entry and the surrounding comments
   untouched. Then search the whole repo for `openspec-plus-apply` and for claims that apply
   delegates to a second skill — including all other `.codex/skills/*/SKILL.md`, `prompts/`,
   and `README.md` — and retarget each to `openspec-apply-change`, adjusting the surrounding
   sentence minimally. Verify no reference remains except the supersedes note.

6. **Self-review.** Using the step-1 inventory, confirm every source rule survives exactly
   once with equal force; no requirement is stated twice; no two orchestration shapes remain;
   every name, path, phase number, and placeholder resolves; frontmatter parses; sampled
   paragraphs are substantially verbatim; other skills differ only in retargeted references.
   Fix what you find and re-read the diff.

7. **Report** the merged section order, files moved, the deletion, the config change, every
   updated reference, each rule dropped as a duplicate and where it survives, any ambiguity
   and how you resolved it, and any problem. Recommend restarting Codex.