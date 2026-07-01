import { formatDate } from '../format'
import { milestoneSignal } from '../signalStatus'
import type { MilestoneItem } from '../types'
import styles from './Card.module.css'

interface MilestoneCardProps {
  item: MilestoneItem
}

export function MilestoneCard({ item }: MilestoneCardProps) {
  const signal = milestoneSignal(item)
  const dueDate = formatDate(item.dueDate)
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
