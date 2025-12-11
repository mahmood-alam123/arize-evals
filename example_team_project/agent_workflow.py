"""
Single-agent workflow with tool use capabilities.

This module implements a simple tool-using agent that can:
1. Analyze user requests
2. Decide which tools to use (if any)
3. Execute tool calls
4. Generate final answers based on tool results
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from openai import OpenAI


# Define available tools
TOOLS = {
    "get_current_time": {
        "description": "Get the current date and time",
        "parameters": {}
    },
    "lookup_plan": {
        "description": "Look up details about a subscription plan",
        "parameters": {
            "plan_name": "Name of the plan (starter, professional, or enterprise)"
        }
    },
    "calculate": {
        "description": "Perform a mathematical calculation",
        "parameters": {
            "expression": "Mathematical expression to evaluate (e.g., '42 * 1.5')"
        }
    },
    "search_docs": {
        "description": "Search documentation for information",
        "parameters": {
            "query": "Search query string"
        }
    }
}


# Tool implementations
def get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


def lookup_plan(plan_name: str) -> str:
    """Look up subscription plan details."""
    plans = {
        "starter": {
            "price": "$29/month",
            "api_calls": "10,000/month",
            "rate_limit": "100 requests/minute",
            "features": ["Unlimited users", "99.9% uptime SLA", "Email support"]
        },
        "professional": {
            "price": "$99/month",
            "api_calls": "100,000/month",
            "rate_limit": "500 requests/minute",
            "features": ["Everything in Starter", "Priority support", "Advanced analytics"]
        },
        "enterprise": {
            "price": "Custom pricing",
            "api_calls": "Unlimited",
            "rate_limit": "2000 requests/minute",
            "features": ["Everything in Professional", "Dedicated account manager", "SLA guarantees", "SSO"]
        }
    }
    
    plan_name_lower = plan_name.lower()
    if plan_name_lower not in plans:
        return f"Plan '{plan_name}' not found. Available plans: starter, professional, enterprise"
    
    plan = plans[plan_name_lower]
    return f"{plan_name.title()} Plan: {plan['price']}, {plan['api_calls']} API calls, {plan['rate_limit']} rate limit. Features: {', '.join(plan['features'])}"


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Only allow basic math operations for safety
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


def search_docs(query: str) -> str:
    """Search documentation (simplified mock implementation)."""
    docs_db = {
        "api": "API documentation: Authentication uses Bearer tokens. Rate limits vary by plan.",
        "billing": "Billing: We accept credit cards and annual invoicing for Enterprise. Changes take effect immediately.",
        "security": "Security: SOC 2 Type II certified, GDPR compliant, AES-256 encryption at rest, TLS 1.3 in transit.",
        "export": "Data Export: Export data in JSON or CSV format anytime from Settings > Data Management.",
        "webhook": "Webhooks: Configure at Settings > Webhooks. HTTPS required, 5-second timeout, 3 retries."
    }
    
    query_lower = query.lower()
    results = []
    
    for key, content in docs_db.items():
        if key in query_lower or any(word in content.lower() for word in query_lower.split()):
            results.append(content)
    
    if not results:
        return "No documentation found for that query."
    
    return " ".join(results)


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Execute a tool with given parameters."""
    if tool_name == "get_current_time":
        return get_current_time()
    elif tool_name == "lookup_plan":
        return lookup_plan(parameters.get("plan_name", ""))
    elif tool_name == "calculate":
        return calculate(parameters.get("expression", ""))
    elif tool_name == "search_docs":
        return search_docs(parameters.get("query", ""))
    else:
        return f"Unknown tool: {tool_name}"


def run_agent(user_input: str, model: str = "gpt-4o-mini", max_iterations: int = 3) -> Dict[str, Any]:
    """
    Run the agent workflow with tool use.
    
    Args:
        user_input: User's request or question
        model: OpenAI model to use
        max_iterations: Maximum number of agent iterations
        
    Returns:
        Dict with keys:
        - "final_answer": The agent's final response
        - "tool_calls": List of tools that were called
        - "reasoning": Agent's reasoning process
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Build tool descriptions for the prompt
    tools_description = "\n".join([
        f"- {name}: {info['description']}"
        for name, info in TOOLS.items()
    ])
    
    system_prompt = f"""You are a helpful AI assistant with access to tools.

Available tools:
{tools_description}

To use a tool, respond with a JSON object in this format:
{{"tool": "tool_name", "parameters": {{"param": "value"}}}}

After receiving tool results, provide a final answer to the user.
If you don't need any tools, just answer directly.

Be concise and helpful."""
    
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    tool_calls = []
    reasoning_steps = []
    
    for iteration in range(max_iterations):
        # Get agent's response
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            temperature=0.7,
            max_tokens=400
        )
        
        agent_message = response.choices[0].message.content.strip()
        reasoning_steps.append(f"Iteration {iteration + 1}: {agent_message[:100]}...")
        
        # Check if agent wants to use a tool
        if agent_message.startswith("{") and "tool" in agent_message.lower():
            try:
                # Parse tool call
                tool_call = json.loads(agent_message)
                tool_name = tool_call.get("tool")
                parameters = tool_call.get("parameters", {})
                
                # Execute tool
                tool_result = execute_tool(tool_name, parameters)
                tool_calls.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": tool_result
                })
                
                # Add tool result to conversation
                conversation_history.append({"role": "assistant", "content": agent_message})
                conversation_history.append({
                    "role": "user",
                    "content": f"Tool result: {tool_result}\n\nNow provide your final answer to the user."
                })
                
            except json.JSONDecodeError:
                # Not valid JSON, treat as final answer
                return {
                    "final_answer": agent_message,
                    "tool_calls": tool_calls,
                    "reasoning": " → ".join(reasoning_steps)
                }
        else:
            # This is the final answer
            return {
                "final_answer": agent_message,
                "tool_calls": tool_calls,
                "reasoning": " → ".join(reasoning_steps)
            }
    
    # Max iterations reached
    return {
        "final_answer": "I apologize, but I wasn't able to complete your request within the iteration limit.",
        "tool_calls": tool_calls,
        "reasoning": " → ".join(reasoning_steps)
    }


def run_agent_batch(inputs: List[str], model: str = "gpt-4o-mini") -> List[Dict]:
    """
    Process multiple inputs through the agent workflow.
    
    Args:
        inputs: List of user input strings
        model: OpenAI model to use
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    for user_input in inputs:
        try:
            result = run_agent(user_input, model)
            results.append(result)
        except Exception as e:
            results.append({
                "final_answer": f"ERROR: {str(e)}",
                "tool_calls": [],
                "reasoning": ""
            })
    
    return results


# Example usage
if __name__ == "__main__":
    # Test queries
    test_queries = [
        "What time is it right now?",
        "What's included in the Professional plan?",
        "How much would it cost for 5 months of the Starter plan?",
        "Tell me about your API security"
    ]
    
    print("=" * 70)
    print("AGENT WORKFLOW - TOOL USE TEST")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print('='*70)
        
        result = run_agent(query)
        
        if result['tool_calls']:
            print("\n🔧 Tools Used:")
            for tc in result['tool_calls']:
                print(f"  • {tc['tool']}({tc['parameters']}) → {tc['result'][:60]}...")
        
        print(f"\n💬 Final Answer:\n{result['final_answer']}")
