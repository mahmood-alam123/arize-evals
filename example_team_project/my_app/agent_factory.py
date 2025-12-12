"""Factory for creating different agent implementations."""

import os
from typing import Optional, Protocol


class Agent(Protocol):
    """Protocol for agent implementations."""
    
    def process_query(self, query: str, context: Optional[str] = None) -> str:
        """Process a customer query and return a response."""
        ...
    
    def reset(self):
        """Reset agent state."""
        ...


class MockAgent:
    """Mock agent that returns templated responses (for demos/testing)."""
    
    def __init__(self):
        """Initialize with predefined responses."""
        self.responses = {
            "How do I track my order?": "You can track your order by logging into your account, going to 'Orders', and clicking 'Track Package'. You'll see real-time updates on shipping status.",
            "What is your return policy?": "We offer a 30-day return policy for most items. Items must be in original condition with tags attached. Contact our support team to initiate a return.",
            "Can I cancel my subscription?": "Yes, you can cancel anytime from your account settings under 'Subscriptions'. There are no cancellation fees. Your access continues until the end of your billing period.",
            "How do I reset my password?": "Click 'Forgot Password' on the login page, enter your email, and we'll send you a reset link. Follow the link and create a new password.",
            "What payment methods do you accept?": "We accept all major credit cards (Visa, Mastercard, American Express), PayPal, Apple Pay, and Google Pay.",
        }
    
    def process_query(self, query: str, context: Optional[str] = None) -> str:
        """Return a templated response."""
        return self.responses.get(query, f"I don't have information about: {query}")
    
    def reset(self):
        """No-op for mock agent."""
        pass


class OpenAIAgent:
    """Agent that uses Azure OpenAI's Chat Completions API."""

    def __init__(
        self,
        model: str = "gpt-4o-deployment",
        temperature: float = 0.7,
        max_tokens: int = 200,
    ):
        """Initialize Azure OpenAI agent.

        Args:
            model: Azure deployment name (e.g., gpt-4o-deployment)
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Maximum tokens in response
        """
        try:
            from openai import AzureOpenAI, APIConnectionError, RateLimitError, AuthenticationError
        except ImportError:
            raise ImportError("OpenAI package required. Install with: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set (Azure OpenAI key)")
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set (e.g. https://<resource>.openai.azure.com/)")

        # Store client and error types
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        self.AuthenticationError = AuthenticationError
        self.RateLimitError = RateLimitError
        self.APIConnectionError = APIConnectionError

        # In Azure, `model` is the deployment name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history = []
        self.system_prompt = """You are a helpful customer support agent for an e-commerce company.
You provide accurate, concise, and professional responses to customer inquiries.
Keep responses to 2-3 sentences maximum."""

    def process_query(self, query: str, context: Optional[str] = None) -> str:
        """Process query using Azure OpenAI Chat Completions API.

        Args:
            query: Customer's question
            context: Optional business context

        Returns:
            Agent's response from the LLM
        """
        system = self.system_prompt
        if context:
            system += f"\nContext: {context}"

        # Build messages from conversation history + new user message
        messages = [{"role": "system", "content": system}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": query})

        try:
            resp = self.client.chat.completions.create(
                model=self.model,  # deployment name (e.g., gpt-4o-deployment)
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            agent_response = resp.choices[0].message.content or ""

            # Update history with user + assistant turns
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": agent_response})

            return agent_response

        except self.AuthenticationError:
            return "Error: Azure OpenAI API key authentication failed"
        except self.RateLimitError:
            return "Error: Azure OpenAI rate limit exceeded. Please try again later."
        except self.APIConnectionError:
            return "Error: Network error while calling Azure OpenAI API"
        except Exception as e:
            return f"Error calling Azure OpenAI: {str(e)}"

    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []


class LocalLLMAgent:
    """Agent that uses a local LLM via llama-cpp-python."""
    
    def __init__(self, model_path: str, n_ctx: int = 512, n_threads: int = 4):
        """Initialize local LLM agent.
        
        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: Number of threads to use
        """
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError("llama-cpp-python required. Install with: pip install llama-cpp-python")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False,
        )
        self.conversation_history = []
        self.system_prompt = """You are a helpful customer support agent for an e-commerce company.
You provide accurate, concise, and professional responses to customer inquiries.
Keep responses to 2-3 sentences maximum."""
    
    def process_query(self, query: str, context: Optional[str] = None) -> str:
        """Process query using local LLM.
        
        Args:
            query: Customer's question
            context: Optional business context
            
        Returns:
            Agent's response
        """
        # Build prompt
        system = self.system_prompt
        if context:
            system += f"\nContext: {context}"
        
        prompt = f"{system}\n\nUser: {query}\n\nAssistant:"
        
        try:
            response = self.llm(
                prompt,
                max_tokens=200,
                temperature=0.7,
                stop=["User:", "\n"],
            )
            
            return response["choices"][0]["text"].strip()
            
        except Exception as e:
            return f"Error calling local LLM: {str(e)}"
    
    def reset(self):
        """No-op for local LLM."""
        pass


def create_agent(agent_type: str = "mock", **kwargs) -> Agent:
    """Factory function to create an agent.
    
    Args:
        agent_type: Type of agent ("mock", "openai", "local")
        **kwargs: Additional arguments passed to agent constructor
        
    Returns:
        An agent instance
        
    Raises:
        ValueError: If agent_type is not recognized
    """
    if agent_type == "mock":
        return MockAgent()
    elif agent_type == "openai":
        return OpenAIAgent(**kwargs)
    elif agent_type == "local":
        return LocalLLMAgent(**kwargs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Choose from: mock, openai, local")
