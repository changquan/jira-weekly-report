# How the Weekly Report Is Built — and What You Need to Do in JIRA

This report pulls straight from JIRA. **It cannot show work that isn't reflected in
JIRA fields.** This doc explains exactly which fields drive each column, so you know
what to keep up to date.

## The reporting window

Weeks run **Monday → Sunday** (`app/dates.py`).

- **This week** = the Monday–Sunday week containing the report date.
- **Last week** = the Monday–Sunday week before that.

The report is normally generated "as of today", so a report generated on Monday
covers the previous Mon–Sun as "last week". You can regenerate any past week with
`/api/report?as_of=YYYY-MM-DD` (or the date picker in the UI) — windows are computed
relative to that date.

The UI shows three columns. The backend runs **four JIRA queries** (column 1 is two
lists merged together).

---

## Column 1 — Progress & Risk

### Progress (what we shipped last week)

**Query** (`progress_jql` in `app/report.py`):

```
project = <PROJECT> AND resolutiondate >= <last Monday> AND resolutiondate < <this Monday>
ORDER BY resolutiondate DESC
```

An issue appears here if — and only if — its **resolution date falls inside last
week**. Any issue type qualifies.

Key implications:

- JIRA sets `resolutiondate` when an issue gets a **Resolution** (usually by moving
  it to Done through the workflow). If a ticket is finished but never resolved in
  JIRA, it will **never show up as progress**.
- If you resolve a ticket late (e.g. work finished last week but you close it this
  Wednesday), it will show up in *next* week's report, not the one covering the week
  the work happened. Resolve tickets in the week you finish them.
- Reopening and re-resolving an issue moves its resolution date, which moves which
  week it reports under.

**AI activity summary.** When an OpenAI key is configured, each progress issue gets
a 1–3 sentence blurb of *what was actually done*. The summarizer
(`app/activity.py`, `app/summarizer.py`):

1. Fetches all comments on the issue **and on each of its subtasks**.
2. Keeps only comments **created from last Monday up to report time**.
3. Sends those comments (up to 30, each truncated to 2,000 chars) plus the subtask
   list to the model, which is instructed to only report work the comments support.

Implications for the team:

- **No comments in the window → no summary.** The card still appears, just without a
  blurb. If you want your work described in the report, leave a short comment on the
  issue (or its subtasks) saying what you did as you go.
- Comments are the *only* evidence used — descriptions, commits, and PR links that
  aren't in comments are invisible to the summary.
- A summarizer failure never breaks the report; the issue just renders without a
  summary.

### Risk (initiatives in danger)

**Query** (`risk_jql`):

```
project = <PROJECT> AND issuetype = "Initiative" AND statusCategory != Done
AND duedate <= <today + 14 days>
ORDER BY duedate ASC
```

An initiative is flagged as a risk when all three hold:

1. Its **issue type** is `Initiative` (configurable via `INITIATIVE_ISSUE_TYPE`).
2. Its **status category is not Done** — the JIRA *category* behind the status, not
   the status name, so any status mapped to the green "Done" category clears it.
3. Its **due date** is on or before **today + 14 days** (configurable via
   `RISK_WINDOW_DAYS`). This includes anything already overdue.

Each risk card carries `daysUntilDue` (negative-ish semantics: computed as
`due − today`, so overdue items have negative values) and an `overdue` flag
(`due < today`).

Implications:

- **Initiatives without a due date can never appear as risks** — silently. Set due
  dates on every initiative.
- Finished initiatives keep showing as risks until their status is actually moved to
  a Done-category status.

---

## Column 2 — This Week

**Query** (`this_week_jql`):

```
sprint in openSprints() ORDER BY updated DESC
```

This is the **full scope of the currently active sprint(s)**: every issue placed in
an open sprint appears, regardless of status (To Do, In Progress, Done). It is
deliberately **not scoped to the project**, because our sprint can pull in issues
from other JIRA projects.

Implications:

- **Sprint membership is the only criterion.** If a ticket you're working on isn't
  in the active sprint, it won't show; if a ticket is parked in the sprint but not
  really being worked, it will.
- Keep the sprint board honest: add tickets to the sprint when they become this
  week's work, and remove ones that get descoped.
- Because there is no project filter, the default query matches **every active
  sprint in the JIRA instance**. If other teams run sprints on the same instance,
  set `THIS_WEEK_JQL` to scope it, e.g.
  `sprint in openSprints() AND project in (ABC, OPS)`.

---

## Column 3 — Milestones & Deadlines

**Query** (`milestones_jql`):

```
project = <PROJECT> AND issuetype = "Initiative" ORDER BY duedate ASC
```

**Every initiative** in the project, regardless of status, sorted by due date
(soonest first; initiatives without a due date sort last). Each card shows status
and due date, and gets an `overdue` flag when the due date is in the past **and**
the status category is not Done — so a completed initiative is never painted
overdue.

Implications:

- This column is only as good as your initiative list: milestone-level work must be
  filed as the `Initiative` issue type with a due date.
- Old initiatives never disappear from this column; close or archive ones that are
  no longer relevant.

---

## Team checklist for a correct report

1. **Resolve tickets in the week you finish them** — the resolution date is the sole
   driver of the Progress list.
2. **Comment as you work** (on the issue or its subtasks) — comments made during the
   window are the only input to the AI progress summaries.
3. **Keep the sprint board honest** — sprint membership drives the This Week
   column; the "Done" status category clears risks and overdue flags.
4. **Give every initiative a due date** — no due date means it can never be flagged
   as a risk and sorts to the bottom of Milestones.
5. **Use the Initiative issue type** for milestone-level work — Risks and Milestones
   only look at that type.

## Configuration knobs (for whoever runs the report)

All set via environment variables / `.env` (`app/config.py`):

| Variable | Default | Effect |
| --- | --- | --- |
| `JIRA_PROJECT_KEY` | required | Project all four queries filter on |
| `INITIATIVE_ISSUE_TYPE` | `Initiative` | Issue type used by Risk and Milestones |
| `RISK_WINDOW_DAYS` | `14` | How far ahead an initiative's due date counts as "at risk" |
| `OPENAI_API_KEY` | unset | Enables AI activity summaries when set |
| `PROGRESS_JQL` / `RISK_JQL` / `THIS_WEEK_JQL` / `MILESTONES_JQL` | unset | Replace any default query verbatim |
| `MOCK_JIRA` | `false` | Serve generated fixture data instead of calling JIRA |
