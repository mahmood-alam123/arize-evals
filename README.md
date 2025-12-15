# Company Eval Framework

**Ship LLM features with confidence. Catch regressions before your users do.**

A standardized evaluation framework for all LLM-powered applications across the company. Built on [Phoenix Evals](https://github.com/Arize-ai/phoenix), this tool brings CI/CD-style quality gates to your AI features.

---

## The Problem

Every team building with LLMs faces the same challenges:

- **"Did my prompt change break something?"** - No way to know until users complain
- **"Is this model better than the last one?"** - Vibes-based evaluation doesn't scale
- **"How do I test my RAG pipeline?"** - Unit tests don't work for non-deterministic outputs
- **"We need to ship faster"** - But quality can't be sacrificed

Teams are reinventing the wheel, building one-off evaluation scripts that don't integrate with CI/CD.

---

## The Solution

A **plug-and-play evaluation framework** that works with any LLM application:

```bash
# Initialize your project
company-eval init my_project

# Generate test data
company-eval generate-dataset --app-type rag --output data/tests.jsonl --num-examples 20

# Run evaluations (locally or in CI)
company-eval ci-run --config eval_config.yaml
```

**That's it.** Your LLM app now has automated quality gates.

---

## Key Features

### 1. Works With Any LLM Pattern

| App Type | What It Evaluates |
|----------|-------------------|
| **Simple Chat** | Response quality, user frustration, toxicity |
| **RAG** | Hallucination, document relevance, answer accuracy |
| **Tool-Using Agents** | Planning quality, appropriate tool selection |
| **Multi-Agent Systems** | Coordination, overall output quality |

### 2. CI/CD Integration Out of the Box

```yaml
# .github/workflows/eval.yml - already included!
- name: Run LLM Evaluation
  run: company-eval ci-run --config eval_config.yaml
```

PRs get blocked if quality drops below thresholds.

### 3. Two Dataset Modes

| Mode | Use Case |
|------|----------|
| **Static** | Regression testing - same inputs every time, track quality trends |
| **Synthetic** | Generate fresh test cases each run for broader coverage |

### 4. Actionable Failure Analysis

When evaluations fail, you get more than just "FAIL":

```
Failure type distribution:
  - hallucination: 3 (60%)
  - refusal: 2 (40%)

Example (hallucination):
  USER: What's our refund policy?
  RESPONSE: We offer 90-day refunds... [WRONG - it's 30 days]
```

---

## Quick Start (5 Minutes)

### 1. Install

```bash
pip install -e eval_framework/
```

### 2. Initialize Your Project

```bash
company-eval init my_evals
```

This creates:
```
my_evals/
├── my_adapter.py          # Connect your LLM app here
├── configs/
│   └── eval_config.yaml   # Evaluation settings
└── data/
    └── eval_dataset.jsonl # Test cases
```

### 3. Connect Your App

Edit `my_adapter.py` to call your LLM:

```python
def run_batch(input_path: str, output_path: str) -> None:
    for row in read_jsonl(input_path):
        # YOUR CODE: Call your LLM app
        response = your_llm_app.generate(row["input"])

        row["output"] = response
        results.append(row)

    write_jsonl(output_path, results)
```

### 4. Generate Test Data

```bash
company-eval generate-dataset \
  --app-type simple_chat \
  --output my_evals/data/eval_dataset.jsonl \
  --num-examples 20 \
  --description "Customer support bot for billing questions"
```

### 5. Run Evaluation

```bash
company-eval ci-run --config my_evals/configs/eval_config.yaml
```

---

## Example Output

```
======================================================================
  LLM EVALUATION PIPELINE
======================================================================

App Name: customer_support_bot
Eval Suite: basic_chat

Running evaluation suite...
  Evaluators: user_frustration, toxicity, helpfulness_quality

----------------------------------------------------------------------
  Metric Summary
----------------------------------------------------------------------
Metric                       Score       Threshold     Status
------------------------------------------------------------
user_frustration              0.05         <= 0.30  [OK] PASS
toxicity                      0.00             N/A  [OK] PASS
helpfulness_quality           0.92         >= 0.70  [OK] PASS

======================================================================
  FINAL RESULT: PASS
======================================================================
```

---

## Configuration

```yaml
# eval_config.yaml
app_name: my_chatbot
app_type: simple_chat  # simple_chat | rag | agent | multi_agent

adapter:
  module: "my_evals.my_adapter"
  function: "run_batch"

dataset:
  mode: "static"  # static | synthetic
  path: "my_evals/data/eval_dataset.jsonl"

eval_suite: "basic_chat"  # basic_chat | basic_rag | agent | multi_agent

thresholds:
  user_frustration:
    max_mean: 0.3    # Fail if > 30% of responses frustrate users
  helpfulness_quality:
    min_mean: 0.7    # Fail if < 70% of responses are helpful
```

---

## GitHub Actions Integration

The included workflow supports three modes:

| Trigger | Mode | Use Case |
|---------|------|----------|
| Push/PR | Static only | Fast regression testing |
| Manual | Static | Regression testing |
| Manual | Synthetic | Broader coverage with fresh test cases |
| Manual | Both | Full validation before releases |

### Setting Up Secrets

Add these to your repo's GitHub Secrets:

```
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_CHAT_DEPLOYMENT
AZURE_OPENAI_EMBEDDING_DEPLOYMENT
AZURE_OPENAI_API_VERSION
```

Or for standard OpenAI:
```
OPENAI_API_KEY
```

---

## Evaluation Suites

### Basic Chat
For simple Q&A or conversational interfaces.

| Metric | What It Measures |
|--------|------------------|
| `user_frustration` | Would the user be frustrated by this response? |
| `toxicity` | Is the response toxic or inappropriate? |
| `helpfulness_quality` | Is the response actually helpful? |

### RAG (Retrieval-Augmented Generation)
For apps that retrieve documents and generate answers.

| Metric | What It Measures |
|--------|------------------|
| `hallucination` | Does the response contain info not in the retrieved docs? |
| `document_relevance` | Are the retrieved documents relevant to the query? |
| `answer_quality` | Is the answer correct based on the retrieved context? |

### Agent
For tool-using AI agents.

| Metric | What It Measures |
|--------|------------------|
| `planning_quality` | Is the agent's plan appropriate for the request? |
| `tool_use_appropriateness` | Did the agent use tools correctly? |

### Multi-Agent
For systems with multiple coordinating agents.

| Metric | What It Measures |
|--------|------------------|
| `overall_answer_quality` | Is the final collaborative output good? |
| `planning_quality` | Did the planning agent do its job well? |

---

## CLI Reference

```bash
# Initialize a new project
company-eval init <directory>

# Generate synthetic test data
company-eval generate-dataset \
  --app-type <simple_chat|rag|agent|multi_agent> \
  --output <path.jsonl> \
  --num-examples <n> \
  --description "Your app description"

# Run evaluation
company-eval ci-run --config <config.yaml>

# Help
company-eval --help
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your LLM App                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Adapter (you write)                         │
│  run_batch(input.jsonl, output.jsonl)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Eval Framework (this tool)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Dataset    │  │  Evaluators  │  │   Metrics    │          │
│  │  Generator   │  │ (LLM Judge)  │  │  & Thresholds│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline                           │
│  ✓ Pass → Merge allowed    ✗ Fail → PR blocked                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why This Matters

| Before | After |
|--------|-------|
| "I think the new prompt is better" | Quantified quality scores |
| Ship and hope | Automated quality gates |
| Manual testing before release | CI/CD catches regressions |
| Each team builds their own evals | Standardized across company |
| "Users are complaining" | Catch issues before production |

---

## Roadmap

- [ ] Dashboard for tracking quality trends over time
- [ ] Production traffic sampling (`company-eval sample-prod`)
- [ ] Custom evaluator templates
- [ ] Slack/Teams notifications on failures
- [ ] Cost tracking per evaluation run

---

## Built With

- [Phoenix Evals](https://github.com/Arize-ai/phoenix) - LLM evaluation library
- [OpenAI / Azure OpenAI](https://openai.com/) - LLM judge for evaluations
- Python 3.12+

---

## Contributing

This is an internal tool. To add new evaluation suites or features:

1. Fork the repo
2. Create a feature branch
3. Add tests
4. Submit a PR

---

## License

Internal use only.

---

**Questions?** Reach out to the AI Platform team.

**Ready to start?** Run `company-eval init my_project` and ship with confidence.
