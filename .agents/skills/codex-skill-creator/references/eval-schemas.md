# Evaluation data contract

> Attribution: this versioned contract was informed by audited Anthropic evaluation concepts and rewritten for Codex without vendor runtime mechanics, copied schemas, or agent definitions.

This document is normative for `suite.json`, `run-index.json`, `run.json`, `grading.json`, `benchmark.json`, and `feedback.json`. The aggregation script, review generator, and static viewer must consume version `1.0` exactly as defined here.

## Contents

- [Common rules](#common-rules)
- [`suite.json`](#suitejson)
- [`run-index.json`](#run-indexjson)
- [`run.json`](#runjson)
- [`grading.json`](#gradingjson)
- [`benchmark.json`](#benchmarkjson)
- [`feedback.json`](#feedbackjson)
- [Rendered review data](#rendered-review-data)
- [Cross-document validation](#cross-document-validation)

## Common rules

Every document is a UTF-8 JSON object with `"schema_version": "1.0"`. Writers emit stable, indented JSON with sorted object keys, LF line endings, and a final newline. JSON numbers must be finite. Validators reject malformed JSON, unsupported schema versions, missing required fields, wrong types, duplicate IDs, and fields that contradict referenced manifests.

Use `criteria` consistently. The obsolete fields `assertions` and `expectations` are errors; a validator must name the obsolete field and direct the author to `criteria` rather than silently migrating it.

IDs are nonempty strings matching `^[A-Za-z0-9][A-Za-z0-9._-]*$`. An ID is immutable within a frozen suite. IDs declared in the same namespace are unique.

A digest is `sha256:` followed by exactly 64 lowercase hexadecimal characters. Timestamps are RFC 3339 UTC strings ending in `Z`. Durations are finite nonnegative seconds. Token values are nonnegative integers or `null`; `null` means the executor did not expose that measurement. Zero means an observed zero and is never a missing-value substitute.

Input manifest paths use `/` separators, are relative to the manifest containing them, and contain neither an empty segment nor `.` or `..`. Absolute paths and backslashes are invalid. Resolve each referenced path and reject it if it escapes the containing manifest's directory. Fixture, artifact, and transcript files must exist; their declared digests must match their bytes where a digest is present. Paths inside referenced run and grading documents remain relative to their own document.

Paths projected into `benchmark.json` are instead relative to the directory containing that `benchmark.json`. They use `/`, are never absolute, and are canonical. Aggregation derives them only after validating and resolving the input path against its source manifest. A generated benchmark-relative path may begin with one or more `..` segments when the chosen benchmark output directory is not an ancestor of the evidence, but `..` cannot occur after the first ordinary segment. Consumers must not reinterpret an unvalidated input path as a benchmark-relative path.

An error is either `null` or:

```json
{
  "code": "executor_timeout",
  "message": "The supported executor timed out before completion."
}
```

Both error fields are nonempty strings. `error` is `null` for a completed status and non-null for an error or invalid status.

An evidence reference is a nonempty string with a source prefix, a manifest-relative path when applicable, and a reproducible locator after `#`. Valid forms include `artifact:outputs/result.json#/summary/count`, `transcript:transcript.md#L20-L24`, `run_manifest:#/status`, and `grading_manifest:#/criteria/0`. The prefix is `transcript`, `artifact`, `run_manifest`, or `grading_manifest`. A reference may summarize a line, section, JSON pointer, cell, page, or command after the locator, but a summary never replaces the source and locator.

## `suite.json`

A suite freezes one candidate-versus-baseline comparison. Its exact top-level fields are `schema_version`, `suite_id`, `configurations`, and `cases`.

```json
{
  "schema_version": "1.0",
  "suite_id": "skill-dev-v1",
  "configurations": [
    {
      "configuration_id": "candidate-v1",
      "role": "candidate",
      "label": "Candidate v1",
      "skill_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    {
      "configuration_id": "baseline-no-skill",
      "role": "baseline",
      "label": "No skill",
      "skill_digest": null,
      "baseline_kind": "no_skill"
    }
  ],
  "cases": [
    {
      "case_id": "case-001",
      "prompt": "Create the requested artifact from fixtures/orders.csv.",
      "fixtures": [
        {
          "path": "fixtures/orders.csv",
          "sha256": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        }
      ],
      "criteria": [
        {
          "id": "case-001-correct-count",
          "text": "The artifact reports the correct row count.",
          "kind": "deterministic"
        }
      ]
    }
  ]
}
```

`configurations` contains exactly two objects with distinct `configuration_id` values: exactly one `candidate` and exactly one `baseline`. Each candidate configuration contains exactly `configuration_id`, `role`, `label`, and `skill_digest`. Each baseline contains exactly those fields plus `baseline_kind`. `label` is a nonempty human-facing label. The candidate has a non-null skill digest and omits `baseline_kind`. The baseline kind is `no_skill` or `old_snapshot`. A `no_skill` baseline has `skill_digest: null`; an `old_snapshot` baseline has a non-null digest.

`cases` is nonempty. Each case contains exactly `case_id`, `prompt`, `fixtures`, and `criteria`. Case IDs are unique. `prompt` is the exact nonempty submitted prompt. `fixtures` may be empty; every entry contains exactly `path` and `sha256`. Fixture digests are verified before execution and again before aggregation.

Each case has at least one precommitted criterion. Each criterion contains exactly `id`, `text`, and `kind`. Criterion IDs are unique across the suite, `text` is nonempty, and `kind` is `deterministic`, `model_judge`, or `human`. Changing any case prompt, fixture, digest, criterion, or configuration after execution starts requires a new suite ID.

## `run-index.json`

A run index is the only discovery mechanism for aggregation. Its exact fields are `schema_version`, `suite_id`, and `runs`.

```json
{
  "schema_version": "1.0",
  "suite_id": "skill-dev-v1",
  "runs": [
    {
      "run_manifest": "runs/case-001/pair-001/candidate/run.json",
      "grading_manifest": "runs/case-001/pair-001/candidate/grading.json"
    },
    {
      "run_manifest": "runs/case-001/pair-001/baseline/run.json"
    }
  ]
}
```

`runs` is an ordered nonempty array. Every entry contains exactly one `run_manifest` and may contain one `grading_manifest`. Omission of `grading_manifest` means no grading manifest was supplied; it does not mean task failure. Duplicate paths and duplicate referenced run IDs are invalid. Directory names, lexical order, and files absent from this array carry no semantics.

## `run.json`

A run manifest records every attempted arm. Its exact top-level fields are:

`schema_version`, `run_id`, `suite_id`, `case_id`, `configuration_id`, `role`, `pair_id`, `skill_digest`, `executor`, `model`, `harness`, `artifacts`, `transcript_path`, `started_at`, `ended_at`, `duration_seconds`, `input_tokens`, `output_tokens`, `total_tokens`, `status`, and `error`.

```json
{
  "schema_version": "1.0",
  "run_id": "case-001-pair-001-candidate",
  "suite_id": "skill-dev-v1",
  "case_id": "case-001",
  "configuration_id": "candidate-v1",
  "role": "candidate",
  "pair_id": "case-001-pair-001",
  "skill_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "executor": {"name": "supported-clean-session", "version": "1.2"},
  "model": {"name": "model-id", "settings": {"reasoning_effort": "high"}},
  "harness": {"name": "local-eval-harness", "version": "1.0"},
  "artifacts": [
    {
      "path": "outputs/result.json",
      "sha256": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "media_type": "application/json"
    }
  ],
  "transcript_path": "transcript.md",
  "started_at": "2026-08-17T10:00:00Z",
  "ended_at": "2026-08-17T10:00:12Z",
  "duration_seconds": 12.0,
  "input_tokens": null,
  "output_tokens": null,
  "total_tokens": null,
  "status": "completed",
  "error": null
}
```

`role`, `configuration_id`, and `skill_digest` exactly match the referenced suite configuration. `case_id` exists in the suite. `pair_id` is shared by one candidate and one baseline attempt for the same case; each repetition uses a new pair ID. A run ID occurs once in the index.

`executor` contains exactly `name` and `version`; `model` contains exactly `name` and `settings`; `harness` contains exactly `name` and `version`. Names are nonempty strings, versions are nonempty strings or `null`, and settings is a JSON object containing only settings actually used.

`artifacts` may be empty. Each artifact contains exactly `path` and `sha256`, plus optional `media_type`; paths and digests are unique within the run and the digest must match the artifact bytes. `transcript_path` is a relative path or `null` when no transcript was captured. A completed run requires a transcript path. Artifact and transcript paths are resolved relative to `run.json`, must remain under that directory, and must exist.

`started_at` is required. `ended_at` and `duration_seconds` are observed values or `null` if the harness could not capture them. When both timestamps and duration are present they must agree within the harness's declared clock precision.

`input_tokens`, `output_tokens`, and `total_tokens` are independently nullable. If all three are present, total equals input plus output. Do not derive tokens from characters or artifact sizes.

`status` is `completed`, `executor_error`, or `invalid`. `completed` means execution reached a normal terminal state and has `error: null`; it does not imply task success. `executor_error` records a harness/executor failure. `invalid` records an attempt unsuitable for comparison, such as fixture drift or provenance mismatch. Error and invalid runs remain indexed.

## `grading.json`

A grading manifest has the exact fields `schema_version`, `grading_id`, `run_id`, `suite_id`, `case_id`, `status`, `grader`, `criteria`, `claims_checked`, `evaluator_quality_warnings`, and `error`.

```json
{
  "schema_version": "1.0",
  "grading_id": "grade-case-001-pair-001-candidate",
  "run_id": "case-001-pair-001-candidate",
  "suite_id": "skill-dev-v1",
  "case_id": "case-001",
  "status": "completed",
  "grader": {"type": "mixed", "version": "rubric-v1"},
  "criteria": [
    {
      "criterion_id": "case-001-correct-count",
      "verdict": "pass",
      "evidence": ["artifact:outputs/result.json#/row_count"]
    }
  ],
  "claims_checked": [
    {
      "claim": "The output contains four data rows.",
      "evaluation": "verified",
      "evidence": ["artifact:outputs/result.json#/row_count"]
    }
  ],
  "evaluator_quality_warnings": [],
  "error": null
}
```

The IDs match the referenced run and suite. `grader` contains exactly `type` and `version`; type is `deterministic`, `model_judge`, `human`, or `mixed`, and version is a nonempty identifier for the checker, rubric, model configuration, or human protocol.

`criteria` uses the canonical term and contains at most one record per suite criterion. `criterion_id` must belong to the case. `verdict` is `pass`, `fail`, or `invalid`. `evidence` is an array of nonempty evidence-reference strings. A `pass` or `fail` verdict requires at least one reference; an `invalid` verdict may use an empty array when no trustworthy evidence exists. `invalid` is never silently converted to `fail`.

A completed grading contains exactly one verdict for every case criterion. A `grading_error` or `invalid` grading may contain a validated partial set, which aggregation preserves but excludes from a complete-run quality score.

Each `claims_checked` entry contains exactly `claim`, `evaluation`, and `evidence`. `evaluation` is `verified`, `contradicted`, or `unverifiable`; evidence is an array of reference strings and is nonempty for verified or contradicted claims.

Each evaluator warning contains:

```json
{
  "code": "non_discriminating_criterion",
  "message": "The criterion checks file presence but not correctness.",
  "criterion_id": "case-001-correct-count",
  "evidence": ["grading_manifest:#/criteria/0"]
}
```

`criterion_id` may be `null` for a suite-wide warning. Warnings diagnose evaluator quality and do not change task verdicts.

Grading `status` is `completed`, `grading_error`, or `invalid`. Completed grading has `error: null`; the other statuses require an error. A run with non-completed execution cannot have completed grading.

## `benchmark.json`

`benchmark.json` is the validated, review-ready projection produced by aggregation. It preserves all indexed attempts, including exclusions. Its top-level fields are `schema_version`, `benchmark_id`, `suite_id`, `generated_at`, `methods`, `counts`, `cases`, `aggregates`, `findings`, `quality_cost`, and `analyzer_notes`.

### Methods and statistic records

`methods` contains:

```json
{
  "quality_score": "pass/(pass+fail); invalid excluded",
  "paired_delta": "candidate-minus-baseline for matching case_id and pair_id",
  "dispersion": "sample_standard_deviation",
  "interval": "seeded_percentile_bootstrap_of_mean",
  "bootstrap_seed": 17,
  "bootstrap_samples": 2000,
  "confidence_level": 0.95,
  "significance_claim": false
}
```

`bootstrap_seed` is the supplied integer. `bootstrap_samples` is a positive integer when intervals are requested and zero otherwise. This contract makes descriptive intervals, not tiny-suite significance claims.

The seeded bootstrap stream is replayable in this canonical order: within each case, candidate then baseline quality and the four resources in documented order, followed by case paired quality; then candidate and baseline aggregate quality/resources, aggregate paired quality, and `quality_cost` quality followed by its four resource deltas. Each statistic with at least two values draws `bootstrap_samples` resamples of the original sample size from one `random.Random(bootstrap_seed)` stream. Sort the resampled means and linearly interpolate at `(1-confidence_level)/2` and its complement; round means, sample standard deviations, and interval bounds to six decimal places. Statistics below two samples or with bootstrap sampling disabled do not consume the stream and have a null interval.

Every statistic record contains exactly:

```json
{
  "sample_count": 3,
  "mean": 0.75,
  "sample_stddev": 0.05,
  "bootstrap_interval": {"lower": 0.70, "upper": 0.80}
}
```

`sample_count` is the number of actual included observations. `mean` is `null` at zero samples. Sample standard deviation and bootstrap interval are `null` below two samples. The interval is also `null` when bootstrap sampling is disabled. Resource statistic records count only runs that expose that resource. A missing metric therefore remains visible as `sample_count: 0` with a null mean rather than disappearing.

### Counts

`counts` contains exactly:

- `indexed_runs`
- `completed_runs`
- `executor_error_runs`
- `invalid_runs`
- `grading_completed_runs`
- `grading_error_runs`
- `grading_invalid_runs`
- `grading_missing_runs`
- `quality_included_runs`
- `quality_excluded_runs`

All are nonnegative integers. Execution status counts sum to `indexed_runs`; grading status plus missing counts also sum to `indexed_runs`; quality included plus excluded counts sum to `indexed_runs`.

### Per-case records

`cases` follows suite order. Every case record contains `case_id`, `prompt`, `criteria`, `configurations`, `pairs`, and `paired_quality`.

`criteria` copies the suite's criterion definitions. `configurations` contains candidate then baseline. Each configuration record contains exactly `configuration_id`, `role`, `label`, `skill_digest`, `baseline_kind`, `runs`, `quality`, and `resources`. `baseline_kind` is null for the candidate and carries the suite value for the baseline.

Every indexed run appears exactly once in `runs` and contains:

- `run_id`, `pair_id`, `run_manifest`, and nullable `grading_manifest`;
- `run_status`, nullable `grading_status`, `run_error`, and `grading_error`;
- `transcript_path` and the complete artifact manifest;
- `criteria`, copied from grading when present, including verdict and evidence;
- `claims_checked` and `evaluator_quality_warnings`, copied as their structured grading records;
- `quality` with `passed`, `failed`, `invalid`, `total`, and nullable `score`;
- nullable `duration_seconds`, `input_tokens`, `output_tokens`, and `total_tokens`.

These are the exact run-projection fields. `run_manifest`, `grading_manifest`, `transcript_path`, and every projected artifact path use the benchmark-relative representation defined above. `grading_manifest` and `transcript_path` may be null when absent; the other projected paths may not.

A run has a quality score only when execution and grading are both completed and at least one criterion is `pass` or `fail`. The score denominator is `passed + failed`; `invalid` remains visible but is excluded. `quality` at configuration level contains `included_count`, `excluded_count`, and a `statistics` record over run scores.

`resources` contains exactly `duration_seconds`, `input_tokens`, `output_tokens`, and `total_tokens`. Each resource contains `observed_count`, `missing_count`, and `statistics`; the statistics sample count equals `observed_count`, while observed plus missing equals the arm's indexed-run count. Missing observations never become zero and do not share the quality denominator.

Each pair record contains exactly `pair_id`, `candidate_run_id`, `baseline_run_id`, `status`, `exclusion_reason`, `candidate_score`, `baseline_score`, and `quality_delta`. Every observed pair ID gets a record, including an unmatched arm. Status is `included` only when both quality scores exist for matching `case_id` and `pair_id`; otherwise it is `excluded`, missing run IDs or unavailable scores are `null`, `quality_delta` is null, and `exclusion_reason` is nonempty. Included `quality_delta` is candidate minus baseline.

`paired_quality` contains `included_pair_count`, `excluded_pair_count`, and a statistic record over included `quality_delta` values.

### Aggregates and findings

`aggregates` contains exactly `configurations` and `paired_quality`. Configuration aggregate records contain exactly `configuration_id`, `role`, `label`, `skill_digest`, `baseline_kind`, `quality`, and `resources`, and use actual cross-case observations. `paired_quality` has included/excluded pair counts plus delta statistics across all included pairs.

`findings` contains arrays named `regressions`, `flakiness`, and `non_discriminating_criteria`.

A regression record contains `case_id`, nullable `criterion_id`, `pair_ids`, `delta`, and evidence references. It identifies observed candidate loss, not a causal claim. A flakiness record contains `case_id`, `configuration_id`, `criterion_id`, `run_ids`, and `observed_verdicts`; flakiness requires both `pass` and `fail` within the same arm and excludes invalid verdicts. A non-discriminating record contains `case_id`, `criterion_id`, `reason`, and `run_ids`; it reports no observed separation and does not prove the criterion is universally weak.

`quality_cost` contains exactly `candidate_configuration_id`, `baseline_configuration_id`, `quality_delta`, `duration_seconds_delta`, `input_tokens_delta`, `output_tokens_delta`, and `total_tokens_delta`. Every delta is a statistic record over matching `case_id`/`pair_id` candidate-baseline arms where both values exist. No arm mean is subtracted from a differently populated arm mean. When no matched observation exists, the record has `sample_count: 0` and null mean, standard deviation, and interval. Positive quality favors the candidate; positive resource deltas mean the candidate used more.

Each analyzer note contains `note_id`, `text`, and nonempty `evidence`. Analyzer evidence contains `case_id` and nullable `run_id`, `pair_id`, `criterion_id`, and `artifact_path`. Notes separate observations from hypotheses and cannot alter computed fields.

## `feedback.json`

Feedback records static-viewer state without claiming workspace write-back. Its exact top-level fields are `schema_version`, `suite_id`, `reviewer`, `timestamp`, `blind_mapping`, and `reviews`.

```json
{
  "schema_version": "1.0",
  "suite_id": "skill-dev-v1",
  "reviewer": {
    "name": "Independent reviewer",
    "metadata": {"reviewer_id": "reviewer-01"}
  },
  "timestamp": "2026-08-17T11:00:00Z",
  "blind_mapping": {
    "scope": "case_pair",
    "method": "sha256_counterbalanced_case_pair_v1",
    "assignments": [
      {
        "case_id": "case-001",
        "pair_id": "case-001-pair-001",
        "A": "baseline-no-skill",
        "B": "candidate-v1"
      }
    ]
  },
  "reviews": [
    {
      "run_id": "case-001-pair-001-candidate",
      "status": "accepted",
      "text": ""
    },
    {
      "run_id": "case-001-pair-001-baseline",
      "status": "changes_requested",
      "text": "The row count is incorrect."
    }
  ]
}
```

`suite_id` equals the benchmark's suite ID. `reviewer` contains exactly `name` and `metadata`; name is a nonempty string and metadata is an otherwise unconstrained JSON object. The top-level timestamp records when this feedback state was saved.

`blind_mapping` contains exactly `scope`, `method`, and `assignments`. `scope` is `case_pair`. `method` is `recorded_random_per_pair_v1` for assignments randomized and persisted by an evaluation harness, or `sha256_counterbalanced_case_pair_v1` for the renderer's reproducible counterbalancing method. `assignments` contains exactly one record for every case/pair in benchmark order; each record contains exactly `case_id`, `pair_id`, `A`, and `B`, and maps A/B to the benchmark's two distinct configuration IDs.

When no feedback file is supplied, the renderer orders immutable case/pair identities by SHA-256 of the suite ID, benchmark ID, case ID, pair ID, and method namespace, chooses a SHA-256-derived starting side, then alternates sides in that order. This is the frozen workflow's explicit counterbalancing alternative: mapping scope is per pair, presentation is balanced to within one assignment, and repeated renders of the same benchmark reproduce exactly. The renderer creates the complete unvisited feedback document before embedding data; the viewer never generates or changes a mapping at page load.

Before explicit unblinding, the ordinary UI uses only neutral A/B and ordinal labels for provenance. It withholds configuration labels/roles/IDs, run and pair IDs, skill digests, raw error text, artifact/transcript paths and links, analyzer evidence IDs, findings, directional aggregates, and other role-bearing provenance copy. After unblinding it reveals those fields and rebased links. This boundary does not claim secrecy from raw HTML source inspection or downloaded feedback: the full validated benchmark and mapping remain embedded for reproducibility.

`reviews` contains exactly one record for every run visible in the benchmark and no others. Status is `unvisited`, `accepted`, or `changes_requested`:

- `unvisited` contains exactly `run_id` and `status`; it omits `text`;
- `accepted` requires `text` as a string and permits it to be empty; and
- `changes_requested` requires nonempty string `text`.

Empty text never implies acceptance unless status is explicitly `accepted`. Tie and insufficient-evidence judgments remain valid review outcomes and may be recorded in accepted review text; they must not be coerced into a false preference.

## Rendered review data

The `review-data` application/JSON element contains exactly `schema_version`, `benchmark`, `feedback`, and `benchmark_link_base`. `benchmark` and `feedback` are complete validated version-1.0 documents; `feedback` is never null and already contains every case/pair mapping. `benchmark_link_base` is the review-output-relative path to the directory containing `benchmark.json`, using the same portable representation and allowing the canonical `.` value. After unblinding, the viewer combines that validated base with benchmark-relative evidence paths, so a review written in a different directory still resolves the original artifacts and transcripts. Before unblinding it creates no artifact or transcript href. It treats path values only as relative link targets, never executable markup or URLs.

## Cross-document validation

Before aggregation or rendering, enforce all of these rules:

1. Every document uses schema version `1.0`, and every referenced suite ID agrees.
2. Input manifest paths are explicit, unique, relative to their containing manifest, and remain inside its directory; only resolved, validated paths are rebased into benchmark and review link paths.
3. Run IDs are unique; run case/configuration/role/digest values exactly match the suite.
4. Each pair ID belongs to one case and has at most one candidate and one baseline run.
5. Grading IDs are unique; grading run/case/suite IDs match the referenced run.
6. Criterion IDs and kinds originate in the suite; no post-hoc criterion is scored as precommitted.
7. Errors and `invalid` states remain visible and are never converted to zero, `fail`, or a missing record.
8. Paired deltas use only matching case and pair IDs in candidate-minus-baseline direction.
9. Counts, sample sizes, means, sample standard deviations, and intervals reproduce from the visible per-run values and the canonical recorded-method stream; render and output validation reject contradictions.
10. Feedback references exactly the benchmark's suite, configuration, case/pair, and visible run IDs, obeys review-state text rules, and is present with one recorded assignment per pair before the viewer starts.
11. `assertions` or `expectations` anywhere a criterion collection is expected produces a named migration error.
12. Rendering preserves hostile text as data, rebases benchmark paths against the chosen review output, never changes the benchmark or feedback schema, and never trusts embedded paths as executable content.
