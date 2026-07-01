import { milestoneSignal } from '../signalStatus'
import type { MilestoneItem } from '../types'
import styles from './Card.module.css'

interface MilestoneCardProps {
  item: MilestoneItem
}

function formatDueDate(dueDate: string | null): string | null {
  if (!dueDate) return null
  return new Intl.DateTimeFormat('en-US', { day: '2-digit', month: 'short' }).format(new Date(dueDate))
}

export function MilestoneCard({ item }: MilestoneCardProps) {
  const signal = milestoneSignal(item)
  const dueDate = formatDueDate(item.dueDate)
  const statusLabel = item.overdue ? 'Overdue' : item.status

  return (
    <a className={styles.card} data-signal={signal} href={item.url} target="_blank" rel="noreferrer">
      <span className={styles.rail} data-signal={signal} aria-hidden="true" />
      <div className={styles.body}>
        <div className={styles.meta}>
          <span>{item.key}</span>
          <span>{statusLabel}</span>
        </div>
        <p className={styles.summary}>{item.summary}</p>
        {dueDate && <p className={styles.footer}>due {dueDate}</p>}
      </div>
    </a>
  )
}
