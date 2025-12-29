export default function EvalSuites() {
  return (
    <div className="docs-content">
      <h1>Evaluation Suites</h1>

      <p>
        Evaluation suites are pre-configured collections of metrics designed for specific
        application types. Each suite uses LLM-powered judges from Arize Phoenix Evals.
      </p>

      <h2>basic_chat</h2>

      <p>For conversational chatbots and simple Q&A applications.</p>

      <pre><code>{`eval_suite: basic_chat`}</code></pre>

      <h3>Metrics</h3>

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

      <h3>Recommended Thresholds</h3>

      <pre><code>{`thresholds:
  user_frustration:
    max_mean: 0.3    # Max 30% frustration rate
  helpfulness_quality:
    min_mean: 0.7    # Min 70% helpful
  toxicity:
    max_mean: 0.05   # Max 5% toxic`}</code></pre>

      <h2>basic_rag</h2>

      <p>For Retrieval-Augmented Generation applications.</p>

      <pre><code>{`eval_suite: basic_rag`}</code></pre>

      <h3>Metrics</h3>

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
            <td>Checks if the answer contains claims not supported by the retrieved context</td>
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

      <h3>Recommended Thresholds</h3>

      <pre><code>{`thresholds:
  hallucination:
    max_mean: 0.1      # Max 10% hallucination rate
  document_relevance:
    min_mean: 0.8      # Min 80% relevant docs
  answer_quality:
    min_mean: 0.7      # Min 70% quality`}</code></pre>

      <h2>agent</h2>

      <p>For single-agent systems with tool use.</p>

      <pre><code>{`eval_suite: agent`}</code></pre>

      <h3>Metrics</h3>

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

      <h3>Recommended Thresholds</h3>

      <pre><code>{`thresholds:
  planning_quality:
    min_mean: 0.7
  tool_use_appropriateness:
    min_mean: 0.8`}</code></pre>

      <h2>multi_agent</h2>

      <p>For multi-agent collaborative systems.</p>

      <pre><code>{`eval_suite: multi_agent`}</code></pre>

      <h3>Metrics</h3>

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
            <td><code>overall_answer_quality</code></td>
            <td>Higher is better</td>
            <td>Quality of the final synthesized answer from all agents</td>
          </tr>
          <tr>
            <td><code>planning_quality</code></td>
            <td>Higher is better</td>
            <td>Quality of coordination between agents</td>
          </tr>
        </tbody>
      </table>

      <h3>Recommended Thresholds</h3>

      <pre><code>{`thresholds:
  overall_answer_quality:
    min_mean: 0.7
  planning_quality:
    min_mean: 0.7`}</code></pre>

      <h2>How Metrics Are Scored</h2>

      <p>
        Each metric uses an LLM judge (GPT-4 by default) to evaluate responses.
        The judge returns a binary score (0 or 1) for each test case:
      </p>

      <ul>
        <li><strong>1.0</strong> = Pass (response meets criteria)</li>
        <li><strong>0.0</strong> = Fail (response fails criteria)</li>
      </ul>

      <p>
        The <strong>mean score</strong> is the average across all test cases.
        A mean of 0.85 means 85% of responses passed the evaluation.
      </p>

      <h2>Combining Suites</h2>

      <p>
        Currently, you can only use one suite per evaluation run. If you need metrics
        from multiple suites, create separate config files and run them sequentially.
      </p>
    </div>
  )
}
