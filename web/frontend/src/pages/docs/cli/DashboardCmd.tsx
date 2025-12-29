export default function DashboardCmd() {
  return (
    <div className="docs-content">
      <h1>dashboard Command</h1>

      <p>
        The <code>dashboard</code> command starts the Quality Dashboard web server
        for viewing and tracking evaluation results.
      </p>

      <h2>Usage</h2>

      <pre><code>{`company-eval dashboard [options]`}</code></pre>

      <h2>Options</h2>

      <table>
        <thead>
          <tr>
            <th>Option</th>
            <th>Default</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>--port, -p</code></td>
            <td>8080</td>
            <td>Port to listen on</td>
          </tr>
          <tr>
            <td><code>--host</code></td>
            <td>0.0.0.0</td>
            <td>Host to bind to</td>
          </tr>
          <tr>
            <td><code>--db</code></td>
            <td>eval_results.db</td>
            <td>Path to SQLite database</td>
          </tr>
          <tr>
            <td><code>--reload</code></td>
            <td>false</td>
            <td>Enable auto-reload for development</td>
          </tr>
        </tbody>
      </table>

      <h2>Examples</h2>

      <h3>Basic Usage</h3>

      <pre><code>{`company-eval dashboard`}</code></pre>

      <h3>Custom Port</h3>

      <pre><code>{`company-eval dashboard --port 3000`}</code></pre>

      <h3>Custom Database Location</h3>

      <pre><code>{`company-eval dashboard --db /var/data/evals.db`}</code></pre>

      <h3>Development Mode</h3>

      <pre><code>{`company-eval dashboard --reload`}</code></pre>

      <h2>Installation</h2>

      <p>The dashboard requires additional dependencies:</p>

      <pre><code>{`pip install company-eval-framework[dashboard]`}</code></pre>

      <h2>Sending Results to Dashboard</h2>

      <p>Use the <code>--report-to</code> flag with <code>ci-run</code>:</p>

      <pre><code>{`# Terminal 1: Start dashboard
company-eval dashboard --port 8080

# Terminal 2: Run evaluation and report
company-eval ci-run --config eval.yaml --report-to http://localhost:8080`}</code></pre>

      <h2>Production Deployment</h2>

      <p>For production, consider:</p>

      <ul>
        <li>Running behind a reverse proxy (nginx, Caddy)</li>
        <li>Using a persistent database location</li>
        <li>Setting up authentication (not built-in yet)</li>
      </ul>

      <pre><code>{`# Production example
company-eval dashboard \\
  --host 127.0.0.1 \\
  --port 8080 \\
  --db /var/lib/company-eval/results.db`}</code></pre>

      <h2>Docker</h2>

      <pre><code>{`FROM python:3.11-slim
RUN pip install company-eval-framework[dashboard]
EXPOSE 8080
CMD ["company-eval", "dashboard", "--host", "0.0.0.0"]`}</code></pre>
    </div>
  )
}
