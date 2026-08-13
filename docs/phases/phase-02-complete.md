# Phase 2 — What We Built & Why

**Status:** Complete (code in repo)  
**Phase goal:** Turn PDFs and FAQs into searchable chunks with embeddings — the knowledge Groundly will answer from in Phase 3.

---

## The big picture

Phase 1 built empty drawers (`documents`, `chunks`).  
Phase 2 **fills** them:

```
Upload PDF or FAQ
  → save file / capture text
  → background worker (Redis + arq)
  → extract text
  → split into overlapping chunks
  → create embeddings (vectors)
  → store in Postgres (pgvector + full-text column)
  → mark document ready (or failed with a clear error)
```

Without this, the chatbot has nothing “grounded” to read.

---

## What we built

### 1. Document APIs (JWT)
| Endpoint | Purpose |
|---|---|
| `POST /documents/upload` | Upload a PDF |
| `POST /documents/faq` | Add a Q&A pair |
| `GET /documents` | List docs + status / errors / chunk counts |
| `DELETE /documents/{id}` | Remove doc + chunks (+ PDF file) |

**Why:** Non-technical clients (later via dashboard) and you (now via curl/Postman) need a way to manage knowledge per tenant.

### 2. Background worker (arq + Redis)
API returns quickly with `status=processing`. A separate **worker** process does the heavy lifting.

**Why:** Extracting a big PDF and calling an embedding API can take seconds/minutes. Doing that inside the HTTP request would freeze the UI and time out. Jobs live in Redis so they survive an API restart.

### 3. Extract → chunk → embed → store
- **pdfplumber** reads text page by page
- Chunks ~1800 chars with overlap (keeps sentences from being cut awkwardly)
- Embeddings: `text-embedding-3-small` when `EMBEDDING_MODE=openai`, or **fake** deterministic vectors for offline/dev
- Rows written to `chunks` (vector + auto `content_tsv` for later hybrid search)
- `usage_events` logs embedding token usage

**Why:** Chunks are the units RAG searches. Embeddings turn meaning into numbers so “Delta Dental” questions can find the insurance FAQ even with different wording. Fake mode lets you develop without spending API money; switch to OpenAI before real demos.

### 4. Local file storage
PDFs saved under `uploads/{tenant_id}/{document_id}.pdf` (shared volume in Docker for API + worker).

**Why:** The worker needs the same file the API saved. A shared folder (or later S3) is required.

### 5. Sample fixture
`fixtures/riverside/insurance-faq.pdf` — tiny dental FAQ PDF for testing.

---

## Why this phase matters for Fiverr / portfolio

Buyers care that the bot uses **their** content. Ingestion is the pipeline that makes “trained on your docs” true — not a ChatGPT wrapper with a prompt pretending to know the business.

---

## How to try it (when Docker is up)

```bash
docker compose up --build -d
docker compose exec api python /scripts/seed_riverside.py

# login → token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@riverside.demo","password":"riverside-demo"}' | jq -r .access_token)

# FAQ ingest
curl -X POST http://localhost:8000/documents/faq \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Do you accept Delta Dental?","answer":"Yes, we accept Delta Dental PPO plans."}'

# PDF ingest
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@fixtures/riverside/insurance-faq.pdf"

# poll status until ready
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/documents
```

Set `EMBEDDING_MODE=openai` and `OPENAI_API_KEY=...` in `.env` for real vectors before Phase 3 demos.

---

## What Phase 2 did **not** do

| Skipped | Comes in |
|---|---|
| Chat / answers / citations | Phase 3 |
| URL crawler | Phase 6 / Premium |
| DOCX | Later |
| Admin upload UI | Phase 5 |

---

## Key files

| Path | Role |
|---|---|
| `backend/app/api/routes/documents.py` | Upload / FAQ / list / delete |
| `backend/app/services/ingest.py` | Pipeline |
| `backend/app/services/extract.py` | PDF text |
| `backend/app/services/chunking.py` | Splitting |
| `backend/app/services/embeddings.py` | OpenAI or fake |
| `backend/app/workers/settings.py` | arq worker |
| `fixtures/riverside/insurance-faq.pdf` | Sample PDF |
