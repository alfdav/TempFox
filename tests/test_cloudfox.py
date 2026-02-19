import logging
from types import SimpleNamespace

from tempfox import cloudfox


def test_check_token_expiration_matches_known_markers():
    assert cloudfox.check_token_expiration("ExpiredToken") is True
    assert cloudfox.check_token_expiration("no issues") is False


def test_run_cloudfox_logs_error_on_nonzero_exit(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2, stdout="not-json", stderr="boom"
        ),
    )

    result = cloudfox.run_cloudfox_aws_all_checks("a", "b", "c")
    assert result is False
    assert "failed" in caplog.text.lower()


def test_run_cloudfox_does_not_log_success_on_nonzero_exit(
    monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2, stdout="not-json", stderr="boom"
        ),
    )

    cloudfox.run_cloudfox_aws_all_checks("a", "b", "c")
    assert "completed successfully" not in caplog.text.lower()
