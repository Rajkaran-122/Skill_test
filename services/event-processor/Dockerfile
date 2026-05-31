FROM python:3.12-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"
COPY src/ src/
COPY tests/ tests/

FROM base AS development
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]

FROM base AS production
RUN pip install --no-cache-dir -e .
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]
