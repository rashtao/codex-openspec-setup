# Generate the release user guide

## Objective

Generate the repository-facing OpenSpec guide at `release/USER_GUIDE.md` from the
current published distribution. Run this prompt manually from the repository root after
`prompts/generate_skills.md` has completed successfully.

The guide must help a user choose and invoke the installed OpenSpec actions, understand
their boundaries and results, and see how each action routes through its skill, action
agent, shared references, specialists, and bounded reviewer tasks.

## Source of truth and write boundary

Treat `release/**`, excluding the output file `release/USER_GUIDE.md`, as the sole source
of truth for every documented runtime fact. Read the current files; do not reconstruct
behavior from memory. In particular:

- derive skills, actions, routes, stages, conditions, outputs, permissions, models,
  efforts, sandboxes, references, reviewer packets, and configuration behavior only from
  explicit content under `release/**`;
- do not inspect or derive runtime behavior from `planning/generated/**`, `lib/**`,
  staging output, Git history, an earlier generation prompt, or hard-coded action names or
  counts;
- do not infer a relationship merely because two components have compatible descriptions;
  require an explicit reference, dispatch instruction, load condition, or route in the
  release content;
- use the requirements in this prompt only to determine the guide's structure and
  validation rules, never to invent a runtime fact absent from `release/**`.

Modify only `release/USER_GUIDE.md`. Do not modify, format, regenerate, rename, or remove
any other file. Temporary validation files may be created only outside the repository,
such as beneath a fresh directory in `/tmp`, and must not be published. Do not generate
PNG, SVG, PlantUML, Graphviz, or other diagram artifacts. Keep Mermaid source embedded in
the guide.

Before reading content, capture a stable, lexically sorted inventory and SHA-256 snapshot
of every regular file under `release/` except `release/USER_GUIDE.md`. Capture
`git status --short` as the ownership baseline. Recheck the source snapshot before
publishing; if it changed during the run, stop without publishing a mixed-version guide.

## Dynamic discovery and consistency gate

Inventory all of the following recursively from the release tree:

1. Every skill represented by a `release/.codex/skills/*/SKILL.md`, using its directory,
   frontmatter name and description, body, and any local metadata.
2. Every action-agent TOML under `release/.codex/agents/` that explicitly declares an
   OpenSpec action route, including optional actions.
3. Every remaining custom-agent TOML under `release/.codex/agents/` as a specialist agent.
4. Every passive support skill and every reference it owns, including all files beneath a
   passive skill's `references/` directory.
5. Every reviewer prompt packet anywhere under `release/.codex/skills/**`.
6. The generated OpenSpec configuration at `release/openspec/config.yaml`.

Use content, not filename prefix alone, to classify components:

- An actionable skill defines a user-selectable action or workflow. An action agent is a
  TOML whose instructions explicitly route that action, normally through a
  `ROUTED_ACTION=<canonical-name>` declaration.
- A skill may remain unpaired only when its own release content explicitly declares it
  passive, non-invocable support that defines no user workflow. Document such a skill and
  its references separately and do not count it as an action.
- An agent without an action route is a specialist. Never promote it to an action merely
  because an action can dispatch it.
- Reviewer packets are Markdown instruction packets explicitly used for bounded review or
  subagent work. Discover them from the files and their references; do not assume a fixed
  packet list.

Pair each actionable skill with exactly one action agent by canonical action name. Require
the skill directory name, skill frontmatter name, agent `name`, routed action declaration,
and referenced skill path to agree wherever those fields are present. Complete discovery
and pairing before writing the guide.

Stop with a message beginning `CONSISTENCY ERROR:` and leave an existing
`release/USER_GUIDE.md` untouched if any of these conditions holds:

- an actionable skill has no matching action agent;
- an action agent has no matching actionable skill;
- an action has duplicate skills or agents;
- the canonical names or the agent's referenced skill path disagree;
- an unpaired skill is not explicitly passive support;
- a required route fact needed by the guide, such as model, effort, or sandbox, is missing
  or ambiguous;
- the OpenSpec configuration named above is missing.

Report every discovered mismatch with its paths. Do not repair release files, invent a
counterpart, silently omit the component, or fall back to a known action list. For example,
an optional action such as `openspec-feedback` is an ordinary discovered pair and must be
documented; its presence is not determined by whether another source enumerates it.

## Fact extraction

For every paired action, read the complete skill and action-agent TOML plus each directly
relevant release reference or packet needed to document it. Extract, without broadening:

- exact canonical action name and whether release content labels it optional;
- purpose, appropriate use cases, natural-language trigger examples, boundaries,
  forbidden effects, expected result, and completion/reporting behavior;
- read-only versus write behavior, including external side effects, separately from the
  agent's sandbox mode;
- exact model, reasoning effort, and sandbox from the matching action agent;
- the one-hop action-skill-to-action-agent routing contract;
- principal workflow stages and explicitly significant decisions, loops, early stops,
  approvals, or blocked outcomes;
- conditional shared-reference loads;
- named specialist agents the action is genuinely eligible to dispatch and the exact
  conditions under which it may do so;
