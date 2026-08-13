# Review and Optimize generate_skills.md

## Summary

Review the complete prompt "prompts/generate_skills.md", then rewrite it in place for reliable Codex CLI execution with gpt-5.6-sol at xhigh reasoning. Preserve its intended skill-generation behavior while removing contradictions, ambiguity, duplication, and unnecessary verbosity. Provide concise review notes explaining material changes.

## Implementation

- Audit the original prompt for conflicting rules, unclear precedence, missing inputs or outputs, impossible sequencing, unsafe autonomy, redundant emphasis, and weak success criteria.
- Cross-check its requirements against current official OpenAI guidance for GPT‑5.6 and Codex skills, plus the skill-creator workflow.
- Reorganize the prompt into a compact execution contract: objective, inputs and assumptions, boundaries, ordered workflow, skill requirements, validation, and final reporting.
- State each rule once, use imperative language, define when Codex should ask questions, and preserve explicit paths, deliverables, and constraints from the original unless they conflict.
- Resolve conflicts by prioritizing safety and user constraints, then explicit output requirements, validation requirements, and workflow guidance. Document every material semantic resolution in the review
notes.

- Keep necessary details for skill triggering, progressive disclosure, scripts/references/assets, metadata, validation, and failure handling; remove generic explanations that GPT‑5.6 does not need.

## Validation

- Perform a static consistency pass covering terminology, instruction precedence, Markdown structure, Codex CLI compatibility, and compliance with current skill requirements.
- Run three independent gpt-5.6-sol/xhigh subagents in isolated temporary workspaces against the revised prompt:
  - A clear instruction-only skill request.
  - A skill requiring a reusable script or reference and executable validation.
  - An underspecified request that tests clarification, assumptions, and scope control.

- Validate generated skill folders with the official quick_validate.py workflow and inspect them for correct triggering metadata, focused scope, appropriate resource use, absence of unnecessary files, and
adherence to requested outputs.

- If a test exposes a prompt-level failure, revise the prompt and rerun the affected scenario. Do not retain generated test artifacts in the repository.

## Deliverables and Assumptions

- Modify only generate_skills.md; all forward-test artifacts remain temporary.
- Return a concise issue summary, the main optimization decisions, validation results, and any residual limitations.
- Preserve the original functional intent rather than introducing new skill-generation capabilities.
- Treat official OpenAI documentation available at execution time as authoritative where it conflicts with stale prompt guidance.