# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create app directory
WORKDIR /app

# Copy UV configuration files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY tempfox/ ./tempfox/
COPY README.md ./

# Install the package
RUN uv pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash tempfox
USER tempfox

# Set the entrypoint
ENTRYPOINT ["uv", "run", "tempfox"]
CMD ["--help"]