- anonymous bounded subagent or reviewer tasks explicitly allowed by the action, including
  the conditions and packet used when applicable.

For every specialist agent, read the complete TOML and extract its exact name, purpose,
model, effort, sandbox, scope/boundaries, and explicitly loaded references. For every
passive skill and shared reference, extract its purpose, trigger/load condition, and
consumers only when those consumers are explicit. For each reviewer packet, extract its
caller, purpose, route, read/write boundary, dispatch condition, and result contract from
release content. Read the OpenSpec configuration and summarize only the rules and role it
actually declares.

Do not equate sandbox access with an action's effects: describe both when they differ. Do
not attach every shared reference, specialist, or reviewer task to every action. Absence of
an explicit route is evidence that no diagram edge should be drawn.

## Required guide structure

Write concise, durable user documentation in this stable order:

1. Title and scope. State that the guide describes the currently published `release/`
   distribution.
2. Architecture and terminology. Briefly distinguish OpenSpec action, action skill,
   one-hop routed action agent, passive shared reference, named custom specialist agent,
   and anonymous bounded subagent/reviewer task. Explain read/write behavior versus agent
   sandbox. Do not add an architecture Mermaid diagram.
3. Action chooser. Provide one lexically sorted row per discovered action pair. Include
   columns for the exact action and links to both its skill and action agent, purpose/when
   to choose it, natural-language trigger examples, expected result, read-only/write and
   external-side-effect behavior, model, effort, sandbox, and optional status. Make the
   examples phrases a user could naturally say, not invented slash-command syntax.
4. Diagram legend. Provide one common prose legend for all action diagrams: solid arrows
   are mandatory flow; dashed labeled arrows are conditional flow; nodes prefixed
   `named agent:` are installed custom agents; nodes prefixed `ad hoc subagent task:` are
   anonymous bounded tasks, even when a reviewer packet configures them. This is the only
   legend; do not add legend nodes to individual graphs.
5. Actions. Add exactly one lexically ordered section for every discovered action pair.
   Each section must contain when-to-use guidance, several natural-language invocation
   examples supported by that action's triggers, boundaries and non-goals, expected output
   or terminal states, exact runtime route facts, relevant conditional support, and exactly
   one Mermaid diagram meeting the diagram contract below. Link the skill, action agent,
   and every shown release asset.
6. Passive shared support. Provide a complete catalog of every passive skill and every
   owned reference, with links, purpose, load condition, and explicitly documented action
   consumers. State that passive skills are not user actions and have no action diagram.
7. Specialist agents. Provide a complete catalog of every specialist-agent TOML, with a
   link, exact purpose, model, effort, sandbox, scope/boundaries, and explicitly eligible
   callers. Do not list anonymous reviewer tasks as installed specialist agents.
8. Supporting assets. Catalog every discovered reviewer prompt packet with its link,
   caller, purpose, model/effort when declared, boundary, dispatch condition, and expected
   result. Also link and accurately describe `openspec/config.yaml`. Do not describe
   planning or source-tree artifacts.

Use repository-relative Markdown links resolved from the guide's location in `release/`.
For example, a release skill link begins `.codex/skills/`, and the configuration link is
`openspec/config.yaml`. Prefer links to raw path text whenever naming a release asset.
Keep paths, action names, agent names, models, efforts, sandboxes, states, and command names
verbatim. Paraphrase prose instead of copying large instruction passages.

Do not include timestamps, generation commentary, machine-specific absolute paths, source
hashes, transient Git status, or claims about a hard-coded number of actions. Preserve an
existing compliant passage when its supporting release facts have not changed; do not
rewrite for stylistic novelty.

## Mermaid action-diagram contract

Include exactly one Mermaid fence in each action section and no Mermaid fence anywhere
else. Every action graph must be independently understandable and satisfy all of these
rules:

1. Start the fence with `flowchart TD`.
2. Make the first node declaration `action["<exact-canonical-action-name>"]`, substituting
   the discovered action name verbatim as the label. The node identifier `action` is local
   to that graph. This must be the unique graph root: it has no incoming edge, and every
   other declared node has at least one incoming edge.
3. Show the action skill, then the one-hop routed matching action agent, as mandatory flow
   immediately after the action. Do not route through another action or action skill.
4. Show the principal workflow stages and every significant explicit branch, loop, stop,
   approval, or conditional outcome needed to avoid a misleading linear workflow.
5. Show a shared reference only when the action explicitly loads it, with a dashed edge
   labeled by the release-stated condition. Show a named specialist only when the action
   explicitly makes that specialist eligible, also with its real condition. Show an ad hoc
   reviewer or subagent task only when explicitly authorized.
6. Label installed specialists `named agent: <exact-agent-name>`. Label anonymous work
   `ad hoc subagent task: <bounded-purpose>`. A prompt packet does not turn an anonymous
   task into a named installed agent.
