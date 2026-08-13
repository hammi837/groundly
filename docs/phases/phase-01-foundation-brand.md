# Phase 1 — Foundation & Brand

**Days:** 2–3  
**Goal:** Lock brand + design, stand up local infra, schema, and admin auth so every later phase builds on a real product shell.

**Depends on:** nothing  
**Unlocks:** Phase 2 (ingestion)

---

## Deliverables

1. **Brand kit in repo**
   - Logo lockup + mark under `assets/brand/`
   - Design tokens documented in [design-system.md](../design-system.md)
   - CSS variables file stub (`packages` or `frontend/src/styles/tokens.css`) matching the design system

2. **Local infrastructure**
   - `docker-compose.yml`: Postgres (pgvector), Redis, API (stub), worker (stub)
   - `.env.example`, root `README.md` (clone → up → health)

3. **Backend core**
   - FastAPI app skeleton
   - Alembic migrations for full schema from product doc (tenants with branding/security fields, users, documents, chunks + `tsvector`, conversations, messages, leads, usage_events)
   - JWT login (`POST /auth/login`), `GET /auth/me`
   - Register **invite-only / disabled by default** (env flag)
   - `GET /health` (DB + Redis)

4. **Seed hook (empty or minimal)**
   - Script path ready: `scripts/seed_riverside.py` (full content in Phase 6; Phase 1 can create one tenant + admin)

5. **Isolation test stub**
   - `scripts/test_tenant_isolation.py` exists and fails clearly until Phase 3 fills retrieval (or asserts schema-level separation for two tenants)

---

## Design / logo work this phase

- Confirm Groundly name + tagline: *AI support that only answers from your docs*
- Place logos in dashboard favicon path (even if UI is blank shell)
- Choose and wire Google Fonts (or self-host): display + UI + mono from design system
- Admin shell wireframe: left nav + top bar with **Groundly lockup** (brand-first chrome)

---

## Acceptance criteria

- [x] `docker compose up` starts Postgres + Redis; API returns healthy
- [x] Migrations apply cleanly; HNSW + GIN indexes exist
- [x] Login with seeded admin returns JWT
- [x] Design tokens + logo files committed
- [x] README documents env vars and how to run

> Implementation landed in repo (Compose, Alembic `0001_phase1_foundation`, JWT auth, seed, admin shell). Run the Quick start in the root README to verify on your machine.

---

## Out of scope

- PDF upload, RAG, widget, full dashboard pages, crawler

---

## Files to create (suggested)

```
backend/
  app/main.py
  app/core/config.py
  app/db/
  alembic/
frontend/   # or apps/admin — shell only
  src/styles/tokens.css
assets/brand/
docs/design-system.md
docker-compose.yml
.env.example
README.md
```

---

## Next

→ [Phase 2 — Document ingestion](phase-02-ingestion.md)
