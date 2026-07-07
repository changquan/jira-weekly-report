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
  activitySummary: null,
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

  it('renders the AI activity summary when present', () => {
    render(
      <IssueCard
        item={{ ...baseIssue, activitySummary: 'Deployed the migration to staging.' }}
      />,
    )

    expect(screen.getByText('Deployed the migration to staging.')).toBeInTheDocument()
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
