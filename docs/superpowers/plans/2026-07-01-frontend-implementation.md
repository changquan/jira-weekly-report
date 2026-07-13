# JIRA Weekly Report Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a React + Vite + TypeScript SPA in a new `frontend/` directory that renders the three-column weekly report from the existing FastAPI backend's `GET /api/report`, styled with the approved ops-desk visual design.

**Architecture:** Vite dev server proxies `/api` and `/health` to the FastAPI backend on `localhost:8000`. A thin typed `api.ts` fetches the report; `App` owns load/error/success state and an `as_of` date; presentational components (`Header`, `ReportColumn`, `IssueCard`, `MilestoneCard`) render it. Plain CSS Modules implement the design tokens (palette, type, signal rail).

**Tech Stack:** React 18, Vite 5, TypeScript 5, Vitest + React Testing Library, plain CSS / CSS Modules. Independent `package.json` from the Python backend.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-01-frontend-design.md` — read it before starting.
- Frontend has its own toolchain (`frontend/package.json`), independent of the Python backend's `requirements*.txt`/pytest setup.
- No auth/login, no auto-refresh/polling, no mobile-specific layout — desktop-first, manual refresh only.
- Palette (exact hex, lowercase in CSS): `--ink #10192b`, `--paper #eceae2`, `--panel #f4f3ed`, `--slate #5b6472`, `--signal-green #4c7a5e`, `--signal-amber #e8a33d`, `--signal-red #c1442e`.
- Type: display = Space Grotesk (masthead/column headers only), body = IBM Plex Sans, utility/data = IBM Plex Mono (keys, dates, timestamp), loaded via Google Fonts in `index.html`.
- The signal rail (3px colored left bar) is the only saturated color in the UI; everything else stays ink/paper/slate.
- The only animation is the `generatedAt` timestamp flip on refresh, and it must be disabled under `prefers-reduced-motion: reduce`.
- Column 1 ("Progress & Risk") is a single merged list: `report.progress` items followed by `report.risks` items, each rendered via `IssueCard` (which tells them apart by the presence of an `overdue` field).

---

## Task 1: Project scaffold, TypeScript config, Vite dev proxy

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/test/setup.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/.gitignore`

**Interfaces:**
- Produces: an `App` named export from `frontend/src/App.tsx` (placeholder in this task; fully implemented in Task 9), rendered by `main.tsx` into `#root`.
- Produces: `npm run build`, `npm run dev`, `npm run test` scripts usable by every later task.

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "jira-weekly-report-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.8",
    "@testing-library/react": "^16.0.1",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.5",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "jsdom": "^25.0.0",
    "typescript": "^5.5.4",
    "vite": "^5.4.2",
    "vitest": "^2.0.5"
  }
}
```

- [ ] **Step 2: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "types": ["vite/client"]
  },
  "include": ["src", "test", "vite.config.ts"]
}
```

- [ ] **Step 3: Create `frontend/test/setup.ts`**

```ts
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 4: Create `frontend/vite.config.ts`**

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
  },
})
```

- [ ] **Step 5: Create `frontend/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Weekly Status</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create `frontend/src/App.tsx` (placeholder, replaced in Task 9)**

```tsx
export function App() {
  return <div>Weekly Status</div>
}
```

- [ ] **Step 7: Create `frontend/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 8: Create `frontend/.gitignore`**

```
node_modules/
dist/
```

- [ ] **Step 9: Install dependencies**

Run: `cd frontend && npm install`
Expected: completes with exit code 0 (a handful of deprecation warnings are fine; no `npm error`).

- [ ] **Step 10: Verify the build**

Run: `cd frontend && npm run build`
Expected: `tsc --noEmit` reports no errors, then Vite prints `✓ built in ...` and creates `frontend/dist/`.

- [ ] **Step 11: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/tsconfig.json frontend/vite.config.ts frontend/index.html frontend/test/setup.ts frontend/src/main.tsx frontend/src/App.tsx frontend/.gitignore
git commit -m "Scaffold frontend Vite+React+TS app with dev proxy"
```

---

## Task 2: Design tokens (palette, type, global styles)

**Files:**
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/global.css`
- Modify: `frontend/index.html` (add Google Fonts links)
- Modify: `frontend/src/main.tsx` (import the two stylesheets)

**Interfaces:**
- Produces: CSS custom properties `--ink`, `--paper`, `--panel`, `--slate`, `--signal-green`, `--signal-amber`, `--signal-red`, `--font-display`, `--font-body`, `--font-mono`, available globally to every component's CSS Module from Task 4 onward.

- [ ] **Step 1: Create `frontend/src/styles/tokens.css`**

```css
:root {
  --ink: #10192b;
  --paper: #eceae2;
  --panel: #f4f3ed;
  --slate: #5b6472;
  --signal-green: #4c7a5e;
  --signal-amber: #e8a33d;
  --signal-red: #c1442e;

  --font-display: 'Space Grotesk', sans-serif;
  --font-body: 'IBM Plex Sans', sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
}
```

- [ ] **Step 2: Create `frontend/src/styles/global.css`**

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--font-body);
}

a {
  color: inherit;
}
```

- [ ] **Step 3: Add font links to `frontend/index.html`**

In the `<head>`, after `<title>Weekly Status</title>`, add:

```html
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;700&display=swap"
      rel="stylesheet"
    />
```

- [ ] **Step 4: Import the stylesheets in `frontend/src/main.tsx`**

Add these two imports above `import { App } from './App'`:

```tsx
import './styles/tokens.css'
import './styles/global.css'
```

- [ ] **Step 5: Verify the build**

Run: `cd frontend && npm run build`
Expected: succeeds with no errors (same as Task 1's check).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/styles frontend/index.html frontend/src/main.tsx
git commit -m "Add ops-desk design tokens and global styles"
```

---

## Task 3: Types and API client

**Files:**
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`
- Test: `frontend/src/api.test.ts`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure new module).
- Produces: types `IssueSummary`, `RiskItem`, `MilestoneItem`, `ReportWindow`, `WeeklyReport` from `./types`; `getReport(asOf?: string): Promise<WeeklyReport>` and class `ApiError extends Error` from `./api`. Every later component task imports from these two files.

- [ ] **Step 1: Create `frontend/src/types.ts`**

```ts
export interface IssueSummary {
  key: string
  summary: string
  status: string
  statusCategory: string
  issueType: string
  assignee: string | null
  priority: string | null
  dueDate: string | null
  resolutionDate: string | null
  updated: string | null
  url: string
}

export interface RiskItem extends IssueSummary {
  daysUntilDue: number | null
  overdue: boolean
}

export interface MilestoneItem {
  key: string
  summary: string
  status: string
  statusCategory: string
  dueDate: string | null
  overdue: boolean
  url: string
}

export interface ReportWindow {
  today: string
  thisWeekStart: string
  thisWeekEnd: string
  lastWeekStart: string
  lastWeekEnd: string
}

export interface WeeklyReport {
  generatedAt: string
  projectKey: string
  window: ReportWindow
  progress: IssueSummary[]
  risks: RiskItem[]
  thisWeek: IssueSummary[]
  milestones: MilestoneItem[]
}
```

- [ ] **Step 2: Write the failing test for `api.ts`**

Create `frontend/src/api.test.ts`:

```ts
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, getReport } from './api'

describe('getReport', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fetches the report from /api/report', async () => {
    const payload = {
      generatedAt: '2026-07-01T09:00:00+00:00',
      projectKey: 'ABC',
      window: {
        today: '2026-07-01',
        thisWeekStart: '2026-06-29',
        thisWeekEnd: '2026-07-05',
        lastWeekStart: '2026-06-22',
        lastWeekEnd: '2026-06-28',
      },
      progress: [],
      risks: [],
      thisWeek: [],
      milestones: [],
    }
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => payload,
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await getReport()

    expect(fetchMock).toHaveBeenCalledWith('/api/report')
    expect(result).toEqual(payload)
  })

  it('appends as_of when provided', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) })
    vi.stubGlobal('fetch', fetchMock)

    await getReport('2026-06-24')

    expect(fetchMock).toHaveBeenCalledWith('/api/report?as_of=2026-06-24')
  })

  it('throws ApiError with the server detail on a non-2xx response', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => ({ detail: 'Could not reach JIRA: timeout' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(getReport()).rejects.toBeInstanceOf(ApiError)
    await expect(getReport()).rejects.toThrow('Could not reach JIRA: timeout')
  })

  it('falls back to a generic message when the error body is not JSON', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('not json')
      },
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(getReport()).rejects.toThrow('Request failed with status 500')
  })
})
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd frontend && npm run test -- api.test.ts`
Expected: FAIL — `frontend/src/api.ts` does not exist (module not found).

- [ ] **Step 4: Create `frontend/src/api.ts`**

```ts
import type { WeeklyReport } from './types'

export class ApiError extends Error {}

export async function getReport(asOf?: string): Promise<WeeklyReport> {
  const url = asOf ? `/api/report?as_of=${asOf}` : '/api/report'
  const response = await fetch(url)

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        detail = body.detail
      }
    } catch {
      // response body wasn't JSON — keep the generic detail
    }
    throw new ApiError(detail)
  }

  return response.json()
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd frontend && npm run test -- api.test.ts`
Expected: PASS, 4 tests.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts frontend/src/api.test.ts
git commit -m "Add report types and API client"
```

---

## Task 4: Signal status util

**Files:**
- Create: `frontend/src/signalStatus.ts`
- Test: `frontend/src/signalStatus.test.ts`

