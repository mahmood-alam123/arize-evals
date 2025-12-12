"""
Utility functions for the evaluation framework.

Provides common helpers for JSONL I/O, logging, and other shared functionality.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging for the evaluation framework.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(level=level, format=format_string)
    return logging.getLogger("company_eval_framework")


def read_jsonl(path: str) -> pd.DataFrame:
    """
    Read a JSONL file into a pandas DataFrame.

    Args:
        path: Path to the JSONL file

    Returns:
        DataFrame with one row per JSON object

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If a line contains invalid JSON
    """
    records: List[Dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Invalid JSON on line {line_num}: {e.msg}",
                    e.doc,
                    e.pos,
                )

    return pd.DataFrame(records)


def write_jsonl(df: pd.DataFrame, path: str) -> None:
    """
    Write a pandas DataFrame to a JSONL file.

    Args:
        df: DataFrame to write
        path: Output file path

    Note:
        Creates parent directories if they don't exist.
    """
    # Ensure parent directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")


def read_json(path: str) -> Dict[str, Any]:
    """
    Read a JSON file.

    Args:
        path: Path to the JSON file

    Returns:
        Parsed JSON object (usually a dict)
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data: Any, path: str, indent: int = 2) -> None:
    """
    Write data to a JSON file.

    Args:
        data: Data to write (must be JSON-serializable)
        path: Output file path
        indent: Indentation level for pretty printing
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, ensure_ascii=False, indent=indent, fp=f)


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        Truncated string with suffix if needed
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dict.

    Args:
        d: Dictionary to get from
        key: Key to look up
        default: Default value if key not found

    Returns:
        Value at key or default
    """
    return d.get(key, default)
