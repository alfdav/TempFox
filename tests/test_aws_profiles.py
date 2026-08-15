import configparser
import os
import stat

from tempfox import aws_profiles


def _isolate_aws_home(monkeypatch, tmp_path):
    aws_dir = tmp_path / ".aws"
    monkeypatch.setattr(aws_profiles, "get_aws_config_dir", lambda: str(aws_dir))
    return aws_dir


def test_generate_profile_name_includes_tempfox_prefix():
    name = aws_profiles.generate_profile_name("AKIA12345678ABCDEFG", "AKIA")
    assert name.startswith("tempfox-akia-")
    assert "ABCDEFG" in name


def test_list_create_and_delete_profiles_on_isolated_filesystem(monkeypatch, tmp_path):
    _isolate_aws_home(monkeypatch, tmp_path)

    assert aws_profiles.list_aws_profiles() == []
    assert aws_profiles.get_tempfox_profiles() == []

    created = aws_profiles.create_aws_profile(
        "tempfox-akia-example",
        "AKIAEXAMPLE",
        "secret-example",
        aws_session_token=None,
        region="us-east-1",
        output_format="json",
    )
    assert created is True
    assert aws_profiles.profile_exists("tempfox-akia-example") is True
    assert aws_profiles.list_aws_profiles() == ["tempfox-akia-example"]
    assert aws_profiles.get_tempfox_profiles() == ["tempfox-akia-example"]

    credentials = aws_profiles.read_aws_credentials()
    assert credentials.get("tempfox-akia-example", "aws_access_key_id") == "AKIAEXAMPLE"
    assert not credentials.has_option("tempfox-akia-example", "aws_session_token")

    config = aws_profiles.read_aws_config()
    assert config.get("profile tempfox-akia-example", "region") == "us-east-1"
    assert config.get("profile tempfox-akia-example", "output") == "json"

    assert aws_profiles.delete_aws_profile("tempfox-akia-example") is True
    assert aws_profiles.profile_exists("tempfox-akia-example") is False
    assert aws_profiles.list_aws_profiles() == []


def test_create_default_profile_uses_default_config_section(monkeypatch, tmp_path):
    _isolate_aws_home(monkeypatch, tmp_path)

    assert aws_profiles.create_aws_profile(
        "default",
        "AKIADEFAULT",
        "secret-default",
        aws_session_token="session",
        region="eu-west-1",
    )
    assert aws_profiles.list_aws_profiles() == ["default"]
    assert aws_profiles.get_tempfox_profiles() == []

    config = aws_profiles.read_aws_config()
    assert config.has_section("default")
    assert not config.has_section("profile default")
    credentials = aws_profiles.read_aws_credentials()
    assert credentials.get("default", "aws_session_token") == "session"


def test_get_tempfox_profiles_ignores_custom_and_default_names(monkeypatch, tmp_path):
    _isolate_aws_home(monkeypatch, tmp_path)
    aws_profiles.create_aws_profile("default", "AKIA1", "s1")
    aws_profiles.create_aws_profile("custom-pentest", "AKIA2", "s2")
    aws_profiles.create_aws_profile("tempfox-asia-abc", "ASIA3", "s3", "token")

    assert aws_profiles.get_tempfox_profiles() == ["tempfox-asia-abc"]
    assert "default" in aws_profiles.list_aws_profiles()
    assert "custom-pentest" in aws_profiles.list_aws_profiles()


def test_write_aws_files_set_owner_only_permissions(monkeypatch, tmp_path):
    _isolate_aws_home(monkeypatch, tmp_path)
    credentials = configparser.ConfigParser()
    credentials.add_section("tempfox-akia-perm")
    credentials.set("tempfox-akia-perm", "aws_access_key_id", "AKIA")
    credentials.set("tempfox-akia-perm", "aws_secret_access_key", "secret")
    config = configparser.ConfigParser()
    config.add_section("profile tempfox-akia-perm")
    config.set("profile tempfox-akia-perm", "region", "us-west-2")

    assert aws_profiles.write_aws_credentials(credentials) is True
    assert aws_profiles.write_aws_config(config) is True

    creds_mode = stat.S_IMODE(os.stat(aws_profiles.get_aws_credentials_file()).st_mode)
    config_mode = stat.S_IMODE(os.stat(aws_profiles.get_aws_config_file()).st_mode)
    assert creds_mode == 0o600
    assert config_mode == 0o600


def test_delete_aws_profile_returns_false_when_credentials_write_fails(
    monkeypatch, tmp_path
):
    _isolate_aws_home(monkeypatch, tmp_path)
    aws_profiles.create_aws_profile("tempfox-akia-fail", "AKIA", "secret")
    monkeypatch.setattr(aws_profiles, "write_aws_credentials", lambda _cfg: False)

    assert aws_profiles.delete_aws_profile("tempfox-akia-fail") is False


def test_delete_aws_profile_returns_false_when_config_write_fails(
    monkeypatch, tmp_path
):
    _isolate_aws_home(monkeypatch, tmp_path)
    aws_profiles.create_aws_profile("tempfox-akia-fail", "AKIA", "secret")
    monkeypatch.setattr(aws_profiles, "write_aws_config", lambda _cfg: False)

    assert aws_profiles.delete_aws_profile("tempfox-akia-fail") is False


def test_create_aws_profile_removes_stale_session_token(monkeypatch, tmp_path):
    _isolate_aws_home(monkeypatch, tmp_path)
    aws_profiles.create_aws_profile(
        "tempfox-akia-rotate",
        "AKIA",
        "secret",
        aws_session_token="old-token",
    )
    aws_profiles.create_aws_profile(
        "tempfox-akia-rotate",
        "AKIA",
        "secret",
        aws_session_token="",
    )
    credentials = aws_profiles.read_aws_credentials()
    assert not credentials.has_option("tempfox-akia-rotate", "aws_session_token")
