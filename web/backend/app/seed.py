"""Seed the database with demo data for hackathon presentation."""

import uuid
import json
from datetime import datetime, timedelta
from .database import SessionLocal, Run, Metric, TestCase, TestCaseScore, Failure, Trace, Span, Dataset, DatasetExample, create_tables


# System prompts for different app types
SYSTEM_PROMPTS = {
    "simple_chat": """You are a helpful customer support assistant for TechCorp Inc.

Your role is to:
- Answer customer questions politely and professionally
- Help resolve issues and provide clear instructions
- Escalate complex issues when necessary
- Never make up information you don't have

Always be empathetic and solution-oriented.""",

    "rag": """You are a documentation assistant that answers questions based on the provided context.

Instructions:
- Only answer based on the provided context
- If the context doesn't contain the answer, say "I don't have information about that in the documentation"
- Quote relevant parts of the documentation when helpful
- Be concise but thorough

Context:
{context}""",

    "agent": """You are a task execution agent with access to various tools.

Available tools:
- calendar.create_event: Schedule calendar events
- calendar.list_events: Check calendar availability
- email.search: Search emails
- email.send: Send emails
- web.search: Search the internet

Instructions:
- Break down complex tasks into steps
- Use the appropriate tools to complete tasks
- Confirm actions before executing them
- Report results clearly"""
}


def generate_prompt(app_type: str, user_input: str, context: str = None) -> str:
    """Generate the full prompt sent to the LLM."""
    system_prompt = SYSTEM_PROMPTS.get(app_type, SYSTEM_PROMPTS["simple_chat"])

    if app_type == "rag" and context:
        system_prompt = system_prompt.format(context=context)

    return f"{system_prompt}\n\nUser: {user_input}"


