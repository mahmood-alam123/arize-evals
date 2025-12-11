# Evaluation Framework Monorepo

use terminal to run this:

cd example_team_project
source ../.venv/bin/activate
export OPENAI_API_KEY="your-real-key"

# Simple LLM workflow
python run_evaluation.py --config eval_config_simple_llm.yaml

# Single-agent workflow
python run_evaluation.py --config eval_config_agent.yaml
