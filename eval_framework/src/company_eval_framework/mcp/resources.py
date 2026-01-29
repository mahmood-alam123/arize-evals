"""MCP resource implementations for the evaluation framework."""

import json
from pathlib import Path
from typing import Dict, Any

import yaml


async def get_config_resource(path: str) -> str:
    """Read and return the contents of a configuration file.
    
    Provides access to config files through the MCP resource protocol.
    Returns the raw YAML contents as a string.
    
    Args:
        path: Relative or absolute path to the config file
        
    Returns:
        str: YAML contents of the configuration file
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
    """
    config_path = Path(path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    try:
        with open(config_path, 'r') as f:
            return f.read()
    except Exception as e:
        raise IOError(f"Failed to read config file: {str(e)}")


async def get_dataset_resource(path: str) -> str:
    """Read and return a sample of a dataset file.
    
    Provides access to dataset files through the MCP resource protocol.
    Returns the first 10 rows to give a preview without loading the entire file.
    
    Args:
        path: Relative or absolute path to the dataset file
        
    Returns:
        str: JSON-formatted preview containing the first 10 rows
        
    Raises:
        FileNotFoundError: If the dataset file doesn't exist
    """
    dataset_path = Path(path)
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    
    rows = []
    try:
        with open(dataset_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                try:
                    rows.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        
        return json.dumps({
            "path": str(path),
            "preview_rows": rows,
            "total_preview_count": len(rows),
            "note": "Showing first 10 rows only"
        }, indent=2)
        
    except Exception as e:
        raise IOError(f"Failed to read dataset file: {str(e)}")


async def get_latest_results_resource() -> str:
    """Get the results from the most recent evaluation run.
    
    Provides access to cached evaluation results through the MCP resource protocol.
    
    Returns:
        str: JSON-formatted evaluation results from the last run
        
    Raises:
        ValueError: If no evaluation has been run yet
    """
    # Import here to avoid circular dependency
    from .tools import _last_evaluation_result
    
    if _last_evaluation_result is None:
        raise ValueError(
            "No evaluation results available. Run an evaluation first using the run_evaluation tool."
        )
    
    return json.dumps(_last_evaluation_result, indent=2)
