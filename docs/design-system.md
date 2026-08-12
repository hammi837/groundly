# Groundly Design System

Brand-first UI for the admin dashboard, embeddable widget, and demo site. Goal: look like a **real product**, not a generic Tailwind template.

**Logo assets:** [assets/brand/groundly-logo-lockup.png](../assets/brand/groundly-logo-lockup.png) · [assets/brand/groundly-mark-icon.png](../assets/brand/groundly-mark-icon.png)

---

## 1. Brand

| Item | Value |
|---|---|
| Name | **Groundly** |
| Tagline | AI support that only answers from your docs |
| Promise | Grounded answers · citations · graceful handoff |
| Voice | Clear, calm, confident. No hype. No fake ROI. |
| Personality | Precise, trustworthy, modern — like a sharp operations tool |

**Name usage**
- Product UI / portfolio: **Groundly**
- Fiverr gig title: outcome-first (“custom AI support chatbot…”), Groundly as product name in gallery/case study

---

## 2. Logo

### Lockup
- Mark (left) + wordmark “Groundly” (right)
- Primary file: `assets/brand/groundly-logo-lockup.png`
- Use on: dashboard header, demo landing, README, Fiverr gallery

### Mark / icon
- Standalone “G” / grounded-document monogram
- Primary file: `assets/brand/groundly-mark-icon.png`
- Use on: favicon, widget launcher bubble, mobile splash, app icon

### Logo rules
- Prefer teal mark on light surfaces; invert to white mark on dark teal/ink blocks
- Clear space: ≥ height of the “G” mark on all sides
- Do not stretch, add glow, purple gradients, or drop heavy multi-layer shadows
- Minimum size: mark ≥ 24px; lockup ≥ 120px wide

**Later (implementation):** export SVG versions of mark + wordmark for crisp scaling (trace or redraw from these PNGs).

---

## 3. Color

Direction: **deep teal + ink** on a soft cool off-white. Avoid purple SaaS clichés, cream/terracotta “AI default,” and neon glow.

```css
:root {
  /* Brand */
  --g-teal-700: #0F766E;
  --g-teal-600: #0D9488;
  --g-teal-100: #CCFBF1;
  --g-ink: #0B1220;
  --g-ink-soft: #1E293B;
  --g-slate: #64748B;
  --g-line: #E2E8F0;
  --g-surface: #F7F9F8;
  --g-surface-elevated: #FFFFFF;
  --g-danger: #B91C1C;
  --g-warning: #B45309;
  --g-success: #047857;

  /* Semantic */
  --color-bg: var(--g-surface);
  --color-bg-card: var(--g-surface-elevated);
  --color-text: var(--g-ink);
  --color-text-muted: var(--g-slate);
  --color-primary: var(--g-teal-700);
  --color-primary-hover: var(--g-teal-600);
  --color-border: var(--g-line);
  --color-accent-soft: var(--g-teal-100);
}
```

**Atmosphere (not flat white):**
- Page background: soft vertical wash `linear-gradient(180deg, #F7F9F8 0%, #EEF6F4 45%, #F7F9F8 100%)`
- Optional faint grid or paper grain at 3–5% opacity behind dashboard shell
- Hero/demo landing: full-bleed teal→ink gradient plane with brand lockup as hero signal

---

## 4. Typography

Do **not** use Inter / Roboto / Arial / system stacks as the brand face.

| Role | Font | Fallback | Use |
|---|---|---|---|
| Display / brand | **Fraunces** or **Newsreader** | Georgia, serif | Logo-adjacent headlines, landing H1 |
| UI / body | **Plus Jakarta Sans** or **Manrope** | system-ui, sans-serif | Dashboard, forms, widget chrome |
| Mono / citations | **IBM Plex Mono** or **JetBrains Mono** | ui-monospace | Chunk IDs, embed snippets, API keys |

**Scale (admin)**
- Display: 36–48px / tight tracking
- Page title: 24–28px
- Section: 18–20px
- Body: 14–16px
- Meta / captions: 12–13px

**Widget:** body 14px; citations 12px mono-ish; bubble label uses mark, not tiny text-only.

---

## 5. Layout principles

1. **One composition** on marketing/demo first viewport — not a dashboard dump
2. **Brand first** — Groundly lockup is a hero-level signal on the demo landing
3. **Hero budget** — brand, one headline, one short line, one CTA group, one dominant visual (widget mock or product shot). No stat strips in the hero
4. **No cards in hero** — cards only when they wrap a real interaction (upload zone, lead form, conversation row actions)
5. **One job per section** — one headline + short support line
6. **Motion with purpose** — at least 2–3 intentional motions:
   - Widget open/close (ease-out ~200ms)
   - Streaming cursor / typing fade
   - Citation chip enter (stagger 40ms)
7. **Admin shell** — left nav + content; quiet chrome; teal accent on active nav only

---

## 6. Component patterns

### Buttons
- Primary: teal fill, white text, 8–10px radius (not pill)
- Secondary: white / surface, ink text, 1px line border
- Danger: outline or soft red for delete only

### Forms
- Labels above fields; 12px muted help text
- Focus ring: teal, 2px, no purple glow

### Citations (widget + admin)
- Small chip under assistant message: `Source: insurance-faq.pdf`
- Soft teal-100 background, teal-700 text, mono excerpt on expand

### Leads inbox
- Table/list, not card grid — status pill `new` / `contacted` (subtle, not rainbow)

### Empty states
- One sentence + one CTA (e.g. “Upload your first FAQ PDF”)

### Widget
- Shadow DOM styles only (no host leakage)
- Launcher: circular teal with white mark icon
- Panel: 360–400px desktop; full-bleed bottom sheet on mobile
- Privacy line under composer: “Answers from this business’s documents”

---

## 7. Surfaces to design (by phase)

| Surface | Phase | Design bar |
|---|---|---|
| Logo + tokens + fonts | Phase 1 | Locked before UI code |
| Widget | Phase 4 | Portfolio-visible; polish first |
| Admin (docs, leads, settings, conversations) | Phase 5 | Clean, non-generic, brand present in header |
| Demo landing (Riverside + Groundly) | Phase 6 | Brand-first hero; widget live in second fold or sticky |

---

## 8. Accessibility

- Contrast: body text on surface ≥ WCAG AA
- Focus visible on all interactive controls
- Widget: keyboard open/close, focus trap in panel when open
- Don’t rely on color alone for lead status

---

## 9. Asset checklist

- [x] PNG lockup
- [x] PNG mark/icon
- [ ] SVG lockup (implement phase)
- [ ] SVG mark (implement phase)
- [ ] Favicon set (16/32/180)
- [ ] Fiverr gallery crops (widget, leads, citations, logo on dark teal)
