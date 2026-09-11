# Final consistency reviewer prompt

Dispatch `opsx-final-consistency-reviewer` read-only only through `spawn_agent`, using `task_name` as a label, `model: "gpt-5.6-sol"`, `reasoning_effort: "xhigh"`, and `fork_turns: "none"`. Replace every placeholder in only the fenced body and use that body verbatim.

```text
Independently review the complete implementation of OpenSpec change {CHANGE_NAME}, schema {SCHEMA_NAME}, as one integrated, high-consequence change. Work only in {WORKING_DIRECTORY} and inspect only the listed artifacts, instructions, and change-associated paths.

Remain read-only: do not edit files, run mutating commands, choose OpenSpec state, implement fixes, invoke another action, spawn agents, or redispatch yourself. Separate session changes from the user-owned baseline and verify raw evidence directly.

Read {SKILLS_DIRECTORY}/openspec-shared/references/review.md and {SKILLS_DIRECTORY}/openspec-shared/references/evidence-first.md. Read performance-memory.md or integration-correctness.md from that directory only when the corresponding axis applies.

OpenSpec artifact paths:
{ARTIFACT_PATHS}

Applicable AGENTS.md files and referenced instructions:
{PROJECT_INSTRUCTION_PATHS}

All change-associated implementation and test paths:
{ALL_CHANGED_PATHS}

Session baseline:
{BASELINE_STATUS}

Raw per-slice and cumulative verification evidence:
{RAW_EVIDENCE}

Build an evidence matrix with a separate PASS, FAIL, or NOT_APPLICABLE verdict for every cross-slice interface, type, and error contract; lifecycle or ordering assumption; shared-state boundary; concept name and representation; duplicated, superseded, or dead unit; cumulative scope item; applicable project instruction; and artifact gap exposed by integration. Cite exact artifact, file:line, test, or command evidence for every verdict.

Severity:
- Critical: broken integration, regression, security defect, or mandatory rule failure that prevents completion.
- Important: cross-slice inconsistency, maintainability problem, cumulative scope or complexity, or applicable project-instruction violation.
- Minor: non-blocking observation.

Return exactly:

STATUS: READY_FOR_GATE | NEEDS_FIXES | ARTIFACT_BLOCKED

Evidence matrix:
- item — PASS | FAIL | NOT_APPLICABLE — evidence

Strengths:
- evidence-backed cross-slice strength

Critical:
- issue — file:line or test — impact — concrete fix

Important:
- issue — file:line or test — impact — concrete fix

Minor:
- observation — file:line or test

Project instructions checked:
- source — PASS | FAIL — evidence

Artifact gaps:
- evidence — affected proposal, spec, design, or task artifact — why code cannot safely decide

Use NEEDS_FIXES for Critical or Important code findings and ARTIFACT_BLOCKED when a planning contradiction must be resolved first. List all findings in one pass.
```
