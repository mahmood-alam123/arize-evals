export default function Chat() {
  return (
    <div className="docs-content">
      <h1>Basic Chat</h1>
      <p>
        Evaluate Q&A bots, conversational interfaces, and customer support assistants.
      </p>

      <h2>Overview</h2>
      <p>
        The Basic Chat evaluation suite is designed for simple conversational AI applications
        where users ask questions and receive responses. This includes:
      </p>
      <ul>
        <li>Customer support chatbots</li>
        <li>FAQ assistants</li>
        <li>General-purpose Q&A interfaces</li>
        <li>Conversational search</li>
      </ul>

      <h2>Evaluation Metrics</h2>

      <h3>User Frustration</h3>
      <p>
        Measures whether the response would frustrate a typical user. This captures issues like:
      </p>
      <ul>
        <li>Unhelpful or evasive answers</li>
        <li>Repetitive or robotic responses</li>
        <li>Failure to understand the question</li>
        <li>Overly long or confusing explanations</li>
      </ul>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 my-4">
        <p className="text-blue-800 font-medium m-0">Recommended threshold: max_mean ≤ 0.30</p>
        <p className="text-blue-600 text-sm m-0">No more than 30% of responses should be frustrating</p>
      </div>

      <h3>Toxicity</h3>
      <p>
        Detects harmful, offensive, or inappropriate content in responses:
      </p>
      <ul>
        <li>Offensive language</li>
        <li>Discriminatory content</li>
        <li>Inappropriate suggestions</li>
        <li>Harmful advice</li>
      </ul>
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 my-4">
        <p className="text-red-800 font-medium m-0">Recommended threshold: max_mean ≤ 0.05</p>
        <p className="text-red-600 text-sm m-0">Toxicity should be near zero</p>
      </div>

      <h3>Helpfulness Quality</h3>
      <p>
        Assesses whether the response actually helps the user accomplish their goal:
      </p>
      <ul>
        <li>Directly answers the question</li>
        <li>Provides actionable information</li>
        <li>Clear and well-structured</li>
        <li>Appropriate level of detail</li>
      </ul>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 my-4">
        <p className="text-green-800 font-medium m-0">Recommended threshold: min_mean ≥ 0.70</p>
        <p className="text-green-600 text-sm m-0">At least 70% of responses should be helpful</p>
      </div>

      <h2>Configuration</h2>
      <pre><code className="language-yaml">{`app_name: my-chatbot
app_type: simple_chat

adapter:
  module: "my_app.eval_adapter"
  function: "run_chat_batch"

dataset:
  mode: static
  path: "data/chat_test_cases.jsonl"

eval_suite: basic_chat

thresholds:
  user_frustration:
    max_mean: 0.30
  toxicity:
    max_mean: 0.05
  helpfulness_quality:
    min_mean: 0.70`}</code></pre>

      <h2>Dataset Format</h2>
      <p>
        Your test dataset should be a JSONL file with the following fields:
      </p>
      <pre><code className="language-json">{`{"conversation_id": "1", "input": "How do I reset my password?"}
{"conversation_id": "2", "input": "What are your business hours?"}
{"conversation_id": "3", "input": "I'm having trouble with my order #12345"}`}</code></pre>

      <h3>Optional Fields</h3>
      <ul>
        <li><code>business_context</code> - Additional context about the business domain</li>
        <li><code>expected_topics</code> - Topics the response should cover</li>
        <li><code>conversation_history</code> - Previous messages for multi-turn conversations</li>
      </ul>

      <h2>Adapter Example</h2>
      <pre><code className="language-python">{`import json
from openai import OpenAI

client = OpenAI()

def run_chat_batch(input_path: str, output_path: str):
    """Process chat inputs through your LLM."""
    with open(input_path) as f:
        inputs = [json.loads(line) for line in f]

    results = []
    for item in inputs:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": item["input"]}
            ]
        )
        results.append({
            **item,
            "output": response.choices[0].message.content
        })

    with open(output_path, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\\n')`}</code></pre>

      <h2>Best Practices</h2>
      <ul>
        <li>Include a variety of question types (how-to, troubleshooting, informational)</li>
        <li>Test edge cases like ambiguous questions or off-topic requests</li>
        <li>Include questions that might trigger inappropriate responses</li>
        <li>Test multi-turn conversations if your app supports them</li>
        <li>Use real user queries from production logs when possible</li>
      </ul>
    </div>
  )
}
