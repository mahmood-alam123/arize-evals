import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Header from '../components/Header'

interface Trace {
  id: string
  name: string
  project_name: string | null
  start_time: string
  end_time: string | null
  duration_ms: number | null
  status: string
  total_tokens: number | null
  total_cost: number | null
  span_count: number
  created_at: string
}

interface TracesResponse {
  traces: Trace[]
  total: number
  limit: number
  offset: number
}

export default function Traces() {
  const [traces, setTraces] = useState<Trace[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [projectFilter, setProjectFilter] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchTraces()
  }, [projectFilter])

  const fetchTraces = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (projectFilter) params.set('project_name', projectFilter)

      const response = await fetch(`/api/traces?${params}`)
      if (!response.ok) throw new Error('Failed to fetch traces')
      const data: TracesResponse = await response.json()
      setTraces(data.traces)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (ms: number | null) => {
    if (ms === null) return '-'
    if (ms < 1000) return `${ms.toFixed(0)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }

  const formatCost = (cost: number | null) => {
    if (cost === null) return '-'
    return `$${cost.toFixed(4)}`
  }

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-100 text-emerald-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getSpanTypeIcon = (name: string) => {
    if (name.toLowerCase().includes('llm') || name.toLowerCase().includes('chat')) {
      return '🤖'
    }
    if (name.toLowerCase().includes('tool')) {
      return '🔧'
    }
    if (name.toLowerCase().includes('retriev') || name.toLowerCase().includes('rag')) {
      return '📚'
    }
    return '⚡'
  }

  // Stats
  const completedCount = traces.filter(t => t.status === 'completed').length
  const errorCount = traces.filter(t => t.status === 'error').length
  const totalTokens = traces.reduce((sum, t) => sum + (t.total_tokens || 0), 0)
  const totalCost = traces.reduce((sum, t) => sum + (t.total_cost || 0), 0)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header variant="light" />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-gray-500">Loading traces...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header variant="light" />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-red-500">Error: {error}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header variant="light" />

      <main className="pt-20 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Traces</h1>
              <p className="text-gray-600 mt-1">Monitor LLM calls, tool usage, and execution flow</p>
            </div>
            <Link
              to="/dashboard"
              className="text-gray-600 hover:text-gray-900 flex items-center gap-2"
            >
              <span>← Back to Dashboard</span>
            </Link>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="light-card p-4">
              <div className="text-2xl font-bold text-gray-900">{total}</div>
              <div className="text-sm text-gray-600">Total Traces</div>
            </div>
            <div className="light-card p-4">
              <div className="text-2xl font-bold text-emerald-600">{completedCount}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="light-card p-4">
              <div className="text-2xl font-bold text-gray-900">{totalTokens.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Total Tokens</div>
            </div>
            <div className="light-card p-4">
              <div className="text-2xl font-bold text-gray-900">${totalCost.toFixed(4)}</div>
              <div className="text-sm text-gray-600">Total Cost</div>
            </div>
          </div>

          {/* Filters */}
          <div className="light-card p-4 mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="Filter by project..."
                value={projectFilter}
                onChange={(e) => setProjectFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Traces Table */}
          {traces.length === 0 ? (
            <div className="light-card p-12 text-center">
              <div className="text-gray-400 text-lg mb-2">No traces yet</div>
              <p className="text-gray-500 text-sm">
                Traces will appear here when your LLM application sends them via the API.
              </p>
            </div>
          ) : (
            <div className="light-card overflow-hidden">
              <table className="table-light">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Name</th>
                    <th>Project</th>
                    <th>Spans</th>
                    <th>Duration</th>
                    <th>Tokens</th>
                    <th>Cost</th>
                    <th>Started</th>
                  </tr>
                </thead>
                <tbody>
                  {traces.map((trace) => (
                    <tr
                      key={trace.id}
                      onClick={() => navigate(`/traces/${trace.id}`)}
                      className="cursor-pointer hover:bg-gray-50"
                    >
                      <td>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(trace.status)}`}>
                          {trace.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="font-medium text-gray-900">
                        {getSpanTypeIcon(trace.name)} {trace.name}
                      </td>
                      <td className="text-gray-600">{trace.project_name || '-'}</td>
                      <td className="text-gray-600">{trace.span_count}</td>
                      <td className="text-gray-600">{formatDuration(trace.duration_ms)}</td>
                      <td className="text-gray-600">{trace.total_tokens?.toLocaleString() || '-'}</td>
                      <td className="text-gray-600">{formatCost(trace.total_cost)}</td>
                      <td className="text-gray-500 text-sm">{formatTime(trace.start_time)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
