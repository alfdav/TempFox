# TempFox

[![PyPI version](https://badge.fury.io/py/tempfox.svg)](https://badge.fury.io/py/tempfox)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Python CLI that holds AWS credentials (AKIA long-term or ASIA temporary) and runs CloudFox checks.

Python 3.8+. No third-party runtime dependencies.

## Install

```bash
uv tool install tempfox
```

```bash
uv tool uninstall tempfox
```

Install [UV](https://docs.astral.sh/uv/) first if you do not have it. `pip install tempfox` works as a one-liner; it is not a second supported installer.

From source:

```bash
git clone https://github.com/alfdav/TempFox.git
cd TempFox
uv sync
uv run tempfox
```

First run installs AWS CLI, Go, and CloudFox if they are missing. PATH updates apply to the current TempFox process only. To use `go` or `cloudfox` in other shells, add `~/.local/go/bin` and `~/go/bin` (or the Windows equivalents).

If you used the old `install.sh` / `install.ps1` scripts, remove the leftover venv (`~/.local/share/tempfox` on Unix, `%LOCALAPPDATA%\tempfox` on Windows) and any PATH lines those scripts added. Do that before `uv tool install`, or only after `uv tool uninstall`. Do not delete `~/.local/bin/tempfox` while a UV install is active.

Docker:

```bash
docker run --rm -it ghcr.io/alfdav/tempfox:latest
```

## Usage

```bash
tempfox
```

Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` first if you already have them. ASIA keys also need `AWS_SESSION_TOKEN`. TempFox prompts for anything missing, checks `sts get-caller-identity`, then runs CloudFox. Expired tokens exit; there is no renewal.

Flags:

- `--skip-preflight` — skip installing Go and CloudFox (AWS CLI is still checked)
- `--version` / `-v`
- `--list-profiles` — list AWS profiles and exit
- `--cleanup-profiles` — delete TempFox-created profiles and exit
- `--no-profile` — skip the prompt to save credentials as an AWS profile

## Development

```bash
make hygiene-fast
make hygiene
```

See `AGENTS.md` for the cleanup/review contract.

## License

MIT. See `LICENSE`. Copyright (c) 2024 David Diaz.

Use at your own risk. You are responsible for any AWS credentials you enter.
