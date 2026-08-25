# Skill contracts

## Future package layout

```text
release/.codex/skills/
  product-discovery/
    SKILL.md
    agents/
      openai.yaml
  product-baseline/
    SKILL.md
    agents/
      openai.yaml
  product-delivery/
    SKILL.md
    agents/
      openai.yaml
  product-shared/
    SKILL.md
    agents/
      openai.yaml
    references/
      workflow-contract.md
      artifact-contracts.md
      openspec-integration.md
      discovery-and-baseline-validation.md
      operating-assumptions.md

release/.codex/agents/
  product-discovery.toml
  product-baseline.toml
  product-delivery.toml
```

`product-shared` is passive, has no custom-agent declaration or executable
helper, and contains only the files shown in this layout. Do not create an
`assets/` directory until a future design names a concrete asset and an action
that consumes it.

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
description: Passive support package containing product-workflow references, including normative artifact templates. Never invoke it as a user-facing action.
---
```

`policy.allow_implicit_invocation: false` is the enforceable activation
boundary for all four packages. Frontmatter descriptions repeat the semantic
exclusions as defense in depth. A natural-language request without the exact
public skill token remains outside the activation boundary.

## Exact interface metadata

`product-discovery/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Discovery"
  short_description: "Initialize and interview a greenfield product."
  default_prompt: "Use $product-discovery to initialize or interview the requested greenfield product."
policy:
  allow_implicit_invocation: false
```

`product-baseline/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Baseline"
  short_description: "Synthesize, review, and freeze a product baseline."
  default_prompt: "Use $product-baseline to synthesize, review, approve, or inspect the persisted product baseline."
policy:
  allow_implicit_invocation: false
```

`product-delivery/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Delivery"
  short_description: "Plan and advance one greenfield delivery slice."
  default_prompt: "Use $product-delivery to roadmap, prepare, archive, or inspect the next product delivery step."
policy:
  allow_implicit_invocation: false
```

`product-shared/agents/openai.yaml`:

```yaml
interface:
  display_name: "Product Shared"
  short_description: "Index passive product workflow references."
  default_prompt: "Use $product-shared only as a passive index for product-workflow references; do not execute it as an action."
policy:
  allow_implicit_invocation: false
