"""Evaluation adapter for the example app."""

def mock_agent_response(query: str, context: str = None) -> str:
    """Mock LLM agent that returns templated responses."""
    responses = {
        "How do I track my order?": "You can track your order by logging into your account, going to 'Orders', and clicking 'Track Package'. You'll see real-time updates on shipping status.",
        "What is your return policy?": "We offer a 30-day return policy for most items. Items must be in original condition with tags attached. Contact our support team to initiate a return.",
        "Can I cancel my subscription?": "Yes, you can cancel anytime from your account settings under 'Subscriptions'. There are no cancellation fees. Your access continues until the end of your billing period.",
        "How do I reset my password?": "Click 'Forgot Password' on the login page, enter your email, and we'll send you a reset link. Follow the link and create a new password.",
        "What payment methods do you accept?": "We accept all major credit cards (Visa, Mastercard, American Express), PayPal, Apple Pay, and Google Pay.",
    }
    
    return responses.get(query, f"I don't have information about: {query}")


def evaluate_agent_response(query: str, context: str = None) -> dict:
    """Adapter function that returns response in expected format.
    
    Args:
        query: User query
        context: Optional context for the query
        
    Returns:
        Dict with 'response' key containing agent response
    """
    response = mock_agent_response(query, context)
    
    return {
        "response": response,
        "context": context,
    }
