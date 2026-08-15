from types import SimpleNamespace

import pytest

from tempfox import core, dependencies


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


def test_check_aws_cli_installs_on_missing_binary(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: None)
    monkeypatch.setattr(dependencies, "install_aws_cli", lambda: True)
    assert dependencies.check_aws_cli() is True


def test_check_aws_cli_does_not_mask_unexpected_runtime_error(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda cmd: "/usr/bin/aws")

    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("unexpected failure")

    install_called = {"value": False}

    def fake_install():
        install_called["value"] = True
        return True

    monkeypatch.setattr(dependencies.subprocess, "run", raise_unexpected)
    monkeypatch.setattr(dependencies, "install_aws_cli", fake_install)

    assert dependencies.check_aws_cli() is False
    assert install_called["value"] is False


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


def test_cleanup_temp_files_preserves_unrelated_cwd_aws_and_installer_names(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    aws_dir = tmp_path / "aws"
    aws_dir.mkdir()
    marker = aws_dir / "package.py"
    marker.write_text("keep me")
    leftover_zip = tmp_path / "awscliv2.zip"
    leftover_zip.write_text("not ours")
    leftover_pkg = tmp_path / "AWSCLIV2.pkg"
    leftover_pkg.write_text("not ours")

    dependencies.cleanup_temp_files()

    assert marker.exists()
    assert leftover_zip.exists()
    assert leftover_pkg.exists()


def test_cleanup_temp_files_removes_only_registered_installer_artifacts(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    created_zip = tmp_path / "awscliv2.zip"
    created_zip.write_text("tempfox created")
    created_dir = tmp_path / "aws"
    created_dir.mkdir()
    (created_dir / "install").write_text("installer")
    unrelated = tmp_path / "AWSCLIV2.pkg"
    unrelated.write_text("operator file")

    dependencies.register_installer_artifact(str(created_zip))
    dependencies.register_installer_artifact(str(created_dir))
    dependencies.cleanup_temp_files()

    assert not created_zip.exists()
    assert not created_dir.exists()
    assert unrelated.exists()


def test_cleanup_on_exit_does_not_delete_unrelated_cwd_aws(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    aws_dir = tmp_path / "aws"
    aws_dir.mkdir()
    marker = aws_dir / "keep.txt"
    marker.write_text("repo package")
    monkeypatch.setattr(core, "cleanup_old_output_files", lambda: None)

    core.cleanup_on_exit()

    assert marker.exists()


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
