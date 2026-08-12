# Phase 6 — Demo, Eval & Launch

**Days:** 1–2  
**Goal:** Portfolio conversion assets — live demo, honest metrics, Fiverr gallery, cloneable ops.

**Depends on:** Phases 1–5  
**Unlocks:** Fiverr gig + case study

---

## Deliverables

### Content & eval
1. `scripts/seed_riverside.py` — Riverside Dental tenant, admin, FAQs/PDF, starter questions, `allowed_origins`
2. `evals/riverside_dental.json` — 20–30 golden Qs (`should_answer` / `should_fallback`)
3. `scripts/run_eval.py` — prints pass rate (claim this, not fake ROI)
4. Isolation test run against demo data — green

### Demo surfaces
5. **Demo landing page** (Riverside + Groundly)
   - Brand-first hero: Groundly lockup, one headline, one sentence, one CTA (“Try the assistant”)
   - Dominant visual plane (gradient/atmosphere) — not a card collage
   - Live widget embedded; second fold can show “how it works” (citations + handoff) — one job per section
6. Demo admin credentials (register disabled on public demo)

### Deploy & ops
7. Deploy API + worker + DB + Redis (Railway/Render)
8. Deploy admin + widget + demo landing (Vercel)
9. README complete: setup, seed, eval, isolation, costs note
10. Optional P2 if time: analytics polish, URL crawler endpoint

### Fiverr / portfolio pack
11. Screenshots: widget citations, leads inbox, documents, logo on teal
12. 60–90s Loom script:
    - Grounded answer + citation  
    - Unknown → lead form  
    - Lead appears in admin  
13. Gig copy from product doc packages (Basic / Standard / Premium) — no “automates 70%” claims

---

## Design bar

- Landing hero follows design system hero budget (brand + headline + line + CTA + one visual)
- Fiverr gallery includes **logo lockup** and mark on product UI — brand recognition
- Export favicon set from mark if not done in Phase 1

---

## Acceptance criteria

- [ ] Public URL: landing + working widget
- [ ] Demo admin can log in and see seeded docs / test leads
- [ ] Eval script runs; pass rate recorded for case study
- [ ] Isolation + wrong-origin + fallback E2E verified on deploy
- [ ] README sufficient for a client to clone (or for you to re-deploy per client)
- [ ] Loom + 4 gallery images ready

---

## Out of scope (unless Premium sale)

- Slack/email webhook automation
- DOCX ingest
- Live human WebSocket chat
- Stripe

---

## Done definition for Groundly v1

Phases 1–6 complete → you have a **sellable white-label demo**: grounded RAG, citations, handoff, designed admin + widget, logo, live URL, honest eval metrics.
