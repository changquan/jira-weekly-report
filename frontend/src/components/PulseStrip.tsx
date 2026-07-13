import { issueSignal, milestoneSignal, riskSignal, type SignalColor } from '../signalStatus'
import type { WeeklyReport } from '../types'
import styles from './PulseStrip.module.css'

interface PulseStripProps {
  report: WeeklyReport
}

const LEGEND: Array<{ signal: SignalColor; label: string }> = [
  { signal: 'green', label: 'done' },
  { signal: 'slate', label: 'in flight' },
  { signal: 'amber', label: 'due soon' },
  { signal: 'red', label: 'overdue' },
]

// One signal per unique issue, in board order (risks also appear in milestones).
function boardSignals(report: WeeklyReport): SignalColor[] {
  const seen = new Map<string, SignalColor>()
  for (const issue of report.progress) {
    if (!seen.has(issue.key)) seen.set(issue.key, issueSignal(issue))
  }
  for (const risk of report.risks) {
    if (!seen.has(risk.key)) seen.set(risk.key, riskSignal(risk))
  }
  for (const issue of report.thisWeek) {
    if (!seen.has(issue.key)) seen.set(issue.key, issueSignal(issue))
  }
  for (const milestone of report.milestones) {
    if (!seen.has(milestone.key)) seen.set(milestone.key, milestoneSignal(milestone))
  }
  return [...seen.values()]
}

export function PulseStrip({ report }: PulseStripProps) {
  const signals = boardSignals(report)
  if (signals.length === 0) return null

  const counts = LEGEND.map(({ signal, label }) => ({
    signal,
    label,
    count: signals.filter((s) => s === signal).length,
  })).filter(({ count }) => count > 0)
  const description = counts.map(({ count, label }) => `${count} ${label}`).join(', ')

  return (
    <section className={styles.pulse} aria-label="Board health">
      <div className={styles.bar} role="img" aria-label={`${signals.length} issues: ${description}`}>
        {signals.map((signal, index) => (
          <span
            key={index}
            className={styles.seg}
            data-signal={signal}
            style={{ animationDelay: `${index * 35}ms` }}
          />
        ))}
      </div>
      <p className={styles.legend} aria-hidden="true">
        {counts.map(({ signal, label, count }) => (
          <span key={signal} className={styles.legendItem}>
            <span className={styles.dot} data-signal={signal} />
            {count} {label}
          </span>
        ))}
      </p>
    </section>
  )
}
