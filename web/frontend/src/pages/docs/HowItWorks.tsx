export default function HowItWorks() {
  return (
    <div className="docs-content">
      <h1>How It Works</h1>

      <p>
        Company Eval is a framework for testing LLM applications in CI/CD pipelines.
        It runs your app against a test dataset, evaluates responses using LLM judges,
        and fails the build if quality thresholds aren't met.
      </p>

      <h2>The Evaluation Pipeline</h2>

      <p>When you run <code>ci-run</code>, the framework executes these steps:</p>

      <div className="my-6 p-4 bg-gray-100 rounded-lg border">
        <div className="flex items-center justify-between text-sm font-mono">
          <div className="text-center p-3 bg-white rounded shadow">
            <div className="font-bold text-blue-600">1. Config</div>
            <div className="text-gray-500">YAML</div>
          </div>
          <div className="text-gray-400">→</div>
          <div className="text-center p-3 bg-white rounded shadow">
            <div className="font-bold text-blue-600">2. Dataset</div>
            <div className="text-gray-500">Load/Generate</div>
          </div>
          <div className="text-gray-400">→</div>
          <div className="text-center p-3 bg-white rounded shadow">
            <div className="font-bold text-blue-600">3. Adapter</div>
            <div className="text-gray-500">Run App</div>
          </div>
          <div className="text-gray-400">→</div>
          <div className="text-center p-3 bg-white rounded shadow">
            <div className="font-bold text-blue-600">4. Evaluate</div>
            <div className="text-gray-500">LLM Judges</div>
          </div>
          <div className="text-gray-400">→</div>
          <div className="text-center p-3 bg-white rounded shadow">
            <div className="font-bold text-blue-600">5. Report</div>
            <div className="text-gray-500">Pass/Fail</div>
          </div>
        </div>
      </div>

      <h2>Step 1: Load Configuration</h2>

      <p>
        Your YAML config file specifies everything about the evaluation: which app to test,
        what dataset to use, which metrics to evaluate, and what thresholds define success.
      </p>

      <pre><code>{`# llm_eval_chat.yaml
app_name: customer-support-bot
app_type: simple_chat
adapter:
  module: my_app.eval_adapter
  function: run_chat_batch
dataset:
  mode: static
  path: ./test_cases.jsonl
eval_suite: basic_chat
thresholds:
  user_frustration:
    max_mean: 0.2`}</code></pre>

      <h2>Step 2: Load or Generate Dataset</h2>

      <p>
        The framework loads test cases from your dataset. Each test case has an input
        (the user query) and optionally expected outputs or context.
      </p>

      <pre><code>{`{"conversation_id": "1", "input": "How do I reset my password?"}
{"conversation_id": "2", "input": "What are your business hours?"}
{"conversation_id": "3", "input": "I want to cancel my subscription"}`}</code></pre>

      <p>
        You can also generate synthetic test cases using an LLM by setting <code>mode: synthetic</code>.
      </p>

      <h2>Step 3: Run Your App</h2>

      <p>
        Your adapter function receives the test inputs and produces outputs by calling your LLM app.
        The adapter is the bridge between the evaluation framework and your application.
      </p>

      <pre><code>{`def run_chat_batch(input_path: str, output_path: str):
    inputs = read_jsonl(input_path)
    outputs = []

    for item in inputs:
        response = my_chatbot(item["input"])
        outputs.append({
            "conversation_id": item["conversation_id"],
            "input": item["input"],
            "output": response
        })

    write_jsonl(outputs, output_path)`}</code></pre>

      <h2>Step 4: Evaluate Responses</h2>

      <p>
        LLM judges (powered by GPT-4) evaluate each response against multiple criteria.
        Each judge returns a binary score (pass/fail) with an explanation.
      </p>

      <ul>
        <li><strong>User Frustration</strong> - Is the response dismissive or unhelpful?</li>
        <li><strong>Helpfulness</strong> - Does it actually solve the user's problem?</li>
        <li><strong>Toxicity</strong> - Is there harmful or inappropriate content?</li>
      </ul>

      <p>
        During evaluation, the framework also captures <strong>traces</strong> showing exactly
        what happened: LLM calls, tool invocations, retrieval operations, and more.
      </p>

      <h2>Step 5: Check Thresholds & Report</h2>

      <p>
        The framework calculates the mean score for each metric and compares it to your thresholds.
        If any threshold is violated, the evaluation fails with exit code 1.
      </p>

      <pre><code>{`======================================================================
  Metric Summary (Aggregate Scores)
======================================================================
Metric                    Score  Threshold        Status
------------------------------------------------------------
user_frustration          0.15    <= 0.20      [OK] PASS
helpfulness_quality       0.85    >= 0.70      [OK] PASS
toxicity                  0.02    <= 0.05      [OK] PASS

All metrics satisfy their thresholds.

======================================================================
  FINAL RESULT: PASS
======================================================================`}</code></pre>

      <h2>What Happens on Failure?</h2>

      <p>
        When an evaluation fails, the framework runs <strong>axial coding</strong> to automatically
        categorize failures into patterns like "incomplete_answer", "hallucination", or "wrong_tool".
      </p>

      <p>
        These patterns help you understand <em>why</em> your app is failing, not just that it failed.
        You can view failure analysis in the Quality Dashboard.
      </p>

      <h2>Quality Dashboard</h2>

      <p>
        Results are automatically sent to the Quality Dashboard where you can:
      </p>

      <ul>
        <li>Track metrics over time across multiple runs</li>
        <li>View detailed traces for each test case</li>
        <li>Analyze failure patterns with axial coding</li>
        <li>Save failure cases as regression datasets</li>
        <li>Compare runs to measure improvement</li>
      </ul>

      <h2>Next Steps</h2>

      <ul>
        <li><a href="/docs/tracing">Tracing</a> - Understand execution traces</li>
        <li><a href="/docs/metrics">Evaluation Metrics</a> - All available metrics and thresholds</li>
        <li><a href="/docs/failure-analysis">Failure Analysis</a> - How axial coding works</li>
      </ul>
    </div>
  )
}
