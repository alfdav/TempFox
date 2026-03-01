#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
	echo "Usage: scripts/run_tool.sh <tool> [args...]" >&2
	exit 1
fi

tool="$1"
shift

candidates=(".venv/bin/$tool")
if common_dir="$(git rev-parse --git-common-dir 2>/dev/null)"; then
	common_root="$(cd "$common_dir/.." && pwd)"
	candidates+=("$common_root/.venv/bin/$tool")
fi

for candidate in "${candidates[@]}"; do
	if [[ -x "$candidate" ]]; then
		exec "$candidate" "$@"
	fi
done

exec env UV_CACHE_DIR=.uv-cache uv run "$tool" "$@"
