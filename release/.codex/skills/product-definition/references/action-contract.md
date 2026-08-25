# Action contract

## Contents

- [Common repository rules](#common-repository-rules)
- [Discover](#product-definition-discover-product-id)
- [Baseline](#product-definition-baseline)
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

## Mutation boundary

| Action | Allowed writes |
|---|---|
| `discover` | Four files under `discovery/` |
| `baseline` | Complete final set under `baseline/` |

No definition action writes application code, `openspec/**`, accepted
baseline files after delivery begins, workflow-control artifacts, receipts,
run outputs, or external messages. No definition action invokes another
product or OpenSpec skill. The user performs every external OpenSpec step
explicitly.

