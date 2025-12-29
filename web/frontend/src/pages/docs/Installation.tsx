export default function Installation() {
  return (
    <div className="docs-content">
      <h1>Installation</h1>

      <p>
        Company Eval can be installed via pip or from source. The framework requires Python 3.9+
        and an OpenAI API key for LLM-based evaluation.
      </p>

      <h2>Install via pip</h2>

      <pre><code>{`pip install company-eval-framework`}</code></pre>

      <h2>Install from Source</h2>

      <pre><code>{`git clone https://github.com/mahmood-alam123/arize-evals.git
cd arize-evals/eval_framework
pip install -e .`}</code></pre>

      <h2>Install with Dashboard Support</h2>

      <p>To use the quality dashboard, install the optional dashboard dependencies:</p>

      <pre><code>{`pip install company-eval-framework[dashboard]

# Or from source
pip install -e ".[dashboard]"`}</code></pre>

      <h2>Environment Setup</h2>

      <p>Set your OpenAI API key as an environment variable:</p>

      <pre><code>{`# Bash
export OPENAI_API_KEY=sk-...

# PowerShell
$env:OPENAI_API_KEY = "sk-..."

# Or in .env file
OPENAI_API_KEY=sk-...`}</code></pre>

      <h2>Verify Installation</h2>

      <pre><code>{`company-eval --version`}</code></pre>

      <h2>Dependencies</h2>

      <p>Core dependencies:</p>

      <ul>
        <li><strong>arize-phoenix-evals</strong> - LLM evaluation library</li>
        <li><strong>openai</strong> - OpenAI API client</li>
        <li><strong>pandas</strong> - Data processing</li>
        <li><strong>pyyaml</strong> - YAML config parsing</li>
        <li><strong>pydantic</strong> - Config validation</li>
      </ul>

      <p>Dashboard dependencies (optional):</p>

      <ul>
        <li><strong>fastapi</strong> - Web framework</li>
        <li><strong>uvicorn</strong> - ASGI server</li>
        <li><strong>sqlalchemy</strong> - Database ORM</li>
      </ul>

      <h2>Troubleshooting</h2>

      <h3>Import Errors</h3>

      <p>If you see import errors, ensure you're using Python 3.9+:</p>

      <pre><code>{`python --version  # Should be 3.9+`}</code></pre>

      <h3>API Key Issues</h3>

      <p>If evaluations fail with authentication errors:</p>

      <pre><code>{`# Verify your API key is set
echo $OPENAI_API_KEY

# Test API connectivity
python -c "import openai; print(openai.api_key)"`}</code></pre>

      <h3>Dashboard Won't Start</h3>

      <p>Ensure dashboard dependencies are installed:</p>

      <pre><code>{`pip install company-eval-framework[dashboard]`}</code></pre>
    </div>
  )
}
