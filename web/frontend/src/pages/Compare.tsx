import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import Header from '../components/Header'

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
  total_cost: number | null
  created_at: string
}

interface MetricComparison {
  name: string
  run_a_score: number
  run_b_score: number
  delta: number
  delta_percent: number | null
  run_a_passed: boolean
  run_b_passed: boolean
  improved: boolean
}

interface ComparisonResponse {
  run_a: Run
  run_b: Run
  metrics: MetricComparison[]
  summary: {
    total_metrics: number
    improved: number
    regressed: number
    unchanged: number
    run_a_passed: boolean
    run_b_passed: boolean
  }
}

interface RunsResponse {
  runs: Run[]
  total: number
}

export default function Compare() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [runs, setRuns] = useState<Run[]>([])
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runAId = searchParams.get('a')
  const runBId = searchParams.get('b')

  useEffect(() => {
    fetchRuns()
  }, [])

  useEffect(() => {
    if (runAId && runBId) {
      fetchComparison()
    } else {
      setComparison(null)
    }
  }, [runAId, runBId])

  const fetchRuns = async () => {
    try {
      const response = await fetch('/api/runs?limit=100')
      if (!response.ok) throw new Error('Failed to fetch runs')
      const data: RunsResponse = await response.json()
      setRuns(data.runs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const fetchComparison = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/runs/compare/${runAId}/${runBId}`)
      if (!response.ok) throw new Error('Failed to fetch comparison')
      const data: ComparisonResponse = await response.json()
      setComparison(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const selectRun = (position: 'a' | 'b', runId: string) => {
    const newParams = new URLSearchParams(searchParams)
    newParams.set(position, runId)
    setSearchParams(newParams)
  }

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`
  }

  const formatDelta = (delta: number, deltaPercent: number | null) => {
    const sign = delta > 0 ? '+' : ''
    const percentStr = deltaPercent !== null ? ` (${sign}${deltaPercent.toFixed(1)}%)` : ''
    return `${sign}${(delta * 100).toFixed(1)}%${percentStr}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header variant="light" />

      <main className="pt-20 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Compare Runs</h1>
              <p className="text-gray-600 mt-1">Compare evaluation metrics between two runs</p>
            </div>
            <Link
              to="/dashboard"
              className="text-gray-600 hover:text-gray-900 flex items-center gap-2"
            >
              <span>← Back to Dashboard</span>
            </Link>
          </div>

          {/* Run Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Run A Selection */}
            <div className="light-card p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Run A (Baseline)</h3>
              <select
                value={runAId || ''}
                onChange={(e) => selectRun('a', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a run...</option>
                {runs.map((run) => (
                  <option key={run.id} value={run.id} disabled={run.id === runBId}>
                    {run.app_name} - {run.eval_suite} ({formatTime(run.started_at)})
                    {run.passed ? ' ✓' : ' ✗'}
                  </option>
                ))}
              </select>
              {comparison?.run_a && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${comparison.run_a.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                      {comparison.run_a.passed ? 'PASS' : 'FAIL'}
                    </span>
                    <span className="font-medium">{comparison.run_a.app_name}</span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {comparison.run_a.git_branch && `Branch: ${comparison.run_a.git_branch}`}
                  </div>
                </div>
              )}
            </div>

            {/* Run B Selection */}
            <div className="light-card p-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Run B (Comparison)</h3>
              <select
                value={runBId || ''}
                onChange={(e) => selectRun('b', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a run...</option>
                {runs.map((run) => (
                  <option key={run.id} value={run.id} disabled={run.id === runAId}>
                    {run.app_name} - {run.eval_suite} ({formatTime(run.started_at)})
                    {run.passed ? ' ✓' : ' ✗'}
                  </option>
                ))}
              </select>
              {comparison?.run_b && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${comparison.run_b.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                      {comparison.run_b.passed ? 'PASS' : 'FAIL'}
                    </span>
                    <span className="font-medium">{comparison.run_b.app_name}</span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {comparison.run_b.git_branch && `Branch: ${comparison.run_b.git_branch}`}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Loading/Error States */}
          {loading && (
            <div className="light-card p-8 text-center">
              <div className="text-gray-500">Loading comparison...</div>
            </div>
          )}

          {error && (
            <div className="light-card p-8 text-center">
              <div className="text-red-500">Error: {error}</div>
            </div>
          )}

          {/* Comparison Results */}
          {comparison && !loading && (
            <>
              {/* Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="light-card p-4">
                  <div className="text-2xl font-bold text-gray-900">{comparison.summary.total_metrics}</div>
                  <div className="text-sm text-gray-600">Metrics Compared</div>
                </div>
                <div className="light-card p-4">
                  <div className="text-2xl font-bold text-emerald-600">{comparison.summary.improved}</div>
                  <div className="text-sm text-gray-600">Improved</div>
                </div>
                <div className="light-card p-4">
                  <div className="text-2xl font-bold text-red-600">{comparison.summary.regressed}</div>
                  <div className="text-sm text-gray-600">Regressed</div>
                </div>
                <div className="light-card p-4">
                  <div className="text-2xl font-bold text-gray-600">{comparison.summary.unchanged}</div>
                  <div className="text-sm text-gray-600">Unchanged</div>
                </div>
              </div>

              {/* Overall Status */}
              <div className="light-card p-4 mb-8">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Run A</div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${comparison.summary.run_a_passed ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                        {comparison.summary.run_a_passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </div>
                    <div className="text-2xl text-gray-400">→</div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Run B</div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${comparison.summary.run_b_passed ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                        {comparison.summary.run_b_passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    {comparison.summary.improved > comparison.summary.regressed ? (
                      <div className="text-emerald-600 font-medium">Overall Improvement</div>
                    ) : comparison.summary.regressed > comparison.summary.improved ? (
                      <div className="text-red-600 font-medium">Overall Regression</div>
                    ) : (
                      <div className="text-gray-600 font-medium">No Net Change</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Metrics Comparison Table */}
              <div className="light-card overflow-hidden">
                <table className="table-light">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th className="text-right">Run A</th>
                      <th className="text-right">Run B</th>
                      <th className="text-right">Delta</th>
                      <th className="text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.metrics.map((metric) => (
                      <tr key={metric.name}>
                        <td className="font-medium text-gray-900">{metric.name}</td>
                        <td className="text-right">
                          <span className={metric.run_a_passed ? 'text-emerald-600' : 'text-red-600'}>
                            {formatPercent(metric.run_a_score)}
                          </span>
                        </td>
                        <td className="text-right">
                          <span className={metric.run_b_passed ? 'text-emerald-600' : 'text-red-600'}>
                            {formatPercent(metric.run_b_score)}
                          </span>
                        </td>
                        <td className="text-right">
                          <span className={metric.delta > 0 ? 'text-emerald-600' : metric.delta < 0 ? 'text-red-600' : 'text-gray-600'}>
                            {formatDelta(metric.delta, metric.delta_percent)}
                          </span>
                        </td>
                        <td className="text-center">
                          {metric.improved ? (
                            <span className="text-emerald-600">↑ Improved</span>
                          ) : metric.delta < 0 ? (
                            <span className="text-red-600">↓ Regressed</span>
                          ) : (
                            <span className="text-gray-500">— Same</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* No Selection */}
          {!runAId && !runBId && !loading && (
            <div className="light-card p-12 text-center">
              <div className="text-gray-400 text-lg mb-2">Select two runs to compare</div>
              <p className="text-gray-500 text-sm">
                Choose a baseline run (A) and a comparison run (B) to see metric differences.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
