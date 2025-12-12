# Evaluation Framework Monorepo

use terminal to run this:

cd /workspaces/arize-evals/example_team_project
source ../.venv/bin/activate

export OPENAI_API_KEY="enter key here"
export AZURE_OPENAI_ENDPOINT="https://visiostandardopenai.openai.azure.com/"
# Optional: match exactly what Azure shows; default is 2024-12-01-preview
export AZURE_OPENAI_API_VERSION="2024-12-01-preview"


# Simple LLM workflow
python run_evaluation.py --config eval_config_simple_llm.yaml

# Single-agent workflow
python run_evaluation.py --config eval_config_agent.yaml
