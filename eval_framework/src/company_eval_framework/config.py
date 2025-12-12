"""
Configuration models for the evaluation framework.

This module defines Pydantic models for loading and validating evaluation
configuration files (YAML). Teams use these configs to specify:
- Which adapter function to call for running their app
- Dataset source (static file or synthetic generation)
- Which eval suite to run
- Threshold definitions for pass/fail criteria
"""

from typing import Any, Dict, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator


class AdapterConfig(BaseModel):
    """
    Configuration for the team's adapter function.

    The adapter is the bridge between the eval framework and the team's app.
    It reads input data, runs the app, and writes output data.

    Attributes:
        module: Python module path, e.g. "example_team_app.eval_adapter"
        function: Function name within the module, e.g. "run_simple_llm_batch"
    """
    module: str = Field(
        ...,
        description="Python module path containing the adapter function"
    )
    function: str = Field(
        ...,
        description="Name of the adapter function to call"
    )


class DatasetConfig(BaseModel):
    """
    Configuration for the evaluation dataset.

    Supports two modes:
    - static: Load from a JSONL/CSV file
    - synthetic: Generate examples using an LLM

    Attributes:
        mode: Either "static" (load from file) or "synthetic" (generate with LLM)
        path: File path for static datasets (JSONL or CSV)
        num_examples: Number of examples to generate in synthetic mode
        generation_model: LLM model for synthetic generation (e.g., "gpt-4o-mini")
        description: Description of the app/dataset for synthetic generation context
        prompt_files: Optional list of prompt files to use as context for generation
    """
    mode: Literal["static", "synthetic"] = Field(
        ...,
        description="Dataset source mode"
    )
    path: Optional[str] = Field(
        default=None,
        description="Path to static dataset file (JSONL or CSV)"
    )
    num_examples: Optional[int] = Field(
        default=20,
        description="Number of synthetic examples to generate"
    )
    generation_model: Optional[str] = Field(
        default="gpt-4o-mini",
        description="Model to use for synthetic data generation"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the app for synthetic generation context"
    )
    prompt_files: Optional[List[str]] = Field(
        default=None,
        description="List of prompt files to include as generation context"
    )

    @model_validator(mode="after")
    def validate_mode_requirements(self) -> "DatasetConfig":
        """Validate that required fields are present based on mode."""
        if self.mode == "static" and not self.path:
            raise ValueError("Dataset path is required when mode is 'static'")
        return self


class ThresholdConfig(BaseModel):
    """
    Threshold configuration for a single metric.

    Define pass/fail criteria using max_mean and/or min_mean bounds.
    A metric passes if its mean score satisfies all specified bounds.

    Attributes:
        max_mean: Maximum allowed mean score (metric fails if mean > max_mean)
        min_mean: Minimum required mean score (metric fails if mean < min_mean)
    """
    max_mean: Optional[float] = Field(
        default=None,
        description="Maximum allowed mean score for this metric"
    )
    min_mean: Optional[float] = Field(
        default=None,
        description="Minimum required mean score for this metric"
    )

    @model_validator(mode="after")
    def validate_at_least_one_bound(self) -> "ThresholdConfig":
        """Ensure at least one threshold bound is specified."""
        if self.max_mean is None and self.min_mean is None:
            raise ValueError("At least one of max_mean or min_mean must be specified")
        return self


class EvalConfig(BaseModel):
    """
    Main evaluation configuration model.

    This is the top-level config that teams define in their llm_eval_*.yaml files.
    It specifies everything needed to run an evaluation:
    - App identification
    - Adapter for running the app
    - Dataset source
    - Evaluation suite to apply
    - Pass/fail thresholds

    Attributes:
        app_name: Human-readable name for the app being evaluated
        app_type: Type of LLM application (affects dataset generation and eval choice)
        adapter: Configuration for the team's adapter function
        dataset: Configuration for the evaluation dataset
        eval_suite: Name of the evaluation suite to run
        thresholds: Dictionary of metric names to threshold configurations
    """
    app_name: str = Field(
        ...,
        description="Human-readable name for the application"
    )
    app_type: Literal["simple_chat", "rag", "agent", "multi_agent"] = Field(
        ...,
        description="Type of LLM application"
    )
    adapter: AdapterConfig = Field(
        ...,
        description="Adapter configuration for running the app"
    )
    dataset: DatasetConfig = Field(
        ...,
        description="Dataset configuration"
    )
    eval_suite: str = Field(
        ...,
        description="Name of the evaluation suite to run"
    )
    thresholds: Dict[str, ThresholdConfig] = Field(
        default_factory=dict,
        description="Metric thresholds for pass/fail determination"
    )


def load_eval_config(path: str) -> EvalConfig:
    """
    Load and validate an evaluation configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file

    Returns:
        Validated EvalConfig instance

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
        pydantic.ValidationError: If the config doesn't match the schema

    Example:
        >>> config = load_eval_config("llm_eval_simple_chat.yaml")
        >>> print(config.app_name)
        "example-simple-chat"
    """
    with open(path, "r") as f:
        raw_config: Dict[str, Any] = yaml.safe_load(f)

    return EvalConfig(**raw_config)
