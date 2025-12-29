"""
Quality Dashboard for company-eval framework.

A web-based dashboard for viewing LLM evaluation results over time.
"""

from .server import create_app, main

__all__ = ["create_app", "main"]
