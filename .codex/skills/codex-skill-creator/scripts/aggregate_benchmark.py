#!/usr/bin/env python3
"""Validate version-1.0 evaluation manifests and aggregate a benchmark."""

# Design informed by audited evaluation concepts and rewritten for Codex with
# standard-library Python and no vendor runtime or model invocation mechanics.

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
ROLES = {"candidate", "baseline"}
RUN_STATUSES = {"completed", "executor_error", "invalid"}
GRADING_STATUSES = {"completed", "grading_error", "invalid"}
VERDICTS = {"pass", "fail", "invalid"}
CRITERION_KINDS = {"deterministic", "model_judge", "human"}
GRADER_TYPES = {"deterministic", "model_judge", "human", "mixed"}
BASELINE_KINDS = {"no_skill", "old_snapshot"}
OBSOLETE_FIELDS = {"assertions", "expectations"}
RESOURCE_FIELDS = ("duration_seconds", "input_tokens", "output_tokens", "total_tokens")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
EVIDENCE_PATTERN = re.compile(
    r"^(artifact|transcript|run_manifest|grading_manifest):([^#]*)#(.+)$"
)


class SchemaError(ValueError):
    """A manifest or aggregation contract failure."""


def _reject_constant(value: str) -> None:
    raise SchemaError(f"JSON number must be finite, got {value}.")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), parse_constant=_reject_constant
        )
    except FileNotFoundError as exc:
        raise SchemaError(f"{label} not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SchemaError(f"Cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must contain a JSON object.")
    _reject_obsolete(value, label)
    return value


def _reject_obsolete(value: Any, label: str, location: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in OBSOLETE_FIELDS:
                raise SchemaError(
                    f"{label} uses obsolete field '{key}' at {location}; migrate it to 'criteria'."
                )
            _reject_obsolete(child, label, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_obsolete(child, label, f"{location}[{index}]")


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object.")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be an array.")
    return value


def _exact(
    value: dict[str, Any], required: set[str], label: str,
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - set(value)
    extra = set(value) - required - optional
    if missing or extra:
        raise SchemaError(
            f"{label} fields must be exact (missing={sorted(missing)}, extra={sorted(extra)})."
        )


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{label} must be a nonempty string.")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _string(value, label)
    if not ID_PATTERN.fullmatch(value):
        raise SchemaError(f"{label} must match {ID_PATTERN.pattern}.")
    return value


def _digest(value: Any, label: str, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
        suffix = " or null" if nullable else ""
        raise SchemaError(f"{label} must be sha256: plus 64 lowercase hex characters{suffix}.")
    return value


def _version(document: dict[str, Any], label: str) -> None:
    if document.get("schema_version") != SCHEMA_VERSION:
        raise SchemaError(f"{label} schema_version must be {SCHEMA_VERSION}.")


def _nullable_number(value: Any, label: str) -> float | int | None:
    if value is None:
        return None
    if (
        isinstance(value, bool) or not isinstance(value, (int, float))
        or not math.isfinite(value) or value < 0
    ):
        raise SchemaError(f"{label} must be a finite nonnegative number or null.")
    return value


def _nullable_token(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SchemaError(f"{label} must be a nonnegative integer or null.")
    return value


def _timestamp(value: Any, label: str, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    value = _string(value, label)
    if not value.endswith("Z"):
        raise SchemaError(f"{label} must be an RFC 3339 UTC timestamp ending in Z.")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise SchemaError(f"{label} must be an RFC 3339 UTC timestamp.") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise SchemaError(f"{label} must be UTC.")
    return value


def _path_parts(raw: Any, label: str) -> str:
    value = _string(raw, label)
    if "\\" in value or "\x00" in value or value.startswith("/"):
        raise SchemaError(f"{label} must be a portable relative path using / separators.")
    parts = value.split("/")
    if any(not part or part in {".", ".."} for part in parts):
        raise SchemaError(f"{label} cannot contain empty, '.' or '..' segments.")
    return value


def _manifest_path(container: Path, raw: Any, label: str, exists: bool = True) -> Path:
    value = _path_parts(raw, label)
    base = container.parent.resolve()
    resolved = (base / Path(value)).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise SchemaError(f"{label} escapes its containing manifest directory.") from exc
    if exists and not resolved.is_file():
        raise SchemaError(f"{label} not found: {resolved}")
    return resolved


def _benchmark_relative(target: Path, benchmark_path: Path) -> str:
    relative = os.path.relpath(target.resolve(), benchmark_path.parent.resolve())
    value = relative.replace(os.sep, "/")
    if "\\" in value or "\x00" in value or value.startswith("/"):
        raise SchemaError("Cannot represent an artifact as a benchmark-relative path.")
    parts = value.split("/")
    if any(not part or part == "." for part in parts):
        raise SchemaError("Benchmark-relative paths must be canonical.")
    return value


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _error(value: Any, label: str, required: bool) -> dict[str, str] | None:
    if value is None:
        if required:
            raise SchemaError(f"{label} must be a non-null error object.")
        return None
    item = _mapping(value, label)
    _exact(item, {"code", "message"}, label)
    _identifier(item.get("code"), f"{label}.code")
    _string(item.get("message"), f"{label}.message")
    return item


def _evidence(value: Any, label: str) -> str:
    value = _string(value, label)
    match = EVIDENCE_PATTERN.fullmatch(value)
    if match is None:
        raise SchemaError(f"{label} is not a valid evidence reference.")
    source, path, locator = match.groups()
    if source in {"artifact", "transcript"}:
        _path_parts(path, f"{label} path")
    elif path:
        _path_parts(path, f"{label} path")
    if not locator.strip():
        raise SchemaError(f"{label} requires a locator after #.")
    return value


def _validate_suite(path: Path, data: dict[str, Any]) -> tuple[dict[str, dict], dict[str, dict]]:
    _version(data, "suite.json")
    _exact(data, {"schema_version", "suite_id", "configurations", "cases"}, "suite.json")
    _identifier(data.get("suite_id"), "suite_id")
    configurations = _list(data.get("configurations"), "configurations")
    if len(configurations) != 2:
        raise SchemaError("suite.json must define exactly two configurations.")
    config_map: dict[str, dict] = {}
    roles: set[str] = set()
    for raw_config in configurations:
        config = _mapping(raw_config, "configuration")
        role = config.get("role")
        if role == "candidate":
            _exact(
                config,
                {"configuration_id", "role", "label", "skill_digest"},
                "candidate configuration",
            )
        elif role == "baseline":
            _exact(
                config,
                {"configuration_id", "role", "label", "skill_digest", "baseline_kind"},
                "baseline configuration",
            )
        else:
            raise SchemaError("Configuration role must be candidate or baseline.")
        config_id = _identifier(config.get("configuration_id"), "configuration_id")
        if config_id in config_map:
            raise SchemaError(f"Duplicate configuration_id: {config_id}")
        if role in roles:
            raise SchemaError("Configurations must contain one candidate and one baseline role.")
        roles.add(role)
        _string(config.get("label"), f"configuration {config_id} label")
        if role == "candidate":
            _digest(config.get("skill_digest"), f"configuration {config_id} skill_digest")
        else:
            kind = config.get("baseline_kind")
            if kind not in BASELINE_KINDS:
                raise SchemaError("Baseline configuration has invalid baseline_kind.")
            _digest(
                config.get("skill_digest"), f"configuration {config_id} skill_digest",
                nullable=kind == "no_skill",
            )
            if kind == "no_skill" and config.get("skill_digest") is not None:
                raise SchemaError("A no_skill baseline must use null skill_digest.")
            if kind == "old_snapshot" and config.get("skill_digest") is None:
                raise SchemaError("An old_snapshot baseline requires skill_digest.")
        config_map[config_id] = config
    if roles != ROLES:
        raise SchemaError("Configurations must contain candidate and baseline roles.")

    cases = _list(data.get("cases"), "cases")
    case_map: dict[str, dict] = {}
    global_criteria: set[str] = set()
    for raw_case in cases:
        case = _mapping(raw_case, "case")
        _exact(case, {"case_id", "prompt", "fixtures", "criteria"}, "case")
        case_id = _identifier(case.get("case_id"), "case_id")
        if case_id in case_map:
            raise SchemaError(f"Duplicate case_id: {case_id}")
        _string(case.get("prompt"), f"case {case_id} prompt")
        fixture_paths: set[str] = set()
        for raw_fixture in _list(case.get("fixtures"), f"case {case_id} fixtures"):
            fixture = _mapping(raw_fixture, "fixture")
            _exact(fixture, {"path", "sha256"}, "fixture")
            fixture_path = _manifest_path(path, fixture.get("path"), "fixture path")
            portable = str(fixture["path"])
            if portable in fixture_paths:
                raise SchemaError(f"Duplicate fixture path: {portable}")
            fixture_paths.add(portable)
            expected = _digest(fixture.get("sha256"), "fixture sha256")
            if _file_digest(fixture_path) != expected:
                raise SchemaError(f"Fixture digest mismatch: {portable}")
        criteria = _list(case.get("criteria"), f"case {case_id} criteria")
        if not criteria:
            raise SchemaError(f"case {case_id} must define criteria.")
        for raw_criterion in criteria:
            criterion = _mapping(raw_criterion, "criterion")
            _exact(criterion, {"id", "text", "kind"}, "criterion")
            criterion_id = _identifier(criterion.get("id"), "criterion id")
            if criterion_id in global_criteria:
                raise SchemaError(f"Duplicate criterion id: {criterion_id}")
            global_criteria.add(criterion_id)
            _string(criterion.get("text"), f"criterion {criterion_id} text")
            if criterion.get("kind") not in CRITERION_KINDS:
                raise SchemaError(f"criterion {criterion_id} has invalid kind.")
        case_map[case_id] = case
    if not case_map:
        raise SchemaError("suite.json must contain at least one case.")
    return config_map, case_map


def _validate_run(
    path: Path, run: dict[str, Any], suite: dict[str, Any],
    configs: dict[str, dict], cases: dict[str, dict],
) -> None:
    _version(run, "run.json")
    _exact(run, {
        "schema_version", "run_id", "suite_id", "case_id", "configuration_id",
        "role", "pair_id", "skill_digest", "executor", "model", "harness",
        "artifacts", "transcript_path", "started_at", "ended_at",
        "duration_seconds", "input_tokens", "output_tokens", "total_tokens",
        "status", "error",
    }, "run.json")
    for field in ("run_id", "suite_id", "case_id", "configuration_id", "pair_id"):
        _identifier(run.get(field), f"run {field}")
    if run["suite_id"] != suite["suite_id"]:
        raise SchemaError(f"run {run['run_id']} suite_id mismatch.")
    if run["case_id"] not in cases:
        raise SchemaError(f"run {run['run_id']} names unknown case_id.")
    config = configs.get(run["configuration_id"])
    if config is None:
        raise SchemaError(f"run {run['run_id']} names unknown configuration_id.")
    if run.get("role") != config["role"]:
        raise SchemaError(f"run {run['run_id']} role/configuration mismatch.")
    if run.get("skill_digest") != config.get("skill_digest"):
        raise SchemaError(f"run {run['run_id']} skill_digest/configuration mismatch.")
    _digest(run.get("skill_digest"), f"run {run['run_id']} skill_digest", nullable=True)

    for field in ("executor", "harness"):
        provenance = _mapping(run.get(field), f"run {run['run_id']} {field}")
        _exact(provenance, {"name", "version"}, f"run {run['run_id']} {field}")
        _string(provenance.get("name"), f"run {run['run_id']} {field}.name")
        version = provenance.get("version")
        if version is not None:
            _string(version, f"run {run['run_id']} {field}.version")
    model = _mapping(run.get("model"), f"run {run['run_id']} model")
    _exact(model, {"name", "settings"}, f"run {run['run_id']} model")
    _string(model.get("name"), f"run {run['run_id']} model.name")
    _mapping(model.get("settings"), f"run {run['run_id']} model.settings")

    artifact_paths: set[str] = set()
    artifact_digests: set[str] = set()
    for raw_artifact in _list(run.get("artifacts"), f"run {run['run_id']} artifacts"):
        artifact = _mapping(raw_artifact, "artifact")
        _exact(artifact, {"path", "sha256"}, "artifact", {"media_type"})
        artifact_path = _manifest_path(path, artifact.get("path"), "artifact path")
        portable = str(artifact["path"])
        digest = _digest(artifact.get("sha256"), "artifact sha256")
        if portable in artifact_paths or digest in artifact_digests:
            raise SchemaError(f"Duplicate artifact path or digest in run {run['run_id']}.")
        artifact_paths.add(portable)
        artifact_digests.add(digest)
        if _file_digest(artifact_path) != digest:
            raise SchemaError(f"Artifact digest mismatch: {portable}")
        if "media_type" in artifact:
            _string(artifact["media_type"], "artifact media_type")

    status = run.get("status")
    if status not in RUN_STATUSES:
        raise SchemaError(f"run {run['run_id']} has invalid status.")
    transcript = run.get("transcript_path")
    if transcript is None:
        if status == "completed":
            raise SchemaError(f"completed run {run['run_id']} requires transcript_path.")
    else:
        _manifest_path(path, transcript, "transcript_path")
    started = _timestamp(run.get("started_at"), "started_at")
    ended = _timestamp(run.get("ended_at"), "ended_at", nullable=True)
    duration = _nullable_number(run.get("duration_seconds"), "duration_seconds")
    if ended is not None and duration is not None:
        started_dt = datetime.fromisoformat(started[:-1] + "+00:00")
        ended_dt = datetime.fromisoformat(ended[:-1] + "+00:00")
        if ended_dt < started_dt or abs((ended_dt - started_dt).total_seconds() - duration) > 0.001:
            raise SchemaError(f"run {run['run_id']} timestamps and duration disagree.")
    tokens = {
        field: _nullable_token(run.get(field), field)
        for field in ("input_tokens", "output_tokens", "total_tokens")
    }
    if all(tokens[field] is not None for field in tokens):
        if tokens["input_tokens"] + tokens["output_tokens"] != tokens["total_tokens"]:
            raise SchemaError(f"run {run['run_id']} token totals disagree.")
    _error(run.get("error"), f"run {run['run_id']} error", required=status != "completed")
    if status == "completed" and run.get("error") is not None:
        raise SchemaError(f"completed run {run['run_id']} must have null error.")


def _validate_grading(
    grading: dict[str, Any], run: dict[str, Any], case: dict[str, Any],
    grading_ids: set[str],
) -> None:
    _version(grading, "grading.json")
    _exact(grading, {
        "schema_version", "grading_id", "run_id", "suite_id", "case_id",
        "status", "grader", "criteria", "claims_checked",
        "evaluator_quality_warnings", "error",
    }, "grading.json")
    for field in ("grading_id", "run_id", "suite_id", "case_id"):
        _identifier(grading.get(field), f"grading {field}")
    if grading["grading_id"] in grading_ids:
        raise SchemaError(f"Duplicate grading_id: {grading['grading_id']}")
    grading_ids.add(grading["grading_id"])
    for field in ("run_id", "suite_id", "case_id"):
        if grading[field] != run[field]:
            raise SchemaError(f"grading {grading['grading_id']} {field} mismatch.")
    status = grading.get("status")
    if status not in GRADING_STATUSES:
        raise SchemaError(f"grading {grading['grading_id']} has invalid status.")
    if run["status"] != "completed" and status == "completed":
        raise SchemaError("A non-completed run cannot have completed grading.")
    grader = _mapping(grading.get("grader"), "grader")
    _exact(grader, {"type", "version"}, "grader")
    if grader.get("type") not in GRADER_TYPES:
        raise SchemaError("grader.type is invalid; use deterministic, model_judge, human, or mixed.")
    _identifier(grader.get("version"), "grader.version")

    expected = {criterion["id"] for criterion in case["criteria"]}
    entries = _list(grading.get("criteria"), "grading criteria")
    seen: set[str] = set()
    for raw_entry in entries:
        entry = _mapping(raw_entry, "grading criterion")
        _exact(entry, {"criterion_id", "verdict", "evidence"}, "grading criterion")
        criterion_id = _identifier(entry.get("criterion_id"), "criterion_id")
        if criterion_id not in expected or criterion_id in seen:
            raise SchemaError(f"Unknown or duplicate graded criterion: {criterion_id}")
        seen.add(criterion_id)
        verdict = entry.get("verdict")
        if verdict not in VERDICTS:
            raise SchemaError(f"criterion {criterion_id} has invalid verdict.")
        evidence = _list(entry.get("evidence"), f"criterion {criterion_id} evidence")
        for reference in evidence:
            _evidence(reference, f"criterion {criterion_id} evidence reference")
        if verdict in {"pass", "fail"} and not evidence:
            raise SchemaError(f"criterion {criterion_id} requires evidence.")
    if status == "completed" and seen != expected:
        raise SchemaError("Completed grading must include every precommitted criterion.")

    for raw_claim in _list(grading.get("claims_checked"), "claims_checked"):
        claim = _mapping(raw_claim, "claim checked")
        _exact(claim, {"claim", "evaluation", "evidence"}, "claim checked")
        _string(claim.get("claim"), "claim checked claim")
        if claim.get("evaluation") not in {"verified", "contradicted", "unverifiable"}:
            raise SchemaError("claim evaluation is invalid.")
        evidence = _list(claim.get("evidence"), "claim evidence")
        for reference in evidence:
            _evidence(reference, "claim evidence reference")
        if claim["evaluation"] != "unverifiable" and not evidence:
            raise SchemaError("Verified or contradicted claims require evidence.")

    for raw_warning in _list(
        grading.get("evaluator_quality_warnings"), "evaluator_quality_warnings"
    ):
        warning = _mapping(raw_warning, "evaluator warning")
        _exact(
            warning, {"code", "message", "criterion_id", "evidence"},
            "evaluator warning",
        )
        _identifier(warning.get("code"), "evaluator warning code")
        _string(warning.get("message"), "evaluator warning message")
        criterion_id = warning.get("criterion_id")
        if criterion_id is not None and criterion_id not in expected:
            raise SchemaError("Evaluator warning names an unknown criterion_id.")
        for reference in _list(warning.get("evidence"), "evaluator warning evidence"):
            _evidence(reference, "evaluator warning evidence reference")
    _error(grading.get("error"), "grading error", required=status != "completed")
    if status == "completed" and grading.get("error") is not None:
        raise SchemaError("Completed grading must have null error.")


def _percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _round(value: float) -> float:
    return round(value, 6)


def _stats(values: list[float], rng: random.Random, bootstrap_samples: int) -> dict[str, Any]:
    count = len(values)
    if not values:
        return {
            "sample_count": 0, "mean": None, "sample_stddev": None,
            "bootstrap_interval": None,
        }
    mean = sum(values) / count
    stddev = None
    if count >= 2:
        stddev = math.sqrt(sum((value - mean) ** 2 for value in values) / (count - 1))
    interval = None
    if count >= 2 and bootstrap_samples > 0:
        means = [
            sum(values[rng.randrange(count)] for _ in range(count)) / count
            for _ in range(bootstrap_samples)
        ]
        interval = {
            "lower": _round(_percentile(means, 0.025)),
            "upper": _round(_percentile(means, 0.975)),
        }
    return {
        "sample_count": count,
        "mean": _round(mean),
        "sample_stddev": None if stddev is None else _round(stddev),
        "bootstrap_interval": interval,
    }


def _quality(run: dict[str, Any], grading: dict[str, Any] | None) -> dict[str, Any]:
    criteria = [] if grading is None else grading["criteria"]
    counts = Counter(item["verdict"] for item in criteria)
    denominator = counts["pass"] + counts["fail"]
    score = None
    if (
        run["status"] == "completed" and grading is not None
        and grading["status"] == "completed" and denominator
    ):
        score = _round(counts["pass"] / denominator)
    return {
        "passed": counts["pass"],
        "failed": counts["fail"],
        "invalid": counts["invalid"],
        "total": len(criteria),
        "score": score,
    }


def _score(record: dict[str, Any]) -> float | None:
    return _quality(record["run"], record["grading"])["score"]


def _resource_summary(
    records: list[dict[str, Any]], field: str, rng: random.Random,
    bootstrap_samples: int,
) -> dict[str, Any]:
    values = [float(item["run"][field]) for item in records if item["run"][field] is not None]
    return {
        "observed_count": len(values),
        "missing_count": len(records) - len(values),
        "statistics": _stats(values, rng, bootstrap_samples),
    }


def _resource_block(
    records: list[dict[str, Any]], rng: random.Random, bootstrap_samples: int,
) -> dict[str, Any]:
    return {
        field: _resource_summary(records, field, rng, bootstrap_samples)
        for field in RESOURCE_FIELDS
    }


def _run_view(record: dict[str, Any], benchmark_path: Path) -> dict[str, Any]:
    run = record["run"]
    grading = record["grading"]
    run_path = record["run_path"]
    grading_path = record["grading_path"]
    artifacts = []
    for artifact in run["artifacts"]:
        item = {
            "path": _benchmark_relative(
                (run_path.parent / artifact["path"]).resolve(), benchmark_path
            ),
            "sha256": artifact["sha256"],
        }
        if "media_type" in artifact:
            item["media_type"] = artifact["media_type"]
        artifacts.append(item)
    transcript = None
    if run["transcript_path"] is not None:
        transcript = _benchmark_relative(
            (run_path.parent / run["transcript_path"]).resolve(), benchmark_path
        )
    return {
        "run_id": run["run_id"],
        "pair_id": run["pair_id"],
        "run_manifest": _benchmark_relative(run_path, benchmark_path),
        "grading_manifest": (
            None if grading_path is None
            else _benchmark_relative(grading_path, benchmark_path)
        ),
        "run_status": run["status"],
        "grading_status": None if grading is None else grading["status"],
        "run_error": run["error"],
        "grading_error": None if grading is None else grading["error"],
        "transcript_path": transcript,
        "artifacts": artifacts,
        "criteria": [] if grading is None else grading["criteria"],
        "claims_checked": [] if grading is None else grading["claims_checked"],
        "evaluator_quality_warnings": (
            [] if grading is None else grading["evaluator_quality_warnings"]
        ),
        "quality": _quality(run, grading),
        "duration_seconds": run["duration_seconds"],
        "input_tokens": run["input_tokens"],
        "output_tokens": run["output_tokens"],
        "total_tokens": run["total_tokens"],
    }


def _analyzer_evidence(
    case_id: str, run_id: str | None = None, pair_id: str | None = None,
    criterion_id: str | None = None, artifact_path: str | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "run_id": run_id,
        "pair_id": pair_id,
        "criterion_id": criterion_id,
        "artifact_path": artifact_path,
    }


def aggregate(
    suite_path: Path, index_path: Path, seed: int, bootstrap_samples: int,
    benchmark_path: Path | None = None,
) -> dict[str, Any]:
    suite_path = suite_path.resolve()
    index_path = index_path.resolve()
    benchmark_path = (
        (suite_path.parent / "benchmark.json") if benchmark_path is None else benchmark_path
    ).resolve()
    suite = _load_json(suite_path, "suite.json")
    configs, cases = _validate_suite(suite_path, suite)
    index = _load_json(index_path, "run-index.json")
    _version(index, "run-index.json")
    _exact(index, {"schema_version", "suite_id", "runs"}, "run-index.json")
    if index.get("suite_id") != suite["suite_id"]:
        raise SchemaError("run-index.json suite_id mismatch.")
    index_entries = _list(index.get("runs"), "run-index runs")
    if not index_entries:
        raise SchemaError("run-index.json runs must be nonempty.")

    records: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    grading_ids: set[str] = set()
    referenced_paths: set[Path] = set()
    pair_roles: set[tuple[str, str, str]] = set()
    pair_cases: dict[str, str] = {}
    for position, raw_item in enumerate(index_entries):
        entry = _mapping(raw_item, f"run-index entry {position}")
        _exact(entry, {"run_manifest"}, f"run-index entry {position}", {"grading_manifest"})
        run_path = _manifest_path(index_path, entry.get("run_manifest"), "run_manifest")
        if run_path in referenced_paths:
            raise SchemaError(f"Duplicate manifest path: {run_path}")
        referenced_paths.add(run_path)
        run = _load_json(run_path, "run.json")
        _validate_run(run_path, run, suite, configs, cases)
        if run["run_id"] in run_ids:
            raise SchemaError(f"Duplicate run_id: {run['run_id']}")
        run_ids.add(run["run_id"])
        previous_case = pair_cases.setdefault(run["pair_id"], run["case_id"])
        if previous_case != run["case_id"]:
            raise SchemaError(f"pair_id {run['pair_id']} is used by multiple cases.")
        pair_key = (run["case_id"], run["pair_id"], run["role"])
        if pair_key in pair_roles:
            raise SchemaError(
                f"Duplicate role in case/pair: {run['case_id']} {run['pair_id']} {run['role']}"
            )
        pair_roles.add(pair_key)
        grading = None
        grading_path = None
        if "grading_manifest" in entry:
            grading_path = _manifest_path(
                index_path, entry["grading_manifest"], "grading_manifest"
            )
            if grading_path in referenced_paths:
                raise SchemaError(f"Duplicate manifest path: {grading_path}")
            referenced_paths.add(grading_path)
            grading = _load_json(grading_path, "grading.json")
            _validate_grading(grading, run, cases[run["case_id"]], grading_ids)
        records.append({
            "run": run, "grading": grading, "position": position,
            "run_path": run_path, "grading_path": grading_path,
        })

    rng = random.Random(seed)
    config_order = [
        next(key for key, value in configs.items() if value["role"] == role)
        for role in ("candidate", "baseline")
    ]
    candidate_id, baseline_id = config_order
    case_results: list[dict[str, Any]] = []
    all_pair_deltas: list[float] = []
    all_pairs: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []
    flakiness: list[dict[str, Any]] = []
    non_discriminating: list[dict[str, Any]] = []

    for case_id, case in cases.items():
        case_records = [item for item in records if item["run"]["case_id"] == case_id]
        configurations: list[dict[str, Any]] = []
        for config_id in config_order:
            arm = [
                item for item in case_records
                if item["run"]["configuration_id"] == config_id
            ]
            scores = [score for score in (_score(item) for item in arm) if score is not None]
            config = configs[config_id]
            configurations.append({
                "configuration_id": config_id,
                "role": config["role"],
                "label": config["label"],
                "skill_digest": config.get("skill_digest"),
                "baseline_kind": config.get("baseline_kind"),
                "runs": [_run_view(item, benchmark_path) for item in arm],
                "quality": {
                    "included_count": len(scores),
                    "excluded_count": len(arm) - len(scores),
                    "statistics": _stats(scores, rng, bootstrap_samples),
                },
                "resources": _resource_block(arm, rng, bootstrap_samples),
            })

        by_pair: dict[str, dict[str, dict[str, Any]]] = {}
        for record in case_records:
            by_pair.setdefault(record["run"]["pair_id"], {})[record["run"]["role"]] = record
        pair_items: list[dict[str, Any]] = []
        criterion_pairs: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
        for pair_id, arms in by_pair.items():
            candidate = arms.get("candidate")
            baseline = arms.get("baseline")
            candidate_score = None if candidate is None else _score(candidate)
            baseline_score = None if baseline is None else _score(baseline)
            status = "included"
            reason = None
            if candidate is None or baseline is None:
                status = "excluded"
                reason = "missing candidate arm" if candidate is None else "missing baseline arm"
            elif candidate_score is None or baseline_score is None:
                status = "excluded"
                if candidate_score is None and baseline_score is None:
                    reason = "both quality scores unavailable"
                elif candidate_score is None:
                    reason = "candidate quality score unavailable"
                else:
                    reason = "baseline quality score unavailable"
            delta = None
            if status == "included":
                delta = _round(candidate_score - baseline_score)
                all_pair_deltas.append(delta)
            pair_item = {
                "pair_id": pair_id,
                "candidate_run_id": None if candidate is None else candidate["run"]["run_id"],
                "baseline_run_id": None if baseline is None else baseline["run"]["run_id"],
                "status": status,
                "exclusion_reason": reason,
                "candidate_score": candidate_score,
                "baseline_score": baseline_score,
                "quality_delta": delta,
            }
            pair_items.append(pair_item)
            all_pairs.append(pair_item)
            if delta is not None and delta < 0 and candidate is not None and baseline is not None:
                candidate_manifest = _benchmark_relative(candidate["run_path"], benchmark_path)
                baseline_manifest = _benchmark_relative(baseline["run_path"], benchmark_path)
                regressions.append({
                    "case_id": case_id,
                    "criterion_id": None,
                    "pair_ids": [pair_id],
                    "delta": delta,
                    "evidence": [
                        f"run_manifest:{candidate_manifest}#/run_id",
                        f"run_manifest:{baseline_manifest}#/run_id",
                    ],
                })
            if candidate is not None and baseline is not None:
                if candidate["grading"] is not None and baseline["grading"] is not None:
                    candidate_verdicts = {
                        item["criterion_id"]: item["verdict"]
                        for item in candidate["grading"]["criteria"]
                    }
                    baseline_verdicts = {
                        item["criterion_id"]: item["verdict"]
                        for item in baseline["grading"]["criteria"]
                    }
                    for criterion_id in candidate_verdicts.keys() & baseline_verdicts.keys():
                        left = candidate_verdicts[criterion_id]
                        right = baseline_verdicts[criterion_id]
                        if left in {"pass", "fail"} and right in {"pass", "fail"}:
                            criterion_pairs[criterion_id].append((
                                left, right,
                                candidate["run"]["run_id"], baseline["run"]["run_id"],
                            ))

        pair_deltas = [item["quality_delta"] for item in pair_items if item["quality_delta"] is not None]
        for config_id in config_order:
            arm = [
                item for item in case_records
                if item["run"]["configuration_id"] == config_id
            ]
            for criterion in case["criteria"]:
                observed: list[tuple[str, str]] = []
                for record in arm:
                    if record["grading"] is None:
                        continue
                    verdict = next((
                        item["verdict"] for item in record["grading"]["criteria"]
                        if item["criterion_id"] == criterion["id"]
                    ), None)
                    if verdict in {"pass", "fail"}:
                        observed.append((record["run"]["run_id"], verdict))
                verdicts = {verdict for _, verdict in observed}
                if verdicts == {"pass", "fail"}:
                    flakiness.append({
                        "case_id": case_id,
                        "configuration_id": config_id,
                        "criterion_id": criterion["id"],
                        "run_ids": [run_id for run_id, _ in observed],
                        "observed_verdicts": sorted(verdicts),
                    })
        for criterion_id, observations in sorted(criterion_pairs.items()):
            if observations and all(left == right for left, right, _, _ in observations):
                non_discriminating.append({
                    "case_id": case_id,
                    "criterion_id": criterion_id,
                    "reason": "All observed matched candidate/baseline verdicts were identical.",
                    "run_ids": [run_id for item in observations for run_id in item[2:]],
                })
        case_results.append({
            "case_id": case_id,
            "prompt": case["prompt"],
            "criteria": case["criteria"],
            "configurations": configurations,
            "pairs": pair_items,
            "paired_quality": {
                "included_pair_count": len(pair_deltas),
                "excluded_pair_count": len(pair_items) - len(pair_deltas),
                "statistics": _stats(pair_deltas, rng, bootstrap_samples),
            },
        })

    aggregate_configurations: list[dict[str, Any]] = []
    for config_id in config_order:
        arm = [item for item in records if item["run"]["configuration_id"] == config_id]
        scores = [score for score in (_score(item) for item in arm) if score is not None]
        config = configs[config_id]
        aggregate_configurations.append({
            "configuration_id": config_id,
            "role": config["role"],
            "label": config["label"],
            "skill_digest": config.get("skill_digest"),
            "baseline_kind": config.get("baseline_kind"),
            "quality": {
                "included_count": len(scores),
                "excluded_count": len(arm) - len(scores),
                "statistics": _stats(scores, rng, bootstrap_samples),
            },
            "resources": _resource_block(arm, rng, bootstrap_samples),
        })

    paired_groups: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        paired_groups[(record["run"]["case_id"], record["run"]["pair_id"])][record["run"]["role"]] = record
    paired_resource_deltas: dict[str, list[float]] = {field: [] for field in RESOURCE_FIELDS}
    for arms in paired_groups.values():
        if set(arms) != ROLES:
            continue
        for field in RESOURCE_FIELDS:
            candidate_value = arms["candidate"]["run"][field]
            baseline_value = arms["baseline"]["run"][field]
            if candidate_value is not None and baseline_value is not None:
                paired_resource_deltas[field].append(float(candidate_value - baseline_value))

    run_statuses = Counter(record["run"]["status"] for record in records)
    grading_statuses = Counter(
        "missing" if record["grading"] is None else record["grading"]["status"]
        for record in records
    )
    quality_included = sum(_score(record) is not None for record in records)
    excluded_records = [record for record in records if _score(record) is None]
    analyzer_notes: list[dict[str, Any]] = []
    if excluded_records:
        analyzer_notes.append({
            "note_id": "excluded-quality-runs",
            "text": "Some indexed runs lack a complete quality score; they remain visible and excluded from quality statistics.",
            "evidence": [
                _analyzer_evidence(
                    record["run"]["case_id"], run_id=record["run"]["run_id"],
                    pair_id=record["run"]["pair_id"],
                )
                for record in excluded_records
            ],
        })
    first_case_id = next(iter(cases))
    analyzer_notes.append({
        "note_id": "descriptive-scope",
        "text": "Results and bootstrap intervals are descriptive; no tiny-suite significance claim is made.",
        "evidence": [_analyzer_evidence(first_case_id)],
    })

    generated_at = max(
        (record["run"]["ended_at"] or record["run"]["started_at"] for record in records),
        key=lambda value: datetime.fromisoformat(value[:-1] + "+00:00"),
    )
    identity_input = {
        "suite": suite,
        "run_index": index,
        "records": [
            {"run": record["run"], "grading": record["grading"]}
            for record in records
        ],
        "seed": seed,
        "bootstrap_samples": bootstrap_samples,
    }
    identity = hashlib.sha256(
        json.dumps(identity_input, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    benchmark_id = f"{suite['suite_id']}-benchmark-{identity}"
    paired_included = sum(item["status"] == "included" for item in all_pairs)
    overall_quality_statistics = _stats(all_pair_deltas, rng, bootstrap_samples)
    quality_cost_quality_statistics = _stats(all_pair_deltas, rng, bootstrap_samples)
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": benchmark_id,
        "suite_id": suite["suite_id"],
        "generated_at": generated_at,
        "methods": {
            "quality_score": "pass/(pass+fail); invalid excluded",
            "paired_delta": "candidate-minus-baseline for matching case_id and pair_id",
            "dispersion": "sample_standard_deviation",
            "interval": "seeded_percentile_bootstrap_of_mean",
            "bootstrap_seed": seed,
            "bootstrap_samples": bootstrap_samples,
            "confidence_level": 0.95,
            "significance_claim": False,
        },
        "counts": {
            "indexed_runs": len(records),
            "completed_runs": run_statuses["completed"],
            "executor_error_runs": run_statuses["executor_error"],
            "invalid_runs": run_statuses["invalid"],
            "grading_completed_runs": grading_statuses["completed"],
            "grading_error_runs": grading_statuses["grading_error"],
            "grading_invalid_runs": grading_statuses["invalid"],
            "grading_missing_runs": grading_statuses["missing"],
            "quality_included_runs": quality_included,
            "quality_excluded_runs": len(records) - quality_included,
        },
        "cases": case_results,
        "aggregates": {
            "configurations": aggregate_configurations,
            "paired_quality": {
                "included_pair_count": paired_included,
                "excluded_pair_count": len(all_pairs) - paired_included,
                "statistics": overall_quality_statistics,
            },
        },
        "findings": {
            "regressions": regressions,
            "flakiness": flakiness,
            "non_discriminating_criteria": non_discriminating,
        },
        "quality_cost": {
            "candidate_configuration_id": candidate_id,
            "baseline_configuration_id": baseline_id,
            "quality_delta": quality_cost_quality_statistics,
            "duration_seconds_delta": _stats(
                paired_resource_deltas["duration_seconds"], rng, bootstrap_samples
            ),
            "input_tokens_delta": _stats(
                paired_resource_deltas["input_tokens"], rng, bootstrap_samples
            ),
            "output_tokens_delta": _stats(
                paired_resource_deltas["output_tokens"], rng, bootstrap_samples
            ),
            "total_tokens_delta": _stats(
                paired_resource_deltas["total_tokens"], rng, bootstrap_samples
            ),
        },
        "analyzer_notes": analyzer_notes,
    }


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink()
        except OSError:
            pass
        raise


def _self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="codex-benchmark-self-test-") as raw:
        root = Path(raw)
        digest_a = "sha256:" + "a" * 64
        suite = {
            "schema_version": SCHEMA_VERSION,
            "suite_id": "self-test-suite",
            "configurations": [
                {
                    "configuration_id": "candidate-v1", "role": "candidate",
                    "label": "Candidate", "skill_digest": digest_a,
                },
                {
                    "configuration_id": "baseline-v1", "role": "baseline",
                    "label": "Baseline", "skill_digest": None,
                    "baseline_kind": "no_skill",
                },
            ],
            "cases": [
                {
                    "case_id": "case-1", "prompt": "Exercise paired quality.",
                    "fixtures": [],
                    "criteria": [{
                        "id": "criterion-1", "text": "Produce the required result.",
                        "kind": "model_judge",
                    }],
                },
                {
                    "case_id": "case-2", "prompt": "Exercise exclusions.",
                    "fixtures": [],
                    "criteria": [{
                        "id": "criterion-2", "text": "Preserve invalid state.",
                        "kind": "human",
                    }],
                },
            ],
        }
        _atomic_json(root / "suite.json", suite)
        definitions = [
            ("c1", "case-1", "p1", "candidate-v1", "candidate", "completed", "completed", "pass", 10.0, 10, 5),
            ("b1", "case-1", "p1", "baseline-v1", "baseline", "completed", "completed", "fail", 12.0, 9, 6),
            ("c2", "case-1", "p2", "candidate-v1", "candidate", "completed", "completed", "fail", 11.0, 12, 5),
            ("b2", "case-1", "p2", "baseline-v1", "baseline", "completed", "completed", "fail", 9.0, 9, 6),
            ("c3", "case-2", "p3", "candidate-v1", "candidate", "executor_error", None, None, None, None, None),
            ("b3", "case-2", "p3", "baseline-v1", "baseline", "completed", "grading_error", None, 8.0, 8, 4),
            ("c4", "case-2", "p4", "candidate-v1", "candidate", "invalid", None, None, None, None, None),
            ("b4", "case-2", "p4", "baseline-v1", "baseline", "completed", "invalid", "invalid", 7.0, None, None),
            ("c5", "case-2", "p5", "candidate-v1", "candidate", "completed", "completed", "pass", 20.0, 100, 20),
            ("c6", "case-2", "p6", "candidate-v1", "candidate", "completed", "completed", "pass", 5.0, None, None),
            ("b6", "case-2", "p6", "baseline-v1", "baseline", "completed", "completed", "pass", 5.0, 11, 4),
        ]
        criterion_for = {"case-1": "criterion-1", "case-2": "criterion-2"}
        digest_for = {"candidate-v1": digest_a, "baseline-v1": None}
        entries = []
        for (
            run_id, case_id, pair_id, config_id, role, status, grade_status,
            verdict, duration, input_tokens, output_tokens,
        ) in definitions:
            run_dir = root / "runs" / case_id / pair_id / role
            run_dir.mkdir(parents=True, exist_ok=True)
            transcript = None
            if status == "completed":
                transcript = "transcript.md"
                (run_dir / transcript).write_text(f"transcript {run_id}\n", encoding="utf-8")
            artifact_path = None
            artifacts = []
            if run_id == "c1":
                artifact_path = run_dir / "outputs" / "result.txt"
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                artifact_path.write_text("result\n", encoding="utf-8")
                artifacts = [{
                    "path": "outputs/result.txt",
                    "sha256": _file_digest(artifact_path),
                    "media_type": "text/plain",
                }]
            total_tokens = (
                None if input_tokens is None or output_tokens is None
                else input_tokens + output_tokens
            )
            run = {
                "schema_version": SCHEMA_VERSION, "run_id": run_id,
                "suite_id": suite["suite_id"], "case_id": case_id,
                "configuration_id": config_id, "role": role, "pair_id": pair_id,
                "skill_digest": digest_for[config_id],
                "executor": {"name": "self-test", "version": "1"},
                "model": {"name": "fixed", "settings": {}},
                "harness": {"name": "in-process", "version": "1"},
                "artifacts": artifacts, "transcript_path": transcript,
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": (
                    None if duration is None
                    else f"2026-01-01T00:00:{int(duration):02d}Z"
                ),
                "duration_seconds": duration,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "total_tokens": total_tokens, "status": status,
                "error": (
                    None if status == "completed"
                    else {"code": status, "message": status}
                ),
            }
            run_path = run_dir / "run.json"
            _atomic_json(run_path, run)
            entry = {"run_manifest": run_path.relative_to(root).as_posix()}
            if grade_status is not None:
                grading = {
                    "schema_version": SCHEMA_VERSION, "grading_id": "g-" + run_id,
                    "run_id": run_id, "suite_id": suite["suite_id"], "case_id": case_id,
                    "status": grade_status,
                    "grader": {
                        "type": "model_judge" if run_id == "c1" else "deterministic",
                        "version": "rubric-v1",
                    },
                    "criteria": [] if verdict is None else [{
                        "criterion_id": criterion_for[case_id], "verdict": verdict,
                        "evidence": (
                            [] if verdict == "invalid"
                            else ["grading_manifest:#/criteria/0"]
                        ),
                    }],
                    "claims_checked": ([{
                        "claim": "The result exists.", "evaluation": "verified",
                        "evidence": ["grading_manifest:#/criteria/0"],
                    }] if run_id == "c1" else []),
                    "evaluator_quality_warnings": ([{
                        "code": "limited_evidence", "message": "One artifact was inspected.",
                        "criterion_id": criterion_for[case_id],
                        "evidence": ["grading_manifest:#/criteria/0"],
                    }] if run_id == "c1" else []),
                    "error": (
                        None if grade_status == "completed"
                        else {"code": grade_status, "message": grade_status}
                    ),
                }
                grading_path = run_dir / "grading.json"
                _atomic_json(grading_path, grading)
                entry["grading_manifest"] = grading_path.relative_to(root).as_posix()
            entries.append(entry)
        _atomic_json(
            root / "run-index.json",
            {"schema_version": SCHEMA_VERSION, "suite_id": suite["suite_id"], "runs": entries},
        )
        output = root / "reports" / "benchmark.json"
        first = aggregate(root / "suite.json", root / "run-index.json", 73, 200, output)
        second = aggregate(root / "suite.json", root / "run-index.json", 73, 200, output)
        assert first == second
        assert set(first) == {
            "schema_version", "benchmark_id", "suite_id", "generated_at", "methods",
            "counts", "cases", "aggregates", "findings", "quality_cost",
            "analyzer_notes",
        }
        assert first["counts"] == {
            "indexed_runs": 11, "completed_runs": 9, "executor_error_runs": 1,
            "invalid_runs": 1, "grading_completed_runs": 7,
            "grading_error_runs": 1, "grading_invalid_runs": 1,
            "grading_missing_runs": 2, "quality_included_runs": 7,
            "quality_excluded_runs": 4,
        }
        assert first["cases"][0]["pairs"][0]["quality_delta"] == 1.0
        assert first["cases"][0]["paired_quality"]["included_pair_count"] == 2
        assert first["aggregates"]["paired_quality"]["included_pair_count"] == 3
        assert first["aggregates"]["paired_quality"]["excluded_pair_count"] == 3
        assert first["quality_cost"]["quality_delta"]["sample_count"] == 3
        assert first["quality_cost"]["total_tokens_delta"]["sample_count"] == 2
        assert first["quality_cost"]["input_tokens_delta"]["sample_count"] == 2
        assert first["quality_cost"]["duration_seconds_delta"]["sample_count"] == 3
        assert first["quality_cost"]["duration_seconds_delta"]["mean"] != 20.0
        run_view = first["cases"][0]["configurations"][0]["runs"][0]
        assert run_view["artifacts"][0]["path"].startswith("../runs/")
        assert run_view["claims_checked"][0]["evaluation"] == "verified"
        assert run_view["evaluator_quality_warnings"][0]["code"] == "limited_evidence"
        assert set(first["quality_cost"]["total_tokens_delta"]) == {
            "sample_count", "mean", "sample_stddev", "bootstrap_interval"
        }
        try:
            _manifest_path(root / "run-index.json", "../escape.json", "escape")
        except SchemaError:
            pass
        else:
            raise AssertionError("path escape was not rejected")
        bad_suite = json.loads(json.dumps(suite))
        bad_suite["extra"] = True
        try:
            _validate_suite(root / "suite.json", bad_suite)
        except SchemaError:
            pass
        else:
            raise AssertionError("extra suite field was not rejected")
        bad_digest = json.loads(json.dumps(suite))
        bad_digest["configurations"][0]["skill_digest"] = "sha256:short"
        try:
            _validate_suite(root / "suite.json", bad_digest)
        except SchemaError:
            pass
        else:
            raise AssertionError("invalid digest was not rejected")
        noncompleted_run = _load_json(
            root / "runs" / "case-2" / "p3" / "candidate" / "run.json",
            "run.json",
        )
        impossible_grading = {
            "schema_version": SCHEMA_VERSION, "grading_id": "g-impossible",
            "run_id": noncompleted_run["run_id"], "suite_id": suite["suite_id"],
            "case_id": noncompleted_run["case_id"], "status": "completed",
            "grader": {"type": "model_judge", "version": "rubric-v1"},
            "criteria": [{
                "criterion_id": "criterion-2", "verdict": "pass",
                "evidence": ["run_manifest:#/status"],
            }],
            "claims_checked": [], "evaluator_quality_warnings": [], "error": None,
        }
        try:
            _validate_grading(
                impossible_grading, noncompleted_run, suite["cases"][1], set()
            )
        except SchemaError:
            pass
        else:
            raise AssertionError("completed grading for a non-completed run was accepted")
        _atomic_json(root / "benchmark-a.json", first)
        _atomic_json(root / "benchmark-b.json", second)
        assert (root / "benchmark-a.json").read_bytes() == (root / "benchmark-b.json").read_bytes()

        stream_root = root / "bootstrap-stream"
        stream_root.mkdir()
        stream_suite = json.loads(json.dumps(suite))
        stream_suite["suite_id"] = "bootstrap-stream-self-test"
        _atomic_json(stream_root / "suite.json", stream_suite)
        stream_definitions = [
            ("case-1", "p1", "candidate", "pass", 4.0, 10, 5, "completed", "completed"),
            ("case-1", "p1", "baseline", "fail", 6.0, 8, 7, "completed", "completed"),
            ("case-1", "p2", "candidate", "fail", 8.0, None, None, "completed", "completed"),
            ("case-1", "p2", "baseline", "fail", 5.0, None, None, "completed", "completed"),
            ("case-1", "p3", "candidate", "pass", 7.0, 12, 8, "completed", "completed"),
            ("case-1", "p3", "baseline", "pass", 9.0, 10, 9, "completed", "completed"),
            ("case-2", "p4", "candidate", None, None, None, None, "executor_error", None),
            ("case-2", "p4", "baseline", None, 3.0, 5, 2, "completed", "grading_error"),
            ("case-2", "p5", "candidate", "pass", 50.0, 100, 20, "completed", "completed"),
            ("case-2", "p5", "baseline", "fail", 2.0, 4, 2, "completed", "completed"),
        ]
        stream_entries = []
        for (
            case_id, pair_id, role, verdict, duration, input_tokens, output_tokens,
            status, grade_status,
        ) in stream_definitions:
            run_id = f"stream-{pair_id}-{role}"
            config_id = f"{role}-v1"
            run_dir = stream_root / "runs" / case_id / pair_id / role
            run_dir.mkdir(parents=True)
            transcript = None
            if status == "completed":
                transcript = "transcript.md"
                (run_dir / transcript).write_text(
                    f"bootstrap stream transcript {run_id}\n", encoding="utf-8"
                )
            total_tokens = (
                None if input_tokens is None or output_tokens is None
                else input_tokens + output_tokens
            )
            run = {
                "schema_version": SCHEMA_VERSION, "run_id": run_id,
                "suite_id": stream_suite["suite_id"], "case_id": case_id,
                "configuration_id": config_id, "role": role, "pair_id": pair_id,
                "skill_digest": digest_for[config_id],
                "executor": {"name": "self-test", "version": "1"},
                "model": {"name": "fixed", "settings": {}},
                "harness": {"name": "in-process", "version": "1"},
                "artifacts": [], "transcript_path": transcript,
                "started_at": "2026-01-02T00:00:00Z",
                "ended_at": (
                    None if duration is None
                    else f"2026-01-02T00:00:{int(duration):02d}Z"
                ),
                "duration_seconds": duration,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "total_tokens": total_tokens, "status": status,
                "error": (
                    None if status == "completed"
                    else {"code": status, "message": status}
                ),
            }
            run_path = run_dir / "run.json"
            _atomic_json(run_path, run)
            entry = {"run_manifest": run_path.relative_to(stream_root).as_posix()}
            if grade_status is not None:
                grading = {
                    "schema_version": SCHEMA_VERSION, "grading_id": "g-" + run_id,
                    "run_id": run_id, "suite_id": stream_suite["suite_id"],
                    "case_id": case_id, "status": grade_status,
                    "grader": {"type": "deterministic", "version": "rubric-v1"},
                    "criteria": [] if verdict is None else [{
                        "criterion_id": criterion_for[case_id], "verdict": verdict,
                        "evidence": ["grading_manifest:#/criteria/0"],
                    }],
                    "claims_checked": [], "evaluator_quality_warnings": [],
                    "error": (
                        None if grade_status == "completed"
                        else {"code": grade_status, "message": grade_status}
                    ),
                }
                grading_path = run_dir / "grading.json"
                _atomic_json(grading_path, grading)
                entry["grading_manifest"] = grading_path.relative_to(stream_root).as_posix()
            stream_entries.append(entry)
        _atomic_json(
            stream_root / "run-index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "suite_id": stream_suite["suite_id"],
                "runs": stream_entries,
            },
        )
        stream_benchmark = aggregate(
            stream_root / "suite.json", stream_root / "run-index.json",
            47, 96, stream_root / "reports" / "benchmark.json",
        )
        aggregate_paired = stream_benchmark["aggregates"]["paired_quality"]["statistics"]
        quality_cost = stream_benchmark["quality_cost"]
        assert len(stream_benchmark["cases"]) == 2
        assert sum(len(case["pairs"]) for case in stream_benchmark["cases"]) == 5
        assert aggregate_paired == {
            "sample_count": 4, "mean": 0.5, "sample_stddev": 0.57735,
            "bootstrap_interval": {"lower": 0.0, "upper": 0.90625},
        }
        assert quality_cost["quality_delta"] == {
            "sample_count": 4, "mean": 0.5, "sample_stddev": 0.57735,
            "bootstrap_interval": {"lower": 0.0, "upper": 1.0},
        }
        assert quality_cost["quality_delta"] is not aggregate_paired
        assert quality_cost["duration_seconds_delta"] == {
            "sample_count": 4, "mean": 11.75, "sample_stddev": 24.281337,
            "bootstrap_interval": {"lower": -2.0, "upper": 31.75},
        }
        assert quality_cost["input_tokens_delta"] == {
            "sample_count": 3, "mean": 33.333333, "sample_stddev": 54.270925,
            "bootstrap_interval": {"lower": 2.0, "upper": 64.666667},
        }
        assert quality_cost["output_tokens_delta"] == {
            "sample_count": 3, "mean": 5.0, "sample_stddev": 11.269428,
            "bootstrap_interval": {"lower": -2.0, "upper": 11.666667},
        }
        assert quality_cost["total_tokens_delta"] == {
            "sample_count": 3, "mean": 38.333333, "sample_stddev": 65.531163,
            "bootstrap_interval": {"lower": 0.333333, "upper": 76.333333},
        }
    print("[OK] aggregate_benchmark self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate manifests and aggregate paired Codex skill benchmarks."
    )
    parser.add_argument("--suite", type=Path, help="Path to suite.json")
    parser.add_argument("--run-index", type=Path, help="Path to run-index.json")
    parser.add_argument("--output", type=Path, help="Output benchmark.json")
    parser.add_argument("--seed", type=int, default=0, help="Deterministic bootstrap seed")
    parser.add_argument(
        "--bootstrap-samples", type=int, default=1000,
        help="Bootstrap resamples; use 0 to disable intervals",
    )
    parser.add_argument("--self-test", action="store_true", help="Run in-process golden tests")
    args = parser.parse_args()
    if args.self_test:
        try:
            _self_test()
            return 0
        except (AssertionError, OSError, SchemaError) as exc:
            print(f"[ERROR] aggregate_benchmark self-test failed: {exc}", file=sys.stderr)
            return 1
    if args.suite is None or args.run_index is None or args.output is None:
        parser.error("--suite, --run-index, and --output are required unless --self-test is used")
    if args.bootstrap_samples < 0:
        parser.error("--bootstrap-samples must be nonnegative")
    try:
        output = args.output.resolve()
        benchmark = aggregate(
            args.suite.resolve(), args.run_index.resolve(),
            args.seed, args.bootstrap_samples, output,
        )
        _atomic_json(output, benchmark)
    except (OSError, SchemaError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] Wrote benchmark: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
