# Groundly

AI support that only answers from your docs — white-label RAG chatbot with citations, human handoff, admin dashboard, and an embeddable widget.

## Docs

- [Product spec](ai-support-agent-platform-docs.md)
- [6-phase build plan](docs/phases/README.md)
- [Phase 1–5 what & why](docs/phases/) · [Phase 6 complete](docs/phases/phase-06-complete.md)
- [Design system](docs/design-system.md)
- [Deploy checklist](docs/ops/deploy-checklist.md)
- [Fiverr / portfolio pack](docs/portfolio/fiverr-pack.md)
- [Repo structure](STRUCTURE.md)

## Prerequisites

- PostgreSQL (local or Docker)
- Redis
- Node 20+
- Python 3.12+

## Quick start

### 1. Env

```bash
cp .env.example .env
# Set DATABASE_URL / REDIS_URL (see backend/.env)
```

### 2. API + migrations

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Optional worker (PDF uploads via queue):

```bash
cd backend
.venv\Scripts\arq app.workers.settings.WorkerSettings
```

### 3. Seed Riverside Dental

```bash
cd backend
.venv\Scripts\python ..\scripts\seed_riverside.py
# re-ingest FAQs: ... seed_riverside.py --force-faqs
```

| Field | Default |
|---|---|
| Email | `admin@riverside.demo` |
| Password | `riverside-demo` |
| Register | **disabled** (`REGISTER_ENABLED=false`) |

Seed prints the tenant **API key** for the widget / demo page.

### 4. Admin dashboard

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — login with seed credentials.

### 5. Widget + demo landing

```bash
cd widget
npm install
npm run build
copy dist\widget.js ..\demo\widget.js

npx --yes serve ..\demo -p 4173
```

Open `http://127.0.0.1:4173/?apiKey=YOUR_KEY` (API must be on `:8000`).

Widget-only hostile CSS harness: `cd widget && npm run dev` → http://localhost:5174

### 6. Eval + isolation

```bash
cd backend
.venv\Scripts\python ..\scripts\run_eval.py --verbose
.venv\Scripts\python ..\scripts\test_tenant_isolation.py
```

Record the eval pass rate for case studies — do **not** invent ROI like “automates 70%.”

Latest local run (`LLM_MODE=fake`, `EMBEDDING_MODE=fake`): **28/28 (100%)** on `evals/riverside_dental.json`. Re-measure after switching to real OpenAI/Anthropic keys.

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI, PostgreSQL (`float8[]` embeddings or pgvector), Redis |
| Admin | React + Vite |
| Widget | Vanilla JS + Shadow DOM → `widget.js` |
| LLM | Groq (`LLM_MODE=groq`), Claude (`anthropic`), or `fake` |
| Embeddings | OpenAI (`EMBEDDING_MODE=openai`) or `fake` |

## Status

Phases **1–6 complete** (local sellable demo). Public deploy: follow [docs/ops/deploy-checklist.md](docs/ops/deploy-checklist.md).
