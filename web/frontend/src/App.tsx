import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import RunDetails from './pages/RunDetails'
import DocsLayout from './components/DocsLayout'

// Docs pages
import Introduction from './pages/docs/Introduction'
import Quickstart from './pages/docs/Quickstart'
import Installation from './pages/docs/Installation'
import Config from './pages/docs/Config'
import AppTypes from './pages/docs/AppTypes'
import Datasets from './pages/docs/Datasets'
import Thresholds from './pages/docs/Thresholds'
import EvalSuites from './pages/docs/EvalSuites'
import CustomEvaluators from './pages/docs/CustomEvaluators'
import FailureAnalysis from './pages/docs/FailureAnalysis'
import CiRun from './pages/docs/cli/CiRun'
import DashboardCmd from './pages/docs/cli/DashboardCmd'
import DashboardDocs from './pages/docs/Dashboard'
import Api from './pages/docs/Api'

function App() {
  return (
    <Routes>
      {/* Landing page */}
      <Route path="/" element={<Landing />} />

      {/* Dashboard */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/runs/:runId" element={<RunDetails />} />

      {/* Docs with sidebar layout */}
      <Route path="/docs" element={<DocsLayout />}>
        <Route index element={<Introduction />} />
        <Route path="quickstart" element={<Quickstart />} />
        <Route path="installation" element={<Installation />} />
        <Route path="config" element={<Config />} />
        <Route path="app-types" element={<AppTypes />} />
        <Route path="datasets" element={<Datasets />} />
        <Route path="thresholds" element={<Thresholds />} />
        <Route path="eval-suites" element={<EvalSuites />} />
        <Route path="custom-evaluators" element={<CustomEvaluators />} />
        <Route path="failure-analysis" element={<FailureAnalysis />} />
        <Route path="cli/ci-run" element={<CiRun />} />
        <Route path="cli/dashboard" element={<DashboardCmd />} />
        <Route path="dashboard" element={<DashboardDocs />} />
        <Route path="api" element={<Api />} />
      </Route>
    </Routes>
  )
}

export default App