```

The four `short_description` values are respectively 46, 50, 47, and 42
characters. Every value must remain between 25 and 64 characters inclusive.

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
  persists and displays its preview, then waits for same-session confirmation.
- `slice` previews one canonical active slice and its roadmap update, waits for
  same-session confirmation of the persisted preview, then writes both targets
  and prints one embedded `$openspec-propose` prompt.
- `archive` moves the one canonical active slice unchanged into
  `delivery/archive/` after the external archive-name check.
- `status` is read-only and prints exactly the next product step.
- A missing or unknown mode prints usage and performs no fallback action.

There are no product delivery modes for applying, verifying, reconciling,
closing, repairing, or altering completed work.

## Routing contract

### Skill-side one-hop guard

`product-discovery/SKILL.md` contains:

“If the current task prompt contains `ROUTED_ACTION=product-discovery`, execute
this installed skill directly and never route `product-discovery` again.
Otherwise dispatch exactly one child using the routing form below.”

`product-baseline/SKILL.md` contains:

“If the current task prompt contains `ROUTED_ACTION=product-baseline`, execute
this installed skill directly and never route `product-baseline` again.
Otherwise dispatch exactly one child using the routing form below.”

`product-delivery/SKILL.md` contains:

“If the current task prompt contains `ROUTED_ACTION=product-delivery`, execute
this installed skill directly and never route `product-delivery` again.
Otherwise dispatch exactly one child using the routing form below.”

Each user-facing `SKILL.md` applies its exact marker guard. An unmarked
invocation dispatches exactly one routed child and performs no product action
in the parent. A marked invocation executes the installed skill directly and
does not dispatch the product action again.

The marker in the current task prompt activates the guard. Reading an agent
`.toml`, using its name as `task_name`, or mentioning its developer instructions
does not activate the guard.

### Routing form

```text
spawn_agent({
  task_name: "<product_action>",
  message: """
ROUTED_ACTION=<skill-name>

Execute exactly this product-skill action.
Read `.codex/skills/<skill-name>/SKILL.md` before acting.
Never route a product action again and never spawn a writer.
For roadmap or slice only, load
`.codex/skills/openspec-shared/references/subagents.md` before any optional
read-only specialist delegation. Every other mode spawns no agent.

MODE: <mode>
USER_REQUEST:
<verbatim current user request>

WORKING_DIRECTORY: repository root
PRODUCT_ROOT: <repository-relative path or unresolved>

Return the result required by the action contract.
""",
  fork_turns: "1",
  model: "<exact model from the mode route table>",
  reasoning_effort: "<exact effort from the mode route table>"
})
```

Top-level product-action routing uses `fork_turns: "1"` so the immediately
preceding user turn is available to the routed child. The child may use that
turn only to parse the explicit invocation, the response to the exactly pending
interview round, or the confirmation or rejection of the exactly pending
delivery preview. Product facts and proposed writes come from persisted
artifacts. The action never relies on older conversation history.

A response without a product-skill token continues `interview` only when
`condition` is `awaiting-interview-response`, `discovery.awaiting_round` names
exactly one persisted round, and that round carries the exact
`pending-response` marker. A confirmation or rejection without a product-skill
token continues `roadmap` or `slice` only when it immediately follows that
preview in the same parent session and the persisted condition and preview
agree. An explicit invocation in a new session never confirms an earlier
preview.

`roadmap` and `slice` may delegate only independent, bounded reads when doing
so materially reduces latency or adds a useful evidence axis. Each specialist
receives a complete evidence packet, uses `fork_turns: "none"`,
`model: "gpt-5.6-terra"`, and `reasoning_effort: "high"`, remains read-only,
returns findings only, and never selects scope, changes workflow state,
presents or accepts confirmation, writes an artifact, routes a product action,
or spawns another agent. The routed product-action child remains the sole
decision-maker and writer. Apply
`.codex/skills/openspec-shared/references/subagents.md` to every such delegation.

## Mode routes

| Skill | Mode | Model | Effort | Write posture |
|---|---|---|---|---|
| `product-discovery` | `init` | `gpt-5.6-sol` | `high` | Discovery/control writes |
| `product-discovery` | `interview` | `gpt-5.6-sol` | `high` | Discovery/control writes |
| `product-discovery` | `status` | `gpt-5.6-luna` | `low` | No writes |
| `product-baseline` | `synthesize` | `gpt-5.6-sol` | `xhigh` | Draft baseline/control writes |
| `product-baseline` | `review` | `gpt-5.6-sol` | `xhigh` | Receipt, manifest-path, and phase writes |
| `product-baseline` | `approve` | `gpt-5.6-sol` | `high` | Manifest and phase writes |
| `product-baseline` | `status` | `gpt-5.6-luna` | `low` | No writes |
| `product-delivery` | `roadmap` | `gpt-5.6-sol` | `high` | Pending preview and confirmed roadmap writes |
| `product-delivery` | `slice` | `gpt-5.6-sol` | `high` | Pending preview and confirmed slice/roadmap writes |
| `product-delivery` | `archive` | `gpt-5.6-sol` | `high` | One unchanged slice move |
| `product-delivery` | `status` | `gpt-5.6-luna` | `low` | No writes |

These are the only public mode routes. All use GPT-5.6 models. `xhigh` is
reserved for synthesis and review; every status mode uses the cheapest route.

Every `status` invocation performs zero writes regardless of the selected
agent's sandbox. It does not update timestamps, normalize invalid state,
persist diagnostics, create control artifacts or run outputs, or spawn a
specialist.

## Standalone declaration defaults and exact files

| Agent | Model | Effort | Sandbox |
|---|---|---|---|
| `product-discovery` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `product-baseline` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `product-delivery` | `gpt-5.6-sol` | `high` | `workspace-write` |

Standalone declaration defaults do not override the public skill's explicit
per-mode spawn route.

`release/.codex/agents/product-discovery.toml`:

```toml
name = "product-discovery"
description = "Routed greenfield product discovery role for explicit initialization, breadth-first interviews, and persisted knowns and unknowns."
developer_instructions = """
ROUTED_ACTION=product-discovery
Execute only the mode in the complete routing packet. Read .codex/skills/product-discovery/SKILL.md before acting. Never route this action again and never spawn another agent. Status performs no write regardless of `sandbox_mode`.
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
Execute only the mode in the complete routing packet. Read .codex/skills/product-baseline/SKILL.md before acting. Never route this action again and never spawn another agent. Status performs no write regardless of `sandbox_mode`.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

`release/.codex/agents/product-delivery.toml`:

```toml
name = "product-delivery"
description = "Routed product delivery role for forward-only roadmap, slice, archive, and status actions around external OpenSpec changes."
developer_instructions = """
ROUTED_ACTION=product-delivery
Execute only the mode in the complete routing packet. Read .codex/skills/product-delivery/SKILL.md before acting. Never route a product action again or spawn a writer. Roadmap and slice may spawn bounded read-only specialists only after loading .codex/skills/openspec-shared/references/subagents.md. Archive and status never spawn an agent. Status performs no write regardless of `sandbox_mode`.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

