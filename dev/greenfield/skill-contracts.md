# Skill contracts

## Package layout

The future implementation adds only these two packages:

```text
release/.codex/skills/
  product-definition/
    SKILL.md
    agents/
      openai.yaml
    references/
      action-contract.md
    assets/
      artifact-templates.md
  product-delivery/
    SKILL.md
    agents/
      openai.yaml
    references/
      action-contract.md
    assets/
      artifact-templates.md
```

Each package owns the action contract and templates it emits. Do not add a
shared skill, custom agent declaration, script, router, generated helper,
package README, or workflow-control file.

The compact `SKILL.md` files act as indexes into selectively loaded references
and assets, following [OpenAI's progressive-disclosure
guidance](https://developers.openai.com/codex/skills) and the
[small, composable, user-controlled approach](https://github.com/mattpocock/skills).

Use GPT-5.6 Sol in Codex CLI. High reasoning is the normal setting; xhigh is
recommended when invoking `baseline`. These are user-selected runtime
settings, not package metadata or enforced routes.

## Exact selection contracts

`product-definition/SKILL.md` begins:

```yaml
---
name: product-definition
description: Explicit-only greenfield product discovery and first-release baseline maintenance. Use only when the user invokes $product-definition discover or $product-definition baseline. Never select it for ordinary brainstorming, requirements, planning, implementation, or OpenSpec work.
---
```

`product-delivery/SKILL.md` begins:

```yaml
---
name: product-delivery
description: Explicit-only roadmap, vertical-slice, and product-record archive workflow for a defined greenfield product. Use only when the user invokes $product-delivery roadmap, $product-delivery slice, or $product-delivery archive. Never select it for ordinary roadmapping, implementation, review, correction, or OpenSpec work.
---
```

Selection is enforced by `policy.allow_implicit_invocation: false`; the
frontmatter descriptions state the same boundary for clarity. No natural
language request without the exact skill token activates either package.

## Exact interface metadata

`product-definition/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Definition"
  short_description: "Discover and baseline a greenfield product."
  default_prompt: "Use $product-definition discover to begin defining this greenfield product."
policy:
  allow_implicit_invocation: false
```

`product-delivery/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Delivery"
  short_description: "Roadmap, slice, and archive product delivery."
  default_prompt: "Use $product-delivery roadmap to begin delivering this defined product."
policy:
  allow_implicit_invocation: false
```

Both short descriptions are between 25 and 64 characters. Metadata contains no
model, reasoning, dependency, or routing configuration.

## Compact `SKILL.md` bodies

After its frontmatter, `product-definition/SKILL.md` contains only this
operational index:

```markdown
# Product Definition

Maintain the first-release definition for one greenfield product.

Accept only:

- `$product-definition discover [product-id]`
- `$product-definition baseline`

Read [`action-contract.md`](references/action-contract.md) completely before
acting. Read the applicable section of
[`artifact-templates.md`](assets/artifact-templates.md) before writing.

Execute the named action directly. Stop every definition action when
`delivery/roadmap.md` exists. Write only the final allowed product artifacts,
then return the exact console envelope.
```

After its frontmatter, `product-delivery/SKILL.md` contains only this
operational index:

```markdown
# Product Delivery

Advance one accepted first-release baseline through explicit product records.

Accept only:

- `$product-delivery roadmap`
- `$product-delivery slice`
- `$product-delivery archive`

Read [`action-contract.md`](references/action-contract.md) completely before
acting. Read the applicable section of
[`artifact-templates.md`](assets/artifact-templates.md) before writing.

Execute the named action directly. Do not invoke OpenSpec. Write only the final
allowed product artifacts, then return the exact console envelope.
```

The future `references/action-contract.md` files contain only the applicable
rules below. The future `assets/artifact-templates.md` files contain the
corresponding definition or delivery sections of
[`artifact-templates.md`](artifact-templates.md). This keeps exact templates
out of `SKILL.md` and avoids a passive shared package.

## Common repository rules

- Resolve one repository root and only its local `openspec/` directory.
- Require `openspec/config.yaml` or `openspec/config.yml`.
- Accept at most one direct product bundle under `docs/product/`.
- Require a lowercase kebab-case product ID and keep all product writes below
  `docs/product/<product-id>/`.
- Reject unsupported `schema_version` values before writing.
- Keep persisted local paths repository-relative with `/` separators. Reject
  absolute paths, parent traversal, home shorthand, drive prefixes, `file:`
  URIs, and paths escaping through symlinks.
- Derive progress from artifact presence. For discovery, the latest interview
  round without a recorded response is the only incomplete round.
- Allocate `FACT-*`, `PDEC-*`, `ASM-*`, `UNK-*`, `FOG-*`, `OOS-*`,
  `SRC-*`, and `REQ-*` IDs with four digits. Scan persisted artifacts and
  indexes, allocate one above the greatest prior value, and never reuse an ID.
- Treat the accepted baseline and archived product slices as user-protected.
  The skills do not hash, lock, or repair them.
- Return one of `done`, `needs-input`, or `blocked` using the exact
  console forms in `artifact-templates.md`.
- A missing or unknown action prints the supported invocations and writes
  nothing. Never infer a replacement action.

## `$product-definition discover [product-id]`

### Inputs and gates

Use the optional ID when initializing. When one product bundle already exists,
infer its ID if omitted and require any supplied ID to match it. When no bundle
exists and no valid ID can be obtained from the invocation, ask for the ID and
write nothing.

Before initialization, inspect repository structure. Permit repository
metadata, development tooling, empty scaffolding, an explicitly disposable
prototype, and the installed OpenSpec distribution. Stop on evidence of:

- durable application behavior;
- canonical capability content under `openspec/specs/`;
- any active or archived OpenSpec delivery history;
- another product bundle under `docs/product/`; or
- an ambiguous artifact that cannot safely be classified as disposable.

Do not install OpenSpec, remove evidence, or convert a brownfield repository.
On every invocation, stop without mutation when
`docs/product/<product-id>/delivery/roadmap.md` exists.

### Behavior

When necessary, create the four discovery artifacts in the template. Do not
create baseline or delivery artifacts.

If the latest interview round is incomplete:

1. Treat substantive text supplied with the invocation as the answer to that
   round.
2. Record the answer verbatim in that round.
3. Classify its outcomes as facts, product decisions, assumptions, precise
   unknowns, fog, exclusions, and sources.
4. Update `map.md`, `decisions.md`, and `sources.md` in the same write.
5. Leave the round incomplete and repeat its questions when no substantive
   answer was supplied. Do not append another round.

After initialization or recording an answer, calculate the breadth-first
frontier across all twelve discovery areas. Ask three through five independent
questions when at least three are ready; otherwise ask every ready question.
Span different areas when possible, defer dependent questions, and include a
recommended answer only when evidence supports it. Append at most one new
incomplete round before returning.

When the user says “I don't know,” distinguish researchable facts, safe
assumptions, delivery-slice deferrals, future-change deferrals, release
exclusions, and fog. Research only material external facts, prefer primary
sources, record narrow claims in `sources.md`, and never decide a product
preference.

When no independent question remains, append nothing and report discovery
ready for `baseline`. Discovery completeness permits explicit unknowns and
exclusions; it does not require certainty.

### Completion and mutations

The action completes when initialization and any supplied answer are persisted,
the discovery map reflects the current evidence, and either one small question
round is present or no ready question remains.

It may create or update only:

```text
docs/product/<product-id>/discovery/map.md
docs/product/<product-id>/discovery/decisions.md
docs/product/<product-id>/discovery/sources.md
docs/product/<product-id>/discovery/interview-log.md
```

Use `needs-input` while questions await answers and `done` when the next
action is `$product-definition baseline`.

## `$product-definition baseline`

### Inputs and gates

Read all discovery artifacts. On refresh, also read the existing baseline to
preserve requirement identity and the manifest creation timestamp. Do not use
conversation-only product facts, application code, canonical OpenSpec specs,
or OpenSpec changes as definition evidence.

Stop without mutation when:

- the roadmap exists;
- a discovery round is incomplete;
- any `FOG-*` remains;
- an unknown lacks an explicit baseline treatment;
- discovery sources contradict one another without a user decision; or
- required discovery artifacts or references are inconsistent.

The user may create a baseline with `UNK-*` entries of any risk when their
treatment is explicit.

### Behavior

Create or refresh the complete baseline in one invocation:

1. Normalize terminology and first-release boundaries.
2. Identify product responsibility domains without treating them as code,
   deployment, service, team, or storage boundaries.
3. Separate domain and cross-domain requirements.
4. Preserve an existing `REQ-*` for the same obligation. Allocate a new ID
   above every active or retired requirement ID for a new obligation. Retain a
   removed ID as `retired` in the manifest requirement index.
5. Give every active requirement one owning location and complete source-ID
   traceability.
6. Render every baseline artifact before replacing the current set.
7. Review the rendered set for exact template shape, unique ownership,
   traceability, terminology, duplicates, contradictions, journey and domain
   coherence, explicit unknown treatment, and repository-relative paths.
8. Repair every issue supported by discovery evidence and repeat the review.
   If a repair requires a new product decision, leave the existing baseline
   unchanged and return `needs-input` with the precise gaps.
9. Write only the final self-reviewed set, removing obsolete baseline files
   that are not in the final artifact inventory. Do not create a separate
   review artifact.

Requirements remain comprehensive first-release obligations with high-level
acceptance signals. They do not contain implementation steps, detailed
OpenSpec scenarios, priorities, change IDs, or delivery status.

### Completion and mutations

The action completes only when all required baseline artifacts exist, the
manifest inventory and requirement index match them, every review check passes,
and the console reports requirement and unknown counts.

It may create, replace, or remove only files under
`docs/product/<product-id>/baseline/**`.
Successful completion points directly to `$product-delivery roadmap`.
`baseline` may be invoked again to refresh the definition until that roadmap
is first created.

## `$product-delivery roadmap`

### Inputs and gates

Require one complete, self-consistent baseline and no incomplete discovery
round. Read discovery and baseline artifacts in full. For a revision, also read
the existing roadmap and all canonical active and archived product slice
records needed to preserve declared coverage.

### Behavior

Create or revise `delivery/roadmap.md` immediately.

The first roadmap:

- contains every active `REQ-*` exactly once;
- initializes every coverage row to `NOT DELIVERED`;
- contains unnumbered candidate slices with an outcome, likely eligible
  requirements, and sequencing rationale; and
- prefers a walking skeleton first, or the highest-risk coherent end-to-end
  path when no walking skeleton exists.

A revision preserves every coverage value and replaces or reorders only
candidate slices. Candidate entries contain no readiness, execution,
dependency, blocker, expected-change, or completion fields. When a canonical
active product slice exists, its scope and declarations remain untouched.

The first successful write marks the current baseline as accepted for
delivery. It adds no acceptance metadata. The presence of the roadmap is the
entire boundary.

### Completion and mutations

The action completes when the roadmap matches the template, covers every active
requirement, preserves existing declarations, and reports its candidate
outcomes.

It may create `docs/product/<product-id>/delivery/` and create or replace only
`delivery/roadmap.md`. It does not change discovery, baseline, slice, archive,
OpenSpec, or code files. Successful completion points to
`$product-delivery slice`.

## `$product-delivery slice`

### Gates

Apply these checks before selecting scope or writing:

1. Require a valid roadmap and baseline.
2. Enumerate direct canonical product slice files under `delivery/`. Exactly
   one blocks the action until its external workflow and product archive are
   complete; more than one is an error.
3. Enumerate direct children of `openspec/changes/` other than `archive`.
   Any child is an active OpenSpec change and blocks the action. Do not read its
   contents.
4. If every roadmap row is `DELIVERED (...)`, report delivery complete and
   write nothing.

Canonical product slice filenames match:

```regex
^slice-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$
```

Noncanonical delivery files do not participate in active-slice detection or
number allocation.

### Read budget

1. Read the roadmap in full and use uncovered or partial rows plus candidate
   outcomes to establish the candidate requirement set.
2. Read `baseline/charter.md`, `baseline/domain-map.md`, and
   `baseline/glossary.md` in full, then the complete owning blocks for
   candidate requirements.
3. Enumerate all archived product slice names. Read the five highest-numbered
   slices in full; from older slices, read only the frontmatter name and first
   non-empty outcome line.
4. Enumerate canonical OpenSpec spec paths and capability headings, then read
   only bodies implicated by candidate requirements.
5. Enumerate archived OpenSpec change basenames and artifact paths, then read
   only bodies whose indexed scope intersects candidate requirements.
6. Enumerate code paths, then read only the candidate capability, its direct
   integration boundary, and tests describing that behavior.
7. Cite any wider read in planning context with the dependency that required
   it.

Do not read discovery artifacts or active OpenSpec change contents, and do not
default to whole-baseline, whole-spec-store, whole-archive, or whole-codebase
body reads.

### Behavior

Choose one coherent, independently demonstrable vertical outcome using only
`NOT DELIVERED` or `PARTIALLY DELIVERED (...)` requirements. If none is
coherent, write nothing and direct the user to revise the roadmap.

Allocate one above the highest canonical number in active and archived product
slice filenames. Accept only `001` through `999`. Derive the slug by
lowercasing the title, retaining ASCII letters and digits, replacing every run
of other characters with one hyphen, and trimming outer hyphens. Stop on an
empty slug or collision; do not invent a suffix.

Reject a proposed name when it equals an active OpenSpec basename or a direct
child of `openspec/changes/archive/` ends in
`-<proposed-canonical-name>`. Near matches do not collide.

Write the canonical active slice and roadmap update in the same invocation.
For each covered requirement:

- `partial` appends the new slice name to a partial declaration;
- `complete` changes the row to `DELIVERED (...)` and retains every prior
  contributing slice name before appending the new one.

Never duplicate a slice name. This immediate coverage update is a planning
declaration, not implementation evidence.

Persist exactly one fully rendered proposal handoff in the active slice and
print the same handoff in the console. Do not create an OpenSpec change.

### Completion and mutations

The action completes when exactly one new canonical active slice exists, its
eligible requirement declarations match the roadmap, the roadmap is updated,
and the complete proposal handoff is printed.

It may create one `delivery/slice-NNN-short-slug.md` and replace
`delivery/roadmap.md`. It writes nothing else. The next step is the external
OpenSpec workflow for the exact same slice name.

## `$product-delivery archive`

### Inputs and gates

Require exactly one canonical active product slice. Let its filename without
`.md` be `<slice-name>`. Enumerate only direct-child basenames under
`openspec/changes/archive/`.

At least one basename must end exactly in `-<slice-name>`. Zero matches block
the move. One or more matches authorize it; prefixes and archive contents are
irrelevant. Do not inspect tasks, implementation, verification, synchronized
specs, or archived change contents.

Require the destination
`delivery/archive/<same-canonical-filename>` to be absent. Never overwrite an
archived product slice.

### Behavior and completion

Move the active product slice to the destination without changing its bytes.
Do not change the roadmap or any OpenSpec artifact.

The action completes when the source is absent, the destination contains the
unchanged file, and the console names both paths and the matching OpenSpec
archive basename. If every roadmap row is now `DELIVERED (...)`, print
delivery completion; otherwise print `$product-delivery slice`.

## Mutation boundary

| Action | Allowed writes |
|---|---|
| `discover` | Four files under `discovery/` |
| `baseline` | Complete final set under `baseline/` |
| `roadmap` | `delivery/roadmap.md` |
| `slice` | One active slice and `delivery/roadmap.md` |
| `archive` | One unchanged move from `delivery/` to `delivery/archive/` |

No product action writes application code, `openspec/**`, accepted baseline
files, workflow-control artifacts, receipts, run outputs, or external messages.
Archived product slice contents are never edited; `archive` may create only
its unchanged destination through the documented move. No action invokes
another product or OpenSpec skill. The user performs every external OpenSpec
step explicitly.
