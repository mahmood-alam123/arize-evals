"""MCP server implementation for the evaluation framework.

This module provides a Model Context Protocol (MCP) server that enables AI assistants
to run evaluations, analyze results, and manage datasets conversationally.

To use this server:

1. Install with MCP support:
   pip install -e ".[mcp]"

2. Run the MCP server:
   company-eval-mcp

3. Configure your MCP client (e.g., Claude Code):
   Add to ~/.claude.json or similar:
   {
     "mcpServers": {
       "company-eval": {
         "command": "company-eval-mcp"
       }
     }
   }

Available tools:
- run_evaluation: Execute a full evaluation pipeline
- list_configs: Discover available evaluation configurations
- list_eval_suites: List available evaluation suites
- validate_config: Validate a configuration without running
- get_evaluation_results: Get results from the last evaluation
- analyze_failures: Analyze failure patterns
- generate_dataset: Generate synthetic test datasets
- preview_dataset: Preview dataset contents

Available resources:
- eval://config/{path}: Read configuration files
- eval://dataset/{path}: Read dataset samples
- eval://results/latest: Get latest evaluation results
"""

from .server import mcp, main
from .types import (
    EvaluationResult,
    MetricResult,
    FailureAnalysis,
    FailureExample,
    ConfigSummary,
    EvalSuiteInfo,
    DatasetPreview,
)

__all__ = [
    "mcp",
    "main",
    "EvaluationResult",
    "MetricResult",
    "FailureAnalysis",
    "FailureExample",
    "ConfigSummary",
    "EvalSuiteInfo",
    "DatasetPreview",
]
