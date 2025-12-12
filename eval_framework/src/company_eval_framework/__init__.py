"""
Company Evaluation Framework

A reusable evaluation framework that wraps Phoenix Evals + OpenAI
for systematic LLM application testing.

This package provides:
- Configuration loading and validation
- Dataset loading (static) and generation (synthetic)
- Evaluation suites for different app types
- Axial coding for failure analysis
- A CLI for CI/CD integration

Quick Start:
    # Run from command line
    company-eval ci-run --config path/to/config.yaml

    # Or use programmatically
    from company_eval_framework import load_eval_config, build_dataset, run_ci_evaluation

    config = load_eval_config("llm_eval_simple_chat.yaml")
    exit_code = run_ci_evaluation("llm_eval_simple_chat.yaml")
"""

from .config import (
    AdapterConfig,
    DatasetConfig,
    EvalConfig,
    ThresholdConfig,
    load_eval_config,
)
from .dataset import (
    build_dataset,
    generate_synthetic_dataset,
    load_static_dataset,
)
from .evaluators import (
    EvaluatorSpec,
    build_agent_suite,
    build_basic_chat_suite,
    build_basic_rag_suite,
    build_eval_suite,
    build_multi_agent_suite,
    get_llm_judge,
    run_evaluations,
    run_evaluations_sync,
)
from .axial import (
    build_failure_type_classifier,
    get_failure_examples,
    run_axial_coding,
    run_axial_coding_sync,
    summarize_failure_types,
)
from .runner import run_ci_evaluation
from .utils import read_jsonl, write_jsonl


__version__ = "0.1.0"

__all__ = [
    # Config
    "AdapterConfig",
    "DatasetConfig",
    "EvalConfig",
    "ThresholdConfig",
    "load_eval_config",
    # Dataset
    "build_dataset",
    "generate_synthetic_dataset",
    "load_static_dataset",
    # Evaluators
    "EvaluatorSpec",
    "build_agent_suite",
    "build_basic_chat_suite",
    "build_basic_rag_suite",
    "build_eval_suite",
    "build_multi_agent_suite",
    "get_llm_judge",
    "run_evaluations",
    "run_evaluations_sync",
    # Axial coding
    "build_failure_type_classifier",
    "get_failure_examples",
    "run_axial_coding",
    "run_axial_coding_sync",
    "summarize_failure_types",
    # Runner
    "run_ci_evaluation",
    # Utils
    "read_jsonl",
    "write_jsonl",
]
