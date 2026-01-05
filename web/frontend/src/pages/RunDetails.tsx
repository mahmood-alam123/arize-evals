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
  prompt: string | null
  trace_id: string | null
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
  total_cost: number | null
  app_cost: number | null
  eval_cost: number | null
  created_at: string
  metrics: Metric[]
  test_cases: TestCase[]
}

export default function RunDetails() {
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

  const formatCost = (cost: number | null) => {
    if (cost === null || cost === undefined) return '-'
    if (cost < 0.01) return `$${cost.toFixed(4)}`
    return `$${cost.toFixed(2)}`
  }

  // Light header component
  const LightHeader = () => (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center transition-transform group-hover:scale-105">
              <span className="text-white font-bold text-sm">CE</span>
            </div>
            <span className="font-semibold text-lg text-gray-900">Company Eval</span>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              to="/docs"
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Docs
            </Link>
            <Link
              to="/"
              className="px-4 py-2 rounded-lg font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              Sign Out
            </Link>
          </div>
        </div>
      </div>
    </header>
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <LightHeader />
        <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto text-center py-20">
            <div className="inline-block w-6 h-6 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-3" />
            <p className="text-gray-500">Loading run details...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error || !run) {
    return (
      <div className="min-h-screen bg-gray-50">
        <LightHeader />
        <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto text-center py-20">
            <p className="text-red-600">Error: {error || 'Run not found'}</p>
            <Link to="/dashboard" className="inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium mt-4 bg-gray-100 text-gray-700 hover:bg-gray-200">
              Back to Dashboard
            </Link>
          </div>
        </main>
      </div>
    )
  }

  // Calculate failure distribution
  const failureTypes: Record<string, number> = {}
  run.test_cases.forEach(tc => {
    if (tc.failure) {
      failureTypes[tc.failure.failure_type] = (failureTypes[tc.failure.failure_type] || 0) + 1
    }
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <LightHeader />

      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Back link */}
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </Link>

          {/* Run header */}
          <div className="light-card p-6 mb-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900">{run.app_name}</h1>
                  <span className={`badge ${run.passed ? 'badge-pass-light' : 'badge-fail-light'}`}>
                    {run.passed ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                <p className="text-gray-500">
                  {run.eval_suite} • {run.app_type} • {run.dataset_size} test cases
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t border-gray-200">
              <div>
                <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Started</div>
                <div className="text-gray-700">{formatDate(run.started_at)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Duration</div>
                <div className="text-gray-700">{formatDuration(run.duration_seconds)}</div>
              </div>
              {run.git_branch && (
                <div>
                  <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Branch</div>
                  <div className="text-gray-700 font-mono text-sm">
                    {run.git_branch} {run.git_commit && `(${run.git_commit})`}
                  </div>
                </div>
              )}
              {run.config_path && (
                <div>
                  <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">Config</div>
                  <div className="text-gray-700 font-mono text-sm truncate">{run.config_path}</div>
                </div>
              )}
            </div>
          </div>

          {/* Cost Breakdown */}
          {(run.total_cost !== null || run.app_cost !== null || run.eval_cost !== null) && (
            <div className="light-card p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Cost Breakdown</h2>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">App Cost</div>
                  <div className="text-2xl font-bold text-gray-900 font-mono">{formatCost(run.app_cost)}</div>
                  <div className="text-xs text-gray-500 mt-1">Output generation</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Eval Cost</div>
                  <div className="text-2xl font-bold text-gray-900 font-mono">{formatCost(run.eval_cost)}</div>
                  <div className="text-xs text-gray-500 mt-1">LLM judging</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                  <div className="text-xs text-blue-600 uppercase tracking-wider mb-2">Total Cost</div>
                  <div className="text-2xl font-bold text-blue-700 font-mono">{formatCost(run.total_cost)}</div>
                  <div className="text-xs text-blue-500 mt-1">Combined</div>
                </div>
              </div>
            </div>
          )}

          {/* Metrics */}
          <div className="light-card mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Metrics</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="table-light">
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
                      <td>
                        <span className="font-medium text-gray-900">{metric.name}</span>
                      </td>
                      <td>
                        <div className="flex items-center gap-4">
                          <span className="text-gray-700 w-12">
                            {(metric.mean_score * 100).toFixed(0)}%
                          </span>
                          <div className="w-32 metric-bar-light">
                            <div
                              className={`metric-fill-light h-full rounded-full ${metric.passed ? 'pass' : 'fail'}`}
                              style={{ width: `${metric.mean_score * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>
                        {metric.threshold_type && metric.threshold_value !== null ? (
                          <span className="text-gray-500">
                            {metric.threshold_type === 'min' ? '≥' : '≤'}{' '}
                            {(metric.threshold_value * 100).toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-gray-300">-</span>
                        )}
                      </td>
                      <td>
                        <span className={`badge ${metric.passed ? 'badge-pass-light' : 'badge-fail-light'}`}>
                          {metric.passed ? 'PASS' : 'FAIL'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Failure Analysis */}
          {Object.keys(failureTypes).length > 0 && (
            <div className="light-card mb-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Failure Analysis</h2>
              </div>
              <div className="p-6">
                <div className="flex flex-wrap gap-3">
                  {Object.entries(failureTypes)
                    .sort((a, b) => b[1] - a[1])
                    .map(([type, count]) => (
                      <div
                        key={type}
                        className="px-4 py-2 rounded-lg bg-red-50 border border-red-200"
                      >
                        <span className="font-medium text-red-700">{type}</span>
                        <span className="text-red-500 ml-2">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Test Cases */}
          <div className="light-card">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Test Cases ({run.test_cases.length})
              </h2>
            </div>
            <div className="divide-y divide-gray-100">
              {run.test_cases.map(tc => {
                const hasFailed = tc.scores.some(s => s.score < 1)
                const isExpanded = expandedTestCase === tc.id

                return (
                  <div key={tc.id}>
                    <button
                      className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
                      onClick={() => setExpandedTestCase(isExpanded ? null : tc.id)}
                    >
                      <div className="flex items-center gap-4 min-w-0">
                        <span className={`badge ${hasFailed ? 'badge-fail-light' : 'badge-pass-light'}`}>
                          {hasFailed ? 'FAIL' : 'PASS'}
                        </span>
                        <span className="font-mono text-sm text-gray-400">
                          #{tc.conversation_id}
                        </span>
                        <span className="text-gray-600 truncate max-w-md">
                          {tc.input}
                        </span>
                      </div>
                      <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {isExpanded && (
                      <div className="px-6 pb-6 space-y-4 bg-gray-50">
                        {/* View Trace Button */}
                        {tc.trace_id && (
                          <div className="flex justify-end">
                            <Link
                              to={`/traces/${tc.trace_id}`}
                              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                              View Trace
                            </Link>
                          </div>
                        )}

                        <div className="grid gap-4">
                          {/* Full LLM Prompt */}
                          {tc.prompt && (
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">Full Prompt (sent to LLM)</div>
                              <div className="bg-gray-900 text-gray-100 border border-gray-700 rounded-lg p-4 whitespace-pre-wrap font-mono text-sm max-h-64 overflow-y-auto">
                                {tc.prompt}
                              </div>
                            </div>
                          )}

                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">User Input</div>
                              <div className="bg-white border border-gray-300 rounded-lg p-4 text-gray-900 whitespace-pre-wrap">
                                {tc.input}
                              </div>
                            </div>

                            {tc.output && (
                              <div>
                                <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">Model Response</div>
                                <div className="bg-white border border-gray-300 rounded-lg p-4 text-gray-900 whitespace-pre-wrap">
                                  {tc.output}
                                </div>
                              </div>
                            )}
                          </div>

                          {tc.context && (
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">RAG Context</div>
                              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-gray-900 whitespace-pre-wrap max-h-48 overflow-y-auto">
                                {tc.context}
                              </div>
                            </div>
                          )}
                        </div>

                        {tc.scores.length > 0 && (
                          <div>
                            <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Scores</div>
                            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                              <table className="table-light">
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
                                      <td className="text-gray-700">{score.metric_name}</td>
                                      <td>
                                        <span className={`badge ${score.score >= 1 ? 'badge-pass-light' : 'badge-fail-light'}`}>
                                          {score.score >= 1 ? 'PASS' : 'FAIL'}
                                        </span>
                                      </td>
                                      <td className="text-gray-600">{score.label || '-'}</td>
                                      <td className="text-gray-500 max-w-xs truncate">
                                        {score.explanation || '-'}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {tc.failure && (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="font-medium text-red-700 mb-1">
                              Failure Type: {tc.failure.failure_type}
                            </div>
                            {tc.failure.explanation && (
                              <div className="text-red-600 text-sm">
                                {tc.failure.explanation}
                              </div>
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
        </div>
      </main>
    </div>
  )
}
