export default function RAG() {
  return (
    <div className="docs-content">
      <h1>RAG</h1>
      <p>
        Evaluate Retrieval-Augmented Generation applications that answer questions from your documents.
      </p>

      <h2>Overview</h2>
      <p>
        The RAG evaluation suite is designed for applications that retrieve relevant documents
        and use them to generate grounded responses. This includes:
      </p>
      <ul>
        <li>Document Q&A systems</li>
        <li>Knowledge base assistants</li>
        <li>Search with AI-generated summaries</li>
        <li>Enterprise search applications</li>
      </ul>

      <h2>Evaluation Metrics</h2>

      <h3>Hallucination</h3>
      <p>
        Detects when the model generates information not present in the retrieved documents:
      </p>
      <ul>
        <li>Made-up facts or statistics</li>
        <li>Information contradicting the source documents</li>
        <li>Extrapolations beyond what documents support</li>
        <li>Confident statements without source backing</li>
      </ul>
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 my-4">
        <p className="text-red-800 font-medium m-0">Recommended threshold: max_mean ≤ 0.10</p>
        <p className="text-red-600 text-sm m-0">Hallucinations should be rare (&lt;10%)</p>
      </div>

      <h3>Document Relevance</h3>
      <p>
        Measures whether the retrieved documents are relevant to the user's query:
      </p>
      <ul>
        <li>Documents address the user's question</li>
        <li>Retrieved content is topically appropriate</li>
        <li>Documents contain information needed to answer</li>
      </ul>
      <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-4 my-4">
        <p className="text-cyan-800 font-medium m-0">Recommended threshold: min_mean ≥ 0.80</p>
        <p className="text-cyan-600 text-sm m-0">At least 80% of retrievals should be relevant</p>
      </div>

      <h3>Answer Quality</h3>
      <p>
        Assesses the overall quality of the generated answer based on the context:
      </p>
      <ul>
        <li>Correctly synthesizes information from documents</li>
        <li>Provides a complete answer to the question</li>
        <li>Well-structured and easy to understand</li>
        <li>Appropriately cites or references sources</li>
      </ul>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 my-4">
        <p className="text-green-800 font-medium m-0">Recommended threshold: min_mean ≥ 0.70</p>
        <p className="text-green-600 text-sm m-0">At least 70% of answers should be high quality</p>
      </div>

      <h2>Configuration</h2>
      <pre><code className="language-yaml">{`app_name: my-rag-app
app_type: rag

adapter:
  module: "my_app.eval_adapter"
  function: "run_rag_batch"

dataset:
  mode: static
  path: "data/rag_test_cases.jsonl"

eval_suite: basic_rag

thresholds:
  hallucination:
    max_mean: 0.10
  document_relevance:
    min_mean: 0.80
  answer_quality:
    min_mean: 0.70`}</code></pre>

      <h2>Dataset Format</h2>
      <p>
        RAG evaluation requires both the query and the retrieved context:
      </p>
      <pre><code className="language-json">{`{
  "conversation_id": "1",
  "input": "What is the return policy?",
  "context": "Our return policy allows returns within 14 days of purchase. Items must be unused and in original packaging. Refunds are processed within 5-7 business days."
}`}</code></pre>

      <h3>Required Fields</h3>
      <ul>
        <li><code>conversation_id</code> - Unique identifier for the test case</li>
        <li><code>input</code> - The user's question</li>
        <li><code>context</code> - The retrieved documents (can be a string or array)</li>
      </ul>

      <h3>Context Formats</h3>
      <p>The context field supports multiple formats:</p>
      <pre><code className="language-json">{`// Single document as string
"context": "Document text here..."

// Multiple documents as array
"context": [
  "Document 1 text...",
  "Document 2 text...",
  "Document 3 text..."
]

// Documents with metadata
"context": [
  {"text": "Document 1", "source": "faq.md", "score": 0.95},
  {"text": "Document 2", "source": "policy.md", "score": 0.87}
]`}</code></pre>

      <h2>Adapter Example</h2>
      <pre><code className="language-python">{`import json
from openai import OpenAI

client = OpenAI()

def run_rag_batch(input_path: str, output_path: str):
    """Process RAG inputs through your pipeline."""
    with open(input_path) as f:
        inputs = [json.loads(line) for line in f]

    results = []
    for item in inputs:
        # Your retrieval step (if not pre-computed)
        # context = retrieve_documents(item["input"])

        # Use provided context
        context = item["context"]
        if isinstance(context, list):
            context = "\\n\\n".join(context)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"""Answer based only on the following context:

{context}

If the answer is not in the context, say "I don't have information about that."
"""
                },
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

      <h2>Failure Analysis</h2>
      <p>
        When RAG evaluations fail, the framework performs axial coding to categorize failures:
      </p>
      <ul>
        <li><strong>retrieval_error</strong> - Wrong or irrelevant documents retrieved</li>
        <li><strong>hallucination</strong> - Model made up information not in docs</li>
        <li><strong>formatting</strong> - Answer format issues (too long, poorly structured)</li>
        <li><strong>refusal</strong> - Model refused to answer when it should have</li>
        <li><strong>irrelevant</strong> - Answer doesn't address the question</li>
      </ul>

      <h2>Best Practices</h2>
      <ul>
        <li>Include questions that require synthesizing multiple documents</li>
        <li>Test questions where the answer is NOT in the documents</li>
        <li>Include questions that might tempt the model to hallucinate</li>
        <li>Test edge cases like contradictory documents</li>
        <li>Verify your retrieval quality separately from generation quality</li>
        <li>Use realistic document chunks from your actual knowledge base</li>
      </ul>
    </div>
  )
}
