"""Test that all modules import correctly."""

def test_config_import():
    """Test config module imports."""
    from company_eval_framework.config import EvalConfig
    assert EvalConfig is not None


def test_dataset_import():
    """Test dataset module imports."""
    from company_eval_framework.dataset import build_dataset
    assert build_dataset is not None


def test_evaluators_import():
    """Test evaluators module imports."""
    from company_eval_framework.evaluators import EvaluationMetric
    assert EvaluationMetric is not None


def test_runner_import():
    """Test runner module imports."""
    from company_eval_framework.runner import run_evaluation
    assert run_evaluation is not None


def test_cli_import():
    """Test cli module imports."""
    from company_eval_framework.cli import main
    assert main is not None
