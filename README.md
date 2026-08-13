# codex-openspec-setup
Enhanced skills for OpenSpec with Codex

## Steps
- `git submodule update --init --recursive`
- `cat prompts/generate_skills.md | codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh" -`
- `cat prompts/generate_documentation.md | codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh" -`

Generated Codex skills, agents, and configuration are published under
`release/.codex/`; the generated OpenSpec configuration is published under
`release/openspec/`.

## Prerequisites

- Linux with Bash, `curl`, and `tar` available.
- OpenSpec CLI installed locally (version `1.8.0`).

## Install

Run this from the project directory:

```bash
curl -fsSL https://raw.githubusercontent.com/rashtao/codex-openspec-setup/main/install.sh | bash
```
