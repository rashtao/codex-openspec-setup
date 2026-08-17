# Manual description testing

> Attribution: this procedure was informed by audited Anthropic description-evaluation concepts and rewritten for Codex without vendor trigger runners, telemetry assumptions, or copied prose.

Use this procedure when testing or revising a skill's frontmatter `description`. It evaluates whether realistic prompts appear appropriately covered while keeping activation evidence separate from output behavior. This build does not automate skill activation.

## Contents

- [Define the decision boundary](#define-the-decision-boundary)
- [Author cases](#author-cases)
- [Separate development and held-out cases](#separate-development-and-held-out-cases)
- [Run each case manually](#run-each-case-manually)
- [Record evidence](#record-evidence)
- [Revise and confirm](#revise-and-confirm)
- [Interpret results cautiously](#interpret-results-cautiously)

## Define the decision boundary

Write down what the skill does, when it should be useful, adjacent tasks it should not own, and any user wording that creates genuine ambiguity. Use only the frontmatter description as the selection contract; do not move trigger instructions into the skill body.

Decide the expected classification before running a prompt:

- `positive`: the task materially matches the skill and should be eligible for implicit selection;
- `near_miss`: the prompt shares vocabulary, files, or domain context but needs a different workflow; or
- `ambiguous`: available context is intentionally insufficient and either selection decision may be defensible.

Do not use obviously unrelated negatives. They inflate apparent accuracy without testing the boundary that matters.

## Author cases

Give every case an immutable ID. Do not key results by prompt text because two useful cases may share wording. Record:

```json
{
  "case_id": "desc-pos-001",
  "split": "development",
  "expected_class": "positive",
  "prompt": "The exact prompt submitted in the clean session.",
  "rationale": "Why this prompt is inside or outside the intended boundary."
}
```

Create realistic positives across formal, casual, abbreviated, and indirect phrasing. Include different inputs, constraints, and edge conditions from ordinary user work. A positive should benefit materially from the skill, not merely contain a keyword from its name.

Create hard near misses that overlap on terms or artifacts but belong to an adjacent skill, a simpler direct action, or a materially different output. Include cases where keyword matching would select the skill incorrectly. Add a small number of genuinely ambiguous cases when the boundary itself needs discussion.

Review case labels and rationales before running them. If a case changes, create a new case ID so older evidence remains interpretable.

## Separate development and held-out cases

Assign cases to `development` or `held_out` before testing. Keep coverage of positives and near misses in both splits. Use development results to revise the description. Do not inspect, score, or tune against held-out results until the description is frozen.

A held-out case stops being held out as soon as its result influences a revision. Move it to development history and reserve a new untouched case for later confirmation. Repeatedly choosing among descriptions on the same held-out set turns it into a validation set and cannot support an unbiased final claim.

For higher-consequence selection boundaries, add more cases and independently reviewed labels. A handful of cases is development feedback, not an estimate of production trigger rates.

## Run each case manually

For each case:

1. Start a new clean host session with the same documented skill inventory and supported settings.
2. Submit the exact prompt without `$skill-name` or any explicit skill invocation.
3. Do not expose the expected class, rationale, skill body, prior results, or evaluator diagnosis to the acting session.
4. Preserve the prompt, response, relevant artifacts, host/version information, and timestamp.
5. Record a supported host selection signal only if the host documents and exposes one for this session.
6. Record output behavior separately from activation evidence.
7. End the session before starting the next case.

Keep environmental conditions stable across comparable cases. If the model, available tools, skill inventory, or host version changes, record a new configuration rather than silently pooling results.

Do not infer activation from response wording, announcements, tool use, file reads, internal binary strings, or behavior that resembles the skill. Those observations may help assess output quality, but they are not an activation receipt.

## Record evidence

Use one result record per immutable case ID:

```json
{
  "case_id": "desc-pos-001",
  "activation": "unknown",
  "activation_signal": null,
  "activation_evidence": null,
  "output_behavior": "meets_expected_behavior",
  "output_evidence": "Transcript and artifact references",
  "host": "host name and version",
  "timestamp": "2026-08-17T12:00:00Z",
  "notes": "No documented machine-readable selection signal was exposed."
}
```

`activation` is `selected`, `not_selected`, or `unknown`. Use `selected` or `not_selected` only when a documented supported host signal directly establishes that state; name the signal and preserve its evidence. When no such signal exists, activation must be `unknown`, even if the output appears to follow the skill closely.

`output_behavior` is `meets_expected_behavior`, `does_not_meet_expected_behavior`, `not_assessed`, or `invalid`. It answers a different question from activation. An infrastructure error is `invalid`; it is not evidence for either selection outcome and must not count as a correct near-miss result.

If activation is unknown, do not calculate activation precision, recall, specificity, or accuracy. You may summarize output behavior with explicit denominators, but label it as behavior rather than trigger accuracy.

## Revise and confirm

Review development errors by boundary pattern, not isolated keyword. Revise the description to state both the capability and the contexts that should select it. Keep the description concise enough to distinguish this skill from adjacent skills.

After a revision:

1. Freeze the new description text and its digest.
2. Re-run development cases in fresh sessions.
3. Check that gains on positives do not introduce near-miss regressions.
4. Stop tuning before opening held-out results.
5. Run held-out cases once against the frozen description.
6. Preserve unknown and invalid states in the denominator report.

Do not create an automated trigger loop, trigger viewer, or description-proposal runner in this skill. A future automation task requires a documented host selection interface and a separately reviewed data contract.

## Interpret results cautiously

Report the exact description digest, host/version, case split, class counts, documented signal availability, and every `unknown` or `invalid` result. Distinguish these conclusions:

- the prompt appears inside or outside the authored description boundary;
- the output did or did not meet the expected behavior; and
- the host did or did not expose supported evidence that the skill was selected.

Only the third conclusion is activation evidence. Without a supported signal, state `activation: unknown` and limit conclusions to description coverage and observed output behavior.
