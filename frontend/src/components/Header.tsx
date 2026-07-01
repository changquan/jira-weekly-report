import { useEffect, useRef, useState } from 'react'
import { formatStamp } from '../format'
import styles from './Header.module.css'

interface HeaderProps {
  projectKey: string | null
  generatedAt: string | null
  asOf: string
  onAsOfChange: (value: string) => void
  onRefresh: () => void
  isLoading: boolean
}

export function Header({ projectKey, generatedAt, asOf, onAsOfChange, onRefresh, isLoading }: HeaderProps) {
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
      <div className={styles.row}>
        <h1 className={styles.title}>Weekly Status</h1>
        {projectKey && <span className={styles.projectBadge}>Project {projectKey}</span>}
        <label className={styles.asOfLabel}>
          As of
          <input
            type="date"
            className={styles.asOfInput}
            value={asOf}
            onChange={(event) => onAsOfChange(event.target.value)}
          />
        </label>
        <button type="button" className={styles.refreshButton} onClick={onRefresh} disabled={isLoading}>
          {isLoading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>
      <p className={flip ? `${styles.stamp} ${styles.stampFlip}` : styles.stamp}>
        Generated {formatStamp(generatedAt)}
      </p>
    </header>
  )
}
