"""Seed the database with sample/demo data."""

import uuid
from datetime import datetime, timedelta
from .database import SessionLocal, Run, Metric, TestCase, TestCaseScore, Failure, create_tables


def seed_demo_data():
    """Populate database with realistic demo evaluation runs."""
    create_tables()
    db = SessionLocal()

    # Check if data already exists
    if db.query(Run).count() > 0:
        print("Database already has data, skipping seed.")
        db.close()
        return

    print("Seeding demo data...")

    # Create several demo runs
    demo_runs = [
        {
            "app_name": "customer-support-bot",
            "app_type": "simple_chat",
            "eval_suite": "basic_chat",
            "passed": True,
            "git_branch": "main",
            "git_commit": "a1b2c3d",
            "hours_ago": 2,
            "metrics": [
                {"name": "user_frustration", "mean_score": 0.92, "threshold_type": "max", "threshold_value": 0.3, "passed": True},
                {"name": "toxicity", "mean_score": 1.0, "threshold_type": None, "threshold_value": None, "passed": True},
                {"name": "helpfulness_quality", "mean_score": 0.88, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
            ],
            "test_cases": [
                {"input": "How do I reset my password?", "output": "To reset your password, click on 'Forgot Password' on the login page and follow the instructions sent to your email.", "passed": True},
                {"input": "What are your business hours?", "output": "Our support team is available Monday through Friday, 9 AM to 6 PM EST.", "passed": True},
                {"input": "I want to cancel my subscription", "output": "I understand you'd like to cancel. You can do this in Account Settings > Subscription > Cancel Plan. Would you like me to walk you through it?", "passed": True},
                {"input": "Your product sucks!", "output": "I'm sorry to hear you're frustrated. I'd like to help make things right. Could you tell me what specific issues you're experiencing?", "passed": True},
                {"input": "Can I get a refund?", "output": "Yes, we offer refunds within 30 days of purchase. Please provide your order number and I'll process it for you.", "passed": True},
            ],
        },
        {
            "app_name": "customer-support-bot",
            "app_type": "simple_chat",
            "eval_suite": "basic_chat",
            "passed": False,
            "git_branch": "feature/new-prompt",
            "git_commit": "x9y8z7w",
            "hours_ago": 24,
            "metrics": [
                {"name": "user_frustration", "mean_score": 0.60, "threshold_type": "max", "threshold_value": 0.3, "passed": False},
                {"name": "toxicity", "mean_score": 1.0, "threshold_type": None, "threshold_value": None, "passed": True},
                {"name": "helpfulness_quality", "mean_score": 0.65, "threshold_type": "min", "threshold_value": 0.7, "passed": False},
            ],
            "test_cases": [
                {"input": "How do I reset my password?", "output": "Password reset is in settings.", "passed": False, "failure_type": "incomplete_answer"},
                {"input": "I need help with billing", "output": "Please contact billing department.", "passed": False, "failure_type": "unhelpful"},
                {"input": "What's the status of my order?", "output": "I don't have access to order information.", "passed": False, "failure_type": "refusal"},
            ],
        },
        {
            "app_name": "docs-qa-bot",
            "app_type": "rag",
            "eval_suite": "basic_rag",
            "passed": True,
            "git_branch": "main",
            "git_commit": "f4e5d6c",
            "hours_ago": 5,
            "metrics": [
                {"name": "hallucination", "mean_score": 0.95, "threshold_type": "max", "threshold_value": 0.1, "passed": True},
                {"name": "document_relevance", "mean_score": 0.90, "threshold_type": "min", "threshold_value": 0.8, "passed": True},
                {"name": "answer_quality", "mean_score": 0.85, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
            ],
            "test_cases": [
                {"input": "What is the API rate limit?", "output": "According to the documentation, the API rate limit is 100 requests per minute for standard accounts and 1000 requests per minute for enterprise accounts.", "context": "API Rate Limits: Standard accounts are limited to 100 requests/minute. Enterprise accounts have a limit of 1000 requests/minute.", "passed": True},
                {"input": "How do I authenticate?", "output": "Authentication is done via API keys. You can generate an API key in your dashboard under Settings > API Keys. Include the key in the Authorization header.", "context": "Authentication: Use API keys for authentication. Generate keys in Dashboard > Settings > API Keys. Pass the key in the Authorization header.", "passed": True},
            ],
        },
        {
            "app_name": "docs-qa-bot",
            "app_type": "rag",
            "eval_suite": "basic_rag",
            "passed": False,
            "git_branch": "fix/retrieval",
            "git_commit": "m2n3o4p",
            "hours_ago": 48,
            "metrics": [
                {"name": "hallucination", "mean_score": 0.70, "threshold_type": "max", "threshold_value": 0.1, "passed": False},
                {"name": "document_relevance", "mean_score": 0.65, "threshold_type": "min", "threshold_value": 0.8, "passed": False},
                {"name": "answer_quality", "mean_score": 0.60, "threshold_type": "min", "threshold_value": 0.7, "passed": False},
            ],
            "test_cases": [
                {"input": "What is the API rate limit?", "output": "The API rate limit is 500 requests per minute.", "context": "Pricing: Our plans start at $29/month.", "passed": False, "failure_type": "hallucination"},
                {"input": "How do I authenticate?", "output": "You authenticate using OAuth2 with JWT tokens.", "context": "Getting Started: Welcome to our platform!", "passed": False, "failure_type": "hallucination"},
            ],
        },
        {
            "app_name": "task-agent",
            "app_type": "agent",
            "eval_suite": "agent",
            "passed": True,
            "git_branch": "main",
            "git_commit": "q5r6s7t",
            "hours_ago": 12,
            "metrics": [
                {"name": "planning_quality", "mean_score": 0.90, "threshold_type": "min", "threshold_value": 0.8, "passed": True},
                {"name": "tool_use_appropriateness", "mean_score": 0.85, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
            ],
            "test_cases": [
                {"input": "Schedule a meeting with John for next Tuesday at 2pm", "output": "I'll schedule that meeting for you. Creating calendar event: Meeting with John, Tuesday 2:00 PM. Done!", "passed": True},
                {"input": "Find all emails from last week about the project", "output": "Searching emails from the past 7 days with keyword 'project'... Found 12 emails. Would you like me to summarize them?", "passed": True},
            ],
        },
    ]

    for run_data in demo_runs:
        started_at = datetime.utcnow() - timedelta(hours=run_data["hours_ago"])
        duration = 45.5 + (hash(run_data["app_name"]) % 60)

        run = Run(
            id=str(uuid.uuid4()),
            app_name=run_data["app_name"],
            app_type=run_data["app_type"],
            eval_suite=run_data["eval_suite"],
            dataset_size=len(run_data["test_cases"]),
            passed=run_data["passed"],
            started_at=started_at,
            finished_at=started_at + timedelta(seconds=duration),
            duration_seconds=duration,
            git_branch=run_data["git_branch"],
            git_commit=run_data["git_commit"],
            config_path=f"configs/{run_data['app_name']}/eval_config.yaml",
        )
        db.add(run)
        db.flush()

        # Add metrics
        for m in run_data["metrics"]:
            metric = Metric(
                run_id=run.id,
                name=m["name"],
                mean_score=m["mean_score"],
                failure_rate=1.0 - m["mean_score"],
                threshold_type=m["threshold_type"],
                threshold_value=m["threshold_value"],
                passed=m["passed"],
            )
            db.add(metric)

        # Add test cases
        for i, tc_data in enumerate(run_data["test_cases"]):
            tc = TestCase(
                run_id=run.id,
                conversation_id=str(i + 1),
                input=tc_data["input"],
                output=tc_data["output"],
                context=tc_data.get("context"),
            )
            db.add(tc)
            db.flush()

            # Add scores for each metric
            for m in run_data["metrics"]:
                score = 1.0 if tc_data["passed"] else 0.0
                tc_score = TestCaseScore(
                    test_case_id=tc.id,
                    metric_name=m["name"],
                    score=score,
                    label="pass" if score == 1.0 else "fail",
                    explanation="Response meets quality criteria." if score == 1.0 else "Response does not meet criteria.",
                )
                db.add(tc_score)

            # Add failure if present
            if not tc_data["passed"] and "failure_type" in tc_data:
                failure = Failure(
                    test_case_id=tc.id,
                    failure_type=tc_data["failure_type"],
                    explanation=f"Test case failed due to {tc_data['failure_type']}",
                )
                db.add(failure)

    db.commit()
    db.close()
    print(f"Seeded {len(demo_runs)} demo runs.")


if __name__ == "__main__":
    seed_demo_data()
