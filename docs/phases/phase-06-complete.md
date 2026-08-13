# Phase 6 complete — what & why

**Goal:** Sellable demo assets — seeded Riverside content, honest eval metrics, brand-first landing with live widget, ops + Fiverr pack. Not a Stripe SaaS launch.

---

## What we built

### Content & eval
1. **`scripts/seed_riverside.py`** — tenant + admin + 9 FAQs ingested synchronously (no worker required for demo knowledge). Re-run with `--force-faqs`. Merges demo origins into `allowed_origins`.
2. **`evals/riverside_dental.json`** — 28 golden cases (`answer` vs `fallback`), including hours/insurance/appointments and off-topic / injection refusals.
3. **`scripts/run_eval.py`** — runs retrieval + LLM path against the golden set; prints overall / should-answer / should-fallback pass rates. **Claim this number**, not fictional ROI.

**Recorded locally (fake LLM + fake embeddings):** 28/28 (100%). Re-run after enabling real API keys.

### Demo surfaces
4. **`demo/`** — Groundly-branded landing (Fraunces + Plus Jakarta, teal atmosphere, hero budget: brand + headline + line + CTA + one visual plane). Second fold: how it works. Live widget via `demo/widget.js` + `?apiKey=`.
5. Register stays **disabled** by default for public demos.

### Ops & portfolio
6. **`docs/ops/deploy-checklist.md`** — local + Railway/Render/Vercel sketch, smoke tests, costs note.
7. **`docs/portfolio/fiverr-pack.md`** — Basic/Standard/Premium copy, gallery shot list, 60–90s Loom script.
8. **README** — full clone path: seed, eval, isolation, widget, demo, admin.

---

## Why this shape

| Choice | Why |
|---|---|
| Sync FAQ ingest in seed | Eval and demo work without waiting on arq |
| Measured eval pass rate | Case study / Loom stay honest |
| Brand-first landing, not a card collage | Matches design system + Fiverr gallery recognition |
| Checklist over “we deployed for you” | Public URL is environment-specific; ops doc is the reusable deliverable |
| No URL crawler / Slack webhooks | Explicitly Premium / out of v1 scope |

---

## How to verify

```bash
# from backend venv
python ..\scripts\seed_riverside.py
python ..\scripts\run_eval.py --verbose
python ..\scripts\test_tenant_isolation.py

cd ..\widget && npm run build && copy dist\widget.js ..\demo\widget.js
npx --yes serve ..\demo -p 4173
# open http://127.0.0.1:4173/?apiKey=...
```

---

## Acceptance (local)

- [x] Seeded FAQs + golden eval + runner
- [x] Demo landing + widget embed path
- [x] README / deploy checklist / Fiverr pack
- [ ] Public production URL — fill when you deploy (see checklist)
- [ ] Loom + gallery screenshots — shoot using the pack script

**Groundly v1 code path (Phases 1–6) is complete** for a sellable white-label demo; production hosting is the remaining ops step on your accounts.
