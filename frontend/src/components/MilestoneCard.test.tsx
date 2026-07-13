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
