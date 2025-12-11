"""Dataset loading and generation."""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

from .config import EvalConfig


def load_static_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Load static dataset from JSONL file.
    
    Args:
        config: EvalConfig with dataset path
        
    Returns:
        DataFrame with examples
    """
    dataset_path = config.dataset.path
    
    if not dataset_path:
        raise ValueError("dataset.path is required for static mode")
    
    if not Path(dataset_path).exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    # Read JSONL file
    data = []
    with open(dataset_path, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    return pd.DataFrame(data)


def generate_synthetic_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Generate synthetic dataset (placeholder).
    
    Args:
        config: EvalConfig with size parameter
        
    Returns:
        DataFrame with synthetic examples
    """
    size = config.dataset.size
    
    # Simple synthetic data
    data = []
    for i in range(size):
        data.append({
            "conversation_id": f"synth_{i}",
            "input": f"Sample question {i}",
            "context": "synthetic"
        })
    
    return pd.DataFrame(data)


def build_dataset(config: EvalConfig) -> pd.DataFrame:
    """
    Build dataset based on config mode.
    
    Args:
        config: EvalConfig
        
    Returns:
        DataFrame with examples
    """
    if config.dataset.mode == "static":
        return load_static_dataset(config)
    elif config.dataset.mode == "synthetic":
        return generate_synthetic_dataset(config)
    else:
        raise ValueError(f"Unknown dataset mode: {config.dataset.mode}")
