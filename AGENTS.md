# TempFox Agent Contract

This file defines the execution contract for cleanup/review tasks in this repository.

## Branch Isolation

- Create and use an isolated worktree for non-trivial changes.
- Use branch names prefixed with `codex/`.
- Keep changes scoped to one objective per branch.

## Mandatory Flow For "Cleanup/Review" Requests

1. Baseline:
   - Run `make hygiene-fast` before editing to detect pre-existing issues.
2. Change discipline:
   - If behavior changes, add/adjust a failing test first, then implement.
   - Remove dead code only when behavior is preserved and covered by tests.
3. Verification gate:
   - Run `make hygiene` before claiming completion or creating a commit.
4. Documentation:
   - Update `README.md` and relevant docs when workflow, checks, or commands change.

## Commit Quality Bar

- Do not commit if `make hygiene` fails.
- Commit messages must state the actual behavior/process change.
- Keep commits cohesive; avoid mixing refactors with unrelated fixes.

## Review Deliverables

- Include:
  - Files changed.
  - Verification commands executed.
  - Any residual risks or gaps.
