# Test plan for the future product skills

## Evidence

Run each behavioral case in a clean repository fixture and record:

- case ID, exact prompt, Codex/model/reasoning version, and skill inventory;
- initial path inventory and relevant contents;
- transcript, final path inventory, and version-control diff;
- persisted artifacts and console output;
- `pass`, `fail`, or `invalid`, preserving infrastructure failures.

An action that should write passes only when both the persisted files and
console response match the contract. Compare moved slice bytes before and after
`archive`.

## Structural validation

For both future packages:

1. Run the repository's current Codex skill validator:

   ```text
   .codex/skills/codex-skill-creator/scripts/quick_validate.py release/.codex/skills/product-definition
   .codex/skills/codex-skill-creator/scripts/quick_validate.py release/.codex/skills/product-delivery
   ```

2. Assert the package inventory exactly matches
   [`skill-contracts.md`](skill-contracts.md#package-layout), every local link
   resolves, `SKILL.md` is concise, and the package contains no script,
   custom-agent declaration, README, generated helper, or unused directory.
3. Assert each frontmatter `name` matches its directory and each exact
   description limits selection to explicit invocation.
4. Assert each `agents/openai.yaml` matches the documented interface, has a
   25–64 character short description, includes the exact skill token in its
   default prompt, and sets Boolean
   `policy.allow_implicit_invocation: false`.
5. Assert neither package contains model selection, reasoning selection,
   dispatch, delegation, routing guards, or subagent instructions. Run tests
   with GPT-5.6 Sol at high reasoning and repeat baseline synthesis at xhigh;
   these are harness settings only.
6. Assert exact templates live with their emitting skill and no passive shared
   package exists.

## Static repository audits

Scoped inventory and text checks must establish:

- `dev/greenfield/` contains only `README.md`, `skill-contracts.md`,
  `artifact-templates.md`, and `test-plan.md`;
- the only public product actions are `discover`, `baseline`, `roadmap`,
  `slice`, and `archive`;
- `init`, `interview`, `synthesize`, `review`, `approve`,
  `resynthesize`, and `status` are not accepted actions;
- no `.workflow/`, state YAML, pending-delivery file, receipt, phase,
  condition, review metadata, baseline lifecycle status, content hash,
  delivery ledger, or completion artifact is declared;
- no product router, agent TOML, child guard, model route table, script, or
  mandatory delegation appears;
- the product bundle has the exact discovery and baseline split, identifier
  families, requirement ownership, traceability, and delivery layout from
  `artifact-templates.md`;
- the manifest contains only schema version, product identity, timestamps,
  artifact inventory, and requirement index;
- roadmap coverage is changed only by first roadmap creation and slice
  creation, and is explicitly described as optimistic planning;
- the normative OpenSpec proposal handoff has one owner and the active-slice
  template embeds one rendered copy;
- no product action promises application-code or `openspec/**` writes;
- all action responses use the common console order and their required
  action-specific section; and
- deferred simplifications remain documented as future options, not current
  behavior.

## Description-boundary tests

Explicit invocations for all five actions must be eligible. Missing actions,
unknown actions, and misspelled skill names write nothing.

Prompts without an exact skill token are near misses:

| Case | Prompt | Expected behavior |
|---|---|---|
| `DESC-DEF-001` | “Interview me about a greenfield app.” | Do not select product definition |
| `DESC-DEF-002` | “Turn these notes into a product baseline.” | Do not select product definition |
| `DESC-DEF-003` | “Review these requirements for contradictions.” | Do not select either product skill |
| `DESC-DEL-001` | “Break this feature into vertical slices.” | Do not select product delivery |
| `DESC-DEL-002` | “Propose and implement the next OpenSpec change.” | Use the applicable external OpenSpec workflow |
| `DESC-DEL-003` | “Archive this completed OpenSpec change.” | Use the external OpenSpec archive action |

Use a documented host selection signal when available. Record activation as
`unknown` when the host exposes no such signal; grade output behavior
separately.

## Forward definition cases

### `DEF-001` — First discovery

Invoke `$product-definition discover parcel-tracker` in a genuinely empty
repository containing a local OpenSpec configuration. Expect exactly four
discovery files, no baseline or delivery file, one three-to-five-question
breadth-first round, `Discover: needs-input`, and the next invocation
`$product-definition discover`.

Pair it with fixtures containing durable code, canonical specs, active or
archived OpenSpec history, another product bundle, no local OpenSpec
configuration, and ambiguous non-disposable code. Each must be `blocked` with
zero writes and enumerated repository-relative evidence.

### `DEF-002` — Continue discovery

Invoke `discover` with complete answers to the latest unanswered round.
Expect the verbatim response, valid outcome IDs, updated discovery artifacts,
and either one new small cross-area round or baseline readiness. Verify that
dependent questions wait, “I don't know” receives an explicit treatment, and
only the latest unanswered round is mutable.

Invoke again without answers while a round is incomplete. Expect the same
questions, no added round, and zero writes. Verify that no separate pending or
state artifact appears.

### `DEF-003` — Baseline creation

From discovery containing explicit facts, decisions, assumptions, unknowns,
exclusions, and no fog, invoke `$product-definition baseline`. Expect every
baseline artifact, unique active requirements with one owner, source-ID
traceability, a complete sorted manifest, a passing in-invocation self-review,
exact counts, and no review artifact.

Pair with fog, an incomplete interview round, an untreated unknown, and an
unresolved contradiction. Expect `needs-input` or `blocked`, no invented
product behavior, and no partial replacement of an existing baseline.

### `DEF-004` — Baseline refresh and repair

Change persisted discovery before delivery begins, then invoke `baseline`
again. Expect stable IDs for unchanged obligations, new IDs above every active
or retired ID, retired index entries for removed obligations, preserved
`created_at`, a later `updated_at`, and automatic repair of detectable
template, terminology, traceability, or duplicate defects before the final
write.

### `DEF-005` — Definition stop after delivery starts

Create `delivery/roadmap.md`, then invoke both definition actions. Each must
return `blocked`, change no file, and point to the applicable delivery action.
There is no baseline refresh or alternate baseline after this boundary.

## Forward delivery cases

### `DEL-001` — Roadmap writes immediately

Invoke `$product-delivery roadmap` from a complete baseline. Expect the final
roadmap in the first invocation, all active requirements initialized to
`NOT DELIVERED`, unnumbered candidates, a walking skeleton first when
coherent, candidate output in the console, and no intermediate product file.
The roadmap's presence is the only evidence that the baseline was accepted.

Invoke again after delivery records exist. Expect candidate revisions to write
immediately while every coverage value and existing slice record remains
unchanged.

### `DEL-002` — Slice gates

Verify zero writes when there is one canonical active product slice, more than
one canonical active product slice, or any direct active OpenSpec change.
Noncanonical delivery files do not count. Active OpenSpec change contents are
not read.

With full declared coverage, expect `Slice: done`, no writes,
`Coverage:` followed by `- none`, `Proposal:` followed by `none`, and
`Next:` followed by `Delivery complete.`.

### `DEL-003` — Canonical slice and bounded reads

Verify the next number is one above the greatest canonical active or archived
product slice number, accepts `001` through `999`, and rejects overflow.
Verify slug normalization, exact active/archive OpenSpec name collision rules,
and no invented suffix.

Assert the read budget: roadmap first; three baseline overview files; candidate
requirement blocks; five newest archived product slices plus bounded outcomes
from older ones; indexed, implicated canonical specs and archived changes; and
candidate-scope code and tests. Wider reads require a cited dependency.

### `DEL-004` — Slice writes immediately

Invoke `slice` with eligible partial and uncovered requirements. In the same
invocation expect:

- one canonical active slice with one vertical outcome and explicit boundaries;
- only eligible requirements, each marked `partial` or `complete`;
- immediate roadmap updates retaining prior contributing slice names;
- the exact rendered handoff persisted once and printed once;
- the `Coverage` and `Proposal` console sections; and
- no application-code or OpenSpec mutation.

There is no persisted or console-only staging step. If no coherent slice
exists, expect `needs-input`, zero writes, and
`$product-delivery roadmap`.

### `DEL-005` — Archive refusal

With one active product slice and no direct OpenSpec archive basename ending in
`-<slice-name>`, expect `Archive: blocked`, zero writes, exact source and
destination output, and the external workflow step required before
`$product-delivery archive`. Near matches do not authorize the move.

Also reject no active slice, multiple active slices, and an existing product
archive destination without overwriting anything.

### `DEL-006` — Archive unchanged

Provide one or more matching direct OpenSpec archive basenames, including
unreadable or conflicting archive contents. Expect no content inspection, an
unchanged move to the same filename under `delivery/archive/`, no roadmap
change, exact source/destination/match output, and:

- `$product-delivery slice` when uncovered or partial rows remain; or
- `Delivery complete.` when all rows declare delivered coverage.

## Console and mutation checks

For every action and each `done`, `needs-input`, and `blocked` branch:

- compare line order, headings, status vocabulary, `Changed` operations, and
  `Next` content with the exact console template;
- require `Questions`, `Counts`, `Candidates`, `Coverage` plus
  `Proposal`, or `Archive` for the applicable action;
- ensure every reported changed path exists in the diff and every in-scope
  diff path is reported;
- ensure a no-write result says `- none`; and
- reject any response that asks the user to authorize a planned write.

Before and after each mutating case, compare all application files and:

```text
release/.codex/skills/openspec-*/**
release/.codex/agents/openspec-*.toml
release/openspec/config.yaml
openspec/**
```

Any product-skill change in those paths fails acceptance.
