#!/usr/bin/env bash
set -euo pipefail

repository_archive_url='https://github.com/rashtao/codex-openspec-setup/archive/refs/heads/main.tar.gz'

for destination in .codex openspec; do
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf 'Installation aborted: %s already exists.\n' "$destination" >&2
    exit 1
  fi
done

for required_command in curl tar; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'Installation aborted: required command not found: %s\n' "$required_command" >&2
    exit 1
  fi
done

temporary_directory=$(mktemp -d "${TMPDIR:-/tmp}/codex-openspec-setup.XXXXXX")
cleanup() {
  rm -rf -- "$temporary_directory"
}
trap cleanup EXIT

archive_path="$temporary_directory/repository.tar.gz"
extraction_directory="$temporary_directory/repository"
mkdir "$extraction_directory"

if ! curl -fsSL "$repository_archive_url" -o "$archive_path"; then
  printf '%s\n' 'Installation aborted: could not download the repository archive.' >&2
  exit 1
fi

if ! tar -xzf "$archive_path" -C "$extraction_directory"; then
  printf '%s\n' 'Installation aborted: could not extract the repository archive.' >&2
  exit 1
fi

release_directory="$extraction_directory/codex-openspec-setup-main/release"
if [ ! -d "$release_directory/.codex" ] || [ ! -d "$release_directory/openspec" ]; then
  printf '%s\n' 'Installation aborted: repository archive is missing release content.' >&2
  exit 1
fi

cp -R "$release_directory/.codex" ./.codex
cp -R "$release_directory/openspec" ./openspec

printf '%s\n' 'Installed .codex and openspec.'
