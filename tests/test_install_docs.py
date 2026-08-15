"""Contract tests for the UV-only install/uninstall path."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RETIRED_INSTALLERS = (
    "install.sh",
    "install.ps1",
    "uninstall.sh",
    "uninstall.ps1",
)
DOC_PATHS = (
    "README.md",
    "MIGRATION.md",
    "AGENTS.md",
    "docs/project-context.md",
    "docs/codex-hygiene-runbook.md",
)
INVOKE_PATHS = DOC_PATHS + (
    "Makefile",
    "Dockerfile",
    "Dockerfile.dev",
    "docker-compose.yml",
    ".github/workflows/python-package.yml",
    ".github/workflows/docker.yml",
)
# Commands that would still run the retired scripts. Mentions of the
# filenames as retired leftovers are allowed.
SCRIPT_INVOCATION = re.compile(
    r"(?:(?:curl|iwr|irm)\b[^\n]*tempfox[^\n]*install\.(?:sh|ps1)|"
    r"(?:^|[^\w./-])\./install\.(?:sh|ps1)|"
    r"bash\s+install\.sh|"
    r"powershell\s+\S*install\.ps1)",
    re.IGNORECASE | re.MULTILINE,
)


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_retired_install_scripts_are_gone():
    remaining = [name for name in RETIRED_INSTALLERS if (REPO_ROOT / name).exists()]
    assert remaining == [], f"retired installers still present: {remaining}"


def test_readme_documents_uv_tool_install_and_uninstall():
    readme = _read("README.md")
    assert "uv tool install tempfox" in readme
    assert "uv tool uninstall tempfox" in readme
    assert "uv sync" in readme
    assert "uv run tempfox" in readme
    assert "https://github.com/alfdav/TempFox" in readme
    assert "auto-renewal" not in readme.lower()
    assert "Permission is hereby granted" not in readme
    emoji = re.search(
        r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0000FE0F\U0000200D]",
        readme,
    )
    assert emoji is None, f"README still has emoji: {emoji.group(0)!r}"


def test_docs_and_automation_do_not_invoke_retired_scripts():
    leftovers = {}
    for path in INVOKE_PATHS:
        text = _read(path)
        match = SCRIPT_INVOCATION.search(text)
        if match:
            leftovers[path] = match.group(0)
    assert leftovers == {}, (
        f"docs/automation still invoke retired installers: {leftovers}"
    )


def test_docs_state_preflight_path_is_session_only():
    readme = _read("README.md")
    migration = _read("MIGRATION.md")
    marker = "current TempFox process"
    assert marker in readme
    assert marker in migration


def test_migration_cleans_script_venv_before_uv_tool_install():
    migration = _read("MIGRATION.md")
    leftover_at = migration.find("~/.local/share/tempfox")
    install_at = migration.find("uv tool install tempfox")
    assert leftover_at != -1, "MIGRATION.md must describe leftover script venv cleanup"
    assert install_at != -1, "MIGRATION.md must show uv tool install tempfox"
    assert leftover_at < install_at, (
        "leftover script-venv cleanup must come before uv tool install "
        "so users do not delete the UV shim"
    )
