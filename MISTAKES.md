# Mistakes

Log mistakes (what happened, root cause, prevention).

## 2026-08-15 — README rewrite left other docs stale

- What happened: The first README cleanup fixed clone URL case and dropped the auto-renewal claim, but `MIGRATION.md` still used `alfdav/tempfox` and `TODO.md` still described a retry flow.
- Root cause: Treated README as the only user-facing surface.
- Prevention: When README facts change, grep the rest of the docs for the same URLs and claims.

## 2026-08-15 — Leftover cleanup after `uv tool install`

- What happened: First-pass docs told users to `rm ~/.local/bin/tempfox` after showing `uv tool install tempfox`, which would delete the UV shim. PATH persistence from the old scripts was also dropped without saying so.
- Root cause: Treated leftover cleanup as an afterthought instead of ordering it before the new install, and assumed preflight replaced persistent PATH.
- Prevention: Clean script-era venvs before `uv tool install`. Never `rm` `~/.local/bin/tempfox` while a UV install is active. Document that preflight PATH is process-only.

## 2026-08-15 — `git check-ignore` on a missing path

- What happened: `git check-ignore -q .worktrees` reported "not ignored" before the directory existed, even though `.gitignore` already had `.worktrees/`.
- Root cause: `check-ignore` was run against a path that did not exist yet; the ignore rule is directory-based.
- Prevention: Create or `mkdir` the ignore target first, or verify the rule with `git check-ignore -v` after the directory exists.
