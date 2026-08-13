# Groundly backend (FastAPI)

## Local (against Compose Postgres/Redis)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Via Docker Compose (from repo root)

```bash
docker compose up --build api
```

Migrations run automatically on API container start.

## Endpoints (Phase 1)

| Method | Path | Auth |
|---|---|---|
| GET | `/health` | none |
| POST | `/auth/login` | none |
| POST | `/auth/register` | gated by `REGISTER_ENABLED` |
| GET | `/auth/me` | Bearer JWT |
