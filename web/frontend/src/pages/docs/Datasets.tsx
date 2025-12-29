export default function Datasets() {
  return (
    <div className="docs-content">
      <h1>Datasets</h1>

      <p>
        Company Eval supports two dataset modes: static (load from file) and synthetic
        (generate using an LLM).
      </p>

      <h2>Static Datasets</h2>

      <p>Load test data from a JSONL file:</p>

      <pre><code>{`dataset:
  mode: static
  path: tests/eval_data.jsonl
  size: 50  # Optional: limit to first N rows`}</code></pre>

      <h3>JSONL Format</h3>

      <p>Each line is a JSON object with at least an <code>input</code> field:</p>

      <pre><code>{`{"conversation_id": "001", "input": "What's your return policy?"}
{"conversation_id": "002", "input": "How do I track my order?"}
{"conversation_id": "003", "input": "Can I change my shipping address?"}`}</code></pre>

      <h3>Required Fields by App Type</h3>

      <table>
        <thead>
          <tr>
            <th>App Type</th>
            <th>Required Fields</th>
            <th>Optional Fields</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>simple_chat</td>
            <td>input</td>
            <td>conversation_id</td>
          </tr>
          <tr>
            <td>rag</td>
            <td>input</td>
            <td>conversation_id, expected_context</td>
          </tr>
          <tr>
            <td>agent</td>
            <td>input</td>
            <td>conversation_id, expected_tools</td>
          </tr>
          <tr>
            <td>multi_agent</td>
            <td>input</td>
            <td>conversation_id</td>
          </tr>
        </tbody>
      </table>

      <h2>Synthetic Datasets</h2>

      <p>Generate test data using an LLM:</p>

      <pre><code>{`dataset:
  mode: synthetic
  num_examples: 20
  generation_model: gpt-4o-mini
  description: "Customer support chatbot for a SaaS product"`}</code></pre>

      <h3>Options</h3>

      <table>
        <thead>
          <tr>
            <th>Field</th>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>num_examples</code></td>
            <td>integer</td>
            <td>Number of examples to generate</td>
          </tr>
          <tr>
            <td><code>generation_model</code></td>
            <td>string</td>
            <td>OpenAI model to use (default: gpt-4o-mini)</td>
          </tr>
          <tr>
            <td><code>description</code></td>
            <td>string</td>
            <td>Description of your app for context</td>
          </tr>
        </tbody>
      </table>

      <h2>Output Format</h2>

      <p>
        Your adapter function adds the <code>output</code> field (and optionally <code>context</code>
        for RAG):
      </p>

      <pre><code>{`// Input (from dataset)
{"conversation_id": "001", "input": "What's your return policy?"}

// Output (after adapter runs)
{
  "conversation_id": "001",
  "input": "What's your return policy?",
  "output": "Our return policy allows returns within 30 days...",
  "context": "Return Policy: Customers may return items..."  // RAG only
}`}</code></pre>

      <h2>Best Practices</h2>

      <ul>
        <li>
          <strong>Use diverse inputs:</strong> Include edge cases, long inputs, and adversarial examples
        </li>
        <li>
          <strong>Include conversation IDs:</strong> Makes it easier to trace failures back to specific inputs
        </li>
        <li>
          <strong>Version your datasets:</strong> Track changes to your test data over time
        </li>
        <li>
          <strong>Sample from production:</strong> Use real user queries for more realistic testing
        </li>
      </ul>

      <h2>Sampling from Production</h2>

      <p>
        The <code>sample-prod</code> command (coming soon) will help you sample real
        queries from production logs for evaluation.
      </p>

      <pre><code>{`# Coming soon
company-eval sample-prod --source logs.jsonl --output eval_data.jsonl --size 100`}</code></pre>
    </div>
  )
}
