export default function Agents() {
  return (
    <div className="docs-content">
      <h1>Agent / Multi-agent</h1>
      <p>
        Evaluate tool-using agents and coordinated multi-agent systems.
      </p>

      <h2>Overview</h2>
      <p>
        The Agent evaluation suites are designed for AI systems that can use tools,
        make decisions, and coordinate with other agents. This includes:
      </p>
      <ul>
        <li>Tool-using assistants (function calling)</li>
        <li>Autonomous agents with planning capabilities</li>
        <li>Multi-agent orchestration systems</li>
        <li>Agentic workflows with multiple steps</li>
      </ul>

      <h2>Single Agent Evaluation</h2>

      <h3>Planning Quality</h3>
      <p>
        Measures whether the agent creates appropriate plans to accomplish tasks:
      </p>
      <ul>
        <li>Identifies correct steps to achieve the goal</li>
        <li>Orders steps logically</li>
        <li>Accounts for dependencies between steps</li>
        <li>Doesn't include unnecessary steps</li>
      </ul>
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 my-4">
        <p className="text-purple-800 font-medium m-0">Recommended threshold: min_mean ≥ 0.70</p>
        <p className="text-purple-600 text-sm m-0">At least 70% of plans should be well-formed</p>
      </div>

      <h3>Tool Use Appropriateness</h3>
      <p>
        Evaluates whether the agent selects and uses tools correctly:
      </p>
      <ul>
        <li>Chooses the right tool for the task</li>
        <li>Provides correct arguments to tools</li>
        <li>Interprets tool results accurately</li>
        <li>Doesn't call tools unnecessarily</li>
      </ul>
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 my-4">
        <p className="text-orange-800 font-medium m-0">Recommended threshold: min_mean ≥ 0.80</p>
        <p className="text-orange-600 text-sm m-0">Tool use should be correct at least 80% of the time</p>
      </div>

      <h2>Multi-Agent Evaluation</h2>

      <h3>Overall Answer Quality</h3>
      <p>
        Assesses the final output quality from the multi-agent system:
      </p>
      <ul>
        <li>Final answer addresses the original request</li>
        <li>Information from multiple agents is synthesized correctly</li>
        <li>Output is coherent and well-structured</li>
      </ul>

      <h3>Coordination Quality</h3>
      <p>
        Evaluates how well agents work together:
      </p>
      <ul>
        <li>Tasks are delegated appropriately</li>
        <li>Agents don't duplicate work</li>
        <li>Information flows correctly between agents</li>
        <li>Conflicts are resolved appropriately</li>
      </ul>

      <h2>Configuration</h2>

      <h3>Single Agent</h3>
      <pre><code className="language-yaml">{`app_name: my-agent
app_type: agent

adapter:
  module: "my_app.eval_adapter"
  function: "run_agent_batch"

dataset:
  mode: static
  path: "data/agent_test_cases.jsonl"

eval_suite: agent

thresholds:
  planning_quality:
    min_mean: 0.70
  tool_use_appropriateness:
    min_mean: 0.80`}</code></pre>

      <h3>Multi-Agent</h3>
      <pre><code className="language-yaml">{`app_name: my-multi-agent
app_type: multi_agent

adapter:
  module: "my_app.eval_adapter"
  function: "run_multi_agent_batch"

dataset:
  mode: static
  path: "data/multi_agent_test_cases.jsonl"

eval_suite: multi_agent

thresholds:
  overall_answer_quality:
    min_mean: 0.70
  planning_quality:
    min_mean: 0.70`}</code></pre>

      <h2>Dataset Format</h2>

      <h3>Single Agent</h3>
      <pre><code className="language-json">{`{
  "conversation_id": "1",
  "input": "What's the weather in Tokyo and book a restaurant there for tomorrow",
  "available_tools": ["get_weather", "search_restaurants", "make_reservation"],
  "business_context": "User is planning a trip to Tokyo"
}`}</code></pre>

      <h3>Multi-Agent</h3>
      <pre><code className="language-json">{`{
  "conversation_id": "1",
  "input": "Research competitors and create a market analysis report",
  "available_agents": ["research_agent", "analysis_agent", "writing_agent"],
  "business_context": "Quarterly competitive analysis"
}`}</code></pre>

      <h2>Adapter Example</h2>

      <h3>Single Agent</h3>
      <pre><code className="language-python">{`import json
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }
    },
    # ... more tools
]

def run_agent_batch(input_path: str, output_path: str):
    with open(input_path) as f:
        inputs = [json.loads(line) for line in f]

    results = []
    for item in inputs:
        messages = [{"role": "user", "content": item["input"]}]

        # Run agent loop
        tool_calls = []
        while True:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=tools
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                tool_calls.extend([tc.function.name for tc in msg.tool_calls])
                # Execute tools and continue...
                # (simplified for example)
                break
            else:
                break

        results.append({
            **item,
            "output": msg.content,
            "tool_calls": tool_calls
        })

    with open(output_path, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\\n')`}</code></pre>

      <h2>Evaluating Tool Calls</h2>
      <p>
        The framework evaluates tool usage by examining the sequence of tool calls:
      </p>
      <pre><code className="language-json">{`{
  "input": "What's the weather in Tokyo?",
  "output": "The weather in Tokyo is sunny and 72°F",
  "tool_calls": [
    {"name": "get_weather", "args": {"city": "Tokyo"}}
  ],
  "expected_tools": ["get_weather"]
}`}</code></pre>

      <h2>Best Practices</h2>
      <ul>
        <li>Test tasks that require multiple tool calls</li>
        <li>Include tasks where the agent should NOT use any tools</li>
        <li>Test error handling when tools fail</li>
        <li>Verify the agent stops when the task is complete</li>
        <li>Test multi-step reasoning with dependencies</li>
        <li>For multi-agent: test scenarios requiring agent coordination</li>
        <li>Include adversarial inputs that might confuse the agent</li>
      </ul>

      <h2>Common Failure Modes</h2>
      <ul>
        <li><strong>Over-planning</strong> - Agent creates unnecessarily complex plans</li>
        <li><strong>Wrong tool selection</strong> - Picks a tool that can't accomplish the task</li>
        <li><strong>Argument errors</strong> - Provides invalid arguments to tools</li>
        <li><strong>Infinite loops</strong> - Agent doesn't know when to stop</li>
        <li><strong>Coordination failures</strong> - Agents work at cross purposes</li>
        <li><strong>Context loss</strong> - Agent forgets earlier steps or results</li>
      </ul>
    </div>
  )
}
