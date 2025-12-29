import { Link } from 'react-router-dom'

export default function Quickstart() {
  return (
    <div className="docs-content">
      <h1>Quickstart</h1>

      <p>
        Get your first LLM evaluation running in under 5 minutes. This guide walks you through
        installing Company Eval, creating a config file, and running your first evaluation.
      </p>

      <h2>Prerequisites</h2>

      <ul>
        <li>Python 3.9 or higher</li>
        <li>An OpenAI API key (for LLM-based evaluation)</li>
        <li>Your LLM application code</li>
      </ul>

      <h2>Step 1: Install the Framework</h2>

      <pre><code>{`pip install company-eval-framework

# Or install from source
git clone https://github.com/mahmood-alam123/arize-evals.git
cd arize-evals/eval_framework
pip install -e .`}</code></pre>

      <h2>Step 2: Set Your API Key</h2>

      <pre><code>{`export OPENAI_API_KEY=your-api-key-here`}</code></pre>

      <h2>Step 3: Create a Config File</h2>

      <p>Create a file called <code>eval_config.yaml</code>:</p>

      <pre><code>{`# eval_config.yaml
app_name: my-chatbot
app_type: simple_chat

adapter:
  module: my_app.eval_adapter
  function: run_batch

dataset:
  mode: static
  path: tests/eval_data.jsonl

eval_suite: basic_chat

thresholds:
  user_frustration:
    max_mean: 0.3      # Max 30% frustration rate
  helpfulness_quality:
    min_mean: 0.7      # Min 70% helpful responses
  toxicity:
    max_mean: 0.05     # Max 5% toxic responses`}</code></pre>

      <h2>Step 4: Create Your Dataset</h2>

      <p>Create a test dataset in JSONL format (<code>tests/eval_data.jsonl</code>):</p>

      <pre><code>{`{"input": "What's the weather like today?", "conversation_id": "test-001"}
{"input": "Help me write a professional email", "conversation_id": "test-002"}
{"input": "Explain quantum computing simply", "conversation_id": "test-003"}
{"input": "What are your business hours?", "conversation_id": "test-004"}
{"input": "I need to reset my password", "conversation_id": "test-005"}`}</code></pre>

      <h2>Step 5: Create an Adapter Function</h2>

      <p>Create an adapter that runs your app on the test inputs (<code>my_app/eval_adapter.py</code>):</p>

      <pre><code>{`import json
from my_app import generate_response  # Your LLM app

def run_batch(input_path: str, output_path: str) -> None:
    """Process test inputs and write outputs."""
    with open(input_path) as f:
        inputs = [json.loads(line) for line in f]

    outputs = []
    for item in inputs:
        response = generate_response(item["input"])
        outputs.append({
            **item,
            "output": response
        })

    with open(output_path, "w") as f:
        for item in outputs:
            f.write(json.dumps(item) + "\\n")`}</code></pre>

      <h2>Step 6: Run the Evaluation</h2>

      <pre><code>{`company-eval ci-run --config eval_config.yaml`}</code></pre>

      <p>You'll see output like:</p>

      <pre><code>{`======================================================================
  LLM EVALUATION PIPELINE
======================================================================

App Name: my-chatbot
App Type: simple_chat
Eval Suite: basic_chat
Dataset Size: 5 rows (static)

Running adapter: my_app.eval_adapter.run_batch
  Adapter completed successfully
  Loaded 5 model outputs

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

      <h2>Step 7: View in Dashboard (Optional)</h2>

      <p>To track results over time, start the dashboard and report results to it:</p>

      <pre><code>{`# Terminal 1: Start dashboard
company-eval dashboard --port 8080

# Terminal 2: Run eval and report to dashboard
company-eval ci-run --config eval_config.yaml --report-to http://localhost:8080`}</code></pre>

      <h2>Next Steps</h2>

      <ul>
        <li><Link to="/docs/config">Configuration reference</Link> - All config options</li>
        <li><Link to="/docs/app-types">App types</Link> - Chat, RAG, Agent configurations</li>
        <li><Link to="/docs/eval-suites">Eval suites</Link> - Built-in evaluation suites</li>
        <li><Link to="/docs/dashboard">Dashboard setup</Link> - Track quality over time</li>
      </ul>
    </div>
  )
}
