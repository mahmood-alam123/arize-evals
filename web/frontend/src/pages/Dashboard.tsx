import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'

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

export default function Dashboard() {
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
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-'
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const mins = Math.floor(seconds / 60)
    const secs = Math.round(seconds % 60)
    return `${mins}m ${secs}s`
  }

  const passCount = runs.filter(r => r.passed).length
  const failCount = runs.filter(r => !r.passed).length
  const passRate = runs.length > 0 ? (passCount / runs.length * 100).toFixed(0) : '0'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Light header */}
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

      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Page header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
            <p className="text-gray-500">Track your LLM evaluation results over time</p>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="light-card p-6">
              <div className="text-3xl font-bold text-gray-900 mb-1">{total}</div>
              <div className="text-sm text-gray-500">Total Runs</div>
            </div>
            <div className="light-card p-6">
              <div className="text-3xl font-bold text-emerald-600 mb-1">{passCount}</div>
              <div className="text-sm text-gray-500">Passed</div>
            </div>
            <div className="light-card p-6">
              <div className="text-3xl font-bold text-red-600 mb-1">{failCount}</div>
              <div className="text-sm text-gray-500">Failed</div>
            </div>
            <div className="light-card p-6">
              <div className="text-3xl font-bold text-gray-900 mb-1">{passRate}%</div>
              <div className="text-sm text-gray-500">Pass Rate</div>
            </div>
          </div>

          {/* Runs table */}
          <div className="light-card">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Runs</h2>
            </div>

            {loading ? (
              <div className="p-12 text-center text-gray-500">
                <div className="inline-block w-6 h-6 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-3" />
                <p>Loading runs...</p>
              </div>
            ) : error ? (
              <div className="p-12 text-center">
                <p className="text-red-600">Error: {error}</p>
              </div>
            ) : runs.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500 mb-4">No evaluation runs yet.</p>
                <p className="text-gray-400 text-sm">
                  Run <code className="bg-gray-100 px-2 py-1 rounded text-gray-700">company-eval ci-run --report-to http://localhost:8080</code> to report results here.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="table-light">
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>App Name</th>
                      <th>Eval Suite</th>
                      <th>Size</th>
                      <th>Duration</th>
                      <th>Branch</th>
                      <th>Started</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map(run => (
                      <tr
                        key={run.id}
                        className="cursor-pointer"
                        onClick={() => navigate(`/runs/${run.id}`)}
                      >
                        <td>
                          <span className={`badge ${run.passed ? 'badge-pass-light' : 'badge-fail-light'}`}>
                            {run.passed ? 'PASS' : 'FAIL'}
                          </span>
                        </td>
                        <td>
                          <span className="font-medium text-gray-900">{run.app_name}</span>
                        </td>
                        <td>
                          <span className="text-gray-600">{run.eval_suite}</span>
                        </td>
                        <td>
                          <span className="text-gray-600">{run.dataset_size}</span>
                        </td>
                        <td>
                          <span className="text-gray-600">{formatDuration(run.duration_seconds)}</span>
                        </td>
                        <td>
                          {run.git_branch ? (
                            <span className="inline-flex items-center gap-2 text-gray-500">
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
                              </svg>
                              {run.git_branch}
                              {run.git_commit && (
                                <span className="font-mono text-xs">({run.git_commit})</span>
                              )}
                            </span>
                          ) : (
                            <span className="text-gray-300">-</span>
                          )}
                        </td>
                        <td>
                          <span className="text-gray-500">{formatDate(run.started_at)}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
