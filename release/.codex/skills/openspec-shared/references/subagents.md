# Bounded delegation and concurrency

Delegate only when a narrow independent task materially improves latency or a high-consequence result. Do not delegate a trivial local read, summon every specialist, use delegation to avoid understanding integration, or let an agent dispatch itself.

## Creation and coordination contract

The only new-agent creation form is:

```text
spawn_agent({ task_name, message, fork_turns?, model?, reasoning_effort? })
```

- Set an explicit GPT-5.6 `model` and explicit `reasoning_effort` for every spawn. Do not rely on inherited defaults.
- Every spawn with either override must set `fork_turns` explicitly. Use `fork_turns: "1"` only for top-level action routing so the latest user request is available. Use `fork_turns: "none"` for a specialist whose message includes the complete evidence packet. Never combine an override with `fork_turns: "all"` or an omitted fork.
- Use `task_name` as a task label. There is no callable custom-agent selector; do not invent `agent_type`, agent-name, role-name, or similar parameters.
- Give the child a bounded objective, exact read/write scope, necessary authoritative artifacts and raw evidence, constraints, expected return, and a no-recursion instruction.
- Reading a custom-agent TOML does not activate its developer instructions or defaults. A generic specialist message must therefore contain its complete role and evidence packet rather than claim TOML activation.
- An action skill follows its own marker-based one-hop guard. A message containing `ROUTED_ACTION=<action>` executes that installed action skill directly and never routes the same action again.
- Coordinate existing agents only with `send_message({ target, message })`, `followup_task({ target, message })`, `interrupt_agent({ target })`, `list_agents({ path_prefix? })`, and `wait_agent({ timeout_ms? })`. These calls do not create agents.

## Specialist selection

Select only a relevant specialist and pass the explicit route shown:

| Specialist | Model | Effort | Default scope | Responsibility |
|---|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | `high` | read-only | Focused codebase, dependency, and test discovery. |
| `opsx-docs-researcher` | `gpt-5.6-terra` | `high` | read-only | Version-specific primary-source research. |
| `opsx-slice-implementer` | `gpt-5.6-terra` | `high` | workspace-write | One bounded vertical slice against fixed artifacts. |
| `opsx-debugger` | `gpt-5.6-sol` | `high` | workspace-write | Hard defects, nondeterminism, concurrency, leaks, and regressions. |
| `opsx-test-reviewer` | `gpt-5.6-sol` | `high` | read-only | Whether tests can fail for the intended defect. |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | `high` | read-only | Implementation against proposal, specs, design, and tasks. |
| `opsx-api-compat-reviewer` | `gpt-5.6-sol` | `high` | read-only | Public API and behavior compatibility, deprecations, and release impact. |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | `high` | read-only | Methodology, hot paths, allocations, and measurement evidence. |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | `xhigh` | read-only | High-consequence cross-artifact consistency. |

The live parent sandbox and approval policy can constrain a child's declared default. Never promise stronger isolation than the runtime supplies. Reviewers and researchers remain read-only and return findings or evidence; they do not choose workflow state or edit artifacts.

Project custom-agent declarations are independently selectable standalone `.codex/agents/*.toml` files. Each declaration sets `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, and `sandbox_mode`. Their defaults apply only when the runtime actually selects that custom agent. Valid sandbox defaults are `read-only`, `workspace-write`, and `danger-full-access`; no generated role requires `danger-full-access`. Configure global concurrency under `[agents]` with `max_concurrent_threads_per_session`.

## Parallel-work decision table

| Work | Parallelize only when | Keep sequential when |
|---|---|---|
| Discovery or review | Domains are independent and parallel reads reduce latency. | Failures may share a cause or whole-system context is required. |
| Implementation | Slices are dependency-independent, file scopes are explicitly disjoint, no file can be touched by multiple writers, and integration order is defined. | Work shares artifacts, schema or config, migrations, public interfaces, files, state, or unresolved dependencies. |
| Bulk archive investigation | Reads concern independent changes or implementation evidence. | Conflict decisions, rule snapshots, main-spec writes, validation, and moves. |

Assign each writer an explicit file and behavior boundary. A writer that sees an unexpected overlapping modification stops and reports it rather than overwriting it. One owner or sequential integration handles shared artifacts, schema and configuration, related migrations, and cross-cutting public interfaces.

After children return, inspect their output and diffs, check for overlap, integrate in the defined order, and apply [`evidence-first.md`](evidence-first.md) to the combined result. A child report alone does not establish completion.
