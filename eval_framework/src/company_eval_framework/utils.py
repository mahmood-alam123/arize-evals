"""Utility functions."""

import json
from pathlib import Path
from typing import List, Dict, Any


def read_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Read JSONL file and return list of dicts."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def write_jsonl(file_path: str, data: List[Dict[str, Any]]) -> None:
    """Write list of dicts to JSONL file."""
    with open(file_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')


def ensure_dir(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)
