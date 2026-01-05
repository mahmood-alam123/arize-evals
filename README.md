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

### When Things Go Wrong

When evaluations fail, you get actionable diagnostics:

```
======================================================================
  LLM EVALUATION PIPELINE
======================================================================

App Name: customer_support_bot
Eval Suite: basic_rag

Running evaluation suite...
  Evaluators: hallucination, document_relevance, answer_quality

----------------------------------------------------------------------
  Metric Summary
----------------------------------------------------------------------
Metric                       Score       Threshold     Status
------------------------------------------------------------
hallucination                 0.35         <= 0.10  [!!] FAIL
document_relevance            0.78         >= 0.80  [!!] FAIL
answer_quality                0.65         >= 0.70  [!!] FAIL

----------------------------------------------------------------------
  Failure Analysis
----------------------------------------------------------------------
Failure type distribution:
  - hallucination: 7 (50%)
  - irrelevant_retrieval: 4 (29%)
  - incomplete_answer: 3 (21%)

Example failures:

[hallucination] Row 12:
  INPUT: What is the return window for electronics?
  RETRIEVED: "General merchandise can be returned within 30 days..."
  OUTPUT: "Electronics have a 90-day return window with full refund."
  ISSUE: Response contains information not present in retrieved context.

[irrelevant_retrieval] Row 8:
  INPUT: How do I cancel my subscription?
  RETRIEVED: "Shipping rates vary by destination..." (relevance: 0.12)
  ISSUE: Retrieved documents don't address the user's question.

[incomplete_answer] Row 15:
  INPUT: What payment methods do you accept?
  OUTPUT: "We accept credit cards."
  ISSUE: Response missing debit, PayPal, and Apple Pay from context.

----------------------------------------------------------------------
  Recommendations
----------------------------------------------------------------------
1. HALLUCINATION: Review prompt to emphasize grounding in retrieved context
2. RETRIEVAL: Check embedding model or chunk size for relevance issues
3. COMPLETENESS: Consider adding instruction to include all relevant details

======================================================================
  FINAL RESULT: FAIL (3 metrics below threshold)
======================================================================
```

This detailed output helps you quickly identify and fix the root cause.

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

## Iterative Improvement Workflow

The eval framework enables a fast feedback loop for improving your LLM app locally:

```
Run Eval → See Failures → Analyze Root Cause → Make Changes → Re-run → See Improvement
```

Below are practical examples for each app type.

---

### Example 1: Simple Chat - Reducing User Frustration

A customer support chatbot is frustrating users with generic responses.

**Configuration:**
```yaml
app_name: support-bot
app_type: simple_chat
eval_suite: basic_chat
thresholds:
  user_frustration:
    max_mean: 0.30
  helpfulness_quality:
    min_mean: 0.70
```

**Initial Run:**
```bash
company-eval ci-run --config eval_config.yaml
```

```
Metric                       Score       Threshold     Status
------------------------------------------------------------
user_frustration              0.45         <= 0.30  [!!] FAIL
helpfulness_quality           0.72         >= 0.70  [OK] PASS

Failure Analysis:
  - generic_response: 5 (45%)
  - missed_question: 3 (27%)
  - no_acknowledgment: 3 (27%)
```

**The Problem:** Bot responds with generic templates without acknowledging the user's specific issue.

**The Fix:** Update system prompt to be more empathetic:
```python
# Before
SYSTEM_PROMPT = "You are a helpful assistant."

# After
SYSTEM_PROMPT = """You are a helpful customer support assistant.
- First, acknowledge the user's specific concern
- Be empathetic and understanding
- Then provide a clear, actionable solution"""
```

**After the Fix:**
```bash
company-eval ci-run --config eval_config.yaml
```

```
Metric                       Score       Threshold     Status
------------------------------------------------------------
user_frustration              0.22         <= 0.30  [OK] PASS
helpfulness_quality           0.78         >= 0.70  [OK] PASS

FINAL RESULT: PASS
```

---

### Example 2: RAG - Eliminating Hallucinations

A documentation Q&A bot is making up information not in the source documents.

**Configuration:**
```yaml
app_name: docs-qa
app_type: rag
eval_suite: basic_rag
thresholds:
  hallucination:
    max_mean: 0.20
  answer_quality:
    min_mean: 0.75
```

**Initial Run:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
hallucination                 0.40         <= 0.20  [!!] FAIL
document_relevance            0.82         >= 0.80  [OK] PASS
answer_quality                0.65         >= 0.75  [!!] FAIL

Failure Analysis:
  - hallucination: 8 (67%)
  - incomplete_answer: 4 (33%)
```

**The Problem:** Model invents features and details not present in retrieved context.

**The Fix:** Strengthen grounding and lower creativity:
```python
# Before
SYSTEM_PROMPT = "Answer the user's question based on the provided context."

# After
SYSTEM_PROMPT = """Answer the user's question using ONLY the provided context.
- If the answer is not in the context, say "I don't have that information"
- Never make up features, prices, or details
- Quote directly from the context when possible"""

# Also reduce temperature
response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.1,  # Was 0.7
    messages=messages
)
```

**After the Fix:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
hallucination                 0.12         <= 0.20  [OK] PASS
document_relevance            0.85         >= 0.80  [OK] PASS
answer_quality                0.81         >= 0.75  [OK] PASS

FINAL RESULT: PASS
```

---

