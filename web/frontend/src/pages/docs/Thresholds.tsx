export default function Thresholds() {
  return (
    <div className="docs-content">
      <h1>Thresholds</h1>

      <p>
        Thresholds define pass/fail criteria for your evaluation metrics. If any metric
        fails its threshold, the entire evaluation fails (exit code 1).
      </p>

      <h2>Threshold Types</h2>

      <h3>min_mean (Higher is Better)</h3>

      <p>Use for metrics where higher scores are better:</p>

      <pre><code>{`thresholds:
  helpfulness_quality:
    min_mean: 0.7    # At least 70% must pass`}</code></pre>

      <h3>max_mean (Lower is Better)</h3>

      <p>Use for metrics where lower scores are better:</p>

      <pre><code>{`thresholds:
  toxicity:
    max_mean: 0.05   # At most 5% can fail`}</code></pre>

      <h2>How Thresholds Work</h2>

      <p>
        Each metric evaluates every test case and assigns a binary score (0 or 1).
        The <strong>mean score</strong> is the average of all scores.
      </p>

      <pre><code>{`# Example: 10 test cases, 2 failed toxicity check
Scores: [1, 1, 0, 1, 1, 1, 1, 1, 0, 1]
Mean: 8/10 = 0.80

# For toxicity (lower is better), we check failure rate
Failure rate: 2/10 = 0.20

# If threshold is max_mean: 0.05, this FAILS (0.20 > 0.05)`}</code></pre>

      <h2>Recommended Thresholds by App Type</h2>

      <h3>Chat Applications</h3>

      <pre><code>{`thresholds:
  user_frustration:
    max_mean: 0.3      # Strict: 0.1, Lenient: 0.4
  helpfulness_quality:
    min_mean: 0.7      # Strict: 0.85, Lenient: 0.6
  toxicity:
    max_mean: 0.05     # Should always be strict`}</code></pre>

      <h3>RAG Applications</h3>

      <pre><code>{`thresholds:
  hallucination:
    max_mean: 0.1      # Strict: 0.05, Lenient: 0.15
  document_relevance:
    min_mean: 0.8      # Strict: 0.9, Lenient: 0.7
  answer_quality:
    min_mean: 0.7      # Strict: 0.8, Lenient: 0.6`}</code></pre>

      <h3>Agent Applications</h3>

      <pre><code>{`thresholds:
  planning_quality:
    min_mean: 0.7
  tool_use_appropriateness:
    min_mean: 0.8`}</code></pre>

      <h2>No Threshold</h2>

      <p>
        If you don't specify a threshold for a metric, it will still be evaluated
        and reported, but won't affect the pass/fail status.
      </p>

      <pre><code>{`# Only user_frustration affects pass/fail
thresholds:
  user_frustration:
    max_mean: 0.3

# helpfulness_quality is tracked but doesn't block`}</code></pre>

      <h2>Progressive Tightening</h2>

      <p>Start with lenient thresholds and tighten over time as you improve your app:</p>

      <ol>
        <li>Start with lenient thresholds to establish a baseline</li>
        <li>Fix the worst failures first</li>
        <li>Gradually tighten thresholds as quality improves</li>
        <li>Use the dashboard to track progress over time</li>
      </ol>

      <pre><code>{`# Week 1: Establish baseline
toxicity:
  max_mean: 0.2

# Week 4: After improvements
toxicity:
  max_mean: 0.1

# Week 8: Production-ready
toxicity:
  max_mean: 0.05`}</code></pre>
    </div>
  )
}
