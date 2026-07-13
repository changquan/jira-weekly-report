import { formatDate } from '../format'
import { issueSignal, riskSignal } from '../signalStatus'
import type { IssueSummary, RiskItem } from '../types'
import styles from './Card.module.css'

interface IssueCardProps {
  item: IssueSummary | RiskItem
}

function isRisk(item: IssueSummary | RiskItem): item is RiskItem {
  return 'overdue' in item
}

export function IssueCard({ item }: IssueCardProps) {
  const risk = isRisk(item)
  const signal = risk ? riskSignal(item) : issueSignal(item)
  const statusLabel = risk ? (item.overdue ? 'Overdue' : 'At risk') : item.status
  const dueDate = formatDate(item.dueDate)

  return (
    <a className={styles.card} data-signal={signal} href={item.url} target="_blank" rel="noreferrer">
      <div className={styles.meta}>
        <span className={styles.key}>{item.key}</span>
        <span className={styles.pill}>{statusLabel}</span>
      </div>
      <p className={styles.summary}>{item.summary}</p>
      {item.activitySummary && (
        <div className={styles.ai}>
          <span className={styles.aiLabel}>✦ AI summary</span>
          <p className={styles.aiText}>{item.activitySummary}</p>
        </div>
      )}
      <p className={styles.footer}>
        {item.assignee && <span>{item.assignee}</span>}
        {dueDate && <span>due {dueDate}</span>}
      </p>
    </a>
  )
}
