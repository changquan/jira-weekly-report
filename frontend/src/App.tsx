import { useCallback, useEffect, useRef, useState } from 'react'
import { Header } from './components/Header'
import { ReportColumn } from './components/ReportColumn'
import { IssueCard } from './components/IssueCard'
import { MilestoneCard } from './components/MilestoneCard'
import { ApiError, getReport } from './api'
import type { IssueSummary, RiskItem, WeeklyReport } from './types'
import styles from './App.module.css'

type Status = 'loading' | 'success' | 'error'

export function App() {
  const [asOf, setAsOf] = useState('')
  const [report, setReport] = useState<WeeklyReport | null>(null)
  const [status, setStatus] = useState<Status>('loading')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const latestRequest = useRef<symbol | null>(null)

  const fetchReport = useCallback((dateForRequest: string) => {
    const requestId = Symbol('report-request')
    latestRequest.current = requestId
    setStatus('loading')
    setErrorMessage(null)

    getReport(dateForRequest || undefined)
      .then((data) => {
        if (latestRequest.current !== requestId) return
        setReport(data)
        setStatus('success')
      })
      .catch((error: unknown) => {
        if (latestRequest.current !== requestId) return
        setErrorMessage(error instanceof ApiError ? error.message : 'Could not reach the server.')
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    fetchReport(asOf)
    // Only run on mount — subsequent fetches are user-triggered via Refresh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleRefresh = () => fetchReport(asOf)

  const progressAndRisk: Array<IssueSummary | RiskItem> = report
    ? [...report.progress, ...report.risks]
    : []

  return (
    <div className={styles.app}>
      <Header
        projectKey={report?.projectKey ?? null}
        generatedAt={report?.generatedAt ?? null}
        asOf={asOf}
        onAsOfChange={setAsOf}
        onRefresh={handleRefresh}
        isLoading={status === 'loading'}
      />
      {status === 'error' && (
        <div className={styles.errorBanner} role="alert">
          <p>Couldn&apos;t load this week&apos;s report — {errorMessage}</p>
          <button type="button" onClick={handleRefresh}>
            Retry
          </button>
        </div>
      )}
      {status === 'loading' && !report && <p className={styles.loading}>Loading report…</p>}
      <main className={styles.columns}>
        <ReportColumn
          title="Progress & Risk"
          items={progressAndRisk}
          emptyMessage="No progress or risks to report"
          renderItem={(item) => <IssueCard item={item} />}
        />
        <ReportColumn
          title="This Week"
          items={report?.thisWeek ?? []}
          emptyMessage="Nothing in progress this week"
          renderItem={(item) => <IssueCard item={item} />}
        />
        <ReportColumn
          title="Milestones & Deadlines"
          items={report?.milestones ?? []}
          emptyMessage="No milestones due"
          renderItem={(item) => <MilestoneCard item={item} />}
        />
      </main>
    </div>
  )
}
