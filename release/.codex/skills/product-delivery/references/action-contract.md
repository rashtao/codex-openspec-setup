# Action contract

## Contents

- [Common repository rules](#common-repository-rules)
- [Roadmap](#product-delivery-roadmap)
- [Slice](#product-delivery-slice)
- [Archive](#product-delivery-archive)
- [Mutation boundary](#mutation-boundary)

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
| `roadmap` | `delivery/roadmap.md` |
| `slice` | One active slice and `delivery/roadmap.md` |
| `archive` | One unchanged move from `delivery/` to `delivery/archive/` |

No delivery action writes application code, `openspec/**`, discovery files,
accepted baseline files, workflow-control artifacts, receipts, run outputs, or
external messages. Archived product slice contents are never edited;
`archive` may create only its unchanged destination through the documented
move. No delivery action invokes another product or OpenSpec skill. The user
performs every external OpenSpec step explicitly.

