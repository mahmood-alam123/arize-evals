"""
Custom evaluators for the example team project.

This module demonstrates how to create custom evaluators that can be used
alongside or instead of the built-in evaluation suites.

Usage:
    In your eval config YAML, add:

    custom_evaluators:
      - module: example_team_project.my_evaluators
        class: BrandVoiceEvaluator
"""

from company_eval_framework.evaluators import EvaluatorSpec


class BrandVoiceEvaluator(EvaluatorSpec):
    """
    Evaluates whether responses match the company's brand voice.

    This is an example custom evaluator that checks if chatbot responses
    are professional, friendly, and on-brand.
    """

    def __init__(self):
        super().__init__(
            name="brand_voice",
            template="""You are evaluating whether a chatbot response matches the company's brand voice.

Our brand voice is:
- Professional but friendly
- Helpful and empathetic
- Clear and concise
- Avoids jargon and technical terms unless necessary

[User Query]
{input}

[Chatbot Response]
{output}

Does this response match our brand voice guidelines?

Respond with one of: on_brand, off_brand""",
            rails_map={
                "on_brand": "on_brand",
                "off_brand": "off_brand",
            },
            input_columns=["input", "output"],
            positive_label="on_brand",
        )


class ResponseLengthEvaluator(EvaluatorSpec):
    """
    Evaluates whether responses are appropriately concise.

    This evaluator checks if responses are not too long or too short,
    providing an appropriate level of detail for the query.
    """

    def __init__(self):
        super().__init__(
            name="response_length",
            template="""You are evaluating whether a chatbot response has an appropriate length.

Good responses should:
- Be long enough to fully answer the question
- Be concise without unnecessary padding
- Not overwhelm the user with too much information

[User Query]
{input}

[Chatbot Response]
{output}

Is the response length appropriate for the query?

Respond with one of: appropriate, too_short, too_long""",
            rails_map={
                "appropriate": "appropriate",
                "too_short": "too_short",
                "too_long": "too_long",
            },
            input_columns=["input", "output"],
            positive_label="appropriate",
        )


class DomainAccuracyEvaluator(EvaluatorSpec):
    """
    Evaluates domain-specific accuracy for a customer support bot.

    This evaluator checks if responses contain accurate information
    about company policies, products, and procedures.
    """

    def __init__(self):
        super().__init__(
            name="domain_accuracy",
            template="""You are evaluating a customer support chatbot's response for accuracy.

The chatbot should provide accurate information about:
- Account management (password resets, profile updates)
- Billing and payments (payment methods, invoices, refunds)
- Subscription management (cancellation, upgrades, downgrades)

[User Query]
{input}

[Chatbot Response]
{output}

Does the response appear to contain accurate and reasonable information?
Note: You should evaluate if the response seems plausible and helpful,
not if you can verify the specific facts.

Respond with one of: accurate, inaccurate, uncertain""",
            rails_map={
                "accurate": "accurate",
                "inaccurate": "inaccurate",
                "uncertain": "uncertain",
            },
            input_columns=["input", "output"],
            positive_label="accurate",
        )
