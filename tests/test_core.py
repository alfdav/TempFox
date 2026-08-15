"""Basic unit tests for TempFox core functionality."""

import pytest

from tempfox import core


def test_get_version():
    """Test that get_version returns a valid version string."""
    version = core.get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_get_platform_info():
    """Test that get_platform_info returns platform information."""
    system, arch = core.get_platform_info()
    assert isinstance(system, str)
    assert isinstance(arch, str)
    assert len(system) > 0
    assert len(arch) > 0


def test_get_aws_config_dir():
    """Test that get_aws_config_dir returns a valid path."""
    config_dir = core.get_aws_config_dir()
    assert isinstance(config_dir, str)
    assert config_dir.endswith("/.aws")


def test_get_aws_regions():
    """Test that get_aws_regions returns a list of regions."""
    regions = core.get_aws_regions()
    assert isinstance(regions, list)
    assert len(regions) > 0
    assert "us-east-1" in regions
    assert "eu-west-1" in regions


def test_check_token_expiration():
    """Test token expiration detection."""
    assert core.check_token_expiration("token has expired") is True
    assert core.check_token_expiration("SecurityTokenExpired") is True
    assert core.check_token_expiration("valid token") is False


def test_generate_profile_name():
    """Test profile name generation."""
    profile_name = core.generate_profile_name("AKIAIOSFODNN7EXAMPLE", "AKIA")
    assert profile_name.startswith("tempfox-akia-")
    # Profile name should contain last 8 characters of access key
    assert profile_name.count("-") >= 3  # tempfox-akia-{last8chars}-{timestamp}


def test_list_aws_profiles_empty():
    """Test listing AWS profiles when none exist."""
    # This will return empty list when no AWS config exists
    profiles = core.list_aws_profiles()
    assert isinstance(profiles, list)


def test_get_tempfox_profiles_empty():
    """Test getting TempFox profiles when none exist."""
    tempfox_profiles = core.get_tempfox_profiles()
    assert isinstance(tempfox_profiles, list)
    # Should be empty if no tempfox profiles exist
    all_profiles = core.list_aws_profiles()
    expected_tempfox = [p for p in all_profiles if p.startswith("tempfox-")]
    assert tempfox_profiles == expected_tempfox


def test_profile_exists_false():
    """Test profile_exists returns False for non-existent profile."""
    result = core.profile_exists("non-existent-profile-12345")
    assert result is False


