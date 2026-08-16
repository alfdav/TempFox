# TempFox Roadmap

Last updated: 2026-08-15

Shipped vs open as of `main` @ `eefccea` (merge #4).

## Shipped (Aug 2026)

Evidence: PRs #2, #3, #4.

### PR #2 — Harden credential cleanup and unblock Python CI

- leftover-cleanup safety: installer cleanup only removes paths TempFox registered.
- AKIA empty session token omit (and inherited empty tokens are popped).
- honest delete returns: `delete_aws_profile` is the AND of credentials/config writes.
- expired-token classify on connection test and all-checks. No renewal. No recursive `main()`.
- access-key `getpass` (same as secret/token).
- LICENSE (MIT).
- Codecov best-effort (`codecov-action@v5`, `fail_ci_if_error: false`). No token invented.
- profile / CLI / CloudFox tests (`tests/test_aws_profiles.py`, CLI flags through `main`, JSON vs raw-text, retention).

### PR #3 — UV-only install

- `install.sh` / `install.ps1` / `uninstall.sh` / `uninstall.ps1` removed.
- Install: `uv tool install tempfox`. Remove: `uv tool uninstall tempfox`.
- From source: `uv sync` / `uv run tempfox`.
- Preflight PATH is for the current TempFox process only.

### PR #4 — README rewrite

- No emoji, no hype, one UV install path.
- Flags documented: `--skip-preflight`, `--version`/`-v`, `--list-profiles`, `--cleanup-profiles`, `--no-profile`.
- Clone URL: `https://github.com/alfdav/TempFox`.
- Expired tokens exit. There is no renewal.

Old "Now" items 1–3 (session lifecycle, critical-path tests, CloudFox nonzero/JSON/retention) are done by the above. ASIA empty-token validation (`validate_session_token`) is on main.

## Open

Do not treat these as shipped.

### Credential rotation

Goal: safer credential refresh without manual file editing.

Done criteria (still unmet):
- Explicit rotation workflow (new command/flag set) for existing TempFox profiles.
- Rotation preserves profile metadata (region/output) unless the user overrides.
- Dry-run mode showing proposed changes.
- Tests for rotate success, missing profile, and overwrite confirmation.

No rotation spec file. Do not invent one here.

### Audit logging

Goal: minimal audit trail for credential/profile actions.

Done criteria (still unmet):
- Structured audit events for profile create/update/delete and CloudFox start/end.
- Configurable log target (stdout vs file path).
- Secrets never logged.
- Tests for redaction and event shape.

No audit spec file. Do not invent one here.

### Multi-account

Goal: run checks across multiple profiles/accounts in one invocation.

Done criteria (still unmet):
- Profile selectors and a batch execution strategy.
- Aggregate result index with per-account status.
- Guardrails against accidental broad scans.

No multi-account spec file. Do not invent one here.

### Extensible checks

Goal: add non-CloudFox checks incrementally.

Done criteria (still unmet):
- Small internal checks interface.
- One additional check type as proof.
- Documented extension points.

### Known leftovers (not claimed done)

- Go 1.21.5 vs current CloudFox (`tempfox/dependencies.py` still pins `go_version = "1.21.5"`).
- `install_aws_cli` unzip-into-cwd (`unzip -o` can overwrite a pre-existing cwd `aws/`).
- CloudFox write-before-returncode (`.txt`/`.json` are written before the exit-code check).
- lexical output rotation (`cleanup_old_output_files` sorts glob names, not mtime).
- profile names embedding key suffix (`generate_profile_name` uses the last 8 characters of the access key).
- chmod-after-create (`write_aws_*` writes then `chmod` 0600; a crash between those steps can leave a wider mode).
- version 1.0.1 vs PyPI stale wheel / `get_version` 1.0.0 fallback (`pyproject.toml` is 1.0.1; `get_version` falls back to `1.0.0`). Do not publish or bump from this file.
- Docker CMD --help (`Dockerfile` `CMD ["--help"]`).

### Preflight/install hardening (remaining)

UV-only install shipped in PR #3. Still open: OS/arch validation messages, timeout/error categorization for AWS CLI/Go/CloudFox installs, and the unzip-into-cwd leftover above.

### UX leftovers

README install/run path shipped in PR #4. Still open: a short troubleshooting section and AKIA vs ASIA prompt/output examples.
