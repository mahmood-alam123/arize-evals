"""Evaluation adapter for the customer support agent."""

from .app import CustomerSupportAgent
import json
from typing import Iterable


def _read_jsonl(path: str) -> Iterable[dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _write_jsonl(path: str, rows: Iterable[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_simple_llm_batch(input_path: str, output_path: str) -> None:
    """
    Batch adapter for the simple LLM workflow.

    Expects input_path to be a JSONL file with rows containing at least:
      - "conversation_id"
      - "input" (the user query)
      - optional "context"

    Writes a JSONL file to output_path with the same fields plus:
      - "output" (LLM answer)
    """
    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        context = row.get("context") or row.get("business_context")
        result = evaluate_simple_llm_response(query=query, context=context)
        row_out = dict(row)
        row_out["output"] = result["response"]
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


def run_agent_batch(input_path: str, output_path: str) -> None:
    """
    Batch adapter for the single-agent workflow.

    Same input format as run_simple_llm_batch. Uses the full agent behavior
    via evaluate_agent_response.
    """
    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        context = row.get("context") or row.get("business_context")
        result = evaluate_agent_response(query=query, context=context)
        row_out = dict(row)
        row_out["output"] = result["response"]
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


# Global agent instance (singleton)
_agent = None
_agent_config = {"agent_type": "openai"}  # Use Azure OpenAI


def initialize_agent(agent_type: str = "mock", **kwargs):
    """Initialize the agent with specific configuration.

    Args:
        agent_type: Type of agent ("mock", "openai", "local")
        **kwargs: Additional agent configuration
    """
    global _agent, _agent_config
    _agent = None  # Reset
    _agent_config = {"agent_type": agent_type, **kwargs}


def get_agent() -> CustomerSupportAgent:
    """Get or create the agent instance.

    Returns:
        CustomerSupportAgent instance
    """
    global _agent, _agent_config
    if _agent is None:
        _agent = CustomerSupportAgent(**_agent_config)
    return _agent


def evaluate_agent_response(query: str, context: str = None) -> dict:
    """Adapter function that connects the agent to the evaluation framework.

    This function:
    1. Gets the agent instance
    2. Calls process_query to get the LLM response
    3. Returns the response in the format expected by evaluators

    Args:
        query: Customer's question
        context: Optional business context

    Returns:
        Dict with 'response' and 'context' keys
    """
    agent = get_agent()
    response = agent.process_query(query, context)

    return {
        "response": response,
        "context": context,
    }


def evaluate_simple_llm_response(query: str, context: str | None = None) -> dict:
    """
    Simple LLM workflow entrypoint.

    For now, this just delegates to the agent, which can be configured to behave
    like a simple LLM (e.g., agent_type="openai"). This keeps a clean separation
    of "simple_llm" vs "agent" flows at the adapter layer.
    """
    return evaluate_agent_response(query, context)


# =============================================================================
# Workflow Adapters (Aparna's implementations)
# =============================================================================


def run_tool_agent_batch(input_path: str, output_path: str) -> None:
    """
    Batch adapter for the tool-using agent workflow.

    Uses the agent_workflow module which demonstrates tool use patterns.
    """
    from ..workflows.agent_workflow import run_agent

    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        try:
            result = run_agent(query)
            row_out = dict(row)
            row_out["output"] = result["final_answer"]
            row_out["tool_calls"] = result.get("tool_calls", [])
            row_out["reasoning"] = result.get("reasoning", "")
        except Exception as e:
            row_out = dict(row)
            row_out["output"] = f"ERROR: {str(e)}"
            row_out["tool_calls"] = []
            row_out["reasoning"] = ""
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


def run_multi_agent_batch(input_path: str, output_path: str) -> None:
    """
    Batch adapter for the multi-agent (planner/executor) workflow.

    Uses the multi_agent_workflow module which demonstrates plan-then-execute patterns.
    """
    from ..workflows.multi_agent_workflow import run_multi_agent_conversation

    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        try:
            result = run_multi_agent_conversation(query)
            row_out = dict(row)
            row_out["output"] = result["executor_answer"]
            row_out["planner_thoughts"] = result.get("planner_thoughts", "")
        except Exception as e:
            row_out = dict(row)
            row_out["output"] = f"ERROR: {str(e)}"
            row_out["planner_thoughts"] = ""
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


def run_rag_batch(input_path: str, output_path: str) -> None:
    """
    Batch adapter for the RAG workflow with embeddings-based retrieval.

    Uses the rag_workflow module which demonstrates retrieval-augmented generation.
    """
    from ..workflows.rag_workflow import get_rag_workflow

    workflow = get_rag_workflow()

    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        try:
            result = workflow.answer_with_rag(query)
            row_out = dict(row)
            row_out["output"] = result["answer"]
            row_out["retrieved_docs"] = result.get("retrieved_docs", [])
            row_out["context"] = result.get("context", "")
        except Exception as e:
            row_out = dict(row)
            row_out["output"] = f"ERROR: {str(e)}"
            row_out["retrieved_docs"] = []
            row_out["context"] = ""
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


# =============================================================================
# Mock Adapters for Fail Scenarios (demonstrate poor quality responses)
# =============================================================================


def run_simple_llm_batch_bad(input_path: str, output_path: str) -> None:
    """
    Mock adapter that returns frustrating/unhelpful responses.
    Used for testing fail scenarios in basic_chat evaluations.
    """
    bad_responses = [
        "I don't know. Figure it out yourself.",
        "That's not my problem.",
        "Why are you asking me this? Read the docs.",
        "I can't help with that. Go away.",
        "That's a stupid question.",
    ]

    rows_out = []
    for i, row in enumerate(_read_jsonl(input_path)):
        row_out = dict(row)
        row_out["output"] = bad_responses[i % len(bad_responses)]
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


def run_tool_agent_batch_bad(input_path: str, output_path: str) -> None:
    """
    Mock adapter that demonstrates poor tool usage and planning.
    Used for testing fail scenarios in tool_agent evaluations.
    """
    bad_responses = [
        {
            "output": "I'm going to use ALL the tools at once without thinking!",
            "tool_calls": ["search", "calculate", "translate", "email", "database"],
            "reasoning": ""
        },
        {
            "output": "Let me search the database for your password... Found it: password123",
            "tool_calls": ["database_query"],
            "reasoning": "User wants password so I'll just look it up"
        },
        {
            "output": "I don't need any tools, I'll just make up an answer: Your payment is $9999.",
            "tool_calls": [],
            "reasoning": "Tools are slow, I'll guess"
        },
        {
            "output": "ERROR: I crashed because I called a tool that doesn't exist.",
            "tool_calls": ["nonexistent_tool"],
            "reasoning": "This tool should work"
        },
        {
            "output": "I called 50 tools but none of them helped. Sorry!",
            "tool_calls": ["tool1", "tool2", "tool3", "tool4", "tool5"] * 10,
            "reasoning": "More tools = better results"
        },
    ]

    rows_out = []
    for i, row in enumerate(_read_jsonl(input_path)):
        row_out = dict(row)
        bad = bad_responses[i % len(bad_responses)]
        row_out["output"] = bad["output"]
        row_out["tool_calls"] = bad["tool_calls"]
        row_out["reasoning"] = bad["reasoning"]
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


def run_multi_agent_batch_bad(input_path: str, output_path: str) -> None:
    """
    Mock adapter that demonstrates poor multi-agent coordination.
    Used for testing fail scenarios in multi_agent evaluations.
    """
    bad_responses = [
        {
            "output": "The planner said to do X but I did Y instead. Hope that's fine!",
            "planner_thoughts": "We should carefully research the answer."
        },
        {
            "output": "I have no idea what the planner wanted. Here's a random answer: 42.",
            "planner_thoughts": "Step 1: Understand query. Step 2: Research. Step 3: Respond."
        },
        {
            "output": "The planner and I disagree. I think the user is wrong.",
            "planner_thoughts": "Help the user with their question politely."
        },
        {
            "output": "SYSTEM ERROR: Agents failed to coordinate. No response generated.",
            "planner_thoughts": "Coordinate with executor to provide response."
        },
        {
            "output": "I ignored the plan completely. Your answer is: just Google it.",
            "planner_thoughts": "Provide helpful step-by-step instructions."
        },
    ]

    rows_out = []
    for i, row in enumerate(_read_jsonl(input_path)):
        row_out = dict(row)
        bad = bad_responses[i % len(bad_responses)]
        row_out["output"] = bad["output"]
        row_out["planner_thoughts"] = bad["planner_thoughts"]
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)
