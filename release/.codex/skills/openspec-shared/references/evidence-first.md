# Evidence before claims

Use evidence proportionate to the claim; do not turn test-first technique into a ritual.

| Change or claim | Evidence contract |
|---|---|
| Behavior change | Prefer a failing executable test before the production fix when the intended behavior can reasonably be expressed as one. Verify through a public seam with expected values independent of the implementation. |
| Bug fix | Reproduce and minimize the failure before fixing it. Add or identify evidence that fails for the defect, then verify the repaired behavior freshly. |
| Refactor | Establish characterization evidence of current behavior before changing structure; rerun it afterward. |
| Performance or memory | Record a reproducible baseline, environment, and representative workload; after the change rerun the same measurement and correctness tests. |
| Connector or framework behavior | Use the narrowest useful contract test, integration test, or reproducible fixture when a unit test cannot represent real protocol or framework semantics. |
| Executable evidence unavailable or inapplicable | Name the reason, limitation, affected scope, and alternate evidence. Do not report a pass from missing evidence. |

Keep each implementation slice behaviorally coherent and its diff focused. Use mocks only at genuine external boundaries; do not substitute a mock for necessary integration evidence. Never mask a failure with skips, todo markers, disabled tests, narrowed filters, suppressed output, or weakened assertions. Remove diagnostic instrumentation before returning.

For any pass, complete, fixed, ready, build, test, lint, validation, or measurement claim:

1. Run a fresh applicable command or measurement after the relevant change when the environment permits it.
2. Report the command, result, and relevant scope. Distinguish focused evidence from broader regression evidence.
3. Inspect changed outputs or diffs where an agent or tool performed the work; a report of success is not independent evidence.
4. If execution is unavailable, report degraded evidence and remaining uncertainty. Absence of evidence is not a passing result.

Mark an implementation task complete only after its observable outcome exists, its applicable focused evidence passes, and required cleanup is complete.
