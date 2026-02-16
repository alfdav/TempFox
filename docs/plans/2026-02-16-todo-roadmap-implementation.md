# TempFox Roadmap Execution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the roadmap in `TODO.md` into shippable increments for credential lifecycle hardening, CloudFox reliability, and test coverage.

**Architecture:** Implement in thin, behavior-focused slices with test-first updates. Keep `tempfox/core.py` as orchestration, push logic into `tempfox/aws_profiles.py`, `tempfox/dependencies.py`, and `tempfox/cloudfox.py`, and validate with CLI-facing tests. Each task is intentionally small so regression risk stays low.

**Tech Stack:** Python 3.8+, pytest, mypy, ruff, subprocess mocking via stdlib monkeypatch fixtures.

### Task 1: Test Harness Expansion For Refactored Modules

**Files:**
- Modify: `tests/test_core.py`
- Create: `tests/test_aws_profiles.py`
- Create: `tests/test_cloudfox.py`
- Create: `tests/test_dependencies.py`

**Step 1: Write the failing tests**

```python
# tests/test_cloudfox.py
from tempfox import cloudfox


def test_check_token_expiration_matches_known_markers():
    assert cloudfox.check_token_expiration("ExpiredToken") is True
    assert cloudfox.check_token_expiration("no issues") is False
```

```python
# tests/test_aws_profiles.py
from tempfox import aws_profiles


def test_generate_profile_name_includes_tempfox_prefix():
    name = aws_profiles.generate_profile_name("AKIA12345678ABCDEFG", "AKIA")
    assert name.startswith("tempfox-akia-")
```

**Step 2: Run tests to verify they fail when missing files/functions**

Run: `uv run pytest tests/test_cloudfox.py tests/test_aws_profiles.py -q`
Expected: FAIL initially until files/tests are fully wired.

**Step 3: Add minimal test files and imports to pass**

```python
# tests/test_dependencies.py
from tempfox import dependencies


def test_platform_info_returns_strings():
    system, arch = dependencies.get_platform_info()
    assert isinstance(system, str)
    assert isinstance(arch, str)
```

**Step 4: Re-run focused tests**

Run: `uv run pytest tests/test_cloudfox.py tests/test_aws_profiles.py tests/test_dependencies.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_core.py tests/test_aws_profiles.py tests/test_cloudfox.py tests/test_dependencies.py
git commit -m "test: expand module-level coverage for refactored code"
```

### Task 2: Replace Expired Token Recursion With Controlled Retry Flow

**Files:**
- Modify: `tempfox/core.py`
- Modify: `tests/test_core.py`

**Step 1: Write failing regression test**

```python
def test_expired_token_path_does_not_recurse_into_main(monkeypatch):
    import tempfox.core as core

    class Result:
        returncode = 1
        stderr = "ExpiredToken"
        stdout = ""

    monkeypatch.setattr(core, "get_aws_cmd", lambda: "aws")
    monkeypatch.setattr(core.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(core, "check_token_expiration", lambda msg: True)
    monkeypatch.setattr("builtins.input", lambda *_: "n")

    # Should return False/exit cleanly without calling main()
    assert core.test_aws_connection("a", "b", "c") is False
```

**Step 2: Run focused test to verify current failure**

Run: `uv run pytest tests/test_core.py::test_expired_token_path_does_not_recurse_into_main -q`
Expected: FAIL before implementation change.

**Step 3: Implement minimal behavior change**

```python
# tempfox/core.py (inside test_aws_connection)
if check_token_expiration(error_message):
    logging.warning("AWS token has expired. Please obtain new temporary credentials.")
    proceed = input("Would you like to enter new credentials? (y/n): ")
    if proceed.lower() == "y":
        return False
    logging.info("Exiting script.")
    return False
```

**Step 4: Re-run focused and full tests**

Run: `uv run pytest tests/test_core.py::test_expired_token_path_does_not_recurse_into_main -q`
Expected: PASS.

Run: `uv run pytest -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add tempfox/core.py tests/test_core.py
git commit -m "fix: replace expired-token recursion with controlled flow"
```

### Task 3: Validate ASIA Session Token Input Explicitly

**Files:**
- Modify: `tempfox/core.py`
- Modify: `tests/test_core.py`

**Step 1: Write failing tests for empty ASIA token**

```python
def test_asia_flow_rejects_empty_session_token(monkeypatch):
    import tempfox.core as core

    responses = iter(["ASIA", "ASIAX", "SECRET", "", "n"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))

    # Add an extracted validator helper and test it directly when possible
    assert core.validate_session_token("ASIA", "") is False
```

**Step 2: Run focused test**

Run: `uv run pytest tests/test_core.py::test_asia_flow_rejects_empty_session_token -q`
Expected: FAIL (helper missing).

**Step 3: Implement minimal helper and usage**

```python
def validate_session_token(key_type: str, aws_session_token: str) -> bool:
    if key_type != "ASIA":
        return True
    return bool(aws_session_token.strip())
```

**Step 4: Re-run focused tests**

