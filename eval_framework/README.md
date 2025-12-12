# Company Eval Framework

A reusable evaluation framework that wraps [Phoenix Evals](https://docs.arize.com/phoenix/evaluation/how-to-evals/running-pre-tested-evals) + OpenAI for systematic LLM application testing.

## Overview

This framework provides a standardized way for teams to evaluate their LLM applications:

- **Configuration-driven**: Define your evaluation in a simple YAML file
- **Multiple app types**: Support for chat, RAG, single-agent, and multi-agent apps
- **Flexible datasets**: Load static test data or generate synthetic examples
- **Built-in evaluators**: Pre-configured evaluation suites using Phoenix Evals
- **Failure analysis**: Axial coding to categorize and understand failures
- **CI/CD ready**: CLI with exit codes for pipeline integration

## Installation

```bash
pip install -e ./eval_framework
```

## Quick Start

### 1. Create a config file

```yaml
# llm_eval_simple_chat.yaml
app_name: my-chatbot
app_type: simple_chat

adapter:
  module: my_app.eval_adapter
  function: run_batch

dataset:
  mode: static
  path: tests/test_data.jsonl

eval_suite: basic_chat

thresholds:
  user_frustration:
    max_mean: 0.3
  toxicity:
    max_mean: 0.05
```

### 2. Create an adapter function

```python
# my_app/eval_adapter.py
from my_app import generate_response
import json

def run_batch(input_path: str, output_path: str) -> None:
    """Process inputs and write outputs."""
    with open(input_path) as f:
        inputs = [json.loads(line) for line in f]

    outputs = []
    for item in inputs:
        response = generate_response(item["input"])
        outputs.append({**item, "output": response})

    with open(output_path, "w") as f:
        for item in outputs:
            f.write(json.dumps(item) + "\n")
```

### 3. Run the evaluation

```bash
export OPENAI_API_KEY=your-key
company-eval ci-run --config llm_eval_simple_chat.yaml
```

## Configuration

### App Types

- `simple_chat`: Basic Q&A or conversational chatbots
- `rag`: Retrieval-augmented generation applications
- `agent`: Single-agent with tool use
- `multi_agent`: Multi-agent collaborative systems

### Dataset Modes

**Static**: Load from a JSONL file
```yaml
dataset:
  mode: static
  path: tests/my_dataset.jsonl
```

**Synthetic**: Generate using an LLM
```yaml
dataset:
  mode: synthetic
  num_examples: 20
  generation_model: gpt-4o-mini
  description: Customer support chatbot for a SaaS product
```

### Evaluation Suites

- `basic_chat`: user_frustration, toxicity, helpfulness_quality
- `basic_rag`: hallucination, document_relevance, answer_quality
- `agent`: planning_quality, tool_use_appropriateness
- `multi_agent`: overall_answer_quality, planning_quality

### Thresholds

Define pass/fail criteria per metric:

```yaml
thresholds:
  hallucination:
    max_mean: 0.1    # Failure rate must be <= 10%
  answer_quality:
    min_mean: 0.7    # Success rate must be >= 70%
```

## CLI Commands

```bash
# Run CI evaluation
company-eval ci-run --config path/to/config.yaml

# Production sampling (coming soon)
company-eval sample-prod --config path/to/config.yaml
```

## Programmatic Usage

```python
from company_eval_framework import (
    load_eval_config,
    build_dataset,
    build_eval_suite,
    run_evaluations_sync,
    get_llm_judge,
)

# Load config
config = load_eval_config("llm_eval_simple_chat.yaml")

# Build dataset
df = build_dataset(config)

# Run evaluations
evaluators = build_eval_suite(config.eval_suite)
llm = get_llm_judge()
results = run_evaluations_sync(df, evaluators, llm)
```

## Output Format

The framework outputs a human-readable summary:

```
==================================================
  Company LLM Evaluation
==================================================

App Name: example-simple-chat
App Type: simple_chat
Eval Suite: basic_chat
Dataset Size: 5 rows (static)

Running adapter: example_team_app.eval_adapter.run_simple_llm_batch
  Adapter completed successfully
  Loaded 5 model outputs

--------------------------------------------------
  Metric Summary (Mean Scores)
--------------------------------------------------
Metric                     Mean     Threshold       Status
------------------------------------------------------------
user_frustration           0.12     <= 0.30          PASS
toxicity                   0.00     <= 0.05          PASS
helpfulness_quality        0.87     >= 0.70          PASS

All metrics satisfy their thresholds.

--------------------------------------------------
  FINAL RESULT: PASS
--------------------------------------------------
```

## Architecture

```
eval_framework/
├── pyproject.toml
├── README.md
└── src/company_eval_framework/
    ├── __init__.py      # Public API exports
    ├── config.py        # Pydantic config models
    ├── dataset.py       # Dataset loading/generation
    ├── evaluators.py    # Phoenix Evals wrappers
    ├── axial.py         # Failure classification
    ├── runner.py        # Main orchestration
    ├── cli.py           # Command-line interface
    └── utils.py         # Helper functions
```

## License

MIT
