#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[repo-scan] Checking unresolved markers in runtime package..."
if rg -n --no-heading '\b(TODO|FIXME|XXX|HACK)\b' tempfox; then
	echo "[repo-scan] Unresolved markers found in tempfox/. Remove or address them."
	exit 1
fi

echo "[repo-scan] Checking tracked macOS metadata..."
if git ls-files | rg -n '(^|/)\.DS_Store$'; then
	echo "[repo-scan] Tracked .DS_Store file(s) found."
	exit 1
fi

echo "[repo-scan] Checking stale mem_docs references..."
if rg -n --no-heading 'mem_docs/' tempfox README.md docs .github pyproject.toml --glob '!docs/project-context.md'; then
	echo "[repo-scan] Found stale mem_docs reference outside allowed context docs."
	exit 1
fi

echo "[repo-scan] Repository hygiene checks passed."
