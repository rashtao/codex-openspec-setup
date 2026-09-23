#!/usr/bin/env python3
"""Validate a completed Codex skill without modifying it."""

# Adapted from the installed OpenAI skill-creator validator and modified for
# the current Codex frontmatter, metadata, and completed-scaffold contracts.

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterator
from urllib.parse import unquote

import yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_BODY_LINES = 499
MAX_INTERFACE_NAME_LENGTH = 64
MAX_INTERFACE_TEXT_LENGTH = 1024
MAX_DEPENDENCY_TYPE_LENGTH = 64
MAX_DEPENDENCY_TRANSPORT_LENGTH = 64
MAX_DEPENDENCY_TEXT_LENGTH = 1024
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCHEME_PATTERN = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
MARKER = "AUTHORING-MARKER"
UNFINISHED_PATTERN = re.compile(
    r"\b(?:" + "|".join(("TO" + "DO", "FIX" + "ME", "T" + "BD")) + r")\b",
    re.IGNORECASE,
)
FRONTMATTER_KEYS = {"description", "metadata", "model", "name"}
INTERFACE_KEYS = {
    "brand_color",
    "default_prompt",
    "display_name",
    "icon_large",
    "icon_small",
    "short_description",
}
DEPENDENCY_TOOL_KEYS = {
    "command",
    "description",
    "oauth",
    "transport",
    "type",
    "url",
    "value",
}
PRODUCTS = {"atlas", "chatgpt", "codex", "ATLAS", "CHATGPT", "CODEX"}


def _extract_frontmatter(content: str) -> tuple[str, str] | None:
    normalized = content.replace("\r\n", "\n")
    match = re.match(
        r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", normalized, re.DOTALL
    )
    if not match:
        return None
    return match.group(1), normalized[match.end() :]


def _type_name(value: Any) -> str:
    return type(value).__name__


def _unexpected_keys(
    value: dict[Any, Any], supported: set[str], label: str
) -> list[str]:
    unexpected = sorted(str(key) for key in set(value) - supported)
    if not unexpected:
        return []
    return [f"{label}: unexpected key(s): " + ", ".join(unexpected)]


def _validate_optional_string(
    value: Any, label: str, maximum: int, *, allow_null: bool = False
) -> list[str]:
    if value is None and allow_null:
        return []
    if not isinstance(value, str):
        return [f"{label} must be a string, got {_type_name(value)}"]
    normalized = " ".join(value.split())
    if not normalized:
        return [f"{label} must be non-empty"]
    if len(normalized) > maximum:
        return [f"{label} exceeds {maximum} characters"]
    return []


def _iter_inline_link_targets(content: str) -> Iterator[str]:
    """Yield inline Markdown link/image destinations, including nested parentheses."""
    cursor = 0
    while True:
        marker = content.find("](", cursor)
        if marker < 0:
            return
        index = marker + 2
        while index < len(content) and content[index] in " \t\r\n":
            index += 1
        if index >= len(content):
            return

        target: list[str] = []
        if content[index] == "<":
            index += 1
            while index < len(content):
                character = content[index]
                if character == "\\" and index + 1 < len(content):
                    target.append(content[index + 1])
                    index += 2
                    continue
                if character == ">":
                    break
                target.append(character)
                index += 1
        else:
            depth = 1
            while index < len(content):
                character = content[index]
                if character == "\\" and index + 1 < len(content):
                    target.append(content[index + 1])
                    index += 2
                    continue
                if character == "(":
                    depth += 1
                elif character == ")":
                    depth -= 1
                    if depth == 0:
                        break
                elif character.isspace() and depth == 1:
                    break
                target.append(character)
                index += 1
        if target:
            yield "".join(target)
        cursor = marker + 2


def validate_links(skill_dir: Path, content: str) -> list[str]:
    """Validate direct local links from ``SKILL.md``."""
    errors: list[str] = []
    root = skill_dir.resolve()
    for raw_target in _iter_inline_link_targets(content):
        target = raw_target.strip()
        if (
            not target
            or target.startswith("#")
            or target.startswith("//")
            or SCHEME_PATTERN.match(target)
        ):
            continue
        path_text = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not path_text:
            continue
        if "\\" in path_text:
            errors.append(f"SKILL.md: local link must use forward slashes: {raw_target}")
            continue
        try:
            resolved = (root / path_text).resolve()
            resolved.relative_to(root)
        except (OSError, RuntimeError, ValueError):
            errors.append(f"SKILL.md: local link escapes the skill directory: {raw_target}")
            continue
        if not resolved.exists():
            errors.append(f"SKILL.md: linked path does not exist: {path_text}")
    return errors


