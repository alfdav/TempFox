import json
import logging
from types import SimpleNamespace

from tempfox import cloudfox, core


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


def test_run_cloudfox_omits_empty_session_token(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AWS_SESSION_TOKEN", "stale-parent-token")
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")

    def fake_run(*args, **kwargs):
        captured["env"] = kwargs["env"]
        return SimpleNamespace(returncode=0, stdout='{"ok": true}', stderr="")

    monkeypatch.setattr(cloudfox.subprocess, "run", fake_run)
    assert cloudfox.run_cloudfox_aws_all_checks("AKIAX", "secret", "") is True
    assert "AWS_SESSION_TOKEN" not in captured["env"]


def test_run_cloudfox_writes_parsed_json_when_stdout_is_json(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout='{"findings": 2}', stderr=""
        ),
    )

    assert cloudfox.run_cloudfox_aws_all_checks("a", "b", "c") is True
    json_files = list(tmp_path.glob("cloudfox_aws_*.json"))
    txt_files = list(tmp_path.glob("cloudfox_aws_*.txt"))
    assert len(json_files) == 1
    assert len(txt_files) == 1
    assert json.loads(json_files[0].read_text()) == {"findings": 2}
    assert txt_files[0].read_text() == '{"findings": 2}'


def test_run_cloudfox_wraps_raw_text_when_stdout_is_not_json(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout="raw cloudfox text", stderr=""
        ),
    )

    assert cloudfox.run_cloudfox_aws_all_checks("a", "b", "c") is True
    json_files = list(tmp_path.glob("cloudfox_aws_*.json"))
    assert json.loads(json_files[0].read_text()) == {"raw_output": "raw cloudfox text"}


def test_run_cloudfox_writes_output_files_before_returncode_check(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2, stdout="partial output", stderr="boom"
        ),
    )

    assert cloudfox.run_cloudfox_aws_all_checks("a", "b", "c") is False
    assert list(tmp_path.glob("cloudfox_aws_*.txt"))
    assert list(tmp_path.glob("cloudfox_aws_*.json"))


def test_run_cloudfox_classifies_expired_token_like_connection_test(
    monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO)
    main_called = {"value": False}

    def fake_main():
        main_called["value"] = True

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cloudfox, "get_aws_account_id", lambda env: "123456789012")
    monkeypatch.setattr(core, "main", fake_main)
    monkeypatch.setattr(
        cloudfox.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1, stdout="", stderr="ExpiredToken"
        ),
    )

    assert cloudfox.run_cloudfox_aws_all_checks("a", "b", "c") is False
    assert "AWS token has expired" in caplog.text
    assert "CloudFox command failed" not in caplog.text
    assert main_called["value"] is False


def test_cleanup_old_output_files_keeps_only_max_recent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for index in range(7):
        (tmp_path / f"cloudfox_aws_111_{index}.txt").write_text("t")
        (tmp_path / f"cloudfox_aws_111_{index}.json").write_text("{}")

    cloudfox.cleanup_old_output_files()

    txt_files = sorted(p.name for p in tmp_path.glob("cloudfox_aws_*.txt"))
    json_files = sorted(p.name for p in tmp_path.glob("cloudfox_aws_*.json"))
    assert len(txt_files) == cloudfox.MAX_OUTPUT_FILES
    assert len(json_files) == cloudfox.MAX_OUTPUT_FILES
    assert txt_files == [
        "cloudfox_aws_111_2.txt",
        "cloudfox_aws_111_3.txt",
        "cloudfox_aws_111_4.txt",
        "cloudfox_aws_111_5.txt",
        "cloudfox_aws_111_6.txt",
    ]


def test_run_cloudfox_handles_unexpected_exceptions(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)

    def raise_unexpected(_env):
        raise RuntimeError("unexpected boom")

    monkeypatch.setattr(cloudfox, "get_aws_account_id", raise_unexpected)
    result = cloudfox.run_cloudfox_aws_all_checks("a", "b", "c")
    assert result is False
    assert "unexpected error" in caplog.text.lower()
