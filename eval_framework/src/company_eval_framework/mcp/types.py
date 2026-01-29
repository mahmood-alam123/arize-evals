"""Type definitions for MCP server responses."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


class MetricResult(BaseModel):
    """Result of a single metric evaluation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Name of the metric")
    mean_score: float = Field(..., description="Average score across all evaluations")
    threshold_type: Optional[Literal["min", "max"]] = Field(
        None, description="Type of threshold applied (min or max)"
    )
    threshold_value: Optional[float] = Field(
        None, description="Threshold value that was applied"
    )
    passed: bool = Field(..., description="Whether this metric passed the threshold")


class FailureExample(BaseModel):
    """Example of a failed evaluation."""
    model_config = ConfigDict(str_strip_whitespace=True)

    input_text: str = Field(..., description="Input that was evaluated")
    expected_output: Optional[str] = Field(None, description="Expected output")
    actual_output: str = Field(..., description="Actual output from the app")
    failure_reason: str = Field(..., description="Why this evaluation failed")


class FailureAnalysis(BaseModel):
    """Analysis of failure patterns."""
    model_config = ConfigDict(str_strip_whitespace=True)

    total_failures: int = Field(..., description="Total number of failures")
    failure_rate: float = Field(..., description="Percentage of evaluations that failed")
    common_patterns: List[str] = Field(
        default_factory=list, description="Common patterns found in failures"
    )
    examples: List[FailureExample] = Field(
        default_factory=list, description="Sample failure examples"
    )


class EvaluationResult(BaseModel):
    """Complete result of an evaluation run."""
    model_config = ConfigDict(str_strip_whitespace=True)

    passed: bool = Field(..., description="Overall pass/fail status")
    app_name: str = Field(..., description="Name of the app that was evaluated")
    app_type: str = Field(..., description="Type of app (e.g., 'rag', 'chat', 'agent')")
    eval_suite: str = Field(..., description="Evaluation suite that was used")
    dataset_size: int = Field(..., description="Number of evaluations run")
    metrics: List[MetricResult] = Field(..., description="Individual metric results")
    failure_analysis: Optional[FailureAnalysis] = Field(
        None, description="Analysis of failures if any occurred"
    )
    execution_time_seconds: float = Field(..., description="Total execution time")


class ConfigSummary(BaseModel):
    """Summary of an evaluation configuration."""
    model_config = ConfigDict(str_strip_whitespace=True)

    path: str = Field(..., description="Path to the configuration file")
    app_name: str = Field(..., description="Name of the app being evaluated")
    app_type: str = Field(..., description="Type of app")
    eval_suite: str = Field(..., description="Evaluation suite to use")
    dataset_path: Optional[str] = Field(None, description="Path to the dataset file")
    adapter_module: str = Field(..., description="Python module path for the adapter")


class EvalSuiteInfo(BaseModel):
    """Information about an evaluation suite."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., description="Suite identifier")
    description: str = Field(..., description="What this suite evaluates")
    typical_app_types: List[str] = Field(..., description="App types this suite works with")
    metrics_evaluated: List[str] = Field(..., description="Metrics this suite checks")


class DatasetPreview(BaseModel):
    """Preview of a dataset file."""
    model_config = ConfigDict(str_strip_whitespace=True)

    path: str = Field(..., description="Path to the dataset file")
    total_rows: int = Field(..., description="Total number of rows in dataset")
    preview_rows: List[dict] = Field(..., description="Sample rows from the dataset")
    columns: List[str] = Field(..., description="Column names in the dataset")
