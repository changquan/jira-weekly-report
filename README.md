# JIRA Weekly Report — Backend

A FastAPI backend that assembles a three-column weekly management report from
JIRA Cloud. **Backend only** — it exposes the report as JSON for a frontend to
render.

## The three columns

| Column | Field(s) in response | What it contains |
| ------ | -------------------- | ---------------- |
| **1. Progress & Risk** | `progress`, `risks` | `progress`: issues **resolved during the previous week**. `risks`: **initiatives** that are not Done and are **overdue or due within `RISK_WINDOW_DAYS`** (default 14). |
| **2. This week** | `thisWeek` | Issues currently **In Progress** — what the team is working on now. |
| **3. Milestones & deadlines** | `milestones` | **Every initiative** and its due date, ordered by deadline. |

"Initiatives" are issues whose JIRA issue type matches `INITIATIVE_ISSUE_TYPE`
(default `Initiative`). Due dates are only evaluated for initiatives, per the
report spec.

Report windows are computed **relative to when the report is generated** (weeks
run Monday→Sunday). You can override the reference date with `?as_of=YYYY-MM-DD`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then fill in your JIRA Cloud details
```

Create a JIRA API token at
<https://id.atlassian.com/manage-profile/security/api-tokens> and set
`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` in
`.env`. See `.env.example` for all options (issue-type name, risk window,
in-progress status category, and optional raw-JQL overrides).

## Run

```bash
uvicorn app.main:app --reload
```

- `GET /health` → `{"status": "ok"}`
- `GET /api/report` → the full weekly report as JSON
- `GET /api/report?as_of=2026-07-01` → the report as if generated on that date
- Interactive docs at `/docs`

### Example response (abridged)

```json
{
  "generatedAt": "2026-07-01T09:00:00+00:00",
  "projectKey": "ABC",
  "window": {
    "today": "2026-07-01",
    "thisWeekStart": "2026-06-29",
    "thisWeekEnd": "2026-07-05",
    "lastWeekStart": "2026-06-22",
    "lastWeekEnd": "2026-06-28"
  },
  "progress": [
    { "key": "ABC-10", "summary": "...", "status": "Done", "url": "https://.../browse/ABC-10" }
  ],
  "risks": [
    { "key": "ABC-1", "summary": "...", "dueDate": "2026-06-25", "overdue": true, "daysUntilDue": -6 }
  ],
  "thisWeek": [
    { "key": "ABC-20", "summary": "...", "status": "In Progress", "assignee": "Dana" }
  ],
  "milestones": [
    { "key": "ABC-1", "summary": "...", "dueDate": "2026-06-25", "overdue": true }
  ]
}
```

## How the data is queried

Each column maps to one JQL query against JIRA Cloud's enhanced search endpoint
(`POST /rest/api/3/search/jql`, with `nextPageToken` pagination):

- **progress**: `resolutiondate` within the previous Mon→Sun week.
- **risks**: `issuetype = Initiative AND statusCategory != Done AND duedate <= today + RISK_WINDOW_DAYS`.
- **thisWeek**: `statusCategory = "In Progress"`.
- **milestones**: `issuetype = Initiative ORDER BY duedate ASC`.

Any of these can be replaced wholesale via the `*_JQL` env vars.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use a fake searcher and never touch the network.

## Project layout

```
app/
  config.py        # env-driven settings (pydantic-settings)
  dates.py         # Monday→Sunday week-window math
  jira_client.py   # async JIRA Cloud search client (httpx)
  models.py        # pydantic response models (camelCase JSON)
  report.py        # JQL builders + report assembly
  main.py          # FastAPI app and routes
tests/             # unit + API tests
```
