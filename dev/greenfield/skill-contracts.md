# Skill contracts

## Future package layout

```text
release/.codex/skills/
  product-discovery/
    SKILL.md
  product-baseline/
    SKILL.md
  product-delivery/
    SKILL.md
  product-shared/
    SKILL.md
    README.md
    references/
      workflow-contract.md
      artifact-contracts.md
      openspec-integration.md
      discovery-and-baseline-validation.md
    assets/
      discovery/
      baseline/
      delivery/

release/.codex/agents/
  product-discovery.toml
  product-baseline.toml
  product-delivery.toml
```

`product-shared` is passive and has no agent or executable helpers. Empty
directories are omitted from the implementation.

## Exact frontmatter selection contracts

### `product-discovery`

```yaml
---
name: product-discovery
description: Explicit-only workflow for initializing and interviewing a genuinely greenfield first-release product. Use only when the user explicitly invokes $product-discovery with init, interview, or status. Never select it for an unqualified request to brainstorm, explore, gather requirements, or plan an OpenSpec change.
---
```

### `product-baseline`

```yaml
---
name: product-baseline
description: Explicit-only workflow for synthesizing, reviewing, approving, or inspecting an immutable first-usable-release product baseline from persisted discovery artifacts. Use only when the user explicitly invokes $product-baseline with synthesize, review, approve, or status. Never select it implicitly for ordinary requirements, documentation, or OpenSpec planning work.
---
```

### `product-delivery`

```yaml
---
name: product-delivery
description: Explicit-only forward delivery workflow for roadmapping a frozen greenfield product baseline, preparing one vertical slice, archiving its unchanged slice record after the matching external OpenSpec workflow, or reporting the next step. Use only when the user explicitly invokes $product-delivery with roadmap, slice, archive, or status. Never select it implicitly for ordinary OpenSpec proposal, implementation, verification, synchronization, or archive requests.
---
```

### `product-shared`

```yaml
---
name: product-shared
description: Passive support package containing product-workflow references, normative templates, assets, and a user-facing README. Never invoke it as a user-facing action.
---
```

Selection language belongs only in these descriptions. A natural-language
request without an explicit public product-skill invocation remains outside
the activation boundary.

## User-facing modes

### Discovery

```text
$product-discovery init <product-id>
$product-discovery interview
$product-discovery status
```

- `init` checks greenfield eligibility and creates discovery/control artifacts.
- `interview` asks one breadth-first round, or records the immediately pending
  response and recalculates the frontier.
- `status` is read-only and reports coverage, unknowns, blockers, and the next
  explicit invocation.
- A missing or unknown mode prints usage and performs no fallback action.

### Baseline

```text
$product-baseline synthesize
$product-baseline review
$product-baseline approve
$product-baseline status
```

- `synthesize` creates a draft baseline from persisted discovery artifacts only.
- `review` independently performs structural, schema, traceability, and
  coherence checks and writes the latest review receipt.
- `approve` requires an `approval-ready` receipt. Invoking it attests that the
  reviewed draft has not changed and freezes that draft.
- `status` is read-only.
- A missing or unknown mode prints usage and performs no fallback action.

### Delivery

```text
$product-delivery roadmap
$product-delivery slice
$product-delivery archive
$product-delivery status
```

- `roadmap` creates or revises coverage and unnumbered candidate slices. It
  always previews its change and waits for same-session confirmation.
- `slice` previews one canonical active slice and its roadmap update, waits for
  same-session confirmation, then persists both and prints one embedded
  `$openspec-propose` prompt.
- `archive` moves the one canonical active slice unchanged into
  `delivery/archive/` after the external archive-name check.
- `status` is read-only and prints exactly the next product step.
- A missing or unknown mode prints usage and performs no fallback action.

There are no product delivery modes for applying, verifying, reconciling,
closing, repairing, or altering completed work.

## Routing contract

Each user-facing skill makes exactly one child dispatch and performs no action
in the parent:

```text
spawn_agent({
  task_name: "<product_action>",
  message: """
ROUTED_ACTION=<skill-name>

Execute exactly this product-skill action.
Read `.codex/skills/<skill-name>/SKILL.md` before acting.
Never route this action again and never spawn another agent.

MODE: <mode>
USER_REQUEST:
<verbatim current user request>

WORKING_DIRECTORY: repository root
PRODUCT_ROOT: <repository-relative path or unresolved>

Return the result required by the action contract.
""",
  fork_turns: "none",
  model: "gpt-5.6-sol",
  reasoning_effort: "high | xhigh"
})
```

The packet is complete and never tells the child to recover facts from parent
history. An immediate response to a pending discovery question or a pending
same-session delivery confirmation may continue that action. A new session
must repeat the explicit invocation and cannot confirm an earlier preview.

## Agent settings and exact files

| Agent | Model | Effort | Sandbox |
|---|---|---|---|
| `product-discovery` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `product-baseline` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `product-delivery` | `gpt-5.6-sol` | `high` | `workspace-write` |

`release/.codex/agents/product-discovery.toml`:

```toml
name = "product-discovery"
description = "Routed greenfield product discovery role for explicit initialization, breadth-first interviews, and persisted knowns and unknowns."
developer_instructions = """
ROUTED_ACTION=product-discovery
Execute only the mode in the complete routing packet. Read .codex/skills/product-discovery/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

`release/.codex/agents/product-baseline.toml`:

```toml
name = "product-baseline"
description = "Routed product baseline role for fresh-context synthesis, independent review, and one-way approval of a first-release baseline."
developer_instructions = """
ROUTED_ACTION=product-baseline
Execute only the mode in the complete routing packet. Read .codex/skills/product-baseline/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
sandbox_mode = "workspace-write"
```

`release/.codex/agents/product-delivery.toml`:

```toml
name = "product-delivery"
description = "Routed product delivery role for forward-only roadmap, slice, archive, and status actions around external OpenSpec changes."
developer_instructions = """
ROUTED_ACTION=product-delivery
Execute only the mode in the complete routing packet. Read .codex/skills/product-delivery/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

## `product-shared/README.md` contract

The future README, rather than the passive `SKILL.md`, concisely states:

- frozen baseline and archived slice artifacts are user-protected;
- roadmap coverage is declared optimistically when a slice is selected;
- one user and one Codex instance are the single writer;
- `$product-delivery archive` attests prior manual inspection of the product
  archive destination;
- Git or other user-controlled history owns accidental-change recovery;
- the user owns the remaining trust assumptions listed in this design.

The passive `SKILL.md` only routes consumers to the relevant reference,
template, asset, or README. It adds no mode, phase, gate, or mutation.

## Authority and mutation boundaries

Within an action, authority descends from compatible explicit user instruction,
to frozen baseline or persisted discovery, to live filesystem facts allowed by
that mode, to the action skill, and finally to passive shared material.

- Discovery writes only discovery and discovery/baseline control artifacts.
- Synthesis writes only the draft baseline and baseline control receipt.
- Approval performs the one-way baseline freeze. No later action checks the
  approved files against a stored byte identity.
- Delivery writes only `delivery/roadmap.md`, the one active slice file, or its
  unchanged archived destination.
- Product skills never write code, OpenSpec specs or changes, or frozen baseline
  files, and never invoke an external OpenSpec skill.
- Routine discovery bookkeeping is automatic after an authorized action.
- Baseline approval and both delivery previews remain explicit user gates.
