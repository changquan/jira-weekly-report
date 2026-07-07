# JIRA Weekly Report — Backend

A FastAPI backend that assembles a three-column weekly management report from
JIRA Cloud. **Backend only** — it exposes the report as JSON for a frontend to
render.

## The three columns

| Column | Field(s) in response | What it contains |
| ------ | -------------------- | ---------------- |
| **1. Progress & Risk** | `progress`, `risks` | `progress`: issues **resolved during the previous week**. With an OpenAI API key configured, each resolved issue also carries `activitySummary`: an AI summary of the comments left on the issue **and its subtasks** during the reporting window — what was actually done. `risks`: **initiatives** that are not Done and are **overdue or due within `RISK_WINDOW_DAYS`** (default 14). |
| **2. This week** | `thisWeek` | Issues in the **currently active sprint(s)**, whatever project they belong to — the sprint's full committed scope. |
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
and optional raw-JQL overrides).

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
    { "key": "ABC-10", "summary": "...", "status": "Done", "url": "https://.../browse/ABC-10",
      "activitySummary": "Rolled the rate limiter out to all tenants after fixing a quota-reset stampede found in load testing." }
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
- **thisWeek**: `sprint in openSprints()` — deliberately **not** scoped to
  `JIRA_PROJECT_KEY`, because a sprint can pull in issues from other projects.
  If other teams run sprints on the same JIRA instance, scope it yourself via
  `THIS_WEEK_JQL` (e.g. `sprint in openSprints() AND project in (ABC, OPS)`).
- **milestones**: `issuetype = Initiative ORDER BY duedate ASC`.

Any of these can be replaced wholesale via the `*_JQL` env vars.

## AI progress summaries (optional)

Set `OPENAI_API_KEY` in `.env` to enable AI summaries for the "Progress"
column. For each issue resolved during the previous week the backend:

1. reads the issue's subtasks (from the `subtasks` field of the search result),
2. fetches comments for the issue **and every subtask**
   (`GET /rest/api/3/issue/{key}/comment`), keeping only those created within
   the reporting window (last week's Monday through the report time),
3. asks OpenAI (`OPENAI_MODEL`, default `gpt-5-mini`) for a 1-3 sentence
   plain-language summary of what was actually done.

Summaries are fetched concurrently (capped by `SUMMARY_MAX_CONCURRENCY`) and
degrade gracefully: if the key is unset, an issue has no comments in the
window, or a comment fetch or OpenAI call fails, the issue is returned with
`activitySummary: null` and the rest of the report is unaffected.

### Trying it without a JIRA instance

Set `MOCK_JIRA=true` in `.env` (the `JIRA_*` values must still be present but
can be dummies) and the backend serves generated fixture data instead of
calling JIRA: resolved issues with subtasks and realistic comment threads,
dated relative to today so they always fall inside the reporting window. With
`OPENAI_API_KEY` also set, `/api/report` returns real AI summaries of the mock
comments — an end-to-end test of the summary pipeline.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use a fake searcher and never touch the network.

## Frontend

A React + Vite frontend that renders this API lives in `frontend/`. See
`frontend/README.md` for setup and run instructions.

## Project layout

```
app/
  config.py        # env-driven settings (pydantic-settings)
  dates.py         # Monday→Sunday week-window math + JIRA datetime parsing
  jira_client.py   # async JIRA Cloud search + comment client (httpx)
  mock_jira.py     # generated fixture data for MOCK_JIRA=true
  activity.py      # ADF comment flattening, subtask + comment collection
  summarizer.py    # OpenAI-powered progress summaries
  models.py        # pydantic response models (camelCase JSON)
  report.py        # JQL builders + report assembly
  main.py          # FastAPI app and routes
tests/             # unit + API tests
```
