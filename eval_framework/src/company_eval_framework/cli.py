"""
Command-line interface for the evaluation framework.

Provides the `company-eval` CLI with subcommands for running evaluations.
"""

import argparse
import sys

from .runner import run_ci_evaluation


def cmd_ci_run(args: argparse.Namespace) -> int:
    """
    Execute the ci-run subcommand.

    Runs the full CI evaluation pipeline using the specified config file.

    Args:
        args: Parsed command-line arguments with 'config' attribute

    Returns:
        Exit code from run_ci_evaluation (0 = pass, 1 = fail)
    """
    return run_ci_evaluation(args.config)


def cmd_sample_prod(args: argparse.Namespace) -> int:
    """
    Execute the sample-prod subcommand (stub).

    This subcommand is a placeholder for future production sampling functionality.
    It would allow teams to sample and evaluate production traffic.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code 0
    """
    print("=" * 50)
    print("  Production Sampling")
    print("=" * 50)
    print()
    print("Production sampling is not yet implemented.")
    print()
    print("Future functionality will include:")
    print("  - Sampling traces from production observability systems")
    print("  - Running evaluations on sampled data")
    print("  - Generating quality reports over time")
    print("  - Alerting on quality regressions")
    print()
    print("For now, use 'company-eval ci-run' for CI/CD evaluation.")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser with subcommands
    """
    parser = argparse.ArgumentParser(
        prog="company-eval",
        description="Company LLM Evaluation Framework CLI",
        epilog="Use 'company-eval <command> --help' for more information on a command.",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        dest="command",
    )

    # ci-run subcommand
    ci_run_parser = subparsers.add_parser(
        "ci-run",
        help="Run evaluation in CI mode",
        description=(
            "Run the full evaluation pipeline for CI/CD. "
            "Loads config, builds dataset, runs adapter, evaluates, "
            "and returns exit code 0 (pass) or 1 (fail)."
        ),
    )
    ci_run_parser.add_argument(
        "--config",
        "-c",
        required=True,
        metavar="PATH",
        help="Path to the evaluation config YAML file",
    )
    ci_run_parser.set_defaults(func=cmd_ci_run)

    # sample-prod subcommand (stub)
    sample_prod_parser = subparsers.add_parser(
        "sample-prod",
        help="Sample and evaluate production traffic (not yet implemented)",
        description=(
            "Sample traces from production and run evaluations. "
            "This feature is not yet implemented."
        ),
    )
    sample_prod_parser.add_argument(
        "--config",
        "-c",
        metavar="PATH",
        help="Path to the evaluation config YAML file (not used yet)",
    )
    sample_prod_parser.add_argument(
        "--sample-size",
        "-n",
        type=int,
        default=100,
        help="Number of samples to evaluate (default: 100)",
    )
    sample_prod_parser.add_argument(
        "--start-time",
        metavar="TIMESTAMP",
        help="Start of sampling window (ISO format)",
    )
    sample_prod_parser.add_argument(
        "--end-time",
        metavar="TIMESTAMP",
        help="End of sampling window (ISO format)",
    )
    sample_prod_parser.set_defaults(func=cmd_sample_prod)

    return parser


def main() -> None:
    """
    Main entry point for the CLI.

    Parses arguments, dispatches to the appropriate subcommand handler,
    and exits with the returned exit code.
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
