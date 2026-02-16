# TempFox Roadmap

Last updated: 2026-02-16

This roadmap keeps the useful ideas from the old TODO and turns them into actionable work with clear done criteria.

## Now (High Priority)

### 1. Credential/session lifecycle hardening
Goal: make AKIA/ASIA flows predictable and safe under failure.

Done criteria:
- ASIA flow validates missing/empty session token with clear remediation guidance.
- Expired-token handling does not recurse into `main()`; uses a controlled retry/exit flow.
- Error messages distinguish auth errors vs tool/runtime errors.
- Tests cover AKIA happy path, ASIA happy path, missing token, and expired token branches.

### 2. Comprehensive test coverage for critical paths
Goal: reduce regressions during refactors.

Done criteria:
- Add tests for `tempfox/aws_profiles.py`, `tempfox/dependencies.py`, and `tempfox/cloudfox.py` critical behaviors.
- Mock `subprocess.run` in tests for AWS CLI, Go, and CloudFox interactions.
- Add CLI-level tests for `--list-profiles`, `--cleanup-profiles`, and `--no-profile` behavior.
- CI remains green with `ruff`, `mypy`, and `pytest`.

### 3. CloudFox run reliability improvements
Goal: make CloudFox execution outcomes easier to trust and debug.

Done criteria:
- Non-zero CloudFox exits are surfaced explicitly (exit code + stderr summary).
- Output file behavior is deterministic for success/failure paths.
- JSON output handling is tested for both valid JSON and raw-text output.
- Cleanup of old output files is covered by tests.

## Next (Medium Priority)

### 4. Credential rotation workflow
Goal: support safer credential refresh without manual file editing.

Done criteria:
- Add an explicit rotation workflow (new command/flag set) for existing TempFox profiles.
- Rotation preserves profile metadata (region/output) unless user overrides.
- Include dry-run mode showing proposed changes.
- Tests cover rotate success, missing profile, and overwrite confirmation paths.

### 5. Audit logging foundation
Goal: provide a minimal audit trail for credential/profile actions.

Done criteria:
- Introduce structured audit events for profile create/update/delete and CloudFox execution start/end.
- Add configurable log target (stdout vs file path).
- Ensure secrets are never logged.
- Tests validate redaction and event shape.

### 6. Preflight/install hardening
Goal: reduce platform-specific installation failures.

Done criteria:
- Improve OS/arch validation and unsupported-platform messages.
- Add timeout/error categorization for AWS CLI, Go, and CloudFox install steps.
- Add tests for platform URL resolution and failure handling.
- Document known prerequisites per OS in README.

## Later (Lower Priority)

### 7. Multi-account orchestration
Goal: run checks across multiple profiles/accounts in one invocation.

Done criteria:
- Accept profile selectors and batch execution strategy.
- Aggregate result index with per-account status.
- Add safety guardrails to avoid accidental broad scans.

### 8. Extensible checks model
Goal: allow incremental addition of non-CloudFox checks.

Done criteria:
- Define a small internal checks interface.
- Implement one additional check type as proof of extensibility.
- Document extension points.

### 9. UX and documentation polish
Goal: reduce operator confusion and setup friction.

Done criteria:
- Add a concise troubleshooting section for common auth/install failures.
- Add examples for AKIA vs ASIA with expected prompts/outputs.
- Keep docs aligned with actual dependencies and module layout.

## Notes

- This file intentionally replaces the old status-style TODO with priority-driven execution items.
- New work should link to issues/PRs under each roadmap item as they are created.
