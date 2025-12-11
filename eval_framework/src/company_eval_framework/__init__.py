"""Company Evaluation Framework for single-agent LLM workflows."""

from .evaluators import (
    EvaluationMetric,
    EvaluationResult,
    BaseEvaluator,
    CoherenceEvaluator,
    RelevanceEvaluator,
    SafetyEvaluator,
    CompletenessEvaluator,
    ToneEvaluator,
)

from .runner import (
    EvaluationRun,
    EvaluationSummary,
    EvaluationRunner,
    run_evaluation,
)

from .end_to_end_eval import (
    load_eval_dataset,
    print_evaluation_summary,
    evaluate_app,
)

__version__ = "0.1.0"

__all__ = [
    # Evaluators
    "EvaluationMetric",
    "EvaluationResult",
    "BaseEvaluator",
    "CoherenceEvaluator",
    "RelevanceEvaluator",
    "SafetyEvaluator",
    "CompletenessEvaluator",
    "ToneEvaluator",
    # Runner
    "EvaluationRun",
    "EvaluationSummary",
    "EvaluationRunner",
    "run_evaluation",
    # End-to-end
    "load_eval_dataset",
    "print_evaluation_summary",
    "evaluate_app",
]
