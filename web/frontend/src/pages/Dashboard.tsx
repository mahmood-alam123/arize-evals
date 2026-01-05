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
  total_cost: number | null
  created_at: string
}

interface RunsResponse {
  runs: Run[]
  total: number
  limit: number
  offset: number
}

interface Integration {
  id: number
  integration_type: 'slack' | 'teams'
  webhook_url: string
  is_active: boolean
  notify_on_pass: boolean
  notify_on_fail: boolean
  created_at: string
  updated_at: string
}

interface IntegrationForm {
  integration_type: 'slack' | 'teams'
  webhook_url: string
  is_active: boolean
  notify_on_pass: boolean
  notify_on_fail: boolean
}

const defaultForm: IntegrationForm = {
  integration_type: 'slack',
  webhook_url: '',
  is_active: true,
  notify_on_pass: false,
  notify_on_fail: true,
}

export default function Dashboard() {
  const [runs, setRuns] = useState<Run[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  // Integration state
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [integrationsLoading, setIntegrationsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<IntegrationForm>(defaultForm)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchRuns()
    fetchIntegrations()
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

  const fetchIntegrations = async () => {
    try {
      const response = await fetch('/api/integrations')
      if (!response.ok) throw new Error('Failed to fetch integrations')
      const data: Integration[] = await response.json()
      setIntegrations(data)
    } catch (err) {
      console.error('Failed to fetch integrations:', err)
    } finally {
      setIntegrationsLoading(false)
    }
  }

  const openAddModal = () => {
    setEditingId(null)
    setForm(defaultForm)
    setShowModal(true)
  }

  const openEditModal = (integration: Integration) => {
    setEditingId(integration.id)
    setForm({
      integration_type: integration.integration_type,
      webhook_url: integration.webhook_url,
      is_active: integration.is_active,
      notify_on_pass: integration.notify_on_pass,
      notify_on_fail: integration.notify_on_fail,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingId(null)
    setForm(defaultForm)
  }

  const handleSave = async () => {
    if (!form.webhook_url.trim()) return
    setSaving(true)
    try {
      const url = editingId ? `/api/integrations/${editingId}` : '/api/integrations'
      const method = editingId ? 'PUT' : 'POST'
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!response.ok) throw new Error('Failed to save integration')
      await fetchIntegrations()
      closeModal()
    } catch (err) {
      console.error('Failed to save integration:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this integration?')) return
    try {
      const response = await fetch(`/api/integrations/${id}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to delete integration')
      await fetchIntegrations()
    } catch (err) {
      console.error('Failed to delete integration:', err)
    }
  }

  const handleToggle = async (integration: Integration) => {
    try {
      const response = await fetch(`/api/integrations/${integration.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !integration.is_active }),
      })
      if (!response.ok) throw new Error('Failed to update integration')
      await fetchIntegrations()
    } catch (err) {
      console.error('Failed to toggle integration:', err)
    }
  }

  const truncateUrl = (url: string) => {
    if (url.length <= 50) return url
    return url.substring(0, 47) + '...'
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

  const formatCost = (cost: number | null) => {
    if (cost === null || cost === undefined) return '-'
    if (cost < 0.01) return `$${cost.toFixed(4)}`
    return `$${cost.toFixed(2)}`
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

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Link to="/traces" className="light-card p-4 hover:bg-gray-50 transition-colors group">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center text-xl">
                  🔍
                </div>
                <div>
                  <div className="font-medium text-gray-900 group-hover:text-blue-600">Traces</div>
                  <div className="text-sm text-gray-500">Monitor LLM calls & tool usage</div>
                </div>
              </div>
            </Link>
            <Link to="/compare" className="light-card p-4 hover:bg-gray-50 transition-colors group">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center text-xl">
                  ⚖️
                </div>
                <div>
                  <div className="font-medium text-gray-900 group-hover:text-blue-600">Compare Runs</div>
                  <div className="text-sm text-gray-500">Side-by-side metric comparison</div>
                </div>
              </div>
            </Link>
            <Link to="/datasets" className="light-card p-4 hover:bg-gray-50 transition-colors group">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 text-green-600 flex items-center justify-center text-xl">
                  📊
                </div>
                <div>
                  <div className="font-medium text-gray-900 group-hover:text-blue-600">Datasets</div>
                  <div className="text-sm text-gray-500">Manage evaluation datasets</div>
                </div>
              </div>
            </Link>
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
                      <th>Cost</th>
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
                          <span className="text-gray-600 font-mono">{formatCost(run.total_cost)}</span>
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

          {/* Integrations Section */}
          <div className="light-card mt-8">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Integrations</h2>
                <p className="text-sm text-gray-500">Configure Slack or Teams notifications for evaluation results</p>
              </div>
              <button
                onClick={openAddModal}
                className="inline-flex items-center px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Integration
              </button>
            </div>

            {integrationsLoading ? (
              <div className="p-12 text-center text-gray-500">
                <div className="inline-block w-6 h-6 border-2 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-3" />
                <p>Loading integrations...</p>
              </div>
            ) : integrations.length === 0 ? (
              <div className="p-12 text-center">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
                <p className="text-gray-500 mb-2">No integrations configured</p>
                <p className="text-gray-400 text-sm">Add a Slack or Teams webhook to receive notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {integrations.map(integration => (
                  <div key={integration.id} className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Icon */}
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        integration.integration_type === 'slack'
                          ? 'bg-purple-100'
                          : 'bg-blue-100'
                      }`}>
                        {integration.integration_type === 'slack' ? (
                          <svg className="w-5 h-5 text-purple-600" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19.404 6.65l-5.998-5.608c-.672-.663-1.573-1.042-2.518-1.042H5.252c-1.666 0-3.02 1.372-3.02 3.061v17.878c0 1.689 1.354 3.061 3.02 3.061h13.496c1.666 0 3.02-1.372 3.02-3.061V9.192c0-.964-.37-1.873-1.046-2.542zm-6.04-4.176c.232.077.443.19.624.363l5.998 5.608c.163.161.286.353.381.559h-5.002c-1.105 0-2.001-.907-2.001-2.026V2.474zm5.584 19.526H5.252c-.553 0-1.002-.459-1.002-1.02V3.061c0-.561.449-1.02 1.002-1.02h5.89v4.463c0 2.22 1.793 4.026 4.001 4.026h5.095v10.409c0 .561-.449 1.02-1.002 1.02zm-10.52-7.77v5.312h2.188v-2.04l1.313 2.04h2.438l-1.688-2.312c.854-.298 1.438-1.074 1.438-2.063 0-1.191-.98-2.156-2.188-2.156H8.428v1.219zm2.188-.5c.479 0 .868.39.868.871 0 .481-.389.871-.868.871H9.615v-1.742h.601z"/>
                          </svg>
                        )}
                      </div>
                      {/* Details */}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900 capitalize">
                            {integration.integration_type === 'teams' ? 'Microsoft Teams' : 'Slack'}
                          </span>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                            integration.is_active
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {integration.is_active ? 'Active' : 'Disabled'}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500 font-mono">{truncateUrl(integration.webhook_url)}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          Notify on: {[
                            integration.notify_on_fail && 'Failures',
                            integration.notify_on_pass && 'Passes'
                          ].filter(Boolean).join(', ') || 'Nothing'}
                        </div>
                      </div>
                    </div>
                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {/* Toggle */}
                      <button
                        onClick={() => handleToggle(integration)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          integration.is_active ? 'bg-blue-600' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            integration.is_active ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                      {/* Edit */}
                      <button
                        onClick={() => openEditModal(integration)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                      {/* Delete */}
                      <button
                        onClick={() => handleDelete(integration.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Add/Edit Integration Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/50" onClick={closeModal} />

            {/* Modal */}
            <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  {editingId ? 'Edit Integration' : 'Add Integration'}
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                {/* Integration Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="type"
                        checked={form.integration_type === 'slack'}
                        onChange={() => setForm({ ...form, integration_type: 'slack' })}
                        className="w-4 h-4 text-blue-600"
                        disabled={!!editingId}
                      />
                      <span className="text-gray-700">Slack</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="type"
                        checked={form.integration_type === 'teams'}
                        onChange={() => setForm({ ...form, integration_type: 'teams' })}
                        className="w-4 h-4 text-blue-600"
                        disabled={!!editingId}
                      />
                      <span className="text-gray-700">Microsoft Teams</span>
                    </label>
                  </div>
                </div>

                {/* Webhook URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Webhook URL</label>
                  <input
                    type="url"
                    value={form.webhook_url}
                    onChange={(e) => setForm({ ...form, webhook_url: e.target.value })}
                    placeholder={form.integration_type === 'slack'
                      ? 'https://hooks.slack.com/services/...'
                      : 'https://outlook.office.com/webhook/...'
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Notification Triggers */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notify when</label>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={form.notify_on_fail}
                        onChange={(e) => setForm({ ...form, notify_on_fail: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded"
                      />
                      <span className="text-gray-700">Evaluation fails</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={form.notify_on_pass}
                        onChange={(e) => setForm({ ...form, notify_on_pass: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded"
                      />
                      <span className="text-gray-700">Evaluation passes</span>
                    </label>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving || !form.webhook_url.trim()}
                  className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
