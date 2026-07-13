# JIRA Weekly Report — Frontend

A React + Vite + TypeScript SPA that renders the three-column weekly report
served by the backend's `GET /api/report`.

## Setup

```bash
cd frontend
npm install
```

## Run

Start the backend first (`uvicorn app.main:app --reload` from the repo
root), then in another terminal:

```bash
cd frontend
npm run dev
```

Vite serves the app on `http://localhost:5173` and proxies `/api` and
`/health` to `http://localhost:8000`, so no CORS setup is needed in dev.

## Test

```bash
npm run test
```

## Build

```bash
npm run build
```

Emits static assets to `frontend/dist/`, which can be served by any static
host (or by FastAPI's `StaticFiles`, if desired — not wired up by default).
