// Follow the user's locale rather than hardcoding one.
const locales = typeof navigator !== 'undefined' ? [...navigator.languages] : undefined

export function formatDate(dateOnly: string | null): string | null {
  if (!dateOnly) return null
  return new Intl.DateTimeFormat(locales, { day: '2-digit', month: 'short', timeZone: 'UTC' }).format(
    new Date(dateOnly),
  )
}

export function formatWeekdayShort(date: Date): string {
  return new Intl.DateTimeFormat(locales, { weekday: 'short', timeZone: 'UTC' }).format(date)
}

export function formatStamp(instant: string | null): string {
  if (!instant) return '—'
  return new Intl.DateTimeFormat(locales, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(instant))
}
