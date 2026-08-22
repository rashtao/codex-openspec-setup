# Skill contracts

## Future package layout

```text
release/.codex/skills/
  openspec-product-discovery/
    SKILL.md
  openspec-product-baseline/
    SKILL.md
  openspec-product-delivery/
    SKILL.md
  openspec-product-shared/
    SKILL.md
    references/
      workflow-contract.md
      artifact-contracts.md
      openspec-integration.md
      failure-recovery.md
    assets/
      discovery/
      baseline/
      delivery/
      handoffs/
    scripts/
      validate_bundle.py
      hash_baseline.py
      render_handoff.py
      inspect_openspec_delivery.py

release/.codex/agents/
  openspec-product-discovery.toml
  openspec-product-baseline.toml
  openspec-product-delivery.toml
```

`openspec-product-shared` is passive and has no matching agent.

## Exact frontmatter selection contracts

### `openspec-product-discovery`

```yaml
---
name: openspec-product-discovery
description: Explicit-only workflow for initializing and interviewing a genuinely greenfield first-release product. Use only when the user explicitly invokes $openspec-product-discovery with init, interview, or status. Never select it for an unqualified request to brainstorm, explore, gather requirements, or plan an OpenSpec change.
---
```

### `openspec-product-baseline`

```yaml
---
name: openspec-product-baseline
description: Explicit-only workflow for synthesizing, reviewing, approving, or inspecting an immutable first-usable-release product baseline from persisted discovery artifacts. Use only when the user explicitly invokes $openspec-product-baseline with synthesize, review, approve, or status. Never select it implicitly for ordinary requirements, documentation, or OpenSpec planning work.
---
```

### `openspec-product-delivery`

```yaml
---
name: openspec-product-delivery
description: Explicit-only workflow for roadmapping, selecting, handing off, structurally reconciling, or closing delivery of a frozen greenfield product baseline through one-at-a-time OpenSpec changes. Use only when the user explicitly invokes $openspec-product-delivery with roadmap, next, status, reconcile, or close. Never select it implicitly for ordinary OpenSpec proposal, implementation, verification, synchronization, or archive requests.
---
```

### `openspec-product-shared`

```yaml
---
name: openspec-product-shared
description: Passive support package containing product-workflow schemas, templates, validators, hashing rules, and prompt-rendering contracts. Never invoke it as a user-facing action.
---
```

Selection language belongs only in these descriptions. Natural-language
requests that do not explicitly name a product skill are outside its activation
boundary.

## User-facing modes

### Discovery

```text
$openspec-product-discovery init <product-id>
$openspec-product-discovery interview
$openspec-product-discovery status
```

- `init` checks greenfield eligibility and creates discovery/control artifacts.
- `interview` asks one breadth-first round, or records the immediately pending
  response and recalculates the frontier.
- `status` is read-only and reports coverage, unknowns, blockers, and the next
  explicit invocation.
- A missing or unrecognized mode never falls back to `status`.

### Baseline

```text
$openspec-product-baseline synthesize
$openspec-product-baseline review
$openspec-product-baseline approve
$openspec-product-baseline status
```

- `synthesize` creates a draft baseline from persisted discovery artifacts only.
- `review` independently checks a draft and writes a review receipt.
- `approve` validates the reviewed digest and freezes the baseline.
- `status` is read-only.
- A missing or unrecognized mode never falls back to `status`.

### Delivery

```text
$openspec-product-delivery roadmap
$openspec-product-delivery next
$openspec-product-delivery status
$openspec-product-delivery reconcile
$openspec-product-delivery close
```

- `roadmap` creates or revises candidate vertical slices.
- `next` selects one ready slice, seals the proposal handoff, and prints the
  complete fresh-session prompt.
- `status` is read-only and prints the current safe next prompt.
- `reconcile` links an active change or structurally reconciles an archive.
- `close` performs final structural reconciliation and archives the product
  bundle.
- A missing or unrecognized mode never falls back to `status`.

There is no product-level `verify`, `archive`, `apply`, or `deviation` mode.

## Routing contract

Each user-facing product skill makes exactly one child dispatch. It does not
execute the action in the parent.

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

The message is a complete packet. It must never tell the child to recover a
request or fact from parent conversation history.

An immediate response to a pending discovery round may continue that explicit
action without repeating the skill name. A response arriving in a new session
must explicitly invoke the discovery skill and include the answer.

## Agent settings

| Agent | Model | Effort | Sandbox |
|---|---|---|---|
| `openspec-product-discovery` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-product-baseline` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `openspec-product-delivery` | `gpt-5.6-sol` | `high` | `workspace-write` |

All modes of a routed skill use its configured effort. Baseline review and
approval validation therefore remain `xhigh` as agreed.

The three future agent files use these exact TOML shapes.

`release/.codex/agents/openspec-product-discovery.toml`:

```toml
name = "openspec-product-discovery"
description = "Routed greenfield product discovery role for explicit initialization, breadth-first interviews, and persisted knowns/unknowns."
developer_instructions = """
ROUTED_ACTION=openspec-product-discovery
Execute only the mode in the complete routing packet. Read .codex/skills/openspec-product-discovery/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

`release/.codex/agents/openspec-product-baseline.toml`:

```toml
name = "openspec-product-baseline"
description = "Routed product baseline role for fresh-context synthesis, independent review, and one-way approval of a first-release baseline."
developer_instructions = """
ROUTED_ACTION=openspec-product-baseline
Execute only the mode in the complete routing packet. Read .codex/skills/openspec-product-baseline/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
sandbox_mode = "workspace-write"
```

`release/.codex/agents/openspec-product-delivery.toml`:

```toml
name = "openspec-product-delivery"
description = "Routed product delivery role for roadmap state, sealed fresh-context handoffs, structural OpenSpec reconciliation, and release closure."
developer_instructions = """
ROUTED_ACTION=openspec-product-delivery
Execute only the mode in the complete routing packet. Read .codex/skills/openspec-product-delivery/SKILL.md before acting. Never route this action again and never spawn another agent.
"""
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
```

## Authority order

Within a product action:

1. the compatible explicit user instruction;
2. frozen baseline and persisted approved product state;
3. live OpenSpec filesystem/CLI facts when delivery is active;
4. the action skill;
5. passive shared techniques.

The passive skill cannot add a phase, approval, output, or OpenSpec mutation.

## Mutation boundaries

- Discovery writes only mutable discovery and control artifacts.
- Baseline synthesis writes only a draft baseline and control receipts.
- Approval performs the one-way freeze transition and writes hashes.
- Delivery never edits the frozen baseline or an OpenSpec change.
- Product skills never implement code, synchronize specs, verify behavior, or
  archive an OpenSpec change.
- Existing OpenSpec skills are invoked manually in separate sessions.
- Routine mutable bookkeeping is automatic after an authorized product action.
- Baseline freeze, slice selection when ambiguous, and release closure remain
  explicit user gates.
