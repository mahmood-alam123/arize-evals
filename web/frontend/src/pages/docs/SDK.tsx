export default function SDK() {
  return (
    <div className="docs-content">
      <h1>SDK</h1>
      <p>
        Use the Python SDK to run evaluations programmatically in your applications.
      </p>

      <h2>Installation</h2>
      <pre><code className="language-bash">pip install company-eval-framework</code></pre>

      <h2>Basic Usage</h2>
      <p>
        The SDK provides programmatic access to all evaluation functionality. You can run
        evaluations, access results, and integrate with your existing Python workflows.
      </p>

      <pre><code className="language-python">{`from company_eval_framework import run_ci_evaluation, load_eval_config

# Load your evaluation configuration
config = load_eval_config("eval_config.yaml")

# Run the evaluation
results = run_ci_evaluation(config)

# Access the results
print(f"Overall: {'PASS' if results.passed else 'FAIL'}")
for metric, data in results.metrics.items():
    print(f"  {metric}: {data['score']:.2f}")`}</code></pre>

      <h2>Configuration</h2>
      <p>
        You can also build configurations programmatically:
      </p>

      <pre><code className="language-python">{`from company_eval_framework.config import EvalConfig, DatasetConfig, ThresholdConfig

config = EvalConfig(
    app_name="my-chatbot",
    app_type="simple_chat",
    dataset=DatasetConfig(
        mode="static",
        path="data/test_cases.jsonl"
    ),
    eval_suite="basic_chat",
    thresholds={
        "user_frustration": ThresholdConfig(max_mean=0.3),
        "helpfulness_quality": ThresholdConfig(min_mean=0.7),
    }
)`}</code></pre>

      <h2>Running Evaluations</h2>
      <p>
        The SDK supports all the same evaluation modes as the CLI:
      </p>

      <h3>With an Adapter</h3>
      <pre><code className="language-python">{`# Your adapter function processes inputs and generates outputs
def my_adapter(input_path: str, output_path: str):
    # Read inputs, call your LLM, write outputs
    pass

results = run_ci_evaluation(config, adapter=my_adapter)`}</code></pre>

      <h3>With Pre-generated Outputs</h3>
      <pre><code className="language-python">{`# If you already have outputs, skip the adapter
results = run_ci_evaluation(config, skip_adapter=True)`}</code></pre>

      <h2>Accessing Results</h2>
      <p>
        The evaluation results include detailed information:
      </p>

      <pre><code className="language-python">{`# Overall pass/fail
results.passed  # bool

# Individual metrics
results.metrics  # dict of metric name -> score data

# Test case details
results.test_cases  # list of individual test results

# Failure analysis
results.failure_analysis  # categorized failure types`}</code></pre>

      <h2>Integration Examples</h2>

      <h3>Pytest Integration</h3>
      <pre><code className="language-python">{`import pytest
from company_eval_framework import run_ci_evaluation, load_eval_config

def test_chatbot_quality():
    config = load_eval_config("eval_config.yaml")
    results = run_ci_evaluation(config)

    assert results.passed, f"Evaluation failed: {results.summary}"`}</code></pre>

      <h3>Custom Reporting</h3>
      <pre><code className="language-python">{`from company_eval_framework import run_ci_evaluation, load_eval_config

config = load_eval_config("eval_config.yaml")
results = run_ci_evaluation(config)

# Send to your monitoring system
if not results.passed:
    send_alert(
        channel="#llm-quality",
        message=f"Eval failed: {results.summary}"
    )

# Log to your observability platform
log_metrics({
    "eval.passed": results.passed,
    **{f"eval.{k}": v["score"] for k, v in results.metrics.items()}
})`}</code></pre>
    </div>
  )
}
