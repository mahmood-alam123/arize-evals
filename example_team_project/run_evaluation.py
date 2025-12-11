"""Run end-to-end evaluation of the customer support agent."""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent / "eval_framework" / "src"))

from company_eval_framework import run_evaluation, load_eval_dataset, print_evaluation_summary
from my_app.eval_adapter import evaluate_agent_response, initialize_agent
from config_loader import load_config, get_agent_config, get_eval_config


if __name__ == "__main__":
    print("⚙️  Loading configuration...\n")
    
    # Load configuration
    config = load_config()
    agent_kwargs = get_agent_config(config)
    eval_config = get_eval_config(config)
    
    # Initialize agent with config
    print(f"Agent Type: {agent_kwargs['agent_type']}")
    if agent_kwargs['agent_type'] == 'openai':
        print(f"  Model: {agent_kwargs.get('model', 'gpt-3.5-turbo')}")
    print()
    
    # Initialize the adapter's agent
    initialize_agent(**agent_kwargs)
    
    # Load evaluation dataset
    dataset_path = Path(__file__).parent / eval_config["dataset_path"]
    eval_data = load_eval_dataset(str(dataset_path))
    
    # Run evaluation
    print(f"🔍 Running evaluation on {len(eval_data)} test cases...\n")
    summary = run_evaluation(
        adapter_func=evaluate_agent_response,
        eval_data=eval_data,
    )
    
    # Print results
    print_evaluation_summary(summary)
    
    # Save results
    output_path = Path(__file__).parent / eval_config["results_dir"] / "evaluation_results.json"
    from company_eval_framework.runner import EvaluationRunner
    runner = EvaluationRunner()
    runner.save_results(summary, str(output_path))
    print(f"\n✅ Results saved to {output_path}")
