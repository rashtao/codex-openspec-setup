# OpenSpec integration and fresh-context prompts

## Integration boundary

The product workflow coordinates external OpenSpec actions without modifying or
calling them:

| Product event | Fresh-session external action | Product workflow consequence |
|---|---|---|
| Active product slice created | `$openspec-propose` | Creates one same-named active OpenSpec change |
| Proposal complete | `$openspec-apply-change <slice-name>` | Implements external tasks and code |
| Apply complete | `$openspec-verify-change <slice-name>` | Produces the external behavioral result |
| Verification accepted | `$openspec-archive-change <slice-name>` | Synchronizes canonical specs and creates an OpenSpec archive |
| Same-name archive exists | `$product-delivery archive` | Moves the unchanged active product slice |

`$openspec-update-change <slice-name>` remains available through the external
workflow when planning needs revision. Existing files under
`release/.codex/skills/openspec-*`, matching external agents, and
`release/openspec/config.yaml` remain outside the product mutation boundary.

Product skills do not invoke bulk creation, bulk archival, fast-forward,
onboarding, registered-store, or separate synchronization workflows.

## Canonical slice identity

An active product slice is a direct child of `delivery/` named:

```text
slice-NNN-short-slug.md
```

Its external OpenSpec change name is the filename without `.md`. There is no
second identifier.

The next number is one greater than the highest canonical number visible among
active and archived direct-child product slice files. The title is lowercased,
ASCII letters and digits are retained, every run of other characters becomes
one hyphen, and outer hyphens are trimmed. The short slug should remain
readable; an empty slug or an identity collision stops instead of inventing a
suffix.

Noncanonical files in the delivery root do not participate in active-slice
detection or number allocation.

## Normative proposal prompt

Every active slice embeds exactly one prompt of this shape, with all
placeholders rendered before persistence:

```text
$openspec-propose

Create exactly one planning-only OpenSpec change for the greenfield product
delivery slice below. This is a fresh session; derive context from the named
repository artifacts and do not rely on prior conversation.

Required change name: slice-NNN-short-slug
Product bundle: docs/product/<product-id>
Active product slice:
docs/product/<product-id>/delivery/slice-NNN-short-slug.md

Read the entire active product slice, the current code, and the canonical
`openspec/specs/` needed to plan this outcome. Create exactly
`slice-NNN-short-slug` using the installed OpenSpec schema. Produce every
planning artifact required by that schema, including detailed behavioral
requirements, scenarios, design, and tasks. Preserve the slice's in-scope and
out-of-scope boundaries and keep it vertical and independently demonstrable.

Do not implement code, apply tasks, verify behavior, synchronize canonical
specs, archive the change, create another change, edit the frozen product
baseline, edit the product roadmap, or edit the active product slice. If the
required name cannot be used or the outcome cannot form one coherent change,
stop and report the evidence.

After the proposal is complete, continue the existing external OpenSpec
workflow for exactly `slice-NNN-short-slug`: apply, verify, and archive it in
separate appropriate sessions. Then invoke:
`$product-delivery archive`
```

This prompt is persisted inside the active slice rather than in a separate
packet or control artifact.

## What `slice` may read

Before selecting scope, `$product-delivery slice` reads:

- the complete roadmap;
- every frozen baseline artifact;
- every canonical direct-child archived product slice;
- canonical `openspec/specs/`;
- archived `openspec/changes/archive/` changes;
- current application code.

It does not read discovery. It lists active OpenSpec direct-child names only to
enforce the no-active-change gate and does not read pending change contents.
The selected requirements must currently be `NOT DELIVERED` or
`PARTIALLY DELIVERED (...)`.

## Active-change gate and collisions

Any direct child of `openspec/changes/` other than `archive` counts as an
active OpenSpec change and stops `slice`. Any one canonical product slice in
the delivery root also stops selection; multiple canonical active product
slices are an error.

Even after the general gate, the proposed name is explicitly rejected when it
equals an active OpenSpec basename or any direct child of the external OpenSpec
archive has a basename ending in `-<proposed-name>`. The archive prefix need
not have any particular form for collision detection.

## Product archive authorization

The archive invocation itself attests that the user has inspected
`delivery/archive/`. The product skill does not inspect that destination.

For active slice `slice-NNN-short-slug`, authorization requires at least one
direct-child basename under `openspec/changes/archive/` ending exactly in:

```text
-slice-NNN-short-slug
```

Zero matches produces:

```text
No archived OpenSpec change was found for `slice-NNN-short-slug`.
Complete and archive the OpenSpec change named `slice-NNN-short-slug`, then
retry `$product-delivery archive`.
```

One or many suffix matches authorize the move. The product skill does not
interpret a prefix or date, resolve ambiguity, inspect archive contents, check
an active twin, inspect implementation or tasks, repeat verification, or check
canonical spec synchronization. Those facts are within the user and external
OpenSpec trust boundary.

The active product slice then moves unchanged to the direct-child destination
with the same filename. The sole successful next-step output is:

```text
$product-delivery slice
```

## Read-only status packets

`$product-delivery status` prints the first applicable result:

```text
# roadmap missing
$product-delivery roadmap

# active product slice present
Finish the external OpenSpec workflow for `<slice-name>`.
$product-delivery archive

# uncovered or partial requirements remain
$product-delivery slice

# all requirements declare complete coverage
Delivery is complete.
```

It performs no external OpenSpec action and writes nothing.
