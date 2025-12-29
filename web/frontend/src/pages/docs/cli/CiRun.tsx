export default function CiRun() {
  return (
    <div className="docs-content">
      <h1>ci-run Command</h1>

      <p>
        The <code>ci-run</code> command runs your evaluation pipeline and returns an
        exit code suitable for CI/CD integration.
      </p>

      <h2>Usage</h2>

      <pre><code>{`company-eval ci-run --config <path-to-config.yaml> [options]`}</code></pre>

      <h2>Arguments</h2>

      <table>
        <thead>
          <tr>
            <th>Argument</th>
            <th>Required</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>--config</code></td>
            <td>Yes</td>
            <td>Path to your evaluation config YAML file</td>
          </tr>
          <tr>
            <td><code>--report-to</code></td>
            <td>No</td>
            <td>Dashboard URL to report results to</td>
          </tr>
        </tbody>
      </table>

      <h2>Exit Codes</h2>

      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Meaning</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>0</code></td>
            <td>All metrics passed their thresholds</td>
          </tr>
          <tr>
            <td><code>1</code></td>
            <td>One or more metrics failed their thresholds</td>
          </tr>
        </tbody>
      </table>

      <h2>Examples</h2>

      <h3>Basic Usage</h3>

      <pre><code>{`company-eval ci-run --config eval_config.yaml`}</code></pre>

      <h3>Report to Dashboard</h3>

      <pre><code>{`company-eval ci-run --config eval_config.yaml --report-to http://localhost:8080`}</code></pre>

      <h3>In CI Pipeline</h3>

      <pre><code>{`# GitHub Actions
- name: Run LLM Evaluation
  run: |
    company-eval ci-run --config eval_config.yaml
  env:
    OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`}</code></pre>

      <pre><code>{`# GitLab CI
test:llm-eval:
  script:
    - pip install company-eval-framework
    - company-eval ci-run --config eval_config.yaml
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY`}</code></pre>

      <h2>Output Format</h2>

      <pre><code>{`======================================================================
  LLM EVALUATION PIPELINE
======================================================================

App Name: my-chatbot
App Type: simple_chat
Eval Suite: basic_chat
Dataset Size: 50 rows (static)

Running adapter: my_app.eval_adapter.run_batch
  Adapter completed successfully
  Loaded 50 model outputs

Running evaluations...
  user_frustration: 50/50 complete
  helpfulness_quality: 50/50 complete
  toxicity: 50/50 complete

--------------------------------------------------
  Metric Summary (Mean Scores)
--------------------------------------------------
Metric                     Mean     Threshold       Status
------------------------------------------------------------
user_frustration           0.08     <= 0.30          PASS
helpfulness_quality        0.92     >= 0.70          PASS
toxicity                   0.00     <= 0.05          PASS

All metrics satisfy their thresholds.

--------------------------------------------------
  FINAL RESULT: PASS
--------------------------------------------------`}</code></pre>

      <h2>Environment Variables</h2>

      <table>
        <thead>
          <tr>
            <th>Variable</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>OPENAI_API_KEY</code></td>
            <td>Required. Your OpenAI API key.</td>
          </tr>
          <tr>
            <td><code>EVAL_DASHBOARD_URL</code></td>
            <td>Alternative to --report-to flag</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
