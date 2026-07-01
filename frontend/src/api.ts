import type { WeeklyReport } from './types'

export class ApiError extends Error {}

export async function getReport(asOf?: string): Promise<WeeklyReport> {
  const url = asOf ? `/api/report?as_of=${asOf}` : '/api/report'
  const response = await fetch(url)

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') {
        detail = body.detail
      }
    } catch {
      // response body wasn't JSON — keep the generic detail
    }
    throw new ApiError(detail)
  }

  return response.json()
}
