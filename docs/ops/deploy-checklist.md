# Deploy checklist (Phase 6)

Cloneable ops for a Groundly demo or per-client deploy. Fill dates as you go.

## Local (required before public URL)

- [ ] Postgres reachable (`DATABASE_URL` / `DB_*`)
- [ ] Redis reachable (`REDIS_URL`)
- [ ] `alembic upgrade head`
- [ ] `python scripts/seed_riverside.py` (prints API key + admin)
- [ ] API: `uvicorn app.main:app --reload --port 8000`
- [ ] Worker (PDF path): `arq app.workers.settings.WorkerSettings`
- [ ] Admin: `cd frontend && npm run dev` → http://localhost:5173
- [ ] Widget build: `cd widget && npm run build` → copy `dist/widget.js` to `demo/widget.js`
- [ ] Demo landing: serve `demo/` (e.g. `npx serve demo -p 4173`) with `?apiKey=...`
- [ ] Tenant `allowed_origins` includes the demo origin
- [ ] `python scripts/run_eval.py --verbose` — record pass rate
- [ ] `python scripts/test_tenant_isolation.py` — green
- [ ] Wrong-origin chat request rejected
- [ ] Unknown question → lead form → appears in admin Leads
- [ ] `REGISTER_ENABLED=false` on any public demo

## Production sketch

| Piece | Typical host |
|---|---|
| API + worker | Railway / Render / Fly |
| Postgres + Redis | Same provider add-ons |
| Admin (`frontend`) | Vercel |
| Widget + `demo/` | Vercel static / Cloudflare Pages |

### Env to set in prod

- `DATABASE_URL`, `REDIS_URL`
- `JWT_SECRET` (long random)
- `REGISTER_ENABLED=false`
- `EMBEDDING_MODE=openai` + `OPENAI_API_KEY` (when leaving fake mode)
- `LLM_MODE=anthropic` + `ANTHROPIC_API_KEY`
- `CORS_ORIGINS` — admin + demo origins
- After seed: set tenant `allowed_origins` to the public demo/widget host(s)

### Smoke after deploy

1. `/health` → db + redis true  
2. Login demo admin  
3. Widget on landing answers a seeded FAQ with citation  
4. Fallback + lead capture  
5. Isolation + eval scripts against prod DB (carefully; don’t spam rate limits)

## Costs note

With real keys, cost is mostly embeddings on ingest + Claude tokens per chat turn.  
`usage_events` in the DB is the honest place to estimate burn — don’t invent ROI percentages.
