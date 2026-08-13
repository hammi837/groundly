# Phase 4 — What We Built & Why

**Status:** Complete (code in repo)  
**Phase goal:** Ship the embeddable chat widget buyers see in a Loom — polished, isolated, and wired to Phase 3 chat APIs.

---

## The big picture

Phases 1–3 built the brain (auth, ingest, RAG).  
Phase 4 is the **face on the client website**:

```
Host page
  → <script src="widget.js" data-api-key ...>
  → Shadow DOM bubble (immune to host CSS)
  → SSE chat / citations / lead form
  → Groundly API (X-Api-Key)
```

Without a good widget, the product feels like a Postman demo — not a Fiverr deliverable.

---

## What we built

### 1. Vanilla TS widget (no React on the host)
Bundled to a single **`widget/dist/widget.js`** (IIFE) so any site can paste one script tag.

**Why:** Client sites run WordPress, Webflow, plain HTML — you cannot force React. Zero runtime deps keeps the embed small and safe.

### 2. Shadow DOM
All widget CSS lives inside a shadow root with Groundly tokens (teal/ink, Plus Jakarta Sans).

**Why:** Host themes love `button { width:100% !important }`. Shadow DOM is the only reliable isolation for an embed.

### 3. UX matching the design system
- Teal launcher with mark SVG  
- Panel open/close ~200ms  
- Welcome + starter questions  
- Streaming tokens + typing dots  
- Simple markdown rendering  
- Citation chips (staggered)  
- Privacy line: “Answers from this business’s documents”  
- Mobile bottom-sheet layout  
- Stable `visitor_id` in localStorage  

### 4. Lead form on fallback
When `was_fallback: true`, show email (required) + optional name/phone → `POST /chat/handoff`.

**Why:** This is the money feature — don’t lose the visitor when the bot doesn’t know.

### 5. `GET /widget/config`
Public (API-key) endpoint returns bot name, color, welcome, starters.

**Why:** Branding can be changed in admin later (Phase 5) without republishing the script.

### 6. Dev harness `widget/demo.html`
Intentionally broken “hostile” host CSS to prove isolation.

---

## How to run

```bash
# API up (Docker or local) + seed + some FAQs ingested
cd widget
npm install
npm run dev
# open demo, paste API key
```

Build:

```bash
npm run build   # → dist/widget.js
```

---

## What Phase 4 did **not** do

| Skipped | Phase |
|---|---|
| Admin “copy embed snippet” UI | 5 |
| Live human agent takeover | later |
| Production CDN deploy | 6 |

---

## Key files

| Path | Role |
|---|---|
| `widget/src/widget.ts` | UI + Shadow DOM |
| `widget/src/api.ts` | Config, SSE, handoff |
| `widget/src/styles.ts` | Isolated CSS + mark SVG |
| `widget/demo.html` | Hostile CSS proof |
| `backend/app/api/routes/widget_config.py` | Branding config API |
