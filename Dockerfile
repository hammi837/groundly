# Monorepo-friendly API image (Railway builds from repo root)
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN chmod +x /app/start.sh

ENV PYTHONPATH=/app
ENV PORT=8000
ENV GROUNDLY_DOCKER_BUILD=5
EXPOSE 8000

CMD ["/app/start.sh"]
