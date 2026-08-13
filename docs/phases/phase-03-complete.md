# Phase 3 — What We Built & Why

**Status:** Complete (code in repo)  
**Phase goal:** Make Groundly actually answer questions — grounded in tenant docs, with citations, honest “I don’t know,” and a hardened public chat API.

---

## The big picture

Phase 2 filled the knowledge base (chunks + embeddings).  
Phase 3 turns that into **answers**:

```
Visitor question
  → check API key + origin + rate limit
  → hybrid search (vector + keyword) scoped to tenant
  → if weak match → skip LLM, show handoff
  → else LLM answers ONLY from retrieved chunks
  → return answer + citations (or fallback)
  → optional lead capture via /chat/handoff
```

This is the product promise: *not a generic chatbot*.

---

## What we built

### 1. Hybrid retrieval
- **Vector search** (pgvector cosine) — meaning similarity  
- **Full-text search** (`tsvector`) — exact names like “Delta Dental”  
- **RRF fusion** — merge both ranked lists into one score  

**Why:** Pure vectors miss brand names and hours. Pure keywords miss paraphrases. Hybrid is what makes dental/clinic FAQs reliable.

### 2. Relevance threshold
If top score is too low (or no chunks) → **do not call the LLM**. Return fallback immediately.

**Why:** Calling the model with garbage context is how hallucinations happen. Skipping the model is safer.

### 3. Chat APIs (public widget path)
| Endpoint | Role |
|---|---|
| `POST /chat/message` | JSON answer + citations |
| `POST /chat/message/stream` | SSE `token` events + `final` |
| `POST /chat/handoff` | Capture email/name/phone + question |

Auth: **`X-Api-Key` header** (never admin JWT).

### 4. Grounded LLM prompt
System rules: answer only from context, refuse prompt injection / doc dumping, emit a fallback marker when unsure.

Modes:
- `LLM_MODE=fake` — offline keyword-grounded stub (dev)
- `LLM_MODE=anthropic` — Claude Sonnet for real demos

### 5. Security
- Origin allowlist per tenant (`allowed_origins`)
- Redis rate limit per API key + IP
- Message length cap
- Tenant filter on every retrieval query

### 6. Isolation test (upgraded)
`scripts/test_tenant_isolation.py` now:
- Creates two tenants with secret chunks  
- Asserts hybrid search never returns the other tenant’s content  
- Asserts each tenant still finds its own content  

---

## Why this matters for Fiverr / portfolio

Anyone can wrap ChatGPT. Phase 3 is proof you can:
1. Ground answers in **their** data  
2. Show **citations**  
3. **Refuse** when unsure (lead capture instead of lying)  
4. Keep tenants **isolated** under abuse (keys in the browser)

---

## How to try (when Docker is up)

```bash
# after seed + ingest FAQ/PDF from Phase 2
curl -X POST http://localhost:8000/chat/message \
  -H "X-Api-Key: <tenant_api_key>" \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -d '{"visitor_id":"v1","message":"Do you accept Delta Dental?"}'
```

Wrong origin → 403. Spam → 429. Unknown question → `was_fallback: true`.

Isolation:

```bash
docker compose exec api python /scripts/test_tenant_isolation.py
```

---

## Env knobs

| Variable | Meaning |
|---|---|
| `EMBEDDING_MODE` | `fake` / `openai` |
| `LLM_MODE` | `fake` / `anthropic` |
| `ANTHROPIC_API_KEY` | required for real Claude |
| `RELEVANCE_THRESHOLD` | optional; default in config |

---

## What Phase 3 did **not** do

| Skipped | Phase |
|---|---|
| Embeddable Shadow DOM widget | 4 |
| Admin conversations/leads UI | 5 |
| Live human agent WebSocket | later |

---

## Key files

| Path | Role |
|---|---|
| `backend/app/services/retrieval.py` | Hybrid search |
| `backend/app/services/llm.py` | Claude / fake |
| `backend/app/services/rag.py` | Orchestration + persistence |
| `backend/app/api/routes/chat.py` | Chat + SSE + handoff |
| `backend/app/core/deps.py` | API key + origin + rate limit |
| `scripts/test_tenant_isolation.py` | Isolation proof |
