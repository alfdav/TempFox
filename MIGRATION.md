# Migration Guide: From pip to UV and Docker

This guide helps you migrate from the traditional pip-based setup to the new UV and Docker-based development environment.

## What Changed

### Package Management
- **Before**: pip + requirements.txt + setup.py
- **After**: UV + pyproject.toml (modern Python packaging)

### Python Version Support
- **Before**: Python 3.6+
- **After**: Python 3.8+ (following modern Python support lifecycle)

### Development Tools
- **Before**: Manual setup of linting and testing tools
- **After**: Integrated development environment with UV

### Containerization
- **New**: Docker support for consistent development and deployment

## Migration Steps

### For End Users

#### Option 1: Use UV

If an older clone left a script-based install behind, remove that leftover first so you do not delete the UV shim later:

```bash
# Unix leftover venv from install.sh (do this before uv tool install)
rm -rf ~/.local/share/tempfox
# Windows leftover from install.ps1: Remove-Item -Recurse -Force $env:LOCALAPPDATA\tempfox
# Also drop PATH lines those scripts added to ~/.bashrc, ~/.zshrc, or the Windows user PATH.
```

Then install with UV:

```bash
# Install UV (Unix/Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install UV (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install TempFox
uv tool install tempfox

# Remove TempFox
uv tool uninstall tempfox
```

`pip install tempfox` still works as a one-line alternative. Do not use the retired `install.sh` / `install.ps1` scripts.

The retired scripts persisted Go, CloudFox, and UV on your shell PATH. UV only puts `tempfox` on PATH. Runtime preflight still installs AWS CLI, Go, and CloudFox for the current TempFox process only.

#### Option 2: Use Docker
```bash
docker run --rm -it ghcr.io/alfdav/tempfox:latest
```

### For Developers

#### Old Development Setup
```bash
git clone https://github.com/alfdav/TempFox.git
cd TempFox
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
```

#### New Development Setup with UV
```bash
git clone https://github.com/alfdav/TempFox.git
cd TempFox
uv sync
uv run tempfox
```

#### New Development Setup with Docker
```bash
git clone https://github.com/alfdav/TempFox.git
cd TempFox
docker-compose run tempfox-dev
```

## Key Benefits

### UV Benefits
- **Faster**: UV is significantly faster than pip
- **Better Dependency Resolution**: More reliable dependency management
- **Modern**: Follows latest Python packaging standards (PEP 517/518)
- **Integrated Tools**: Built-in support for development tools

### Docker Benefits
- **Consistency**: Same environment across all systems
- **Isolation**: No conflicts with system packages
- **Easy Deployment**: Ready-to-use containers
- **Development Environment**: Pre-configured development containers

## Development Workflow Changes

### Testing
```bash
# Old way
pip install pytest
pytest

# New way with UV
uv run pytest
```

### Linting and Formatting
```bash
# Old way
pip install black isort ruff mypy
black .
isort .
ruff check .
mypy tempfox/

# Current gates (ruff + mypy + pytest + repo-scan via Makefile / pre-commit)
make hygiene-fast
make hygiene
```

### Adding Dependencies
```bash
# Old way
echo "new-package>=1.0.0" >> requirements.txt
pip install -r requirements.txt

# New way with UV
uv add "new-package>=1.0.0"
```

### Adding Development Dependencies
```bash
# Old way
echo "pytest>=7.0.0" >> requirements-dev.txt
pip install -r requirements-dev.txt

# New way with UV
uv add --dev "pytest>=7.0.0"
```

## File Changes

### Removed Files
- `requirements.txt` - Replaced by dependencies in pyproject.toml
- `setup.py` - Replaced by modern pyproject.toml configuration
- `install.sh` / `install.ps1` / `uninstall.sh` / `uninstall.ps1` - Replaced by `uv tool install tempfox` and `uv tool uninstall tempfox`

### New Files
- `Dockerfile` - Production container
- `Dockerfile.dev` - Development container
- `docker-compose.yml` - Development orchestration
- `.dockerignore` - Docker build optimization

### Modified Files
- `pyproject.toml` - Updated with UV configuration and modern packaging
- `.gitignore` - Added UV and Docker-related ignores
- `README.md` - Updated installation and development instructions
- `.github/workflows/` - Updated CI/CD for UV and Docker

## Troubleshooting

### UV Installation Issues
If UV installation fails, try:
```bash
# Alternative installation method
pip install uv
```

### Docker Issues
If Docker commands fail:
1. Ensure Docker is installed and running
2. Check Docker permissions (add user to docker group on Linux)
3. Try with `sudo` if necessary

### Python Version Issues
TempFox needs Python 3.8 or higher. Upgrade, or use the Docker image.

## Rollback

`pip install tempfox` still works as a one-liner. It is not a second supported installer.

## Support

For issues with the migration:
1. Check the [GitHub Issues](https://github.com/alfdav/TempFox/issues)
2. Review the updated [README.md](README.md)
3. Try the Docker option for a clean environment
4. Create a new issue with migration details if problems persist
