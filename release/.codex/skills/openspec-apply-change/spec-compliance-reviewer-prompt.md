# Spec-compliance reviewer prompt

Dispatch this read-only review only through `spawn_agent`, using a bounded `task_name` label, `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`. Replace every placeholder in only the fenced body and use that body verbatim.

```text
Independently review OpenSpec change {CHANGE_NAME}, slice {SLICE_ID} ({SLICE_NAME}), for compliance with the supplied authoritative artifacts. Work only in {WORKING_DIRECTORY} and inspect only the listed artifacts and changed paths.

Remain read-only: do not edit files, run mutating commands, choose OpenSpec state, implement fixes, spawn agents, or redispatch yourself. Treat the session baseline as user-owned work and the raw evidence as evidence to verify, not conclusions to trust.

Read {SKILLS_DIRECTORY}/openspec-shared/references/review.md and {SKILLS_DIRECTORY}/openspec-shared/references/evidence-first.md. Read performance-memory.md or integration-correctness.md from that directory only if the supplied contract includes that axis.

Tasks or bounded untracked outcome:
{TASKS_OR_OUTCOME}

Relevant requirements and scenarios:
{REQUIREMENTS_AND_SCENARIOS}

Authoritative artifact paths:
{ARTIFACT_PATHS}

Changed implementation and test paths:
{CHANGED_PATHS}

Applicable repository instructions:
{PROJECT_INSTRUCTION_PATHS}

Session baseline:
{BASELINE_STATUS}

Raw verification evidence:
{RAW_EVIDENCE}

Build an evidence matrix with a separate verdict for every task or outcome, requirement, scenario, relevant scope constraint, and applicable design decision. Use FULFILLED, PARTIAL, MISSING, HONORED, VIOLATED, or NOT_APPLICABLE as appropriate; cite exact artifact and code/test locations and identify untraceable changed behavior.

Issue categories: Task-Incomplete, Missing-Requirement, Missing-Scenario, Out-of-Scope, Design-Violation. Severity: Critical for unusable or unsafe contract failure; Important for a real incomplete, incorrect, or out-of-scope result; Minor for a non-blocking observation.

Return exactly:

STATUS: COMPLIANT | ISSUES

Evidence matrix:
- item — verdict — artifact evidence — implementation/test evidence

Critical:
- category — item — file:line or test — observed evidence — expected contract — impact

Important:
- category — item — file:line or test — observed evidence — expected contract — impact

Minor:
- observation — file:line or test

Use ISSUES when any Critical or Important finding exists. List all findings in one pass.
```
