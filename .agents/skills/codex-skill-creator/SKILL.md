---
name: codex-skill-creator
description: Create or update Codex skills in the current OpenAI format, including concise SKILL.md instructions, reusable scripts, references, assets, agents/openai.yaml metadata, validation, realistic forward tests, and—when explicitly requested or when behavior is complex, fragile, consequential, or hard to assess—structured candidate-versus-baseline evaluation. Use when authoring, migrating, repairing, validating, or improving a Codex skill or its trigger description.
---

<!-- Adapted from the installed OpenAI skill-creator instructions and modified for current Codex rules. -->

# Codex Skill Creator

Build the smallest skill that makes the intended behavior reliable, then validate it with realistic use.

## Establish the contract

1. Gather two or three concrete requests, the user's intent, boundaries, destination, and observable success conditions. Ask only questions whose answers would materially change the result.
2. Honor a user-specified destination exactly. Never substitute a sibling, add a mirror, or relocate the skill silently.
3. If no destination is supplied, ask before writing. Recommend `.agents/skills/<skill-name>` for a repository skill or `$HOME/.agents/skills/<skill-name>` for a user skill. Use `/etc/codex/skills/<skill-name>` only for an authorized administrator installation. Treat plugin packaging as a separate distribution task.
4. Use a lowercase ASCII name containing only letters, digits, and single internal hyphens. Keep it at most 64 characters and match the directory basename.

## Preserve existing work

For an update, inventory the exact target and establish a pre-change snapshot or diff base before editing. Classify content as intentional, generated residue, or uncertain. For an underspecified update, treat every existing script, reference, metadata file, and other file as intentional; change one only when the user requests its change or an observed defect or required interface change proves it necessary. Preserve all other intentional and uncertain content, remove generated residue only when its origin is clear, and default to the smallest file set without opportunistically improving preserved files. State the narrow assumptions that bound the update, record preservation evidence such as the reviewed inventory and unchanged hashes or final diff, and never replace an existing skill with a newly initialized sibling.

For third-party material, preserve applicable licenses and notices, and mark adapted files as modified. Do not invent an owner, copyright notice, source, or license claim.

## Plan reusable contents

Analyze how each concrete request would be completed from scratch, then include only resources that make those workflows repeatable:

- Put deterministic or repeatedly rewritten operations in `scripts/`.
- Put selectively loaded domain knowledge and detailed procedures in `references/`.
- Put templates and other output inputs in `assets/`.
- Keep variable judgment as concise instructions; use parameterized patterns for bounded variation and strict scripts for fragile operations.
- Omit unused categories, empty directories, placeholders, and auxiliary documentation.

Link every reference directly from `SKILL.md`, state when to read it, and avoid duplicating its details. Give references longer than 100 lines a compact table of contents.

## Create or update the skill

1. For a new skill, run `scripts/init_skill.py <skill-name> --path <parent-directory>` with only the required `--resources`, optional `--examples`, and `--interface key=value` arguments. For an existing skill, edit it in place without running the initializer.
2. Build and exercise useful resources before finalizing `SKILL.md`. Replace or remove initializer examples after they serve their scaffolding purpose.
3. Write `SKILL.md` for another Codex instance. Require `name` and `description` in frontmatter. Add only the currently supported optional fields when they are useful: `metadata.short-description` for a compact label and `model: luna` for the runtime's bounded delegation hint. Place all selection language in the description, and keep the body concise, imperative, nonempty, and below 500 lines.
4. Before creating or regenerating UI metadata, read the [openai.yaml metadata reference](references/openai_yaml.md). Use `scripts/generate_openai_yaml.py` and include only supported fields that the skill actually needs.
5. Remove authoring markers, unused files, generated examples, and empty resource directories before completion.

## Validate and iterate

1. Execute every materially distinct bundled script with realistic input. For a large family of near-identical scripts, exercise a representative sample and explain the sampling boundary.
2. Run `scripts/quick_validate.py <skill-directory>`. Repair every failure and rerun it.
3. Retain the exact command, stdout, stderr, and numeric exit status for every required validation or representative script execution. Make final claims only when retained evidence supports them; omit or qualify unsupported validation, dry-run, or audit claims.
4. Inspect resource relevance, file modes, and the final diff. The validator checks direct local links, completed scaffolds, supported frontmatter fields, and the current local `agents/openai.yaml` interface, MCP-dependency, and policy schema. Treat structural validation as one check, not proof of behavior or activation.
5. Exercise two or three realistic ordinary requests in clean enough contexts. Inspect the response, produced artifacts, and command results; iterate from evidence without leaking expected answers or prior diagnoses into later runs.
6. Ask before tests that are expensive, approval-gated, or capable of mutating production systems.

When testing or revising a skill description, read the [manual description-testing procedure](references/description-testing.md). Keep selection evidence separate from output quality and do not infer activation from response wording or apparent behavior.

Stop after the lightweight validation loop by default. Lint alone is insufficient, but formal benchmarking is not the default cost.

## Run deep evaluation conditionally

Enter the deep workflow only when explicitly requested or when behavior is complex, fragile, consequential, or hard to assess. Read the [deep-evaluation protocol](references/evaluation.md), then read the [evaluation schemas](references/eval-schemas.md) before authoring manifests or running evaluation scripts. Freeze a small realistic suite and discriminating criteria, run candidate and meaningful baseline independently in clean contexts, preserve invalid and error records, grade against evidence, aggregate with `scripts/aggregate_benchmark.py`, and iterate without leaking evaluation conclusions.

For qualitative review, use `scripts/generate_review.py` with the [static evaluation viewer template](assets/eval-viewer.html). Treat the generated page as an in-memory review surface, not a workspace writer, and avoid broad statistical claims from tiny suites.
