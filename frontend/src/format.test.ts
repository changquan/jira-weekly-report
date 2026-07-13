import { describe, expect, it } from 'vitest'
import { formatDate, formatStamp } from './format'

describe('formatDate', () => {
  it('returns null for a null date', () => {
    expect(formatDate(null)).toBeNull()
  })

  it('formats a date-only string without shifting to the previous day in a west-of-UTC zone', () => {
    expect(formatDate('2026-06-25')).toBe('Jun 25')
  })
})

describe('formatStamp', () => {
  it('returns an em dash for a null instant', () => {
    expect(formatStamp(null)).toBe('—')
  })

  it('formats a UTC instant', () => {
    expect(formatStamp('2026-07-01T09:00:00+00:00')).toMatch(/Jul 01, 2026/)
  })
})
