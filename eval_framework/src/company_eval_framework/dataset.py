"""
Dataset loading and generation module.

This module handles dataset loading from multiple sources:
- Static files (JSONL/CSV)
- Synthetic generation using LLMs
- Quality Dashboard (fetch by dataset name)

Teams can use any approach depending on their evaluation needs.
"""

import json
import uuid
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin

import pandas as pd
import requests
from openai import OpenAI

from .config import EvalConfig


def load_static_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Load a static dataset from a JSONL or CSV file.

    The dataset should contain at minimum:
    - conversation_id: Unique identifier for each conversation
    - input: The user query/input text

    For RAG apps, it may also contain:
    - context: Retrieved document context

    Args:
        config: Evaluation configuration containing dataset path

    Returns:
        DataFrame with the loaded dataset

    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        ValueError: If required columns are missing
    """
    path = config.dataset.path
    if path is None:
        raise ValueError("Dataset path is required for static mode")

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    # Load based on file extension
    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif file_path.suffix.lower() in (".jsonl", ".json"):
        # Read JSONL (one JSON object per line)
        records = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        df = pd.DataFrame(records)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Validate required columns
    required_columns = ["conversation_id", "input"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {missing_columns}. "
            f"Found columns: {list(df.columns)}"
        )

    return df


def generate_synthetic_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Generate a synthetic dataset using an LLM.

    Creates realistic test inputs based on the app type and description.
    This is useful for quickly generating diverse test cases without
    manually curating a dataset.

    Args:
        config: Evaluation configuration with generation parameters

    Returns:
        DataFrame with generated examples containing:
        - conversation_id: Unique identifier
        - input: Generated user query
    """
    client = OpenAI()
    num_examples = config.dataset.num_examples or 20
    model = config.dataset.generation_model or "gpt-4o-mini"
    description = config.dataset.description or f"A {config.app_type} application"

    # Read any prompt files for additional context
    prompt_context = ""
    if config.dataset.prompt_files:
        for prompt_file in config.dataset.prompt_files:
            try:
                with open(prompt_file, "r") as f:
                    prompt_context += f"\n\nPrompt file ({prompt_file}):\n{f.read()}"
            except FileNotFoundError:
                pass  # Skip missing files

    # Build generation prompt based on app type
    generation_prompts = {
        "simple_chat": _get_simple_chat_prompt(description, prompt_context),
        "rag": _get_rag_prompt(description, prompt_context),
        "agent": _get_agent_prompt(description, prompt_context),
        "multi_agent": _get_multi_agent_prompt(description, prompt_context),
    }

    system_prompt = generation_prompts.get(
        config.app_type,
        generation_prompts["simple_chat"]
    )

    # Generate examples in a single call for efficiency
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Generate exactly {num_examples} diverse test queries. "
                           f"Output each query on its own line, with no numbering or bullets."
            }
        ],
        temperature=0.9,
        max_tokens=2000,
    )

    # Parse the generated queries
    raw_output = response.choices[0].message.content or ""
    queries = [
        line.strip()
        for line in raw_output.strip().split("\n")
        if line.strip()
    ]

    # Ensure we have the right number of examples
    queries = queries[:num_examples]
    while len(queries) < num_examples:
        queries.append(f"Sample query {len(queries) + 1}")

    # Build DataFrame
    records = []
    for i, query in enumerate(queries):
        records.append({
            "conversation_id": f"conv_{uuid.uuid4().hex[:8]}",
            "input": query,
        })

    return pd.DataFrame(records)


