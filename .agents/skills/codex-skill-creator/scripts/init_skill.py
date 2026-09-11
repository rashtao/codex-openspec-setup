#!/usr/bin/env python3
"""Create a new Codex skill from a bounded authoring scaffold."""

# Adapted from the installed OpenAI skill-creator initializer and modified for
# current Codex transactional creation and scaffold-completion rules.

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from generate_openai_yaml import (
    validate_interface_arguments,
    validate_skill_name,
    write_openai_yaml,
)

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = {"scripts", "references", "assets"}
MARKER = "AUTHORING-MARKER"

SKILL_TEMPLATE = """---
name: {skill_name}
description: "{marker}: Replace this sentence with what the skill does and the concrete tasks that should invoke it."
---

# {skill_title}

{marker}: Replace this bounded scaffold with concise imperative instructions.

## Workflow

1. State the inputs and observable outcome.
2. Describe the smallest reliable workflow.
3. Link only resources that materially support the workflow.

Remove every authoring marker before validation.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Generic removable command-line helper created by the skill initializer."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print supplied text to demonstrate a working skill helper."
    )
    parser.add_argument("--text", default="example helper is ready")
    args = parser.parse_args()
    print(args.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

EXAMPLE_REFERENCE = """# Generic removable reference

Use this file to record stable, task-specific facts that are too detailed for
the main skill instructions. Replace it with useful content or remove it.
"""

EXAMPLE_ASSET = """Generic removable asset scaffold.
Replace this file with an output template or remove the assets directory.
"""


class InputError(ValueError):
    """A handled initializer argument failure."""


def normalize_skill_name(skill_name: str) -> str:
    normalized = skill_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized.strip("-"))
    return normalized


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def parse_resources(raw_resources: str) -> list[str]:
    if not raw_resources:
        return []
    resources = [item.strip() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in resources if item not in ALLOWED_RESOURCES})
    if invalid:
        raise InputError(
            "Unknown resource type(s): " + ", ".join(invalid)
            + ". Allowed: " + ", ".join(sorted(ALLOWED_RESOURCES))
        )
    deduped: list[str] = []
    for resource in resources:
        if resource not in deduped:
            deduped.append(resource)
    return deduped


def _write_staged(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content if content.endswith("\n") else content + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    if mode is not None:
        path.chmod(mode)


def create_resource_dirs(
    skill_dir: Path, skill_name: str, skill_title: str,
    resources: list[str], include_examples: bool,
) -> None:
    del skill_name, skill_title
    for resource in resources:
        resource_dir = skill_dir / resource
        resource_dir.mkdir(exist_ok=False)
        if not include_examples:
            print(f"[OK] Created {resource}/")
            continue
        if resource == "scripts":
            path = resource_dir / "example.py"
            _write_staged(path, EXAMPLE_SCRIPT, 0o755)
            print("[OK] Created removable example script")
        elif resource == "references":
            path = resource_dir / ("api" + "_reference.md")
            _write_staged(path, EXAMPLE_REFERENCE)
            print("[OK] Created removable example reference")
        else:
            path = resource_dir / ("example" + "_asset.txt")
            _write_staged(path, EXAMPLE_ASSET)
            print("[OK] Created removable example asset")


def init_skill(
    skill_name: str,
    path: str | Path,
    resources: list[str],
    include_examples: bool,
    interface_overrides: list[str],
) -> Path | None:
    """Create a skill transactionally, returning its Path or None on failure."""
    try:
        name = validate_skill_name(skill_name)
        if any(resource not in ALLOWED_RESOURCES for resource in resources):
            raise InputError("Resources must be selected from scripts, references, assets.")
        if len(set(resources)) != len(resources):
            raise InputError("Resources must be de-duplicated before initialization.")
        if include_examples and not resources:
            raise InputError("--examples requires --resources to be set.")
        parent = Path(path).resolve()
        target = parent / name
        if target.exists():
            raise InputError(f"Skill directory already exists: {target}")
        if not validate_interface_arguments(target, name, interface_overrides):
            return None
    except (InputError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        return None

    staged: Path | None = None
    try:
        parent.mkdir(parents=True, exist_ok=True)
        staged = Path(tempfile.mkdtemp(prefix=f".{name}.stage-", dir=parent))
        title = title_case_skill_name(name)
        _write_staged(
            staged / "SKILL.md",
            SKILL_TEMPLATE.format(skill_name=name, skill_title=title, marker=MARKER),
        )
        print("[OK] Staged SKILL.md")
        if not write_openai_yaml(staged, name, interface_overrides):
            raise InputError("Could not create agents/openai.yaml.")
        create_resource_dirs(staged, name, title, resources, include_examples)
        if target.exists():
            raise InputError(f"Skill directory appeared during creation: {target}")
        staged.rename(target)
        staged = None
    except (OSError, InputError, ValueError) as exc:
        print(f"[ERROR] Skill creation failed: {exc}")
        if staged is not None and staged.exists():
            shutil.rmtree(staged, ignore_errors=True)
        return None

    print(f"\n[OK] Skill '{name}' initialized successfully at {target}")
    print("\nNext steps:")
    print(f"1. Replace and remove every {MARKER} in SKILL.md.")
    if resources:
        print("2. Replace removable examples or populate every selected resource directory.")
    else:
        print("2. Add resource directories only when the skill needs them.")
    print("3. Run quick_validate.py and exercise every materially distinct script.")
    print("4. Forward-test the completed skill with realistic requests.")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new Codex skill with transactional publication."
    )
    parser.add_argument("skill_name", help="Skill name (normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Parent directory for the skill")
    parser.add_argument(
        "--resources", default="",
        help="Comma-separated list: scripts,references,assets",
    )
    parser.add_argument(
        "--examples", action="store_true",
        help="Create functional removable files in selected resource directories",
    )
    parser.add_argument(
        "--interface", action="append", default=[],
        help="Interface override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    raw_name = args.skill_name
    name = normalize_skill_name(raw_name)
    if not name:
        print("[ERROR] Skill name must include at least one ASCII letter or digit.")
        return 1
    if len(name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] Skill name '{name}' is too long ({len(name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH}."
        )
        return 1
    try:
        resources = parse_resources(args.resources)
    except InputError as exc:
        print(f"[ERROR] {exc}")
        return 1
    if args.examples and not resources:
        print("[ERROR] --examples requires --resources to be set.")
        return 1
    if name != raw_name:
        print(f"Note: Normalized skill name from '{raw_name}' to '{name}'.")
    print(f"Initializing skill: {name}")
    print(f"   Location: {args.path}")
    print(f"   Resources: {', '.join(resources) if resources else 'none'}")
    result = init_skill(name, args.path, resources, args.examples, args.interface)
    return 0 if result is not None else 1


if __name__ == "__main__":
    sys.exit(main())

