import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, getReport } from './api'

describe('getReport', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fetches the report from /api/report', async () => {
    const payload = {
      generatedAt: '2026-07-01T09:00:00+00:00',
      projectKey: 'ABC',
      window: {
        today: '2026-07-01',
        thisWeekStart: '2026-06-29',
        thisWeekEnd: '2026-07-05',
        lastWeekStart: '2026-06-22',
        lastWeekEnd: '2026-06-28',
      },
      progress: [],
      risks: [],
      thisWeek: [],
      milestones: [],
    }
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => payload,
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await getReport()

    expect(fetchMock).toHaveBeenCalledWith('/api/report')
    expect(result).toEqual(payload)
  })

  it('appends as_of when provided', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) })
    vi.stubGlobal('fetch', fetchMock)

    await getReport('2026-06-24')

    expect(fetchMock).toHaveBeenCalledWith('/api/report?as_of=2026-06-24')
  })

  it('throws ApiError with the server detail on a non-2xx response', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => ({ detail: 'Could not reach JIRA: timeout' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(getReport()).rejects.toBeInstanceOf(ApiError)
    await expect(getReport()).rejects.toThrow('Could not reach JIRA: timeout')
  })

  it('falls back to a generic message when the error body is not JSON', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error('not json')
      },
    })
    vi.stubGlobal('fetch', fetchMock)

    await expect(getReport()).rejects.toThrow('Request failed with status 500')
  })
})
