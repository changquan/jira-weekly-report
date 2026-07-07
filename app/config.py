"""Application configuration, loaded from environment variables / a .env file."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the weekly report backend.

    Values are read from environment variables (case-insensitive) or a local
    ``.env`` file. Field names map directly to upper-case env vars, e.g.
    ``jira_base_url`` <- ``JIRA_BASE_URL``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- JIRA Cloud connection (required) ---
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str

    # --- Development ---
    # Serve generated fixture data instead of calling JIRA. Lets the full
    # pipeline (report, comments, AI summaries) run without a JIRA instance.
    mock_jira: bool = False

    # --- Report tuning ---
    initiative_issue_type: str = "Initiative"
    risk_window_days: int = 14
    in_progress_status_category: str = "In Progress"

    # --- AI activity summaries (optional; disabled when no API key is set) ---
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    activity_lookback_days: int = 7
    summary_max_concurrency: int = 4

    # --- HTTP client ---
    request_timeout_seconds: float = 30.0
    max_results_per_page: int = 100

    # --- Optional JQL overrides (used verbatim when set) ---
    progress_jql: str | None = None
    risk_jql: str | None = None
    this_week_jql: str | None = None
    milestones_jql: str | None = None
