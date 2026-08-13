# Phase 5 — What We Built & Why

**Status:** Complete (code in repo)  
**Phase goal:** Give non-technical clients (and your Fiverr demo) a real admin — upload knowledge, see chats, work leads, copy the embed snippet.

---

## The big picture

Phases 1–4 built the engine + widget.  
Phase 5 is the **control panel** that makes Groundly feel like a product, not a script:

```
Login (JWT)
  → Documents (PDF/FAQ + processing status)
  → Conversations (transcript + citations)
  → Leads inbox (handoff follow-up)
  → Settings (branding, origins, API key, embed code)
  → Overview (thin analytics + content gaps)
```

This is the differentiator vs $50 “PDF chatbot” gigs.

---

## What we built

### Backend (JWT admin APIs)
- `GET/PATCH /settings` — branding, origins, webhook, masked/reveal API key, embed snippet  
- `GET /conversations` + `GET /conversations/{id}` — list + transcript with citation labels  
- `GET/PATCH /leads` — inbox + `new`/`contacted`  
- `GET /analytics/overview` + `/analytics/unanswered` — volume + content gaps  

### Frontend (design-system UI)
- Brand-first **login** (lockup + one job: sign in)  
- Shell with left nav + Groundly lockup header  
- **Documents** — dashed teal upload zone, FAQ form, status polling  
- **Conversations** — list + detail with citation chips  
- **Leads** — table, mark contacted, open transcript  
- **Settings** — save branding, reveal key, copy embed snippet  
- **Overview** — stats + unanswered list  

No purple SaaS theme — teal/ink tokens, Fraunces + Plus Jakarta Sans.

---

## Why it matters

Clients will not live in Postman. If they can upload a FAQ and see a lead appear after a widget fallback, they understand the product — and keep paying for updates.

---

## How to run

```bash
# API + worker + DB running, seed done
cd frontend
npm install
npm run dev
```

Login: `admin@riverside.demo` / `riverside-demo`

---

## What Phase 5 did **not** do

| Skipped | Phase |
|---|---|
| Live public deploy + Loom | 6 |
| Fancy question clustering | out of scope |
| Stripe billing | never for this framing |

---

## Key files

| Path | Role |
|---|---|
| `frontend/src/pages/*` | Login, docs, chats, leads, settings, overview |
| `frontend/src/layouts/AppShell.tsx` | Nav chrome |
| `frontend/src/lib/api.ts` | JWT API client |
| `backend/app/api/routes/settings.py` | Settings + embed snippet |
| `backend/app/api/routes/admin.py` | Conversations, leads, analytics |
