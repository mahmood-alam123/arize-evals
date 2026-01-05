import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import RunDetails from './pages/RunDetails'
import Traces from './pages/Traces'
import TraceDetails from './pages/TraceDetails'
import Compare from './pages/Compare'
import DatasetsPage from './pages/DatasetsPage'
import DocsLayout from './components/DocsLayout'

// Docs pages - Getting Started
import Introduction from './pages/docs/Introduction'
import Quickstart from './pages/docs/Quickstart'
import Installation from './pages/docs/Installation'

// Docs pages - Core Concepts
import HowItWorks from './pages/docs/HowItWorks'
import Tracing from './pages/docs/Tracing'
import Metrics from './pages/docs/Metrics'
import FailureAnalysis from './pages/docs/FailureAnalysis'

// Docs pages - Guides
import UseCaseChat from './pages/docs/use-cases/Chat'
import UseCaseRAG from './pages/docs/use-cases/RAG'
import UseCaseAgents from './pages/docs/use-cases/Agents'
import CustomEvaluators from './pages/docs/CustomEvaluators'

// Docs pages - Tools & Integration
import SDK from './pages/docs/SDK'
import CiRun from './pages/docs/cli/CiRun'
import CICD from './pages/docs/CICD'
import DashboardDocs from './pages/docs/Dashboard'

// Docs pages - Reference
import Config from './pages/docs/Config'
import Api from './pages/docs/Api'
import Integrations from './pages/docs/Integrations'

function App() {
  return (
    <Routes>
      {/* Landing page */}
      <Route path="/" element={<Landing />} />

      {/* Dashboard */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/runs/:runId" element={<RunDetails />} />
      <Route path="/compare" element={<Compare />} />
      <Route path="/traces" element={<Traces />} />
      <Route path="/traces/:traceId" element={<TraceDetails />} />
      <Route path="/datasets" element={<DatasetsPage />} />

      {/* Docs with sidebar layout */}
      <Route path="/docs" element={<DocsLayout />}>
        {/* Getting Started */}
        <Route index element={<Introduction />} />
        <Route path="quickstart" element={<Quickstart />} />
        <Route path="installation" element={<Installation />} />

        {/* Core Concepts */}
        <Route path="how-it-works" element={<HowItWorks />} />
        <Route path="tracing" element={<Tracing />} />
        <Route path="metrics" element={<Metrics />} />
        <Route path="failure-analysis" element={<FailureAnalysis />} />

        {/* Guides */}
        <Route path="use-cases/chat" element={<UseCaseChat />} />
        <Route path="use-cases/rag" element={<UseCaseRAG />} />
        <Route path="use-cases/agents" element={<UseCaseAgents />} />
        <Route path="custom-evaluators" element={<CustomEvaluators />} />

        {/* Tools & Integration */}
        <Route path="sdk" element={<SDK />} />
        <Route path="cli/ci-run" element={<CiRun />} />
        <Route path="cicd" element={<CICD />} />
        <Route path="dashboard" element={<DashboardDocs />} />

        {/* Reference */}
        <Route path="config" element={<Config />} />
        <Route path="api" element={<Api />} />
        <Route path="integrations" element={<Integrations />} />
      </Route>
    </Routes>
  )
}

export default App
