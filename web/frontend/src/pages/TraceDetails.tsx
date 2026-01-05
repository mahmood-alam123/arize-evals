import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Header from '../components/Header'

interface Span {
  id: string
  trace_id: string
  parent_span_id: string | null
  name: string
  span_type: string
  start_time: string
  end_time: string | null
  duration_ms: number | null
  status: string
  input: string | null
  output: string | null
  model: string | null
  provider: string | null
  prompt_tokens: number | null
  completion_tokens: number | null
  total_tokens: number | null
  cost: number | null
  tool_name: string | null
  tool_args: string | null
  error_message: string | null
  metadata: string | null
}

interface TraceDetail {
  id: string
  name: string
  project_name: string | null
  start_time: string
  end_time: string | null
  duration_ms: number | null
  status: string
  input: string | null
  output: string | null
  metadata: string | null
  total_tokens: number | null
  total_cost: number | null
  error_message: string | null
  created_at: string
  spans: Span[]
}

export default function TraceDetails() {
  const { traceId } = useParams<{ traceId: string }>()
  const [trace, setTrace] = useState<TraceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSpan, setSelectedSpan] = useState<Span | null>(null)

  useEffect(() => {
    if (traceId) {
      fetchTrace()
    }
  }, [traceId])

  const fetchTrace = async () => {
    try {
      const response = await fetch(`/api/traces/${traceId}`)
      if (!response.ok) throw new Error('Failed to fetch trace')
      const data: TraceDetail = await response.json()
      setTrace(data)
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
        return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getSpanTypeColor = (type: string) => {
    switch (type) {
      case 'llm':
        return 'bg-purple-500'
      case 'tool':
        return 'bg-orange-500'
      case 'retrieval':
        return 'bg-blue-500'
      case 'chain':
        return 'bg-green-500'
      case 'agent':
        return 'bg-pink-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getSpanTypeIcon = (type: string) => {
    switch (type) {
      case 'llm':
        return '🤖'
      case 'tool':
        return '🔧'
      case 'retrieval':
        return '📚'
      case 'chain':
        return '🔗'
      case 'agent':
        return '🤖'
      default:
        return '⚡'
    }
  }

  const parseJSON = (str: string | null) => {
    if (!str) return null
    try {
      return JSON.parse(str)
    } catch {
      return str
    }
  }

  // Calculate span positions for waterfall
  const calculateWaterfall = (spans: Span[]) => {
    if (spans.length === 0) return []

    const traceStart = new Date(trace!.start_time).getTime()
    const traceDuration = trace!.duration_ms || 1

    return spans.map(span => {
      const spanStart = new Date(span.start_time).getTime()
      const startOffset = ((spanStart - traceStart) / traceDuration) * 100
      const width = ((span.duration_ms || 0) / traceDuration) * 100

      return {
        ...span,
        startOffset: Math.max(0, Math.min(startOffset, 100)),
        width: Math.max(1, Math.min(width, 100 - startOffset)),
      }
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header variant="light" />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-gray-500">Loading trace...</div>
        </div>
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header variant="light" />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-red-500">Error: {error || 'Trace not found'}</div>
        </div>
      </div>
    )
  }

  const waterfallSpans = calculateWaterfall(trace.spans)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header variant="light" />

      <main className="pt-20 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Link to="/traces" className="text-gray-500 hover:text-gray-700">
                  ← Traces
                </Link>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                {trace.name}
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(trace.status)}`}>
                  {trace.status.toUpperCase()}
                </span>
              </h1>
              {trace.project_name && (
                <p className="text-gray-600 mt-1">Project: {trace.project_name}</p>
              )}
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="light-card p-4">
              <div className="text-sm text-gray-600">Duration</div>
              <div className="text-xl font-bold text-gray-900">{formatDuration(trace.duration_ms)}</div>
            </div>
            <div className="light-card p-4">
              <div className="text-sm text-gray-600">Spans</div>
              <div className="text-xl font-bold text-gray-900">{trace.spans.length}</div>
            </div>
            <div className="light-card p-4">
              <div className="text-sm text-gray-600">Total Tokens</div>
              <div className="text-xl font-bold text-gray-900">{trace.total_tokens?.toLocaleString() || '-'}</div>
            </div>
            <div className="light-card p-4">
              <div className="text-sm text-gray-600">Cost</div>
              <div className="text-xl font-bold text-gray-900">{formatCost(trace.total_cost)}</div>
            </div>
            <div className="light-card p-4">
              <div className="text-sm text-gray-600">Started</div>
              <div className="text-sm font-medium text-gray-900">{formatTime(trace.start_time)}</div>
            </div>
          </div>

          {/* Input/Output */}
          {(trace.input || trace.output) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {trace.input && (
                <div className="light-card p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Input</h3>
                  <pre className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg overflow-x-auto">
                    {typeof parseJSON(trace.input) === 'object'
                      ? JSON.stringify(parseJSON(trace.input), null, 2)
                      : trace.input}
                  </pre>
                </div>
              )}
              {trace.output && (
                <div className="light-card p-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Output</h3>
                  <pre className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg overflow-x-auto">
                    {typeof parseJSON(trace.output) === 'object'
                      ? JSON.stringify(parseJSON(trace.output), null, 2)
                      : trace.output}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {trace.error_message && (
            <div className="light-card p-4 mb-8 border-l-4 border-red-500">
              <h3 className="text-sm font-medium text-red-700 mb-2">Error</h3>
              <pre className="text-sm text-red-800 bg-red-50 p-3 rounded-lg overflow-x-auto">
                {trace.error_message}
              </pre>
            </div>
          )}

          {/* Span Legend */}
          <div className="light-card p-4 mb-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Span Types</h3>
            <div className="flex flex-wrap gap-4">
              {['llm', 'tool', 'retrieval', 'chain', 'agent', 'custom'].map(type => (
                <div key={type} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded ${getSpanTypeColor(type)}`}></div>
                  <span className="text-sm text-gray-600 capitalize">{getSpanTypeIcon(type)} {type}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Waterfall View */}
          <div className="light-card overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Span Waterfall</h3>
            </div>

            {trace.spans.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No spans recorded for this trace
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {waterfallSpans.map((span) => (
                  <div
                    key={span.id}
                    className={`p-4 hover:bg-gray-50 cursor-pointer ${selectedSpan?.id === span.id ? 'bg-blue-50' : ''}`}
                    onClick={() => setSelectedSpan(selectedSpan?.id === span.id ? null : span)}
                  >
                    <div className="flex items-center gap-4">
                      {/* Span Info */}
                      <div className="w-48 flex-shrink-0">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${getSpanTypeColor(span.span_type)}`}></span>
                          <span className="font-medium text-gray-900 text-sm truncate">
                            {getSpanTypeIcon(span.span_type)} {span.name}
                          </span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {span.span_type} • {formatDuration(span.duration_ms)}
                        </div>
                      </div>

                      {/* Waterfall Bar */}
                      <div className="flex-1 h-6 bg-gray-100 rounded relative">
                        <div
                          className={`absolute h-full rounded ${getSpanTypeColor(span.span_type)} opacity-80`}
                          style={{
                            left: `${span.startOffset}%`,
                            width: `${span.width}%`,
                          }}
                        ></div>
                      </div>

                      {/* Quick Stats */}
                      <div className="w-32 flex-shrink-0 text-right text-sm text-gray-600">
                        {span.total_tokens && (
                          <div>{span.total_tokens.toLocaleString()} tokens</div>
                        )}
                        {span.cost && (
                          <div>{formatCost(span.cost)}</div>
                        )}
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {selectedSpan?.id === span.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200 bg-white rounded-lg p-4">
                        {/* Basic Info Row - Always shows */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div>
                            <div className="text-xs text-gray-500 uppercase tracking-wider">Type</div>
                            <div className="text-sm font-medium text-gray-900">{span.span_type}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 uppercase tracking-wider">Status</div>
                            <div className="text-sm font-medium text-gray-900">{span.status}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 uppercase tracking-wider">Duration</div>
                            <div className="text-sm font-medium text-gray-900">{formatDuration(span.duration_ms)}</div>
                          </div>
                          {span.model ? (
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider">Model</div>
                              <div className="text-sm font-medium text-gray-900">{span.model}</div>
                            </div>
                          ) : span.tool_name ? (
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider">Tool</div>
                              <div className="text-sm font-medium text-gray-900">{span.tool_name}</div>
                            </div>
                          ) : (
                            <div>
                              <div className="text-xs text-gray-500 uppercase tracking-wider">ID</div>
                              <div className="text-sm font-medium text-gray-900 truncate">{span.id.slice(0, 8)}...</div>
                            </div>
                          )}
                        </div>

                        {/* Token/Cost Info for LLM spans */}
                        {(span.provider || span.prompt_tokens || span.completion_tokens || span.cost) && (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                            {span.provider && (
                              <div>
                                <div className="text-xs text-gray-500">Provider</div>
                                <div className="text-sm font-semibold text-gray-900">{span.provider}</div>
                              </div>
                            )}
                            {span.prompt_tokens != null && (
                              <div>
                                <div className="text-xs text-gray-500">Prompt Tokens</div>
                                <div className="text-sm font-semibold text-gray-900">{span.prompt_tokens.toLocaleString()}</div>
                              </div>
                            )}
                            {span.completion_tokens != null && (
                              <div>
                                <div className="text-xs text-gray-500">Completion Tokens</div>
                                <div className="text-sm font-semibold text-gray-900">{span.completion_tokens.toLocaleString()}</div>
                              </div>
                            )}
                            {span.cost != null && (
                              <div>
                                <div className="text-xs text-gray-500">Cost</div>
                                <div className="text-sm font-semibold text-gray-900">{formatCost(span.cost)}</div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Input Section */}
                        <div className="mb-4">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Input</div>
                          <pre className="text-sm text-gray-900 bg-gray-100 p-3 rounded-lg overflow-x-auto max-h-48 border border-gray-300 whitespace-pre-wrap">
                            {span.input
                              ? (typeof parseJSON(span.input) === 'object'
                                ? JSON.stringify(parseJSON(span.input), null, 2)
                                : span.input)
                              : '(no input)'}
                          </pre>
                        </div>

                        {/* Output Section */}
                        <div className="mb-4">
                          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Output</div>
                          <pre className="text-sm text-gray-900 bg-gray-100 p-3 rounded-lg overflow-x-auto max-h-48 border border-gray-300 whitespace-pre-wrap">
                            {span.output
                              ? (typeof parseJSON(span.output) === 'object'
                                ? JSON.stringify(parseJSON(span.output), null, 2)
                                : span.output)
                              : '(no output)'}
                          </pre>
                        </div>

                        {/* Error Section */}
                        {span.error_message && (
                          <div>
                            <div className="text-xs text-red-600 uppercase tracking-wider mb-2">Error</div>
                            <pre className="text-xs bg-red-50 text-red-700 p-3 rounded-lg overflow-x-auto border border-red-200">
                              {span.error_message}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
