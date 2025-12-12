"""
Evaluation runner module.

This module orchestrates the full evaluation flow:
1. Load configuration
2. Build/load dataset
3. Run the team's adapter to get model outputs
4. Run evaluation suite
5. Compute metrics and compare to thresholds
6. Run axial coding on failures
7. Print summary and return exit code
"""

import importlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .axial import run_axial_coding_sync, summarize_failure_types, get_failure_examples
from .config import EvalConfig, ThresholdConfig, load_eval_config
from .dataset import build_dataset
from .evaluators import build_eval_suite, get_llm_judge, run_evaluations_sync
from .utils import read_jsonl, write_jsonl


def run_ci_evaluation(config_path: str) -> int:
    """
    Main entry point for CI evaluation.

    This function orchestrates the entire evaluation process:
    1. Loads the evaluation config
    2. Builds/loads the test dataset
    3. Calls the team's adapter to produce model outputs
    4. Runs the evaluation suite on the outputs
    5. Computes aggregate metrics and compares to thresholds
    6. Runs axial coding on failures for debugging insights
    7. Prints a human-readable summary
    8. Returns exit code (0 = pass, 1 = fail)

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Exit code: 0 if all metrics pass thresholds, 1 otherwise
    """
    print("=" * 50)
    print("  Company LLM Evaluation")
    print("=" * 50)
    print()

    # Step 1: Load configuration
    print(f"Loading config from: {config_path}")
    config = load_eval_config(config_path)
    print(f"App Name: {config.app_name}")
    print(f"App Type: {config.app_type}")
    print(f"Eval Suite: {config.eval_suite}")
    print()

    # Step 2: Build dataset
    print("Building dataset...")
    dataset_df = build_dataset(config)
    dataset_mode = config.dataset.mode
    print(f"Dataset Size: {len(dataset_df)} rows ({dataset_mode})")
    print()

    # Step 3: Save dataset to temp file and run adapter
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "inputs.jsonl")
        output_path = os.path.join(tmpdir, "outputs.jsonl")

        # Write inputs
        write_jsonl(dataset_df, input_path)

        # Dynamically import and call the adapter
        print(f"Running adapter: {config.adapter.module}.{config.adapter.function}")
        try:
            adapter_module = importlib.import_module(config.adapter.module)
            adapter_fn = getattr(adapter_module, config.adapter.function)
            adapter_fn(input_path, output_path)
            print("  Adapter completed successfully")
        except Exception as e:
            print(f"  ERROR: Adapter failed: {e}")
            return 1

        # Step 4: Load outputs
        if not os.path.exists(output_path):
            print(f"  ERROR: Adapter did not produce output file: {output_path}")
            return 1

        outputs_df = read_jsonl(output_path)
        print(f"  Loaded {len(outputs_df)} model outputs")
        print()

        # Merge inputs with outputs on conversation_id if needed
        if "output" not in outputs_df.columns:
            print("  ERROR: Output file missing 'output' column")
            return 1

        # Use outputs_df as the main dataframe (should have all columns)
        eval_df = outputs_df

    # Step 5: Run evaluation suite
    print(f"Running evaluation suite ({config.eval_suite})...")
    evaluators = build_eval_suite(config.eval_suite)
    llm = get_llm_judge()

    print(f"  Evaluators: {', '.join(e.name for e in evaluators)}")
    eval_results = run_evaluations_sync(eval_df, evaluators, llm)
    print("  Evaluation complete")
    print()

    # Step 6: Compute metrics and check thresholds
    print("-" * 50)
    print("  Metric Summary (Mean Scores)")
    print("-" * 50)

    metric_results = compute_metrics(eval_results, evaluators, config.thresholds)
    all_passed = print_metric_summary(metric_results)
    print()

    # Step 7: Run axial coding on failures
    print("-" * 50)
    print("  Failure Axial Coding")
    print("-" * 50)

    # Identify failures (any row with any metric score < 1)
    failure_mask = pd.Series([False] * len(eval_results))
    for evaluator in evaluators:
        score_col = f"{evaluator.name}_score"
        if score_col in eval_results.columns:
            failure_mask |= (eval_results[score_col] < 1.0)

    failures_df = eval_results[failure_mask]

    if failures_df.empty:
        print("No failures detected - axial coding skipped.")
    else:
        print(f"Analyzing {len(failures_df)} failing conversations...")
        coded_failures = run_axial_coding_sync(failures_df, llm)
        summary = summarize_failure_types(coded_failures)

        print("\nFailure type distribution:")
        for failure_type, count in summary["top_types"][:5]:
            pct = summary["percentages"].get(failure_type, 0)
            print(f"  - {failure_type}: {count} ({pct:.1f}%)")

        # Show example for top failure type
        if summary["top_types"]:
            top_type = summary["top_types"][0][0]
            examples = get_failure_examples(coded_failures, top_type, n=1)
            if not examples.empty:
                ex = examples.iloc[0]
                print(f"\nExample ({top_type}):")
                print(f"  USER: {str(ex.get('input', ''))[:100]}...")
                print(f"  RESPONSE: {str(ex.get('output', ''))[:100]}...")

    print()
    print("-" * 50)

    # Step 8: Final result
    if all_passed:
        print("  FINAL RESULT: PASS")
        print("-" * 50)
        return 0
    else:
        print("  FINAL RESULT: FAIL")
        print("-" * 50)
        return 1


