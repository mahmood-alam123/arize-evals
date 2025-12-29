"""
Command-line interface for the evaluation framework.

Provides the `company-eval` CLI with subcommands for running evaluations.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from .runner import run_ci_evaluation, EvaluationResults


def cmd_generate_dataset(args: argparse.Namespace) -> int:
    """
    Generate a synthetic evaluation dataset.

    Creates test queries using an LLM based on the app type and description.
    Saves the dataset to a JSONL file that can be used with ci-run.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code 0 on success, 1 on failure
    """
    import os
    from openai import OpenAI, AzureOpenAI

    print("=" * 60)
    print("  Dataset Generator")
    print("=" * 60)
    print()
    print(f"App Type: {args.app_type}")
    print(f"Description: {args.description or '(default)'}")
    print(f"Examples: {args.num_examples}")
    print(f"Output: {args.output}")
    print()

    # Check for Azure OpenAI first, then standard OpenAI
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if azure_endpoint and azure_deployment:
        api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        model = azure_deployment
        print(f"Using Azure OpenAI: {azure_deployment}")
    else:
        client = OpenAI()
        model = args.model
        print(f"Using OpenAI: {model}")

    print()
    print("Generating dataset...")

    # Build generation prompt based on app type
    prompts = {
        "simple_chat": _get_chat_generation_prompt,
        "rag": _get_rag_generation_prompt,
        "agent": _get_agent_generation_prompt,
        "multi_agent": _get_multi_agent_generation_prompt,
    }

    prompt_fn = prompts.get(args.app_type, _get_chat_generation_prompt)
    system_prompt = prompt_fn(args.description or f"A {args.app_type} application")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Generate exactly {args.num_examples} diverse test queries. "
                               f"Output each query on its own line, with no numbering or bullets."
                }
            ],
            temperature=0.9,
            max_tokens=3000,
        )

        # Parse the generated queries
        raw_output = response.choices[0].message.content or ""
        queries = [
            line.strip()
            for line in raw_output.strip().split("\n")
            if line.strip() and not line.strip().startswith(("-", "*", "•"))
        ]

        # Clean up numbered lines (e.g., "1. Query" -> "Query")
        import re
        queries = [re.sub(r'^\d+[\.\)]\s*', '', q) for q in queries]

        # Ensure we have the right number
        queries = queries[:args.num_examples]

        # Build records
        records = []
        for i, query in enumerate(queries, 1):
            records.append({
                "conversation_id": str(i),
                "input": query,
                "business_context": f"Generated test case {i} for {args.app_type} evaluation."
            })

        # Write to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"Generated {len(records)} examples")
        print(f"Saved to: {args.output}")
        print()
        print("Sample queries:")
        for i, record in enumerate(records[:3], 1):
            print(f"  {i}. {record['input'][:70]}{'...' if len(record['input']) > 70 else ''}")
        if len(records) > 3:
            print(f"  ... and {len(records) - 3} more")
        print()
        print("Next steps:")
        print(f"  1. Review and edit {args.output} as needed")
        print(f"  2. Create a config YAML pointing to this dataset")
        print(f"  3. Run: company-eval ci-run --config your_config.yaml")

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def _get_chat_generation_prompt(description: str) -> str:
    return f"""You are a test data generator for a customer support chatbot.

Application description: {description}

Generate realistic customer support queries that users might ask this chatbot.
Include a mix of:
- Simple FAQ questions (password reset, billing inquiries, account issues)
- More complex requests requiring explanation
- Edge cases and unusual requests
- Both polite and frustrated user tones

Each query should be a realistic user message, 1-3 sentences long.
Do NOT number the queries or use bullet points."""


def _get_rag_generation_prompt(description: str) -> str:
    return f"""You are a test data generator for a RAG (Retrieval-Augmented Generation) application.

Application description: {description}

Generate realistic user queries that would require looking up information from a knowledge base.
Include a mix of:
- Factual questions requiring specific information
- Questions that need context from multiple documents
- Questions with specific entity references (names, dates, products)
- Questions that might have partial or no answers in the docs
- Follow-up questions that reference previous context

Each query should be a realistic user question, 1-2 sentences long.
Do NOT number the queries or use bullet points."""


def _get_agent_generation_prompt(description: str) -> str:
    return f"""You are a test data generator for an AI agent with tool-use capabilities.

Application description: {description}

Generate realistic user requests that would require the agent to use tools or take actions.
Include a mix of:
- Simple tool invocations (check status, look up information)
- Multi-step tasks requiring planning and multiple tool calls
- Ambiguous requests that need clarification
- Tasks that might not need tools at all (just knowledge)
- Complex requests that could fail or need error handling

