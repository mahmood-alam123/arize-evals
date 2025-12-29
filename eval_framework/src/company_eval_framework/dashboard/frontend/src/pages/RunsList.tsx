import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface Run {
  id: string
  app_name: string
  app_type: string
  eval_suite: string
  dataset_size: number
  passed: boolean
  started_at: string
  finished_at: string | null
  duration_seconds: number | null
  git_branch: string | null
  git_commit: string | null
  created_at: string
}

interface RunsResponse {
  runs: Run[]
  total: number
  limit: number
  offset: number
}

function RunsList() {
  const [runs, setRuns] = useState<Run[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchRuns()
  }, [])

  const fetchRuns = async () => {
    try {
      const response = await fetch('/api/runs')
      if (!response.ok) throw new Error('Failed to fetch runs')
      const data: RunsResponse = await response.json()
      setRuns(data.runs)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString()
  }

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-'
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const mins = Math.floor(seconds / 60)
    const secs = Math.round(seconds % 60)
    return `${mins}m ${secs}s`
  }

  // Calculate stats
  const passCount = runs.filter(r => r.passed).length
  const failCount = runs.filter(r => !r.passed).length
  const passRate = runs.length > 0 ? (passCount / runs.length * 100).toFixed(0) : '0'

  if (loading) {
    return <div className="loading">Loading runs...</div>
  }

  if (error) {
    return <div className="error">Error: {error}</div>
  }

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total Runs</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#22c55e' }}>{passCount}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#ef4444' }}>{failCount}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{passRate}%</div>
          <div className="stat-label">Pass Rate</div>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>Recent Evaluation Runs</h2>
        {runs.length === 0 ? (
          <p className="text-muted">
            No evaluation runs yet. Run <code>company-eval ci-run --report-to http://localhost:8080</code> to report results here.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>App Name</th>
                <th>Eval Suite</th>
                <th>Dataset Size</th>
                <th>Duration</th>
                <th>Branch</th>
                <th>Started</th>
              </tr>
            </thead>
            <tbody>
              {runs.map(run => (
                <tr
                  key={run.id}
                  className="clickable"
                  onClick={() => navigate(`/runs/${run.id}`)}
                >
                  <td>
                    <span className={`badge ${run.passed ? 'badge-pass' : 'badge-fail'}`}>
                      {run.passed ? 'PASS' : 'FAIL'}
                    </span>
                  </td>
                  <td><strong>{run.app_name}</strong></td>
                  <td>{run.eval_suite}</td>
                  <td>{run.dataset_size}</td>
                  <td>{formatDuration(run.duration_seconds)}</td>
                  <td>
                    {run.git_branch && (
                      <span className="text-muted">
                        {run.git_branch}
                        {run.git_commit && ` (${run.git_commit})`}
                      </span>
                    )}
                  </td>
                  <td className="text-muted">{formatDate(run.started_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default RunsList
