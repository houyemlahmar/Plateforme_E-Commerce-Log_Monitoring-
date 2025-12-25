# ============================================
# Multi-stage Production-Ready Flask Dockerfile
# Python 3.11-slim | Gunicorn WSGI Server
# Optimized for: Security, Size, Layer Caching
# ============================================

# ============================================
# Stage 1: Builder - Dependencies Installation
# ============================================
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Install system build dependencies (only needed for building packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
# Changes to requirements.txt will invalidate this layer and all subsequent ones
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================
# Stage 2: Runtime - Lightweight Production Image
# ============================================
FROM python:3.11-slim

# Security: Create non-root user for running the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Install only runtime system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_ENV=production \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=300

# Copy application source code (after dependencies for better caching)
# Any change to the code will only invalidate this layer and subsequent ones
COPY --chown=appuser:appuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app/uploads /app/logs && \
    chmod 755 /app/uploads /app/logs

# Switch to non-root user for security
USER appuser

# Expose application port
EXPOSE 5000

# Health check endpoint - ensures container is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Gunicorn production server entrypoint
# --bind: Listen on all interfaces
# --workers: Number of worker processes (CPU cores * 2 + 1)
# --threads: Threads per worker for handling concurrent requests
# --timeout: Worker timeout in seconds
# --access-logfile: Log all HTTP requests to stdout
# --error-logfile: Log errors to stderr
# --log-level: Logging verbosity
CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "4", \
    "--threads", "2", \
    "--timeout", "300", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "main:create_app()"]
