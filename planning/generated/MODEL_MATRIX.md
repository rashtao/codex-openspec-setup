# Model matrix

All routes explicitly select the listed model and reasoning effort. No `xhigh` route is substituted with a lower effort. `opsx-slice-implementer` deliberately uses `gpt-5.6-terra` at `high` for bounded connector slices with concurrency, resource-lifetime, and conversion edge cases. `openspec-verify-change` uses `workspace-write` only so fresh build/test tools can create ordinary outputs; its instructions forbid authored project edits, and specialist reviewers remain `read-only`.

## OpenSpec actions and action agents

| Action / action agent | Model | Effort | Sandbox |
|---|---|---|---|
| `openspec-explore` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-propose` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `openspec-new-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-continue-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-ff-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-update-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-apply-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-verify-change` | `gpt-5.6-sol` | `xhigh` | `workspace-write` |
| `openspec-sync-specs` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-archive-change` | `gpt-5.6-terra` | `high` | `workspace-write` |
| `openspec-bulk-archive-change` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `openspec-onboard` | `gpt-5.6-terra` | `medium` | `workspace-write` |
| `openspec-feedback` (optional action) | `gpt-5.6-terra` | `high` | `read-only` |

## Specialist agents

| Specialist agent | Model | Effort | Sandbox |
|---|---|---|---|
| `opsx-code-explorer` | `gpt-5.6-terra` | `high` | `read-only` |
| `opsx-docs-researcher` | `gpt-5.6-terra` | `high` | `read-only` |
| `opsx-slice-implementer` | `gpt-5.6-terra` | `high` | `workspace-write` |
| `opsx-debugger` | `gpt-5.6-sol` | `high` | `workspace-write` |
| `opsx-test-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-spec-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-api-compat-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-perf-memory-reviewer` | `gpt-5.6-sol` | `high` | `read-only` |
| `opsx-final-consistency-reviewer` | `gpt-5.6-sol` | `xhigh` | `read-only` |
