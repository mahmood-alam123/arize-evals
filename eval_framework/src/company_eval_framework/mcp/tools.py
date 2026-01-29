"""MCP tool implementations for the evaluation framework."""

import json
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from glob import glob

import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import Context

from .types import (
    EvaluationResult,
    MetricResult,
    FailureAnalysis,
    FailureExample,
    ConfigSummary,
    EvalSuiteInfo,
    DatasetPreview,
)


# Global cache for storing the last evaluation result
_last_evaluation_result: Optional[Dict[str, Any]] = None


# ==============================================================================
# Input Models
# ==============================================================================


class RunEvaluationInput(BaseModel):
    """Input for running an evaluation."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    config_path: str = Field(
        ...,
        description="Path to the evaluation configuration YAML file (e.g., 'configs/my_app.yaml')",
        min_length=1,
    )

    @field_validator('config_path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.endswith(('.yaml', '.yml')):
            raise ValueError("Config path must end with .yaml or .yml")
        return v


class ListConfigsInput(BaseModel):
    """Input for listing configuration files."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    directory: str = Field(
        default=".",
        description="Directory to search for config files (default: current directory)",
    )


class ValidateConfigInput(BaseModel):
    """Input for validating a configuration."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    config_path: str = Field(
        ...,
        description="Path to the configuration YAML file to validate",
        min_length=1,
    )


class GenerateDatasetInput(BaseModel):
    """Input for generating a synthetic dataset."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    output_path: str = Field(
        ...,
        description="Path where the generated dataset should be saved (e.g., 'datasets/my_data.jsonl')",
        min_length=1,
    )
    num_samples: int = Field(
        default=10,
        description="Number of samples to generate",
        ge=1,
        le=1000,
    )
    app_type: str = Field(
        default="chat",
        description="Type of app to generate data for (e.g., 'chat', 'rag', 'agent')",
    )


class PreviewDatasetInput(BaseModel):
    """Input for previewing a dataset."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    dataset_path: str = Field(
        ...,
        description="Path to the dataset file to preview (JSONL format)",
        min_length=1,
    )
    num_rows: int = Field(
        default=10,
        description="Number of rows to preview",
        ge=1,
        le=50,
    )


# ==============================================================================
# Helper Functions
# ==============================================================================


def _load_yaml_config(path: str) -> Dict[str, Any]:
    """Load and parse a YAML configuration file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file: {e}")


def _format_metric_result(metric: Dict[str, Any]) -> MetricResult:
    """Format a metric result dictionary into a MetricResult model."""
    return MetricResult(
        name=metric.get("name", "unknown"),
        mean_score=metric.get("mean_score", 0.0),
        threshold_type=metric.get("threshold_type"),
        threshold_value=metric.get("threshold_value"),
        passed=metric.get("passed", False),
    )


def _analyze_failures(results: List[Dict[str, Any]]) -> Optional[FailureAnalysis]:
    """Analyze failure patterns from evaluation results."""
    failures = [r for r in results if not r.get("passed", True)]
    
    if not failures:
        return None
    
    total = len(results)
    failure_count = len(failures)
    
    # Extract failure examples
    examples = []
    for failure in failures[:5]:  # Limit to 5 examples
        examples.append(FailureExample(
            input_text=failure.get("input", "")[:200],  # Truncate long inputs
            expected_output=failure.get("expected_output", "")[:200] if failure.get("expected_output") else None,
            actual_output=failure.get("actual_output", "")[:200],
            failure_reason=failure.get("failure_reason", "Unknown failure"),
        ))
    
    # Identify common patterns (simplified)
    common_patterns = []
    if failure_count > total * 0.5:
        common_patterns.append("More than 50% of evaluations failed")
    if any("timeout" in f.get("failure_reason", "").lower() for f in failures):
        common_patterns.append("Timeout errors detected")
    if any("error" in f.get("failure_reason", "").lower() for f in failures):
        common_patterns.append("Runtime errors detected")
    
    return FailureAnalysis(
        total_failures=failure_count,
        failure_rate=round((failure_count / total) * 100, 2),
        common_patterns=common_patterns or ["Various failure types"],
        examples=examples,
    )


def _read_jsonl_file(path: str, max_rows: int = 10) -> List[Dict[str, Any]]:
    """Read a JSONL file and return up to max_rows."""
    rows = []
    try:
        with open(path, 'r') as f:
            for i, line in enumerate(f):
                if i >= max_rows:
                    break
                try:
                    rows.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {path}")
    return rows


