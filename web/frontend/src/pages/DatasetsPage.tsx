import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/Header'

interface DatasetExample {
  id: number
  input: string
  expected_output: string | null
  context: string | null
  metadata: string | null
}

interface Dataset {
  id: string
  name: string
  description: string | null
  app_type: string | null
  num_examples: number
  source: string | null
  source_run_id: string | null
  generation_config: string | null
  created_at: string
  updated_at: string
  examples?: DatasetExample[]
}

interface Run {
  id: string
  app_name: string
  app_type: string
  started_at: string
  dataset_size: number
  passed: boolean
}

interface FailureStat {
  failure_type: string
  count: number
  app_names: string[]
}

interface DatasetsResponse {
  datasets: Dataset[]
  total: number
}

interface RunsResponse {
  runs: Run[]
  total: number
}

interface FailureStatsResponse {
  stats: FailureStat[]
}

type ModalType = 'upload' | 'fromRun' | 'generate' | 'fromFailures' | null

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null)
  const [activeModal, setActiveModal] = useState<ModalType>(null)
  const [submitting, setSubmitting] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Data for modals
  const [runs, setRuns] = useState<Run[]>([])
  const [failureStats, setFailureStats] = useState<FailureStat[]>([])

  // Upload form state
  const [uploadName, setUploadName] = useState('')
  const [uploadDescription, setUploadDescription] = useState('')
  const [uploadAppType, setUploadAppType] = useState('')
  const [uploadFile, setUploadFile] = useState<File | null>(null)

  // From Run form state
  const [fromRunId, setFromRunId] = useState('')
  const [fromRunName, setFromRunName] = useState('')
  const [fromRunDescription, setFromRunDescription] = useState('')
  const [fromRunFailuresOnly, setFromRunFailuresOnly] = useState(false)

  // Generate form state
  const [generateName, setGenerateName] = useState('')
  const [generateDescription, setGenerateDescription] = useState('')
  const [generateAppType, setGenerateAppType] = useState('simple_chat')
  const [generateNumExamples, setGenerateNumExamples] = useState(20)
  const [generateAppDescription, setGenerateAppDescription] = useState('')

  // From Failures form state
  const [failuresName, setFailuresName] = useState('')
  const [failuresDescription, setFailuresDescription] = useState('')
  const [failuresAppName, setFailuresAppName] = useState('')
  const [failuresTypes, setFailuresTypes] = useState<string[]>([])
  const [failuresNumPerType, setFailuresNumPerType] = useState(5)

  useEffect(() => {
    fetchDatasets()
  }, [])

  const fetchDatasets = async () => {
    try {
      const response = await fetch('/api/datasets')
      if (!response.ok) throw new Error('Failed to fetch datasets')
      const data: DatasetsResponse = await response.json()
      setDatasets(data.datasets)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fetchRuns = async () => {
    try {
      const response = await fetch('/api/runs?limit=50')
      if (!response.ok) throw new Error('Failed to fetch runs')
      const data: RunsResponse = await response.json()
      setRuns(data.runs)
    } catch (err) {
      console.error('Failed to fetch runs:', err)
    }
  }

  const fetchFailureStats = async () => {
    try {
      const response = await fetch('/api/datasets/failure-stats')
      if (!response.ok) throw new Error('Failed to fetch failure stats')
      const data: FailureStatsResponse = await response.json()
      setFailureStats(data.stats)
    } catch (err) {
      console.error('Failed to fetch failure stats:', err)
    }
  }

  const fetchDatasetDetails = async (id: string) => {
    try {
      const response = await fetch(`/api/datasets/${id}`)
      if (!response.ok) throw new Error('Failed to fetch dataset')
      const data: Dataset = await response.json()
      setSelectedDataset(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const openModal = (type: ModalType) => {
    setActiveModal(type)
    setShowDropdown(false)
    if (type === 'fromRun') fetchRuns()
    if (type === 'fromFailures') fetchFailureStats()
  }

  const closeModal = () => {
    setActiveModal(null)
    // Reset all form states
    setUploadName('')
    setUploadDescription('')
    setUploadAppType('')
    setUploadFile(null)
    setFromRunId('')
    setFromRunName('')
    setFromRunDescription('')
    setFromRunFailuresOnly(false)
    setGenerateName('')
    setGenerateDescription('')
    setGenerateAppType('simple_chat')
    setGenerateNumExamples(20)
    setGenerateAppDescription('')
    setFailuresName('')
    setFailuresDescription('')
    setFailuresAppName('')
    setFailuresTypes([])
    setFailuresNumPerType(5)
  }

  const handleUpload = async () => {
    if (!uploadFile || !uploadName) return
    setSubmitting(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', uploadFile)

      const params = new URLSearchParams()
      params.set('name', uploadName)
      if (uploadDescription) params.set('description', uploadDescription)
      if (uploadAppType) params.set('app_type', uploadAppType)

      const response = await fetch(`/api/datasets/upload?${params}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Upload failed')
      }

      closeModal()
      fetchDatasets()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleFromRun = async () => {
    if (!fromRunId || !fromRunName) return
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch('/api/datasets/from-run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: fromRunId,
          name: fromRunName,
          description: fromRunDescription || undefined,
          include_failures_only: fromRunFailuresOnly,
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Import failed')
      }

      closeModal()
      fetchDatasets()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleGenerate = async () => {
    if (!generateName) return
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch('/api/datasets/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: generateName,
          description: generateDescription || undefined,
          app_type: generateAppType,
          num_examples: generateNumExamples,
          generation_config: {
            model: 'gpt-4o-mini',
            app_description: generateAppDescription || undefined,
            example_inputs: [],
            temperature: 0.9,
          },
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Generation failed')
      }

      closeModal()
      fetchDatasets()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleFromFailures = async () => {
    if (!failuresName) return
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch('/api/datasets/from-failures', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: failuresName,
          description: failuresDescription || undefined,
          app_name: failuresAppName || undefined,
          failure_types: failuresTypes,
          num_examples_per_type: failuresNumPerType,
          model: 'gpt-4o-mini',
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Creation failed')
      }

      closeModal()
      fetchDatasets()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Creation failed')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this dataset?')) return

    try {
      const response = await fetch(`/api/datasets/${id}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to delete dataset')

      if (selectedDataset?.id === id) {
        setSelectedDataset(null)
      }
      fetchDatasets()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const handleExport = (id: string, name: string) => {
    window.open(`/api/datasets/${id}/export`, '_blank')
  }

  const copyYamlSnippet = (name: string) => {
    const yaml = `dataset:
  mode: "dashboard"
  dataset_name: "${name}"`
    navigator.clipboard.writeText(yaml)
    alert('YAML snippet copied to clipboard!')
  }

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString()
  }

  const getAppTypeColor = (type: string | null) => {
    switch (type) {
      case 'simple_chat': return 'bg-blue-100 text-blue-800'
      case 'rag': return 'bg-purple-100 text-purple-800'
      case 'agent': return 'bg-orange-100 text-orange-800'
      case 'multi_agent': return 'bg-pink-100 text-pink-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getSourceBadge = (source: string | null) => {
    switch (source) {
      case 'upload': return { label: 'Uploaded', color: 'bg-gray-100 text-gray-700' }
      case 'run_import': return { label: 'From Run', color: 'bg-green-100 text-green-700' }
      case 'synthetic': return { label: 'Synthetic', color: 'bg-blue-100 text-blue-700' }
      case 'failure_analysis': return { label: 'Failures', color: 'bg-amber-100 text-amber-700' }
      default: return null
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header variant="light" />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-gray-500">Loading datasets...</div>
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
              <h1 className="text-2xl font-bold text-gray-900">Datasets</h1>
              <p className="text-gray-600 mt-1">Manage evaluation datasets</p>
            </div>
            <div className="flex items-center gap-4">
              {/* Create Dataset Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <span>+ Create Dataset</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                    <button
                      onClick={() => openModal('upload')}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                      </svg>
                      Upload JSONL
                    </button>
                    <button
                      onClick={() => openModal('fromRun')}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                      Import from Run
                    </button>
                    <button
                      onClick={() => openModal('generate')}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Generate Synthetic
                    </button>
                    <button
                      onClick={() => openModal('fromFailures')}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      From Failure Patterns
                    </button>
                  </div>
                )}
              </div>
              <Link
                to="/dashboard"
                className="text-gray-600 hover:text-gray-900 flex items-center gap-2"
              >
                <span>← Back to Dashboard</span>
              </Link>
            </div>
          </div>

          {error && (
            <div className="light-card p-4 mb-6 border-l-4 border-red-500">
              <p className="text-red-700">{error}</p>
              <button onClick={() => setError(null)} className="text-sm text-red-500 underline mt-1">
                Dismiss
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Dataset List */}
            <div className="lg:col-span-1">
              <div className="light-card">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-medium text-gray-900">{datasets.length} Datasets</h3>
                </div>

                {datasets.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    No datasets yet. Create one to get started.
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {datasets.map((dataset) => {
                      const sourceBadge = getSourceBadge(dataset.source)
                      return (
                        <div
                          key={dataset.id}
                          className={`p-4 cursor-pointer hover:bg-gray-50 ${selectedDataset?.id === dataset.id ? 'bg-blue-50' : ''}`}
                          onClick={() => fetchDatasetDetails(dataset.id)}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <div className="font-medium text-gray-900">{dataset.name}</div>
                            {dataset.app_type && (
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getAppTypeColor(dataset.app_type)}`}>
                                {dataset.app_type}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-500">
                            <span>{dataset.num_examples} examples</span>
                            {sourceBadge && (
                              <span className={`px-1.5 py-0.5 rounded text-xs ${sourceBadge.color}`}>
                                {sourceBadge.label}
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Dataset Details */}
            <div className="lg:col-span-2">
              {selectedDataset ? (
                <div className="light-card">
                  <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{selectedDataset.name}</h3>
                      {selectedDataset.description && (
                        <p className="text-sm text-gray-600 mt-1">{selectedDataset.description}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => copyYamlSnippet(selectedDataset.name)}
                        className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                        title="Copy YAML snippet"
                      >
                        Copy YAML
                      </button>
                      <button
                        onClick={() => handleExport(selectedDataset.id, selectedDataset.name)}
                        className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded"
                      >
                        Export
                      </button>
                      <button
                        onClick={() => handleDelete(selectedDataset.id)}
                        className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  <div className="p-4 border-b border-gray-200">
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-500">Examples</div>
                        <div className="font-medium">{selectedDataset.num_examples}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">App Type</div>
                        <div className="font-medium">{selectedDataset.app_type || '-'}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Source</div>
                        <div className="font-medium">{getSourceBadge(selectedDataset.source)?.label || 'Unknown'}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Created</div>
                        <div className="font-medium">{formatTime(selectedDataset.created_at)}</div>
                      </div>
                    </div>
                    {selectedDataset.source_run_id && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <Link
                          to={`/runs/${selectedDataset.source_run_id}`}
                          className="text-sm text-blue-600 hover:underline"
                        >
                          View source run →
                        </Link>
                      </div>
                    )}
                  </div>

                  {/* Examples */}
                  <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
                    {selectedDataset.examples?.map((example, idx) => (
                      <div key={example.id} className="p-4">
                        <div className="text-xs text-gray-500 mb-2">Example #{idx + 1}</div>
                        <div className="space-y-2">
                          <div>
                            <div className="text-xs font-medium text-gray-600">Input</div>
                            <div className="text-sm bg-gray-50 p-2 rounded mt-1">{example.input}</div>
                          </div>
                          {example.expected_output && (
                            <div>
                              <div className="text-xs font-medium text-gray-600">Expected Output</div>
                              <div className="text-sm bg-gray-50 p-2 rounded mt-1">{example.expected_output}</div>
                            </div>
                          )}
                          {example.context && (
                            <div>
                              <div className="text-xs font-medium text-gray-600">Context</div>
                              <div className="text-sm bg-gray-50 p-2 rounded mt-1 max-h-20 overflow-y-auto">{example.context}</div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="light-card p-12 text-center">
                  <div className="text-gray-400 text-lg mb-2">Select a dataset</div>
                  <p className="text-gray-500 text-sm">
                    Click on a dataset to view its examples
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Upload Modal */}
      {activeModal === 'upload' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Dataset</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="my-dataset"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional description"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">App Type</label>
                <select
                  value={uploadAppType}
                  onChange={(e) => setUploadAppType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select type...</option>
                  <option value="simple_chat">Simple Chat</option>
                  <option value="rag">RAG</option>
                  <option value="agent">Agent</option>
                  <option value="multi_agent">Multi-Agent</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">JSONL File *</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".jsonl"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={closeModal} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button
                onClick={handleUpload}
                disabled={!uploadName || !uploadFile || submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import from Run Modal */}
      {activeModal === 'fromRun' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Import from Run</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select Run *</label>
                <select
                  value={fromRunId}
                  onChange={(e) => setFromRunId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a run...</option>
                  {runs.map((run) => (
                    <option key={run.id} value={run.id}>
                      {run.app_name} - {new Date(run.started_at).toLocaleDateString()} ({run.dataset_size} tests, {run.passed ? 'passed' : 'failed'})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dataset Name *</label>
                <input
                  type="text"
                  value={fromRunName}
                  onChange={(e) => setFromRunName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="imported-dataset"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={fromRunDescription}
                  onChange={(e) => setFromRunDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional description"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="failuresOnly"
                  checked={fromRunFailuresOnly}
                  onChange={(e) => setFromRunFailuresOnly(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <label htmlFor="failuresOnly" className="text-sm text-gray-700">Include only failed test cases</label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={closeModal} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button
                onClick={handleFromRun}
                disabled={!fromRunId || !fromRunName || submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Importing...' : 'Import'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generate Synthetic Modal */}
      {activeModal === 'generate' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Synthetic Dataset</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dataset Name *</label>
                <input
                  type="text"
                  value={generateName}
                  onChange={(e) => setGenerateName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="synthetic-dataset"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">App Type *</label>
                <select
                  value={generateAppType}
                  onChange={(e) => setGenerateAppType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="simple_chat">Simple Chat</option>
                  <option value="rag">RAG</option>
                  <option value="agent">Agent</option>
                  <option value="multi_agent">Multi-Agent</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Number of Examples: {generateNumExamples}</label>
                <input
                  type="range"
                  min="5"
                  max="100"
                  value={generateNumExamples}
                  onChange={(e) => setGenerateNumExamples(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">App Description</label>
                <textarea
                  value={generateAppDescription}
                  onChange={(e) => setGenerateAppDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Describe your app for better generation..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={closeModal} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button
                onClick={handleGenerate}
                disabled={!generateName || submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* From Failures Modal */}
      {activeModal === 'fromFailures' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create from Failure Patterns</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dataset Name *</label>
                <input
                  type="text"
                  value={failuresName}
                  onChange={(e) => setFailuresName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="failure-focused-dataset"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Failure Types</label>
                <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-2">
                  {failureStats.length === 0 ? (
                    <p className="text-sm text-gray-500">No failures found in runs</p>
                  ) : (
                    failureStats.map((stat) => (
                      <label key={stat.failure_type} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={failuresTypes.includes(stat.failure_type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFailuresTypes([...failuresTypes, stat.failure_type])
                            } else {
                              setFailuresTypes(failuresTypes.filter((t) => t !== stat.failure_type))
                            }
                          }}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm">{stat.failure_type} ({stat.count})</span>
                      </label>
                    ))
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Examples per Type: {failuresNumPerType}</label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  value={failuresNumPerType}
                  onChange={(e) => setFailuresNumPerType(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={closeModal} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
              <button
                onClick={handleFromFailures}
                disabled={!failuresName || submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Click outside dropdown to close */}
      {showDropdown && (
        <div className="fixed inset-0 z-0" onClick={() => setShowDropdown(false)} />
      )}
    </div>
  )
}
