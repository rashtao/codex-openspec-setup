#!/usr/bin/env python3
"""Render and validate a dependency-free static evaluation review."""

# Design informed by audited evaluation concepts and rewritten for Codex with
# safe JSON embedding, atomic output, and no server or vendor runtime.

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
SENTINEL = "__CODEX_EVAL_DATA__"
REVIEW_STATUSES = {"unvisited", "accepted", "changes_requested"}
RUN_STATUSES = {"completed", "executor_error", "invalid"}
GRADING_STATUSES = {"completed", "grading_error", "invalid"}
RESOURCE_FIELDS = ("duration_seconds", "input_tokens", "output_tokens", "total_tokens")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
TOP_LEVEL_FIELDS = {
    "schema_version", "benchmark_id", "suite_id", "generated_at", "methods",
    "counts", "cases", "aggregates", "findings", "quality_cost", "analyzer_notes",
}


class ReviewError(ValueError):
    """A template, document, or rendered-output validation failure."""


class ReviewParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.data_blocks: list[dict[str, Any]] = []
        self.external_dependencies: list[str] = []
        self._data_block: dict[str, Any] | None = None
        self._in_style = False
        self._style_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs}
        lower = tag.lower()
        source = values.get("src")
        if source and not source.startswith("data:"):
            self.external_dependencies.append(f"{lower} src={source}")
        if lower == "link" and values.get("href"):
            self.external_dependencies.append(f"link href={values['href']}")
        if lower == "script" and values.get("id") == "review-data":
            block = {"type": values.get("type"), "parts": []}
            self.data_blocks.append(block)
            self._data_block = block
        if lower == "style":
            self._in_style = True
            self._style_parts = []

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower == "script" and self._data_block is not None:
            self._data_block = None
        if lower == "style" and self._in_style:
            css = "".join(self._style_parts)
            if re.search(r"@import|url\(\s*['\"]?\s*(?:https?:|//)", css, re.IGNORECASE):
                self.external_dependencies.append("external stylesheet or font URL")
            self._in_style = False
            self._style_parts = []

    def handle_data(self, data: str) -> None:
        if self._data_block is not None:
            self._data_block["parts"].append(data)
        if self._in_style:
            self._style_parts.append(data)


def _parse_html(text: str) -> ReviewParser:
    parser = ReviewParser()
    parser.feed(text)
    parser.close()
    return parser


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label} must be a nonempty string.")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _string(value, label)
    if not ID_PATTERN.fullmatch(value):
        raise ReviewError(f"{label} has an invalid identifier.")
    return value


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReviewError(f"{label} must be an object.")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ReviewError(f"{label} must be an array.")
    return value