# ==============================================================================
# Tool Implementations
# ==============================================================================


async def run_evaluation(params: RunEvaluationInput, ctx: Context) -> str:
    """Execute a full evaluation pipeline from a configuration file.
    
    This tool runs the complete evaluation process including:
    1. Loading the configuration
    2. Initializing the app adapter
    3. Running evaluations on the dataset
    4. Collecting metrics and results
    5. Caching results for later analysis
    
    Args:
        params: RunEvaluationInput containing:
            - config_path (str): Path to evaluation config YAML file
        ctx: MCP context for progress reporting
    
    Returns:
        str: JSON-formatted evaluation results including:
            - passed (bool): Overall pass/fail status
            - metrics (list): Individual metric results with scores
            - failure_analysis (dict): Analysis of any failures
            - execution_time_seconds (float): Total runtime
    """
    global _last_evaluation_result
    
    await ctx.report_progress(0.1, "Loading configuration...")
    
    # Load config
    try:
        config = _load_yaml_config(params.config_path)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to load config: {str(e)}",
            "suggestion": "Check that the config path is correct and the file is valid YAML"
        }, indent=2)
    
    await ctx.report_progress(0.2, "Validating configuration...")
    
    # Validate required fields
    required_fields = ["app_name", "app_type", "eval_suite", "adapter_module"]
    missing = [f for f in required_fields if f not in config]
    if missing:
        return json.dumps({
            "error": f"Missing required fields in config: {', '.join(missing)}",
            "suggestion": "Add the missing fields to your configuration file"
        }, indent=2)
    
    await ctx.report_progress(0.3, f"Running evaluation for {config['app_name']}...")
    
    # Simulate running evaluation (in real implementation, import and call run_ci_evaluation)
    # This is a placeholder that demonstrates the structure
    start_time = time.time()
    
    try:
        # In real implementation:
        # from company_eval_framework.ci import run_ci_evaluation
        # result = run_ci_evaluation(params.config_path)
        
        # Simulated result for demonstration
        await ctx.report_progress(0.5, "Running adapter on dataset...")
        await ctx.report_progress(0.7, "Computing metrics...")
        
        # Simulated metrics
        metrics = [
            MetricResult(
                name="accuracy",
                mean_score=0.85,
                threshold_type="min",
                threshold_value=0.8,
                passed=True,
            ),
            MetricResult(
                name="response_time",
                mean_score=1.2,
                threshold_type="max",
                threshold_value=2.0,
                passed=True,
            ),
        ]
        
        execution_time = time.time() - start_time
        
        result = EvaluationResult(
            passed=all(m.passed for m in metrics),
            app_name=config["app_name"],
            app_type=config["app_type"],
            eval_suite=config["eval_suite"],
            dataset_size=config.get("dataset_size", 10),
            metrics=metrics,
            failure_analysis=None,  # Would come from _analyze_failures()
            execution_time_seconds=round(execution_time, 2),
        )
        
        # Cache the result
        _last_evaluation_result = result.model_dump()
        
        await ctx.report_progress(1.0, "Evaluation complete!")
        
        return json.dumps(result.model_dump(), indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Evaluation failed: {str(e)}",
            "suggestion": "Check that the adapter module can be imported and the dataset path is valid"
        }, indent=2)


async def list_configs(params: ListConfigsInput) -> str:
    """Discover available evaluation configurations in a directory.
    
    Searches for YAML configuration files and parses them to provide
    a summary of available evaluations.
    
    Args:
        params: ListConfigsInput containing:
            - directory (str): Directory to search (default: current directory)
    
    Returns:
        str: JSON-formatted list of configuration summaries with:
            - path (str): Path to config file
            - app_name (str): Name of the app
            - app_type (str): Type of app
            - eval_suite (str): Suite being used
            - adapter_module (str): Python module for adapter
    """
    search_dir = Path(params.directory).resolve()
    
    if not search_dir.exists():
        return json.dumps({
            "error": f"Directory not found: {params.directory}",
            "suggestion": "Provide a valid directory path"
        }, indent=2)
    
    # Find all YAML files
    yaml_files = list(search_dir.glob("**/*.yaml")) + list(search_dir.glob("**/*.yml"))
    
    if not yaml_files:
        return json.dumps({
            "configs": [],
            "message": f"No YAML configuration files found in {params.directory}"
        }, indent=2)
    
    configs = []
    for yaml_file in yaml_files:
        try:
            config = _load_yaml_config(str(yaml_file))
            
            # Only include if it looks like an eval config
            if "app_name" in config and "adapter_module" in config:
                configs.append(ConfigSummary(
                    path=str(yaml_file.relative_to(search_dir)),
                    app_name=config.get("app_name", "unknown"),
                    app_type=config.get("app_type", "unknown"),
                    eval_suite=config.get("eval_suite", "unknown"),
                    dataset_path=config.get("dataset_path"),
                    adapter_module=config.get("adapter_module", "unknown"),
                ).model_dump())
        except Exception:
            # Skip files that can't be parsed
            continue
    
    return json.dumps({
        "configs": configs,
        "total": len(configs),
        "directory": str(search_dir)
    }, indent=2)


