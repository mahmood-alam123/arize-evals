export default function CICD() {
  return (
    <div className="docs-content">
      <h1>CI/CD Integration</h1>
      <p>
        Integrate LLM quality gates into your CI/CD pipeline to catch regressions before they reach production.
      </p>

      <h2>GitHub Actions</h2>
      <p>
        The easiest way to add LLM evaluation to your pipeline is with GitHub Actions.
      </p>

      <h3>Basic Workflow</h3>
      <pre><code className="language-yaml">{`name: LLM Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install company-eval-framework
          pip install -e .  # Install your project

      - name: Run evaluation
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}
        run: |
          company-eval ci-run --config eval_config.yaml

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results/`}</code></pre>

      <h3>With Azure OpenAI</h3>
      <pre><code className="language-yaml">{`- name: Run evaluation
  env:
    AZURE_OPENAI_API_KEY: \${{ secrets.AZURE_OPENAI_API_KEY }}
    AZURE_OPENAI_ENDPOINT: \${{ secrets.AZURE_OPENAI_ENDPOINT }}
    AZURE_OPENAI_DEPLOYMENT: \${{ secrets.AZURE_OPENAI_DEPLOYMENT }}
    AZURE_OPENAI_API_VERSION: "2024-02-15-preview"
  run: |
    company-eval ci-run --config eval_config.yaml`}</code></pre>

      <h2>Quality Gates</h2>
      <p>
        The CLI returns exit code 1 when thresholds are not met, automatically failing
        the CI job and blocking the PR.
      </p>

      <pre><code className="language-yaml">{`# This will fail the job if any threshold is not met
- name: Run evaluation
  run: company-eval ci-run --config eval_config.yaml

# Or continue on error and handle manually
- name: Run evaluation
  id: eval
  continue-on-error: true
  run: company-eval ci-run --config eval_config.yaml

- name: Check results
  if: steps.eval.outcome == 'failure'
  run: |
    echo "::warning::LLM evaluation failed - review results"
    # Could post a PR comment, send Slack notification, etc.`}</code></pre>

      <h2>Multiple Configurations</h2>
      <p>
        Run different evaluation suites for different parts of your application:
      </p>

      <pre><code className="language-yaml">{`jobs:
  evaluate-chat:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install company-eval-framework
      - run: company-eval ci-run --config eval_chat.yaml
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}

  evaluate-rag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install company-eval-framework
      - run: company-eval ci-run --config eval_rag.yaml
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`}</code></pre>

      <h2>Caching</h2>
      <p>
        Speed up your CI runs by caching Python dependencies:
      </p>

      <pre><code className="language-yaml">{`- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

- name: Install dependencies
  run: pip install company-eval-framework`}</code></pre>

      <h2>Manual Triggers</h2>
      <p>
        Allow running evaluations on-demand with workflow dispatch:
      </p>

      <pre><code className="language-yaml">{`on:
  workflow_dispatch:
    inputs:
      config:
        description: 'Config file to use'
        required: true
        default: 'eval_config.yaml'
        type: choice
        options:
          - eval_config.yaml
          - eval_config_rag.yaml
          - eval_config_agent.yaml
      dataset_mode:
        description: 'Dataset mode'
        required: true
        default: 'static'
        type: choice
        options:
          - static
          - synthetic

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install company-eval-framework
      - run: company-eval ci-run --config \${{ inputs.config }}
        env:
          OPENAI_API_KEY: \${{ secrets.OPENAI_API_KEY }}`}</code></pre>

      <h2>GitLab CI</h2>
      <pre><code className="language-yaml">{`llm-evaluation:
  image: python:3.12
  stage: test
  script:
    - pip install company-eval-framework
    - company-eval ci-run --config eval_config.yaml
  variables:
    OPENAI_API_KEY: $OPENAI_API_KEY
  artifacts:
    paths:
      - eval_results/
    when: always`}</code></pre>

      <h2>Jenkins</h2>
      <pre><code className="language-groovy">{`pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('LLM Evaluation') {
            steps {
                sh 'pip install company-eval-framework'
                sh 'company-eval ci-run --config eval_config.yaml'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'eval_results/**'
        }
    }
}`}</code></pre>
    </div>
  )
}
