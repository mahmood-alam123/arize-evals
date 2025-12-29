export default function Config() {
  return (
    <div className="docs-content">
      <h1>Configuration File</h1>

      <p>
        Company Eval uses YAML configuration files to define evaluations. This page documents
        all available configuration options.
      </p>

      <h2>Complete Example</h2>

      <pre><code>{`# eval_config.yaml
app_name: my-rag-app
app_type: rag

adapter:
  module: my_app.eval_adapter
  function: run_rag_batch

dataset:
  mode: static
  path: tests/rag_dataset.jsonl
  size: 100  # Optional: limit dataset size

eval_suite: basic_rag

thresholds:
  hallucination:
    max_mean: 0.1
  document_relevance:
    min_mean: 0.8
  answer_quality:
    min_mean: 0.7`}</code></pre>

      <h2>Top-Level Options</h2>

      <table>
        <thead>
          <tr>
            <th>Field</th>
            <th>Type</th>
            <th>Required</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>app_name</code></td>
            <td>string</td>
            <td>Yes</td>
            <td>Name of your application (used in dashboard)</td>
          </tr>
          <tr>
            <td><code>app_type</code></td>
            <td>string</td>
            <td>Yes</td>
            <td>One of: simple_chat, rag, agent, multi_agent</td>
          </tr>
          <tr>
            <td><code>adapter</code></td>
            <td>object</td>
            <td>Yes</td>
            <td>Adapter configuration (see below)</td>
          </tr>
          <tr>
            <td><code>dataset</code></td>
            <td>object</td>
            <td>Yes</td>
            <td>Dataset configuration (see below)</td>
          </tr>
          <tr>
            <td><code>eval_suite</code></td>
            <td>string</td>
            <td>Yes</td>
            <td>Evaluation suite to use</td>
          </tr>
          <tr>
            <td><code>thresholds</code></td>
            <td>object</td>
            <td>No</td>
            <td>Pass/fail thresholds per metric</td>
          </tr>
        </tbody>
      </table>

      <h2>Adapter Configuration</h2>

      <p>The adapter runs your LLM application on test inputs:</p>

      <pre><code>{`adapter:
  module: my_app.eval_adapter    # Python module path
  function: run_batch            # Function name`}</code></pre>

      <p>Your adapter function must have this signature:</p>

      <pre><code>{`def run_batch(input_path: str, output_path: str) -> None:
    """
    Read inputs from input_path (JSONL), run your app,
    write outputs to output_path (JSONL).
    """
    pass`}</code></pre>

      <h2>Dataset Configuration</h2>

      <h3>Static Dataset</h3>

      <pre><code>{`dataset:
  mode: static
  path: tests/eval_data.jsonl
  size: 50  # Optional: limit to first N rows`}</code></pre>

      <h3>Synthetic Dataset</h3>

      <pre><code>{`dataset:
  mode: synthetic
  num_examples: 20
  generation_model: gpt-4o-mini
  description: "Customer support chatbot for a SaaS product"`}</code></pre>

      <h2>Threshold Configuration</h2>

      <p>Thresholds define pass/fail criteria for each metric:</p>

      <pre><code>{`thresholds:
  metric_name:
    min_mean: 0.7    # Mean score must be >= 0.7
    # OR
    max_mean: 0.3    # Mean score must be <= 0.3`}</code></pre>

      <p>Examples:</p>

      <pre><code>{`thresholds:
  # For "good" metrics (higher is better)
  helpfulness_quality:
    min_mean: 0.7

  # For "bad" metrics (lower is better)
  user_frustration:
    max_mean: 0.3
  toxicity:
    max_mean: 0.05
  hallucination:
    max_mean: 0.1`}</code></pre>

      <h2>Available Eval Suites</h2>

      <table>
        <thead>
          <tr>
            <th>Suite</th>
            <th>Metrics</th>
            <th>For App Type</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>basic_chat</code></td>
            <td>user_frustration, helpfulness_quality, toxicity</td>
            <td>simple_chat</td>
          </tr>
          <tr>
            <td><code>basic_rag</code></td>
            <td>hallucination, document_relevance, answer_quality</td>
            <td>rag</td>
          </tr>
          <tr>
            <td><code>agent</code></td>
            <td>planning_quality, tool_use_appropriateness</td>
            <td>agent</td>
          </tr>
          <tr>
            <td><code>multi_agent</code></td>
            <td>overall_answer_quality, planning_quality</td>
            <td>multi_agent</td>
          </tr>
        </tbody>
      </table>

      <h2>Environment Variables</h2>

      <p>Config values can reference environment variables:</p>

      <pre><code>{`dataset:
  path: \${EVAL_DATASET_PATH}

# Set via environment
export EVAL_DATASET_PATH=tests/prod_sample.jsonl`}</code></pre>
    </div>
  )
}
