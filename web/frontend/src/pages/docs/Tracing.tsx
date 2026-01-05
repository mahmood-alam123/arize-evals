export default function Tracing() {
  return (
    <div className="docs-content">
      <h1>Tracing</h1>

      <p>
        Traces provide complete visibility into what happened during each test case execution.
        They show every LLM call, tool invocation, retrieval operation, and agent step in a
        visual timeline.
      </p>

      <h2>What is a Trace?</h2>

      <p>
        A trace represents the full execution of a single test case through your LLM application.
        It contains a tree of <strong>spans</strong>, where each span represents one operation.
      </p>

      <div className="my-6 p-4 bg-gray-50 rounded-lg border font-mono text-sm">
        <div className="mb-2 font-bold text-gray-700">Trace: "How do I reset my password?"</div>
        <div className="ml-4 border-l-2 border-blue-300 pl-4 space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">llm</span>
            <span>generate_response (1.2s)</span>
          </div>
        </div>
      </div>

      <p>
        For more complex apps like RAG or agents, traces show the full execution flow:
      </p>

      <div className="my-6 p-4 bg-gray-50 rounded-lg border font-mono text-sm">
        <div className="mb-2 font-bold text-gray-700">Trace: "What's the API rate limit?"</div>
        <div className="ml-4 border-l-2 border-blue-300 pl-4 space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">retrieval</span>
            <span>search_documents (0.3s)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">llm</span>
            <span>generate_answer (0.8s)</span>
          </div>
        </div>
      </div>

      <h2>Span Types</h2>

      <p>Each span has a type indicating what kind of operation it represents:</p>

      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Description</th>
            <th>Typical Fields</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>llm</code></td>
            <td>Call to an LLM (OpenAI, Anthropic, etc.)</td>
            <td>Model, tokens, cost, prompt, completion</td>
          </tr>
          <tr>
            <td><code>retrieval</code></td>
            <td>Document retrieval operation</td>
            <td>Query, documents returned, relevance scores</td>
          </tr>
          <tr>
            <td><code>tool</code></td>
            <td>Tool or function call</td>
            <td>Tool name, arguments, result</td>
          </tr>
          <tr>
            <td><code>chain</code></td>
            <td>Orchestration step (planning, routing)</td>
            <td>Decision, next steps</td>
          </tr>
          <tr>
            <td><code>agent</code></td>
            <td>Agent action or decision</td>
            <td>Thought, action, observation</td>
          </tr>
          <tr>
            <td><code>custom</code></td>
            <td>Custom operation</td>
            <td>User-defined metadata</td>
          </tr>
        </tbody>
      </table>

      <h2>Viewing Traces in the Dashboard</h2>

      <p>
        To view a trace for a specific test case:
      </p>

      <ol>
        <li>Go to the <strong>Dashboard</strong> and click on a run</li>
        <li>In the <strong>Test Cases</strong> section, find the test case you want to inspect</li>
        <li>Click the <strong>View Trace</strong> button</li>
      </ol>

      <h3>The Trace View</h3>

      <p>The trace view shows:</p>

      <ul>
        <li><strong>Waterfall Timeline</strong> - Visual representation of when each span started and how long it took</li>
        <li><strong>Span Details</strong> - Click any span to see its inputs, outputs, and metadata</li>
        <li><strong>Token Usage</strong> - For LLM spans, see prompt and completion token counts</li>
        <li><strong>Cost Tracking</strong> - Estimated cost for each LLM call</li>
        <li><strong>Error Information</strong> - If a span failed, see the error message</li>
      </ul>

      <h2>Example Traces by App Type</h2>

      <h3>Simple Chat</h3>

      <p>A single LLM call with the user message and system prompt:</p>

      <div className="my-4 p-4 bg-gray-50 rounded border font-mono text-sm">
        <div className="text-gray-500 text-xs mb-2">Trace for chat application</div>
        <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-blue-500">
          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">llm</span>
          <span>chat_completion</span>
          <span className="text-gray-400 ml-auto">850ms • 245 tokens • $0.0012</span>
        </div>
      </div>

      <h3>RAG Application</h3>

      <p>Document retrieval followed by answer generation:</p>

      <div className="my-4 p-4 bg-gray-50 rounded border font-mono text-sm">
        <div className="text-gray-500 text-xs mb-2">Trace for RAG application</div>
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-purple-500">
            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">retrieval</span>
            <span>document_search</span>
            <span className="text-gray-400 ml-auto">320ms • 3 docs</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-blue-500">
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">llm</span>
            <span>generate_answer</span>
            <span className="text-gray-400 ml-auto">1.1s • 892 tokens • $0.0045</span>
          </div>
        </div>
      </div>

      <h3>Agent with Tools</h3>

      <p>Planning, tool execution, and response generation:</p>

      <div className="my-4 p-4 bg-gray-50 rounded border font-mono text-sm">
        <div className="text-gray-500 text-xs mb-2">Trace for agent application</div>
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-yellow-500">
            <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs">chain</span>
            <span>plan_task</span>
            <span className="text-gray-400 ml-auto">450ms</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-green-500">
            <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">tool</span>
            <span>calendar.create_event</span>
            <span className="text-gray-400 ml-auto">230ms</span>
          </div>
          <div className="flex items-center gap-2 p-2 bg-white rounded border-l-4 border-blue-500">
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">llm</span>
            <span>generate_response</span>
            <span className="text-gray-400 ml-auto">680ms • 312 tokens • $0.0016</span>
          </div>
        </div>
      </div>

      <h2>Using Traces for Debugging</h2>

      <p>
        When a test case fails, traces help you understand exactly what went wrong:
      </p>

      <ul>
        <li><strong>Hallucination?</strong> Check the retrieval span to see what context was provided vs. what the LLM generated</li>
        <li><strong>Wrong tool?</strong> Look at the planning span to see the agent's reasoning</li>
        <li><strong>Slow response?</strong> The waterfall shows where time was spent</li>
        <li><strong>High cost?</strong> Token counts reveal if prompts are too long</li>
      </ul>

      <h2>Next Steps</h2>

      <ul>
        <li><a href="/docs/metrics">Evaluation Metrics</a> - Understand what the LLM judges evaluate</li>
        <li><a href="/docs/failure-analysis">Failure Analysis</a> - How failures are categorized</li>
        <li><a href="/docs/dashboard">Quality Dashboard</a> - Navigate the dashboard interface</li>
      </ul>
    </div>
  )
}