def load_dashboard_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Load a dataset from the Quality Dashboard by name.

    Fetches the dataset from the dashboard's API endpoint and converts
    the examples to a DataFrame format suitable for evaluation.

    Args:
        config: Evaluation configuration containing dashboard settings

    Returns:
        DataFrame with the loaded dataset containing:
        - conversation_id: Unique identifier for each example
        - input: The user query/input text
        - expected_output: (optional) Expected model response
        - context: (optional) RAG context

    Raises:
        ValueError: If dataset_name is not specified
        requests.HTTPError: If the API request fails
        ConnectionError: If the dashboard is not reachable

    Example YAML configuration:
        dataset:
          mode: "dashboard"
          dataset_name: "customer-support-failures-v2"
          dashboard_url: "http://localhost:8000"  # optional
    """
    dataset_name = config.dataset.dataset_name
    if not dataset_name:
        raise ValueError("Dataset name is required for dashboard mode")

    dashboard_url = config.dataset.dashboard_url or "http://localhost:8000"

    # Ensure URL ends without trailing slash for clean joining
    dashboard_url = dashboard_url.rstrip("/")
    api_url = f"{dashboard_url}/api/datasets/by-name/{dataset_name}"

    print(f"  Fetching dataset '{dataset_name}' from dashboard...")

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to Quality Dashboard at {dashboard_url}. "
            "Make sure the dashboard is running."
        )
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ValueError(
                f"Dataset '{dataset_name}' not found in the Quality Dashboard. "
                "Check the dataset name or create it first."
            )
        raise

    data = response.json()
    examples = data.get("examples", [])

    if not examples:
        raise ValueError(
            f"Dataset '{dataset_name}' has no examples. "
            "Add examples to the dataset before using it."
        )

    # Convert to DataFrame format expected by the evaluation framework
    records = []
    for i, example in enumerate(examples):
        record = {
            "conversation_id": f"dashboard_{dataset_name}_{i}",
            "input": example.get("input", ""),
        }

        # Include optional fields if present
        if example.get("expected_output"):
            record["expected_output"] = example["expected_output"]
        if example.get("context"):
            record["context"] = example["context"]

        # Parse metadata if present
        if example.get("metadata"):
            try:
                metadata = json.loads(example["metadata"])
                record.update(metadata)
            except (json.JSONDecodeError, TypeError):
                pass  # Skip invalid metadata

        records.append(record)

    df = pd.DataFrame(records)
    print(f"  Loaded {len(df)} examples from dashboard dataset '{dataset_name}'")

    return df


def _get_simple_chat_prompt(description: str, context: str) -> str:
    """Generate system prompt for simple chat dataset generation."""
    return f"""You are a test data generator for a customer support chatbot.

Application description: {description}
{context}

Generate realistic customer support queries that users might ask this chatbot.
Include a mix of:
- Simple FAQ questions (password reset, billing inquiries)
- More complex requests requiring explanation
- Edge cases and unusual requests
- Polite and frustrated user tones

Each query should be a realistic user message, 1-3 sentences long."""


def _get_rag_prompt(description: str, context: str) -> str:
    """Generate system prompt for RAG dataset generation."""
    return f"""You are a test data generator for a RAG (Retrieval-Augmented Generation) application.

Application description: {description}
{context}

Generate realistic user queries that would require looking up information from a knowledge base.
Include a mix of:
- Factual questions requiring specific information
- Questions that need context from multiple documents
- Questions with specific entity references
- Questions that might have partial or no answers in the docs

Each query should be a realistic user question, 1-2 sentences long."""


def _get_agent_prompt(description: str, context: str) -> str:
    """Generate system prompt for agent dataset generation."""
    return f"""You are a test data generator for an AI agent with tool-use capabilities.

Application description: {description}
{context}

Generate realistic user requests that would require the agent to use tools or take actions.
Include a mix of:
- Simple tool invocations (check time, look up information)
- Multi-step tasks requiring planning
- Ambiguous requests requiring clarification
- Tasks that might not need tools at all

Each request should be a realistic user message, 1-3 sentences long."""


def _get_multi_agent_prompt(description: str, context: str) -> str:
    """Generate system prompt for multi-agent dataset generation."""
    return f"""You are a test data generator for a multi-agent AI system.

Application description: {description}
{context}

Generate realistic user requests that would benefit from multiple AI agents collaborating.
Include a mix of:
- Complex tasks requiring planning and execution
- Research and synthesis tasks
- Tasks with multiple steps or components
- Creative tasks requiring different perspectives

Each request should be a realistic user message, 1-3 sentences long."""


def build_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Build the evaluation dataset based on configuration.

    This is the main entry point for dataset creation. It dispatches
    to the appropriate loading method based on the config's dataset mode:
    - static: Load from JSONL/CSV file
    - synthetic: Generate using LLM
    - dashboard: Fetch from Quality Dashboard by name

    Args:
        config: Evaluation configuration

    Returns:
        DataFrame with evaluation dataset

    Example:
        >>> config = load_eval_config("llm_eval_simple_chat.yaml")
        >>> df = build_dataset(config)
        >>> print(df.columns)
        Index(['conversation_id', 'input'], dtype='object')

    Example YAML for dashboard mode:
        dataset:
          mode: "dashboard"
          dataset_name: "customer-support-failures-v2"
    """
    if config.dataset.mode == "static":
        return load_static_dataset(config)
    elif config.dataset.mode == "synthetic":
        return generate_synthetic_dataset(config)
    elif config.dataset.mode == "dashboard":
        return load_dashboard_dataset(config)
    else:
        raise ValueError(f"Unknown dataset mode: {config.dataset.mode}")