def test_expired_token_path_does_not_recurse_into_main(monkeypatch):
    import tempfox.core as core

    class Result:
        returncode = 1
        stderr = "ExpiredToken"
        stdout = ""

    monkeypatch.setattr(core, "get_aws_cmd", lambda: "aws")
    monkeypatch.setattr(core.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(core, "check_token_expiration", lambda msg: True)

    assert core.test_aws_connection("a", "b", "c") is False


def test_asia_flow_rejects_empty_session_token(monkeypatch):
    import tempfox.core as core

    assert core.validate_session_token("ASIA", "") is False


def test_main_exits_nonzero_when_aws_connection_fails(monkeypatch):
    import tempfox.core as core

    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(core, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    creds = iter(["AKIAX", "SECRET"])
    monkeypatch.setattr(core, "get_credential", lambda *_, **__: next(creds))
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: False)

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 1


def test_main_exits_nonzero_when_cloudfox_analysis_fails(monkeypatch):
    import tempfox.core as core

    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(core, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    creds = iter(["AKIAX", "SECRET"])
    monkeypatch.setattr(core, "get_credential", lambda *_, **__: next(creds))
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: True)
    monkeypatch.setattr(core, "run_cloudfox_aws_all_checks", lambda *args: False)

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


def test_test_aws_connection_omits_empty_session_token(monkeypatch):
    captured = {}

    class Result:
        returncode = 0
        stdout = '{"Account":"1","Arn":"arn","UserId":"uid"}'
        stderr = ""

    def fake_run(*args, **kwargs):
        captured["env"] = kwargs["env"]
        return Result()

    monkeypatch.setenv("AWS_SESSION_TOKEN", "stale-parent-token")
    monkeypatch.setattr(core, "get_aws_cmd", lambda: "aws")
    monkeypatch.setattr(core.subprocess, "run", fake_run)

    assert core.test_aws_connection("AKIAX", "secret", "") is True
    assert "AWS_SESSION_TOKEN" not in captured["env"]
    assert captured["env"]["AWS_ACCESS_KEY_ID"] == "AKIAX"
    assert captured["env"]["AWS_SECRET_ACCESS_KEY"] == "secret"


def test_test_aws_connection_sets_session_token_when_present(monkeypatch):
    captured = {}

    class Result:
        returncode = 0
        stdout = '{"Account":"1","Arn":"arn","UserId":"uid"}'
        stderr = ""

    def fake_run(*args, **kwargs):
        captured["env"] = kwargs["env"]
        return Result()

    monkeypatch.setattr(core, "get_aws_cmd", lambda: "aws")
    monkeypatch.setattr(core.subprocess, "run", fake_run)

    assert core.test_aws_connection("ASIAX", "secret", "session-token") is True
    assert captured["env"]["AWS_SESSION_TOKEN"] == "session-token"


def test_main_collects_access_key_id_as_secret(monkeypatch):
    seen = {}

    def fake_get_credential(env_var, prompt_text, secret=False):
        seen[env_var] = secret
        if env_var == "AWS_ACCESS_KEY_ID":
            return "AKIAX"
        if env_var == "AWS_SECRET_ACCESS_KEY":
            return "SECRET"
        return ""

    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(core, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    monkeypatch.setattr(core, "get_credential", fake_get_credential)
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: False)

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 1
    assert seen["AWS_ACCESS_KEY_ID"] is True
    assert seen["AWS_SECRET_ACCESS_KEY"] is True


def test_main_list_profiles_labels_tempfox_entries(monkeypatch, caplog):
    caplog.set_level("INFO")
    monkeypatch.setattr(core.sys, "argv", ["tempfox", "--list-profiles"])
    monkeypatch.setattr(
        core, "list_aws_profiles", lambda: ["default", "tempfox-akia-x"]
    )
    monkeypatch.setattr(core, "get_tempfox_profiles", lambda: ["tempfox-akia-x"])

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 0
    assert "tempfox-akia-x (TempFox)" in caplog.text
    assert "• default" in caplog.text


def test_main_cleanup_profiles_reports_failed_delete(monkeypatch, caplog):
    caplog.set_level("INFO")
    monkeypatch.setattr(core.sys, "argv", ["tempfox", "--cleanup-profiles"])
    monkeypatch.setattr(core, "get_tempfox_profiles", lambda: ["tempfox-akia-x"])
    monkeypatch.setattr(core, "delete_aws_profile", lambda _name: False)
    monkeypatch.setattr("builtins.input", lambda *_: "y")

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 0
    assert "Failed to delete profile: tempfox-akia-x" in caplog.text
    assert "Deleted 0/1 profiles" in caplog.text


def test_main_cleanup_profiles_cancelled(monkeypatch, caplog):
    caplog.set_level("INFO")
    deleted = {"count": 0}
    monkeypatch.setattr(core.sys, "argv", ["tempfox", "--cleanup-profiles"])
    monkeypatch.setattr(core, "get_tempfox_profiles", lambda: ["tempfox-akia-x"])
    monkeypatch.setattr(
        core,
        "delete_aws_profile",
        lambda _name: deleted.__setitem__("count", deleted["count"] + 1) or True,
    )
    monkeypatch.setattr("builtins.input", lambda *_: "n")

    with pytest.raises(SystemExit) as exc:
        core.main()
    assert exc.value.code == 0
    assert deleted["count"] == 0
    assert "cancelled" in caplog.text.lower()


def test_main_no_profile_skips_profile_prompt(monkeypatch):
    prompted = {"value": False}

    def fake_prompt(*_args, **_kwargs):
        prompted["value"] = True
        return None

    monkeypatch.setattr(
        core.sys, "argv", ["tempfox", "--skip-preflight", "--no-profile"]
    )
    monkeypatch.setattr(core, "check_aws_cli", lambda: True)
    monkeypatch.setattr(core, "check_access_key_type", lambda: "AKIA")
    creds = iter(["AKIAX", "SECRET"])
    monkeypatch.setattr(core, "get_credential", lambda *_, **__: next(creds))
    monkeypatch.setattr(core, "test_aws_connection", lambda *args: True)
    monkeypatch.setattr(core, "prompt_for_profile_creation", fake_prompt)
    monkeypatch.setattr(core, "run_cloudfox_aws_all_checks", lambda *args: True)

    core.main()
    assert prompted["value"] is False
