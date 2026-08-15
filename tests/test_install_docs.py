"""Contract tests for the UV-only install/uninstall path."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RETIRED_INSTALLERS = (
    "install.sh",
    "install.ps1",
    "uninstall.sh",
    "uninstall.ps1",
)
SCRIPT_INSTALL_MARKERS = (
    "raw.githubusercontent.com/alfdav/tempfox/main/install.sh",
    "raw.githubusercontent.com/alfdav/tempfox/main/install.ps1",
    "raw.githubusercontent.com/alfdav/tempfox/main/uninstall.sh",
    "raw.githubusercontent.com/alfdav/tempfox/main/uninstall.ps1",
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


def test_user_docs_do_not_instruct_curl_or_irm_of_retired_scripts():
    docs = {
        "README.md": _read("README.md"),
        "MIGRATION.md": _read("MIGRATION.md"),
        "AGENTS.md": _read("AGENTS.md"),
        "docs/project-context.md": _read("docs/project-context.md"),
        "docs/codex-hygiene-runbook.md": _read("docs/codex-hygiene-runbook.md"),
    }
    leftovers = {
        path: marker
        for path, text in docs.items()
        for marker in SCRIPT_INSTALL_MARKERS
        if marker in text
    }
    assert leftovers == {}, f"docs still point at retired installers: {leftovers}"
