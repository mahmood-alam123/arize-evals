import { Routes, Route } from 'react-router-dom'
import RunsList from './pages/RunsList'
import RunDetails from './pages/RunDetails'

function App() {
  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>Company Eval Dashboard</h1>
        </div>
      </div>
      <div className="container">
        <Routes>
          <Route path="/" element={<RunsList />} />
          <Route path="/runs/:runId" element={<RunDetails />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
