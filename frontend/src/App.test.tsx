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