def compute_metrics(
    eval_results: pd.DataFrame,
    evaluators: list,
    thresholds: Dict[str, ThresholdConfig],
) -> List[Dict]:
    """
    Compute aggregate metrics and compare to thresholds.

    Args:
        eval_results: DataFrame with evaluation results
        evaluators: List of EvaluatorSpec objects
        thresholds: Dict of metric name to ThresholdConfig

    Returns:
        List of dicts with metric info including:
        - name: Metric name
        - mean: Mean score
        - threshold_type: "max" or "min"
        - threshold_value: The threshold value
        - passed: Whether the metric passed
    """
    results = []

    for evaluator in evaluators:
        score_col = f"{evaluator.name}_score"
        if score_col not in eval_results.columns:
            continue

        mean_score = eval_results[score_col].mean()

        # Check thresholds
        threshold = thresholds.get(evaluator.name)
        passed = True
        threshold_type = None
        threshold_value = None

        if threshold:
            if threshold.max_mean is not None:
                threshold_type = "max"
                threshold_value = threshold.max_mean
                # For metrics where lower is better (like frustration, toxicity)
                # we check if mean <= max_mean
                # But score is inverted (1 = good), so we need to check 1 - mean
                # Actually, score represents success rate, so mean is proportion passing
                # For "negative" metrics like frustration, score=1 means NOT frustrated
                # So we want (1 - mean) <= max_mean, i.e., failure rate <= max
                failure_rate = 1.0 - mean_score
                passed = failure_rate <= threshold.max_mean

            if threshold.min_mean is not None:
                threshold_type = "min"
                threshold_value = threshold.min_mean
                passed = passed and (mean_score >= threshold.min_mean)

        results.append({
            "name": evaluator.name,
            "mean": mean_score,
            "failure_rate": 1.0 - mean_score,
            "threshold_type": threshold_type,
            "threshold_value": threshold_value,
            "passed": passed,
        })

    return results


def print_metric_summary(metric_results: List[Dict]) -> bool:
    """
    Print a formatted metric summary table.

    Args:
        metric_results: List of metric result dicts from compute_metrics

    Returns:
        True if all metrics passed, False otherwise
    """
    print(f"{'Metric':<25} {'Mean':>8} {'Threshold':>15} {'Status':>10}")
    print("-" * 60)

    all_passed = True
    for metric in metric_results:
        name = metric["name"]
        mean = metric["mean"]

        # Format threshold string
        if metric["threshold_type"] == "max":
            # For max thresholds, show failure rate vs threshold
            threshold_str = f"<= {metric['threshold_value']:.2f}"
            display_value = metric["failure_rate"]
        elif metric["threshold_type"] == "min":
            threshold_str = f">= {metric['threshold_value']:.2f}"
            display_value = mean
        else:
            threshold_str = "N/A"
            display_value = mean

        status = "PASS" if metric["passed"] else "FAIL"
        status_icon = "" if metric["passed"] else ""

        print(f"{name:<25} {display_value:>8.2f} {threshold_str:>15} {status_icon:>2} {status:>6}")

        if not metric["passed"]:
            all_passed = False

    print()
    if all_passed:
        print("All metrics satisfy their thresholds.")
    else:
        print("At least one threshold was violated.")

    return all_passed
