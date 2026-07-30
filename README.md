# codex-openspec-setup
Enhanced skills for OpenSpec with Codex

## Steps
- install OpenSpec
- install OpenSpecPlus
- adapt skills for Codex: `prompts/1_init.md`
- add dbg skill: `prompts/2_add_dbg_skill.md`

## Pre-Reqs
- OpenSpec CLI installed locally (version `1.7.0`).

## Install

Copy the prompt below and paste it directly into Codex CLI.
It will download, install, and configure everything automatically.

```
Setup OpenSpec Codex

Your task is to install the skills and the OpenSpec directory from the GitHub repository
https://github.com/rashtao/codex-openspec-setup into the current project.

Follow these steps in order.

Step 1 — Verify OpenSpec is not set up

Check if an `openspec/` directory exists in the current working directory.
- If it exists:
  warn the user that OpenSpec directory is already set up in this project.
  Suggest removing the `openspec/` directory and retry.
  STOP here — do not continue.
- If it does not exist:
  proceed to Step 2.

Step 2 — Verify skills are not already installed

Detect whether in the current project there are directories named like `.codex/skills/openspec-*`.
- If they exist:
  warn the user that OpenSpec skills are already set up in this project.
  Suggest removing `.codex/skills/openspec-*` directories and retry.
  STOP here — do not continue.
- If they do not exist:
  proceed to Step 3.

Step 3 — Download from GitHub

Download the repository https://github.com/rashtao/codex-openspec-setup to a temporary
location.

Step 4 — Install skills and OpenSpec directory

From the downloaded repository:
1. Copy all `.codex/skills/openspec-*` directories inside `.codex/skills/` of the current project, copy the entire directories recursively.
2. Copy `openspec` directory inside the current project, copy the entire directory recursively.

Step 5 — Clean up

Remove the temporary download directory.

Step 7 — Summary report

Provide a brief summary with:
- The skills installed
- The openspec directory installed
- Whether any problem has been encountered

Recommend the user to restart Codex for the skills to take effect.
```
