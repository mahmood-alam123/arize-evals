"""Pydantic schemas for the API."""

from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class MetricCreate(BaseModel):
    name: str
    mean_score: float = Field(ge=0.0, le=1.0)
    failure_rate: float = Field(ge=0.0, le=1.0)
    threshold_type: Optional[Literal["min", "max"]] = None
    threshold_value: Optional[float] = None
    passed: bool


class TestCaseScoreCreate(BaseModel):
    metric_name: str
    score: float = Field(ge=0.0, le=1.0)
    label: Optional[str] = None
    explanation: Optional[str] = None


class FailureCreate(BaseModel):
    failure_type: str
    explanation: Optional[str] = None


class TestCaseCreate(BaseModel):
    conversation_id: str
    input: str
    output: Optional[str] = None
    context: Optional[str] = None
    prompt: Optional[str] = None  # Full prompt sent to LLM
    trace_id: Optional[str] = None
    scores: List[TestCaseScoreCreate] = []
    failure: Optional[FailureCreate] = None


class RunCreate(BaseModel):
    app_name: str
    app_type: Literal["simple_chat", "rag", "agent", "multi_agent"]
    eval_suite: str
    dataset_size: int
    passed: bool
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    config_path: Optional[str] = None
    total_cost: Optional[float] = None
    app_cost: Optional[float] = None
    eval_cost: Optional[float] = None
    metrics: List[MetricCreate] = []
    test_cases: List[TestCaseCreate] = []


class MetricResponse(BaseModel):
    id: int
    name: str
    mean_score: float
    failure_rate: float
    threshold_type: Optional[str] = None
    threshold_value: Optional[float] = None
    passed: bool

    class Config:
        from_attributes = True


class TestCaseScoreResponse(BaseModel):
    id: int
    metric_name: str
    score: float
    label: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class FailureResponse(BaseModel):
    id: int
    failure_type: str
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class TestCaseResponse(BaseModel):
    id: int
    conversation_id: str
    input: str
    output: Optional[str] = None
    context: Optional[str] = None
    prompt: Optional[str] = None
    trace_id: Optional[str] = None
    scores: List[TestCaseScoreResponse] = []
    failure: Optional[FailureResponse] = None

    class Config:
        from_attributes = True


class RunSummaryResponse(BaseModel):
    id: str
    app_name: str
    app_type: str
    eval_suite: str
    dataset_size: int
    passed: bool
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    total_cost: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RunDetailResponse(BaseModel):
    id: str
    app_name: str
    app_type: str
    eval_suite: str
    dataset_size: int
    passed: bool
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    config_path: Optional[str] = None
    total_cost: Optional[float] = None
    app_cost: Optional[float] = None
    eval_cost: Optional[float] = None
    created_at: datetime
    metrics: List[MetricResponse] = []
    test_cases: List[TestCaseResponse] = []

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    runs: List[RunSummaryResponse]
    total: int
    limit: int
    offset: int


class RunCreatedResponse(BaseModel):
    id: str
    message: str = "Run created successfully"


# Integration schemas
class IntegrationConfigCreate(BaseModel):
    integration_type: Literal["slack", "teams"]
    webhook_url: str
    is_active: bool = True
    notify_on_pass: bool = False
    notify_on_fail: bool = True


class IntegrationConfigUpdate(BaseModel):
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None
    notify_on_pass: Optional[bool] = None
    notify_on_fail: Optional[bool] = None


class IntegrationConfigResponse(BaseModel):
    id: int
    integration_type: str
    webhook_url: str
    is_active: bool
    notify_on_pass: bool
    notify_on_fail: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Tracing Schemas ==============

class SpanCreate(BaseModel):
    """Create a new span within a trace."""
    name: str
    span_type: Literal["llm", "tool", "retrieval", "chain", "agent", "custom"]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: Literal["running", "completed", "error"] = "running"
    parent_span_id: Optional[str] = None
    input: Optional[str] = None  # JSON string
    output: Optional[str] = None  # JSON string
    model: Optional[str] = None
    provider: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[float] = None
    tool_name: Optional[str] = None
    tool_args: Optional[str] = None  # JSON string
    error_message: Optional[str] = None
    span_metadata: Optional[str] = None  # JSON string


class TraceCreate(BaseModel):
    """Create a new trace."""
    name: str
    project_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: Literal["running", "completed", "error"] = "running"
    input: Optional[str] = None
    output: Optional[str] = None
    trace_metadata: Optional[str] = None  # JSON string
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    error_message: Optional[str] = None
    spans: List[SpanCreate] = []