async def list_eval_suites() -> str:
    """List available evaluation suites with their descriptions.
    
    Returns information about built-in evaluation suites including
    what they test for and which app types they work with.
    
    Returns:
        str: JSON-formatted list of evaluation suites with:
            - name (str): Suite identifier
            - description (str): What the suite evaluates
            - typical_app_types (list): App types this works with
            - metrics_evaluated (list): Metrics this suite checks
    """
    suites = [
        EvalSuiteInfo(
            name="basic_chat",
            description="Evaluates conversational AI applications",
            typical_app_types=["chat", "chatbot"],
            metrics_evaluated=["response_quality", "coherence", "relevance"],
        ),
        EvalSuiteInfo(
            name="basic_rag",
            description="Evaluates retrieval-augmented generation systems",
            typical_app_types=["rag", "qa"],
            metrics_evaluated=["factual_accuracy", "context_usage", "citation_quality"],
        ),
        EvalSuiteInfo(
            name="agent",
            description="Evaluates autonomous agent systems",
            typical_app_types=["agent", "assistant"],
            metrics_evaluated=["task_completion", "tool_usage", "reasoning_quality"],
        ),
        EvalSuiteInfo(
            name="multi_agent",
            description="Evaluates multi-agent collaboration systems",
            typical_app_types=["multi_agent", "orchestrator"],
            metrics_evaluated=["coordination", "task_distribution", "collective_performance"],
        ),
    ]
    
    return json.dumps({
        "suites": [s.model_dump() for s in suites],
        "total": len(suites)
    }, indent=2)


