# PWA (Stage 8)

Vite + React (TypeScript). Placeholder until Stage 8; we do Home Assistant first (Stage 3) for phone, desktop, and Watch.

**Stage:** PWA development is part of **Stage 8** (optional native apps and desktop). Phone/desktop/Watch go through HA first; this PWA is the optional standalone app or desktop experience if you’re not using the HA dashboard. See [docs/PROJECT_PLAN.md](../docs/PROJECT_PLAN.md) for the full staged plan.

## Run

From this directory:

```bash
npm install
npm run dev
```

App at http://localhost:5173. No need to run from repo root. The dev server proxies `/api` to the backend at http://localhost:8000 when you add API calls later.
