# Phase 1 — What We Built & Why

**Status:** Complete (code in repo)  
**Phase goal:** Give Groundly a real foundation — brand, database, auth, and local infra — before any AI features.

This note is for you (and future clients/case studies): **what** we did, **why** we needed it, and a short explanation of each piece.

---

## The big picture

Without Phase 1, Phase 2+ would be chaos: nowhere to store tenants, no login, no Postgres/Redis, no brand. Phase 1 is the **skeleton**. Later phases hang muscles on it (ingest → RAG → widget → dashboard).

```
Phase 1 foundation
    → Phase 2: fill knowledge (PDFs/FAQs)
    → Phase 3: answer questions safely
    → Phase 4–5: show it to buyers
    → Phase 6: live demo
```

---

## 1. Brand & design system

### What we did
- Named the product **Groundly**
- Locked tagline: *AI support that only answers from your docs*
- Created logo lockup + mark icon under `assets/brand/`
- Wrote [design-system.md](../design-system.md) (teal/ink colors, fonts, layout rules)
- Put CSS tokens in `frontend/src/styles/tokens.css`
- Built a simple admin **shell** (left nav + top bar with logo)

### Why we needed it
Fiverr buyers judge in seconds. A generic purple “AI dashboard” looks like every other gig. Brand + tokens early means every later screen (widget, admin, demo landing) looks like **one product**, not bolted-together tutorials.

### Simple explanation
Think of brand as the storefront sign and paint colors. You paint the walls before stocking shelves — same idea.

---

## 2. Docker Compose (Postgres + Redis + API + worker stub)

### What we did
- Added `docker-compose.yml` with:
  - **Postgres** (`pgvector/pgvector`) — data + vector search later
  - **Redis** — rate limits + background jobs later
  - **API** container — runs migrations, then FastAPI
  - **Worker** stub — placeholder until Phase 2 ingest jobs

### Why we needed it
Groundly is not a single script. It needs a database and a job queue. Docker lets anyone (you, a client, a future you) run the same stack with one command instead of installing Postgres by hand.

### Simple explanation
Compose is a recipe: “start these services together.” Postgres = filing cabinet. Redis = sticky notes / waiting line for heavy work. API = the waiter taking orders.

> **Note:** Full `docker compose up` verification can wait until project end if Docker Desktop is flaky on your machine. The files are ready.

---

## 3. Database schema (Alembic migration)

### What we did
- Migration `0001_phase1_foundation` creates all core tables:
  - `tenants` — each business (branding, API key, allowed origins…)
  - `users` — admin logins tied to a tenant
  - `documents` / `chunks` — knowledge base (filled in Phase 2)
  - `conversations` / `messages` — chat history (Phase 3+)
  - `leads` — handoff emails when the bot doesn’t know
  - `usage_events` — token/cost tracking
- Enabled **pgvector** + **HNSW** index (for similarity search later)
- Enabled **full-text (`tsvector` + GIN)** on chunks (for keyword search later)

### Why we needed it
Multi-tenant means every row must know which business it belongs to (`tenant_id`). If we skip that and “add tenancy later,” we risk leaking Client A’s FAQs to Client B — fatal for a support product.

Building indexes now means Phase 3 hybrid RAG does not require a painful schema rewrite.

### Simple explanation
Schema = the shape of the filing cabinet drawers. We labeled drawers for “who owns this,” “source docs,” “chat,” and “leads” before stuffing papers in.

---

## 4. FastAPI app + health check

### What we did
- `backend/app/main.py` — Groundly API entry
- `GET /health` — checks database **and** Redis
- Config via env (`.env` / `.env.example`)
- CORS for the local admin UI

### Why we needed it
A health endpoint proves the stack is actually wired. When something breaks in production or on a client laptop, `/health` tells you instantly: DB down? Redis down? Or only the app?

### Simple explanation
Health is like a “systems OK” light on a car dashboard.

---

## 5. Auth (JWT login, gated register, `/auth/me`)

### What we did
- `POST /auth/login` — email/password → JWT
- `GET /auth/me` — who am I + tenant summary
- `POST /auth/register` — **disabled by default** (`REGISTER_ENABLED=false`)
- Passwords hashed with bcrypt; tokens signed with `JWT_SECRET`

### Why we needed it
The admin dashboard must not be public. JWT is a standard “wristband” after login: the API can trust requests without storing server sessions for every click.

Open self-serve register would turn the portfolio demo into a spam magnet. Invite-only / disabled register matches the white-label story: **you** create tenants for clients (or seed Riverside).

### Simple explanation
Login checks the password. JWT is a temporary badge. Register stays locked so random people cannot open new businesses on your demo.

**Demo seed account (Phase 1):**
- Email: `admin@riverside.demo`
- Password: `riverside-demo`

---

## 6. Seed script (`scripts/seed_riverside.py`)

### What we did
- Creates **Riverside Dental Group** tenant + admin user
- Sets bot name, color, welcome message, starter questions, allowed origins

### Why we needed it
You need a realistic fake client for demos and later evals. Seeding beats clicking register every time you reset the DB.

### Simple explanation
One command fills the demo clinic into the database so you can log in and show the product.

---

## 7. Isolation test stub (`scripts/test_tenant_isolation.py`)

### What we did
- Creates two temporary tenants, each with a document
- Asserts queries filtered by `tenant_id` do not cross-leak
- Cleans up after itself
- Phase 3 will extend this to **retrieval** (vector search) isolation

### Why we needed it
“Trust me, it’s multi-tenant” is not enough for a portfolio or a client. An automated check catches mistakes when someone forgets `WHERE tenant_id = …`.

### Simple explanation
Two fake clinics, two folders of docs — the test makes sure Clinic A never sees Clinic B’s file names.

---

## 8. Repo / ops hygiene

### What we did
- `.gitignore` (no `.env`, venv, `node_modules`, uploads…)
- `.env.example` documenting required variables
- Root `README.md` with Quick start
- Backend/frontend/widget folder structure

### Why we needed it
Pushing secrets or junk to GitHub is how projects get burned. A clear README is how you (or a Fiverr client with source code) can run Groundly again months later.

---

## What Phase 1 deliberately did **not** do

| Skipped | Why wait |
|---|---|
| PDF upload / embeddings | Needs Phase 2 worker + OpenAI key |
| Chat / RAG answers | Needs knowledge in DB first (Phase 3) |
| Fancy widget | Buyers see it in Phase 4; needs chat API |
| Full admin pages | Phase 5; shell is enough for brand now |
| URL crawler / Stripe | Premium / out of MVP |

---

## Files that matter most (Phase 1)

| Path | Role |
|---|---|
| `docker-compose.yml` | Local stack |
| `backend/alembic/versions/0001_phase1_foundation.py` | Database shape |
| `backend/app/models/__init__.py` | ORM models |
| `backend/app/api/routes/auth.py` | Login / register / me |
| `backend/app/api/routes/health.py` | Health |
| `scripts/seed_riverside.py` | Demo tenant |
| `scripts/test_tenant_isolation.py` | Isolation check |
| `frontend/src/App.tsx` + `styles/*` | Branded admin shell |
| `docs/design-system.md` | Design rules |

---

## How to run Phase 1 (when Docker is ready)

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python /scripts/seed_riverside.py
curl http://localhost:8000/health
```

Admin UI shell:

```bash
cd frontend && npm install && npm run dev
```

---

## Phase 1 → Phase 2 bridge

Phase 1 gave us **tenants, users, empty document/chunk tables, and Redis**.  
Phase 2 fills those tables: upload PDF/FAQ → extract text → chunk → embed → store — so Phase 3 can answer questions from real content.
