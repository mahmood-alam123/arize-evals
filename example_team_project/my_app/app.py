"""Simple LLM-based customer support agent."""

from typing import Optional


class CustomerSupportAgent:
    """A simple single-agent LLM workflow for customer support."""
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize the agent.
        
        Args:
            model: LLM model to use
        """
        self.model = model
        self.conversation_history = []
    
    def process_query(self, customer_query: str, context: Optional[str] = None) -> str:
        """Process a customer query and return a response.
        
        Args:
            customer_query: The customer's question or request
            context: Optional business context (product info, policies, etc.)
            
        Returns:
            The agent's response
        """
        # Store in history
        self.conversation_history.append({
            "role": "customer",
            "content": customer_query
        })
        
        # In a real scenario, this would call an LLM API
        # For now, return a mock response
        response = f"Response to: {customer_query}"
        if context:
            response += f" (Context: {context})"
        
        self.conversation_history.append({
            "role": "agent",
            "content": response
        })
        
        return response
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []
