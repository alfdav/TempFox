from types import SimpleNamespace

import pytest

from tempfox import dependencies


def test_platform_info_returns_strings():
    system, arch = dependencies.get_platform_info()
    assert isinstance(system, str)
    assert isinstance(arch, str)


def test_get_platform_info_normalizes_amd64(monkeypatch):
    monkeypatch.setattr(dependencies.platform, "system", lambda: "Linux")
    monkeypatch.setattr(dependencies.platform, "machine", lambda: "x86_64")
    system, arch = dependencies.get_platform_info()
    assert system == "linux"
    assert arch == "amd64"


def test_get_aws_cli_download_url_linux_amd64(monkeypatch):
    monkeypatch.setattr(dependencies, "get_platform_info", lambda: ("linux", "amd64"))
    assert (
        dependencies.get_aws_cli_download_url()
        == "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
    )


def test_get_aws_cli_download_url_unsupported_platform(monkeypatch):
    monkeypatch.setattr(dependencies, "get_platform_info", lambda: ("solaris", "sparc"))
    with pytest.raises(ValueError):
        dependencies.get_aws_cli_download_url()


def test_check_aws_cli_returns_true_when_installed(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: "/usr/bin/aws")
    monkeypatch.setattr(
        dependencies.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="aws-cli/2.0"),
    )
    assert dependencies.check_aws_cli() is True


def test_check_aws_cli_installs_when_missing(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: None)
    monkeypatch.setattr(dependencies, "install_aws_cli", lambda: True)
    assert dependencies.check_aws_cli() is True


def test_check_go_installation_missing_binary(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: None)
    installed, version = dependencies.check_go_installation()
    assert installed is False
    assert version is None


def test_check_cloudfox_installation_help_fallback(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: "/usr/bin/cloudfox")
    calls = {"count": 0}

    def fake_run(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return SimpleNamespace(returncode=1, stdout="", stderr="unknown")
        return SimpleNamespace(returncode=0, stdout="usage", stderr="")

    monkeypatch.setattr(dependencies.subprocess, "run", fake_run)
    installed, version = dependencies.check_cloudfox_installation()
    assert installed is True
    assert version == "CloudFox (version unknown)"


def test_check_uv_installation_missing_binary(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: None)
    installed, version = dependencies.check_uv_installation()
    assert installed is False
    assert version is None


def test_run_preflight_checks_success(monkeypatch):
    monkeypatch.setattr(dependencies, "check_aws_cli", lambda: True)
    monkeypatch.setattr(dependencies, "check_uv_installation", lambda: (True, "uv 0.x"))
    monkeypatch.setattr(dependencies, "check_go_installation", lambda: (True, "go1.22"))
    monkeypatch.setattr(
        dependencies, "check_cloudfox_installation", lambda: (True, "cloudfox 1.x")
    )
    monkeypatch.setattr(
        dependencies.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )
    assert dependencies.run_preflight_checks() is True


def test_run_preflight_checks_fails_when_install_steps_fail(monkeypatch):
    monkeypatch.setattr(dependencies, "check_aws_cli", lambda: True)
    monkeypatch.setattr(dependencies, "check_uv_installation", lambda: (False, None))
    monkeypatch.setattr(dependencies, "check_go_installation", lambda: (False, None))
    monkeypatch.setattr(dependencies, "install_go", lambda: False)
    monkeypatch.setattr(
        dependencies, "check_cloudfox_installation", lambda: (False, None)
    )
    monkeypatch.setattr(dependencies, "install_cloudfox", lambda: False)
    assert dependencies.run_preflight_checks() is False