class SpanResponse(BaseModel):
    """Response for a span."""
    id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    span_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str
    input: Optional[str] = None
    output: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[float] = None
    tool_name: Optional[str] = None
    tool_args: Optional[str] = None
    error_message: Optional[str] = None
    span_metadata: Optional[str] = None

    class Config:
        from_attributes = True


class TraceSummaryResponse(BaseModel):
    """Summary response for a trace (list view)."""
    id: str
    name: str
    project_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    span_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TraceDetailResponse(BaseModel):
    """Detailed response for a trace (includes spans)."""
    id: str
    name: str
    project_name: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str
    input: Optional[str] = None
    output: Optional[str] = None
    trace_metadata: Optional[str] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    spans: List[SpanResponse] = []

    class Config:
        from_attributes = True


class TraceListResponse(BaseModel):
    """Paginated list of traces."""
    traces: List[TraceSummaryResponse]
    total: int
    limit: int
    offset: int


# ============== Dataset Schemas ==============

class DatasetExampleCreate(BaseModel):
    """Create a dataset example."""
    input: str
    expected_output: Optional[str] = None
    context: Optional[str] = None
    metadata: Optional[str] = None  # JSON string


class DatasetCreate(BaseModel):
    """Create a new dataset."""
    name: str
    description: Optional[str] = None
    app_type: Optional[Literal["simple_chat", "rag", "agent", "multi_agent"]] = None
    examples: List[DatasetExampleCreate] = []


class DatasetExampleResponse(BaseModel):
    """Response for a dataset example."""
    id: int
    input: str
    expected_output: Optional[str] = None
    context: Optional[str] = None
    metadata: Optional[str] = None

    class Config:
        from_attributes = True


class DatasetSummaryResponse(BaseModel):
    """Summary response for a dataset (list view)."""
    id: str
    name: str
    description: Optional[str] = None
    app_type: Optional[str] = None
    num_examples: int
    source: Optional[str] = None  # "upload", "run_import", "synthetic", "failure_analysis"
    source_run_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatasetDetailResponse(BaseModel):
    """Detailed response for a dataset (includes examples)."""
    id: str
    name: str
    description: Optional[str] = None
    app_type: Optional[str] = None
    num_examples: int
    source: Optional[str] = None
    source_run_id: Optional[str] = None
    generation_config: Optional[str] = None  # JSON string
    created_at: datetime
    updated_at: datetime
    examples: List[DatasetExampleResponse] = []

    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    """Paginated list of datasets."""
    datasets: List[DatasetSummaryResponse]
    total: int
    limit: int
    offset: int


# ============== Dataset Generation Schemas ==============

class DatasetFromRunCreate(BaseModel):
    """Create a dataset from a previous run's test cases."""
    run_id: str
    name: str
    description: Optional[str] = None
    include_failures_only: bool = False


class SyntheticGenerationConfig(BaseModel):
    """Configuration for LLM-based synthetic data generation."""
    model: str = "gpt-4o-mini"
    app_description: Optional[str] = None
    system_prompt: Optional[str] = None
    example_inputs: List[str] = []
    temperature: float = 0.9


class DatasetGenerateCreate(BaseModel):
    """Create a synthetic dataset using LLM generation."""
    name: str
    description: Optional[str] = None
    app_type: Literal["simple_chat", "rag", "agent", "multi_agent"]
    num_examples: int = Field(default=20, ge=1, le=100)
    generation_config: SyntheticGenerationConfig


class DatasetFromFailuresCreate(BaseModel):
    """Create a dataset targeting specific failure patterns."""
    name: str
    description: Optional[str] = None
    app_name: Optional[str] = None  # Filter by app
    failure_types: List[str] = []  # Empty = all types
    num_examples_per_type: int = Field(default=5, ge=1, le=20)
    model: str = "gpt-4o-mini"


class FailureStatItem(BaseModel):
    """Statistics for a single failure type."""
    failure_type: str
    count: int
    app_names: List[str]


class FailureStatsResponse(BaseModel):
    """Response containing failure statistics."""
    stats: List[FailureStatItem]


# ============== Run Comparison Schemas ==============

class MetricComparison(BaseModel):
    """Comparison of a single metric between two runs."""
    name: str
    run_a_score: float
    run_b_score: float
    delta: float  # run_b - run_a
    delta_percent: Optional[float] = None  # percentage change
    run_a_passed: bool
    run_b_passed: bool
    improved: bool  # True if run_b is better


class RunComparisonResponse(BaseModel):
    """Comparison between two runs."""
    run_a: RunSummaryResponse
    run_b: RunSummaryResponse
    metrics: List[MetricComparison]
    summary: dict  # Overall summary stats
