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
    "TODO.md",
    "docs/project-context.md",
    "docs/codex-hygiene-runbook.md",
    "docs/plans/2026-02-16-todo-roadmap-implementation.md",
)
SHIPPED_TODO_MARKERS = (
    "Last updated: 2026-08-15",
    "PR #2",
    "PR #3",
    "PR #4",
    "leftover-cleanup",
    "empty session token",
    "delete returns",
    "expired-token",
    "getpass",
    "LICENSE",
    "Codecov",
    "uv tool install tempfox",
)
OPEN_TODO_MARKERS = (
    "credential rotation",
    "audit logging",
    "multi-account",
    "extensible checks",
    "Go 1.21.5",
    "unzip-into-cwd",
    "write-before-returncode",
    "lexical output rotation",
    "key suffix",
    "chmod-after-create",
    "get_version",
    "Docker CMD --help",
)
LOWERCASE_REPO = re.compile(r"github\.com/alfdav/tempfox\b")
EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0000FE0F\U0000200D]"
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
    assert "Permission is hereby granted" not in readme


def test_live_docs_match_readme_facts():
    leftovers = {}
    for path in DOC_PATHS:
        text = _read(path)
        problems = []
        if LOWERCASE_REPO.search(text):
            problems.append("lowercase GitHub URL")
        if "auto-renewal" in text.lower() or "controlled retry" in text.lower():
            problems.append("token renewal/retry claim")
        emoji = EMOJI_RE.search(text)
        if emoji:
            problems.append(f"emoji {emoji.group(0)!r}")
        if problems:
            leftovers[path] = problems
    assert leftovers == {}, f"docs drift from README facts: {leftovers}"


def test_pyproject_urls_use_canonical_github_repo():
    text = _read("pyproject.toml")
    assert "github.com/alfdav/TempFox" in text
    assert "github.com/alfdav/tempfox" not in text


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


def test_todo_marks_aug_2026_shipped_work_and_leaves_open_items():
    todo = _read("TODO.md")
    missing_shipped = [marker for marker in SHIPPED_TODO_MARKERS if marker not in todo]
    assert missing_shipped == [], f"TODO.md missing shipped markers: {missing_shipped}"
    missing_open = [
        marker for marker in OPEN_TODO_MARKERS if marker.lower() not in todo.lower()
    ]
    assert missing_open == [], f"TODO.md dropped open leftovers: {missing_open}"
    assert "Last updated: 2026-02-16" not in todo


def test_migration_uses_make_hygiene_not_black_isort():
    migration = _read("MIGRATION.md")
    assert "make hygiene-fast" in migration
    assert "make hygiene" in migration
    assert "uv run black" not in migration
    assert "uv run isort" not in migration


def test_roadmap_plan_status_matches_main():
    plan = _read("docs/plans/2026-02-16-todo-roadmap-implementation.md")
    assert "Task 1:" in plan and "done" in plan.lower()
    assert "Task 7:" in plan
    assert "rotation-workflow-spec.md" not in plan or "not created" in plan.lower()
    assert not (REPO_ROOT / "docs/plans/rotation-workflow-spec.md").exists()
    assert not (REPO_ROOT / "docs/plans/audit-logging-spec.md").exists()
    assert not (REPO_ROOT / "docs/plans/multi-account-spec.md").exists()