Run: `uv run pytest tests/test_core.py::test_asia_flow_rejects_empty_session_token -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add tempfox/core.py tests/test_core.py
git commit -m "feat: validate required ASIA session token input"
```

### Task 4: Surface CloudFox Non-Zero Exit Status Explicitly

**Files:**
- Modify: `tempfox/cloudfox.py`
- Modify: `tests/test_cloudfox.py`

**Step 1: Write failing test for non-zero CloudFox return code**

```python
def test_run_cloudfox_logs_failure_on_nonzero_exit(monkeypatch, caplog, tmp_path):
    from tempfox import cloudfox

    class Result:
        returncode = 2
        stdout = ""
        stderr = "permission denied"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(cloudfox.subprocess, "run", lambda *a, **k: Result())

    cloudfox.run_cloudfox_aws_all_checks("a", "b", "c")
    assert "exit code" in caplog.text.lower()
```

**Step 2: Run focused test**

Run: `uv run pytest tests/test_cloudfox.py::test_run_cloudfox_logs_failure_on_nonzero_exit -q`
Expected: FAIL.

**Step 3: Implement minimal error reporting**

```python
if process.returncode != 0:
    logging.error(
        "CloudFox command failed with exit code %s: %s",
        process.returncode,
        process.stderr.strip(),
    )
```

**Step 4: Re-run focused and module tests**

Run: `uv run pytest tests/test_cloudfox.py -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add tempfox/cloudfox.py tests/test_cloudfox.py
git commit -m "fix: report cloudfox non-zero exits with diagnostics"
```

### Task 5: Stabilize Output File Behavior Tests

**Files:**
- Modify: `tests/test_cloudfox.py`

**Step 1: Add deterministic output tests**

```python
def test_cleanup_old_output_files_keeps_recent_five(tmp_path, monkeypatch):
    from tempfox import cloudfox

    monkeypatch.chdir(tmp_path)
    for i in range(7):
        (tmp_path / f"cloudfox_aws_123_{i}.txt").write_text("x")
        (tmp_path / f"cloudfox_aws_123_{i}.json").write_text("{}")

    cloudfox.cleanup_old_output_files()
    assert len(list(tmp_path.glob("cloudfox_aws_*.txt"))) == 5
    assert len(list(tmp_path.glob("cloudfox_aws_*.json"))) == 5
```

**Step 2: Run focused test**

Run: `uv run pytest tests/test_cloudfox.py::test_cleanup_old_output_files_keeps_recent_five -q`
Expected: PASS.

**Step 3: Commit**

```bash
git add tests/test_cloudfox.py
git commit -m "test: enforce deterministic cloudfox output file retention"
```

### Task 6: Add CLI Flag Behavior Tests

**Files:**
- Modify: `tests/test_core.py`

**Step 1: Write tests for key CLI flags**

```python
def test_list_profiles_flag_exits(monkeypatch):
    import tempfox.core as core

    monkeypatch.setattr(core.sys, "argv", ["tempfox", "--list-profiles"])
    monkeypatch.setattr(core, "list_aws_profiles", lambda: [])
    try:
        core.main()
    except SystemExit as exc:
        assert exc.code == 0
```

**Step 2: Run focused tests**

Run: `uv run pytest tests/test_core.py::test_list_profiles_flag_exits -q`
Expected: PASS after wiring.

**Step 3: Expand for `--cleanup-profiles` and `--no-profile`**

Run: `uv run pytest tests/test_core.py -q`
Expected: PASS.

**Step 4: Commit**

```bash
git add tests/test_core.py
git commit -m "test: add CLI flag behavior coverage"
```

### Task 7: Document Next/Later Track As Issue-Ready Specs

**Files:**
- Modify: `TODO.md`
- Create: `docs/plans/rotation-workflow-spec.md`
- Create: `docs/plans/audit-logging-spec.md`
- Create: `docs/plans/multi-account-spec.md`

**Step 1: Create concise issue-ready specs**

```markdown
# Rotation Workflow Spec
- Problem
- CLI contract
- Data model impact
- Test cases
- Rollout plan
```

**Step 2: Link specs from `TODO.md`**

```markdown
- [ ] Credential rotation workflow (see docs/plans/rotation-workflow-spec.md)
```

**Step 3: Validate docs formatting and repository checks**

Run: `uv run ruff check .`
Expected: PASS.

**Step 4: Commit**

```bash
git add TODO.md docs/plans/rotation-workflow-spec.md docs/plans/audit-logging-spec.md docs/plans/multi-account-spec.md
git commit -m "docs: add issue-ready specs for roadmap next phases"
```

### Task 8: Final Verification Gate For This Plan

**Files:**
- Modify: none

**Step 1: Run lint**

Run: `uv run ruff check .`
Expected: PASS.

**Step 2: Run typing**

Run: `uv run mypy tempfox/`
Expected: PASS.

**Step 3: Run tests**

Run: `uv run pytest -q`
Expected: PASS.

**Step 4: Prepare integration PR from worktree branch**

```bash
git log --oneline main..HEAD
git status
```

Expected: clean status, coherent commit series.
