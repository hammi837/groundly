# Monorepo-friendly API image (Railway builds from repo root)
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV PYTHONPATH=/app
ENV GROUNDLY_DOCKER_BUILD=2
EXPOSE 8000

# Railway sets $PORT (often 8080). Fall back to 8000 for local Docker runs.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
