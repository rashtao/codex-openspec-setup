---
name: openspec-feedback
description: Optional OpenSpec feedback action counterpart, outside the 12 enumerated generated skills. Use when the user wants to draft, anonymize, approve, and submit feedback about OpenSpec through the current CLI.
---

# OpenSpec feedback

Turn recent-conversation feedback about OpenSpec into a useful privacy-safe report, submit it only after the user approves the complete current draft, report the outcome, and stop.

This optional action counterpart is not one of the 12 generated OpenSpec skills and is not a lifecycle phase. It does not create or modify project files, planning artifacts, changes, code, Git state, or releases. Its only authorized external side effect is one invocation of `openspec feedback` after explicit approval.

## One-hop action routing

If the current task prompt contains `ROUTED_ACTION=openspec-feedback`, execute this installed skill directly and never route `openspec-feedback` again. Otherwise call exactly:

```text
spawn_agent({
  task_name: "openspec_feedback",
  message: "ROUTED_ACTION=openspec-feedback. Execute the latest user request directly. Read .codex/skills/openspec-feedback/SKILL.md and follow it. Never route openspec-feedback again.",
  fork_turns: "1",
  model: "gpt-5.6-terra",
  reasoning_effort: "high"
})
```

Wait for the child and return its result without also executing the action. `task_name` is only a label; do not invent a custom-agent selector or claim that a TOML file was activated.

## Procedure

1. Gather evidence from the recent conversation only:
   - identify what the user was trying to do with OpenSpec;
   - record what actually happened, including useful errors or observable results;
   - distinguish praise, friction, and requested improvement;
   - retain concrete technical details that help maintainers understand or reproduce the report;
   - do not invent missing facts or turn inferences into events. If the intended feedback or a material fact is absent, ask the user.

   Do not start external research merely to draft feedback.

2. Draft two CLI inputs:
   - **Title input:** one clear sentence without a `Feedback:` prefix.
   - **Body input:** concise prose covering the supported goal, outcome, relevant context, and suggestion or request. Omit unsupported content.

3. Anonymize both inputs before every display:
   - sensitive file paths become `<path>` or a safe generic description;
   - API keys, tokens, passwords, credentials, and secrets become `<redacted>`;
   - company or organization names become `<company>`;
   - personal names become `<user>`;
   - identifying URLs become `<url>` unless public and necessary;
   - remove other unnecessary identifying detail while retaining useful technical names, versions, errors, and behavior.

   Never include raw sensitive context merely because it appeared earlier. Recheck the complete title and body after every revision.

4. Present the complete sanitized current draft exactly as:

```text
Title input:
<title>

Body input:
<body>

OpenSpec will create the issue title as:
Feedback: <title>

OpenSpec will append its version, platform, and submission timestamp to the body.
```

   Ask the user to request changes or explicitly approve submission of this exact version. Approval must clearly authorize submission, not merely acknowledge the text. Do not run a command while awaiting the answer.

   Any revision requires re-anonymization, a complete redisplay, and fresh explicit approval. Approval never carries across a revision. If the user declines or withdraws the request, report that nothing was submitted and stop.

5. Only after explicit approval, invoke exactly once:

```text
openspec feedback "<approved title>" --body "<approved body>"
```

   Preserve each value as one shell argument. Do not substitute `gh`, a GitHub API, a browser, or another route. Approval authorizes this command invocation and the CLI's own missing-label retry; it does not authorize an agent-authored retry after an uncertain result.

## CLI outcomes

- **Automatic success:** report the printed issue URL and successful submission.
- **Missing repository label:** the CLI may establish that the labeled attempt created no issue and retry without the label. Report the printed issue URL, success, and that the issue is unlabeled. Do not retry again.
- **GitHub CLI missing:** report that nothing was submitted automatically and provide the CLI's prefilled manual URL.
- **GitHub CLI unauthenticated:** report that nothing was submitted automatically and provide the manual URL plus the CLI's authentication guidance.
- **Other GitHub CLI failure:** report no confirmed submission, the failure, exit status, and manual URL. Do not retry.
- **OpenSpec unavailable, interrupted, or outcome uncertain:** preserve the approved draft, report the sanitized limitation and available output, and state that submission is unknown when creation cannot be ruled out. Require a new explicit decision before any retry.

The CLI adds the `Feedback: ` title prefix and the version/platform/timestamp footer. Do not add them to the inputs.

## Completion

Report the sanitized command form, exit status when available, and exactly one outcome: submitted with URL; not submitted with manual fallback; automatic submission failed with no confirmed submission and fallback; or submission state unknown. Include the unlabeled condition when applicable. Never describe a manual URL as a completed submission or expose sensitive command output. Stop after reporting.
