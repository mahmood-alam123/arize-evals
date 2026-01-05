export default function Metrics() {
  return (
    <div className="docs-content">
      <h1>Evaluation Metrics</h1>

      <p>
        Metrics are the criteria used to evaluate your LLM application's responses.
        Each metric uses an LLM judge to assess quality and returns a binary pass/fail score.
        Thresholds determine when the overall evaluation passes or fails.
      </p>

      <h2>How Scoring Works</h2>

      <p>
        Each metric evaluates every test case and assigns a binary score:
      </p>

      <ul>
        <li><strong>1.0</strong> = Pass (response meets criteria)</li>
        <li><strong>0.0</strong> = Fail (response fails criteria)</li>
      </ul>

      <p>
        The <strong>mean score</strong> is the average across all test cases.
        A mean of 0.85 means 85% of responses passed the evaluation.
      </p>

      <h2>Available Eval Suites</h2>

      <p>
        Choose an eval suite based on your application type. Each suite includes
        metrics specifically designed for that use case.
      </p>

      <h3>basic_chat</h3>

      <p>For conversational chatbots and Q&A applications.</p>

      <pre><code>{`eval_suite: basic_chat`}</code></pre>

      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>user_frustration</code></td>
            <td>Lower is better</td>
            <td>Detects responses likely to frustrate users (dismissive, unhelpful, confusing)</td>
          </tr>
          <tr>
            <td><code>helpfulness_quality</code></td>
            <td>Higher is better</td>
            <td>Measures how useful and complete the response is</td>
          </tr>
          <tr>
            <td><code>toxicity</code></td>
            <td>Lower is better</td>
            <td>Detects harmful, offensive, or inappropriate content</td>
          </tr>
        </tbody>
      </table>

      <h3>basic_rag</h3>

      <p>For Retrieval-Augmented Generation applications.</p>

      <pre><code>{`eval_suite: basic_rag`}</code></pre>

      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>hallucination</code></td>
            <td>Lower is better</td>
            <td>Checks if the answer contains claims not supported by retrieved context</td>
          </tr>
          <tr>
            <td><code>document_relevance</code></td>
            <td>Higher is better</td>
            <td>Evaluates whether retrieved documents are relevant to the query</td>
          </tr>
          <tr>
            <td><code>answer_quality</code></td>
            <td>Higher is better</td>
            <td>Overall quality assessment of the generated answer</td>
          </tr>
        </tbody>
      </table>

      <h3>agent</h3>

      <p>For AI agents with tool use capabilities.</p>

      <pre><code>{`eval_suite: agent`}</code></pre>

      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>planning_quality</code></td>
            <td>Higher is better</td>
            <td>Evaluates the quality of the agent's reasoning and planning</td>
          </tr>
          <tr>
            <td><code>tool_use_appropriateness</code></td>
            <td>Higher is better</td>
            <td>Checks if the agent selected and used tools correctly</td>
          </tr>
        </tbody>
      </table>

      <h2>Configuring Thresholds</h2>

      <p>
        Thresholds define pass/fail criteria. If any metric fails its threshold,
        the entire evaluation fails (exit code 1).
      </p>

      <h3>min_mean (Higher is Better)</h3>

      <p>Use for metrics where higher scores are better:</p>

      <pre><code>{`thresholds:
  helpfulness_quality:
    min_mean: 0.7    # At least 70% must pass`}</code></pre>

      <h3>max_mean (Lower is Better)</h3>

      <p>Use for metrics where lower scores (fewer failures) are better:</p>

      <pre><code>{`thresholds:
  toxicity:
    max_mean: 0.05   # At most 5% can fail`}</code></pre>

      <h2>Recommended Thresholds</h2>

      <h3>Chat Applications</h3>

      <pre><code>{`thresholds:
  user_frustration:
    max_mean: 0.2      # Max 20% frustration rate
  helpfulness_quality:
    min_mean: 0.7      # Min 70% helpful
  toxicity:
    max_mean: 0.05     # Max 5% toxic (always strict)`}</code></pre>

      <h3>RAG Applications</h3>

      <pre><code>{`thresholds:
  hallucination:
    max_mean: 0.1      # Max 10% hallucination rate
  document_relevance:
    min_mean: 0.8      # Min 80% relevant docs
  answer_quality:
    min_mean: 0.7      # Min 70% quality`}</code></pre>

      <h3>Agent Applications</h3>

      <pre><code>{`thresholds:
  planning_quality:
    min_mean: 0.7      # Min 70% good planning
  tool_use_appropriateness:
    min_mean: 0.8      # Min 80% correct tool use`}</code></pre>

      <h2>Threshold Strategies</h2>

      <h3>No Threshold (Track Only)</h3>

      <p>
        Metrics without thresholds are still evaluated and reported,
        but don't affect pass/fail status:
      </p>

      <pre><code>{`# Only user_frustration affects pass/fail
thresholds:
  user_frustration:
    max_mean: 0.3

# helpfulness_quality is tracked but doesn't block`}</code></pre>

      <h3>Progressive Tightening</h3>

      <p>Start lenient and tighten as you improve:</p>

      <pre><code>{`# Week 1: Establish baseline
toxicity:
  max_mean: 0.2

# Week 4: After improvements
toxicity:
  max_mean: 0.1

# Week 8: Production-ready
toxicity:
  max_mean: 0.05`}</code></pre>

      <h2>Understanding Results</h2>

      <p>
        When the evaluation runs, you'll see a summary like this:
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
======================================================================`}</code></pre>

      <h2>Next Steps</h2>

      <ul>
        <li><a href="/docs/failure-analysis">Failure Analysis</a> - Understand why tests fail</li>
        <li><a href="/docs/custom-evaluators">Custom Evaluators</a> - Create your own metrics</li>
        <li><a href="/docs/config">Configuration</a> - Full YAML reference</li>
      </ul>
    </div>
  )
}