**Interfaces:**
- Consumes: `IssueSummary`, `RiskItem`, `MilestoneItem` from `./types` (Task 3).
- Produces: `type SignalColor = 'green' | 'amber' | 'red' | 'slate'`, and functions `issueSignal(issue: IssueSummary): SignalColor`, `riskSignal(risk: RiskItem): SignalColor`, `milestoneSignal(milestone: MilestoneItem): SignalColor`. Used by `IssueCard` and `MilestoneCard` (Tasks 6–7).

- [ ] **Step 1: Write the failing test**

Create `frontend/src/signalStatus.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { issueSignal, milestoneSignal, riskSignal } from './signalStatus'
import type { IssueSummary, MilestoneItem, RiskItem } from './types'

const baseIssue: IssueSummary = {
  key: 'ABC-1',
  summary: 'Example',
  status: 'In Progress',
  statusCategory: 'In Progress',
  issueType: 'Task',
  assignee: null,
  priority: null,
  dueDate: null,
  resolutionDate: null,
  updated: null,
  url: 'https://example.atlassian.net/browse/ABC-1',
}

describe('issueSignal', () => {
  it('returns green for a Done issue', () => {
    expect(issueSignal({ ...baseIssue, statusCategory: 'Done' })).toBe('green')
  })

  it('returns slate for a non-Done issue', () => {
    expect(issueSignal(baseIssue)).toBe('slate')
  })
})

describe('riskSignal', () => {
  const baseRisk: RiskItem = { ...baseIssue, daysUntilDue: 5, overdue: false }

  it('returns red for an overdue risk', () => {
    expect(riskSignal({ ...baseRisk, overdue: true })).toBe('red')
  })

  it('returns amber for a non-overdue risk', () => {
    expect(riskSignal(baseRisk)).toBe('amber')
  })
})

describe('milestoneSignal', () => {
  const baseMilestone: MilestoneItem = {
    key: 'ABC-1',
    summary: 'Example',
    status: 'In Progress',
    statusCategory: 'In Progress',
    dueDate: '2026-07-10',
    overdue: false,
    url: 'https://example.atlassian.net/browse/ABC-1',
  }

  it('returns red for an overdue milestone', () => {
    expect(milestoneSignal({ ...baseMilestone, overdue: true })).toBe('red')
  })

  it('returns green for a Done milestone', () => {
    expect(milestoneSignal({ ...baseMilestone, statusCategory: 'Done' })).toBe('green')
  })

  it('returns slate for an upcoming, non-Done, non-overdue milestone', () => {
    expect(milestoneSignal(baseMilestone)).toBe('slate')
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test -- signalStatus.test.ts`
Expected: FAIL — `frontend/src/signalStatus.ts` does not exist.

- [ ] **Step 3: Create `frontend/src/signalStatus.ts`**

```ts
import type { IssueSummary, MilestoneItem, RiskItem } from './types'

export type SignalColor = 'green' | 'amber' | 'red' | 'slate'

export function issueSignal(issue: IssueSummary): SignalColor {
  return issue.statusCategory === 'Done' ? 'green' : 'slate'
}

export function riskSignal(risk: RiskItem): SignalColor {
  return risk.overdue ? 'red' : 'amber'
}

export function milestoneSignal(milestone: MilestoneItem): SignalColor {
  if (milestone.overdue) return 'red'
  return milestone.statusCategory === 'Done' ? 'green' : 'slate'
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npm run test -- signalStatus.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/signalStatus.ts frontend/src/signalStatus.test.ts
git commit -m "Add signal status util for the rail color coding"
```

---

## Task 5: ReportColumn component

**Files:**
- Create: `frontend/src/components/ReportColumn.tsx`
- Create: `frontend/src/components/ReportColumn.module.css`
- Test: `frontend/src/components/ReportColumn.test.tsx`

**Interfaces:**
- Consumes: nothing from earlier component tasks (generic, only needs items with a `key: string`).
- Produces: `ReportColumn<T extends { key: string }>` component with props `{ title: string; items: T[]; emptyMessage: string; renderItem: (item: T) => React.ReactNode }`. Used by `App` (Task 9).

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/ReportColumn.test.tsx`:

```tsx
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ReportColumn } from './ReportColumn'

interface Item {
  key: string
  label: string
}

