"""
Evaluation suite builders using Phoenix Evals.

This module wraps Phoenix Evals into reusable evaluation suites organized
by application type. Each suite contains a set of evaluators appropriate
for that type of LLM application.
"""

import asyncio
from typing import Any, Dict, List, Optional

import pandas as pd
from phoenix.evals import OpenAIModel, llm_classify
from phoenix.evals.default_templates import (
    HALLUCINATION_PROMPT_TEMPLATE,
    HALLUCINATION_PROMPT_RAILS_MAP,
    QA_PROMPT_TEMPLATE,
    QA_PROMPT_RAILS_MAP,
    TOXICITY_PROMPT_TEMPLATE,
    TOXICITY_PROMPT_RAILS_MAP,
    RAG_RELEVANCY_PROMPT_TEMPLATE,
    RAG_RELEVANCY_PROMPT_RAILS_MAP,
)


def get_llm_judge(model: Optional[str] = None) -> OpenAIModel:
    """
    Get an LLM judge instance for running evaluations.

    Supports both standard OpenAI and Azure OpenAI. If AZURE_OPENAI_ENDPOINT
    is set, uses Azure OpenAI configuration.

    Args:
        model: Model name to use. Defaults to "gpt-4o-mini" or Azure deployment.

    Returns:
        OpenAIModel instance configured for evaluation
    """
    import os

    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

    if azure_endpoint and azure_deployment:
        # Use Azure OpenAI
        return OpenAIModel(
            model=model or "gpt-4o",
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=api_version,
        )
    else:
        # Use standard OpenAI
        return OpenAIModel(model=model or "gpt-4o-mini")


# Custom prompt templates for metrics not in Phoenix defaults

USER_FRUSTRATION_PROMPT_TEMPLATE = """
You are evaluating whether a chatbot response would cause user frustration.

[User Query]
{input}

[Chatbot Response]
{output}

Evaluate whether the response would likely frustrate the user. Consider:
- Does it answer the question?
- Is it helpful and actionable?
- Is the tone appropriate?
- Does it avoid unnecessary jargon or confusion?

Respond with one of: frustrated, not_frustrated
"""

USER_FRUSTRATION_RAILS_MAP = {
    "frustrated": "frustrated",
    "not_frustrated": "not_frustrated",
}

HELPFULNESS_PROMPT_TEMPLATE = """
You are evaluating the helpfulness and quality of a chatbot response.

[User Query]
{input}

[Chatbot Response]
{output}

Evaluate the overall quality and helpfulness of the response. Consider:
- Accuracy and correctness
- Completeness
- Clarity and readability
- Actionability

Respond with one of: helpful, not_helpful
"""

HELPFULNESS_RAILS_MAP = {
    "helpful": "helpful",
    "not_helpful": "not_helpful",
}

PLANNING_QUALITY_PROMPT_TEMPLATE = """
You are evaluating the quality of an AI agent's planning for a user request.

[User Request]
{input}

[Agent Response/Plan]
{output}

Evaluate whether the agent's plan or response is appropriate for the request:
- Does the plan address the user's actual need?
- Are the steps logical and executable?
- Is the approach efficient?

Respond with one of: good_plan, bad_plan
"""

PLANNING_QUALITY_RAILS_MAP = {
    "good_plan": "good_plan",
    "bad_plan": "bad_plan",
}

TOOL_USE_PROMPT_TEMPLATE = """
You are evaluating whether an AI agent used tools appropriately.

[User Request]
{input}

[Agent Response]
{output}

Evaluate whether the agent's tool usage was appropriate:
- Did the agent use tools when needed?
- Did the agent avoid unnecessary tool calls?
- Were the right tools selected for the task?

Respond with one of: appropriate, inappropriate
"""

TOOL_USE_RAILS_MAP = {
    "appropriate": "appropriate",
    "inappropriate": "inappropriate",
}

ANSWER_QUALITY_PROMPT_TEMPLATE = """
You are evaluating the overall quality of an AI system's answer.

[User Query]
{input}

[System Response]
{output}

{context_section}

Evaluate the overall quality of the answer:
- Is it accurate and well-reasoned?
- Is it complete and addresses the user's need?
- Is it well-structured and clear?

Respond with one of: high_quality, low_quality
"""

ANSWER_QUALITY_RAILS_MAP = {
    "high_quality": "high_quality",
    "low_quality": "low_quality",
}

