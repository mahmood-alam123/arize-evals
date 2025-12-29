import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

interface Metric {
  id: number
  name: string
  mean_score: number
  failure_rate: number
  threshold_type: string | null
  threshold_value: number | null
  passed: boolean
}

interface Score {
  id: number
  metric_name: string
  score: number
  label: string | null
  explanation: string | null
}

interface Failure {
  id: number
  failure_type: string
  explanation: string | null
}

interface TestCase {
  id: number
  conversation_id: string
  input: string
  output: string | null
  context: string | null
  scores: Score[]
  failure: Failure | null
}

interface RunDetail {
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
  config_path: string | null
  created_at: string
  metrics: Metric[]
  test_cases: TestCase[]
}

function RunDetails() {
  const { runId } = useParams<{ runId: string }>()
  const [run, setRun] = useState<RunDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedTestCase, setExpandedTestCase] = useState<number | null>(null)

  useEffect(() => {
    fetchRunDetails()
  }, [runId])

  const fetchRunDetails = async () => {
    try {
      const response = await fetch(`/api/runs/${runId}`)
      if (!response.ok) throw new Error('Failed to fetch run details')
      const data: RunDetail = await response.json()
      setRun(data)
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

  const toggleTestCase = (id: number) => {
    setExpandedTestCase(expandedTestCase === id ? null : id)
  }

  if (loading) {
    return <div className="loading">Loading run details...</div>
  }

  if (error || !run) {
    return <div className="error">Error: {error || 'Run not found'}</div>
  }

  // Calculate failure distribution
  const failureTypes: Record<string, number> = {}
  run.test_cases.forEach(tc => {
    if (tc.failure) {
      failureTypes[tc.failure.failure_type] = (failureTypes[tc.failure.failure_type] || 0) + 1
    }
  })

  return (
    <div>
      <Link to="/" className="back-link">
        &larr; Back to Runs
      </Link>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ marginTop: 0 }}>{run.app_name}</h2>
            <p className="text-muted" style={{ margin: 0 }}>
              {run.eval_suite} &bull; {run.app_type} &bull; {run.dataset_size} test cases
            </p>
          </div>
          <span className={`badge ${run.passed ? 'badge-pass' : 'badge-fail'}`} style={{ fontSize: '16px', padding: '8px 16px' }}>
            {run.passed ? 'PASS' : 'FAIL'}
          </span>
        </div>

        <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          <div>
            <strong>Started:</strong><br />
            <span className="text-muted">{formatDate(run.started_at)}</span>
          </div>
          <div>
            <strong>Duration:</strong><br />
            <span className="text-muted">{formatDuration(run.duration_seconds)}</span>
          </div>
          {run.git_branch && (
            <div>
              <strong>Git Branch:</strong><br />
              <span className="text-muted">{run.git_branch} {run.git_commit && `(${run.git_commit})`}</span>
            </div>
          )}
          {run.config_path && (
            <div>
              <strong>Config:</strong><br />
              <span className="text-muted">{run.config_path}</span>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Metrics</h3>
        <table>
          <thead>
            <tr>
              <th>Metric</th>
              <th>Score</th>
              <th>Threshold</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {run.metrics.map(metric => (
              <tr key={metric.id}>
                <td><strong>{metric.name}</strong></td>
                <td>
                  <div className="metric-row">
                    <span style={{ width: '50px' }}>{(metric.mean_score * 100).toFixed(0)}%</span>
                    <div className="metric-bar">
                      <div
                        className={`metric-fill ${metric.passed ? 'pass' : 'fail'}`}
                        style={{ width: `${metric.mean_score * 100}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td>
                  {metric.threshold_type && metric.threshold_value !== null ? (
                    <span className="text-muted">
                      {metric.threshold_type === 'min' ? '>=' : '<='} {(metric.threshold_value * 100).toFixed(0)}%
                    </span>
                  ) : '-'}
                </td>
                <td>
                  <span className={`badge ${metric.passed ? 'badge-pass' : 'badge-fail'}`}>
                    {metric.passed ? 'PASS' : 'FAIL'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {Object.keys(failureTypes).length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Failure Analysis</h3>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {Object.entries(failureTypes)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count]) => (
                <div key={type} style={{ background: '#fee2e2', padding: '8px 16px', borderRadius: '8px' }}>
                  <strong>{type}</strong>: {count}
                </div>
              ))}
          </div>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Test Cases ({run.test_cases.length})</h3>
        {run.test_cases.map(tc => {
          const hasFailed = tc.scores.some(s => s.score < 1)
          const isExpanded = expandedTestCase === tc.id

          return (
            <div key={tc.id} className="test-case">
              <div
                className="test-case-header"
                onClick={() => toggleTestCase(tc.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span className={`badge ${hasFailed ? 'badge-fail' : 'badge-pass'}`}>
                    {hasFailed ? 'FAIL' : 'PASS'}
                  </span>
                  <span style={{ fontFamily: 'monospace', color: '#6b7280' }}>
                    #{tc.conversation_id}
                  </span>
                  <span style={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {tc.input}
                  </span>
                </div>
                <span>{isExpanded ? '▼' : '▶'}</span>
              </div>

              {isExpanded && (
                <div className="test-case-body">
                  <div style={{ marginBottom: '12px' }}>
                    <strong>Input:</strong>
                    <p style={{ background: '#f3f4f6', padding: '8px', borderRadius: '4px', whiteSpace: 'pre-wrap' }}>
                      {tc.input}
                    </p>
                  </div>

                  {tc.output && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Output:</strong>
                      <p style={{ background: '#f3f4f6', padding: '8px', borderRadius: '4px', whiteSpace: 'pre-wrap' }}>
                        {tc.output}
                      </p>
                    </div>
                  )}

                  {tc.context && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Context:</strong>
                      <p style={{ background: '#f3f4f6', padding: '8px', borderRadius: '4px', whiteSpace: 'pre-wrap', maxHeight: '200px', overflow: 'auto' }}>
                        {tc.context}
                      </p>
                    </div>
                  )}

                  <div style={{ marginBottom: '12px' }}>
                    <strong>Scores:</strong>
                    <table style={{ marginTop: '8px' }}>
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th>Score</th>
                          <th>Label</th>
                          <th>Explanation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {tc.scores.map(score => (
                          <tr key={score.id}>
                            <td>{score.metric_name}</td>
                            <td>
                              <span className={`badge ${score.score >= 1 ? 'badge-pass' : 'badge-fail'}`}>
                                {score.score >= 1 ? 'PASS' : 'FAIL'}
                              </span>
                            </td>
                            <td>{score.label || '-'}</td>
                            <td className="text-muted" style={{ maxWidth: '300px' }}>
                              {score.explanation || '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {tc.failure && (
                    <div style={{ background: '#fee2e2', padding: '12px', borderRadius: '8px' }}>
                      <strong>Failure Type:</strong> {tc.failure.failure_type}
                      {tc.failure.explanation && (
                        <p style={{ margin: '8px 0 0 0' }}>{tc.failure.explanation}</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default RunDetails
