---
name: product-definition
description: Explicit-only greenfield product discovery and first-release baseline maintenance. Use only when the user invokes $product-definition discover or $product-definition baseline. Never select it for ordinary brainstorming, requirements, planning, implementation, or OpenSpec work.
---

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