describe('ReportColumn', () => {
  it('renders the title and one entry per item', () => {
    const items: Item[] = [
      { key: 'A-1', label: 'First' },
      { key: 'A-2', label: 'Second' },
    ]

    render(
      <ReportColumn
        title="This Week"
        items={items}
        emptyMessage="Nothing in progress this week"
        renderItem={(item) => <span>{item.label}</span>}
      />,
    )

    expect(screen.getByText('This Week')).toBeInTheDocument()
    expect(screen.getByText('First')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
  })

  it('renders the empty message when there are no items', () => {
    render(
      <ReportColumn
        title="This Week"
        items={[]}
        emptyMessage="Nothing in progress this week"
        renderItem={(item: Item) => <span>{item.label}</span>}
      />,
    )

    expect(screen.getByText('Nothing in progress this week')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test -- ReportColumn.test.tsx`
Expected: FAIL — `frontend/src/components/ReportColumn.tsx` does not exist.

- [ ] **Step 3: Create `frontend/src/components/ReportColumn.module.css`**

```css
.column {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.title {
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ink);
  margin: 0;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.empty {
  font-family: var(--font-body);
  font-size: 0.85rem;
  color: var(--slate);
  border: 1px dashed rgba(16, 25, 43, 0.15);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin: 0;
}
```

- [ ] **Step 4: Create `frontend/src/components/ReportColumn.tsx`**

```tsx
import type { ReactNode } from 'react'
import styles from './ReportColumn.module.css'

interface ReportColumnProps<T extends { key: string }> {
  title: string
  items: T[]
  emptyMessage: string
  renderItem: (item: T) => ReactNode
}

export function ReportColumn<T extends { key: string }>({
  title,
  items,
  emptyMessage,
  renderItem,
}: ReportColumnProps<T>) {
  return (
    <section className={styles.column}>
      <h2 className={styles.title}>{title}</h2>
      {items.length === 0 ? (
        <p className={styles.empty}>{emptyMessage}</p>
      ) : (
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item.key}>{renderItem(item)}</li>
          ))}
        </ul>
      )}
    </section>
  )
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd frontend && npm run test -- ReportColumn.test.tsx`
Expected: PASS, 2 tests.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ReportColumn.tsx frontend/src/components/ReportColumn.module.css frontend/src/components/ReportColumn.test.tsx
git commit -m "Add generic ReportColumn component"
```

---

## Task 6: Shared card styles + IssueCard component

**Files:**
- Create: `frontend/src/components/Card.module.css`
- Create: `frontend/src/components/IssueCard.tsx`
- Test: `frontend/src/components/IssueCard.test.tsx`

**Interfaces:**
- Consumes: `IssueSummary`, `RiskItem` from `../types` (Task 3); `issueSignal`, `riskSignal` from `../signalStatus` (Task 4).
- Produces: `IssueCard` component with props `{ item: IssueSummary | RiskItem }`. Used by `App` (Task 9) for both the "Progress & Risk" and "This Week" columns.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/IssueCard.test.tsx`:

```tsx
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { IssueCard } from './IssueCard'
import type { IssueSummary, RiskItem } from '../types'

const baseIssue: IssueSummary = {
  key: 'ABC-10',
  summary: 'Migrate billing service',
  status: 'Done',
  statusCategory: 'Done',
  issueType: 'Task',
  assignee: 'Dana',
  priority: null,
  dueDate: null,
  resolutionDate: '2026-06-28T00:00:00+00:00',
  updated: null,
  url: 'https://example.atlassian.net/browse/ABC-10',
}

describe('IssueCard', () => {
  it('renders a plain issue with its status and a green rail', () => {
    render(<IssueCard item={baseIssue} />)

    expect(screen.getByText('ABC-10')).toBeInTheDocument()
    expect(screen.getByText('Migrate billing service')).toBeInTheDocument()
    expect(screen.getByText('Done')).toBeInTheDocument()
    expect(screen.getByText('Dana')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'green')
  })

  it('renders an overdue risk with a red rail and an Overdue label', () => {
    const risk: RiskItem = {
      ...baseIssue,
      key: 'ABC-1',
      statusCategory: 'In Progress',
      daysUntilDue: -6,
      overdue: true,
    }

    render(<IssueCard item={risk} />)

    expect(screen.getByText('Overdue')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'red')
  })

  it('renders a non-overdue risk with an amber rail and an At risk label', () => {
    const risk: RiskItem = {
      ...baseIssue,
      key: 'ABC-2',
      statusCategory: 'In Progress',
      daysUntilDue: 5,
      overdue: false,
    }

    render(<IssueCard item={risk} />)

    expect(screen.getByText('At risk')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'amber')
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test -- IssueCard.test.tsx`
Expected: FAIL — `frontend/src/components/IssueCard.tsx` does not exist.

- [ ] **Step 3: Create `frontend/src/components/Card.module.css`**

```css
.card {
  display: flex;
  gap: 0.75rem;
  background: var(--panel);
  border: 1px solid rgba(16, 25, 43, 0.08);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: var(--ink);
  transition: border-color 0.15s ease;
}

.card:hover {
  border-color: rgba(16, 25, 43, 0.2);
}

.rail {
  flex: 0 0 3px;
  border-radius: 2px;
  background: var(--slate);
}

.rail[data-signal='green'] {
  background: var(--signal-green);
}

.rail[data-signal='amber'] {
  background: var(--signal-amber);
}

.rail[data-signal='red'] {
  background: var(--signal-red);
}

.body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.meta {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--slate);
}

.summary {
  margin: 0;
  font-family: var(--font-body);
  font-size: 0.9rem;
}

.footer {
  margin: 0;
  display: flex;
  gap: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--slate);
}
```

- [ ] **Step 4: Create `frontend/src/components/IssueCard.tsx`**

```tsx
import { issueSignal, riskSignal } from '../signalStatus'
import type { IssueSummary, RiskItem } from '../types'
import styles from './Card.module.css'

interface IssueCardProps {
  item: IssueSummary | RiskItem
}

function isRisk(item: IssueSummary | RiskItem): item is RiskItem {
  return 'overdue' in item
}

function formatDueDate(dueDate: string | null): string | null {
  if (!dueDate) return null
  return new Intl.DateTimeFormat('en-US', { day: '2-digit', month: 'short' }).format(new Date(dueDate))
}

export function IssueCard({ item }: IssueCardProps) {
  const risk = isRisk(item)
  const signal = risk ? riskSignal(item) : issueSignal(item)
  const statusLabel = risk ? (item.overdue ? 'Overdue' : 'At risk') : item.status
  const dueDate = formatDueDate(item.dueDate)

  return (
    <a className={styles.card} data-signal={signal} href={item.url} target="_blank" rel="noreferrer">
      <span className={styles.rail} data-signal={signal} aria-hidden="true" />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span>{item.key}</span>
          <span>{statusLabel}</span>
        </div>
        <p className={styles.summary}>{item.summary}</p>
        <p className={styles.footer}>
          {item.assignee && <span>{item.assignee}</span>}
          {dueDate && <span>due {dueDate}</span>}
        </p>
      </div>
    </a>
  )
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd frontend && npm run test -- IssueCard.test.tsx`
Expected: PASS, 3 tests.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/Card.module.css frontend/src/components/IssueCard.tsx frontend/src/components/IssueCard.test.tsx
git commit -m "Add IssueCard component with signal rail"
```

---

## Task 7: MilestoneCard component

**Files:**
- Create: `frontend/src/components/MilestoneCard.tsx`
- Test: `frontend/src/components/MilestoneCard.test.tsx`

**Interfaces:**
- Consumes: `MilestoneItem` from `../types` (Task 3); `milestoneSignal` from `../signalStatus` (Task 4); shared classes from `./Card.module.css` (Task 6).
- Produces: `MilestoneCard` component with props `{ item: MilestoneItem }`. Used by `App` (Task 9) for the "Milestones & Deadlines" column.

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/MilestoneCard.test.tsx`:

```tsx
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MilestoneCard } from './MilestoneCard'
import type { MilestoneItem } from '../types'

const baseMilestone: MilestoneItem = {
  key: 'ABC-1',
  summary: 'Q3 platform launch',
  status: 'In Progress',
  statusCategory: 'In Progress',
  dueDate: '2026-06-25',
  overdue: false,
  url: 'https://example.atlassian.net/browse/ABC-1',
}

describe('MilestoneCard', () => {
  it('renders an upcoming milestone with a slate rail', () => {
    render(<MilestoneCard item={baseMilestone} />)

    expect(screen.getByText('ABC-1')).toBeInTheDocument()
    expect(screen.getByText('Q3 platform launch')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'slate')
  })

  it('renders an overdue milestone with a red rail and an Overdue label', () => {
    render(<MilestoneCard item={{ ...baseMilestone, overdue: true }} />)

    expect(screen.getByText('Overdue')).toBeInTheDocument()
    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'red')
  })

  it('renders a Done milestone with a green rail', () => {
    render(<MilestoneCard item={{ ...baseMilestone, statusCategory: 'Done', status: 'Done' }} />)

    expect(screen.getByRole('link')).toHaveAttribute('data-signal', 'green')
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test -- MilestoneCard.test.tsx`
Expected: FAIL — `frontend/src/components/MilestoneCard.tsx` does not exist.

- [ ] **Step 3: Create `frontend/src/components/MilestoneCard.tsx`**

```tsx
import { milestoneSignal } from '../signalStatus'
import type { MilestoneItem } from '../types'
import styles from './Card.module.css'

interface MilestoneCardProps {
  item: MilestoneItem
}

function formatDueDate(dueDate: string | null): string | null {
  if (!dueDate) return null
  return new Intl.DateTimeFormat('en-US', { day: '2-digit', month: 'short' }).format(new Date(dueDate))
}

export function MilestoneCard({ item }: MilestoneCardProps) {
  const signal = milestoneSignal(item)
  const dueDate = formatDueDate(item.dueDate)
  const statusLabel = item.overdue ? 'Overdue' : item.status

  return (
    <a className={styles.card} data-signal={signal} href={item.url} target="_blank" rel="noreferrer">
      <span className={styles.rail} data-signal={signal} aria-hidden="true" />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span>{item.key}</span>
          <span>{statusLabel}</span>
        </div>
        <p className={styles.summary}>{item.summary}</p>
        {dueDate && <p className={styles.footer}>due {dueDate}</p>}
      </div>
    </a>
  )
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npm run test -- MilestoneCard.test.tsx`
Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/MilestoneCard.tsx frontend/src/components/MilestoneCard.test.tsx
git commit -m "Add MilestoneCard component"
```

---

## Task 8: Header component

**Files:**
- Create: `frontend/src/components/Header.tsx`
- Create: `frontend/src/components/Header.module.css`
- Test: `frontend/src/components/Header.test.tsx`

**Interfaces:**
- Consumes: nothing from earlier component tasks (plain props).
- Produces: `Header` component with props `{ projectKey: string | null; generatedAt: string | null; asOf: string; onAsOfChange: (value: string) => void; onRefresh: () => void; isLoading: boolean }`. Used by `App` (Task 9).

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/Header.test.tsx`:

```tsx
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Header } from './Header'

describe('Header', () => {
  it('renders the project key and generated timestamp', () => {
    render(
      <Header
        projectKey="ABC"
        generatedAt="2026-07-01T09:00:00+00:00"
        asOf=""
        onAsOfChange={() => {}}
        onRefresh={() => {}}
        isLoading={false}
      />,
    )

    expect(screen.getByText('Project ABC')).toBeInTheDocument()
    expect(screen.getByText('Refresh')).toBeInTheDocument()
  })

  it('calls onRefresh when the refresh button is clicked', async () => {
    const onRefresh = vi.fn()
    render(
      <Header
        projectKey={null}
        generatedAt={null}
        asOf=""
        onAsOfChange={() => {}}
        onRefresh={onRefresh}
        isLoading={false}
      />,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Refresh' }))

    expect(onRefresh).toHaveBeenCalledTimes(1)
  })

  it('disables the button and shows a loading label while loading', () => {
    render(
      <Header
        projectKey={null}
        generatedAt={null}
        asOf=""
        onAsOfChange={() => {}}
        onRefresh={() => {}}
        isLoading={true}
      />,
    )

    const button = screen.getByRole('button', { name: 'Refreshing…' })
    expect(button).toBeDisabled()
  })

  it('calls onAsOfChange when the date input changes', async () => {
    const onAsOfChange = vi.fn()
    render(
      <Header
        projectKey={null}
        generatedAt={null}
        asOf=""
        onAsOfChange={onAsOfChange}
        onRefresh={() => {}}
        isLoading={false}
      />,
    )

    const input = screen.getByLabelText('As of')
    await userEvent.type(input, '2026-06-24')

    expect(onAsOfChange).toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test -- Header.test.tsx`
Expected: FAIL — `frontend/src/components/Header.tsx` does not exist.

- [ ] **Step 3: Create `frontend/src/components/Header.module.css`**

```css
.masthead {
  background: var(--ink);
  color: var(--paper);
  padding: 1rem 2rem;
}

.row {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 1.1rem;
  margin: 0;
}

.projectBadge {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  border: 1px solid rgba(236, 234, 226, 0.4);
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
}

.asOfLabel {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.asOfInput {
  font-family: var(--font-mono);
  background: transparent;
  border: 1px solid rgba(236, 234, 226, 0.4);
  border-radius: 4px;
  color: var(--paper);
  padding: 0.25rem 0.5rem;
}

.refreshButton {
  font-family: var(--font-body);
  font-weight: 600;
  background: var(--signal-amber);
  color: var(--ink);
  border: none;
  border-radius: 4px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
}

.refreshButton:disabled {
  opacity: 0.6;
  cursor: default;
}

.stamp {
  margin: 0.5rem 0 0;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: rgba(236, 234, 226, 0.7);
}

.stampFlip {
  animation: flip 0.4s ease;
}

@keyframes flip {
  0% {
    opacity: 0.2;
    transform: translateY(-4px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .stampFlip {
    animation: none;
  }
}
```

- [ ] **Step 4: Create `frontend/src/components/Header.tsx`**

```tsx
import { useEffect, useRef, useState } from 'react'
import styles from './Header.module.css'

interface HeaderProps {
  projectKey: string | null
  generatedAt: string | null
  asOf: string
  onAsOfChange: (value: string) => void
  onRefresh: () => void
  isLoading: boolean
}

function formatStamp(generatedAt: string | null): string {
  if (!generatedAt) return '—'
  return new Intl.DateTimeFormat('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(generatedAt))
}

export function Header({ projectKey, generatedAt, asOf, onAsOfChange, onRefresh, isLoading }: HeaderProps) {
  const [flip, setFlip] = useState(false)
  const previousStamp = useRef<string | null>(null)

  useEffect(() => {
    const previous = previousStamp.current
    previousStamp.current = generatedAt
    if (generatedAt && previous && previous !== generatedAt) {
      setFlip(true)
      const timeout = setTimeout(() => setFlip(false), 400)
      return () => clearTimeout(timeout)
    }
  }, [generatedAt])

  return (
    <header className={styles.masthead}>
      <div className={styles.row}>
        <h1 className={styles.title}>Weekly Status</h1>
        {projectKey && <span className={styles.projectBadge}>Project {projectKey}</span>}
        <label className={styles.asOfLabel}>
          As of
          <input
            type="date"
            className={styles.asOfInput}
            value={asOf}
            onChange={(event) => onAsOfChange(event.target.value)}
          />
        </label>
        <button type="button" className={styles.refreshButton} onClick={onRefresh} disabled={isLoading}>
          {isLoading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>
      <p className={flip ? `${styles.stamp} ${styles.stampFlip}` : styles.stamp}>
        Generated {formatStamp(generatedAt)}
      </p>
    </header>
  )
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd frontend && npm run test -- Header.test.tsx`
Expected: PASS, 4 tests.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/Header.tsx frontend/src/components/Header.module.css frontend/src/components/Header.test.tsx
git commit -m "Add Header component with as_of picker and refresh"
```

---

## Task 9: App component (wiring, error/empty/loading states)

**Files:**
- Modify: `frontend/src/App.tsx` (replace the Task 1 placeholder)
- Create: `frontend/src/App.module.css`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: `getReport`, `ApiError` from `./api` (Task 3); `Header` (Task 8); `ReportColumn` (Task 5); `IssueCard` (Task 6); `MilestoneCard` (Task 7); `WeeklyReport`, `IssueSummary`, `RiskItem` from `./types` (Task 3).
- Produces: `App` named export — the app's root component, unchanged public shape from Task 1 (still rendered by `main.tsx`).

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/App.test.tsx`:

```tsx
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { App } from './App'
import { ApiError, getReport } from './api'

vi.mock('./api', () => ({
  getReport: vi.fn(),
  ApiError: class ApiError extends Error {},
}))

const mockedGetReport = vi.mocked(getReport)

const sampleReport = {
  generatedAt: '2026-07-01T09:00:00+00:00',
  projectKey: 'ABC',
  window: {
    today: '2026-07-01',
    thisWeekStart: '2026-06-29',
    thisWeekEnd: '2026-07-05',
    lastWeekStart: '2026-06-22',
    lastWeekEnd: '2026-06-28',
  },
  progress: [
    {
      key: 'ABC-10',
      summary: 'Migrate billing service',
      status: 'Done',
      statusCategory: 'Done',
      issueType: 'Task',
      assignee: 'Dana',
      priority: null,
      dueDate: null,
      resolutionDate: '2026-06-28T00:00:00+00:00',
      updated: null,
      url: 'https://example.atlassian.net/browse/ABC-10',
    },
  ],
  risks: [],
  thisWeek: [],
  milestones: [],
}

describe('App', () => {
  beforeEach(() => {
    mockedGetReport.mockReset()
  })

  it('shows the report once loading succeeds', async () => {
    mockedGetReport.mockResolvedValue(sampleReport)

    render(<App />)

    expect(await screen.findByText('Migrate billing service')).toBeInTheDocument()
    expect(screen.getByText('Project ABC')).toBeInTheDocument()
  })

  it('shows an error banner with the server detail when loading fails, and recovers on retry', async () => {
    mockedGetReport.mockRejectedValueOnce(new ApiError("Could not reach JIRA: timeout"))
    mockedGetReport.mockResolvedValueOnce(sampleReport)

    render(<App />)

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach JIRA: timeout')

    await userEvent.click(screen.getByRole('button', { name: 'Retry' }))

    expect(await screen.findByText('Migrate billing service')).toBeInTheDocument()
  })

  it('shows a generic message when the failure is not an ApiError', async () => {
    mockedGetReport.mockRejectedValueOnce(new TypeError('Failed to fetch'))
    mockedGetReport.mockResolvedValueOnce(sampleReport)

    render(<App />)

    expect(await screen.findByRole('alert')).toHaveTextContent('Could not reach the server')
  })

  it('shows empty-state messages for columns with no items', async () => {
    mockedGetReport.mockResolvedValue(sampleReport)

    render(<App />)

    await screen.findByText('Migrate billing service')

    expect(screen.getByText('Nothing in progress this week')).toBeInTheDocument()
    expect(screen.getByText('No milestones due')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd frontend && npm run test -- App.test.tsx`
Expected: FAIL — the current placeholder `App` doesn't fetch, render columns, or show an error banner.

- [ ] **Step 3: Create `frontend/src/App.module.css`**

```css
.app {
  min-height: 100vh;
  background: var(--paper);
}

.columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  padding: 1.5rem 2rem;
}

.errorBanner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin: 1rem 2rem 0;
  padding: 0.75rem 1rem;
  background: rgba(193, 68, 46, 0.1);
  border: 1px solid var(--signal-red);
  border-radius: 6px;
  color: var(--ink);
  font-family: var(--font-body);
}

.errorBanner button {
  background: var(--signal-red);
  color: var(--paper);
  border: none;
  border-radius: 4px;
  padding: 0.4rem 0.9rem;
  font-family: var(--font-body);
  cursor: pointer;
}

.loading {
  padding: 1.5rem 2rem;
  font-family: var(--font-body);
  color: var(--slate);
}
```

- [ ] **Step 4: Replace `frontend/src/App.tsx`**

```tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import { Header } from './components/Header'
import { ReportColumn } from './components/ReportColumn'
import { IssueCard } from './components/IssueCard'
import { MilestoneCard } from './components/MilestoneCard'
import { ApiError, getReport } from './api'
import type { IssueSummary, RiskItem, WeeklyReport } from './types'
import styles from './App.module.css'

type Status = 'loading' | 'success' | 'error'

export function App() {
  const [asOf, setAsOf] = useState('')
  const [report, setReport] = useState<WeeklyReport | null>(null)
  const [status, setStatus] = useState<Status>('loading')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const latestRequest = useRef<symbol | null>(null)

  const fetchReport = useCallback((dateForRequest: string) => {
    const requestId = Symbol('report-request')
    latestRequest.current = requestId
    setStatus('loading')
    setErrorMessage(null)

    getReport(dateForRequest || undefined)
      .then((data) => {
        if (latestRequest.current !== requestId) return
        setReport(data)
        setStatus('success')
      })
      .catch((error: unknown) => {
        if (latestRequest.current !== requestId) return
        setErrorMessage(error instanceof ApiError ? error.message : 'Could not reach the server.')
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    fetchReport(asOf)
    // Only run on mount — subsequent fetches are user-triggered via Refresh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleRefresh = () => fetchReport(asOf)

  const progressAndRisk: Array<IssueSummary | RiskItem> = report
    ? [...report.progress, ...report.risks]
    : []

  return (
    <div className={styles.app}>
      <Header
        projectKey={report?.projectKey ?? null}
        generatedAt={report?.generatedAt ?? null}
        asOf={asOf}
        onAsOfChange={setAsOf}
        onRefresh={handleRefresh}
        isLoading={status === 'loading'}
      />
      {status === 'error' && (
        <div className={styles.errorBanner} role="alert">
          <p>Couldn&apos;t load this week&apos;s report — {errorMessage}</p>
          <button type="button" onClick={handleRefresh}>
            Retry
          </button>
        </div>
      )}
      {status === 'loading' && !report && <p className={styles.loading}>Loading report…</p>}
      <main className={styles.columns}>
        <ReportColumn
          title="Progress & Risk"
          items={progressAndRisk}
          emptyMessage="No progress or risks to report"
          renderItem={(item) => <IssueCard item={item} />}
        />
        <ReportColumn
          title="This Week"
          items={report?.thisWeek ?? []}
          emptyMessage="Nothing in progress this week"
          renderItem={(item) => <IssueCard item={item} />}
        />
        <ReportColumn
          title="Milestones & Deadlines"
          items={report?.milestones ?? []}
          emptyMessage="No milestones due"
          renderItem={(item) => <MilestoneCard item={item} />}
        />
      </main>
    </div>
  )
}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd frontend && npm run test -- App.test.tsx`
Expected: PASS, 4 tests.

- [ ] **Step 6: Run the full test suite**

Run: `cd frontend && npm run test`
Expected: all test files pass (App, Header, IssueCard, MilestoneCard, ReportColumn, api, signalStatus).

- [ ] **Step 7: Run the build**

Run: `cd frontend && npm run build`
Expected: succeeds with no type errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/App.tsx frontend/src/App.module.css frontend/src/App.test.tsx
git commit -m "Wire App to fetch and render the weekly report"
```

---

## Task 10: Documentation

**Files:**
- Create: `frontend/README.md`
- Modify: `README.md` (root)

**Interfaces:**
- None (documentation only).

- [ ] **Step 1: Create `frontend/README.md`**

```markdown
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
```

- [ ] **Step 2: Add a "Frontend" section to the root `README.md`**

After the "## Tests" section (before "## Project layout"), add:

```markdown
## Frontend

A React + Vite frontend that renders this API lives in `frontend/`. See
`frontend/README.md` for setup and run instructions.
```

- [ ] **Step 3: Commit**

```bash
git add frontend/README.md README.md
git commit -m "Document the frontend setup and usage"
```
