# Demo landing (Phase 6)

Brand-first public page for the Riverside Dental Groundly demo.

## Run locally

1. Seed (prints `api_key`):
   ```bash
   cd backend
   .venv\Scripts\python ..\scripts\seed_riverside.py
   ```
2. Build widget into this folder:
   ```bash
   cd widget
   npm run build
   copy dist\widget.js ..\demo\widget.js
   ```
3. Serve this folder (origin must be in tenant `allowed_origins`):
   ```bash
   npx --yes serve demo -p 4173
   ```
4. Open `http://127.0.0.1:4173/?apiKey=YOUR_KEY`

API must be running on `http://127.0.0.1:8000` (override with `?apiBase=`).
