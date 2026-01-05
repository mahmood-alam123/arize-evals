import { Link } from 'react-router-dom'

export default function Introduction() {
  return (
    <div className="docs-content">
      <h1>Company Eval Framework</h1>

      <p>
        A production-ready evaluation framework for LLM applications. Built on{' '}
        <a href="https://docs.arize.com/phoenix/evaluation" target="_blank" rel="noopener noreferrer">
          Arize Phoenix Evals
        </a>
        , Company Eval provides automated quality gates for your AI features.
      </p>

      <div className="grid md:grid-cols-2 gap-4 my-8">
        <Link to="/docs/quickstart" className="block p-6 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-gray-300 transition-all">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-0">Quickstart →</h3>
          <p className="text-gray-500 text-sm mb-0">
            Get up and running in 5 minutes with your first evaluation.
          </p>
        </Link>
        <Link to="/docs/how-it-works" className="block p-6 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-gray-300 transition-all">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-0">How It Works →</h3>
          <p className="text-gray-500 text-sm mb-0">
            Understand the evaluation pipeline and what happens when you run.
          </p>
        </Link>
      </div>

      <h2>Why Company Eval?</h2>

      <p>
        LLM applications are notoriously difficult to test. Traditional unit tests don't capture
        the nuances of natural language, and manual QA doesn't scale. Company Eval bridges this gap
        with LLM-powered evaluation that runs automatically in your CI/CD pipeline.
      </p>

      <h3>Key Features</h3>

      <ul>
        <li><strong>Configuration-driven:</strong> Define evaluations in simple YAML files</li>
        <li><strong>Multiple app types:</strong> Support for Chat, RAG, Agents, and Multi-Agent systems</li>
        <li><strong>Built-in evaluators:</strong> Pre-configured evaluation suites using Phoenix Evals</li>
        <li><strong>Failure analysis:</strong> Axial coding to categorize and understand failures</li>
        <li><strong>Quality dashboard:</strong> Track quality metrics over time</li>
        <li><strong>CI/CD ready:</strong> Exit codes and reporting for pipeline integration</li>
      </ul>

      <h2>How It Works</h2>

      <ol>
        <li>
          <strong>Define your evaluation</strong> in a YAML config file specifying your app type,
          dataset, and quality thresholds.
        </li>
        <li>
          <strong>Create an adapter function</strong> that runs your LLM application on test inputs
          and returns the outputs.
        </li>
        <li>
          <strong>Run evaluations</strong> using the CLI. LLM judges assess each output for quality
          metrics like hallucination, helpfulness, and toxicity.
        </li>
        <li>
          <strong>View results</strong> in the terminal or the quality dashboard. Failed runs block
          your PR from merging.
        </li>
      </ol>

      <h2>Supported Evaluators</h2>

      <table>
        <thead>
          <tr>
            <th>Evaluator</th>
            <th>Description</th>
            <th>App Types</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>user_frustration</code></td>
            <td>Detects responses likely to frustrate users</td>
            <td>Chat, RAG, Agent</td>
          </tr>
          <tr>
            <td><code>helpfulness_quality</code></td>
            <td>Measures response usefulness and completeness</td>
            <td>All</td>
          </tr>
          <tr>
            <td><code>toxicity</code></td>
            <td>Detects harmful or inappropriate content</td>
            <td>All</td>
          </tr>
          <tr>
            <td><code>hallucination</code></td>
            <td>Identifies factually incorrect claims</td>
            <td>RAG</td>
          </tr>
          <tr>
            <td><code>document_relevance</code></td>
            <td>Checks if retrieved docs are relevant</td>
            <td>RAG</td>
          </tr>
          <tr>
            <td><code>planning_quality</code></td>
            <td>Evaluates agent reasoning quality</td>
            <td>Agent, Multi-Agent</td>
          </tr>
        </tbody>
      </table>

      <h2>Next Steps</h2>

      <ul>
        <li><Link to="/docs/quickstart">Quickstart guide</Link> - Run your first evaluation</li>
        <li><Link to="/docs/config">Configuration reference</Link> - All config options explained</li>
        <li><Link to="/docs/dashboard">Dashboard setup</Link> - Track quality over time</li>
      </ul>
    </div>
  )
}
