For each skill directory under `.codex/skills/`, create a sub-agent task, with `gpt-5.6-sol` with high reasoning effort,
and make execute the following:

---

Input: <current> skill

### Objectives & Instructions

Review, correct, and enhance the files of the current skill (including `SKILL.md`, prompts, and supporting templates).
This setup is built exclusively for **Codex CLI**. Ignore other agentic frameworks (Claude Code, Cursor, Windsurf, etc.).

1. **Thorough Skill & Workspace Inspection**
   - Read skill definition, prompt templates, and supporting files under `.codex/skills/<current>`.
   - Inspect any local CLI tools, project configuration files, or templates referenced by the skills to ensure full behavioral alignment.

2. **Codex-Native Optimization**
   - Remove or replace framework-specific instructions, slash commands (`/opsx-*`), and pseudo-tools (`todowrite`, generic `question tool`, `skill tool`, etc.) with accurate Codex-native behavior (e.g. `update_plan`, direct questions, native commands).
   - Adapt subagent dispatches (`spawn_agent`, `send_message`, `wait_agent`, etc.) to Codex-native paradigms.
   - Enforce explicit model routing in dispatches:
     - `gpt-5.6-sol` high for Main orchestrator, planning, design, spec, and review agents
     - `gpt-5.6-terra` medium for Implementer / Fixer agent

3. **Clarity, Reliability, & Quality Improvements**
   - Streamline prompt length and eliminate repetitive slogans or performative rituals while preserving core rigor.
   - Tailor prompts knowing they will be executed by capable models
   - Establish clear delegation contracts between agents (orchestrator, implementer, reviewers) without polluting the main context.
   - Fix any edge cases, broken references, or invalid YAML frontmatter attributes across all skills.

Important Notes:
- Preserve the exact semantics and intended behavior of the skills.
- Apply the minimal needed modifications

Goal:
- make these skills execute cleanly and reliably in Codex CLI
- enforce specific models for sub-agents