### Example 3: Agent - Improving Tool Selection

A task automation agent is calling tools unnecessarily and making poor selections.

**Configuration:**
```yaml
app_name: task-agent
app_type: agent
eval_suite: agent
thresholds:
  tool_use_appropriateness:
    min_mean: 0.80
  planning_quality:
    min_mean: 0.75
```

**Initial Run:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
tool_use_appropriateness      0.55         >= 0.80  [!!] FAIL
planning_quality              0.70         >= 0.75  [!!] FAIL

Failure Analysis:
  - unnecessary_api_call: 6 (40%)
  - wrong_tool_selected: 5 (33%)
  - missing_tool_call: 4 (27%)
```

**The Problem:** Agent calls search API when data is already in memory, selects wrong tools.

**The Fix:** Improve tool descriptions and add explicit planning step:
```python
# Before
tools = [
    {"name": "search", "description": "Search for information"},
    {"name": "calculate", "description": "Do math"},
]

# After - Clearer descriptions with when to use
tools = [
    {
        "name": "search_external",
        "description": "Search external sources. Use ONLY when information is not in the conversation or provided context."
    },
    {
        "name": "calculate",
        "description": "Perform mathematical calculations. Use for any numeric operations."
    },
]

# Add planning instruction
SYSTEM_PROMPT = """Before taking any action:
1. List what information you already have
2. Identify what's missing
3. Choose the most direct tool to get missing info
4. Explain your tool choice before calling it"""
```

**After the Fix:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
tool_use_appropriateness      0.88         >= 0.80  [OK] PASS
planning_quality              0.82         >= 0.75  [OK] PASS

FINAL RESULT: PASS
```

---

### Example 4: Multi-Agent - Better Coordination

A research multi-agent system produces redundant work with incoherent final outputs.

**Configuration:**
```yaml
app_name: research-system
app_type: multi_agent
eval_suite: multi_agent
thresholds:
  overall_answer_quality:
    min_mean: 0.80
  planning_quality:
    min_mean: 0.75
```

**Initial Run:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
overall_answer_quality        0.60         >= 0.80  [!!] FAIL
planning_quality              0.68         >= 0.75  [!!] FAIL

Failure Analysis:
  - redundant_work: 5 (38%)
  - poor_synthesis: 4 (31%)
  - missing_handoff: 4 (31%)
```

**The Problem:** Agents work on overlapping tasks, no clear synthesis step.

**The Fix:** Add explicit handoff protocol and synthesis agent:
```python
# Before - loose coordination
agents = [research_agent, analysis_agent]
result = run_agents(agents, query)

# After - structured workflow with handoffs
ORCHESTRATOR_PROMPT = """You coordinate a research team:
1. PLAN: Break the query into distinct, non-overlapping sub-tasks
2. ASSIGN: Give each agent ONE specific sub-task
3. COLLECT: Gather all agent outputs
4. SYNTHESIZE: Combine into a coherent final answer

After each agent completes, summarize what they found before moving to the next."""

# Add synthesis step
agents = [research_agent, analysis_agent, synthesis_agent]
result = run_agents_with_handoffs(agents, query, orchestrator=ORCHESTRATOR_PROMPT)
```

**After the Fix:**
```
Metric                       Score       Threshold     Status
------------------------------------------------------------
overall_answer_quality        0.85         >= 0.80  [OK] PASS
planning_quality              0.79         >= 0.75  [OK] PASS

FINAL RESULT: PASS
```

---

### Tips for Effective Iteration

| Tip | Why It Helps |
|-----|--------------|
| **Start with 5-10 test cases** | Fast feedback loop, quick iterations |
| **Fix one metric at a time** | Easier to isolate what works |
| **Read the failure analysis** | Axial coding tells you *why* things fail |
| **Track changes with git** | Know which change improved which metric |
| **Increase dataset size later** | Once core issues fixed, test broader coverage |
| **Use static datasets for regression** | Same inputs = reliable trend tracking |

---

## Recently Shipped

| Feature | Description |
|---------|-------------|
| **Quality Dashboard** | Web UI for tracking evaluation trends over time, comparing branches, and drilling into failures |
| **Slack/Teams Notifications** | Alert channels when CI evals fail with summary and links to details |
| **Custom Evaluator Templates** | Define your own LLM-as-judge evaluators with custom prompts and rubrics |
| **Cost Tracking** | Track OpenAI/Azure spend per evaluation run with budget alerts |
| **MCP Server** | Model Context Protocol server enabling AI assistants to run evals, check results, and manage datasets conversationally |

## Roadmap

### Near-Term

| Feature | Description |
|---------|-------------|
| **Production Traffic Sampling** | `company-eval sample-prod` to pull real user interactions for evaluation |
| **A/B Experiment Analysis** | Compare evaluation metrics between model versions or prompt variants |

### Long-Term Vision

| Feature | Description |
|---------|-------------|
| **Auto-Generated Test Cases** | Automatically generate adversarial and edge-case inputs based on failure patterns |
| **Human-in-the-Loop Calibration** | UI for humans to label samples and calibrate LLM judges against human judgment |
| **Continuous Production Monitoring** | Always-on sampling and evaluation of production traffic with anomaly detection |
| **Multi-Model Comparison** | Run same inputs through multiple models and compare quality/cost tradeoffs |

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

**Ready to start?** Run `company-eval init my_project` and ship with confidence.