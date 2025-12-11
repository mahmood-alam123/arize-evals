"""End-to-end evaluation script for single-agent LLM workflows."""

import json
from pathlib import Path
from typing import Dict, Any, List

from .runner import run_evaluation, EvaluationRunner
from .evaluators import EvaluationMetric


def load_eval_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    """Load evaluation dataset from JSON file.
    
    Args:
        dataset_path: Path to JSON dataset file
        
    Returns:
        List of evaluation items
    """
    with open(dataset_path, "r") as f:
        return json.load(f)


def print_evaluation_summary(summary) -> None:
    """Pretty print evaluation summary.
    
    Args:
        summary: EvaluationSummary object
    """
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    print(f"\nTotal Runs: {summary.total_runs}")
    print(f"Passed: {summary.passed_runs} ✓")
    print(f"Failed: {summary.failed_runs} ✗")
    print(f"Pass Rate: {summary.passed_runs/summary.total_runs*100:.1f}%")
    
    print("\nMetric Scores:")
    print("-" * 70)
    for metric, score in summary.metric_scores.items():
        status = "✓" if score >= 0.7 else "✗"
        print(f"  {metric:15s}: {score:.2f} {status}")
    
    print("\nDetailed Results:")
    print("-" * 70)
    for i, run in enumerate(summary.runs, 1):
        status = "✓ PASS" if run.all_passed else "✗ FAIL"
        print(f"\n  Run {i}: {status} (Overall: {run.overall_score:.2f})")
        print(f"    Query: {run.query}")
        print(f"    Response: {run.response[:100]}...")
        for result in run.results:
            metric_status = "✓" if result.passed else "✗"
            print(f"      {result.metric.value:15s}: {result.score:.2f} {metric_status} - {result.reason}")
    
    print("\n" + "="*70 + "\n")


def evaluate_app(
    adapter_func,
    dataset_path: str,
    output_dir: str = "eval_results",
    metrics: List[EvaluationMetric] = None,
) -> None:
    """End-to-end evaluation of an LLM app.
    
    Args:
        adapter_func: Adapter function from the app
        dataset_path: Path to evaluation dataset
        output_dir: Directory to save results
        metrics: Optional list of metrics to evaluate
    """
    print(f"\n📊 Starting evaluation...")
    print(f"📂 Loading dataset from: {dataset_path}")
    
    # Load dataset
    eval_data = load_eval_dataset(dataset_path)
    print(f"✓ Loaded {len(eval_data)} evaluation items")
    
    # Run evaluation
    print(f"\n🔄 Running evaluation...")
    summary = run_evaluation(adapter_func, eval_data, metrics=metrics)
    
    # Print results
    print_evaluation_summary(summary)
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    results_file = output_path / "evaluation_results.json"
    
    runner = EvaluationRunner(metrics=metrics)
    runner.save_results(summary, str(results_file))
    print(f"💾 Results saved to: {results_file}")
    
    return summary
