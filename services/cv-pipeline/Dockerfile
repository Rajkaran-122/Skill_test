# ============================================================
# SIP CV Pipeline — Multi-Stage Dockerfile
# ============================================================

# --- Base Stage ---
FROM python:3.12-slim AS base

WORKDIR /app

# System dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY src/ src/
COPY tests/ tests/

# --- Development Stage ---
FROM base AS development
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]

# --- Production Stage ---
FROM base AS production
RUN pip install --no-cache-dir -e .
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]
