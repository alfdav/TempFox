"""Basic unit tests for TempFox core functionality."""

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
    monkeypatch.setattr("builtins.input", lambda *_: "n")

    assert core.test_aws_connection("a", "b", "c") is False


def test_asia_flow_rejects_empty_session_token(monkeypatch):
    import tempfox.core as core

    responses = iter(["ASIA", "ASIAX", "SECRET", "", "n"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))

    assert core.validate_session_token("ASIA", "") is False
