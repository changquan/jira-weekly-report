# Frontend for JIRA Weekly Report — Design

## Context

The backend (`app/`) is a FastAPI service exposing `GET /api/report`, which
returns a `WeeklyReport` JSON payload: three columns of JIRA data (Progress &
Risk, This Week, Milestones & Deadlines), plus a `window` object and
`generatedAt`/`projectKey` metadata. It also accepts `?as_of=YYYY-MM-DD` to
generate the report as of an arbitrary date. No frontend exists yet.

This spec covers building a frontend to render that report for management
consumption.

## Goals

- Render the three-column weekly report from `GET /api/report`.
- Let the user pick an arbitrary `as_of` date to view a past week's report.
- Manual refresh only (no auto-polling) — the underlying data changes on a
  weekly cadence, so this is sufficient.
- Distinctive, intentional visual design (not a generic templated look),
  applied during implementation via the frontend-design skill.

## Non-goals

- No auth/login (out of scope; assumed to run behind existing network/VPN
  access controls, same as the backend today).
- No write operations — the frontend is read-only, mirroring the backend's
  "backend only" JSON-serving design.
- No auto-refresh/polling.
- No mobile-specific layout optimization (desktop-first, dashboard use case).

## Architecture

- New top-level `frontend/` directory: a Vite + React + TypeScript app, with
  its own `package.json` independent of the Python backend.
- Vite's dev server proxies `/api/*` and `/health` to the FastAPI backend
  (`http://localhost:8000` by default, configurable), so the app fetches
  relative paths (`/api/report`) and no CORS configuration is needed in dev.
- Production build (`npm run build`) emits static assets to
  `frontend/dist/`. The README documents that these can optionally be served
  by FastAPI's `StaticFiles` or any static host; the frontend has no runtime
  dependency on how it's served.

## Components

- `App` — top-level state owner: report data, loading/error status, selected
  `as_of` date. Renders `Header` + the three `ReportColumn`s.
- `Header` — title, `as_of` date picker (empty = today/current week),
  "Refresh" button, and metadata display (`generatedAt`, `projectKey`) from
  the last successful response.
- `ReportColumn` — generic column shell (title + list of items + empty
  state), reused for all three columns.
- `IssueCard` — renders one `IssueSummary` or `RiskItem`: key, summary,
  status, assignee, due date (when present), overdue indicator (for
  `RiskItem`), and a link to the JIRA issue (`url`).
- `MilestoneCard` — renders one `MilestoneItem`: key, summary, due date,
  overdue indicator.
- `api.ts` — thin fetch wrapper: `getReport(asOf?: string): Promise<WeeklyReport>`,
  calling `/api/report` (with `?as_of=` when set) and throwing on non-2xx
  responses with the backend's error detail.
- `types.ts` — TypeScript interfaces mirroring the backend's Pydantic models
  (`IssueSummary`, `RiskItem`, `MilestoneItem`, `ReportWindow`,
  `WeeklyReport`), matching the camelCase JSON shape.

## Data flow

- On mount, `App` calls `getReport()` once for the current week.
- User can either click "Refresh" (re-fetches with the currently selected
  `as_of`) or pick a new date and confirm, which re-fetches with that date.
- State machine: `idle → loading → success | error`. Only one in-flight
  request at a time; a new request supersedes any prior in-flight one.
- Items with `overdue: true` (risks, milestones) get a distinct visual
  treatment (e.g. color/badge) in their card.

## Error handling

- Network failure or non-2xx response (including the backend's `502` when
  JIRA is unreachable or errors) surfaces an inline error banner with the
  server-provided message (or a generic fallback for network errors), plus a
  "Retry" action that re-runs the same fetch.
- Each column independently renders an explicit empty state ("No items")
  when its list is empty, rather than collapsing or leaving a blank gap.
- Malformed/unexpected response shapes are not specially handled beyond
  TypeScript's compile-time typing — the backend's own tests are the
  contract; if it fails to parse expected fields, cards render with their
  optional fields blank (this mirrors the backend `models.py`, where most
  fields are already `Optional`).

## Testing

- Vitest + React Testing Library for component tests:
  - `ReportColumn` renders items, renders empty state.
  - `IssueCard` / `MilestoneCard` render overdue vs. non-overdue styling.
  - `App` renders loading → success and loading → error transitions, using a
    mocked `api.ts`.
- `api.ts` tested with a mocked `fetch` (success and error-status cases) —
  no real network calls, consistent with how the backend fakes its JIRA
  searcher in `tests/`.

## Visual design

Direction: an **ops-desk / dispatch-board** aesthetic — the report reads like
a control-room status board, scanned by color rather than read line by line.

**Palette** (CSS custom properties):

| Token | Hex | Use |
| --- | --- | --- |
| `--ink` | `#10192B` | masthead background, primary text |
| `--paper` | `#ECEAE2` | page background |
| `--panel` | `#F4F3ED` | card surface |
| `--slate` | `#5B6472` | secondary text, "in progress" signal |
| `--signal-green` | `#4C7A5E` | resolved / progress signal |
| `--signal-amber` | `#E8A33D` | due-soon / at-risk signal |
| `--signal-red` | `#C1442E` | overdue signal |

**Type:**
- Display — Space Grotesk, tracked-out caps — masthead title + column headers
  only.
- Body — IBM Plex Sans — summaries, labels.
- Utility/data — IBM Plex Mono, tabular figures — JIRA keys, dates, the
  `generatedAt` stamp.

All three loaded via Google Fonts (or self-hosted if offline use matters
later — out of scope for now).

**Layout:** dark `ink` masthead bar (title, project key, `as_of` date picker,
Refresh button, `generatedAt` stamp in mono). Below it, three columns of
`panel` cards on the `paper` background — 6px radius, hairline border, no
heavy shadows.

**Signature element — the signal rail:** every row (issue/risk/milestone
card) has a 3px colored bar on its left edge, using the signal colors above
to encode status: green = resolved, slate = in progress, amber = due soon,
red = overdue. It's the only saturated color in the UI; everything else
stays ink/paper/slate, so the rail is what a manager scans first.

**Motion:** minimal. On a successful refresh, the `generatedAt` stamp does a
brief split-flap-style flip to its new value; this is the only animation in
the design and must be skipped when `prefers-reduced-motion` is set — the
timestamp still updates, just without the flip transition. No hover
scale/shadow effects; hover only brightens a card's signal rail slightly.

**Copy voice:** empty states are specific and actionable per column (e.g.
"No milestones due" rather than "No data"). The error banner speaks in the
interface's voice and names what happened (e.g. "Couldn't load this
week's report — JIRA didn't respond.") with a "Retry" action, never an
apology.