def _load_yaml_mapping(
    path: Path, label: str
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return None, [f"{label}: invalid YAML: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}: expected a YAML mapping"]
    return value, []


def _validate_icon(skill_dir: Path, key: str, value: str) -> list[str]:
    label = f"agents/openai.yaml: interface.{key}"
    if "\\" in value:
        return [f"{label} must use forward slashes"]
    relative = PurePosixPath(value)
    parts = relative.parts
    if relative.is_absolute() or ".." in parts or not parts:
        return [f"{label} must be a relative path beneath assets/"]
    normalized_parts = parts[1:] if parts[0] == "." else parts
    if not normalized_parts or normalized_parts[0] != "assets":
        return [f"{label} must be a relative path beneath assets/"]
    try:
        assets_root = (skill_dir / "assets").resolve()
        resolved = (skill_dir / Path(*normalized_parts)).resolve()
        resolved.relative_to(assets_root)
    except (OSError, RuntimeError, ValueError):
        return [f"{label} escapes the skill assets directory"]
    if not resolved.is_file():
        return [f"{label} file does not exist: {value}"]
    return []


def _validate_interface(value: Any, skill_dir: Path) -> list[str]:
    label = "agents/openai.yaml: interface"
    if value is None:
        return []
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    errors = _unexpected_keys(value, INTERFACE_KEYS, label)
    for key, field_value in value.items():
        if key not in INTERFACE_KEYS:
            continue
        maximum = (
            MAX_INTERFACE_NAME_LENGTH if key == "display_name" else MAX_INTERFACE_TEXT_LENGTH
        )
        field_errors = _validate_optional_string(field_value, f"{label}.{key}", maximum)
        errors.extend(field_errors)
        if field_errors or not isinstance(field_value, str):
            continue
        if key == "brand_color" and not COLOR_PATTERN.fullmatch(field_value.strip()):
            errors.append(f"{label}.brand_color must use #RRGGBB syntax")
        if key in {"icon_small", "icon_large"}:
            errors.extend(_validate_icon(skill_dir, key, field_value.strip()))
    return errors


def _validate_dependency_tool(value: Any, index: int) -> list[str]:
    label = f"agents/openai.yaml: dependencies.tools[{index}]"
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    errors = _unexpected_keys(value, DEPENDENCY_TOOL_KEYS, label)
    for required in ("type", "value"):
        if required not in value:
            errors.append(f"{label}.{required} is required")
    string_limits = {
        "type": MAX_DEPENDENCY_TYPE_LENGTH,
        "value": MAX_DEPENDENCY_TEXT_LENGTH,
        "description": MAX_DEPENDENCY_TEXT_LENGTH,
        "transport": MAX_DEPENDENCY_TRANSPORT_LENGTH,
        "command": MAX_DEPENDENCY_TEXT_LENGTH,
        "url": MAX_DEPENDENCY_TEXT_LENGTH,
    }
    for key, maximum in string_limits.items():
        if key in value:
            errors.extend(_validate_optional_string(value[key], f"{label}.{key}", maximum))

    kind = value.get("type")
    if isinstance(kind, str) and kind.strip().lower() != "mcp":
        errors.append(f"{label}.type must be 'mcp'")
    transport = value.get("transport", "streamable_http")
    if isinstance(transport, str):
        normalized_transport = transport.strip().lower()
        if normalized_transport not in {"stdio", "streamable_http"}:
            errors.append(f"{label}.transport must be 'stdio' or 'streamable_http'")
        required_endpoint = "command" if normalized_transport == "stdio" else "url"
        if (
            normalized_transport in {"stdio", "streamable_http"}
            and required_endpoint not in value
        ):
            errors.append(
                f"{label}.{required_endpoint} is required for {normalized_transport} transport"
            )

    if "oauth" in value:
        oauth = value["oauth"]
        oauth_label = f"{label}.oauth"
        if not isinstance(oauth, dict):
            errors.append(f"{oauth_label} must be a mapping")
        else:
            errors.extend(
                _unexpected_keys(oauth, {"callbackPort", "callback_port"}, oauth_label)
            )
            if "callbackPort" in oauth and "callback_port" in oauth:
                errors.append(
                    f"{oauth_label} cannot contain both callbackPort and callback_port"
                )
            for key in ("callbackPort", "callback_port"):
                if key not in oauth:
                    continue
                port = oauth[key]
                if (
                    isinstance(port, bool)
                    or not isinstance(port, int)
                    or not 0 <= port <= 65535
                ):
                    errors.append(
                        f"{oauth_label}.{key} must be an integer from 0 through 65535"
                    )
    return errors


def _validate_dependencies(value: Any) -> list[str]:
    label = "agents/openai.yaml: dependencies"
    if value is None:
        return []
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    errors = _unexpected_keys(value, {"tools"}, label)
    tools = value.get("tools", [])
    if not isinstance(tools, list):
        errors.append(f"{label}.tools must be a list")
        return errors
    for index, tool in enumerate(tools):
        errors.extend(_validate_dependency_tool(tool, index))
    return errors


def _validate_policy(value: Any) -> list[str]:
    label = "agents/openai.yaml: policy"
    if value is None:
        return []
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    errors = _unexpected_keys(value, {"allow_implicit_invocation", "products"}, label)
    if "allow_implicit_invocation" in value and not isinstance(
        value["allow_implicit_invocation"], bool
    ):
        errors.append(f"{label}.allow_implicit_invocation must be Boolean")
    if "products" in value:
        products = value["products"]
        if not isinstance(products, list):
            errors.append(f"{label}.products must be a list")
        else:
            for index, product in enumerate(products):
                if not isinstance(product, str) or product not in PRODUCTS:
                    errors.append(
                        f"{label}.products[{index}] must be atlas, chatgpt, or codex"
                    )
    return errors


def validate_openai_yaml(path: Path, skill_dir: Path) -> list[str]:
    """Validate the current Codex ``agents/openai.yaml`` schema when present."""
    data, errors = _load_yaml_mapping(path, "agents/openai.yaml")
    if data is None:
        return errors
    errors.extend(
        _unexpected_keys(
            data, {"dependencies", "interface", "policy"}, "agents/openai.yaml"
        )
    )
    if "interface" in data:
        errors.extend(_validate_interface(data["interface"], skill_dir))
    if "dependencies" in data:
        errors.extend(_validate_dependencies(data["dependencies"]))
    if "policy" in data:
        errors.extend(_validate_policy(data["policy"]))
    return errors


def validate_skill(skill_path: str | Path) -> list[str]:
    """Return every structural validation error without writing files."""
    errors: list[str] = []
    directory = Path(skill_path).resolve()
    if not directory.is_dir():
        return [f"Skill directory not found: {directory}"]
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md not found"]
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read SKILL.md: {exc}"]

    extracted = _extract_frontmatter(content)
    if extracted is None:
        return ["Invalid SKILL.md frontmatter format"]
    frontmatter_text, body = extracted
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        return [f"Invalid YAML in SKILL.md frontmatter: {exc}"]
    if not isinstance(frontmatter, dict):
        return ["SKILL.md frontmatter must be a YAML mapping"]

    errors.extend(_unexpected_keys(frontmatter, FRONTMATTER_KEYS, "SKILL.md frontmatter"))
    for required in ("name", "description"):
        if required not in frontmatter:
            errors.append(f"SKILL.md frontmatter missing: {required}")

    name = frontmatter.get("name")
    if not isinstance(name, str):
        errors.append(f"SKILL.md name must be a string, got {_type_name(name)}")
    else:
        name = name.strip()
        if not name:
            errors.append("SKILL.md name must be non-empty")
        elif len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"SKILL.md name exceeds {MAX_SKILL_NAME_LENGTH} characters")
        elif not NAME_PATTERN.fullmatch(name):
            errors.append(
                "SKILL.md name must use lowercase ASCII letters, digits, and single hyphens"
            )
        elif directory.name != name:
            errors.append(
                f"skill folder name {directory.name!r} does not match frontmatter name {name!r}"
            )

    description = frontmatter.get("description")
    description_errors = _validate_optional_string(
        description, "SKILL.md description", MAX_DESCRIPTION_LENGTH
    )
    errors.extend(description_errors)
    if not description_errors and isinstance(description, str) and (
        "<" in description or ">" in description
    ):
        errors.append("SKILL.md description cannot contain angle brackets")

    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if not isinstance(metadata, dict):
            errors.append("SKILL.md metadata must be a mapping")
        else:
            errors.extend(
                _unexpected_keys(metadata, {"short-description"}, "SKILL.md metadata")
            )
            if "short-description" in metadata:
                errors.extend(
                    _validate_optional_string(
                        metadata["short-description"],
                        "SKILL.md metadata.short-description",
                        MAX_DESCRIPTION_LENGTH,
                        allow_null=True,
                    )
                )
    if "model" in frontmatter and frontmatter["model"] not in (None, "luna"):
        errors.append("SKILL.md model must be 'luna' when provided")

    if not body.strip():
        errors.append("SKILL.md body must be non-empty")
    body_lines = len(body.splitlines())
    if body_lines > MAX_SKILL_BODY_LINES:
        errors.append(
            f"SKILL.md body must be below 500 lines (got {body_lines})"
        )
    if UNFINISHED_PATTERN.search(content) or MARKER in content:
        errors.append("SKILL.md contains an unfinished authoring marker")

    known_examples = (
        Path("scripts") / "example.py",
        Path("references") / ("api" + "_reference.md"),
        Path("assets") / ("example" + "_asset.txt"),
    )
    for relative in known_examples:
        if (directory / relative).exists():
            errors.append(f"Remove initializer example file: {relative.as_posix()}")
    for resource in ("scripts", "references", "assets"):
        path = directory / resource
        if path.is_dir():
            try:
                if not any(path.iterdir()):
                    errors.append(f"Resource directory is empty: {resource}/")
            except OSError as exc:
                errors.append(f"Cannot inspect resource directory {resource}/: {exc}")

    errors.extend(validate_links(directory, content))
    openai_yaml = directory / "agents" / "openai.yaml"
    if openai_yaml.exists():
        if not openai_yaml.is_file():
            errors.append("agents/openai.yaml must be a file")
        else:
            errors.extend(validate_openai_yaml(openai_yaml, directory))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a completed Codex skill directory without modifying it."
    )
    parser.add_argument("skill_directory", type=Path, help="Path to the skill directory")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors = validate_skill(args.skill_directory)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"[OK] Skill is valid: {args.skill_directory.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
