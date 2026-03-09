"""Basic unit tests for TempFox core functionality."""

import pytest

from tempfox import cloudfox, core, dependencies


def test_get_version():
    """Test that get_version returns a valid version string."""
    version = core.get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_expired_token_path_does_not_recurse_into_main(monkeypatch):
    class Result:
        returncode = 1
        stderr = "ExpiredToken"
        stdout = ""

    monkeypatch.setattr(cloudfox, "get_aws_cmd", lambda: "aws")
    monkeypatch.setattr(core.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(cloudfox, "check_token_expiration", lambda msg: True)

    assert core.test_aws_connection("a", "b", "c") is False


def test_asia_flow_rejects_empty_session_token(monkeypatch):
    assert core.validate_session_token("ASIA", "") is False


def test_main_exits_nonzero_when_aws_connection_fails(monkeypatch):
    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(dependencies, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    creds = iter(["AKIAX", "SECRET"])
    monkeypatch.setattr(core, "get_credential", lambda *_, **__: next(creds))
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: False)

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 1


def test_main_exits_nonzero_when_cloudfox_analysis_fails(monkeypatch):
    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(dependencies, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    creds = iter(["AKIAX", "SECRET"])
    monkeypatch.setattr(core, "get_credential", lambda *_, **__: next(creds))
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: True)
    monkeypatch.setattr(cloudfox, "run_cloudfox_aws_all_checks", lambda *args: False)

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 1


def test_get_credential_uses_getpass_for_secret_prompt(monkeypatch):
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.setattr(core.getpass, "getpass", lambda *_: "secret-value")
    monkeypatch.setattr(
        "builtins.input", lambda *_: pytest.fail("input() should not be used")
    )

    value = core.get_credential(
        "AWS_SECRET_ACCESS_KEY",
        "Enter your AWS_SECRET_ACCESS_KEY: ",
        secret=True,
    )
    assert value == "secret-value"


def test_get_credential_uses_input_for_non_secret_prompt(monkeypatch):
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.setattr("builtins.input", lambda *_: "AKIAXXXX")

    value = core.get_credential(
        "AWS_ACCESS_KEY_ID",
        "Enter your AWS_ACCESS_KEY_ID: ",
        secret=False,
    )
    assert value == "AKIAXXXX"
