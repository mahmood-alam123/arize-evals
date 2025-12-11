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
      - "response" (LLM answer)
    """
    rows_out = []
    for row in _read_jsonl(input_path):
        query = row.get("input") or row.get("query") or ""
        context = row.get("context")
        result = evaluate_simple_llm_response(query=query, context=context)
        row_out = dict(row)
        row_out.update(result)
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
        context = row.get("context")
        result = evaluate_agent_response(query=query, context=context)
        row_out = dict(row)
        row_out.update(result)
        rows_out.append(row_out)

    _write_jsonl(output_path, rows_out)


# Global agent instance (singleton)
_agent = None
_agent_config = {"agent_type": "mock"}


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
