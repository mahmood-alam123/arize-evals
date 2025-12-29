export default function AppTypes() {
  return (
    <div className="docs-content">
      <h1>App Types</h1>

      <p>
        Company Eval supports four types of LLM applications, each with specialized
        evaluation metrics and dataset requirements.
      </p>

      <h2>simple_chat</h2>

      <p>
        For basic chatbots and conversational AI without retrieval or tool use.
      </p>

      <pre><code>{`app_type: simple_chat
eval_suite: basic_chat`}</code></pre>

      <h3>Dataset Format</h3>

      <pre><code>{`{
  "conversation_id": "conv-001",
  "input": "What's the weather like today?"
}
// After adapter runs:
{
  "conversation_id": "conv-001",
  "input": "What's the weather like today?",
  "output": "I'm sorry, I can't check the weather..."
}`}</code></pre>

      <h3>Available Metrics</h3>

      <ul>
        <li><strong>user_frustration</strong> - Detects responses that frustrate users</li>
        <li><strong>helpfulness_quality</strong> - Measures response usefulness</li>
        <li><strong>toxicity</strong> - Detects harmful content</li>
      </ul>

      <h2>rag</h2>

      <p>
        For Retrieval-Augmented Generation apps that retrieve documents and synthesize answers.
      </p>

      <pre><code>{`app_type: rag
eval_suite: basic_rag`}</code></pre>

      <h3>Dataset Format</h3>

      <pre><code>{`{
  "conversation_id": "rag-001",
  "input": "How do I reset my password?"
}
// After adapter runs:
{
  "conversation_id": "rag-001",
  "input": "How do I reset my password?",
  "output": "To reset your password, go to Settings > Security...",
  "context": "Password Reset Guide: Navigate to Settings..."
}`}</code></pre>

      <p>
        <strong>Important:</strong> RAG apps must include a <code>context</code> field
        containing the retrieved documents. This is required for hallucination detection.
      </p>

      <h3>Available Metrics</h3>

      <ul>
        <li><strong>hallucination</strong> - Checks if answer is grounded in context</li>
        <li><strong>document_relevance</strong> - Checks if retrieved docs are relevant</li>
        <li><strong>answer_quality</strong> - Overall answer quality assessment</li>
      </ul>

      <h2>agent</h2>

      <p>
        For single-agent systems that use tools and multi-step reasoning.
      </p>

      <pre><code>{`app_type: agent
eval_suite: agent`}</code></pre>

      <h3>Dataset Format</h3>

      <pre><code>{`{
  "conversation_id": "agent-001",
  "input": "Book a flight from NYC to LA for tomorrow"
}
// After adapter runs:
{
  "conversation_id": "agent-001",
  "input": "Book a flight from NYC to LA for tomorrow",
  "output": "I've found several flights...",
  "tool_calls": [
    {"name": "search_flights", "args": {"from": "NYC", "to": "LA"}},
    {"name": "check_availability", "args": {"date": "2024-01-15"}}
  ]
}`}</code></pre>

      <h3>Available Metrics</h3>

      <ul>
        <li><strong>planning_quality</strong> - Quality of reasoning and planning</li>
        <li><strong>tool_use_appropriateness</strong> - Correct tool selection and usage</li>
      </ul>

      <h2>multi_agent</h2>

      <p>
        For multi-agent collaborative systems with multiple LLM agents working together.
      </p>

      <pre><code>{`app_type: multi_agent
eval_suite: multi_agent`}</code></pre>

      <h3>Dataset Format</h3>

      <pre><code>{`{
  "conversation_id": "multi-001",
  "input": "Research and summarize recent AI news"
}
// After adapter runs:
{
  "conversation_id": "multi-001",
  "input": "Research and summarize recent AI news",
  "output": "Here's a summary of recent AI developments...",
  "agent_trace": [
    {"agent": "researcher", "action": "search", "result": "..."},
    {"agent": "writer", "action": "summarize", "result": "..."}
  ]
}`}</code></pre>

      <h3>Available Metrics</h3>

      <ul>
        <li><strong>overall_answer_quality</strong> - Quality of final synthesized answer</li>
        <li><strong>planning_quality</strong> - Quality of agent coordination</li>
      </ul>

      <h2>Choosing an App Type</h2>

      <table>
        <thead>
          <tr>
            <th>Your App Does...</th>
            <th>Use App Type</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Simple Q&A, no external data</td>
            <td><code>simple_chat</code></td>
          </tr>
          <tr>
            <td>Retrieves documents, then answers</td>
            <td><code>rag</code></td>
          </tr>
          <tr>
            <td>Uses tools, multi-step reasoning</td>
            <td><code>agent</code></td>
          </tr>
          <tr>
            <td>Multiple agents collaborating</td>
            <td><code>multi_agent</code></td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