Each request should be a realistic user message, 1-3 sentences long.
Do NOT number the queries or use bullet points."""


def _get_multi_agent_generation_prompt(description: str) -> str:
    return f"""You are a test data generator for a multi-agent AI system.

Application description: {description}

Generate realistic user requests that would benefit from multiple AI agents collaborating.
Include a mix of:
- Complex tasks requiring planning and execution by different agents
- Research and synthesis tasks needing multiple perspectives
- Tasks with multiple steps or components
- Creative tasks requiring brainstorming and refinement
- Tasks that need coordination between specialist agents

Each request should be a realistic user message, 1-3 sentences long.
Do NOT number the queries or use bullet points."""


def cmd_init(args: argparse.Namespace) -> int:
    """
    Initialize a new evaluation project with starter files.

    Creates a basic directory structure and config files to help teams
    get started quickly.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code 0 on success
    """
    import os

    project_dir = Path(args.directory)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "data").mkdir(exist_ok=True)
    (project_dir / "configs").mkdir(exist_ok=True)

    # Create sample config
    sample_config = f"""# Evaluation Configuration
# Generated by: company-eval init

app_name: my_app
app_type: simple_chat  # Options: simple_chat, rag, agent, multi_agent

adapter:
  module: "{args.directory}.my_adapter"
  function: "run_batch"

dataset:
  mode: "static"
  path: "{args.directory}/data/eval_dataset.jsonl"
  size: 10

eval_suite: "basic_chat"  # Options: basic_chat, basic_rag, agent, multi_agent

thresholds:
  user_frustration:
    max_mean: 0.3
  helpfulness_quality:
    min_mean: 0.7
"""

    config_path = project_dir / "configs" / "eval_config.yaml"
    with open(config_path, "w") as f:
        f.write(sample_config)

    # Create sample adapter
    adapter_code = '''"""
Evaluation adapter for your LLM application.

This module connects your app to the evaluation framework.
Implement the run_batch function to process evaluation inputs.
"""

import json
from typing import Iterable


def _read_jsonl(path: str) -> Iterable[dict]:
    """Read a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _write_jsonl(path: str, rows: Iterable[dict]) -> None:
    """Write records to a JSONL file."""
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\\n")


