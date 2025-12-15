"""Load and parse agent configuration."""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str = "agent_config.yaml") -> Dict[str, Any]:
    """Load agent configuration from YAML file.

    Args:
        config_path: Path to config file (default: agent_config.yaml)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config


def get_agent_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and validate agent configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Agent-specific configuration

    Raises:
        ValueError: If configuration is invalid
    """
    agent_type = config.get("agent_type", "mock")

    if agent_type not in ["mock", "openai", "local"]:
        raise ValueError(
            f"Invalid agent_type: {agent_type}. Must be: mock, openai, local"
        )

    # Build kwargs for agent creation
    agent_kwargs = {"agent_type": agent_type}

    if agent_type == "openai":
        openai_config = config.get("openai", {})
        agent_kwargs.update(
            {
                "model": openai_config.get("model", "gpt-3.5-turbo"),
                "temperature": openai_config.get("temperature", 0.7),
                "max_tokens": openai_config.get("max_tokens", 200),
            }
        )

        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. Required for agent_type: openai"
            )

    elif agent_type == "local":
        local_config = config.get("local", {})
        model_path = local_config.get("model_path", "./models/mistral-7b.gguf")

        if not Path(model_path).exists():
            raise ValueError(f"Local model not found: {model_path}")

        agent_kwargs.update(
            {
                "model_path": model_path,
                "n_ctx": local_config.get("n_ctx", 512),
                "n_threads": local_config.get("n_threads", 4),
            }
        )

    return agent_kwargs


def get_eval_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract evaluation configuration.

    Args:
        config: Full configuration dictionary

    Returns:
        Evaluation-specific configuration
    """
    eval_config = config.get("evaluation", {})
    return {
        "dataset_path": eval_config.get("dataset_path", "eval_dataset.json"),
        "results_dir": eval_config.get("results_dir", "eval_results"),
        "metrics": eval_config.get(
            "metrics", ["coherence", "relevance", "safety", "completeness", "tone"]
        ),
    }
