# Codex Hygiene Runbook

This runbook makes cleanup/review work reproducible and low-friction.

## 1) Setup

```bash
uv sync --dev
```

Install local hook automation:

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

## 2) Routine Commands

- Fast local check (before and during edits):

```bash
make hygiene-fast
```

- Full gate (same quality bar as CI + repo scan):

```bash
make hygiene
```

- Safe auto-fixes, then full gate:

```bash
make hygiene-fix
```

## 3) Cleanup/Review Workflow

1. Create isolated branch/worktree (`codex/<task>`).
2. Run `make hygiene-fast` for baseline.
3. For behavior changes: add failing test, then implement minimal fix.
4. Remove dead code only after tests confirm no behavior drift.
5. Run `make hygiene`.
6. Commit only after successful verification.

## 4) What `make hygiene` Enforces

- Ruff lint checks.
- Ruff formatting checks.
- Mypy type checks.
- Pytest with `--cov-fail-under=35`.
- Repository scan for:
  - unresolved `TODO/FIXME/XXX/HACK` markers in `tempfox/`,
  - tracked `.DS_Store` files,
  - stale legacy memory-folder references outside approved context files.
