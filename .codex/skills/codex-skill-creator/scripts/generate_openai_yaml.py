#!/usr/bin/env python3
"""Generate validated agents/openai.yaml metadata for a Codex skill."""

# Adapted from the installed OpenAI skill-creator generator and modified for
# current Codex metadata validation, preservation, and atomic-write rules.

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

MAX_SKILL_NAME_LENGTH = 64
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
ACRONYMS = {"GH", "MCP", "API", "CI", "CLI", "LLM", "PDF", "PR", "UI", "URL", "SQL"}
BRANDS = {
    "openai": "OpenAI", "openapi": "OpenAPI", "github": "GitHub",
    "pagerduty": "PagerDuty", "datadog": "DataDog", "sqlite": "SQLite",
    "fastapi": "FastAPI",
}
SMALL_WORDS = {"and", "or", "to", "up", "with"}
INTERFACE_ORDER = (
    "display_name", "short_description", "icon_small", "icon_large",
    "brand_color", "default_prompt",
)
ALLOWED_INTERFACE_KEYS = set(INTERFACE_ORDER)
PRESERVED_OPTIONAL_KEYS = {"icon_small", "icon_large", "brand_color", "default_prompt"}


class MetadataError(ValueError):
    """A user-facing metadata validation failure."""


def yaml_quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\").replace('"', '\\"')
        .replace("\r", "\\r").replace("\n", "\\n")
    )
    return f'"{escaped}"'


def format_display_name(skill_name: str) -> str:
    formatted: list[str] = []
    for index, word in enumerate(part for part in skill_name.split("-") if part):
        lower, upper = word.lower(), word.upper()
        if upper in ACRONYMS:
            formatted.append(upper)
        elif lower in BRANDS:
            formatted.append(BRANDS[lower])
        elif index > 0 and lower in SMALL_WORDS:
            formatted.append(lower)
        else:
            formatted.append(word.capitalize())
    return " ".join(formatted)


def generate_short_description(display_name: str) -> str:
    description = f"Help with {display_name} tasks"
    if len(description) < 25:
        description = f"Help with {display_name} tasks and workflows"
    if len(description) < 25:
        description = f"Help with {display_name} tasks with guidance"
    if len(description) > 64:
        description = f"Help with {display_name}"
    if len(description) > 64:
        description = f"{display_name} helper"
    if len(description) > 64:
        description = f"{display_name} tools"
    if len(description) > 64:
        suffix = " helper"
        description = f"{display_name[:64 - len(suffix)].rstrip()}{suffix}"
    if len(description) > 64:
        description = description[:64].rstrip()
    if len(description) < 25:
        description = f"{description} workflows"[:64].rstrip()
    return description


def default_prompt(skill_name: str, display_name: str) -> str:
    return "Use $" + skill_name + f" to help with {display_name} tasks."


def validate_skill_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MetadataError("Skill name must be a nonempty string.")
    name = value.strip()
    if len(name) > MAX_SKILL_NAME_LENGTH:
        raise MetadataError(
            f"Skill name is too long ({len(name)} characters); maximum is "
            f"{MAX_SKILL_NAME_LENGTH}."
        )
    if not NAME_RE.fullmatch(name):
        raise MetadataError(
            "Skill name must use lowercase ASCII letters, digits, and single "
            "hyphens without leading or trailing hyphens."
        )
    return name


def _frontmatter_text(content: str) -> str:
    normalized = content.replace("\r\n", "\n")
    match = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", normalized, re.DOTALL)
    if not match:
        raise MetadataError("Invalid SKILL.md frontmatter format.")
    return match.group(1)


def read_frontmatter_name(skill_dir: Path | str) -> str | None:
    skill_md = Path(skill_dir) / "SKILL.md"
    try:
        if not skill_md.is_file():
            raise MetadataError(f"SKILL.md not found in {skill_dir}")
        frontmatter = yaml.safe_load(
            _frontmatter_text(skill_md.read_text(encoding="utf-8"))
        )
        if not isinstance(frontmatter, dict):
            raise MetadataError("Frontmatter must be a YAML mapping.")
        return validate_skill_name(frontmatter.get("name"))
    except (OSError, UnicodeError, yaml.YAMLError, MetadataError) as exc:
        print(f"[ERROR] {exc}")
        return None


def parse_interface_overrides(
    raw_overrides: list[str],
) -> tuple[dict[str, str] | None, list[str] | None]:
    overrides: dict[str, str] = {}
    for item in raw_overrides:
        if "=" not in item:
            print(f"[ERROR] Invalid interface override '{item}'. Use key=value.")
            return None, None
        key, value = item.split("=", 1)
        key, value = key.strip(), value.strip()
        if not key:
            print(f"[ERROR] Invalid interface override '{item}'. Key is empty.")
            return None, None
        if key not in ALLOWED_INTERFACE_KEYS:
            allowed = ", ".join(sorted(ALLOWED_INTERFACE_KEYS))
            print(f"[ERROR] Unknown interface field '{key}'. Allowed: {allowed}")
            return None, None
        overrides[key] = value
    return overrides, list(INTERFACE_ORDER)


