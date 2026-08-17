<!-- Adapted from the installed OpenAI skill-creator metadata reference and modified for current Codex rules. -->

# `agents/openai.yaml` metadata

Use `agents/openai.yaml` for product and harness metadata, not agent instructions. Keep operational guidance in `SKILL.md` and references.

## Supported shape

The OpenAI format can contain these top-level sections:

- `interface`: UI metadata and a starter prompt.
- `dependencies`: declared tool dependencies.
- `policy`: product invocation policy.

The bundled validator rejects unknown keys that the runtime would otherwise
ignore. It validates current runtime field types and limits, local icon paths,
MCP transports and their required endpoint fields, OAuth callback ports,
`policy.allow_implicit_invocation`, and `policy.products`.

The bundled `scripts/generate_openai_yaml.py` intentionally owns only an `interface`-only file. It refuses to overwrite an existing file containing `dependencies`, `policy`, or any unknown top-level key. Preserve and validate those hand-authored sections separately instead of discarding them during regeneration.

## Interface fields

The generator accepts only these `--interface key=value` keys:

- `display_name`: a nonempty human-facing title.
- `short_description`: a human-facing summary from 25 through 64 characters.
- `icon_small`: an existing skill-relative path beneath `./assets/`.
- `icon_large`: an existing skill-relative path beneath `./assets/`.
- `brand_color`: a six-digit color in `#RRGGBB` form.
- `default_prompt`: a short starter that explicitly contains `$<skill-name>`.

Quote every string value and leave mapping keys unquoted. Prefer a one-sentence default prompt. Include icons and color only when the user supplies them or the skill has a concrete UI need for them.

The generator emits interface keys in this order: `display_name`, `short_description`, `icon_small`, `icon_large`, `brand_color`, `default_prompt`. Repeated CLI assignments use the last value.

## Safe generation

Create or refresh metadata with:

```bash
scripts/generate_openai_yaml.py <skill-directory> --interface 'display_name=Human-facing name' --interface 'short_description=Human-facing summary text' --interface 'default_prompt=Use $skill-name to complete the task.'
```

When values are omitted, the generator derives deterministic display-name, short-description, and default-prompt values from the skill name. Supply explicit values when the derived copy would be misleading.

Before regeneration:

1. Read the current file and preserve supported optional interface values that remain relevant.
2. Confirm every icon path exists inside the skill's `assets/` directory.
3. Confirm the default prompt names the exact skill with `$skill-name` syntax.
4. Refuse unknown top-level content rather than replacing it.

After regeneration, inspect the diff and ensure the metadata still matches `SKILL.md`.

## Interface-only example

```yaml
interface:
  display_name: "Release Note Polisher"
  short_description: "Polish concise customer release notes"
  default_prompt: "Use $release-note-polisher to polish these release notes."
```

## Optional product sections

OpenAI metadata may additionally define MCP tool dependencies under
`dependencies.tools`. Each tool requires `type` and `value`; current Codex MCP
dependencies support `streamable_http` with `url` or `stdio` with `command`,
plus optional `description` and `oauth.callbackPort`. Policy supports Boolean
`allow_implicit_invocation` and a `products` list containing `atlas`, `chatgpt`,
or `codex`. Add these sections only when the user and runtime requirements call
for them. Because this skill's generator will not rewrite such a file, make
deliberate hand edits and run `scripts/quick_validate.py` afterward.