def run_batch(input_path: str, output_path: str) -> None:
    """
    Process a batch of evaluation inputs through your LLM app.

    Args:
        input_path: Path to input JSONL with test cases
        output_path: Path to write results JSONL

    Each input row should have:
        - conversation_id: Unique identifier
        - input: The user query

    Each output row should have all input fields plus:
        - output: Your app's response
    """
    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input", "")

        # TODO: Replace this with your actual LLM app call
        # response = your_app.process(query)
        response = f"This is a placeholder response for: {query}"

        row_out = dict(row)
        row_out["output"] = response
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)
'''

    adapter_path = project_dir / "my_adapter.py"
    with open(adapter_path, "w") as f:
        f.write(adapter_code)

    # Create __init__.py
    init_path = project_dir / "__init__.py"
    with open(init_path, "w") as f:
        f.write('"""Evaluation project package."""\n')

    # Create sample dataset
    sample_data = [
        {"conversation_id": "1", "input": "How do I reset my password?", "business_context": "User needs account help."},
        {"conversation_id": "2", "input": "What are your pricing plans?", "business_context": "User considering upgrade."},
        {"conversation_id": "3", "input": "Can I cancel anytime?", "business_context": "User evaluating commitment."},
    ]

    data_path = project_dir / "data" / "eval_dataset.jsonl"
    with open(data_path, "w") as f:
        for record in sample_data:
            f.write(json.dumps(record) + "\n")

    print("=" * 60)
    print("  Project Initialized")
    print("=" * 60)
    print()
    print(f"Created project structure in: {project_dir}/")
    print()
    print("Files created:")
    print(f"  {project_dir}/")
    print(f"  ├── __init__.py")
    print(f"  ├── my_adapter.py          # Your adapter (edit this!)")
    print(f"  ├── configs/")
    print(f"  │   └── eval_config.yaml   # Evaluation config")
    print(f"  └── data/")
    print(f"      └── eval_dataset.jsonl # Sample dataset")
    print()
    print("Next steps:")
    print(f"  1. Edit {adapter_path} to call your LLM app")
    print(f"  2. Generate more test data:")
    print(f"     company-eval generate-dataset --app-type simple_chat \\")
    print(f"       --output {data_path} --num-examples 20")
    print(f"  3. Run evaluation:")
    print(f"     company-eval ci-run --config {config_path}")
    print()

    return 0


def cmd_ci_run(args: argparse.Namespace) -> int:
    """
    Execute the ci-run subcommand.

    Runs the full CI evaluation pipeline using the specified config file.

    Args:
        args: Parsed command-line arguments with 'config' attribute

    Returns:
        Exit code from run_ci_evaluation (0 = pass, 1 = fail)
    """
    # Get dashboard URL from args or environment
    report_to = getattr(args, "report_to", None) or os.environ.get("EVAL_DASHBOARD_URL")

    if report_to:
        # Run with result capture and report to dashboard
        result = run_ci_evaluation(args.config, return_results=True)
        if isinstance(result, EvaluationResults):
            _report_to_dashboard(report_to, result)
            return 0 if result.passed else 1
        return result
    else:
        return run_ci_evaluation(args.config)


def _report_to_dashboard(dashboard_url: str, results: EvaluationResults) -> None:
    """Report evaluation results to the dashboard API."""
    import urllib.request
    import urllib.error

    url = f"{dashboard_url.rstrip('/')}/api/runs"
    data = json.dumps(results.to_dict()).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode())
            print()
            print(f"Results reported to dashboard: {dashboard_url}")
            print(f"Run ID: {response_data.get('id', 'unknown')}")
    except urllib.error.URLError as e:
        print(f"\nWarning: Failed to report to dashboard: {e}")
    except Exception as e:
        print(f"\nWarning: Failed to report to dashboard: {e}")


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
    ci_run_parser.add_argument(
        "--report-to",
        metavar="URL",
        help="Dashboard URL to report results to (e.g., http://localhost:8080)",
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

    # init subcommand
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new evaluation project",
        description=(
            "Create a new evaluation project with starter files including "
            "a sample config, adapter template, and example dataset."
        ),
    )
    init_parser.add_argument(
        "directory",
        metavar="DIRECTORY",
        help="Directory name for the new project (e.g., 'my_evals')",
    )
    init_parser.set_defaults(func=cmd_init)

    # generate-dataset subcommand
    gen_parser = subparsers.add_parser(
        "generate-dataset",
        help="Generate a synthetic evaluation dataset",
        description=(
            "Generate test queries using an LLM based on your app type. "
            "Creates a JSONL file ready for use with ci-run."
        ),
    )
    gen_parser.add_argument(
        "--app-type",
        "-t",
        required=True,
        choices=["simple_chat", "rag", "agent", "multi_agent"],
        help="Type of application to generate test cases for",
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        required=True,
        metavar="PATH",
        help="Output path for the generated JSONL dataset",
    )
    gen_parser.add_argument(
        "--num-examples",
        "-n",
        type=int,
        default=20,
        help="Number of test cases to generate (default: 20)",
    )
    gen_parser.add_argument(
        "--description",
        "-d",
        metavar="TEXT",
        help="Description of your application for better test generation",
    )
    gen_parser.add_argument(
        "--model",
        "-m",
        default="gpt-4o-mini",
        help="OpenAI model to use for generation (default: gpt-4o-mini)",
    )
    gen_parser.set_defaults(func=cmd_generate_dataset)

    # dashboard subcommand
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Start the Quality Dashboard web server",
        description=(
            "Start the Quality Dashboard server for viewing evaluation results. "
            "Results from ci-run --report-to will be stored and displayed here."
        ),
    )
    dashboard_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)",
    )
    dashboard_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    dashboard_parser.add_argument(
        "--db",
        metavar="PATH",
        default="eval_results.db",
        help="Path to SQLite database (default: eval_results.db)",
    )
    dashboard_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    dashboard_parser.set_defaults(func=cmd_dashboard)

    return parser


def cmd_dashboard(args: argparse.Namespace) -> int:
    """
    Start the Quality Dashboard server.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code 0
    """
    try:
        from .dashboard import main as dashboard_main
    except ImportError as e:
        print("Error: Dashboard dependencies not installed.")
        print("Install with: pip install company-eval-framework[dashboard]")
        print(f"Details: {e}")
        return 1

    print("=" * 60)
    print("  Quality Dashboard")
    print("=" * 60)
    print()
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Database: {args.db}")
    print()
    print("Press Ctrl+C to stop")
    print()

    dashboard_main(
        host=args.host,
        port=args.port,
        db_path=args.db,
        reload=args.reload,
    )
    return 0


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
