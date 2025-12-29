"""
Pydantic schemas for the Quality Dashboard API.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Request Schemas
# ============================================================================


class MetricCreate(BaseModel):
    """Metric data for creating a run."""

    name: str
    mean_score: float = Field(ge=0.0, le=1.0)
    failure_rate: float = Field(ge=0.0, le=1.0)
    threshold_type: Optional[Literal["min", "max"]] = None
    threshold_value: Optional[float] = None
    passed: bool


class TestCaseScoreCreate(BaseModel):
    """Score data for a test case."""

    metric_name: str
    score: float = Field(ge=0.0, le=1.0)
    label: Optional[str] = None
    explanation: Optional[str] = None


class FailureCreate(BaseModel):
    """Failure data for a test case."""

    failure_type: str
    explanation: Optional[str] = None


class TestCaseCreate(BaseModel):
    """Test case data for creating a run."""

    conversation_id: str
    input: str
    output: Optional[str] = None
    context: Optional[str] = None
    scores: list[TestCaseScoreCreate] = []
    failure: Optional[FailureCreate] = None


class RunCreate(BaseModel):
    """Request body for creating a new evaluation run."""

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
    metrics: list[MetricCreate] = []
    test_cases: list[TestCaseCreate] = []


# ============================================================================
# Response Schemas
# ============================================================================


class MetricResponse(BaseModel):
    """Metric response in API."""

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
    """Score response for a test case."""

    id: int
    metric_name: str
    score: float
    label: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class FailureResponse(BaseModel):
    """Failure response for a test case."""

    id: int
    failure_type: str
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class TestCaseResponse(BaseModel):
    """Test case response in API."""

    id: int
    conversation_id: str
    input: str
    output: Optional[str] = None
    context: Optional[str] = None
    scores: list[TestCaseScoreResponse] = []
    failure: Optional[FailureResponse] = None

    class Config:
        from_attributes = True


class RunSummaryResponse(BaseModel):
    """Summary of a run for list view."""

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
    created_at: datetime

    class Config:
        from_attributes = True


class RunDetailResponse(BaseModel):
    """Full run details including metrics and test cases."""

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
    created_at: datetime
    metrics: list[MetricResponse] = []
    test_cases: list[TestCaseResponse] = []

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    """Paginated list of runs."""

    runs: list[RunSummaryResponse]
    total: int
    limit: int
    offset: int


class FailureSummaryResponse(BaseModel):
    """Summary of failures for a run."""

    total_failures: int
    distribution: dict[str, int]


class RunCreatedResponse(BaseModel):
    """Response after creating a run."""

    id: str
    message: str = "Run created successfully"