## `product-shared/references/operating-assumptions.md` contract

The future reference is the normative owner of these operational trust
assumptions:

- Treat the frozen baseline and archived product slice files as user-protected
  artifacts. Product skills do not detect or repair later edits.
- Treat roadmap coverage as an optimistic declaration of planned partial or
  complete coverage made when a slice is selected, not as evidence that
  implementation, verification, synchronization, or archive has occurred.
- Assume one user and one Codex instance are the single writer for product
  artifacts and OpenSpec changes. The workflow provides no locking or
  concurrent-write coordination.
- Invoking `$product-delivery archive` attests that the user manually inspected
  `docs/product/<product-id>/delivery/archive/` and accepts the unchanged
  active-slice destination.
- Use Git or other user-controlled history for recovery from accidental edits,
  deletion, or filesystem conflict. The product workflow provides no repair or
  rollback mode.
- The user owns roadmap correctness, scan completeness, implementation success,
  protection of archived slices, OpenSpec archive correctness, canonical
  synchronization, suffix ambiguity, filesystem conflicts, and all corrective
  work.

The passive `SKILL.md` contains this exact index entry:

```markdown
- [`operating-assumptions.md`](references/operating-assumptions.md) — before relying on user-protected product artifacts, declared coverage, single-writer operation, archive-destination attestation, recovery, or another user-owned trust assumption.
```

The passive `SKILL.md` indexes the applicable reference by link and load
condition. It adds no mode, phase, gate, authority, mutation, or user-facing
documentation file.

## Authority and mutation boundaries

Within an action, authority descends from compatible explicit user instruction,
to frozen baseline or persisted discovery, to live filesystem facts allowed by
that mode, to the action skill, and finally to passive shared material.

- Discovery writes only discovery and discovery/baseline control artifacts.
- Synthesis writes only the draft baseline and baseline control receipt.
- Approval performs the one-way baseline freeze. No later action checks the
  approved files against a stored byte identity.
- Delivery writes only its pending control-plane preview,
  `delivery/roadmap.md`, the one active slice file, or its unchanged archived
  destination.
- Product skills never write code, OpenSpec specs or changes, or frozen baseline
  files, and never invoke an external OpenSpec skill.
- Routine discovery bookkeeping is automatic after an authorized action.
- Baseline approval and both delivery previews remain explicit user gates.
