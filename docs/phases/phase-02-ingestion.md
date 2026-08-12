# Phase 2 — Document Ingestion

**Days:** 2  
**Goal:** Turn PDFs and manual FAQs into tenant-scoped chunks + embeddings with visible processing status.

**Depends on:** Phase 1  
**Unlocks:** Phase 3 (RAG)

---

## Deliverables

1. **Upload & FAQ APIs** (JWT)
   - `POST /documents/upload` — PDF only in this phase
   - `POST /documents/faq` — Q&A pair as a document source
   - `GET /documents` — list with `status`, `error_message`, `chunk_count`, `bytes`
   - `DELETE /documents/{id}` — cascade chunks

2. **Background worker (arq or RQ + Redis)**
   - Extract text (`pdfplumber`)
   - Chunk with overlap; respect page breaks where possible
   - Embed with OpenAI `text-embedding-3-small` (dim 1536 locked)
   - Write `chunks` (+ `content_tsv` generated column)
   - Update document → `ready` or `failed` + `error_message`

3. **Usage logging**
   - Record embedding token usage on `usage_events`

4. **Storage**
   - Local/dev file storage path or object stub; enough for demo uploads

---

## Design notes

- No full UI yet — but API error messages must be human-readable (they surface in Phase 5 Documents page)
- Plan upload dropzone UX for Phase 5: dashed teal border, not a heavy card stack

---

## Acceptance criteria

- [ ] Upload a sample PDF → status `processing` → `ready` with `chunk_count > 0`
- [ ] Corrupt/empty file → `failed` with clear `error_message`
- [ ] FAQ ingest creates searchable chunks for that `tenant_id` only
- [ ] Delete document removes all related chunks
- [ ] Worker survives API restart (job in Redis)

---

## Out of scope

- URL crawler (Phase 6 Premium / later P2)
- DOCX (P3)
- Chat / retrieval
- Admin UI for uploads (Phase 5) — Postman/curl OK here

---

## Suggested test assets

- `fixtures/riverside/insurance-faq.pdf` (can be generated in Phase 6; placeholder text PDF OK now)

---

## Next

→ [Phase 3 — Hybrid RAG & security](phase-03-rag-security.md)
