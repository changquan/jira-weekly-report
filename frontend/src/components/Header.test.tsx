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