def create_trace_for_test_case(db, app_type: str, input_text: str, output_text: str, started_at: datetime, is_failure: bool = False, tool_name: str = None) -> str:
    """Create a trace with appropriate spans based on app type."""
    trace_id = str(uuid.uuid4())
    duration_ms = 800 + (hash(input_text) % 1500)

    trace = Trace(
        id=trace_id,
        name=f"{app_type}_request",
        project_name=app_type,
        start_time=started_at,
        end_time=started_at + timedelta(milliseconds=duration_ms),
        duration_ms=duration_ms,
        status="completed",
        input=json.dumps({"message": input_text}),
        output=json.dumps({"response": output_text}),
        total_tokens=200 + (hash(input_text) % 400),
        total_cost=0.002 + (hash(input_text) % 100) * 0.00002,
    )
    db.add(trace)
    db.flush()

    span_time = started_at

    if app_type == "rag":
        # RAG: retrieval span + LLM span
        retrieval_duration = 150 + (hash(input_text) % 200)
        retrieval_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name="document_search",
            span_type="retrieval",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=retrieval_duration),
            duration_ms=retrieval_duration,
            status="completed",
            input=json.dumps({"query": input_text, "top_k": 3}),
            output=json.dumps({"documents": 3, "relevance_scores": [0.92, 0.87, 0.81]}),
        )
        db.add(retrieval_span)
        span_time += timedelta(milliseconds=retrieval_duration)

        llm_duration = duration_ms - retrieval_duration - 50
        llm_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name="generate_answer",
            span_type="llm",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=llm_duration),
            duration_ms=llm_duration,
            status="completed",
            model="gpt-4o",
            provider="openai",
            input=json.dumps({"messages": [{"role": "system", "content": "Answer based on context"}, {"role": "user", "content": input_text}]}),
            output=json.dumps({"content": output_text}),
            prompt_tokens=350 + (hash(input_text) % 150),
            completion_tokens=120 + (hash(output_text) % 80),
            total_tokens=470 + (hash(input_text) % 200),
            cost=0.0045,
        )
        db.add(llm_span)

    elif app_type == "agent":
        # Agent: planning span + tool span + LLM span
        planning_duration = 200 + (hash(input_text) % 150)
        planning_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name="plan_task",
            span_type="chain",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=planning_duration),
            duration_ms=planning_duration,
            status="completed",
            input=json.dumps({"task": input_text}),
            output=json.dumps({"plan": ["Analyze request", "Select tool", "Execute", "Respond"]}),
        )
        db.add(planning_span)
        span_time += timedelta(milliseconds=planning_duration)

        tool_duration = 250 + (hash(input_text) % 200)
        actual_tool = tool_name or ("calendar.create_event" if "meeting" in input_text.lower() or "schedule" in input_text.lower() else "email.search")
        tool_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name=actual_tool,
            span_type="tool",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=tool_duration),
            duration_ms=tool_duration,
            status="error" if is_failure else "completed",
            tool_name=actual_tool,
            tool_args=json.dumps({"query": input_text}),
            input=json.dumps({"action": "execute", "tool": actual_tool}),
            output=json.dumps({"error": "Invalid arguments"} if is_failure else {"result": "success", "data": {"created": True}}),
        )
        db.add(tool_span)
        span_time += timedelta(milliseconds=tool_duration)

        llm_duration = duration_ms - planning_duration - tool_duration - 50
        llm_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name="generate_response",
            span_type="llm",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=llm_duration),
            duration_ms=llm_duration,
            status="completed",
            model="gpt-4o",
            provider="openai",
            input=json.dumps({"messages": [{"role": "user", "content": input_text}]}),
            output=json.dumps({"content": output_text}),
            prompt_tokens=180,
            completion_tokens=95,
            total_tokens=275,
            cost=0.0028,
        )
        db.add(llm_span)

    else:
        # Simple chat: just LLM span
        llm_span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace_id,
            name="chat_completion",
            span_type="llm",
            start_time=span_time,
            end_time=span_time + timedelta(milliseconds=duration_ms - 20),
            duration_ms=duration_ms - 20,
            status="completed",
            model="gpt-4o-mini",
            provider="openai",
            input=json.dumps({"messages": [{"role": "system", "content": SYSTEM_PROMPTS["simple_chat"]}, {"role": "user", "content": input_text}]}),
            output=json.dumps({"content": output_text}),
            prompt_tokens=85 + (hash(input_text) % 50),
            completion_tokens=60 + (hash(output_text) % 40),
            total_tokens=145 + (hash(input_text) % 80),
            cost=0.00035,
        )
        db.add(llm_span)

    return trace_id


