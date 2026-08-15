# Mistakes

Log mistakes (what happened, root cause, prevention).

## 2026-08-15 — `git check-ignore` on a missing path

- What happened: `git check-ignore -q .worktrees` reported "not ignored" before the directory existed, even though `.gitignore` already had `.worktrees/`.
- Root cause: `check-ignore` was run against a path that did not exist yet; the ignore rule is directory-based.
- Prevention: Create or `mkdir` the ignore target first, or verify the rule with `git check-ignore -v` after the directory exists.
