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
