import { useEffect, useRef, useState } from 'react'
import { formatDate, formatStamp } from '../format'
import type { ReportWindow } from '../types'
import styles from './Header.module.css'

interface HeaderProps {
  projectKey: string | null
  generatedAt: string | null
  window?: ReportWindow | null
  asOf: string
  onAsOfChange: (value: string) => void
  onRefresh: () => void
  isLoading: boolean
}

// ISO 8601 week number of the week containing the given date.
function isoWeek(dateOnly: string): number {
  const date = new Date(`${dateOnly}T00:00:00Z`)
  date.setUTCDate(date.getUTCDate() + 3 - ((date.getUTCDay() + 6) % 7))
  const week1 = new Date(Date.UTC(date.getUTCFullYear(), 0, 4))
  return (
    1 +
    Math.round(
      ((date.getTime() - week1.getTime()) / 86400000 - 3 + ((week1.getUTCDay() + 6) % 7)) / 7,
    )
  )
}

export function Header({
  projectKey,
  generatedAt,
  window: reportWindow,
  asOf,
  onAsOfChange,
  onRefresh,
  isLoading,
}: HeaderProps) {
  const [flip, setFlip] = useState(false)
  const previousStamp = useRef<string | null>(null)

  useEffect(() => {
    const previous = previousStamp.current
    previousStamp.current = generatedAt
    if (generatedAt && previous && previous !== generatedAt) {
      setFlip(true)
      const timeout = setTimeout(() => setFlip(false), 400)
      return () => clearTimeout(timeout)
    }
  }, [generatedAt])

  return (
    <header className={styles.masthead}>
      <div>
        <p className={styles.eyebrow}>
          Weekly report
          {projectKey && (
            <>
              {' · '}
              <span>Project {projectKey}</span>
            </>
          )}
        </p>
        <h1 className={styles.weekTitle}>
          {reportWindow ? `Week ${isoWeek(reportWindow.thisWeekStart)}` : 'Weekly Report'}
        </h1>
        {reportWindow && (
          <p className={styles.weekRange}>
            {formatDate(reportWindow.thisWeekStart)} – {formatDate(reportWindow.thisWeekEnd)}
            {' · progress counted '}
            {formatDate(reportWindow.lastWeekStart)} – {formatDate(reportWindow.lastWeekEnd)}
          </p>
        )}
        <p className={flip ? `${styles.stamp} ${styles.stampFlip}` : styles.stamp} aria-live="polite">
          Generated {formatStamp(generatedAt)}
        </p>
      </div>
      <div className={styles.controls}>
        <label className={styles.asOfLabel}>
          As of
          <input
            type="date"
            name="as-of"
            autoComplete="off"
            className={styles.asOfInput}
            value={asOf}
            onChange={(event) => onAsOfChange(event.target.value)}
          />
        </label>
        <button type="button" className={styles.refreshButton} onClick={onRefresh} disabled={isLoading}>
          {isLoading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>
    </header>
  )
}
