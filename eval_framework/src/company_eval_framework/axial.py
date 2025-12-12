"""
Axial coding module for failure analysis.

This module provides "axial coding" functionality - classifying failures
into meaningful categories to help teams understand what went wrong.
Uses an LLM classifier to categorize failing responses.
"""

import asyncio
from typing import Optional

import pandas as pd
from phoenix.evals import OpenAIModel, llm_classify

from .evaluators import get_llm_judge


# Failure type classification prompt
FAILURE_TYPE_PROMPT_TEMPLATE = """
You are analyzing why an LLM application's response failed quality checks.

[User Input]
{input}

[Application Response]
{output}

[Context (if available)]
{context}

[Failure Information]
This response was flagged as a failure in automated evaluation.

Classify the primary failure type into exactly one of these categories:
- retrieval_error: The system failed to retrieve relevant information
- hallucination: The response contains information not supported by context/facts
- formatting: The response has format/structure issues but content is okay
- refusal: The system refused to answer when it should have answered
- irrelevant: The response doesn't address the user's actual question
- other: Doesn't fit the above categories

Respond with exactly one of: retrieval_error, hallucination, formatting, refusal, irrelevant, other
"""

FAILURE_TYPE_RAILS_MAP = {
    "retrieval_error": "retrieval_error",
    "hallucination": "hallucination",
    "formatting": "formatting",
    "refusal": "refusal",
    "irrelevant": "irrelevant",
    "other": "other",
}


def build_failure_type_classifier() -> dict:
    """
    Build the failure type classifier configuration.

    Returns a dict with the template and rails for use with llm_classify.

    Returns:
        Dict with 'template' and 'rails' keys
    """
    return {
        "template": FAILURE_TYPE_PROMPT_TEMPLATE,
        "rails": list(FAILURE_TYPE_RAILS_MAP.keys()),
    }


async def run_axial_coding(
    failures_df: pd.DataFrame,
    llm: Optional[OpenAIModel] = None,
) -> pd.DataFrame:
    """
    Run axial coding (failure type classification) on failing rows.

    Given a DataFrame of 'failing' rows (e.g., those where a metric like
    hallucination_score > threshold), this function runs an LLM classifier
    to categorize each failure into a meaningful type.

    Args:
        failures_df: DataFrame containing failing rows with columns:
            - input: User query
            - output: Model response
            - context: (optional) Retrieved context for RAG
        llm: LLM judge to use. Defaults to gpt-4o-mini.

    Returns:
        DataFrame with added 'failure_type' column containing one of:
        - retrieval_error
        - hallucination
        - formatting
        - refusal
        - irrelevant
        - other

    Example:
        >>> failures = eval_results[eval_results['hallucination_score'] > 0.5]
        >>> coded = await run_axial_coding(failures)
        >>> print(coded['failure_type'].value_counts())
    """
    if llm is None:
        llm = get_llm_judge()

    if failures_df.empty:
        # Return empty dataframe with the expected column
        result = failures_df.copy()
        result["failure_type"] = pd.Series(dtype=str)
        result["failure_type_explanation"] = pd.Series(dtype=str)
        return result

    # Ensure context column exists (may be empty for non-RAG apps)
    df = failures_df.copy()
    if "context" not in df.columns:
        df["context"] = "N/A"

    # Fill NaN contexts
    df["context"] = df["context"].fillna("N/A")

    # Run classification
    try:
        classifier_config = build_failure_type_classifier()
        result = llm_classify(
            dataframe=df,
            template=classifier_config["template"],
            model=llm,
            rails=classifier_config["rails"],
            provide_explanation=True,
        )

        df["failure_type"] = result["label"]
        if "explanation" in result.columns:
            df["failure_type_explanation"] = result["explanation"]
        else:
            df["failure_type_explanation"] = ""

    except Exception as e:
        # On error, mark as "other" with error explanation
        df["failure_type"] = "other"
        df["failure_type_explanation"] = f"Classification error: {e}"

    return df


def run_axial_coding_sync(
    failures_df: pd.DataFrame,
    llm: Optional[OpenAIModel] = None,
) -> pd.DataFrame:
    """
    Synchronous wrapper for run_axial_coding.

    Args:
        failures_df: DataFrame with failing rows
        llm: Optional LLM judge

    Returns:
        DataFrame with failure_type column added
    """
    return asyncio.run(run_axial_coding(failures_df, llm))


def summarize_failure_types(coded_df: pd.DataFrame) -> dict:
    """
    Summarize failure type distribution from axial coding results.

    Args:
        coded_df: DataFrame with 'failure_type' column from run_axial_coding

    Returns:
        Dict with:
        - counts: Dict mapping failure_type to count
        - percentages: Dict mapping failure_type to percentage
        - total: Total number of failures
        - top_types: List of (type, count) tuples sorted by frequency
    """
    if coded_df.empty or "failure_type" not in coded_df.columns:
        return {
            "counts": {},
            "percentages": {},
            "total": 0,
            "top_types": [],
        }

    counts = coded_df["failure_type"].value_counts().to_dict()
    total = len(coded_df)
    percentages = {k: (v / total * 100) for k, v in counts.items()}

    top_types = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "counts": counts,
        "percentages": percentages,
        "total": total,
        "top_types": top_types,
    }


def get_failure_examples(
    coded_df: pd.DataFrame,
    failure_type: str,
    n: int = 3,
) -> pd.DataFrame:
    """
    Get example failures of a specific type.

    Args:
        coded_df: DataFrame with failure_type column
        failure_type: The failure type to filter for
        n: Maximum number of examples to return

    Returns:
        DataFrame with up to n examples of the specified failure type
    """
    if coded_df.empty or "failure_type" not in coded_df.columns:
        return pd.DataFrame()

    matching = coded_df[coded_df["failure_type"] == failure_type]
    return matching.head(n)