7. Use only solid `-->` edges for mandatory flow. Use only dashed, non-empty labeled
   `-. <condition> .->` edges for conditional flow, including optional branches and loops.
   Keep condition text single-line and free of Mermaid control characters. Do not use an
   unlabeled dashed edge or label a conditional edge as mandatory.
8. Use ASCII node identifiers matching `[A-Za-z][A-Za-z0-9_]*`. Give every node one unique
   identifier and an explicit quoted label. Keep labels single-line and escape characters
   that Mermaid or Markdown would otherwise parse. Do not use `subgraph`, `click`, HTML,
   custom initialization directives, or legend nodes.
9. Ensure the graph's edges, not visual ordering alone, express control flow. Connect every
   support node from the stage that conditionally loads or dispatches it. If it returns to
   the workflow, draw the explicit conditional return edge only when release content says
   it does.
10. Derive every relationship from release content. Never make all specialists appear
    universally available and never add a relationship merely to make a graph look
    complete.

Protect these especially easy-to-misstate boundaries whenever they occur in the current
release:

- onboarding may teach or demonstrate other actions, but that does not mean it invokes
  their action skills or agents;
- archive readiness is not a verification-action invocation;
- an inline synchronization stage is not an invocation of the separate sync action.

Represent those behaviors as ordinary local workflow stages when release content supports
them, without an edge to another action skill or action agent.

## Validation before publication

Build and validate a complete candidate outside the repository before updating the target.
Use deterministic lexical ordering and stable prose/heading templates. Run all of the
following checks, fixing the candidate and repeating the entire validation set after any
change:

### Coverage and factual consistency

- Re-run dynamic discovery from a fresh read of `release/**` and compare it with the
  candidate. Every current actionable skill and matching action agent must appear in the
  chooser and its action section. Every passive skill/reference, specialist agent, reviewer
  packet, and the OpenSpec configuration must appear exactly once in the appropriate
  complete catalog.
- Compare every documented model, effort, sandbox, action boundary, side effect, output,
  stage, branch, route, reference load, specialist eligibility, and ad hoc task against its
  cited release file. Remove unsupported inferences.
- Assert that no action invokes a different action skill or action agent unless release
  content explicitly requires such invocation. Specifically audit onboarding, archive,
  and inline sync representations against the boundary rules above.
- Assert that optional actions receive the same required coverage as other actions and are
  clearly labeled optional only when release content says so.

### Markdown, links, and Mermaid structure

- Parse Markdown fences. Require exactly one `mermaid` fence per action pair, zero for each
  passive support skill, and no additional Mermaid fences. Require every fence to close.
- For every diagram, require `flowchart TD` first and
  `action["<exact-canonical-action-name>"]` as the first node. Parse all node declarations
  and edges; reject duplicate or invalid identifiers, missing or unsafe labels, references
  to undeclared nodes, unsupported syntax, and malformed conditional edges.
- Compute indegree from all diagram edges. Require `action` to have indegree zero, every
  other node to have positive indegree, and therefore `action` to be the first and only
  zero-incoming-edge node. Require all nodes to be reachable from `action`.
- Require every mandatory edge to use `-->`. Require every conditional edge to use exactly
  `-. non-empty label .->`. Reject other edge forms. Check that the diagram relationships
  and mandatory/conditional classification agree with the linked release instructions.
- Resolve every relative Markdown link from `release/USER_GUIDE.md`, including the file
  component of links with fragments. Reject path escapes, missing targets, incorrect case,
  and unresolved local fragments. Ignore only explicitly external URI schemes.
- If `mmdc` is already available on `PATH`, extract each diagram to the temporary directory
  and render-check it there. Do not install Mermaid CLI or any dependency. Absence of
  `mmdc` is not a warning or failure; structural validation remains mandatory.

### Idempotence and repository safety

- Produce a second candidate from a fresh source inventory using the same ordering and
  templates, then compare the two byte for byte. Reconcile any difference and repeat until
  unchanged release content produces identical output. If the existing guide is already
  byte-identical, leave it untouched.
- Recheck the release source snapshot immediately before publication. Publish only the
  accepted candidate to `release/USER_GUIDE.md`.
- Verify against the initial Git-status baseline that no path other than
  `release/USER_GUIDE.md` was changed by this run. Preserve all pre-existing user changes.
- Run exactly `git diff --check`. Do not edit another file to fix an unrelated failure;
  report that limitation precisely instead.
- Repeat the coverage, link, diagram, and factual checks against the published file. Compare
  it byte for byte with the accepted candidate.

If any required check fails and cannot be corrected by changing only the candidate guide,
do not publish it. If an existing guide was present, leave it unchanged. Report the failed
check, affected paths or diagram, and evidence. Never weaken a check, install a package, or
change release runtime files to obtain a pass.

## Completion report

After successful publication, report the discovered counts for action pairs, passive
skills and references, specialist agents, and reviewer packets without treating those
counts as permanent. Report the output path, validation results, whether `mmdc` was used or
absent, and whether the guide was created, updated, or already unchanged. Do not claim that
the guide is installed by `install.sh`; it is repository documentation generated only by
this manual prompt.
