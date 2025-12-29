export default function Api() {
  return (
    <div className="docs-content">
      <h1>API Reference</h1>

      <p>
        The Quality Dashboard exposes a REST API for programmatic access to
        evaluation results.
      </p>

      <h2>Base URL</h2>

      <pre><code>{`http://localhost:8080/api`}</code></pre>

      <h2>Authentication</h2>

      <p>
        Currently, the API has no authentication. For production use, place it
        behind a reverse proxy with authentication.
      </p>

      <h2>Endpoints</h2>

      <h3>List Runs</h3>

      <pre><code>{`GET /api/runs`}</code></pre>

      <p>Query parameters:</p>

      <table>
        <thead>
          <tr>
            <th>Param</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>app_name</code></td>
            <td>string</td>
            <td>Filter by app name</td>
          </tr>
          <tr>
            <td><code>limit</code></td>
            <td>integer</td>
            <td>Number of runs (default: 50, max: 100)</td>
          </tr>
          <tr>
            <td><code>offset</code></td>
            <td>integer</td>
            <td>Pagination offset</td>
          </tr>
        </tbody>
      </table>

      <p>Response:</p>

      <pre><code>{`{
  "runs": [
    {
      "id": "uuid",
      "app_name": "my-chatbot",
      "app_type": "simple_chat",
      "eval_suite": "basic_chat",
      "dataset_size": 50,
      "passed": true,
      "started_at": "2024-01-15T10:30:00Z",
      "finished_at": "2024-01-15T10:32:00Z",
      "duration_seconds": 120.5,
      "git_branch": "main",
      "git_commit": "abc123",
      "created_at": "2024-01-15T10:32:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}`}</code></pre>

      <h3>Get Run Details</h3>

      <pre><code>{`GET /api/runs/{run_id}`}</code></pre>

      <p>Response:</p>

      <pre><code>{`{
  "id": "uuid",
  "app_name": "my-chatbot",
  "app_type": "simple_chat",
  "eval_suite": "basic_chat",
  "dataset_size": 50,
  "passed": true,
  "started_at": "2024-01-15T10:30:00Z",
  "finished_at": "2024-01-15T10:32:00Z",
  "duration_seconds": 120.5,
  "git_branch": "main",
  "git_commit": "abc123",
  "config_path": "eval_config.yaml",
  "metrics": [
    {
      "name": "user_frustration",
      "mean_score": 0.92,
      "failure_rate": 0.08,
      "threshold_type": "max",
      "threshold_value": 0.3,
      "passed": true
    }
  ],
  "test_cases": [
    {
      "id": 1,
      "conversation_id": "test-001",
      "input": "What's your return policy?",
      "output": "Our return policy...",
      "scores": [
        {
          "metric_name": "user_frustration",
          "score": 1.0,
          "label": "not_frustrated",
          "explanation": null
        }
      ],
      "failure": null
    }
  ]
}`}</code></pre>

      <h3>Create Run</h3>

      <pre><code>{`POST /api/runs`}</code></pre>

      <p>
        This endpoint is used internally by <code>ci-run --report-to</code>.
        Request body matches the full run structure.
      </p>

      <h3>Get Failure Summary</h3>

      <pre><code>{`GET /api/runs/{run_id}/failures/summary`}</code></pre>

      <p>Response:</p>

      <pre><code>{`{
  "total_failures": 8,
  "distribution": {
    "unhelpful_response": 4,
    "incomplete_answer": 3,
    "dismissive_tone": 1
  }
}`}</code></pre>

      <h3>Health Check</h3>

      <pre><code>{`GET /api/health`}</code></pre>

      <p>Response:</p>

      <pre><code>{`{
  "status": "healthy",
  "database": "eval_results.db"
}`}</code></pre>

      <h2>OpenAPI Spec</h2>

      <p>
        Interactive API documentation is available at:
      </p>

      <pre><code>{`http://localhost:8080/docs`}</code></pre>
    </div>
  )
}
