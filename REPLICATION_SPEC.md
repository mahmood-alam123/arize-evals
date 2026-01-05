# LLM Evaluation Framework - Complete Replication Specification

> **Purpose**: This document provides a complete specification to replicate the Company Eval Framework from scratch. It includes architecture, data models, API contracts, UI components, and implementation details.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Eval Framework (Python CLI)](#3-eval-framework-python-cli)
4. [Web Backend (FastAPI)](#4-web-backend-fastapi)
5. [Web Frontend (React)](#5-web-frontend-react)
6. [Data Formats & Contracts](#6-data-formats--contracts)
7. [Configuration Schema](#7-configuration-schema)
8. [CI/CD Integration](#8-cicd-integration)
9. [Docker Deployment](#9-docker-deployment)
10. [Refactoring Opportunities](#10-refactoring-opportunities)

---

## 1. Project Overview

### What This Is

An LLM evaluation platform that brings CI/CD-style quality gates to AI applications. Teams can:

- Run automated evaluations against their LLM apps
- Define pass/fail thresholds for quality metrics
- View results in a web dashboard
- Track traces and debug failures
- Integrate with Slack/Teams for notifications

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Adapter** | User-defined function that runs their LLM app on test inputs |
| **Dataset** | Test cases (static files, synthetic generation, or from dashboard) |
| **Eval Suite** | Predefined set of LLM-judge evaluators for an app type |
| **Threshold** | Pass/fail criteria for each metric (min/max bounds) |
| **Axial Coding** | LLM-based failure classification for debugging |
| **Trace** | End-to-end request through an LLM app with nested spans |

### App Types Supported

1. **simple_chat** - Basic Q&A chatbots
2. **rag** - Retrieval-augmented generation apps
3. **agent** - Single tool-using agents
4. **multi_agent** - Multi-agent orchestration systems

---

## 2. Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Codebase                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ LLM App     │  │ Adapter Fn  │  │ eval_config.yaml        │  │
│  │ (their code)│  │ (bridge)    │  │ (configuration)         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Eval Framework (Python CLI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ Config   │→ │ Dataset  │→ │ Runner   │→ │ Evaluators      │  │
│  │ Loader   │  │ Builder  │  │          │  │ (Phoenix Evals) │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘  │
│                                    │                             │
│                                    ▼                             │
│                            ┌──────────────┐                      │
│                            │ Axial Coding │                      │
│                            │ (Failure Dx) │                      │
│                            └──────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (--report-to)
┌─────────────────────────────────────────────────────────────────┐
│                     Web Dashboard                                │
│  ┌────────────────────────┐  ┌────────────────────────────────┐ │
│  │ Backend (FastAPI)      │  │ Frontend (React + Tailwind)    │ │
│  │ - /api/runs            │  │ - Dashboard (runs list)        │ │
│  │ - /api/datasets        │  │ - Run Details (metrics/cases)  │ │
│  │ - /api/traces          │  │ - Compare (side-by-side)       │ │
│  │ - /api/integrations    │  │ - Traces (LLM call browser)    │ │
│  │ - SQLite DB            │  │ - Datasets (management)        │ │
│  └────────────────────────┘  │ - Docs (15+ pages)             │ │
│                              └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
/
├── eval_framework/
│   ├── pyproject.toml              # Python package config
│   └── src/company_eval_framework/
│       ├── __init__.py             # Public exports
│       ├── cli.py                  # CLI commands (~600 lines)
│       ├── config.py               # Pydantic config models (~240 lines)
│       ├── dataset.py              # Dataset loading/generation (~350 lines)
│       ├── evaluators.py           # LLM judge wrappers (~820 lines)
│       ├── axial.py                # Failure classification (~180 lines)
│       ├── runner.py               # Orchestration (~550 lines)
│       └── utils.py                # Helpers (~100 lines)
│
├── web/
│   ├── docker-compose.yml          # Local dev setup
│   ├── Dockerfile                  # Production multi-stage
│   ├── backend/
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py             # FastAPI app setup
│   │       ├── database.py         # SQLAlchemy models (11 tables)
│   │       ├── schemas.py          # Pydantic request/response
│   │       ├── seed.py             # Demo data seeding
│   │       └── api/
│   │           ├── runs.py         # Runs CRUD
│   │           ├── datasets.py     # Datasets CRUD
│   │           ├── traces.py       # Traces CRUD
│   │           └── integrations.py # Webhooks CRUD
│   └── frontend/
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── src/
│           ├── App.tsx             # Router
│           ├── main.tsx            # Entry
│           ├── index.css           # Tailwind imports
│           ├── components/
│           │   ├── Header.tsx
│           │   └── DocsLayout.tsx
│           └── pages/
│               ├── Landing.tsx
│               ├── Dashboard.tsx
│               ├── RunDetails.tsx
│               ├── Compare.tsx
│               ├── Traces.tsx
│               ├── TraceDetails.tsx
│               ├── DatasetsPage.tsx
│               └── docs/           # 15+ documentation pages
│
├── example_team_project/           # Demo showing framework usage
│   ├── my_app/
│   │   ├── app.py                  # Example LLM app
│   │   └── eval_adapter.py         # Adapter functions
│   ├── eval_config*.yaml           # Example configs
│   └── data/                       # Sample datasets
│
└── .github/workflows/eval.yml      # CI/CD pipeline
```

---

## 3. Eval Framework (Python CLI)

### 3.1 CLI Commands

```bash
# Main evaluation command
company-eval ci-run --config eval_config.yaml [--report-to URL]

# Generate synthetic test data
company-eval generate-dataset \
  --app-type simple_chat|rag|agent|multi_agent \
  --output dataset.jsonl \
  --num-examples 20 \
  --description "Customer support chatbot" \
  --model gpt-4o-mini

# Initialize new project
company-eval init

# Start dashboard server
company-eval dashboard --port 8080
```

### 3.2 Configuration Models (Pydantic)

```python
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

class AdapterConfig(BaseModel):
    """Bridge between framework and user's app."""
    module: str  # e.g., "my_app.eval_adapter"
    function: str  # e.g., "run_batch"

class DatasetConfig(BaseModel):
    """Dataset source configuration."""
    mode: Literal["static", "synthetic", "dashboard"]
    path: Optional[str] = None  # For static mode
    dataset_name: Optional[str] = None  # For dashboard mode
    dashboard_url: str = "http://localhost:8000"
    num_examples: int = 20  # For synthetic mode
    generation_model: str = "gpt-4o-mini"
    description: Optional[str] = None
    prompt_files: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_mode_requirements(self):
        if self.mode == "static" and not self.path:
            raise ValueError("path required for static mode")
        if self.mode == "dashboard" and not self.dataset_name:
            raise ValueError("dataset_name required for dashboard mode")
        return self

class CustomEvaluatorConfig(BaseModel):
    """Reference to user-defined evaluator class."""
    module: str  # e.g., "my_evaluators"
    class_name: str = Field(alias="class")  # e.g., "BrandVoiceEvaluator"

class ThresholdConfig(BaseModel):
    """Pass/fail bounds for a metric."""
    max_mean: Optional[float] = None  # Failure rate must be <= this
    min_mean: Optional[float] = None  # Success rate must be >= this

    @model_validator(mode="after")
    def validate_at_least_one_bound(self):
        if self.max_mean is None and self.min_mean is None:
            raise ValueError("At least one of max_mean or min_mean required")
        return self

class EvalConfig(BaseModel):
    """Main configuration model."""
    app_name: str
    app_type: Literal["simple_chat", "rag", "agent", "multi_agent"]
    adapter: AdapterConfig
    dataset: DatasetConfig
    eval_suite: Optional[str] = None  # "basic_chat", "basic_rag", "agent", "multi_agent"
    custom_evaluators: List[CustomEvaluatorConfig] = []
    thresholds: Dict[str, ThresholdConfig] = {}

    @model_validator(mode="after")
    def validate_has_evaluators(self):
        if not self.eval_suite and not self.custom_evaluators:
            raise ValueError("eval_suite or custom_evaluators required")
        return self

def load_eval_config(path: str) -> EvalConfig:
    """Load and validate YAML config."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    return EvalConfig(**raw)
```

### 3.3 Evaluators (LLM Judges)

The framework uses Phoenix Evals for LLM-as-judge evaluations.

#### EvaluatorSpec Class

```python
class EvaluatorSpec:
    def __init__(
        self,
        name: str,               # Metric name, e.g., "hallucination"
        template: str,           # Prompt template for LLM judge
        rails_map: Dict[str, str],  # Output classification mapping
        input_columns: List[str],   # Required DataFrame columns
        positive_label: str,     # Label indicating success
    ):
        self.name = name
        self.template = template
        self.rails_map = rails_map
        self.input_columns = input_columns
        self.positive_label = positive_label
```

#### Evaluation Suites

**basic_chat** (for simple Q&A):
- `user_frustration` - Would response frustrate user?
- `toxicity` - Is response toxic/inappropriate?
- `helpfulness_quality` - Is response helpful?

**basic_rag** (for RAG apps):
- `hallucination` - Info not grounded in context?
- `document_relevance` - Retrieved docs relevant?
- `answer_quality` - Answer correct per context?

**agent** (for tool-using agents):
- `planning_quality` - Is plan appropriate?
- `tool_use_appropriateness` - Tools used correctly?

**multi_agent** (for multi-agent systems):
- `overall_answer_quality` - Final output quality?
- `planning_quality` - Coordination quality?

#### Additional Available Metrics

- `answer_relevance` - Response addresses question?
- `coherence` - Logically coherent?
- `conciseness` - Appropriately concise?
- `factual_accuracy` - Factually accurate?
- `moderation` - Safe and appropriate?
- `context_precision` - Context focused and relevant?
- `context_recall` - Context complete?

#### Prompt Template Example

```python
USER_FRUSTRATION_PROMPT_TEMPLATE = """
You are evaluating whether a chatbot response would cause user frustration.

[User Query]
{input}

[Chatbot Response]
{output}

Evaluate whether the response would likely frustrate the user. Consider:
- Does it answer the question?
- Is it helpful and actionable?
- Is the tone appropriate?
- Does it avoid unnecessary jargon or confusion?

Respond with one of: frustrated, not_frustrated
"""

USER_FRUSTRATION_RAILS_MAP = {
    "frustrated": "frustrated",
    "not_frustrated": "not_frustrated",
}
```

#### Running Evaluations

```python
def get_llm_judge(model: Optional[str] = None) -> OpenAIModel:
    """Get LLM judge (supports Azure OpenAI if env vars set)."""
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if azure_endpoint and azure_deployment:
        return OpenAIModel(
            model=model or "gpt-4o",
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    return OpenAIModel(model=model or "gpt-4o-mini")

async def run_evaluations(
    df: pd.DataFrame,
    evaluators: List[EvaluatorSpec],
    llm: Optional[OpenAIModel] = None,
) -> pd.DataFrame:
    """Run all evaluators on DataFrame."""
    if llm is None:
        llm = get_llm_judge()

    result_df = df.copy()

    for evaluator in evaluators:
        eval_result = llm_classify(
            dataframe=df,
            template=evaluator.template,
            model=llm,
            rails=list(evaluator.rails_map.keys()),
            provide_explanation=True,
        )

        result_df[f"{evaluator.name}_label"] = eval_result["label"]
        result_df[f"{evaluator.name}_score"] = (
            eval_result["label"] == evaluator.positive_label
        ).astype(float)
        result_df[f"{evaluator.name}_explanation"] = eval_result.get("explanation", "")

    return result_df
```

### 3.4 Axial Coding (Failure Classification)

```python
FAILURE_TYPES = [
    "retrieval_error",  # System failed to retrieve relevant info
    "hallucination",    # Made-up info not in context
    "formatting",       # Format issues (content OK)
    "refusal",          # Refused when should answer
    "irrelevant",       # Doesn't address question
    "other",            # Doesn't fit categories
]

AXIAL_CODING_PROMPT = """
You are analyzing why an LLM response failed quality checks.

[User Input]
{input}

[Model Output]
{output}

{context_section}

Classify the failure into one of these types:
- retrieval_error: Failed to retrieve relevant information
- hallucination: Contains info not supported by context
- formatting: Format issues but content is OK
- refusal: Refused to answer when it should have
- irrelevant: Response doesn't address the question
- other: Doesn't fit other categories

Respond with the failure type and a brief explanation.
"""

def run_axial_coding_sync(failures_df: pd.DataFrame, llm) -> pd.DataFrame:
    """Classify each failure into a failure type."""
    # Adds: failure_type, failure_type_explanation columns
    ...

def summarize_failure_types(coded_df: pd.DataFrame) -> dict:
    """Return counts, percentages, top_types."""
    ...
```

### 3.5 Runner (Orchestration)

```python
@dataclass
class EvaluationResults:
    passed: bool
    app_name: str
    app_type: str
    eval_suite: str
    config_path: str
    dataset_size: int
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    total_cost: Optional[float] = None
    app_cost: Optional[float] = None
    eval_cost: Optional[float] = None
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    test_cases: List[Dict[str, Any]] = field(default_factory=list)

def run_ci_evaluation(config_path: str, return_results: bool = False):
    """
    Main evaluation pipeline:
    1. Load config
    2. Build dataset
    3. Run adapter (user's app)
    4. Run evaluators
    5. Compute metrics
    6. Check thresholds
    7. Run axial coding on failures
    8. Return exit code (0=pass, 1=fail) or EvaluationResults
    """
    started_at = datetime.utcnow()
    git_branch, git_commit = _get_git_info()

    # Load config
    config = load_eval_config(config_path)

    # Build dataset
    dataset_df = build_dataset(config)

    # Run adapter via dynamic import
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "inputs.jsonl")
        output_path = os.path.join(tmpdir, "outputs.jsonl")

        write_jsonl(dataset_df, input_path)

        adapter_module = importlib.import_module(config.adapter.module)
        adapter_fn = getattr(adapter_module, config.adapter.function)
        adapter_fn(input_path, output_path)

        outputs_df = read_jsonl(output_path)

    # Run evaluators
    evaluators = build_eval_suite(config.eval_suite) if config.eval_suite else []
    if config.custom_evaluators:
        evaluators.extend(_load_custom_evaluators(config.custom_evaluators))

    llm = get_llm_judge()
    eval_results = run_evaluations_sync(outputs_df, evaluators, llm)

    # Compute metrics and check thresholds
    metric_results = compute_metrics(eval_results, evaluators, config.thresholds)
    all_passed = all(m["passed"] for m in metric_results)

    # Run axial coding on failures
    failure_mask = pd.Series([False] * len(eval_results))
    for evaluator in evaluators:
        score_col = f"{evaluator.name}_score"
        if score_col in eval_results.columns:
            failure_mask |= (eval_results[score_col] < 1.0)

    failures_df = eval_results[failure_mask]
    coded_failures = run_axial_coding_sync(failures_df, llm) if not failures_df.empty else None

    # Return
    finished_at = datetime.utcnow()
    if return_results:
        return EvaluationResults(
            passed=all_passed,
            app_name=config.app_name,
            # ... all fields
        )
    return 0 if all_passed else 1
```

### 3.6 Dataset Module

```python
def build_dataset(config: EvalConfig) -> pd.DataFrame:
    """Dispatch to appropriate loader based on mode."""
    if config.dataset.mode == "static":
        return load_static_dataset(config)
    elif config.dataset.mode == "synthetic":
        return generate_synthetic_dataset(config)
    elif config.dataset.mode == "dashboard":
        return load_dashboard_dataset(config)

def load_static_dataset(config: EvalConfig) -> pd.DataFrame:
    """Load from JSONL or CSV file."""
    path = config.dataset.path
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_json(path, lines=True)

    # Validate required columns
    required = ["conversation_id", "input"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df

def generate_synthetic_dataset(config: EvalConfig) -> pd.DataFrame:
    """Generate test cases using LLM."""
    # Uses OpenAI to generate diverse test cases
    # App-type-specific prompts
    # Returns DataFrame with conversation_id, input, context (if RAG)
    ...

def load_dashboard_dataset(config: EvalConfig) -> pd.DataFrame:
    """Fetch from Quality Dashboard API."""
    url = f"{config.dataset.dashboard_url}/api/datasets/by-name/{config.dataset.dataset_name}"
    response = requests.get(url)
    data = response.json()

    examples = []
    for ex in data["examples"]:
        examples.append({
            "conversation_id": str(ex["id"]),
            "input": ex["input"],
            "context": ex.get("context"),
            "expected_output": ex.get("expected_output"),
        })

    return pd.DataFrame(examples)
```

---

## 4. Web Backend (FastAPI)

### 4.1 Database Models (SQLAlchemy)

```python
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Run(Base):
    """An evaluation run."""
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    app_name = Column(String, nullable=False)
    app_type = Column(String, nullable=False)
    eval_suite = Column(String, nullable=False)
    dataset_size = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    git_branch = Column(String, nullable=True)
    git_commit = Column(String, nullable=True)
    config_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_cost = Column(Float, nullable=True)
    app_cost = Column(Float, nullable=True)
    eval_cost = Column(Float, nullable=True)

    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_runs_app_name", "app_name"),
        Index("idx_runs_started_at", "started_at"),
    )

class Metric(Base):
    """Metric results for a run."""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    name = Column(String, nullable=False)
    mean_score = Column(Float, nullable=False)
    failure_rate = Column(Float, nullable=False)
    threshold_type = Column(String, nullable=True)  # "min" or "max"
    threshold_value = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False)

    run = relationship("Run", back_populates="metrics")

class TestCase(Base):
    """Individual test case in a run."""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    conversation_id = Column(String, nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # For RAG
    prompt = Column(Text, nullable=True)
    trace_id = Column(String, ForeignKey("traces.id"), nullable=True)

    run = relationship("Run", back_populates="test_cases")
    scores = relationship("TestCaseScore", back_populates="test_case", cascade="all, delete-orphan")
    failure = relationship("Failure", back_populates="test_case", uselist=False, cascade="all, delete-orphan")

class TestCaseScore(Base):
    """Per-metric score for a test case."""
    __tablename__ = "test_case_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    label = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)

    test_case = relationship("TestCase", back_populates="scores")

class Failure(Base):
    """Failure analysis for a test case."""
    __tablename__ = "failures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    failure_type = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)

    test_case = relationship("TestCase", back_populates="failure")

class Trace(Base):
    """End-to-end request trace."""
    __tablename__ = "traces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    project_name = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String, default="running")  # running, completed, error
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    trace_metadata = Column(Text, nullable=True)  # JSON
    total_tokens = Column(Integer, nullable=True)
    total_cost = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_traces_project_name", "project_name"),
        Index("idx_traces_start_time", "start_time"),
    )

class Span(Base):
    """Single operation within a trace."""
    __tablename__ = "spans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String, ForeignKey("traces.id"), nullable=False)
    parent_span_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    span_type = Column(String, nullable=False)  # llm, tool, retrieval, chain, agent, custom
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String, default="running")
    input = Column(Text, nullable=True)  # JSON
    output = Column(Text, nullable=True)  # JSON
    model = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    tool_name = Column(String, nullable=True)
    tool_args = Column(Text, nullable=True)  # JSON
    error_message = Column(Text, nullable=True)
    span_metadata = Column(Text, nullable=True)  # JSON

    trace = relationship("Trace", back_populates="spans")

class Dataset(Base):
    """Named evaluation dataset."""
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    app_type = Column(String, nullable=True)
    num_examples = Column(Integer, default=0)
    source = Column(String, nullable=True)  # upload, run_import, synthetic, failure_analysis
    source_run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    generation_config = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    examples = relationship("DatasetExample", back_populates="dataset", cascade="all, delete-orphan")

class DatasetExample(Base):
    """Example in a dataset."""
    __tablename__ = "dataset_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    input = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    example_metadata = Column(Text, nullable=True)  # JSON

    dataset = relationship("Dataset", back_populates="examples")

class IntegrationConfig(Base):
    """Webhook integration (Slack/Teams)."""
    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_type = Column(String, nullable=False)  # slack, teams
    webhook_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    notify_on_pass = Column(Boolean, default=False)
    notify_on_fail = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///./eval_results.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 4.2 API Routes

#### Runs API (`/api/runs`)

```
GET  /api/runs                      List runs (paginated)
     Query: app_name, limit, offset
     Response: { runs: Run[], total, limit, offset }

GET  /api/runs/{run_id}             Get run details
     Response: RunDetailResponse (with metrics, test_cases, scores, failures)

POST /api/runs                      Create run (from CLI)
     Body: RunCreate
     Response: { id, message }

GET  /api/runs/{id}/compare         Compare with another run
     Query: other_run_id
     Response: RunComparisonResponse
```

#### Datasets API (`/api/datasets`)

```
GET  /api/datasets                  List datasets (paginated)
GET  /api/datasets/{id}             Get dataset with examples
GET  /api/datasets/by-name/{name}   Get by name (for YAML integration)
POST /api/datasets                  Create dataset
POST /api/datasets/from-run/{id}    Import from run's test cases
POST /api/datasets/generate         LLM-based generation
POST /api/datasets/from-failures    Create from failure patterns
GET  /api/datasets/failure-stats    Aggregate failure distribution
```

#### Traces API (`/api/traces`)

```
GET  /api/traces                    List traces (paginated)
GET  /api/traces/{trace_id}         Get trace with spans
POST /api/traces                    Create trace
GET  /api/traces/{id}/spans         Get spans for trace
```

#### Integrations API (`/api/integrations`)

```
GET    /api/integrations            List webhook configs
POST   /api/integrations            Add webhook
PUT    /api/integrations/{id}       Update webhook
DELETE /api/integrations/{id}       Remove webhook
```

### 4.3 FastAPI App Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Company Eval Dashboard",
    description="Quality Dashboard for LLM Evaluation Results",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(runs.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(traces.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")

@app.on_event("startup")
def startup():
    create_tables()
    seed_demo_data()  # Optional demo data

# Serve React SPA
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse("frontend/dist/index.html")
```

### 4.4 Pydantic Schemas

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Request schemas
class RunCreate(BaseModel):
    app_name: str
    app_type: str
    eval_suite: str
    dataset_size: int
    passed: bool
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    config_path: Optional[str] = None
    total_cost: Optional[float] = None
    app_cost: Optional[float] = None
    eval_cost: Optional[float] = None
    metrics: List[MetricCreate]
    test_cases: List[TestCaseCreate]

class MetricCreate(BaseModel):
    name: str
    mean_score: float
    failure_rate: float
    threshold_type: Optional[str] = None
    threshold_value: Optional[float] = None
    passed: bool

class TestCaseCreate(BaseModel):
    conversation_id: str
    input: str
    output: Optional[str] = None
    context: Optional[str] = None
    scores: List[TestCaseScoreCreate]
    failure: Optional[FailureCreate] = None

# Response schemas
class RunSummaryResponse(BaseModel):
    id: str
    app_name: str
    app_type: str
    eval_suite: str
    dataset_size: int
    passed: bool
    started_at: datetime
    duration_seconds: Optional[float]
    git_branch: Optional[str]
    git_commit: Optional[str]
    total_cost: Optional[float]

class RunDetailResponse(RunSummaryResponse):
    metrics: List[MetricResponse]
    test_cases: List[TestCaseResponse]

class RunListResponse(BaseModel):
    runs: List[RunSummaryResponse]
    total: int
    limit: int
    offset: int
```

---

## 5. Web Frontend (React)

### 5.1 Technology Stack

- **React 18** with TypeScript
- **React Router 6** for routing
- **Tailwind CSS 3** for styling
- **Vite 5** for build/dev
- **Fonts**: Space Grotesk (sans), JetBrains Mono (mono)

### 5.2 Tailwind Configuration

```javascript
// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      colors: {
        background: '#000000',
        foreground: '#ffffff',
        muted: {
          DEFAULT: '#18181b',
          foreground: '#a1a1aa',
        },
        accent: {
          DEFAULT: '#3b82f6',
          foreground: '#ffffff',
        },
        border: 'rgba(255, 255, 255, 0.1)',
        card: {
          DEFAULT: 'rgba(255, 255, 255, 0.02)',
          hover: 'rgba(255, 255, 255, 0.05)',
        },
      },
      backgroundImage: {
        'gradient-glow': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.3), transparent)',
        'grid-pattern': 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
      },
      animation: {
        'glow': 'glow 4s ease-in-out infinite alternate',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { opacity: 0.5 },
          '100%': { opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        slideUp: {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
}
```

### 5.3 Routes

```tsx
// App.tsx
import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Routes>
      {/* Landing */}
      <Route path="/" element={<Landing />} />

      {/* Dashboard */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/runs/:runId" element={<RunDetails />} />
      <Route path="/compare" element={<Compare />} />
      <Route path="/traces" element={<Traces />} />
      <Route path="/traces/:traceId" element={<TraceDetails />} />
      <Route path="/datasets" element={<DatasetsPage />} />

      {/* Docs with sidebar */}
      <Route path="/docs" element={<DocsLayout />}>
        <Route index element={<Introduction />} />
        <Route path="quickstart" element={<Quickstart />} />
        <Route path="installation" element={<Installation />} />
        <Route path="how-it-works" element={<HowItWorks />} />
        <Route path="tracing" element={<Tracing />} />
        <Route path="metrics" element={<Metrics />} />
        <Route path="failure-analysis" element={<FailureAnalysis />} />
        <Route path="use-cases/chat" element={<UseCaseChat />} />
        <Route path="use-cases/rag" element={<UseCaseRAG />} />
        <Route path="use-cases/agents" element={<UseCaseAgents />} />
        <Route path="custom-evaluators" element={<CustomEvaluators />} />
        <Route path="sdk" element={<SDK />} />
        <Route path="cli/ci-run" element={<CiRun />} />
        <Route path="cicd" element={<CICD />} />
        <Route path="dashboard" element={<DashboardDocs />} />
        <Route path="config" element={<Config />} />
        <Route path="api" element={<Api />} />
        <Route path="integrations" element={<Integrations />} />
      </Route>
    </Routes>
  )
}
```

### 5.4 Page Components

#### Dashboard Page
- Stats grid: Total runs, Passed, Failed, Pass rate
- Quick action cards: Traces, Compare, Datasets
- Runs table with clickable rows
- Integrations section with add/edit/delete modals

#### RunDetails Page
- Run header with status badge, metadata
- Metrics table with pass/fail indicators
- Test cases list with expandable details
- Per-metric scores with explanations
- Failure analysis section

#### Compare Page
- Dropdown selectors for two runs
- Side-by-side metric comparison
- Delta indicators (improvement/regression)

#### Traces Page
- Paginated trace list
- Filters by project, status, date
- Click to view trace details

#### TraceDetails Page
- Trace header with timing/cost
- Span tree visualization
- Expandable span details (input/output, tokens, cost)

#### DatasetsPage
- Dataset list with counts
- Create dataset modal
- Import from run
- Generate synthetic data

### 5.5 Common Patterns

```tsx
// Fetching data
const [data, setData] = useState<DataType[]>([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)

useEffect(() => {
  fetchData()
}, [])

const fetchData = async () => {
  try {
    const response = await fetch('/api/endpoint')
    if (!response.ok) throw new Error('Failed to fetch')
    const result = await response.json()
    setData(result)
  } catch (err) {
    setError(err instanceof Error ? err.message : 'An error occurred')
  } finally {
    setLoading(false)
  }
}

// Status badge
<span className={`badge ${passed ? 'badge-pass' : 'badge-fail'}`}>
  {passed ? 'PASS' : 'FAIL'}
</span>

// Light card (for dashboard pages)
<div className="light-card p-6">
  {/* content */}
</div>

// Dark card (for landing/marketing)
<div className="glass-card p-6">
  {/* content */}
</div>
```

---

## 6. Data Formats & Contracts

### 6.1 JSONL Dataset Format

**Input (before adapter)**:
```json
{"conversation_id": "conv_001", "input": "What is your return policy?", "context": "Returns within 30 days..."}
```

**Output (after adapter)**:
```json
{"conversation_id": "conv_001", "input": "What is...", "context": "...", "output": "We accept returns within 30 days."}
```

**After evaluation**:
```json
{"conversation_id": "conv_001", "input": "...", "output": "...", "hallucination_score": 1.0, "hallucination_label": "factual", "hallucination_explanation": "Response grounded in context."}
```

### 6.2 API Response Format

**Paginated list**:
```json
{
  "runs": [...],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**Run detail**:
```json
{
  "id": "uuid",
  "app_name": "my_chatbot",
  "app_type": "simple_chat",
  "eval_suite": "basic_chat",
  "dataset_size": 20,
  "passed": true,
  "started_at": "2025-01-02T10:30:00Z",
  "finished_at": "2025-01-02T10:35:00Z",
  "duration_seconds": 300,
  "git_branch": "main",
  "git_commit": "abc1234",
  "total_cost": 0.45,
  "metrics": [
    {
      "name": "hallucination",
      "mean_score": 0.85,
      "failure_rate": 0.15,
      "threshold_type": "max",
      "threshold_value": 0.2,
      "passed": true
    }
  ],
  "test_cases": [
    {
      "id": 1,
      "conversation_id": "conv_001",
      "input": "...",
      "output": "...",
      "scores": [
        {"metric_name": "hallucination", "score": 1.0, "label": "factual", "explanation": "..."}
      ],
      "failure": null
    }
  ]
}
```

---

## 7. Configuration Schema

### 7.1 eval_config.yaml

```yaml
app_name: my-customer-support-bot
app_type: rag  # simple_chat | rag | agent | multi_agent

adapter:
  module: my_app.eval_adapter
  function: run_rag_batch

dataset:
  mode: static  # static | synthetic | dashboard
  path: data/eval_dataset.jsonl
  # For synthetic:
  # num_examples: 20
  # generation_model: gpt-4o-mini
  # description: "Customer support chatbot for e-commerce"
  # For dashboard:
  # dataset_name: "prod-samples-2025-01"
  # dashboard_url: http://localhost:8080

eval_suite: basic_rag

# Optional: custom evaluators in addition to or instead of eval_suite
custom_evaluators:
  - module: my_evaluators
    class: BrandVoiceEvaluator

thresholds:
  hallucination:
    max_mean: 0.2  # Fail if failure rate > 20%
  document_relevance:
    min_mean: 0.8  # Fail if success rate < 80%
  answer_quality:
    min_mean: 0.7
```

### 7.2 Custom Evaluator Example

```python
# my_evaluators.py
from company_eval_framework.evaluators import EvaluatorSpec

class BrandVoiceEvaluator(EvaluatorSpec):
    def __init__(self):
        super().__init__(
            name="brand_voice",
            template="""
You are evaluating whether a response matches our brand voice guidelines.

[User Query]
{input}

[Response]
{output}

Our brand voice is: friendly, professional, concise, empathetic.

Respond with one of: on_brand, off_brand
""",
            rails_map={"on_brand": "on_brand", "off_brand": "off_brand"},
            input_columns=["input", "output"],
            positive_label="on_brand",
        )
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      use_synthetic:
        description: 'Use synthetic dataset'
        type: boolean
        default: false

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install ./eval_framework
          pip install ./example_team_project

      - name: Run evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          company-eval ci-run --config example_team_project/eval_config.yaml

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results/
```

---

## 9. Docker Deployment

### 9.1 Multi-stage Dockerfile

```dockerfile
# Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Production image
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 9.2 docker-compose.yml

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    volumes:
      - ./backend/app:/app/app
    healthcheck:
      test: curl -f http://localhost:8080/api/health
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
    environment:
      VITE_API_URL: http://backend:8080
```

---

## 10. Refactoring Opportunities

When replicating this codebase, consider these consolidation opportunities:

### 10.1 Merge Dashboard Implementations

**Current**: There are two dashboard implementations:
1. `eval_framework/src/company_eval_framework/dashboard/` - Embedded in CLI
2. `web/` - Standalone web app

**Recommendation**: Keep only the `web/` implementation. The embedded dashboard was an early prototype. Remove `eval_framework/dashboard/` and use `company-eval dashboard` to simply start the web backend.

### 10.2 Consolidate Evaluator Definitions

**Current**: Evaluator specs are defined multiple times:
- In `evaluators.py` as functions (`build_basic_chat_suite()`)
- In `get_available_evaluators()` dictionary

**Recommendation**: Define evaluators once in a registry pattern:

```python
EVALUATOR_REGISTRY = {
    "user_frustration": EvaluatorSpec(...),
    "toxicity": EvaluatorSpec(...),
    # ...
}

SUITE_DEFINITIONS = {
    "basic_chat": ["user_frustration", "toxicity", "helpfulness_quality"],
    "basic_rag": ["hallucination", "document_relevance", "answer_quality"],
    # ...
}

def build_eval_suite(name: str) -> List[EvaluatorSpec]:
    return [EVALUATOR_REGISTRY[e] for e in SUITE_DEFINITIONS[name]]
```

### 10.3 Use Alembic for Migrations

**Current**: Tables created with `Base.metadata.create_all()` on startup.

**Recommendation**: Use Alembic for proper schema migrations. This allows schema changes without data loss.

### 10.4 Add Response Caching

**Current**: No caching of API responses.

**Recommendation**: Add Redis or in-memory caching for frequently accessed data like run lists, dataset metadata.

### 10.5 Extract Shared Types

**Current**: TypeScript interfaces duplicated across pages.

**Recommendation**: Create a `types/` directory with shared interfaces:

```typescript
// types/run.ts
export interface Run {
  id: string
  app_name: string
  // ...
}

// types/api.ts
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}
```

### 10.6 Use React Query or SWR

**Current**: Manual `fetch` + `useState` + `useEffect` pattern everywhere.

**Recommendation**: Use React Query for data fetching:

```typescript
const { data, isLoading, error } = useQuery(['runs'], () =>
  fetch('/api/runs').then(r => r.json())
)
```

### 10.7 Simplify Threshold Semantics

**Current**: Confusing threshold semantics where:
- `max_mean` applies to failure rate
- `min_mean` applies to success rate
- Score is inverted for "negative" metrics

**Recommendation**: Use clearer naming:

```yaml
thresholds:
  hallucination:
    max_failure_rate: 0.2  # Clearer intent
  answer_quality:
    min_success_rate: 0.8  # Clearer intent
```

### 10.8 Add OpenTelemetry Support

**Current**: Custom tracing implementation.

**Recommendation**: Add OpenTelemetry export support so traces can be sent to any OTEL-compatible backend (Jaeger, Datadog, etc.).

### 10.9 Remove Unused Code

**Current**: Some deleted files still referenced:
- `AppTypes.tsx`, `Datasets.tsx`, `EvalSuites.tsx`, `Thresholds.tsx`, `DashboardCmd.tsx` are deleted but may have remnants.

**Recommendation**: Clean up all imports and references to deleted files.

### 10.10 Consolidate CSS

**Current**: Mix of Tailwind utility classes and custom CSS in `index.css`.

**Recommendation**: Move all custom styles to Tailwind config or create a proper design system with consistent component classes.

---

## Dependencies Summary

### Python (eval_framework)
```toml
[project]
dependencies = [
    "arize-phoenix-evals>=0.5.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "pandas>=2.0.0",
    "tqdm>=4.0.0",
]

[project.scripts]
company-eval = "company_eval_framework.cli:main"
```

### Python (web/backend)
```
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
```

### Node.js (web/frontend)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

## Environment Variables

```bash
# Required for evaluations
OPENAI_API_KEY=sk-...

# Optional: Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01

# Frontend (development)
VITE_API_URL=http://localhost:8080
```

---

## Quick Start Commands

```bash
# Install framework
pip install -e ./eval_framework

# Run evaluation
company-eval ci-run --config eval_config.yaml

# Start dashboard
cd web
docker-compose up -d
# Visit http://localhost:3000

# Generate synthetic data
company-eval generate-dataset --app-type rag --output data.jsonl --num-examples 50
```

---

*This specification should provide everything needed to replicate the Company Eval Framework. Focus on the architecture patterns and data contracts rather than copying code verbatim.*
