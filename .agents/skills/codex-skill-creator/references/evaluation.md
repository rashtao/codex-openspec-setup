# Deep evaluation protocol

> Attribution: this protocol was informed by audited Anthropic evaluation concepts and rewritten for Codex without vendor runtime mechanics, copied prose, or agent definitions.

Use this protocol only when the user requests structured evaluation or when the skill's behavior is complex, fragile, consequential, or otherwise hard to assess. Ordinary skill work should stop after realistic forward tests and validation.

## Contents

- [Freeze the evaluation contract](#freeze-the-evaluation-contract)
- [Construct paired runs](#construct-paired-runs)
- [Capture execution evidence](#capture-execution-evidence)
- [Grade without hiding uncertainty](#grade-without-hiding-uncertainty)
- [Aggregate and inspect](#aggregate-and-inspect)
- [Review blindly when warranted](#review-blindly-when-warranted)
- [Iterate without leakage](#iterate-without-leakage)
- [Report bounded conclusions](#report-bounded-conclusions)

## Freeze the evaluation contract

Write the version-`1.0` manifests described in `eval-schemas.md` before executing a case. Treat `suite.json` as immutable after the first run begins. If a prompt, fixture, criterion, configuration, or digest changes, create a new suite ID rather than editing the old suite in place.

Start with two or three realistic cases that exercise materially different behavior. Add cases only after the harness and grading process are stable. A small suite is useful for development; it is not evidence of broad production performance.

For every case:

1. Preserve the prompt exactly as it will be submitted.
2. Record every fixture by relative path and SHA-256 digest.
3. Define the expected outcome in criteria before viewing any output.
4. Give each case, criterion, configuration, run, and pair an immutable ID.
5. Prefer criteria that distinguish genuine completion from superficial compliance.

Use three criterion kinds:

- `deterministic` for checks a reproducible program can decide from captured evidence;
- `model_judge` for judgments that require semantic interpretation;
- `human` for taste, usefulness, visual quality, or decisions reserved for a person.

Do not disguise subjective preferences as deterministic checks. Do not add a criterion after seeing an output and then score that same output as if the criterion had been precommitted. Record post-run discoveries as analyzer notes and place any new criterion in the next suite.

## Construct paired runs

Compare exactly one normalized `candidate` configuration with one normalized `baseline` configuration. Use:

- `no_skill` as the baseline kind for a new skill; or
- `old_snapshot` as the baseline kind for an update, using a frozen pre-change snapshot.

Record a digest for the candidate skill and for an old-snapshot baseline. A `no_skill` baseline has a `null` skill digest. Human-readable labels may describe the configurations, but labels never replace normalized roles or immutable configuration IDs.

For each repetition, assign one `pair_id` and run both arms with:

- the same case prompt and fixture bytes;
- the same model and exposed settings;
- the same authorized tool set and workspace setup;
- independent clean contexts; and
- no access to the other arm's transcript, artifacts, grades, or reviewer notes.

Use a supported clean-session mechanism supplied by the host. Do not invent a generic Codex command or vendor-specific runner. If genuinely independent contexts are unavailable, label the exercise as an inline sanity check and do not present it as a controlled baseline comparison.

When deterministic candidate activation is needed, explicitly invoke the candidate skill in the candidate intervention and omit or disable it for the baseline. Record that intervention in provenance. This establishes the intended treatment; it does not prove that the host emitted an independent activation receipt.

Vary only the intended intervention. If a difference in tools, model settings, fixture state, or harness behavior is unavoidable, create a different suite or mark the affected run `invalid`.

## Capture execution evidence

Write one `run.json` for every attempted arm, including failed and invalid attempts. Never make a failed run disappear by omitting its manifest.

Persist:

- executor, model, and harness identity and version where exposed;
- configuration role, skill digest, case ID, and pair ID;
- transcript and artifact manifests with digests;
- start/end timestamps and wall-clock duration;
- input, output, and total token counts only when the host exposes them; and
- a structured error for `executor_error` or `invalid` status.

Use `null` for unavailable telemetry. Never substitute character count, file size, estimated tokens, or a completion notification for a metric the host did not expose. Keep raw evidence immutable after grading starts.

List run and optional grading manifests explicitly in `run-index.json`. Directory names and discovery order carry no meaning. Preserve index entries for missing grading, executor errors, and invalid records so denominators remain auditable.

## Grade without hiding uncertainty

Grade the transcript and material artifacts, not the final response alone. Inspect binary or structured outputs with appropriate deterministic readers when available. Require evidence references for every criterion verdict.

Apply these verdicts:

- `pass`: captured evidence demonstrates substantive completion of the criterion;
- `fail`: captured evidence contradicts the criterion or demonstrates incomplete work; or
- `invalid`: the criterion cannot be decided from trustworthy available evidence, or the evaluator failed.

An absent observable is not automatically a product failure. Preserve `invalid` separately and explain what prevented a decision. Never silently convert `invalid` to `fail`, though an analysis may separately state how excluded evidence affects confidence.

Check factual, process, and quality claims made by the run. Record each claim as verified, contradicted, or unverifiable with evidence. Also record evaluator-quality warnings when a criterion is trivial, non-discriminating, ambiguous, unobservable, or missing an important outcome. Weak evaluation design and task failure are different findings.

Use deterministic graders for deterministic criteria. Record the actual grader type and version for model or human judgments. If a grading attempt errors, retain any partial verdicts, set grading status to `grading_error`, and exclude undecidable values rather than inventing scores.

## Aggregate and inspect

Run the aggregator only from a validated `suite.json` and `run-index.json`. The benchmark must retain every attempted run and state both included and excluded denominators.

Interpret quality scores as descriptive summaries of valid `pass` and `fail` verdicts, not as replacements for case-level evidence. Inspect, in this order:

1. per-case candidate and baseline runs;
2. matched `pair_id` deltas in candidate-minus-baseline direction;
3. executor, grading-error, and invalid exclusions;
4. criterion-level regressions and improvements;
5. within-arm flakiness across repetitions;
6. criteria that do not discriminate between arms;
7. actual sample counts, mean, and sample standard deviation;
8. seeded bootstrap intervals when the sample count permits them; and
9. duration and token observations only where those metrics are exposed.

A positive quality delta favors the candidate. Positive duration or token deltas mean the candidate cost more. Do not pool unmatched arms into a paired delta. Do not infer missing values as zero.

Analyzer notes must distinguish observed facts from hypotheses and cite case, run, pair, criterion, or artifact evidence. A single pair can suggest a causal hypothesis; it cannot establish causation. Confirm important hypotheses with a targeted rerun and broader cases.

## Review blindly when warranted

Use blind A/B review for consequential choices or when provenance could bias judgment. Randomize and record the A/B mapping per pair before review. When an external random assignment is unavailable, the review generator uses the frozen contract's equivalent counterbalancing option: it ranks immutable case/pair identities with SHA-256, alternates which configuration is A, and records every assignment before writing the page. This produces a stable per-pair mapping with an A/B imbalance of at most one rather than one global role mapping. The viewer never generates or changes mappings at page load.

Before explicit unblinding, the ordinary rendered UI hides configuration labels, roles and IDs, run and pair IDs, skill digests, role-bearing errors, artifact/transcript paths and links, analyzer evidence IDs, findings, directional aggregates, and causal analysis. It still shows neutral A/B labels, run/grading status, task-quality observations, precommitted criterion text, and neutral evidence/artifact summaries. After unblinding it reveals the actual provenance and rebased local links.

This is an ordinary-UI bias boundary, not encryption. The complete validated benchmark, feedback, and mapping remain embedded so the static artifact is reproducible; a reviewer who inspects raw page source or downloaded feedback can recover them. Use an independent reviewer who agrees not to inspect source before judging, and use separate redacted artifacts if protection from a hostile reviewer is required.

Give the reviewer the original prompt, relevant artifacts, run/error status, and precommitted criteria. Permit `A`, `B`, tie, and insufficient-evidence judgments. Do not pressure the reviewer to manufacture a difference. Use multiple independent reviewers when the decision justifies the added cost.

Generate the static review artifact through `generate_review.py`; do not start a server or write a custom review surface. The viewer edits feedback only in browser memory and downloads a schema-valid `feedback.json`. It does not write to the workspace.

Treat `unvisited`, explicit acceptance, and requested changes as separate review states. Empty text is evidence of acceptance only when the reviewer explicitly chose `accepted`; it never means an unvisited run was approved.

## Iterate without leakage

Keep development cases separate from held-out cases. Tune instructions, resources, and criteria using development evidence only. Freeze the candidate before opening held-out results. Once a held-out result influences a revision, relabel it as development evidence and reserve new untouched cases for future confirmation.

For every new iteration:

1. State the evidence-backed hypothesis for the change.
2. Create a new candidate snapshot and digest.
3. Keep prompts, fixtures, baseline, criteria, and harness fixed unless the new suite records the change.
4. Run fresh independent arms.
5. Do not reveal expected answers, prior failures, reviewer feedback, A/B mapping, grades, or analyzer conclusions to executors.
6. Compare targeted failures and a broader regression set before accepting the revision.

Read transcripts as well as artifacts. Remove instructions that add work without measurable value. Bundle repeated deterministic work only when doing so generalizes beyond the current examples.

## Report bounded conclusions

Report the suite ID, skill digests, baseline kind, harness/model provenance, repetitions, all inclusion and exclusion counts, interval method, and available resource denominators. Link conclusions to captured evidence.

State results as development evidence when the suite is small. Do not make significance, reliability, or production-readiness claims from two or three cases. Increase cases, repetitions, independent judgments, and held-out coverage according to the cost and consequence of being wrong.
