# Bounded code-quality review task

This is an ad-hoc task with no role identity or standing agent. Dispatch the bounded read-only review only through `spawn_agent`, using `task_name` only as a label, `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`. Replace every placeholder in only the fenced body and use that body verbatim.

```text
Perform a bounded independent code-quality review task for OpenSpec change {CHANGE_NAME}, slice {SLICE_ID} ({SLICE_NAME}). Work only in {WORKING_DIRECTORY}; the contract-compliance result is supplied, so do not repeat it or inspect unrelated paths.

Remain read-only: do not edit files, run mutating commands, choose OpenSpec state, implement fixes, spawn agents, or redispatch yourself. Distinguish session work from the user-owned baseline and verify raw evidence directly.

Read {SKILLS_DIRECTORY}/openspec-shared/references/review.md and {SKILLS_DIRECTORY}/openspec-shared/references/evidence-first.md. Read performance-memory.md or integration-correctness.md from that directory only when the corresponding axis applies.

Slice scope and contract-compliance result:
{SLICE_SCOPE_AND_COMPLIANCE}

Relevant design paths:
{DESIGN_PATHS}

Changed implementation and test paths:
{CHANGED_PATHS}

Applicable AGENTS.md files and referenced instructions:
{PROJECT_INSTRUCTION_PATHS}

Session baseline:
{BASELINE_STATUS}

Raw verification evidence:
{RAW_EVIDENCE}

Applicable review items selected under the canonical references:
{APPLICABLE_REVIEW_ITEMS}

Build an evidence matrix with one PASS, FAIL, or NOT_APPLICABLE verdict for every applicable project instruction and supplied review item. Cite file:line or test evidence for every nontrivial verdict; do not introduce unrelated review axes.

Severity:
- Critical: bug, security issue, regression, broken build, or mandatory rule violation that makes the change unusable.
- Important: maintainability or design problem, real missing edge coverage, unnecessary scope or complexity, or applicable project-instruction violation.
- Minor: non-blocking observation or documented should-level preference.

Return exactly:

STATUS: READY | NEEDS_FIXES

Evidence matrix:
- instruction or axis — PASS | FAIL | NOT_APPLICABLE — evidence

Strengths:
- evidence-backed strength

Critical:
- issue — file:line or test — violated rule or risk — concrete fix

Important:
- issue — file:line or test — violated rule or risk — concrete fix

Minor:
- observation — file:line or test

Project instructions checked:
- source — PASS | FAIL — evidence

Use NEEDS_FIXES only when Critical or Important findings exist. List all such findings in one pass.
```
