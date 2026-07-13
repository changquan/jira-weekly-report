import type { IssueSummary, MilestoneItem, RiskItem } from './types'

export type SignalColor = 'green' | 'amber' | 'red' | 'slate'

export function issueSignal(issue: IssueSummary): SignalColor {
  return issue.statusCategory === 'Done' ? 'green' : 'slate'
}

export function riskSignal(risk: RiskItem): SignalColor {
  return risk.overdue ? 'red' : 'amber'
}

export function milestoneSignal(milestone: MilestoneItem): SignalColor {
  if (milestone.overdue) return 'red'
  return milestone.statusCategory === 'Done' ? 'green' : 'slate'
}
