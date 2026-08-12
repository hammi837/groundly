# Phase 5 — Admin Dashboard

**Days:** 2–3  
**Goal:** Non-technical client UI — upload docs, see chats, work leads, copy embed code. This is your differentiator vs $50 wrappers.

**Depends on:** Phases 3–4  
**Unlocks:** Phase 6 (demo admin login)

---

## Deliverables

### App shell
- React + Vite + Tailwind (or CSS modules) using **design tokens**
- Auth: login page with Groundly lockup (brand-first, not a tiny eyebrow)
- Layout: left nav + content; header shows lockup / tenant name
- Fonts: display + UI from design system

### Pages
1. **Documents** — upload PDF, add FAQ, status / errors / chunk counts, delete  
2. **Conversations** — list + detail with citations  
3. **Leads inbox** — email, name, phone, question, status `new`/`contacted`, open transcript  
4. **Settings** — bot name, primary color, welcome, starter questions, allowed origins, embed snippet, API key reveal, optional webhook URL  
5. **Analytics (thin / optional if time)** — volume + unanswered list only (full polish can finish in Phase 6)

### API wiring
- All JWT-protected routes from product spec
- Embed snippet generator matching Phase 4 widget

---

## Design bar (non-negotiable)

Follow [design-system.md](../design-system.md):

- Atmosphere background (soft teal wash), not flat gray-white only
- Cards only where interaction needs a container (upload zone, settings groups) — not decorative card grids
- Leads = clean list/table, subtle status chips
- Empty states with one CTA
- Primary buttons teal, radius 8–10px (not pill soup)
- Groundly logo in header at recognizable size

**Login first viewport:** brand lockup + short line (“Manage your grounded support agent”) + form — one composition.

---

## Acceptance criteria

- [ ] Login → documents upload → chunks ready (poll status)
- [ ] Conversation detail shows citations
- [ ] Lead from widget appears in inbox; status can flip to `contacted`
- [ ] Settings update changes widget welcome/color on reload
- [ ] Embed snippet copyable and works against Phase 4 widget
- [ ] UI matches design tokens (no default purple theme)

---

## Out of scope

- Stripe billing
- Open public registration
- Question-clustering “AI insights” theater

---

## Next

→ [Phase 6 — Demo, eval & launch](phase-06-demo-deploy.md)
