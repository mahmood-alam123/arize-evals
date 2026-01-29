"""MCP server for the evaluation framework.

This server exposes evaluation framework capabilities through the Model Context Protocol,
enabling AI assistants to run evaluations, analyze results, and manage datasets conversationally.
"""

from mcp.server.fastmcp import FastMCP

from .tools import (
    run_evaluation,
    list_configs,
    list_eval_suites,
    validate_config,
    get_evaluation_results,
    analyze_failures,
    generate_dataset,
    preview_dataset,
    RunEvaluationInput,
    ListConfigsInput,
    ValidateConfigInput,
    GenerateDatasetInput,
    PreviewDatasetInput,
)
from .resources import (
    get_config_resource,
    get_dataset_resource,
    get_latest_results_resource,
)


# Initialize FastMCP server
mcp = FastMCP("company_eval_mcp")


# ==============================================================================
# Core Tools
# ==============================================================================


@mcp.tool(
    name="run_evaluation",
    annotations={
        "title": "Run Evaluation",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def run_evaluation_tool(params: RunEvaluationInput, ctx) -> str:
    """Execute a full evaluation pipeline from a configuration file.
    
    This tool runs the complete evaluation process including loading config,
    initializing the app adapter, running evaluations on the dataset, collecting
    metrics, and caching results for later analysis.
    
    Use this when you need to:
    - Run a complete evaluation of an AI application
    - Test an app against a dataset using specific metrics
    - Generate results that can be analyzed later
    
    Args:
        params: RunEvaluationInput with config_path
        ctx: MCP context for progress reporting
        
    Returns:
        JSON with evaluation results including pass/fail status, metrics, and timing
    """
    return await run_evaluation(params, ctx)


@mcp.tool(
    name="list_configs",
    annotations={
        "title": "List Evaluation Configs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def list_configs_tool(params: ListConfigsInput) -> str:
    """Discover available evaluation configurations in a directory.
    
    Searches for YAML configuration files and parses them to provide a summary
    of available evaluations.
    
    Use this when you need to:
    - Discover what evaluations are available
    - Find configuration files in a project
    - Get an overview of configured evaluations
    
    Args:
        params: ListConfigsInput with directory to search
        
    Returns:
        JSON list of config summaries with app names, types, and suites
    """
    return await list_configs(params)


@mcp.tool(
    name="list_eval_suites",
    annotations={
        "title": "List Evaluation Suites",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def list_eval_suites_tool() -> str:
    """List available evaluation suites with their descriptions.
    
    Returns information about built-in evaluation suites including what they
    test for and which app types they work with.
    
    Use this when you need to:
    - Learn about available evaluation suites
    - Choose the right suite for your app type
    - Understand what metrics different suites evaluate
    
    Returns:
        JSON list of suites with descriptions, app types, and metrics
    """
    return await list_eval_suites()


@mcp.tool(
    name="validate_config",
    annotations={
        "title": "Validate Configuration",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def validate_config_tool(params: ValidateConfigInput) -> str:
    """Validate an evaluation configuration without running it.
    
    Checks that the configuration file is valid and contains all required fields
    without actually executing the evaluation.
    
    Use this when you need to:
    - Check if a config file is properly formatted
    - Verify all required fields are present
    - Debug configuration issues before running
    
    Args:
        params: ValidateConfigInput with config_path
        
    Returns:
        JSON with validation results, errors, and warnings
    """
    return await validate_config(params)


# ==============================================================================
# Analysis Tools
# ==============================================================================


@mcp.tool(
    name="get_evaluation_results",
    annotations={
        "title": "Get Evaluation Results",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def get_evaluation_results_tool() -> str:
    """Get detailed results from the most recent evaluation run.
    
    Returns the cached results from the last evaluation, including all metrics,
    scores, and failure analysis.
    
    Use this when you need to:
    - Review results from a recent evaluation
    - Get detailed metric scores
    - Check overall pass/fail status
    
    Returns:
        JSON with complete evaluation results from the last run
    """
    return await get_evaluation_results()


@mcp.tool(
    name="analyze_failures",
    annotations={
        "title": "Analyze Failures",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def analyze_failures_tool() -> str:
    """Deep-dive into failure patterns from the last evaluation.
    
    Provides detailed analysis of failures including common patterns, sample
    failure examples with inputs/outputs, and failure rate statistics.
    
    Use this when you need to:
    - Debug why an evaluation failed
    - Understand common failure patterns
    - Get specific examples of failures
    
    Returns:
        JSON with failure analysis including patterns, examples, and statistics
    """
    return await analyze_failures()


# ==============================================================================
# Dataset Tools
# ==============================================================================


@mcp.tool(
    name="generate_dataset",
    annotations={
        "title": "Generate Synthetic Dataset",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def generate_dataset_tool(params: GenerateDatasetInput) -> str:
    """Generate a synthetic test dataset for evaluation.
    
    Creates a JSONL dataset file with synthetic test cases appropriate for
    the specified app type.
    
    Use this when you need to:
    - Create a test dataset quickly
    - Generate sample data for a new evaluation
    - Prototype an evaluation setup
    
    Args:
        params: GenerateDatasetInput with output_path, num_samples, and app_type
        
    Returns:
        JSON with dataset path and preview of generated samples
    """
    return await generate_dataset(params)


@mcp.tool(
    name="preview_dataset",
    annotations={
        "title": "Preview Dataset",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def preview_dataset_tool(params: PreviewDatasetInput) -> str:
    """Preview the contents of a dataset file.
    
    Reads and displays the first N rows of a JSONL dataset file to help verify
    its structure and contents.
    
    Use this when you need to:
    - Inspect a dataset before running an evaluation
    - Verify dataset format and structure
    - Check what fields are available
    
    Args:
        params: PreviewDatasetInput with dataset_path and num_rows
        
    Returns:
        JSON with dataset preview, column names, and total row count
    """
    return await preview_dataset(params)


# ==============================================================================
# Resources
# ==============================================================================


@mcp.resource("eval://config/{path}")
async def config_resource(path: str) -> str:
    """Access evaluation configuration files.
    
    URI template: eval://config/{path}
    Example: eval://config/my_app.yaml
    
    Returns the raw YAML contents of the configuration file.
    """
    return await get_config_resource(path)


@mcp.resource("eval://dataset/{path}")
async def dataset_resource(path: str) -> str:
    """Access dataset files with automatic preview.
    
    URI template: eval://dataset/{path}
    Example: eval://dataset/datasets/test_data.jsonl
    
    Returns a JSON preview of the first 10 rows from the dataset.
    """
    return await get_dataset_resource(path)


@mcp.resource("eval://results/latest")
async def latest_results_resource() -> str:
    """Access results from the most recent evaluation run.
    
    URI: eval://results/latest
    
    Returns the cached evaluation results from the last run.
    """
    return await get_latest_results_resource()


# ==============================================================================
# Server Entry Point
# ==============================================================================


def main():
    """Main entry point for the MCP server."""
    # Run with stdio transport (default for CLI tools)
    mcp.run()


if __name__ == "__main__":
    main()
