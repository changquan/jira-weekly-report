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
