"""Basic unit tests for TempFox core functionality."""

import pytest

from tempfox import core


def test_get_version():
    """Test that get_version returns a valid version string."""
    version = core.get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_expired_token_path_does_not_recurse_into_main():
    class Result:
        returncode = 1
        stderr = "ExpiredToken"
        stdout = ""

    result = core.test_aws_connection(
        "a",
        "b",
        "c",
        _get_aws_cmd=lambda: "aws",
        _run_cmd=lambda *a, **k: Result(),
        _check_expiration=lambda msg: True,
    )
    assert result is False


def test_asia_flow_rejects_empty_session_token():
    assert core.validate_session_token("ASIA", "") is False


def test_main_exits_nonzero_when_aws_connection_fails():
    creds = iter(["AKIAX", "SECRET"])
    deps = core.MainDeps(
        check_aws_cli=lambda: True,
        check_access_key_type=lambda: "AKIA",
        get_credential=lambda *_, **__: next(creds),
        test_aws_connection=lambda *a, **kw: False,
    )

    with pytest.raises(SystemExit) as exc:
        core.main(["--skip-preflight", "--no-profile"], _deps=deps)
    assert exc.value.code == 1


def test_main_exits_nonzero_when_cloudfox_analysis_fails():
    creds = iter(["AKIAX", "SECRET"])
    deps = core.MainDeps(
        check_aws_cli=lambda: True,
        check_access_key_type=lambda: "AKIA",
        get_credential=lambda *_, **__: next(creds),
        test_aws_connection=lambda *a, **kw: True,
        run_cloudfox_aws_all_checks=lambda *a, **kw: False,
    )

    with pytest.raises(SystemExit) as exc:
        core.main(["--skip-preflight", "--no-profile"], _deps=deps)
    assert exc.value.code == 1


def test_get_credential_uses_getpass_for_secret_prompt():
    value = core.get_credential(
        "AWS_SECRET_ACCESS_KEY",
        "Enter your AWS_SECRET_ACCESS_KEY: ",
        secret=True,
        _environ={},
        _getpass=lambda *_: "secret-value",
        _input=lambda *_: pytest.fail("input() should not be used"),
    )
    assert value == "secret-value"


def test_get_credential_uses_input_for_non_secret_prompt():
    value = core.get_credential(
        "AWS_ACCESS_KEY_ID",
        "Enter your AWS_ACCESS_KEY_ID: ",
        secret=False,
        _environ={},
        _input=lambda *_: "AKIAXXXX",
    )
    assert value == "AKIAXXXX"
