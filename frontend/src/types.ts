export interface IssueSummary {
  key: string
  summary: string
  status: string
  statusCategory: string
  issueType: string
  assignee: string | null
  priority: string | null
  dueDate: string | null
  resolutionDate: string | null
  updated: string | null
  url: string
  activitySummary: string | null
}

export interface RiskItem extends IssueSummary {
  daysUntilDue: number | null
  overdue: boolean
}

export interface MilestoneItem {
  key: string
  summary: string
  status: string
  statusCategory: string
  dueDate: string | null
  overdue: boolean
  url: string
}

export interface ReportWindow {
  today: string
  thisWeekStart: string
  thisWeekEnd: string
  lastWeekStart: string
  lastWeekEnd: string
}

export interface WeeklyReport {
  generatedAt: string
  projectKey: string
  window: ReportWindow
  progress: IssueSummary[]
  risks: RiskItem[]
  thisWeek: IssueSummary[]
  milestones: MilestoneItem[]
}