def seed_demo_data():
    """Populate database with demo data for hackathon presentation."""
    create_tables()
    db = SessionLocal()

    # Check if data already exists
    if db.query(Run).count() > 0:
        print("Database already has data, skipping seed.")
        db.close()
        return

    print("Seeding demo data for hackathon...")

    # ========================================
    # 6 DEMO RUNS
    # ========================================
    demo_runs = [
        # 1. Simple Chat - PASS
        {
            "app_name": "customer-support-bot",
            "app_type": "simple_chat",
            "eval_suite": "basic_chat",
            "passed": True,
            "git_branch": "main",
            "git_commit": "a1b2c3d",
            "hours_ago": 2,
            "app_cost": 0.0052,
            "eval_cost": 0.0148,
            "metrics": [
                {"name": "user_frustration", "mean_score": 0.08, "threshold_type": "max", "threshold_value": 0.2, "passed": True},
                {"name": "helpfulness_quality", "mean_score": 0.92, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
                {"name": "toxicity", "mean_score": 0.00, "threshold_type": "max", "threshold_value": 0.05, "passed": True},
            ],
            "test_cases": [
                {"input": "How do I reset my password?", "output": "I'd be happy to help you reset your password! Here's how:\n\n1. Go to the login page and click 'Forgot Password'\n2. Enter your email address\n3. Check your inbox for a reset link (valid for 24 hours)\n4. Click the link and create a new password\n\nIf you don't receive the email within 5 minutes, check your spam folder. Let me know if you need any other help!", "passed": True},
                {"input": "What are your business hours?", "output": "Our support team is available:\n\n- Monday to Friday: 9 AM - 8 PM EST\n- Saturday: 10 AM - 6 PM EST\n- Sunday: Closed\n\nFor urgent issues outside these hours, you can use our 24/7 automated help center at help.techcorp.com. Is there anything specific I can help you with right now?", "passed": True},
                {"input": "I want to cancel my subscription", "output": "I understand you'd like to cancel your subscription. Before I help with that, would you mind sharing what's prompting the cancellation? We might be able to address any concerns.\n\nIf you'd like to proceed:\n1. Go to Account Settings > Subscription\n2. Click 'Manage Plan'\n3. Select 'Cancel Subscription'\n\nYour access will continue until the end of your billing period. Would you like me to walk you through this?", "passed": True},
                {"input": "Your product is broken and I'm very frustrated!", "output": "I'm truly sorry you're experiencing issues - I completely understand how frustrating that must be. Let's get this fixed for you right away.\n\nCould you tell me:\n1. What specific feature isn't working?\n2. What device/browser are you using?\n3. When did this start happening?\n\nThis will help me troubleshoot quickly. In the meantime, have you tried clearing your browser cache? That often resolves common issues.", "passed": True},
                {"input": "Can I get a refund for my last purchase?", "output": "Yes, we offer full refunds within 30 days of purchase! Here's what I need to process your refund:\n\n1. Your order number (found in your confirmation email)\n2. The email address used for the purchase\n\nOnce I have those, I can process the refund immediately. It typically takes 3-5 business days to appear on your statement. Do you have your order number handy?", "passed": True},
                {"input": "How do I upgrade my plan?", "output": "Great choice! Upgrading is easy:\n\n1. Log into your account\n2. Go to Settings > Billing\n3. Click 'Change Plan'\n4. Select your new plan\n\nThe price difference will be prorated for your current billing period. Pro plans include priority support and advanced features. Would you like me to explain the differences between our plans?", "passed": True},
            ],
        },
        # 2. Simple Chat - FAIL
        {
            "app_name": "customer-support-bot",
            "app_type": "simple_chat",
            "eval_suite": "basic_chat",
            "passed": False,
            "git_branch": "feature/new-prompt-v2",
            "git_commit": "x9y8z7w",
            "hours_ago": 26,
            "app_cost": 0.0038,
            "eval_cost": 0.0112,
            "metrics": [
                {"name": "user_frustration", "mean_score": 0.45, "threshold_type": "max", "threshold_value": 0.2, "passed": False},
                {"name": "helpfulness_quality", "mean_score": 0.55, "threshold_type": "min", "threshold_value": 0.7, "passed": False},
                {"name": "toxicity", "mean_score": 0.00, "threshold_type": "max", "threshold_value": 0.05, "passed": True},
            ],
            "test_cases": [
                {"input": "How do I reset my password?", "output": "Go to settings and reset it there.", "passed": False, "failure_type": "incomplete_answer", "failure_explanation": "Response is too brief and lacks step-by-step guidance. User may still be confused about the process."},
                {"input": "I need help with my billing issue", "output": "You'll need to contact the billing department for that.", "passed": False, "failure_type": "unhelpful_response", "failure_explanation": "Response deflects the user without providing any assistance or contact information."},
                {"input": "What's the status of my order #12345?", "output": "I cannot access order information.", "passed": False, "failure_type": "capability_refusal", "failure_explanation": "Response refuses to help without offering alternatives or escalation path."},
                {"input": "Your app keeps crashing on my phone", "output": "Try restarting your phone.", "passed": False, "failure_type": "dismissive_response", "failure_explanation": "Response is dismissive and doesn't gather troubleshooting information or show empathy."},
                {"input": "Can I speak to a manager?", "output": "Managers are not available right now.", "passed": False, "failure_type": "unhelpful_response", "failure_explanation": "Response blocks escalation without offering alternatives or timeframes."},
            ],
        },
        # 3. RAG - PASS
        {
            "app_name": "docs-qa-assistant",
            "app_type": "rag",
            "eval_suite": "basic_rag",
            "passed": True,
            "git_branch": "main",
            "git_commit": "f4e5d6c",
            "hours_ago": 6,
            "app_cost": 0.0095,
            "eval_cost": 0.0185,
            "metrics": [
                {"name": "hallucination", "mean_score": 0.04, "threshold_type": "max", "threshold_value": 0.1, "passed": True},
                {"name": "document_relevance", "mean_score": 0.94, "threshold_type": "min", "threshold_value": 0.8, "passed": True},
                {"name": "answer_quality", "mean_score": 0.88, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
            ],
            "test_cases": [
                {"input": "What is the API rate limit?", "output": "According to the documentation, the API rate limits are:\n\n- **Standard accounts**: 100 requests per minute\n- **Pro accounts**: 500 requests per minute  \n- **Enterprise accounts**: 2,000 requests per minute\n\nIf you exceed these limits, you'll receive a 429 status code. The rate limit resets every minute.", "context": "# API Rate Limits\n\nOur API enforces the following rate limits based on your account tier:\n- Standard: 100 requests/minute\n- Pro: 500 requests/minute\n- Enterprise: 2,000 requests/minute\n\nExceeding limits returns HTTP 429. Limits reset every 60 seconds.", "passed": True},
                {"input": "How do I authenticate API requests?", "output": "API authentication uses API keys. Here's how to authenticate:\n\n1. Generate an API key in Dashboard > Settings > API Keys\n2. Include the key in your request headers:\n   ```\n   Authorization: Bearer YOUR_API_KEY\n   ```\n\nKeep your API key secret and never expose it in client-side code.", "context": "# Authentication\n\nAll API requests must be authenticated using API keys.\n\n## Generating Keys\nNavigate to Dashboard > Settings > API Keys to create a new key.\n\n## Using Keys\nInclude your key in the Authorization header:\n```\nAuthorization: Bearer YOUR_API_KEY\n```\n\nNote: Never expose API keys in client-side code.", "passed": True},
                {"input": "What formats does the export feature support?", "output": "The export feature supports three formats:\n\n1. **JSON** - Best for programmatic access\n2. **CSV** - Best for spreadsheets and data analysis\n3. **PDF** - Best for reports and sharing\n\nYou can access export from the Data menu or via the `/export` API endpoint.", "context": "# Data Export\n\nExport your data in multiple formats:\n\n## Supported Formats\n- JSON: Structured data for APIs\n- CSV: Tabular format for Excel/Google Sheets\n- PDF: Formatted reports for sharing\n\n## How to Export\n- UI: Data menu > Export\n- API: POST /export with format parameter", "passed": True},
                {"input": "How do I set up webhooks?", "output": "To set up webhooks:\n\n1. Go to Settings > Webhooks\n2. Click 'Add Webhook'\n3. Enter your endpoint URL (must be HTTPS)\n4. Select the events you want to receive\n5. Save and test the webhook\n\nWebhooks will POST JSON payloads to your endpoint. Make sure your server responds with 200 OK within 30 seconds.", "context": "# Webhooks\n\nWebhooks allow you to receive real-time notifications.\n\n## Setup\n1. Navigate to Settings > Webhooks\n2. Click 'Add Webhook'\n3. Enter HTTPS endpoint URL\n4. Choose events to subscribe to\n5. Save configuration\n\n## Requirements\n- Endpoint must use HTTPS\n- Must respond with 200 within 30s\n- Payload format is JSON", "passed": True},
                {"input": "What's the maximum file upload size?", "output": "The maximum file upload size depends on your plan:\n\n- **Free**: 10 MB per file\n- **Pro**: 100 MB per file\n- **Enterprise**: 500 MB per file\n\nSupported formats include JPG, PNG, PDF, and DOCX. For larger files, consider using our chunked upload API.", "context": "# File Uploads\n\n## Size Limits\nMaximum file sizes by plan:\n- Free: 10 MB\n- Pro: 100 MB\n- Enterprise: 500 MB\n\n## Supported Formats\nJPG, PNG, GIF, PDF, DOCX, XLSX\n\n## Large Files\nFor files exceeding limits, use the chunked upload API endpoint.", "passed": True},
            ],
        },
        # 4. RAG - FAIL
        {
            "app_name": "docs-qa-assistant",
            "app_type": "rag",
            "eval_suite": "basic_rag",
            "passed": False,
            "git_branch": "experiment/new-retriever",
            "git_commit": "m2n3o4p",
            "hours_ago": 52,
            "app_cost": 0.0072,
            "eval_cost": 0.0138,
            "metrics": [
                {"name": "hallucination", "mean_score": 0.35, "threshold_type": "max", "threshold_value": 0.1, "passed": False},
                {"name": "document_relevance", "mean_score": 0.52, "threshold_type": "min", "threshold_value": 0.8, "passed": False},
                {"name": "answer_quality", "mean_score": 0.58, "threshold_type": "min", "threshold_value": 0.7, "passed": False},
            ],
            "test_cases": [
                {"input": "What is the API rate limit?", "output": "The API rate limit is 500 requests per second for all account types. Enterprise customers get priority queue access.", "context": "# Pricing Plans\n\nOur pricing is simple and transparent:\n- Starter: $29/month\n- Pro: $99/month\n- Enterprise: Custom pricing\n\nAll plans include 24/7 support.", "passed": False, "failure_type": "hallucination", "failure_explanation": "Response fabricates rate limit information (500/second) that is not present in the retrieved context. The context is about pricing, not rate limits."},
                {"input": "How do I authenticate API requests?", "output": "You can authenticate using OAuth 2.0 with JWT tokens. First register your application, then implement the OAuth flow with the /oauth/authorize endpoint.", "context": "# Company Overview\n\nWelcome to TechCorp! We've been serving customers since 2015.\n\nOur mission is to simplify technology for everyone.", "passed": False, "failure_type": "hallucination", "failure_explanation": "Response fabricates OAuth/JWT authentication method. The retrieved context is completely irrelevant (company overview) and contains no authentication information."},
                {"input": "What happens when I exceed the storage limit?", "output": "When you exceed storage limits, your oldest files are automatically deleted to make room for new ones.", "context": "# Getting Started\n\nFollow these steps to begin:\n1. Create an account\n2. Verify your email\n3. Complete your profile", "passed": False, "failure_type": "hallucination", "failure_explanation": "Response fabricates auto-deletion behavior that is not mentioned in the context. This could cause users to lose important data based on false information."},
                {"input": "Does the API support batch operations?", "output": "Yes, batch operations are supported. You can process up to 1000 items per batch request using the /batch endpoint.", "context": "# Terms of Service\n\nBy using our service, you agree to:\n- Use the service lawfully\n- Not share your account\n- Report any security issues", "passed": False, "failure_type": "hallucination", "failure_explanation": "Response fabricates batch API details. The context is Terms of Service, completely unrelated to API capabilities."},
            ],
        },
        # 5. Agent - PASS
        {
            "app_name": "task-automation-agent",
            "app_type": "agent",
            "eval_suite": "agent",
            "passed": True,
            "git_branch": "main",
            "git_commit": "q5r6s7t",
            "hours_ago": 14,
            "app_cost": 0.0285,
            "eval_cost": 0.0215,
            "metrics": [
                {"name": "planning_quality", "mean_score": 0.92, "threshold_type": "min", "threshold_value": 0.7, "passed": True},
                {"name": "tool_use_appropriateness", "mean_score": 0.88, "threshold_type": "min", "threshold_value": 0.8, "passed": True},
            ],
            "test_cases": [
                {"input": "Schedule a meeting with Sarah for next Tuesday at 2pm to discuss the Q4 roadmap", "output": "I'll schedule that meeting for you.\n\n**Action taken:**\n- Created calendar event: 'Q4 Roadmap Discussion with Sarah'\n- Date: Tuesday, January 7th at 2:00 PM\n- Duration: 1 hour (default)\n- Attendee: Sarah\n\nI've sent a calendar invite to Sarah. Would you like me to add any notes or adjust the duration?", "passed": True, "tool_name": "calendar.create_event"},
                {"input": "Find all emails from the product team about the launch", "output": "I searched your emails for messages from the product team about the launch.\n\n**Found 8 emails:**\n1. 'Launch Timeline Update' from product@company.com (Dec 15)\n2. 'Launch Checklist Review' from sarah@company.com (Dec 12)\n3. 'RE: Launch Marketing Assets' from mike@company.com (Dec 10)\n... and 5 more\n\nWould you like me to summarize these emails or show the full list?", "passed": True, "tool_name": "email.search"},
                {"input": "Check if I have any conflicts on Thursday afternoon", "output": "I checked your calendar for Thursday afternoon.\n\n**Thursday, January 9th (12 PM - 6 PM):**\n- 1:00 PM - 2:00 PM: Team Standup\n- 3:30 PM - 4:00 PM: 1:1 with Manager\n\n**Available slots:**\n- 12:00 PM - 1:00 PM\n- 2:00 PM - 3:30 PM\n- 4:00 PM - 6:00 PM\n\nWould you like me to schedule something in one of the available slots?", "passed": True, "tool_name": "calendar.list_events"},
                {"input": "Send a reminder email to the team about tomorrow's demo", "output": "I'll draft and send that reminder email.\n\n**Email sent:**\n- To: team@company.com\n- Subject: Reminder: Demo Tomorrow\n- Body: 'Hi team, Just a friendly reminder about our demo scheduled for tomorrow. Please come prepared with your updates. See you there!'\n\nThe email has been sent. Would you like me to send any follow-up reminders?", "passed": True, "tool_name": "email.send"},
                {"input": "What's the weather forecast for the team offsite next week?", "output": "I searched for weather information for your team offsite location.\n\n**San Francisco, CA - Next Week Forecast:**\n- Monday: 62°F, Partly Cloudy\n- Tuesday: 58°F, Light Rain\n- Wednesday: 61°F, Sunny\n- Thursday: 65°F, Sunny\n- Friday: 63°F, Cloudy\n\nTuesday might need indoor backup plans. Would you like me to add weather notes to the offsite calendar event?", "passed": True, "tool_name": "web.search"},
            ],
        },
        # 6. Agent - FAIL
        {
            "app_name": "task-automation-agent",
            "app_type": "agent",
            "eval_suite": "agent",
            "passed": False,
            "git_branch": "feature/tool-improvements",
            "git_commit": "j8k9l0m",
            "hours_ago": 38,
            "app_cost": 0.0198,
            "eval_cost": 0.0167,
            "metrics": [
                {"name": "planning_quality", "mean_score": 0.55, "threshold_type": "min", "threshold_value": 0.7, "passed": False},
                {"name": "tool_use_appropriateness", "mean_score": 0.48, "threshold_type": "min", "threshold_value": 0.8, "passed": False},
            ],
            "test_cases": [
                {"input": "Schedule a meeting with the team for tomorrow", "output": "I tried to schedule the meeting but encountered an error. The calendar service returned an error.", "passed": False, "failure_type": "tool_execution_error", "failure_explanation": "Agent attempted to use calendar tool but failed to handle missing required parameters (time, attendees). Should have asked for clarification.", "tool_name": "calendar.create_event"},
                {"input": "Send an email to John about the project update", "output": "I searched for emails from John but didn't find any relevant project updates to reference.", "passed": False, "failure_type": "wrong_tool_selection", "failure_explanation": "Agent used email.search instead of email.send. User wanted to SEND an email, not search for one.", "tool_name": "email.search"},
                {"input": "What meetings do I have next week?", "output": "I've drafted an email about your meetings next week. Should I send it?", "passed": False, "failure_type": "wrong_tool_selection", "failure_explanation": "Agent attempted to send an email instead of checking the calendar. Completely misunderstood the user's intent.", "tool_name": "email.send"},
                {"input": "Book a flight to New York for the conference", "output": "I've scheduled a calendar event for your New York trip. Is there anything else you need?", "passed": False, "failure_type": "capability_mismatch", "failure_explanation": "Agent used calendar instead of acknowledging it cannot book flights. Created a calendar event which doesn't fulfill the actual request.", "tool_name": "calendar.create_event"},
                {"input": "Reschedule my 3pm meeting to 4pm", "output": "I searched your calendar but couldn't find any meetings. Your calendar appears to be empty.", "passed": False, "failure_type": "tool_execution_error", "failure_explanation": "Agent failed to properly query the calendar. The error message suggests a technical failure or incorrect API usage.", "tool_name": "calendar.list_events"},
            ],
        },
    ]

    for run_data in demo_runs:
        started_at = datetime.utcnow() - timedelta(hours=run_data["hours_ago"])
        duration = 55.0 + (hash(run_data["app_name"] + run_data["git_commit"]) % 45)

        app_cost = run_data.get("app_cost", 0.0)
        eval_cost = run_data.get("eval_cost", 0.0)
        total_cost = app_cost + eval_cost

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
            total_cost=total_cost,
            app_cost=app_cost,
            eval_cost=eval_cost,
        )
        db.add(run)
        db.flush()

        # Add metrics
        for m in run_data["metrics"]:
            metric = Metric(
                run_id=run.id,
                name=m["name"],
                mean_score=m["mean_score"],
                failure_rate=1.0 - m["mean_score"] if m["threshold_type"] == "min" else m["mean_score"],
                threshold_type=m["threshold_type"],
                threshold_value=m["threshold_value"],
                passed=m["passed"],
            )
            db.add(metric)

        # Add test cases
        for i, tc_data in enumerate(run_data["test_cases"]):
            tc_started_at = started_at + timedelta(seconds=i * 3)
            trace_id = create_trace_for_test_case(
                db,
                app_type=run_data["app_type"],
                input_text=tc_data["input"],
                output_text=tc_data["output"],
                started_at=tc_started_at,
                is_failure=not tc_data["passed"],
                tool_name=tc_data.get("tool_name"),
            )

            full_prompt = generate_prompt(
                app_type=run_data["app_type"],
                user_input=tc_data["input"],
                context=tc_data.get("context"),
            )

            tc = TestCase(
                run_id=run.id,
                conversation_id=f"conv-{i + 1:03d}",
                input=tc_data["input"],
                output=tc_data["output"],
                context=tc_data.get("context"),
                prompt=full_prompt,
                trace_id=trace_id,
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
                    explanation="Response meets quality criteria." if score == 1.0 else tc_data.get("failure_explanation", "Response does not meet criteria."),
                )
                db.add(tc_score)

            # Add failure if present
            if not tc_data["passed"] and "failure_type" in tc_data:
                failure = Failure(
                    test_case_id=tc.id,
                    failure_type=tc_data["failure_type"],
                    explanation=tc_data.get("failure_explanation", f"Test case failed due to {tc_data['failure_type']}"),
                )
                db.add(failure)

    # ========================================
    # DEMO DATASETS
    # ========================================
    demo_datasets = [
        {
            "name": "customer-support-golden",
            "description": "Curated golden test cases for customer support evaluation",
            "app_type": "simple_chat",
            "source": "upload",
            "examples": [
                {"input": "How do I change my email address?", "expected_output": "Navigate to Settings > Account > Email to update your email address."},
                {"input": "I forgot my password and can't access my email", "expected_output": "Contact support with your account details for manual verification."},
                {"input": "Can I have multiple users on one account?", "expected_output": "Yes, our Team plan supports up to 10 users. Enterprise has unlimited users."},
                {"input": "How do I export my data?", "expected_output": "Go to Settings > Data > Export. You can export as CSV, JSON, or PDF."},
                {"input": "What payment methods do you accept?", "expected_output": "We accept Visa, Mastercard, American Express, and PayPal."},
            ],
        },
        {
            "name": "rag-edge-cases",
            "description": "Synthetic edge cases for RAG system testing",
            "app_type": "rag",
            "source": "synthetic",
            "generation_config": json.dumps({"model": "gpt-4o", "focus": "edge_cases", "generated_at": datetime.utcnow().isoformat()}),
            "examples": [
                {"input": "What features were deprecated in version 2.0?", "context": "Version 2.0 release notes..."},
                {"input": "How do I migrate from the legacy API?", "context": "Migration guide..."},
                {"input": "Is there a rate limit for webhooks?", "context": "Webhook documentation..."},
                {"input": "Can I use the API without authentication for testing?", "context": "Authentication docs..."},
            ],
        },
        {
            "name": "agent-tool-scenarios",
            "description": "Test cases covering various tool usage patterns",
            "app_type": "agent",
            "source": "upload",
            "examples": [
                {"input": "Schedule a recurring weekly meeting", "expected_output": "Created recurring event..."},
                {"input": "Find and forward the latest invoice email", "expected_output": "Found invoice, forwarding..."},
                {"input": "Cancel all meetings for tomorrow", "expected_output": "Cancelled 3 meetings..."},
                {"input": "Set a reminder for the project deadline", "expected_output": "Reminder set for..."},
            ],
        },
        {
            "name": "frustration-patterns",
            "description": "Test cases derived from user frustration failures",
            "app_type": "simple_chat",
            "source": "failure_analysis",
            "examples": [
                {"input": "This is the third time I'm asking for help!", "expected_output": "Acknowledge frustration, apologize, escalate if needed"},
                {"input": "Your support is useless", "expected_output": "Empathize, offer concrete solution, escalate path"},
                {"input": "I've been waiting 20 minutes for a response", "expected_output": "Apologize for wait, prioritize resolution"},
                {"input": "Nobody seems to understand my problem", "expected_output": "Ask clarifying questions, summarize understanding"},
            ],
        },
        {
            "name": "hallucination-cases",
            "description": "Test cases targeting hallucination detection",
            "app_type": "rag",
            "source": "failure_analysis",
            "examples": [
                {"input": "What's the pricing for the enterprise plan?", "context": "Pricing page content...", "expected_output": "Quote exact pricing from docs"},
                {"input": "List all API endpoints", "context": "API reference...", "expected_output": "Only list documented endpoints"},
                {"input": "What integrations are supported?", "context": "Integrations page...", "expected_output": "Only mention documented integrations"},
            ],
        },
    ]

    for ds_data in demo_datasets:
        dataset = Dataset(
            id=str(uuid.uuid4()),
            name=ds_data["name"],
            description=ds_data.get("description"),
            app_type=ds_data.get("app_type"),
            num_examples=len(ds_data.get("examples", [])),
            source=ds_data.get("source"),
            generation_config=ds_data.get("generation_config"),
            created_at=datetime.utcnow() - timedelta(days=hash(ds_data["name"]) % 7),
        )
        db.add(dataset)
        db.flush()

        for i, ex in enumerate(ds_data.get("examples", [])):
            example = DatasetExample(
                dataset_id=dataset.id,
                input=ex.get("input", ""),
                expected_output=ex.get("expected_output"),
                context=ex.get("context"),
                example_metadata=json.dumps({"index": i}),
            )
            db.add(example)

    db.commit()
    db.close()
    print(f"Seeded {len(demo_runs)} demo runs and {len(demo_datasets)} demo datasets.")


if __name__ == "__main__":
    seed_demo_data()