def _exact(
    value: dict[str, Any], fields: set[str], label: str,
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = fields - set(value)
    extra = set(value) - fields - optional
    if missing or extra:
        raise ReviewError(
            f"{label} fields must be exact (missing={sorted(missing)}, extra={sorted(extra)})."
        )


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReviewError(f"{label} must be a nonnegative integer.")
    return value


def _number(value: Any, label: str, nullable: bool = True) -> float | int | None:
    if value is None and nullable:
        return None
    if (
        isinstance(value, bool) or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ReviewError(f"{label} must be a finite number{' or null' if nullable else ''}.")
    return value


def _timestamp(value: Any, label: str) -> str:
    value = _string(value, label)
    if not value.endswith("Z"):
        raise ReviewError(f"{label} must be an RFC 3339 UTC timestamp ending in Z.")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ReviewError(f"{label} must be an RFC 3339 UTC timestamp.") from exc
    return value


def _digest(value: Any, label: str, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
        raise ReviewError(f"{label} must be a strict sha256 digest{' or null' if nullable else ''}.")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ReviewError(f"{label} contains non-finite JSON number {value}.")

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=reject_constant
        )
    except FileNotFoundError as exc:
        raise ReviewError(f"{label} not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"Cannot read {label} {path}: {exc}") from exc
    return _mapping(value, label)


def _canonical_relative(value: Any, label: str, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    value = _string(value, label)
    if value.startswith("/") or "\\" in value or "\x00" in value or ":" in value:
        raise ReviewError(f"{label} must be a portable relative path.")
    parts = value.split("/")
    if any(not part or part == "." for part in parts):
        raise ReviewError(f"{label} must be canonical.")
    first_normal = next((index for index, part in enumerate(parts) if part != ".."), len(parts))
    if first_normal == len(parts) or any(part == ".." for part in parts[first_normal:]):
        raise ReviewError(f"{label} may contain '..' only as a leading generated rebase.")
    return value


def _link_base(value: Any) -> str:
    value = _string(value, "benchmark_link_base")
    if value == ".":
        return value
    return _canonical_relative(value, "benchmark_link_base")


def _require_link(path: str | None, benchmark_dir: Path | None, label: str) -> None:
    if path is None or benchmark_dir is None:
        return
    target = (benchmark_dir / path).resolve()
    if not target.is_file():
        raise ReviewError(f"{label} does not resolve to a file: {target}")


def _validate_error(value: Any, label: str, nullable: bool = True) -> None:
    if value is None and nullable:
        return
    error = _mapping(value, label)
    _exact(error, {"code", "message"}, label)
    _identifier(error.get("code"), f"{label}.code")
    _string(error.get("message"), f"{label}.message")


def _validate_statistic(value: Any, label: str) -> None:
    stat = _mapping(value, label)
    _exact(
        stat, {"sample_count", "mean", "sample_stddev", "bootstrap_interval"}, label
    )
    count = _integer(stat.get("sample_count"), f"{label}.sample_count")
    mean = _number(stat.get("mean"), f"{label}.mean")
    deviation = _number(stat.get("sample_stddev"), f"{label}.sample_stddev")
    if deviation is not None and deviation < 0:
        raise ReviewError(f"{label}.sample_stddev must be nonnegative.")
    if count == 0 and mean is not None:
        raise ReviewError(f"{label}.mean must be null at zero samples.")
    if count > 0 and mean is None:
        raise ReviewError(f"{label}.mean must be present when samples exist.")
    if count < 2 and deviation is not None:
        raise ReviewError(f"{label}.sample_stddev must be null below two samples.")
    interval = stat.get("bootstrap_interval")
    if interval is not None:
        if count < 2:
            raise ReviewError(f"{label}.bootstrap_interval requires at least two samples.")
        interval = _mapping(interval, f"{label}.bootstrap_interval")
        _exact(interval, {"lower", "upper"}, f"{label}.bootstrap_interval")
        lower = _number(interval.get("lower"), f"{label}.bootstrap_interval.lower", False)
        upper = _number(interval.get("upper"), f"{label}.bootstrap_interval.upper", False)
        if lower > upper:
            raise ReviewError(f"{label}.bootstrap_interval bounds are reversed.")


def _rounded(value: float) -> float:
    return round(value, 6)


def _percentile(values: list[float], probability: float) -> float:
    position = (len(values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return values[lower_index]
    fraction = position - lower_index
    return values[lower_index] + fraction * (
        values[upper_index] - values[lower_index]
    )


def _expected_statistic(
    values: list[float | int], methods: dict[str, Any], rng: random.Random,
) -> dict[str, Any]:
    count = len(values)
    if not count:
        return {
            "sample_count": 0,
            "mean": None,
            "sample_stddev": None,
            "bootstrap_interval": None,
        }
    numeric = list(values)
    mean = _rounded(sum(numeric) / count)
    deviation = None
    interval = None
    if count >= 2:
        deviation = _rounded(statistics.stdev(numeric))
        samples = methods["bootstrap_samples"]
        if samples:
            means = sorted(
                sum(rng.choice(numeric) for _ in numeric) / count
                for _ in range(samples)
            )
            alpha = (1.0 - methods["confidence_level"]) / 2.0
            interval = {
                "lower": _rounded(_percentile(means, alpha)),
                "upper": _rounded(_percentile(means, 1.0 - alpha)),
            }
    return {
        "sample_count": count,
        "mean": mean,
        "sample_stddev": deviation,
        "bootstrap_interval": interval,
    }


def _assert_statistic(
    actual: dict[str, Any], values: list[float | int], label: str,
    methods: dict[str, Any], rng: random.Random,
) -> None:
    expected = _expected_statistic(values, methods, rng)
    for field in ("sample_count", "mean", "sample_stddev"):
        if actual.get(field) != expected[field]:
            raise ReviewError(
                f"{label}.{field} does not reproduce from visible observations "
                f"(expected {expected[field]!r})."
            )
    if actual.get("bootstrap_interval") != expected["bootstrap_interval"]:
        raise ReviewError(
            f"{label}.bootstrap_interval does not reproduce from the recorded "
            "seed, sample count, confidence level, and visible observations."
        )


def _validate_resources(value: Any, label: str) -> None:
    resources = _mapping(value, label)
    _exact(resources, set(RESOURCE_FIELDS), label)
    for field in RESOURCE_FIELDS:
        item = _mapping(resources[field], f"{label}.{field}")
        _exact(item, {"observed_count", "missing_count", "statistics"}, f"{label}.{field}")
        observed = _integer(item.get("observed_count"), f"{label}.{field}.observed_count")
        _integer(item.get("missing_count"), f"{label}.{field}.missing_count")
        _validate_statistic(item.get("statistics"), f"{label}.{field}.statistics")
        if item["statistics"]["sample_count"] != observed:
            raise ReviewError(f"{label}.{field} observed_count does not match statistics.")


def _validate_quality(value: Any, label: str) -> None:
    quality = _mapping(value, label)
    _exact(quality, {"included_count", "excluded_count", "statistics"}, label)
    included = _integer(quality.get("included_count"), f"{label}.included_count")
    _integer(quality.get("excluded_count"), f"{label}.excluded_count")
    _validate_statistic(quality.get("statistics"), f"{label}.statistics")
    if quality["statistics"]["sample_count"] != included:
        raise ReviewError(f"{label} included_count does not match statistics.")


def _validate_configuration(
    value: Any, label: str, with_runs: bool, benchmark_dir: Path | None,
    visible_runs: set[str], statuses: list[str], grading_statuses: list[str],
    scored: list[bool],
) -> tuple[str, str]:
    config = _mapping(value, label)
    fields = {
        "configuration_id", "role", "label", "skill_digest", "baseline_kind",
        "quality", "resources",
    }
    if with_runs:
        fields.add("runs")
    _exact(config, fields, label)
    config_id = _identifier(config.get("configuration_id"), f"{label}.configuration_id")
    role = config.get("role")
    if role not in {"candidate", "baseline"}:
        raise ReviewError(f"{label}.role is invalid.")
    _string(config.get("label"), f"{label}.label")
    if role == "candidate":
        _digest(config.get("skill_digest"), f"{label}.skill_digest")
        if config.get("baseline_kind") is not None:
            raise ReviewError("Candidate benchmark configuration baseline_kind must be null.")
    else:
        kind = config.get("baseline_kind")
        if kind not in {"no_skill", "old_snapshot"}:
            raise ReviewError("Baseline benchmark configuration has invalid baseline_kind.")
        _digest(config.get("skill_digest"), f"{label}.skill_digest", nullable=kind == "no_skill")
        if kind == "no_skill" and config.get("skill_digest") is not None:
            raise ReviewError("no_skill benchmark baseline must have null skill_digest.")
        if kind == "old_snapshot" and config.get("skill_digest") is None:
            raise ReviewError("old_snapshot benchmark baseline requires skill_digest.")
    _validate_quality(config.get("quality"), f"{label}.quality")
    _validate_resources(config.get("resources"), f"{label}.resources")
    if with_runs:
        runs = _array(config.get("runs"), f"{label}.runs")
        for raw_run in runs:
            run = _mapping(raw_run, "benchmark run")
            _exact(run, {
                "run_id", "pair_id", "run_manifest", "grading_manifest", "run_status",
                "grading_status", "run_error", "grading_error", "transcript_path",
                "artifacts", "criteria", "claims_checked",
                "evaluator_quality_warnings", "quality", "duration_seconds",
                "input_tokens", "output_tokens", "total_tokens",
            }, "benchmark run")
            run_id = _identifier(run.get("run_id"), "benchmark run_id")
            _identifier(run.get("pair_id"), "benchmark pair_id")
            if run_id in visible_runs:
                raise ReviewError(f"Duplicate visible run_id: {run_id}")
            visible_runs.add(run_id)
            run_manifest = _canonical_relative(run.get("run_manifest"), "run_manifest")
            grading_manifest = _canonical_relative(
                run.get("grading_manifest"), "grading_manifest", nullable=True
            )
            transcript = _canonical_relative(
                run.get("transcript_path"), "transcript_path", nullable=True
            )
            _require_link(run_manifest, benchmark_dir, "run_manifest")
            _require_link(grading_manifest, benchmark_dir, "grading_manifest")
            _require_link(transcript, benchmark_dir, "transcript_path")
            run_status = run.get("run_status")
            if run_status not in RUN_STATUSES:
                raise ReviewError(f"Visible run {run_id} has invalid run_status.")
            grading_status = run.get("grading_status")
            if grading_status is not None and grading_status not in GRADING_STATUSES:
                raise ReviewError(f"Visible run {run_id} has invalid grading_status.")
            if run_status != "completed" and grading_status == "completed":
                raise ReviewError("A non-completed run cannot expose completed grading.")
            _validate_error(run.get("run_error"), "run_error")
            _validate_error(run.get("grading_error"), "grading_error")
            if (run_status == "completed") != (run.get("run_error") is None):
                raise ReviewError("run_error does not match run_status.")
            if run_status == "completed" and transcript is None:
                raise ReviewError("A completed run requires transcript_path.")
            if grading_status is None:
                if grading_manifest is not None or run.get("grading_error") is not None:
                    raise ReviewError("Missing grading must have null manifest and error.")
            elif grading_manifest is None:
                raise ReviewError("A grading status requires grading_manifest.")
            elif (grading_status == "completed") != (run.get("grading_error") is None):
                raise ReviewError("grading_error does not match grading_status.")
            for raw_artifact in _array(run.get("artifacts"), f"run {run_id} artifacts"):
                artifact = _mapping(raw_artifact, "benchmark artifact")
                _exact(artifact, {"path", "sha256"}, "benchmark artifact", {"media_type"})
                artifact_path = _canonical_relative(artifact.get("path"), "artifact path")
                _require_link(artifact_path, benchmark_dir, "artifact path")
                _digest(artifact.get("sha256"), "artifact sha256")
                if "media_type" in artifact:
                    _string(artifact["media_type"], "artifact media_type")
            for raw_criterion in _array(run.get("criteria"), f"run {run_id} criteria"):
                criterion = _mapping(raw_criterion, "graded criterion")
                _exact(criterion, {"criterion_id", "verdict", "evidence"}, "graded criterion")
                _identifier(criterion.get("criterion_id"), "graded criterion_id")
                if criterion.get("verdict") not in {"pass", "fail", "invalid"}:
                    raise ReviewError("graded criterion verdict is invalid.")
                for evidence in _array(criterion.get("evidence"), "criterion evidence"):
                    _string(evidence, "criterion evidence reference")
            for raw_claim in _array(run.get("claims_checked"), f"run {run_id} claims_checked"):
                claim = _mapping(raw_claim, "claim checked")
                _exact(claim, {"claim", "evaluation", "evidence"}, "claim checked")
                _string(claim.get("claim"), "claim text")
                if claim.get("evaluation") not in {"verified", "contradicted", "unverifiable"}:
                    raise ReviewError("claim evaluation is invalid.")
                for evidence in _array(claim.get("evidence"), "claim evidence"):
                    _string(evidence, "claim evidence reference")
            for raw_warning in _array(
                run.get("evaluator_quality_warnings"), f"run {run_id} evaluator warnings"
            ):
                warning = _mapping(raw_warning, "evaluator warning")
                _exact(
                    warning, {"code", "message", "criterion_id", "evidence"},
                    "evaluator warning",
                )
                _identifier(warning.get("code"), "evaluator warning code")
                _string(warning.get("message"), "evaluator warning message")
                if warning.get("criterion_id") is not None:
                    _identifier(warning["criterion_id"], "evaluator warning criterion_id")
                for evidence in _array(warning.get("evidence"), "evaluator warning evidence"):
                    _string(evidence, "evaluator warning evidence reference")
            run_quality = _mapping(run.get("quality"), "run quality")
            _exact(run_quality, {"passed", "failed", "invalid", "total", "score"}, "run quality")
            for field in ("passed", "failed", "invalid", "total"):
                _integer(run_quality.get(field), f"run quality.{field}")
            if run_quality["passed"] + run_quality["failed"] + run_quality["invalid"] != run_quality["total"]:
                raise ReviewError("run quality counts do not sum to total.")
            verdict_counts = {
                verdict: sum(criterion["verdict"] == verdict for criterion in run["criteria"])
                for verdict in ("pass", "fail", "invalid")
            }
            if (
                run_quality["passed"] != verdict_counts["pass"]
                or run_quality["failed"] != verdict_counts["fail"]
                or run_quality["invalid"] != verdict_counts["invalid"]
                or run_quality["total"] != len(run["criteria"])
            ):
                raise ReviewError("run quality counts do not reproduce from visible criteria.")
            score = _number(run_quality.get("score"), "run quality.score")
            if score is not None and not 0 <= score <= 1:
                raise ReviewError("run quality.score must be between zero and one.")
            if score is not None and (run_status != "completed" or grading_status != "completed"):
                raise ReviewError("Only completed execution and grading may have a quality score.")
            denominator = run_quality["passed"] + run_quality["failed"]
            expected_score = (
                _rounded(run_quality["passed"] / denominator)
                if run_status == "completed" and grading_status == "completed" and denominator
                else None
            )
            if score != expected_score:
                raise ReviewError(
                    "run quality.score does not reproduce from visible pass/fail verdicts."
                )
            _number(run.get("duration_seconds"), "duration_seconds")
            for field in ("input_tokens", "output_tokens", "total_tokens"):
                token = run.get(field)
                if token is not None:
                    _integer(token, field)
            statuses.append(run_status)
            grading_statuses.append("missing" if grading_status is None else grading_status)
            scored.append(score is not None)
        if config["quality"]["included_count"] + config["quality"]["excluded_count"] != len(runs):
            raise ReviewError(f"{label}.quality counts do not match runs.")
        for field in RESOURCE_FIELDS:
            resource = config["resources"][field]
            if resource["observed_count"] + resource["missing_count"] != len(runs):
                raise ReviewError(f"{label}.{field} counts do not match runs.")
    return config_id, role


def _validate_derived_statistics(benchmark: dict[str, Any]) -> None:
    """Replay the aggregator's documented statistic stream from visible records."""
    methods = benchmark["methods"]
    rng = random.Random(methods["bootstrap_seed"])
    all_runs: dict[str, list[dict[str, Any]]] = {
        item["configuration_id"]: []
        for item in benchmark["aggregates"]["configurations"]
    }
    all_quality_deltas: list[float | int] = []
    all_excluded_pairs = 0
    resource_deltas: dict[str, list[float | int]] = {
        field: [] for field in RESOURCE_FIELDS
    }

    for case in benchmark["cases"]:
        runs_by_id: dict[str, dict[str, Any]] = {}
        for arm in case["configurations"]:
            runs = arm["runs"]
            all_runs[arm["configuration_id"]].extend(runs)
            for run in runs:
                runs_by_id[run["run_id"]] = run

            scores = [
                run["quality"]["score"]
                for run in runs
                if run["quality"]["score"] is not None
            ]
            if arm["quality"]["included_count"] != len(scores):
                raise ReviewError("case configuration quality included_count is not reproducible.")
            if arm["quality"]["excluded_count"] != len(runs) - len(scores):
                raise ReviewError("case configuration quality excluded_count is not reproducible.")
            _assert_statistic(
                arm["quality"]["statistics"], scores,
                f"case {case['case_id']} configuration {arm['configuration_id']} quality.statistics",
                methods, rng,
            )
            for field in RESOURCE_FIELDS:
                values = [run[field] for run in runs if run[field] is not None]
                resource = arm["resources"][field]
                if resource["observed_count"] != len(values):
                    raise ReviewError(
                        f"case configuration {field} observed_count is not reproducible."
                    )
                if resource["missing_count"] != len(runs) - len(values):
                    raise ReviewError(
                        f"case configuration {field} missing_count is not reproducible."
                    )
                _assert_statistic(
                    resource["statistics"], values,
                    f"case {case['case_id']} configuration {arm['configuration_id']} "
                    f"resources.{field}.statistics",
                    methods, rng,
                )

        case_deltas: list[float | int] = []
        case_excluded = 0
        for pair in case["pairs"]:
            if pair["status"] == "included":
                case_deltas.append(pair["quality_delta"])
                all_quality_deltas.append(pair["quality_delta"])
            else:
                case_excluded += 1
                all_excluded_pairs += 1
            candidate = runs_by_id.get(pair["candidate_run_id"])
            baseline = runs_by_id.get(pair["baseline_run_id"])
            if candidate is not None and baseline is not None:
                for field in RESOURCE_FIELDS:
                    if candidate[field] is not None and baseline[field] is not None:
                        resource_deltas[field].append(candidate[field] - baseline[field])
        paired = case["paired_quality"]
        if paired["included_pair_count"] != len(case_deltas):
            raise ReviewError("case paired_quality included_pair_count is not reproducible.")
        if paired["excluded_pair_count"] != case_excluded:
            raise ReviewError("case paired_quality excluded_pair_count is not reproducible.")
        _assert_statistic(
            paired["statistics"], case_deltas,
            f"case {case['case_id']} paired_quality.statistics", methods, rng,
        )

    for aggregate in benchmark["aggregates"]["configurations"]:
        runs = all_runs[aggregate["configuration_id"]]
        scores = [
            run["quality"]["score"]
            for run in runs
            if run["quality"]["score"] is not None
        ]
        if aggregate["quality"]["included_count"] != len(scores):
            raise ReviewError("aggregate quality included_count is not reproducible.")
        if aggregate["quality"]["excluded_count"] != len(runs) - len(scores):
            raise ReviewError("aggregate quality excluded_count is not reproducible.")
        _assert_statistic(
            aggregate["quality"]["statistics"], scores,
            f"aggregate configuration {aggregate['configuration_id']} quality.statistics",
            methods, rng,
        )
        for field in RESOURCE_FIELDS:
            values = [run[field] for run in runs if run[field] is not None]
            resource = aggregate["resources"][field]
            if resource["observed_count"] != len(values):
                raise ReviewError(f"aggregate {field} observed_count is not reproducible.")
            if resource["missing_count"] != len(runs) - len(values):
                raise ReviewError(f"aggregate {field} missing_count is not reproducible.")
            _assert_statistic(
                resource["statistics"], values,
                f"aggregate configuration {aggregate['configuration_id']} "
                f"resources.{field}.statistics",
                methods, rng,
            )

    aggregate_paired = benchmark["aggregates"]["paired_quality"]
    if aggregate_paired["included_pair_count"] != len(all_quality_deltas):
        raise ReviewError("aggregate paired_quality included_pair_count is not reproducible.")
    if aggregate_paired["excluded_pair_count"] != all_excluded_pairs:
        raise ReviewError("aggregate paired_quality excluded_pair_count is not reproducible.")
    _assert_statistic(
        aggregate_paired["statistics"], all_quality_deltas,
        "aggregate paired_quality.statistics", methods, rng,
    )

    quality_cost = benchmark["quality_cost"]
    _assert_statistic(
        quality_cost["quality_delta"], all_quality_deltas,
        "quality_cost.quality_delta", methods, rng,
    )
    for field in RESOURCE_FIELDS:
        _assert_statistic(
            quality_cost[f"{field}_delta"], resource_deltas[field],
            f"quality_cost.{field}_delta", methods, rng,
        )


def validate_benchmark(
    benchmark: dict[str, Any], benchmark_dir: Path | None = None,
) -> tuple[set[str], dict[str, str]]:
    if benchmark.get("schema_version") != SCHEMA_VERSION:
        raise ReviewError(f"benchmark schema_version must be {SCHEMA_VERSION}.")
    _exact(benchmark, TOP_LEVEL_FIELDS, "benchmark.json")
    _identifier(benchmark.get("benchmark_id"), "benchmark_id")
    _identifier(benchmark.get("suite_id"), "benchmark suite_id")
    _timestamp(benchmark.get("generated_at"), "benchmark generated_at")
    methods = _mapping(benchmark.get("methods"), "benchmark methods")
    _exact(methods, {
        "quality_score", "paired_delta", "dispersion", "interval", "bootstrap_seed",
        "bootstrap_samples", "confidence_level", "significance_claim",
    }, "benchmark methods")
    method_values = {
        "quality_score": "pass/(pass+fail); invalid excluded",
        "paired_delta": "candidate-minus-baseline for matching case_id and pair_id",
        "dispersion": "sample_standard_deviation",
        "interval": "seeded_percentile_bootstrap_of_mean",
    }
    for field, expected in method_values.items():
        if methods.get(field) != expected:
            raise ReviewError(f"benchmark methods.{field} does not match version-1.0 semantics.")
    if isinstance(methods.get("bootstrap_seed"), bool) or not isinstance(methods.get("bootstrap_seed"), int):
        raise ReviewError("bootstrap_seed must be an integer.")
    _integer(methods.get("bootstrap_samples"), "bootstrap_samples")
    confidence = _number(methods.get("confidence_level"), "confidence_level", False)
    if not 0 < confidence < 1:
        raise ReviewError("confidence_level must be between zero and one.")
    if methods.get("significance_claim") is not False:
        raise ReviewError("significance_claim must be false.")

    count_fields = {
        "indexed_runs", "completed_runs", "executor_error_runs", "invalid_runs",
        "grading_completed_runs", "grading_error_runs", "grading_invalid_runs",
        "grading_missing_runs", "quality_included_runs", "quality_excluded_runs",
    }
    counts = _mapping(benchmark.get("counts"), "benchmark counts")
    _exact(counts, count_fields, "benchmark counts")
    for field in count_fields:
        _integer(counts.get(field), f"benchmark counts.{field}")

    visible_runs: set[str] = set()
    statuses: list[str] = []
    grading_statuses: list[str] = []
    scored: list[bool] = []
    canonical_configs: dict[str, str] = {}
    case_ids: set[str] = set()
    for raw_case in _array(benchmark.get("cases"), "benchmark cases"):
        case = _mapping(raw_case, "benchmark case")
        _exact(
            case,
            {"case_id", "prompt", "criteria", "configurations", "pairs", "paired_quality"},
            "benchmark case",
        )
        case_id = _identifier(case.get("case_id"), "case_id")
        if case_id in case_ids:
            raise ReviewError(f"Duplicate benchmark case_id: {case_id}")
        case_ids.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ReviewError("case prompt must be a nonempty string.")
        criterion_ids: set[str] = set()
        for raw_criterion in _array(case.get("criteria"), "case criteria"):
            criterion = _mapping(raw_criterion, "case criterion")
            _exact(criterion, {"id", "text", "kind"}, "case criterion")
            criterion_id = _identifier(criterion.get("id"), "case criterion id")
            if criterion_id in criterion_ids:
                raise ReviewError(f"Duplicate case criterion_id: {criterion_id}")
            criterion_ids.add(criterion_id)
            _string(criterion.get("text"), "case criterion text")
            if criterion.get("kind") not in {"deterministic", "model_judge", "human"}:
                raise ReviewError("case criterion kind is invalid.")
        arms = _array(case.get("configurations"), "case configurations")
        if len(arms) != 2:
            raise ReviewError("Each benchmark case must contain candidate and baseline configurations.")
        case_configs: dict[str, str] = {}
        for index, arm in enumerate(arms):
            config_id, role = _validate_configuration(
                arm, f"case configuration {index}", True, benchmark_dir,
                visible_runs, statuses, grading_statuses, scored,
            )
            if config_id in case_configs or role in case_configs.values():
                raise ReviewError("Case configurations must be unique by id and role.")
            case_configs[config_id] = role
            if config_id in canonical_configs and canonical_configs[config_id] != role:
                raise ReviewError("Configuration role changes between cases.")
            canonical_configs[config_id] = role
        if set(case_configs.values()) != {"candidate", "baseline"}:
            raise ReviewError("Each case must contain one candidate and one baseline.")
        if [arm["role"] for arm in arms] != ["candidate", "baseline"]:
            raise ReviewError("Case configurations must be ordered candidate then baseline.")
        case_runs: dict[str, tuple[str, str, float | None]] = {}
        for arm in arms:
            for run in arm["runs"]:
                for criterion in run["criteria"]:
                    if criterion["criterion_id"] not in criterion_ids:
                        raise ReviewError("Visible run grades a criterion outside its case.")
                for warning in run["evaluator_quality_warnings"]:
                    if warning["criterion_id"] is not None and warning["criterion_id"] not in criterion_ids:
                        raise ReviewError("Evaluator warning names a criterion outside its case.")
                case_runs[run["run_id"]] = (
                    arm["role"], run["pair_id"], run["quality"]["score"]
                )
        seen_pair_ids: set[str] = set()
        paired_run_ids: set[str] = set()
        included_pairs = 0
        for raw_pair in _array(case.get("pairs"), "case pairs"):
            pair = _mapping(raw_pair, "case pair")
            _exact(pair, {
                "pair_id", "candidate_run_id", "baseline_run_id", "status",
                "exclusion_reason", "candidate_score", "baseline_score", "quality_delta",
            }, "case pair")
            pair_id = _identifier(pair.get("pair_id"), "case pair_id")
            if pair_id in seen_pair_ids:
                raise ReviewError(f"Duplicate case pair_id: {pair_id}")
            seen_pair_ids.add(pair_id)
            for field, expected_role in (
                ("candidate_run_id", "candidate"), ("baseline_run_id", "baseline")
            ):
                if pair.get(field) is not None:
                    _identifier(pair[field], f"case pair {field}")
                    if pair[field] not in case_runs:
                        raise ReviewError(f"case pair {field} is not a run in this case.")
                    role, run_pair_id, score = case_runs[pair[field]]
                    if role != expected_role or run_pair_id != pair_id:
                        raise ReviewError(f"case pair {field} has the wrong role or pair_id.")
                    paired_run_ids.add(pair[field])
                    score_field = "candidate_score" if expected_role == "candidate" else "baseline_score"
                    if pair.get(score_field) != score:
                        raise ReviewError(f"case pair {score_field} does not match its visible run.")
            if pair.get("status") not in {"included", "excluded"}:
                raise ReviewError("case pair status is invalid.")
            for field in ("candidate_score", "baseline_score", "quality_delta"):
                number = _number(pair.get(field), f"case pair {field}")
                if field != "quality_delta" and number is not None and not 0 <= number <= 1:
                    raise ReviewError(f"case pair {field} must be between zero and one.")
            if pair["status"] == "included":
                included_pairs += 1
                if pair.get("exclusion_reason") is not None:
                    raise ReviewError("Included case pair must have null exclusion_reason.")
                if any(pair.get(field) is None for field in (
                    "candidate_run_id", "baseline_run_id", "candidate_score",
                    "baseline_score", "quality_delta",
                )):
                    raise ReviewError("Included case pair must have both arms and scores.")
                if abs(
                    pair["candidate_score"] - pair["baseline_score"] - pair["quality_delta"]
                ) > 0.000001:
                    raise ReviewError("Included case pair quality_delta has the wrong direction or value.")
            else:
                _string(pair.get("exclusion_reason"), "excluded pair reason")
                if pair.get("quality_delta") is not None:
                    raise ReviewError("Excluded case pair must have null quality_delta.")
        if paired_run_ids != set(case_runs):
            raise ReviewError("Every visible run must appear in exactly one case pair record.")
        paired = _mapping(case.get("paired_quality"), "case paired_quality")
        _exact(paired, {"included_pair_count", "excluded_pair_count", "statistics"}, "case paired_quality")
        included = _integer(paired.get("included_pair_count"), "included_pair_count")
        _integer(paired.get("excluded_pair_count"), "excluded_pair_count")
        _validate_statistic(paired.get("statistics"), "case paired_quality.statistics")
        if paired["statistics"]["sample_count"] != included:
            raise ReviewError("case paired_quality count does not match statistics.")
        if included != included_pairs or paired["excluded_pair_count"] != len(seen_pair_ids) - included_pairs:
            raise ReviewError("case paired_quality counts do not match pair records.")

    aggregates = _mapping(benchmark.get("aggregates"), "benchmark aggregates")
    _exact(aggregates, {"configurations", "paired_quality"}, "benchmark aggregates")
    aggregate_configs: dict[str, str] = {}
    empty_statuses: list[str] = []
    empty_grading: list[str] = []
    empty_scored: list[bool] = []
    aggregate_items = _array(aggregates.get("configurations"), "aggregate configurations")
    if len(aggregate_items) != 2:
        raise ReviewError("Aggregate configurations must contain exactly two records.")
    for index, item in enumerate(aggregate_items):
        config_id, role = _validate_configuration(
            item, f"aggregate configuration {index}", False, None, set(),
            empty_statuses, empty_grading, empty_scored,
        )
        if config_id in aggregate_configs or role in aggregate_configs.values():
            raise ReviewError("Aggregate configurations must be unique by id and role.")
        aggregate_configs[config_id] = role
    if [item["role"] for item in aggregate_items] != ["candidate", "baseline"]:
        raise ReviewError("Aggregate configurations must be ordered candidate then baseline.")
    if aggregate_configs != canonical_configs:
        raise ReviewError("Aggregate configurations do not match case configurations.")
    paired = _mapping(aggregates.get("paired_quality"), "aggregate paired_quality")
    _exact(paired, {"included_pair_count", "excluded_pair_count", "statistics"}, "aggregate paired_quality")
    included = _integer(paired.get("included_pair_count"), "aggregate included_pair_count")
    _integer(paired.get("excluded_pair_count"), "aggregate excluded_pair_count")
    _validate_statistic(paired.get("statistics"), "aggregate paired_quality.statistics")
    if paired["statistics"]["sample_count"] != included:
        raise ReviewError("aggregate paired_quality count does not match statistics.")

    findings = _mapping(benchmark.get("findings"), "benchmark findings")
    _exact(findings, {"regressions", "flakiness", "non_discriminating_criteria"}, "benchmark findings")
    for raw in _array(findings.get("regressions"), "regressions"):
        item = _mapping(raw, "regression")
        _exact(item, {"case_id", "criterion_id", "pair_ids", "delta", "evidence"}, "regression")
        _identifier(item.get("case_id"), "regression case_id")
        if item.get("criterion_id") is not None:
            _identifier(item["criterion_id"], "regression criterion_id")
        _number(item.get("delta"), "regression delta", False)
        for pair_id in _array(item.get("pair_ids"), "regression pair_ids"):
            _identifier(pair_id, "regression pair_id")
        for evidence in _array(item.get("evidence"), "regression evidence"):
            _string(evidence, "regression evidence reference")
    for raw in _array(findings.get("flakiness"), "flakiness"):
        item = _mapping(raw, "flakiness finding")
        _exact(item, {"case_id", "configuration_id", "criterion_id", "run_ids", "observed_verdicts"}, "flakiness finding")
        for field in ("case_id", "configuration_id", "criterion_id"):
            _identifier(item.get(field), f"flakiness {field}")
        for run_id in _array(item.get("run_ids"), "flakiness run_ids"):
            _identifier(run_id, "flakiness run_id")
        if set(_array(item.get("observed_verdicts"), "observed_verdicts")) != {"pass", "fail"}:
            raise ReviewError("Flakiness observed_verdicts must contain pass and fail.")
    for raw in _array(findings.get("non_discriminating_criteria"), "non-discriminating findings"):
        item = _mapping(raw, "non-discriminating finding")
        _exact(item, {"case_id", "criterion_id", "reason", "run_ids"}, "non-discriminating finding")
        _identifier(item.get("case_id"), "non-discriminating case_id")
        _identifier(item.get("criterion_id"), "non-discriminating criterion_id")
        _string(item.get("reason"), "non-discriminating reason")
        for run_id in _array(item.get("run_ids"), "non-discriminating run_ids"):
            _identifier(run_id, "non-discriminating run_id")

    quality_cost = _mapping(benchmark.get("quality_cost"), "benchmark quality_cost")
    _exact(quality_cost, {
        "candidate_configuration_id", "baseline_configuration_id", "quality_delta",
        "duration_seconds_delta", "input_tokens_delta", "output_tokens_delta",
        "total_tokens_delta",
    }, "benchmark quality_cost")
    candidate = _identifier(quality_cost.get("candidate_configuration_id"), "candidate_configuration_id")
    baseline = _identifier(quality_cost.get("baseline_configuration_id"), "baseline_configuration_id")
    if aggregate_configs.get(candidate) != "candidate" or aggregate_configs.get(baseline) != "baseline":
        raise ReviewError("quality_cost configuration IDs do not match aggregate roles.")
    for field in (
        "quality_delta", "duration_seconds_delta", "input_tokens_delta",
        "output_tokens_delta", "total_tokens_delta",
    ):
        _validate_statistic(quality_cost.get(field), f"quality_cost.{field}")

    for raw_note in _array(benchmark.get("analyzer_notes"), "benchmark analyzer_notes"):
        note = _mapping(raw_note, "analyzer note")
        _exact(note, {"note_id", "text", "evidence"}, "analyzer note")
        _identifier(note.get("note_id"), "analyzer note_id")
        _string(note.get("text"), "analyzer note text")
        evidence_items = _array(note.get("evidence"), "analyzer note evidence")
        if not evidence_items:
            raise ReviewError("Analyzer notes require evidence.")
        for raw_evidence in evidence_items:
            evidence = _mapping(raw_evidence, "analyzer evidence")
            _exact(evidence, {"case_id", "run_id", "pair_id", "criterion_id", "artifact_path"}, "analyzer evidence")
            _identifier(evidence.get("case_id"), "analyzer evidence case_id")
            for field in ("run_id", "pair_id", "criterion_id"):
                if evidence.get(field) is not None:
                    _identifier(evidence[field], f"analyzer evidence {field}")
            if evidence.get("artifact_path") is not None:
                artifact_path = _canonical_relative(evidence["artifact_path"], "analyzer artifact_path")
                _require_link(artifact_path, benchmark_dir, "analyzer artifact_path")

    if counts["indexed_runs"] != len(statuses):
        raise ReviewError("indexed_runs does not match visible runs.")
    if counts["completed_runs"] != statuses.count("completed"):
        raise ReviewError("completed_runs does not match visible runs.")
    if counts["executor_error_runs"] != statuses.count("executor_error"):
        raise ReviewError("executor_error_runs does not match visible runs.")
    if counts["invalid_runs"] != statuses.count("invalid"):
        raise ReviewError("invalid_runs does not match visible runs.")
    if counts["grading_completed_runs"] != grading_statuses.count("completed"):
        raise ReviewError("grading_completed_runs does not match visible runs.")
    if counts["grading_error_runs"] != grading_statuses.count("grading_error"):
        raise ReviewError("grading_error_runs does not match visible runs.")
    if counts["grading_invalid_runs"] != grading_statuses.count("invalid"):
        raise ReviewError("grading_invalid_runs does not match visible runs.")
    if counts["grading_missing_runs"] != grading_statuses.count("missing"):
        raise ReviewError("grading_missing_runs does not match visible runs.")
    if counts["quality_included_runs"] != sum(scored):
        raise ReviewError("quality_included_runs does not match visible scores.")
    if counts["quality_excluded_runs"] != len(scored) - sum(scored):
        raise ReviewError("quality_excluded_runs does not match visible scores.")
    _validate_derived_statistics(benchmark)
    return visible_runs, aggregate_configs


def _pair_keys(benchmark: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        (case["case_id"], pair["pair_id"])
        for case in benchmark["cases"]
        for pair in case["pairs"]
    ]


def _counterbalanced_assignments(
    benchmark: dict[str, Any], config_roles: dict[str, str],
) -> list[dict[str, str]]:
    """Return a stable, pair-scoped, near-exactly balanced A/B presentation."""
    keys = _pair_keys(benchmark)
    config_ids = sorted(config_roles)
    namespace = (
        f"{benchmark['suite_id']}\0{benchmark['benchmark_id']}\0"
        "sha256-counterbalanced-case-pair-v1"
    )
    ranked = sorted(
        keys,
        key=lambda key: hashlib.sha256(
            f"{namespace}\0{key[0]}\0{key[1]}".encode("utf-8")
        ).digest(),
    )
    start = hashlib.sha256(f"{namespace}\0start".encode("utf-8")).digest()[0] & 1
    by_key: dict[tuple[str, str], dict[str, str]] = {}
    for index, key in enumerate(ranked):
        choice = start ^ (index & 1)
        by_key[key] = {
            "case_id": key[0],
            "pair_id": key[1],
            "A": config_ids[choice],
            "B": config_ids[1 - choice],
        }
    return [by_key[key] for key in keys]


def validate_feedback(
    feedback: dict[str, Any], benchmark: dict[str, Any], visible_runs: set[str],
    config_roles: dict[str, str],
) -> None:
    if feedback.get("schema_version") != SCHEMA_VERSION:
        raise ReviewError(f"feedback schema_version must be {SCHEMA_VERSION}.")
    _exact(
        feedback,
        {"schema_version", "suite_id", "reviewer", "timestamp", "blind_mapping", "reviews"},
        "feedback.json",
    )
    if feedback.get("suite_id") != benchmark["suite_id"]:
        raise ReviewError("feedback suite_id does not match benchmark.")
    reviewer = _mapping(feedback.get("reviewer"), "feedback reviewer")
    _exact(reviewer, {"name", "metadata"}, "feedback reviewer")
    _string(reviewer.get("name"), "reviewer name")
    _mapping(reviewer.get("metadata"), "reviewer metadata")
    _timestamp(feedback.get("timestamp"), "feedback timestamp")
    mapping = _mapping(feedback.get("blind_mapping"), "blind_mapping")
    _exact(mapping, {"scope", "method", "assignments"}, "blind_mapping")
    if mapping.get("scope") != "case_pair":
        raise ReviewError("blind_mapping.scope must be case_pair.")
    if mapping.get("method") not in {
        "recorded_random_per_pair_v1", "sha256_counterbalanced_case_pair_v1",
    }:
        raise ReviewError("blind_mapping.method is not supported by version 1.0.")
    assignment_keys: set[tuple[str, str]] = set()
    assignments: list[dict[str, str]] = []
    for raw_assignment in _array(mapping.get("assignments"), "blind_mapping assignments"):
        assignment = _mapping(raw_assignment, "blind mapping assignment")
        _exact(assignment, {"case_id", "pair_id", "A", "B"}, "blind mapping assignment")
        case_id = _identifier(assignment.get("case_id"), "blind mapping case_id")
        pair_id = _identifier(assignment.get("pair_id"), "blind mapping pair_id")
        key = (case_id, pair_id)
        if key in assignment_keys:
            raise ReviewError(f"Duplicate blind mapping assignment: {case_id}/{pair_id}")
        assignment_keys.add(key)
        if {assignment.get("A"), assignment.get("B")} != set(config_roles):
            raise ReviewError("Each blind mapping assignment must map A/B to both configurations.")
        assignments.append(assignment)
    expected_keys = set(_pair_keys(benchmark))
    if assignment_keys != expected_keys:
        raise ReviewError("blind_mapping must contain exactly one assignment per visible pair.")
    if mapping["method"] == "sha256_counterbalanced_case_pair_v1":
        if assignments != _counterbalanced_assignments(benchmark, config_roles):
            raise ReviewError("Counterbalanced blind mapping does not reproduce from benchmark identity.")

    review_ids: set[str] = set()
    for raw_review in _array(feedback.get("reviews"), "feedback reviews"):
        review = _mapping(raw_review, "feedback review")
        status = review.get("status")
        required = {"run_id", "status"} if status == "unvisited" else {"run_id", "status", "text"}
        _exact(review, required, "feedback review")
        run_id = _identifier(review.get("run_id"), "feedback run_id")
        if run_id in review_ids:
            raise ReviewError(f"Duplicate feedback run_id: {run_id}")
        review_ids.add(run_id)
        if status not in REVIEW_STATUSES:
            raise ReviewError(f"Review {run_id} has invalid status.")
        if status != "unvisited":
            text = review.get("text")
            if not isinstance(text, str):
                raise ReviewError("Visited reviews must contain text.")
            if status == "changes_requested" and not text.strip():
                raise ReviewError("changes_requested reviews require nonempty text.")
    if review_ids != visible_runs:
        missing = sorted(visible_runs - review_ids)
        extra = sorted(review_ids - visible_runs)
        raise ReviewError(
            f"feedback must cover every visible run (missing={missing}, extra={extra})."
        )


def _template_data(text: str) -> None:
    if text.count(SENTINEL) != 1:
        raise ReviewError("Template must contain exactly one review-data sentinel.")
    parser = _parse_html(text)
    if parser.external_dependencies:
        raise ReviewError(
            "Template contains external dependencies: " + ", ".join(parser.external_dependencies)
        )
    if len(parser.data_blocks) != 1:
        raise ReviewError("Template must contain exactly one script element with id review-data.")
    block = parser.data_blocks[0]
    if block["type"] != "application/json":
        raise ReviewError("review-data script type must be application/json.")
    data = "".join(block["parts"])
    if data.count(SENTINEL) != 1:
        raise ReviewError("The sentinel must occur inside the review-data element.")


def check_template(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReviewError(f"Cannot read viewer template {path}: {exc}") from exc
    _template_data(text)


def _extract_output(text: str, output_path: Path | None = None) -> dict[str, Any]:
    if SENTINEL in text:
        raise ReviewError("Rendered output still contains the template sentinel.")
    parser = _parse_html(text)
    if parser.external_dependencies:
        raise ReviewError(
            "Rendered output contains external dependencies: " + ", ".join(parser.external_dependencies)
        )
    if len(parser.data_blocks) != 1:
        raise ReviewError("Rendered output must contain exactly one review-data element.")
    block = parser.data_blocks[0]
    if block["type"] != "application/json":
        raise ReviewError("Rendered review-data type must be application/json.")
    raw = "".join(block["parts"]).strip()
    try:
        embedded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReviewError(f"Rendered review-data is invalid JSON: {exc}") from exc
    embedded = _mapping(embedded, "embedded review data")
    _exact(
        embedded,
        {"schema_version", "benchmark", "feedback", "benchmark_link_base"},
        "embedded review data",
    )
    if embedded.get("schema_version") != SCHEMA_VERSION:
        raise ReviewError(f"embedded schema_version must be {SCHEMA_VERSION}.")
    link_base = _link_base(embedded.get("benchmark_link_base"))
    benchmark_dir = None
    if output_path is not None:
        benchmark_dir = (output_path.parent / link_base).resolve()
    benchmark = _mapping(embedded.get("benchmark"), "embedded benchmark")
    visible, configs = validate_benchmark(benchmark, benchmark_dir)
    feedback = _mapping(embedded.get("feedback"), "embedded feedback")
    validate_feedback(feedback, benchmark, visible, configs)
    return embedded


def check_output(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReviewError(f"Cannot read rendered review {path}: {exc}") from exc
    return _extract_output(text, path.resolve())


def _safe_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return (
        encoded.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _default_feedback(
    benchmark: dict[str, Any], visible_runs: set[str], config_roles: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "suite_id": benchmark["suite_id"],
        "reviewer": {
            "name": "Independent reviewer",
            "metadata": {
                "blind_mapping_method": "sha256_counterbalanced_case_pair_v1",
            },
        },
        "timestamp": benchmark["generated_at"],
        "blind_mapping": {
            "scope": "case_pair",
            "method": "sha256_counterbalanced_case_pair_v1",
            "assignments": _counterbalanced_assignments(benchmark, config_roles),
        },
        "reviews": [
            {"run_id": run_id, "status": "unvisited"}
            for run_id in sorted(visible_runs)
        ],
    }


def render(
    benchmark_path: Path, viewer_path: Path, output_path: Path,
    feedback_path: Path | None = None,
) -> dict[str, Any]:
    benchmark_path = benchmark_path.resolve()
    viewer_path = viewer_path.resolve()
    output_path = output_path.resolve()
    check_template(viewer_path)
    benchmark = _load_json(benchmark_path, "benchmark.json")
    visible, configs = validate_benchmark(benchmark, benchmark_path.parent)
    if feedback_path is None:
        feedback = _default_feedback(benchmark, visible, configs)
    else:
        feedback = _load_json(feedback_path.resolve(), "feedback.json")
    validate_feedback(feedback, benchmark, visible, configs)
    link_base = os.path.relpath(benchmark_path.parent, output_path.parent).replace(os.sep, "/")
    _link_base(link_base)
    embedded = {
        "schema_version": SCHEMA_VERSION,
        "benchmark": benchmark,
        "feedback": feedback,
        "benchmark_link_base": link_base,
    }
    template = viewer_path.read_text(encoding="utf-8")
    rendered = template.replace(SENTINEL, _safe_json(embedded))
    if output_path == viewer_path:
        raise ReviewError("Output path must not overwrite the viewer template.")
    if output_path == benchmark_path:
        raise ReviewError("Output path must not overwrite benchmark.json.")
    _atomic_text(output_path, rendered)
    return embedded


def _empty_stat() -> dict[str, Any]:
    return {
        "sample_count": 0, "mean": None, "sample_stddev": None,
        "bootstrap_interval": None,
    }


def _one_stat(value: float) -> dict[str, Any]:
    return {
        "sample_count": 1, "mean": value, "sample_stddev": None,
        "bootstrap_interval": None,
    }


def _resources(observed: bool) -> dict[str, Any]:
    return {
        field: {
            "observed_count": 1 if observed else 0,
            "missing_count": 0 if observed else 1,
            "statistics": _one_stat(1.0) if observed else _empty_stat(),
        }
        for field in RESOURCE_FIELDS
    }


def _minimal_benchmark(hostile: str) -> dict[str, Any]:
    digest = "sha256:" + "a" * 64
    record = {
        "run_id": "run-hostile", "pair_id": "pair-1",
        "run_manifest": "evidence/run.json", "grading_manifest": "evidence/grading.json",
        "run_status": "completed", "grading_status": "completed",
        "run_error": None, "grading_error": None,
        "transcript_path": "evidence/transcript.md",
        "artifacts": [{"path": "evidence/artifact.txt", "sha256": digest}],
        "criteria": [{
            "criterion_id": "criterion-1", "verdict": "pass",
            "evidence": ["grading_manifest:#/criteria/0"],
        }],
        "claims_checked": [], "evaluator_quality_warnings": [],
        "quality": {"passed": 1, "failed": 0, "invalid": 0, "total": 1, "score": 1.0},
        "duration_seconds": None, "input_tokens": None,
        "output_tokens": None, "total_tokens": None,
    }
    candidate = {
        "configuration_id": "candidate", "role": "candidate", "label": "Candidate",
        "skill_digest": digest, "baseline_kind": None,
        "quality": {"included_count": 1, "excluded_count": 0, "statistics": _one_stat(1.0)},
        "resources": _resources(False),
    }
    baseline = {
        "configuration_id": "baseline", "role": "baseline", "label": "Baseline",
        "skill_digest": None, "baseline_kind": "no_skill",
        "quality": {"included_count": 0, "excluded_count": 0, "statistics": _empty_stat()},
        "resources": {
            field: {"observed_count": 0, "missing_count": 0, "statistics": _empty_stat()}
            for field in RESOURCE_FIELDS
        },
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "review-self-test-benchmark",
        "suite_id": "review-self-test",
        "generated_at": "2026-01-01T00:00:00Z",
        "methods": {
            "quality_score": "pass/(pass+fail); invalid excluded",
            "paired_delta": "candidate-minus-baseline for matching case_id and pair_id",
            "dispersion": "sample_standard_deviation",
            "interval": "seeded_percentile_bootstrap_of_mean",
            "bootstrap_seed": 7, "bootstrap_samples": 0,
            "confidence_level": 0.95, "significance_claim": False,
        },
        "counts": {
            "indexed_runs": 1, "completed_runs": 1, "executor_error_runs": 0,
            "invalid_runs": 0, "grading_completed_runs": 1,
            "grading_error_runs": 0, "grading_invalid_runs": 0,
            "grading_missing_runs": 0, "quality_included_runs": 1,
            "quality_excluded_runs": 0,
        },
        "cases": [{
            "case_id": "case-hostile", "prompt": hostile,
            "criteria": [{"id": "criterion-1", "text": hostile, "kind": "deterministic"}],
            "configurations": [dict(candidate, runs=[record]), dict(baseline, runs=[])],
            "pairs": [{
                "pair_id": "pair-1", "candidate_run_id": "run-hostile",
                "baseline_run_id": None, "status": "excluded",
                "exclusion_reason": "missing baseline arm", "candidate_score": 1.0,
                "baseline_score": None, "quality_delta": None,
            }],
            "paired_quality": {
                "included_pair_count": 0, "excluded_pair_count": 1,
                "statistics": _empty_stat(),
            },
        }],
        "aggregates": {
            "configurations": [candidate, baseline],
            "paired_quality": {
                "included_pair_count": 0, "excluded_pair_count": 1,
                "statistics": _empty_stat(),
            },
        },
        "findings": {
            "regressions": [], "flakiness": [], "non_discriminating_criteria": [],
        },
        "quality_cost": {
            "candidate_configuration_id": "candidate",
            "baseline_configuration_id": "baseline",
            "quality_delta": _empty_stat(), "duration_seconds_delta": _empty_stat(),
            "input_tokens_delta": _empty_stat(), "output_tokens_delta": _empty_stat(),
            "total_tokens_delta": _empty_stat(),
        },
        "analyzer_notes": [{
            "note_id": "hostile-data", "text": hostile,
            "evidence": [{
                "case_id": "case-hostile", "run_id": "run-hostile",
                "pair_id": "pair-1", "criterion_id": "criterion-1",
                "artifact_path": "evidence/artifact.txt",
            }],
        }],
    }


def _statistic_test_benchmark(hostile: str) -> dict[str, Any]:
    benchmark = _minimal_benchmark(hostile)
    case = benchmark["cases"][0]
    original = case["configurations"][0]["runs"][0]

    def fixed_stat(values: list[float | int]) -> dict[str, Any]:
        if not values:
            return _empty_stat()
        return {
            "sample_count": len(values),
            "mean": _rounded(sum(values) / len(values)),
            "sample_stddev": (
                _rounded(statistics.stdev(values)) if len(values) >= 2 else None
            ),
            "bootstrap_interval": None,
        }

    def make_run(
        run_id: str, pair_id: str, score: float, duration: float,
    ) -> dict[str, Any]:
        run = copy.deepcopy(original)
        verdict = "pass" if score == 1.0 else "fail"
        run.update({"run_id": run_id, "pair_id": pair_id, "duration_seconds": duration})
        run["criteria"][0]["verdict"] = verdict
        run["quality"] = {
            "passed": int(verdict == "pass"),
            "failed": int(verdict == "fail"),
            "invalid": 0,
            "total": 1,
            "score": score,
        }
        return run

    candidate_runs = [
        make_run("candidate-run-1", "pair-1", 1.0, 4.0),
        make_run("candidate-run-2", "pair-2", 1.0, 5.0),
    ]
    baseline_runs = [
        make_run("baseline-run-1", "pair-1", 0.0, 6.0),
        make_run("baseline-run-2", "pair-2", 1.0, 5.0),
    ]

    def quality(runs: list[dict[str, Any]]) -> dict[str, Any]:
        values = [run["quality"]["score"] for run in runs]
        return {
            "included_count": len(values), "excluded_count": 0,
            "statistics": fixed_stat(values),
        }

    def resources(runs: list[dict[str, Any]]) -> dict[str, Any]:
        result = {}
        for field in RESOURCE_FIELDS:
            values = [run[field] for run in runs if run[field] is not None]
            result[field] = {
                "observed_count": len(values),
                "missing_count": len(runs) - len(values),
                "statistics": fixed_stat(values),
            }
        return result

    candidate_meta = {
        key: value for key, value in benchmark["aggregates"]["configurations"][0].items()
        if key not in {"quality", "resources"}
    }
    baseline_meta = {
        key: value for key, value in benchmark["aggregates"]["configurations"][1].items()
        if key not in {"quality", "resources"}
    }
    candidate = dict(candidate_meta, quality=quality(candidate_runs), resources=resources(candidate_runs))
    baseline = dict(baseline_meta, quality=quality(baseline_runs), resources=resources(baseline_runs))
    case["configurations"] = [
        dict(candidate, runs=candidate_runs), dict(baseline, runs=baseline_runs),
    ]
    case["pairs"] = [
        {
            "pair_id": "pair-1", "candidate_run_id": "candidate-run-1",
            "baseline_run_id": "baseline-run-1", "status": "included",
            "exclusion_reason": None, "candidate_score": 1.0,
            "baseline_score": 0.0, "quality_delta": 1.0,
        },
        {
            "pair_id": "pair-2", "candidate_run_id": "candidate-run-2",
            "baseline_run_id": "baseline-run-2", "status": "included",
            "exclusion_reason": None, "candidate_score": 1.0,
            "baseline_score": 1.0, "quality_delta": 0.0,
        },
    ]
    quality_deltas = [1.0, 0.0]
    duration_deltas = [-2.0, 0.0]
    case["paired_quality"] = {
        "included_pair_count": 2, "excluded_pair_count": 0,
        "statistics": fixed_stat(quality_deltas),
    }
    benchmark["aggregates"] = {
        "configurations": [candidate, baseline],
        "paired_quality": copy.deepcopy(case["paired_quality"]),
    }
    benchmark["counts"] = {
        "indexed_runs": 4, "completed_runs": 4, "executor_error_runs": 0,
        "invalid_runs": 0, "grading_completed_runs": 4,
        "grading_error_runs": 0, "grading_invalid_runs": 0,
        "grading_missing_runs": 0, "quality_included_runs": 4,
        "quality_excluded_runs": 0,
    }
    benchmark["quality_cost"] = {
        "candidate_configuration_id": "candidate",
        "baseline_configuration_id": "baseline",
        "quality_delta": fixed_stat(quality_deltas),
        "duration_seconds_delta": fixed_stat(duration_deltas),
        "input_tokens_delta": _empty_stat(),
        "output_tokens_delta": _empty_stat(),
        "total_tokens_delta": _empty_stat(),
    }
    benchmark["findings"]["flakiness"] = [{
        "case_id": "case-hostile", "configuration_id": "baseline",
        "criterion_id": "criterion-1",
        "run_ids": ["baseline-run-1", "baseline-run-2"],
        "observed_verdicts": ["fail", "pass"],
    }]
    benchmark["analyzer_notes"][0]["evidence"][0].update({
        "run_id": "candidate-run-1", "pair_id": "pair-1",
    })
    return benchmark


def self_test(viewer_path: Path) -> None:
    check_template(viewer_path)
    hostile = "</script><script src=\"http://invalid.example/x.js\">&\u2028\u2029"
    benchmark = _statistic_test_benchmark(hostile)
    with tempfile.TemporaryDirectory(prefix="codex-review-self-test-") as raw:
        root = Path(raw)
        evidence = root / "benchmark" / "evidence"
        evidence.mkdir(parents=True)
        for name in ("run.json", "grading.json", "transcript.md", "artifact.txt"):
            (evidence / name).write_text(name + "\n", encoding="utf-8")
        artifact = evidence / "artifact.txt"
        artifact_digest = "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest()
        for arm in benchmark["cases"][0]["configurations"]:
            for run in arm["runs"]:
                run["artifacts"][0]["sha256"] = artifact_digest
        benchmark_path = root / "benchmark" / "benchmark.json"
        benchmark_path.write_text(
            json.dumps(benchmark, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
        output_a = root / "reviews" / "one" / "review.html"
        output_b = root / "reviews" / "two" / "review.html"
        embedded_a = render(benchmark_path, viewer_path, output_a)
        embedded_b = render(benchmark_path, viewer_path, output_b)
        decoded = check_output(output_a)
        check_output(output_b)
        assert decoded == embedded_a
        assert decoded["benchmark"]["cases"][0]["prompt"] == hostile
        assert embedded_a["feedback"]["blind_mapping"] == embedded_b["feedback"]["blind_mapping"]
        mapping = embedded_a["feedback"]["blind_mapping"]
        assert mapping["scope"] == "case_pair"
        assert mapping["method"] == "sha256_counterbalanced_case_pair_v1"
        assert len(mapping["assignments"]) == 2
        assert {item["A"] for item in mapping["assignments"]} == {"candidate", "baseline"}
        rendered = output_a.read_text(encoding="utf-8")
        assert "</script><script src=" not in rendered
        assert "\\u003c/script\\u003e" in rendered

        for name, field, replacement in (
            ("quality mean sign", "mean", -0.5),
            ("quality sample count", "sample_count", 3),
            ("quality sample standard deviation", "sample_stddev", 0.0),
        ):
            forged = copy.deepcopy(benchmark)
            forged["quality_cost"]["quality_delta"][field] = replacement
            try:
                validate_benchmark(forged, benchmark_path.parent)
            except ReviewError:
                pass
            else:
                raise AssertionError(f"forged {name} was accepted")
        forged_resource = copy.deepcopy(benchmark)
        forged_resource["quality_cost"]["duration_seconds_delta"]["mean"] = 1.0
        try:
            validate_benchmark(forged_resource, benchmark_path.parent)
        except ReviewError:
            pass
        else:
            raise AssertionError("forged resource-delta statistic was accepted")

        run = decoded["benchmark"]["cases"][0]["configurations"][0]["runs"][0]
        resolved = (
            output_a.parent / decoded["benchmark_link_base"] / run["artifacts"][0]["path"]
        ).resolve()
        assert resolved == artifact.resolve()
    print("[OK] generate_review self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render and validate a dependency-free static evaluation review."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="Render a static review")
    render_parser.add_argument("--benchmark", type=Path, required=True)
    render_parser.add_argument("--viewer", type=Path, required=True)
    render_parser.add_argument("--output", type=Path, required=True)
    render_parser.add_argument("--feedback", type=Path)

    template_parser = subparsers.add_parser("check-template", help="Validate a viewer template")
    template_parser.add_argument("--viewer", type=Path, required=True)

    output_parser = subparsers.add_parser("check-output", help="Validate a rendered review")
    output_parser.add_argument("--html", type=Path, required=True)

    test_parser = subparsers.add_parser("self-test", help="Run the hostile-data self-test")
    test_parser.add_argument("--viewer", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "render":
            render(
                args.benchmark.resolve(), args.viewer.resolve(), args.output.resolve(),
                None if args.feedback is None else args.feedback.resolve(),
            )
            print(f"[OK] Wrote review: {args.output.resolve()}")
        elif args.command == "check-template":
            check_template(args.viewer.resolve())
            print("[OK] Viewer template is valid")
        elif args.command == "check-output":
            check_output(args.html.resolve())
            print("[OK] Rendered review is valid")
        else:
            self_test(args.viewer.resolve())
        return 0
    except (AssertionError, OSError, ReviewError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
