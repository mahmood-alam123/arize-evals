"""
Multi-agent workflow implementation with planner and executor agents.

This module demonstrates a basic multi-agent pattern where:
1. A planner agent decomposes user requests into actionable steps
2. An executor agent follows the plan to generate the final answer
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI, AzureOpenAI


def run_multi_agent_conversation(user_input: str, model: str = None) -> Dict[str, str]:
    """
    Execute a multi-agent workflow with planner and executor.

    Supports both standard OpenAI and Azure OpenAI. If AZURE_OPENAI_ENDPOINT
    is set, uses Azure OpenAI configuration.

    Args:
        user_input: The user's request or question
        model: Model/deployment name to use for both agents

    Returns:
        Dict with keys:
        - "planner_thoughts": The plan created by the planner agent
        - "executor_answer": The final answer from the executor agent
        - "full_output": Combined output for easy display
    """
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

    if azure_endpoint:
        client = AzureOpenAI(
            api_key=azure_api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        model = model or os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-deployment")
    else:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        model = model or "gpt-4o-mini"

    # Step 1: Planner Agent
    planner_system_prompt = """You are a planning agent that decomposes tasks into clear, actionable steps.

Given a user request, create a concise plan with 2-4 numbered steps that would help solve the problem.
Focus on logical decomposition and clarity. Keep each step concrete and actionable.

Format your response as:
PLAN:
1. [First step]
2. [Second step]
...
"""

    planner_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": planner_system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=300
    )

    planner_thoughts = planner_response.choices[0].message.content.strip()

    # Step 2: Executor Agent
    executor_system_prompt = """You are an execution agent that follows plans to answer user questions.

You will receive:
1. The original user request
2. A plan from the planning agent

Your job is to follow the plan step-by-step and provide a comprehensive answer to the user's request.
Be thorough but concise. Reference the plan steps as you execute them if helpful.
"""

    executor_user_message = f"""ORIGINAL REQUEST:
{user_input}

PLAN TO FOLLOW:
{planner_thoughts}

Please execute this plan and provide a complete answer to the user's request."""

    executor_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": executor_system_prompt},
            {"role": "user", "content": executor_user_message}
        ],
        temperature=0.7,
        max_tokens=500
    )

    executor_answer = executor_response.choices[0].message.content.strip()

    # Combine for full output
    full_output = f"""=== PLANNER ===
{planner_thoughts}

=== EXECUTOR ===
{executor_answer}"""

    return {
        "planner_thoughts": planner_thoughts,
        "executor_answer": executor_answer,
        "full_output": full_output
    }


def run_multi_agent_batch(inputs: List[str], model: str = "gpt-4o-mini") -> List[Dict[str, str]]:
    """
    Process multiple inputs through the multi-agent workflow.

    Args:
        inputs: List of user input strings
        model: OpenAI model to use

    Returns:
        List of result dictionaries, one per input
    """
    results = []

    for user_input in inputs:
        try:
            result = run_multi_agent_conversation(user_input, model)
            results.append(result)
        except Exception as e:
            # Return error info but continue processing
            results.append({
                "planner_thoughts": f"ERROR: {str(e)}",
                "executor_answer": f"ERROR: {str(e)}",
                "full_output": f"ERROR: {str(e)}"
            })

    return results


# Example usage
if __name__ == "__main__":
    # Test with a sample query
    test_input = "I need to plan a team offsite for 15 people in Q2. What should I consider?"

    result = run_multi_agent_conversation(test_input)

    print("=" * 60)
    print("MULTI-AGENT WORKFLOW TEST")
    print("=" * 60)
    print(f"\nUSER INPUT:\n{test_input}\n")
    print(result["full_output"])
