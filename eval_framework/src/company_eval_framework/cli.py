"""Command-line interface for evaluation framework."""

import argparse
import json
import sys
from pathlib import Path

from .runner import evaluate_from_config_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Company Evaluation Framework",
        prog="company-eval"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="eval_config.yaml",
        help="Path to eval config file (default: eval_config.yaml)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="eval_results.json",
        help="Path to save results (default: eval_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run evaluation
    try:
        results, all_passed = evaluate_from_config_file(args.config)
        
        # Save results
        output_data = {
            "all_passed": all_passed,
            "results": results,
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