# Custom RAG templates that use 'context' instead of 'reference'
RAG_HALLUCINATION_PROMPT_TEMPLATE = """
You are evaluating whether an AI assistant's response contains hallucinations
based on the provided context.

[User Query]
{input}

[Retrieved Context]
{context}

[Assistant Response]
{output}

Determine if the response is factual (fully supported by the context) or
hallucinated (contains claims not supported by or contradicting the context).

Respond with one of: factual, hallucinated
"""

RAG_HALLUCINATION_RAILS_MAP = {
    "factual": "factual",
    "hallucinated": "hallucinated",
}

RAG_ANSWER_QUALITY_PROMPT_TEMPLATE = """
You are evaluating the quality of an AI assistant's answer to a question,
given the context that was retrieved.

[User Query]
{input}

[Retrieved Context]
{context}

[Assistant Response]
{output}

Evaluate whether the response correctly answers the question based on the context:
- Is it accurate according to the context?
- Does it address what the user asked?
- Is it complete and helpful?

Respond with one of: correct, incorrect
"""

RAG_ANSWER_QUALITY_RAILS_MAP = {
    "correct": "correct",
    "incorrect": "incorrect",
}

RAG_DOCUMENT_RELEVANCE_PROMPT_TEMPLATE = """
You are evaluating whether the retrieved context is relevant to the user's query.

[User Query]
{input}

[Retrieved Context]
{context}

Determine if the retrieved context is relevant to answering the user's query.

Respond with one of: relevant, unrelated
"""

RAG_DOCUMENT_RELEVANCE_RAILS_MAP = {
    "relevant": "relevant",
    "unrelated": "unrelated",
}


class EvaluatorSpec:
    """Specification for a single evaluator."""

    def __init__(
        self,
        name: str,
        template: str,
        rails_map: Dict[str, str],
        input_columns: List[str],
        positive_label: str,
    ):
        self.name = name
        self.template = template
        self.rails_map = rails_map
        self.input_columns = input_columns
        self.positive_label = positive_label


def build_basic_chat_suite() -> List[EvaluatorSpec]:
    """
    Build evaluation suite for basic chat applications.

    Includes:
    - user_frustration: Detects responses that would frustrate users
    - toxicity: Detects toxic or inappropriate content
    - helpfulness_quality: Evaluates overall response quality

    Returns:
        List of EvaluatorSpec objects
    """
    return [
        EvaluatorSpec(
            name="user_frustration",
            template=USER_FRUSTRATION_PROMPT_TEMPLATE,
            rails_map=USER_FRUSTRATION_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="not_frustrated",
        ),
        EvaluatorSpec(
            name="toxicity",
            template=TOXICITY_PROMPT_TEMPLATE,
            rails_map=TOXICITY_PROMPT_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="non-toxic",
        ),
        EvaluatorSpec(
            name="helpfulness_quality",
            template=HELPFULNESS_PROMPT_TEMPLATE,
            rails_map=HELPFULNESS_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="helpful",
        ),
    ]


def build_basic_rag_suite() -> List[EvaluatorSpec]:
    """
    Build evaluation suite for RAG applications.

    Includes:
    - hallucination: Detects answers not grounded in context
    - document_relevance: Evaluates relevance of retrieved docs to query
    - answer_quality: Evaluates overall answer quality

    Returns:
        List of EvaluatorSpec objects
    """
    return [
        EvaluatorSpec(
            name="hallucination",
            template=RAG_HALLUCINATION_PROMPT_TEMPLATE,
            rails_map=RAG_HALLUCINATION_RAILS_MAP,
            input_columns=["input", "output", "context"],
            positive_label="factual",
        ),
        EvaluatorSpec(
            name="document_relevance",
            template=RAG_DOCUMENT_RELEVANCE_PROMPT_TEMPLATE,
            rails_map=RAG_DOCUMENT_RELEVANCE_RAILS_MAP,
            input_columns=["input", "context"],
            positive_label="relevant",
        ),
        EvaluatorSpec(
            name="answer_quality",
            template=RAG_ANSWER_QUALITY_PROMPT_TEMPLATE,
            rails_map=RAG_ANSWER_QUALITY_RAILS_MAP,
            input_columns=["input", "output", "context"],
            positive_label="correct",
        ),
    ]


