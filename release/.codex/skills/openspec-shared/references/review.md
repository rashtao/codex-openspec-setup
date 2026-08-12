# Independent review

Review is read-only and finding-oriented. Give a reviewer the authoritative artifacts, relevant diff, repository standards, and raw verification evidence; never give the implementer's private reasoning transcript. The implementer owns fixes. The same reviewer may evaluate fresh evidence afterward without becoming an implementer.

Select only relevant axes:

- task and artifact completeness;
- behavior against requirements and scenarios, including whether tests fail for the intended defect;
- design and cross-artifact coherence;
- protocol and framework integration and version claims;
- performance and memory methodology, workload, thresholds, allocations, and evidence;
- errors, resources, concurrency, cancellation, timeouts, backpressure, and cleanup;
- repository conventions, scope control, and unrelated changes;
- high-consequence consistency across all applicable axes.

For each finding, report location, violated requirement or risk, evidence, consequence, and severity appropriate to the calling action. Distinguish correctness from optional improvement. Do not add an approval gate or claim a pass without fresh applicable evidence.

When receiving findings:

1. Read and understand the complete set; clarify material ambiguity before editing related items.
2. Verify each claim against the artifacts, repository, supported versions, and current evidence.
3. Accept, reject, or narrow it with technical reasons. Do not implement unsupported scope or respond performatively.
4. Let the authorized implementer fix confirmed findings and produce fresh evidence. A reviewer remains read-only.

For any pass claim, apply [`evidence-first.md`](evidence-first.md). Findings alone are not fresh command or measurement evidence.
