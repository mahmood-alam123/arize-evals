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
