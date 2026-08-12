# Phase 4 — Embeddable Widget

**Days:** 1–2  
**Goal:** Ship a portfolio-grade chat widget — this is what Fiverr buyers see in the Loom.

**Depends on:** Phase 3  
**Unlocks:** Phase 5 (admin embed snippet must match this widget), Phase 6 (live demo)

---

## Deliverables

1. **Vanilla JS widget** (no React runtime on host pages)
   - Single script tag embed
   - **Shadow DOM** for CSS isolation
   - Bundled for CDN (`widget.js`)

2. **UX (follow design system)**
   - Launcher: teal circle + Groundly **mark** icon
   - Panel: welcome message, **starter questions**, composer
   - **SSE streaming** + typing indicator
   - Markdown answers
   - Citation chips under answers
   - Fallback → lead form (email required; name/phone optional)
   - Privacy line: “Answers from this business’s documents”
   - Persist `visitor_id` (localStorage/cookie)
   - Mobile: bottom-sheet style panel

3. **Config from API / embed**
   - Public API key + API base URL
   - Pull or embed: `bot_name`, `primary_color`, `welcome_message`, `starter_questions`

4. **Dev harness**
   - `widget/demo.html` dummy host page with conflicting CSS (proves Shadow DOM)

---

## Design bar (non-negotiable)

- Use tokens from [design-system.md](../design-system.md)
- No purple glow, no pill spam, no generic Inter-only look
- Motion: open/close ~200ms ease-out; citation chips stagger in
- Brand mark visible on launcher (not a blank chat icon)

---

## Acceptance criteria

- [ ] Embed works on demo HTML with hostile global CSS
- [ ] Streaming tokens render live
- [ ] Citations visible for grounded answers
- [ ] Fallback shows lead form; submit hits `/chat/handoff`
- [ ] `visitor_id` stable across refresh
- [ ] Usable on a 375px-wide viewport

---

## Out of scope

- Admin UI to copy embed snippet (Phase 5)
- Live human agent takeover

---

## Next

→ [Phase 5 — Admin dashboard](phase-05-admin-dashboard.md)
