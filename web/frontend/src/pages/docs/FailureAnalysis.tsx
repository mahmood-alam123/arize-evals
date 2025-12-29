export default function FailureAnalysis() {
  return (
    <div className="docs-content">
      <h1>Failure Analysis</h1>

      <p>
        When evaluations fail, Company Eval uses axial coding to categorize and explain
        failures, helping you understand patterns and prioritize fixes.
      </p>

      <h2>Axial Coding</h2>

      <p>
        Axial coding is a qualitative research technique that groups failures into
        categories. An LLM analyzes each failure and assigns:
      </p>

      <ul>
        <li><strong>failure_type:</strong> Category of the failure</li>
        <li><strong>explanation:</strong> Why this response failed</li>
      </ul>

      <h2>Common Failure Types</h2>

      <h3>For Chat Applications</h3>

      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>unhelpful_response</code></td>
            <td>Response doesn't address the user's question</td>
          </tr>
          <tr>
            <td><code>incomplete_answer</code></td>
            <td>Response is too brief or missing key information</td>
          </tr>
          <tr>
            <td><code>dismissive_tone</code></td>
            <td>Response feels curt or dismissive</td>
          </tr>
          <tr>
            <td><code>off_topic</code></td>
            <td>Response doesn't relate to the question</td>
          </tr>
          <tr>
            <td><code>incorrect_info</code></td>
            <td>Response contains factually wrong information</td>
          </tr>
        </tbody>
      </table>

      <h3>For RAG Applications</h3>

      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>hallucination</code></td>
            <td>Claims not supported by retrieved documents</td>
          </tr>
          <tr>
            <td><code>retrieval_error</code></td>
            <td>Wrong documents were retrieved</td>
          </tr>
          <tr>
            <td><code>synthesis_error</code></td>
            <td>Information was incorrectly combined</td>
          </tr>
          <tr>
            <td><code>missing_context</code></td>
            <td>Relevant documents weren't retrieved</td>
          </tr>
        </tbody>
      </table>

      <h3>For Agent Applications</h3>

      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>wrong_tool</code></td>
            <td>Used inappropriate tool for the task</td>
          </tr>
          <tr>
            <td><code>planning_error</code></td>
            <td>Poor reasoning or sequencing</td>
          </tr>
          <tr>
            <td><code>tool_misuse</code></td>
            <td>Correct tool but wrong parameters</td>
          </tr>
          <tr>
            <td><code>incomplete_execution</code></td>
            <td>Didn't finish the task</td>
          </tr>
        </tbody>
      </table>

      <h2>Viewing Failure Analysis</h2>

      <h3>In Terminal Output</h3>

      <pre><code>{`--------------------------------------------------
  Failure Analysis (Axial Coding)
--------------------------------------------------
Failure Type               Count     %
------------------------------------------------------------
unhelpful_response         8         40%
incomplete_answer          6         30%
dismissive_tone            4         20%
off_topic                  2         10%`}</code></pre>

      <h3>In Dashboard</h3>

      <p>
        The dashboard shows failure distribution charts and lets you drill into
        individual failures with full input/output/explanation context.
      </p>

      <h2>Using Failure Analysis</h2>

      <h3>1. Identify Patterns</h3>

      <p>
        Look at the distribution of failure types. If 50% of failures are
        "incomplete_answer", focus on making your responses more thorough.
      </p>

      <h3>2. Read Explanations</h3>

      <p>
        The LLM provides specific explanations for why each response failed.
        Use these to understand the nuance.
      </p>

      <h3>3. Prioritize Fixes</h3>

      <p>
        Attack the most common failure types first. A fix that addresses 40%
        of failures is more valuable than one addressing 5%.
      </p>

      <h3>4. Track Improvement</h3>

      <p>
        Use the dashboard to compare failure distributions across runs.
        Watch failure rates drop as you improve your prompts.
      </p>

      <h2>Custom Failure Types</h2>

      <p>
        Currently, failure types are determined automatically by the LLM.
        Custom failure type definitions are on the roadmap.
      </p>
    </div>
  )
}