async def validate_config(params: ValidateConfigInput) -> str:
    """Validate an evaluation configuration without running it.
    
    Checks that the configuration file is valid and contains all
    required fields without actually executing the evaluation.
    
    Args:
        params: ValidateConfigInput containing:
            - config_path (str): Path to config file to validate
    
    Returns:
        str: JSON-formatted validation result with:
            - valid (bool): Whether config is valid
            - errors (list): Any validation errors found
            - warnings (list): Non-critical warnings
    """
    errors = []
    warnings = []
    
    # Check if file exists
    if not Path(params.config_path).exists():
        return json.dumps({
            "valid": False,
            "errors": [f"Config file not found: {params.config_path}"],
            "warnings": []
        }, indent=2)
    
    # Try to load the config
    try:
        config = _load_yaml_config(params.config_path)
    except Exception as e:
        return json.dumps({
            "valid": False,
            "errors": [f"Failed to parse YAML: {str(e)}"],
            "warnings": []
        }, indent=2)
    
    # Check required fields
    required_fields = ["app_name", "app_type", "eval_suite", "adapter_module"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Check optional but recommended fields
    recommended_fields = ["dataset_path", "metrics"]
    for field in recommended_fields:
        if field not in config:
            warnings.append(f"Recommended field not set: {field}")
    
    # Validate adapter module path
    if "adapter_module" in config:
        adapter_path = config["adapter_module"]
        if not adapter_path or not isinstance(adapter_path, str):
            errors.append("adapter_module must be a non-empty string")
    
    # Validate dataset path if provided
    if "dataset_path" in config:
        dataset_path = config["dataset_path"]
        if dataset_path and not Path(dataset_path).exists():
            warnings.append(f"Dataset file not found: {dataset_path}")
    
    return json.dumps({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "config_summary": {
            "app_name": config.get("app_name"),
            "app_type": config.get("app_type"),
            "eval_suite": config.get("eval_suite"),
        } if len(errors) == 0 else None
    }, indent=2)


async def get_evaluation_results() -> str:
    """Get detailed results from the most recent evaluation run.
    
    Returns the cached results from the last evaluation, including
    all metrics, scores, and failure analysis.
    
    Returns:
        str: JSON-formatted evaluation results, or an error if no
            evaluation has been run yet
    """
    global _last_evaluation_result
    
    if _last_evaluation_result is None:
        return json.dumps({
            "error": "No evaluation has been run yet",
            "suggestion": "Use run_evaluation to execute an evaluation first"
        }, indent=2)
    
    return json.dumps(_last_evaluation_result, indent=2)


async def analyze_failures() -> str:
    """Deep-dive into failure patterns from the last evaluation.
    
    Provides detailed analysis of failures including:
    - Common failure patterns
    - Sample failure examples with inputs/outputs
    - Failure rate statistics
    
    Returns:
        str: JSON-formatted failure analysis, or a message if there
            were no failures or no evaluation has been run
    """
    global _last_evaluation_result
    
    if _last_evaluation_result is None:
        return json.dumps({
            "error": "No evaluation has been run yet",
            "suggestion": "Use run_evaluation to execute an evaluation first"
        }, indent=2)
    
    failure_analysis = _last_evaluation_result.get("failure_analysis")
    
    if failure_analysis is None:
        return json.dumps({
            "message": "No failures detected in the last evaluation",
            "all_metrics_passed": True
        }, indent=2)
    
    return json.dumps(failure_analysis, indent=2)


async def generate_dataset(params: GenerateDatasetInput) -> str:
    """Generate a synthetic test dataset for evaluation.
    
    Creates a JSONL dataset file with synthetic test cases appropriate
    for the specified app type.
    
    Args:
        params: GenerateDatasetInput containing:
            - output_path (str): Where to save the dataset
            - num_samples (int): Number of samples to generate (1-1000)
            - app_type (str): Type of app (e.g., 'chat', 'rag', 'agent')
    
    Returns:
        str: JSON-formatted result with:
            - path (str): Path where dataset was saved
            - num_samples (int): Number of samples generated
            - preview (list): First few samples for verification
    """
    # Ensure output directory exists
    output_path = Path(params.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate synthetic data based on app type
    samples = []
    for i in range(params.num_samples):
        if params.app_type == "chat":
            samples.append({
                "input": f"Sample chat query {i+1}",
                "expected_output": f"Sample chat response {i+1}",
                "metadata": {"sample_id": i+1}
            })
        elif params.app_type == "rag":
            samples.append({
                "query": f"Sample RAG query {i+1}",
                "context": f"Sample context for query {i+1}",
                "expected_answer": f"Sample answer {i+1}",
                "metadata": {"sample_id": i+1}
            })
        else:  # generic/agent
            samples.append({
                "input": f"Sample input {i+1}",
                "expected_output": f"Sample output {i+1}",
                "metadata": {"sample_id": i+1, "app_type": params.app_type}
            })
    
    # Write to JSONL file
    with open(output_path, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    
    return json.dumps({
        "success": True,
        "path": str(output_path),
        "num_samples": params.num_samples,
        "app_type": params.app_type,
        "preview": samples[:3]  # Show first 3 samples
    }, indent=2)


async def preview_dataset(params: PreviewDatasetInput) -> str:
    """Preview the contents of a dataset file.
    
    Reads and displays the first N rows of a JSONL dataset file
    to help verify its structure and contents.
    
    Args:
        params: PreviewDatasetInput containing:
            - dataset_path (str): Path to dataset file
            - num_rows (int): Number of rows to preview (1-50)
    
    Returns:
        str: JSON-formatted preview with:
            - path (str): Dataset file path
            - total_rows (int): Total rows in dataset
            - preview_rows (list): Sample rows from dataset
            - columns (list): Column names found
    """
    try:
        # Read all rows to count them
        all_rows = _read_jsonl_file(params.dataset_path, max_rows=10000)
        
        if not all_rows:
            return json.dumps({
                "error": "Dataset file is empty or contains no valid JSON",
                "path": params.dataset_path
            }, indent=2)
        
        # Get preview rows
        preview_rows = all_rows[:params.num_rows]
        
        # Extract column names from first row
        columns = list(preview_rows[0].keys()) if preview_rows else []
        
        result = DatasetPreview(
            path=params.dataset_path,
            total_rows=len(all_rows),
            preview_rows=preview_rows,
            columns=columns,
        )
        
        return json.dumps(result.model_dump(), indent=2)
        
    except FileNotFoundError:
        return json.dumps({
            "error": f"Dataset file not found: {params.dataset_path}",
            "suggestion": "Check that the path is correct"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to read dataset: {str(e)}",
            "suggestion": "Ensure the file is in JSONL format (one JSON object per line)"
        }, indent=2)
