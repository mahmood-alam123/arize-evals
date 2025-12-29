import { Link } from 'react-router-dom'

export default function Dashboard() {
  return (
    <div className="docs-content">
      <h1>Quality Dashboard</h1>

      <p>
        The Quality Dashboard provides a web interface for viewing and tracking
        evaluation results over time.
      </p>

      <h2>Features</h2>

      <ul>
        <li><strong>Run History:</strong> View all evaluation runs with pass/fail status</li>
        <li><strong>Metrics Tracking:</strong> See metric scores and trends</li>
        <li><strong>Failure Analysis:</strong> Drill into individual failures</li>
        <li><strong>Git Integration:</strong> Track results by branch and commit</li>
      </ul>

      <h2>Quick Start</h2>

      <pre><code>{`# Install with dashboard support
pip install company-eval-framework[dashboard]

# Start the dashboard
company-eval dashboard --port 8080

# Run evaluation and report to dashboard
company-eval ci-run --config eval.yaml --report-to http://localhost:8080`}</code></pre>

      <h2>Dashboard Views</h2>

      <h3>Runs List</h3>

      <p>The main view shows all evaluation runs:</p>

      <ul>
        <li>Pass/Fail status badge</li>
        <li>App name and eval suite</li>
        <li>Dataset size and duration</li>
        <li>Git branch and commit</li>
        <li>Timestamp</li>
      </ul>

      <h3>Run Details</h3>

      <p>Click on a run to see detailed results:</p>

      <ul>
        <li><strong>Metrics Table:</strong> Score, threshold, and status for each metric</li>
        <li><strong>Failure Analysis:</strong> Distribution of failure types</li>
        <li><strong>Test Cases:</strong> Expandable list of all inputs/outputs with scores</li>
      </ul>

      <h2>API Access</h2>

      <p>
        The dashboard also exposes a REST API for programmatic access.
        See the <Link to="/docs/api">API Reference</Link>.
      </p>

      <h2>Data Storage</h2>

      <p>
        Results are stored in a SQLite database (default: <code>eval_results.db</code>).
        You can specify a different location:
      </p>

      <pre><code>{`company-eval dashboard --db /path/to/custom.db`}</code></pre>

      <h2>Filtering (Coming Soon)</h2>

      <p>Future versions will support filtering runs by:</p>

      <ul>
        <li>App name</li>
        <li>Date range</li>
        <li>Pass/Fail status</li>
        <li>Git branch</li>
      </ul>
    </div>
  )
}