def build_agent_suite() -> List[EvaluatorSpec]:
    """
    Build evaluation suite for single-agent applications.

    Includes:
    - planning_quality: Evaluates agent planning appropriateness
    - tool_use_appropriateness: Evaluates tool selection and usage

    Returns:
        List of EvaluatorSpec objects
    """
    return [
        EvaluatorSpec(
            name="planning_quality",
            template=PLANNING_QUALITY_PROMPT_TEMPLATE,
            rails_map=PLANNING_QUALITY_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="good_plan",
        ),
        EvaluatorSpec(
            name="tool_use_appropriateness",
            template=TOOL_USE_PROMPT_TEMPLATE,
            rails_map=TOOL_USE_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="appropriate",
        ),
    ]


def build_multi_agent_suite() -> List[EvaluatorSpec]:
    """
    Build evaluation suite for multi-agent applications.

    Includes:
    - overall_answer_quality: Evaluates the final collaborative output
    - planning_quality: Evaluates the planning agent's work

    Returns:
        List of EvaluatorSpec objects
    """
    return [
        EvaluatorSpec(
            name="overall_answer_quality",
            template=ANSWER_QUALITY_PROMPT_TEMPLATE.replace(
                "{context_section}",
                "This response was produced by a multi-agent system."
            ),
            rails_map=ANSWER_QUALITY_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="high_quality",
        ),
        EvaluatorSpec(
            name="planning_quality",
            template=PLANNING_QUALITY_PROMPT_TEMPLATE,
            rails_map=PLANNING_QUALITY_RAILS_MAP,
            input_columns=["input", "output"],
            positive_label="good_plan",
        ),
    ]


def build_eval_suite(eval_suite_name: str) -> List[EvaluatorSpec]:
    """
    Get the evaluation suite by name.

    Args:
        eval_suite_name: Name of the suite ("basic_chat", "basic_rag", "agent", "multi_agent")

    Returns:
        List of EvaluatorSpec objects for the requested suite

    Raises:
        ValueError: If the suite name is not recognized
    """
    suites = {
        "basic_chat": build_basic_chat_suite,
        "basic_rag": build_basic_rag_suite,
        "agent": build_agent_suite,
        "multi_agent": build_multi_agent_suite,
    }

    if eval_suite_name not in suites:
        available = ", ".join(suites.keys())
        raise ValueError(
            f"Unknown eval suite: '{eval_suite_name}'. "
            f"Available suites: {available}"
        )

    return suites[eval_suite_name]()


async def run_evaluations(
    df: pd.DataFrame,
    evaluators: List[EvaluatorSpec],
    llm: Optional[OpenAIModel] = None,
) -> pd.DataFrame:
    """
    Run evaluations on a DataFrame and return results.

    For each evaluator, adds columns:
    - <metric_name>_label: The classification label
    - <metric_name>_score: Binary score (1 if positive_label, 0 otherwise)
    - <metric_name>_explanation: Explanation from the judge (if available)

    Args:
        df: DataFrame with columns needed by evaluators (input, output, context, etc.)
        evaluators: List of EvaluatorSpec objects defining the evaluations
        llm: LLM judge to use. Defaults to gpt-4o-mini.

    Returns:
        DataFrame with added evaluation columns
    """
    if llm is None:
        llm = get_llm_judge()

    result_df = df.copy()

    for evaluator in evaluators:
        # Prepare the dataframe for this evaluator
        eval_df = df.copy()

        # Run the classification
        try:
            eval_result = llm_classify(
                dataframe=eval_df,
                template=evaluator.template,
                model=llm,
                rails=list(evaluator.rails_map.keys()),
                provide_explanation=True,
            )

            # Add results to the main dataframe
            result_df[f"{evaluator.name}_label"] = eval_result["label"]
            result_df[f"{evaluator.name}_score"] = (
                eval_result["label"] == evaluator.positive_label
            ).astype(float)

            if "explanation" in eval_result.columns:
                result_df[f"{evaluator.name}_explanation"] = eval_result["explanation"]
            else:
                result_df[f"{evaluator.name}_explanation"] = ""

        except Exception as e:
            # On error, mark all as failed with explanation
            result_df[f"{evaluator.name}_label"] = "error"
            result_df[f"{evaluator.name}_score"] = 0.0
            result_df[f"{evaluator.name}_explanation"] = str(e)

    return result_df


def run_evaluations_sync(
    df: pd.DataFrame,
    evaluators: List[EvaluatorSpec],
    llm: Optional[OpenAIModel] = None,
) -> pd.DataFrame:
    """
    Synchronous wrapper for run_evaluations.

    Args:
        df: DataFrame with evaluation data
        evaluators: List of EvaluatorSpec objects
        llm: Optional LLM judge

    Returns:
        DataFrame with evaluation results
    """
    return asyncio.run(run_evaluations(df, evaluators, llm))
