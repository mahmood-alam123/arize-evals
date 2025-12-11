"""LLM-based customer support agent."""

from typing import Optional
from .agent_factory import create_agent


class CustomerSupportAgent:
    """A single-agent LLM workflow for customer support.
    
    This is the main application that:
    1. Takes customer queries
    2. Passes them to an LLM (configurable backend)
    3. Returns responses
    
    Single-agent design: One agent handles all customer queries
    """
    
    def __init__(self, agent_type: str = "mock", **agent_kwargs):
        """Initialize the customer support agent.
        
        Args:
            agent_type: Type of backend ("mock", "openai", "local")
            **agent_kwargs: Additional arguments for the agent (model, api_key, etc.)
        """
        self.agent = create_agent(agent_type, **agent_kwargs)
        self.agent_type = agent_type
    
    def process_query(self, customer_query: str, context: Optional[str] = None) -> str:
        """Process a customer query and return a response.
        
        This is the main LLM workflow:
        - Takes a customer query
        - Optionally adds business context
        - Delegates to the backend agent
        - Returns the response
        
        Args:
            customer_query: The customer's question or request
            context: Optional business context (policies, product info, etc.)
            
        Returns:
            The agent's response
        """
        return self.agent.process_query(customer_query, context)
    
    def reset(self):
        """Reset agent conversation history."""
        self.agent.reset()
