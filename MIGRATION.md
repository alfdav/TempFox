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

#### Option 1: Use UV (Recommended)
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install TempFox
uv tool install tempfox
```

#### Option 2: Use Installation Scripts
```bash
# Unix/Linux/macOS
curl -sSL https://raw.githubusercontent.com/alfdav/tempfox/main/install.sh | bash

# Windows PowerShell
iwr https://raw.githubusercontent.com/alfdav/tempfox/main/install.ps1 | iex
```

#### Option 3: Use Docker
```bash
docker run --rm -it \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  ghcr.io/alfdav/tempfox:latest
```

### For Developers

#### Old Development Setup
```bash
git clone https://github.com/alfdav/tempfox.git
cd tempfox
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
```

#### New Development Setup with UV
```bash
git clone https://github.com/alfdav/tempfox.git
cd tempfox
uv sync
uv run tempfox
```

#### New Development Setup with Docker
```bash
git clone https://github.com/alfdav/tempfox.git
cd tempfox
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

# New way with UV
uv run black .
uv run isort .
uv run ruff check .
uv run mypy tempfox/
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

### New Files
- `Dockerfile` - Production container
- `Dockerfile.dev` - Development container
- `docker-compose.yml` - Development orchestration
- `.dockerignore` - Docker build optimization
- `install.sh` / `install.ps1` - Cross-platform installation scripts
- `uninstall.sh` / `uninstall.ps1` - Clean uninstallation scripts

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
If you're using Python < 3.8:
1. Upgrade to Python 3.8 or higher
2. Use the legacy pip installation method temporarily
3. Consider using Docker for consistent environment

## Rollback Plan

If you need to rollback to the old system:
1. Uninstall UV version: `uv tool uninstall tempfox`
2. Install via pip: `pip install tempfox`
3. Use the previous development setup with virtual environments

## Support

For issues with the migration:
1. Check the [GitHub Issues](https://github.com/alfdav/tempfox/issues)
2. Review the updated [README.md](README.md)
3. Try the Docker option for a clean environment
4. Create a new issue with migration details if problems persist
