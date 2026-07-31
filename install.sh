#!/usr/bin/env bash
set -euo pipefail

if [ -e "openspec" ] || [ -L "openspec" ]; then
  printf '%s\n' 'OpenSpec installation aborted: openspec directory already exists.' >&2
  exit 1
fi

if [ -L ".codex" ]; then
  printf '%s\n' 'OpenSpec installation aborted: .codex directory is a symlink.' >&2
  exit 1
fi
if [ -L ".codex/skills" ]; then
  printf '%s\n' 'OpenSpec installation aborted: .codex/skills directory is a symlink.' >&2
  exit 1
fi

for skill_directory in .codex/skills/openspec-*; do
  if [ -e "$skill_directory" ] || [ -L "$skill_directory" ]; then
    printf '%s\n' 'OpenSpec installation aborted: OpenSpec skills already exist.' >&2
    exit 1
  fi
done

for required_command in bash curl tar; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'OpenSpec installation aborted: required command not found: %s\n' "$required_command" >&2
    exit 1
  fi
done

temporary_directory=$(mktemp -d "${TMPDIR:-/tmp}/codex-openspec-setup.XXXXXX")
installation_complete=false
created_skill_paths=()
created_openspec=
created_codex_directory=false
created_skills_directory=false
active_child=
cleanup() {
  if ! "$installation_complete"; then
    if [ -n "$created_openspec" ]; then
      rm -rf "$created_openspec"
    fi
    for created_skill_path in "${created_skill_paths[@]}"; do
      rm -rf "$created_skill_path"
    done
    if "$created_skills_directory"; then
      rmdir .codex/skills 2>/dev/null || true
    fi
    if "$created_codex_directory"; then
      rmdir .codex 2>/dev/null || true
    fi
  fi
  rm -rf "$temporary_directory"
}
interrupt() {
  if [ -n "$active_child" ]; then
    kill -TERM "$active_child" 2>/dev/null || true
    wait "$active_child" 2>/dev/null || true
  fi
  exit 130
}
trap cleanup EXIT
trap interrupt INT TERM

release_metadata_file="$temporary_directory/release.json"
curl -fsSL 'https://api.github.com/repos/rashtao/codex-openspec-setup/releases/latest' > "$release_metadata_file" &
active_child=$!
if ! wait "$active_child"; then
  active_child=
  printf '%s\n' 'OpenSpec installation aborted: could not fetch latest release metadata.' >&2
  exit 1
fi
active_child=
release_metadata=$(<"$release_metadata_file")
source_archive_url=$(printf '%s\n' "$release_metadata" | sed -n 's/.*"tarball_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
if [ -z "$source_archive_url" ]; then
  printf '%s\n' 'OpenSpec installation aborted: latest release metadata contains no source tarball URL.' >&2
  exit 1
fi

source_archive="$temporary_directory/release.tar.gz"
curl -fsSL "$source_archive_url" -o "$source_archive" &
active_child=$!
if ! wait "$active_child"; then
  active_child=
  printf '%s\n' 'OpenSpec installation aborted: could not download the release source archive.' >&2
  exit 1
fi
active_child=

extracted_directory="$temporary_directory/extracted"
mkdir "$extracted_directory"
if ! tar -xzf "$source_archive" -C "$extracted_directory"; then
  printf '%s\n' 'OpenSpec installation aborted: could not extract the release source archive.' >&2
  exit 1
fi

release_directory=
for candidate in "$extracted_directory"/*; do
  if [ -d "$candidate/.codex/skills" ] && [ -d "$candidate/openspec" ]; then
    release_directory=$candidate
    break
  fi
done
if [ -z "$release_directory" ]; then
  printf '%s\n' 'OpenSpec installation aborted: release archive is missing OpenSpec content.' >&2
  exit 1
fi

installed_skills=()
for skill_directory in "$release_directory/.codex/skills"/openspec-*; do
  if [ -d "$skill_directory" ]; then
    installed_skills+=("$(basename "$skill_directory")")
  fi
done
if [ "${#installed_skills[@]}" -eq 0 ]; then
  printf '%s\n' 'OpenSpec installation aborted: release archive contains no OpenSpec skills.' >&2
  exit 1
fi
for skill_name in "${installed_skills[@]}"; do
  skill_directory="$release_directory/.codex/skills/$skill_name"
  if [ -L "$skill_directory" ] || [ ! -f "$skill_directory/SKILL.md" ] || [ -L "$skill_directory/SKILL.md" ] || [ -n "$(find "$skill_directory" -type l -print -quit)" ]; then
    printf 'OpenSpec installation aborted: release archive contains invalid skill %s.\n' "$skill_name" >&2
    exit 1
  fi
done
if [ -L "$release_directory/openspec" ] || [ ! -f "$release_directory/openspec/config.yaml" ] || [ -L "$release_directory/openspec/config.yaml" ] || [ -n "$(find "$release_directory/openspec" -type l -print -quit)" ]; then
  printf '%s\n' 'OpenSpec installation aborted: release archive contains invalid openspec content.' >&2
  exit 1
fi

if [ ! -d .codex ]; then
  mkdir .codex
  created_codex_directory=true
fi
if [ ! -d .codex/skills ]; then
  mkdir .codex/skills
  created_skills_directory=true
fi
for skill_name in "${installed_skills[@]}"; do
  destination_skill=".codex/skills/$skill_name"
  if ! mkdir "$destination_skill"; then
    printf 'OpenSpec installation aborted: OpenSpec skill destination already exists: %s.\n' "$skill_name" >&2
    exit 1
  fi
  created_skill_paths+=("$destination_skill")
  if ! cp -R "$release_directory/.codex/skills/$skill_name/." "$destination_skill"; then
    printf 'OpenSpec installation aborted: could not install skill %s.\n' "$skill_name" >&2
    exit 1
  fi
done
if ! mkdir openspec; then
  printf '%s\n' 'OpenSpec installation aborted: openspec destination already exists.' >&2
  exit 1
fi
created_openspec=openspec
if ! cp -R "$release_directory/openspec/." openspec; then
  printf '%s\n' 'OpenSpec installation aborted: could not install openspec directory.' >&2
  exit 1
fi

installation_complete=true
printf 'Installed OpenSpec skills: %s\n' "${installed_skills[*]}"
printf '%s\n' 'Installed openspec directory.'
printf '%s\n' 'Restart Codex for the installed skills to take effect.'
