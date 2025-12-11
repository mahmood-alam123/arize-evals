"""Main evaluation runner for single-agent LLM workflows."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .evaluators import (
    BaseEvaluator,
    EvaluationResult,
    EvaluationMetric,
    EVALUATORS,
)


@dataclass
class EvaluationRun:
    """Results from a single evaluation run."""
    
    query: str
    response: str
    context: Optional[str]
    results: List[EvaluationResult]
    overall_score: float
    all_passed: bool


@dataclass
class EvaluationSummary:
    """Summary of all evaluation runs."""
    
    total_runs: int
    passed_runs: int
    failed_runs: int
    metric_scores: Dict[str, float]
    runs: List[EvaluationRun]


class EvaluationRunner:
    """Orchestrates evaluation of single-agent LLM workflows."""
    
    def __init__(self, metrics: Optional[List[EvaluationMetric]] = None):
        """Initialize the runner.
        
        Args:
            metrics: List of metrics to evaluate. Defaults to all.
        """
        self.metrics = metrics or list(EVALUATORS.keys())
        self.evaluators: Dict[EvaluationMetric, BaseEvaluator] = {
            metric: EVALUATORS[metric]() for metric in self.metrics
        }
    
    def evaluate_response(
        self,
        response: str,
        query: str,
        context: Optional[str] = None,
    ) -> EvaluationRun:
        """Evaluate a single response.
        
        Args:
            response: The agent's response
            query: The original query
            context: Optional business context
            
        Returns:
            EvaluationRun with all metric results
        """
        results = []
        
        for metric, evaluator in self.evaluators.items():
            result = evaluator.evaluate(response, query, context)
            results.append(result)
        
        # Calculate overall score (average of all metrics)
        overall_score = sum(r.score for r in results) / len(results) if results else 0.0
        all_passed = all(r.passed for r in results)
        
        return EvaluationRun(
            query=query,
            response=response,
            context=context,
            results=results,
            overall_score=overall_score,
            all_passed=all_passed,
        )
    
    def evaluate_batch(
        self,
        eval_data: List[Dict[str, Any]],
    ) -> EvaluationSummary:
        """Evaluate a batch of responses.
        
        Args:
            eval_data: List of dicts with keys: response, query, context
            
        Returns:
            EvaluationSummary with all runs and aggregated metrics
        """
        runs = []
        
        for item in eval_data:
            run = self.evaluate_response(
                response=item.get("response", ""),
                query=item.get("query", ""),
                context=item.get("context"),
            )
            runs.append(run)
        
        # Aggregate metrics
        metric_scores = {}
        for metric in self.metrics:
            scores = [
                r.score
                for run in runs
                for r in run.results
                if r.metric == metric
            ]
            metric_scores[metric.value] = sum(scores) / len(scores) if scores else 0.0
        
        # Count pass/fail
        passed_runs = sum(1 for run in runs if run.all_passed)
        failed_runs = len(runs) - passed_runs
        
        return EvaluationSummary(
            total_runs=len(runs),
            passed_runs=passed_runs,
            failed_runs=failed_runs,
            metric_scores=metric_scores,
            runs=runs,
        )
    
    def save_results(self, summary: EvaluationSummary, filepath: str) -> None:
        """Save evaluation results to JSON.
        
        Args:
            summary: EvaluationSummary to save
            filepath: Path to save JSON file
        """
        # Convert dataclasses to dicts for JSON serialization
        results_dict = {
            "total_runs": summary.total_runs,
            "passed_runs": summary.passed_runs,
            "failed_runs": summary.failed_runs,
            "metric_scores": summary.metric_scores,
            "runs": [
                {
                    "query": run.query,
                    "response": run.response,
                    "context": run.context,
                    "overall_score": run.overall_score,
                    "all_passed": run.all_passed,
                    "results": [
                        {
                            "metric": r.metric.value,
                            "score": r.score,
                            "reason": r.reason,
                            "passed": r.passed,
                        }
                        for r in run.results
                    ],
                }
                for run in summary.runs
            ],
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(results_dict, f, indent=2)


def run_evaluation(
    adapter_func,
    eval_data: List[Dict[str, Any]],
    metrics: Optional[List[EvaluationMetric]] = None,
) -> EvaluationSummary:
    """High-level function to run evaluation.
    
    Args:
        adapter_func: Function that takes query/context and returns response dict
        eval_data: List of evaluation items
        metrics: Optional list of metrics to use
        
    Returns:
        EvaluationSummary
    """
    runner = EvaluationRunner(metrics=metrics)
    
    # Call adapter for each item and enrich with response
    enriched_data = []
    for item in eval_data:
        result = adapter_func(
            query=item.get("query"),
            context=item.get("context"),
        )
        enriched_data.append({
            **item,
            "response": result.get("response"),
        })
    
    return runner.evaluate_batch(enriched_data)
