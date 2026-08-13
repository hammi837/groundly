# Groundly embeddable chat widget (vanilla TS → IIFE bundle).

## Dev (with hostile CSS harness)

```bash
cd widget
npm install
npm run dev
```

Opens `demo.html`. Paste tenant API key when prompted (from `scripts/seed_riverside.py`), or use `?apiKey=...`.

API must be running at `http://localhost:8000` (Phase 1–3).

## Build for CDN / static embed

```bash
npm run build
```

Outputs `dist/widget.js`. Embed:

```html
<script
  src="https://your-cdn/widget.js"
  data-api-base="https://api.yourdomain.com"
  data-api-key="TENANT_PUBLIC_KEY"
  async
></script>
```

Or mount manually:

```html
<script src="./dist/widget.js"></script>
<script>
  GroundlyWidget.mountGroundlyWidget({
    apiBaseUrl: "http://localhost:8000",
    apiKey: "..."
  });
</script>
```

## Features

- Shadow DOM (host CSS cannot break the chat)
- SSE streaming + typing indicator
- Markdown answers + citation chips
- Starter questions from `/widget/config`
- Fallback lead form → `/chat/handoff`
- Persistent `visitor_id` in localStorage
- Mobile bottom-sheet layout
