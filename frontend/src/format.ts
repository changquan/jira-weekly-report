export function formatDate(dateOnly: string | null): string | null {
  if (!dateOnly) return null
  return new Intl.DateTimeFormat('en-US', { day: '2-digit', month: 'short', timeZone: 'UTC' }).format(
    new Date(dateOnly),
  )
}

export function formatStamp(instant: string | null): string {
  if (!instant) return '—'
  return new Intl.DateTimeFormat('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(instant))
}
