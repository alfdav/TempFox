# Project Context (Consolidated)

This document preserves the still-relevant context previously spread across `mem_docs/`.
It is intended to be the maintained source of project context going forward.

## Product Purpose

TempFox is a CLI tool that:
- Accepts AWS credentials (AKIA long-term and ASIA temporary).
- Verifies AWS identity via `sts get-caller-identity`.
- Optionally saves credentials into AWS profiles.
- Runs `cloudfox aws all-checks` and stores timestamped outputs.
- Performs pre-flight checks/install flows for AWS CLI, Go, and CloudFox (UV optional).

## Current Architecture (Behavioral)

- Entry point: `tempfox.__main__ -> tempfox.core.main`.
- `tempfox.core`: CLI orchestration and backward-compatible exports.
- `tempfox.aws_profiles`: AWS config/credentials read-write and profile prompts.
- `tempfox.dependencies`: tool detection/install and pre-flight checks.
- `tempfox.cloudfox`: account lookup, output rotation, CloudFox execution helpers.

## Important Operational Characteristics

- Writes AWS credentials/config under `~/.aws` with `0600` permissions.
- Keeps only a bounded number of CloudFox output files.
- Allows listing and cleanup of TempFox-generated profiles via CLI flags.
- Uses subprocess-based integration with local toolchain (`aws`, `go`, `cloudfox`, `uv`).

## Priority Improvement Areas (Still Relevant)

- Better automated tests (especially integration/mocking around subprocess + profile writes).
- Clearer credential/session lifecycle handling and recovery paths.
- Continued hardening of installation/preflight paths across OS variants.
- Documentation consistency and drift prevention.

## What Was Intentionally Not Carried Forward

The following old `mem_docs` items were not retained as facts because they are outdated or speculative:
- Python 3.6 baseline (project now targets Python 3.8+).
- `boto3` as an active runtime dependency (removed from project metadata).
- `requirements.txt`/`setup.py` packaging model (migrated to `pyproject.toml` + UV).
- `aws_cli_manager.py` as an active module (dead/empty, removed).
- Claimed design patterns (singleton/factory/observer) that do not match implementation.

## Source Note

This file was derived from legacy notes in `mem_docs/` and validated against the current codebase on 2026-02-16.
