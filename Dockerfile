# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create app directory
WORKDIR /app

# Copy UV configuration files and README (needed for package metadata)
COPY pyproject.toml ./
COPY README.md ./

# Copy application code
COPY tempfox/ ./tempfox/

# Install dependencies and the package
RUN uv sync --no-dev && uv pip install -e .

# Create non-root user and set up UV cache in user home
RUN useradd --create-home --shell /bin/bash tempfox && \
    chown -R tempfox:tempfox /app
USER tempfox
ENV UV_CACHE_DIR=/home/tempfox/.cache/uv

# Set the entrypoint
ENTRYPOINT ["uv", "run", "tempfox"]
CMD ["--help"]