def _load_existing_interface(output_path: Path) -> dict[str, str]:
    if not output_path.exists():
        return {}
    if not output_path.is_file():
        raise MetadataError(f"Existing metadata path is not a file: {output_path}")
    try:
        document = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise MetadataError(f"Cannot safely read existing metadata: {exc}") from exc
    if not isinstance(document, dict):
        raise MetadataError("Existing agents/openai.yaml must be a YAML mapping.")
    if set(document) != {"interface"}:
        detail = ", ".join(sorted(set(document) - {"interface"})) or "missing interface"
        raise MetadataError(
            "Refusing to overwrite metadata that is not generator-owned "
            f"interface-only YAML ({detail})."
        )
    interface = document["interface"]
    if not isinstance(interface, dict):
        raise MetadataError("Existing interface must be a YAML mapping.")
    unknown = sorted(set(interface) - ALLOWED_INTERFACE_KEYS)
    if unknown:
        raise MetadataError(
            "Existing interface contains unsupported field(s): " + ", ".join(unknown)
        )
    if any(not isinstance(value, str) for value in interface.values()):
        raise MetadataError("Every existing interface value must be a string.")
    return dict(interface)


def _validate_icon(skill_dir: Path, key: str, value: str) -> None:
    if not value.startswith("./assets/") or "\\" in value:
        raise MetadataError(f"{key} must be a skill-relative ./assets/ path.")
    relative = PurePosixPath(value[2:])
    if relative.is_absolute() or ".." in relative.parts or relative.name in {"", "."}:
        raise MetadataError(f"{key} must not escape the skill assets directory.")
    assets_root = (skill_dir / "assets").resolve()
    icon_path = (skill_dir / Path(*relative.parts)).resolve()
    try:
        icon_path.relative_to(assets_root)
    except ValueError as exc:
        raise MetadataError(f"{key} must remain inside ./assets/.") from exc
    if not icon_path.is_file():
        raise MetadataError(f"{key} does not name an existing file: {value}")


def _prepare_interface(
    skill_dir: Path, skill_name: str, raw_overrides: list[str],
    existing: dict[str, str] | None = None,
) -> dict[str, str] | None:
    overrides, _ = parse_interface_overrides(raw_overrides)
    if overrides is None:
        return None
    name = validate_skill_name(skill_name)
    existing = existing or {}
    values = {"display_name": overrides.get("display_name", format_display_name(name))}
    values["short_description"] = overrides.get(
        "short_description", generate_short_description(values["display_name"])
    )
    for key in PRESERVED_OPTIONAL_KEYS:
        if key in overrides:
            values[key] = overrides[key]
        elif key in existing:
            values[key] = existing[key]
    values.setdefault("default_prompt", default_prompt(name, values["display_name"]))

    if not values["display_name"].strip():
        raise MetadataError("display_name must be nonempty.")
    if not (25 <= len(values["short_description"]) <= 64):
        raise MetadataError(
            f"short_description must be 25-64 characters "
            f"(got {len(values['short_description'])})."
        )
    prompt_token = "$" + name
    if not values["default_prompt"].strip() or prompt_token not in values["default_prompt"]:
        raise MetadataError(f"default_prompt must contain {prompt_token}.")
    if "brand_color" in values and not COLOR_RE.fullmatch(values["brand_color"]):
        raise MetadataError("brand_color must use #RRGGBB syntax.")
    for key in ("icon_small", "icon_large"):
        if key in values:
            _validate_icon(skill_dir, key, values[key])
    return values


def validate_interface_arguments(
    skill_dir: Path | str, skill_name: str, raw_overrides: list[str]
) -> bool:
    try:
        return _prepare_interface(Path(skill_dir), skill_name, raw_overrides, {}) is not None
    except MetadataError as exc:
        print(f"[ERROR] {exc}")
        return False


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        try:
            temporary_path.unlink()
        except OSError:
            pass
        raise


def write_openai_yaml(
    skill_dir: Path | str, skill_name: str, raw_overrides: list[str]
) -> Path | None:
    directory = Path(skill_dir)
    output_path = directory / "agents" / "openai.yaml"
    try:
        name = validate_skill_name(skill_name)
        values = _prepare_interface(
            directory, name, raw_overrides, _load_existing_interface(output_path)
        )
        if values is None:
            return None
        lines = ["interface:"]
        for key in INTERFACE_ORDER:
            if key in values:
                lines.append(f"  {key}: {yaml_quote(values[key])}")
        _atomic_write_text(output_path, "\n".join(lines) + "\n")
        print("[OK] Created agents/openai.yaml")
        return output_path
    except (OSError, UnicodeError, yaml.YAMLError, MetadataError) as exc:
        print(f"[ERROR] {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create validated agents/openai.yaml for a skill directory."
    )
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--name", help="Skill name override (defaults to SKILL.md)")
    parser.add_argument(
        "--interface", action="append", default=[],
        help="Interface override in key=value format (repeatable)",
    )
    args = parser.parse_args()
    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        print(f"[ERROR] Skill directory not found: {skill_dir}")
        return 1
    skill_name = args.name if args.name is not None else read_frontmatter_name(skill_dir)
    if skill_name is None:
        return 1
    try:
        skill_name = validate_skill_name(skill_name)
    except MetadataError as exc:
        print(f"[ERROR] {exc}")
        return 1
    return 0 if write_openai_yaml(skill_dir, skill_name, args.interface) else 1


if __name__ == "__main__":
    sys.exit(main())

