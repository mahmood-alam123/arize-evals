"""Run end-to-end evaluation of the example app."""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent / "eval_framework" / "src"))

from company_eval_framework import run_evaluation, load_eval_dataset, print_evaluation_summary
from my_app.eval_adapter import evaluate_agent_response


if __name__ == "__main__":
    # Load evaluation dataset
    dataset_path = Path(__file__).parent / "eval_dataset.json"
    eval_data = load_eval_dataset(str(dataset_path))
    
    # Run evaluation
    print("\n🔍 Running evaluation...\n")
    summary = run_evaluation(
        adapter_func=evaluate_agent_response,
        eval_data=eval_data,
    )
    
    # Print results
    print_evaluation_summary(summary)
    
    # Save results
    output_path = Path(__file__).parent / "eval_results" / "evaluation_results.json"
    from company_eval_framework.runner import EvaluationRunner
    runner = EvaluationRunner()
    runner.save_results(summary, str(output_path))
    print(f"\n✅ Results saved to {output_path}")
