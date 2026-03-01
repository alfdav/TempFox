SHELL := /bin/bash
RUN_TOOL := ./scripts/run_tool.sh

.PHONY: help test coverage lint format-check format typecheck repo-scan hygiene-fast hygiene hygiene-fix

help:
	@echo "Available targets:"
	@echo "  make hygiene-fast  # lint + format-check + typecheck + tests + repo scan"
	@echo "  make hygiene       # full gate (includes coverage threshold)"
	@echo "  make hygiene-fix   # apply safe ruff fixes, then run full gate"

test:
	$(RUN_TOOL) pytest -q

coverage:
	$(RUN_TOOL) pytest --cov=tempfox --cov-report=xml --cov-fail-under=35

lint:
	$(RUN_TOOL) ruff check .

format-check:
	$(RUN_TOOL) ruff format --check .

format:
	$(RUN_TOOL) ruff format .

typecheck:
	$(RUN_TOOL) mypy tempfox/

repo-scan:
	./scripts/repo_hygiene_check.sh

hygiene-fast: lint format-check typecheck test repo-scan

hygiene: lint format-check typecheck coverage repo-scan

hygiene-fix:
	$(RUN_TOOL) ruff check . --fix
	$(RUN_TOOL) ruff format .
	$(MAKE) hygiene
