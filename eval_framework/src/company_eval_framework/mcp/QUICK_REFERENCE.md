# MCP Server Quick Reference

## Installation & Setup

```bash
# Install
pip install -e ".[mcp]"

# Run server
company-eval-mcp

# Configure Claude Code (~/.claude.json)
{
  "mcpServers": {
    "company-eval": {"command": "company-eval-mcp"}
  }
}
```

## Tools Quick Reference

### Core Tools

| Tool | Input | Purpose |
|------|-------|---------|
| `run_evaluation` | config_path | Execute full evaluation pipeline |
| `list_configs` | directory? | Find available configs |
| `list_eval_suites` | - | Show available eval suites |
| `validate_config` | config_path | Validate config without running |

### Analysis Tools

| Tool | Input | Purpose |
|------|-------|---------|
| `get_evaluation_results` | - | Get last evaluation results |
| `analyze_failures` | - | Deep-dive into failures |

### Dataset Tools

| Tool | Input | Purpose |
|------|-------|---------|
| `generate_dataset` | output_path, num_samples, app_type | Create synthetic dataset |
| `preview_dataset` | dataset_path, num_rows? | Preview dataset contents |

## Resources Quick Reference

| URI | Returns |
|-----|---------|
| `eval://config/{path}` | Raw YAML config |
| `eval://dataset/{path}` | First 10 dataset rows |
| `eval://results/latest` | Last evaluation results |

## Tool Call Examples

### Run Evaluation
```json
{
  "config_path": "configs/my_app.yaml"
}
```

### List Configs
```json
{
  "directory": "./configs"
}
```

### Generate Dataset
```json
{
  "output_path": "datasets/test.jsonl",
  "num_samples": 50,
  "app_type": "chat"
}
```

### Preview Dataset
```json
{
  "dataset_path": "datasets/test.jsonl",
  "num_rows": 5
}
```

## Configuration File Template

```yaml
app_name: "My App"
app_type: "chat"  # chat|rag|agent|multi_agent
eval_suite: "basic_chat"  # basic_chat|basic_rag|agent|multi_agent
adapter_module: "my.module.adapter"
dataset_path: "datasets/data.jsonl"

metrics:
  - name: "accuracy"
    threshold_type: "min"
    threshold_value: 0.8
```

## Evaluation Suites

| Suite | App Types | Metrics |
|-------|-----------|---------|
| basic_chat | chat, chatbot | response_quality, coherence, relevance |
| basic_rag | rag, qa | factual_accuracy, context_usage, citation_quality |
| agent | agent, assistant | task_completion, tool_usage, reasoning_quality |
| multi_agent | multi_agent, orchestrator | coordination, task_distribution, collective_performance |

## Common Workflows

### 1. First-Time Setup
```
1. list_eval_suites              → See available options
2. generate_dataset              → Create test data
3. validate_config               → Check config
4. run_evaluation                → Execute evaluation
5. get_evaluation_results        → View results
```

### 2. Debug Failed Evaluation
```
1. run_evaluation                → Run evaluation
2. analyze_failures              → See what failed
3. preview_dataset               → Check dataset
4. validate_config               → Verify config
```

### 3. Explore Existing Setup
```
1. list_configs                  → Find configs
2. validate_config               → Check a config
3. preview_dataset               → Look at data
4. run_evaluation                → Execute
```

## Error Messages

All tools return actionable errors:

```json
{
  "error": "Description of what went wrong",
  "suggestion": "How to fix it"
}
```

## Progress Reporting

Long operations report progress:
- 0.1 - Loading configuration
- 0.2 - Validating configuration
- 0.5 - Running adapter
- 0.7 - Computing metrics
- 1.0 - Complete

## File Paths

### Relative Paths
```python
"configs/my_app.yaml"           # Relative to current dir
"datasets/test.jsonl"           # Relative to current dir
```

### Absolute Paths
```python
"/path/to/configs/my_app.yaml"  # Absolute path
```

## Testing

```bash
# Manual test
python test_mcp.py

# MCP Inspector
npx @modelcontextprotocol/inspector company-eval-mcp
```

## Response Formats

### Success Response
```json
{
  "passed": true,
  "metrics": [...],
  "execution_time_seconds": 5.2
}
```

### Error Response
```json
{
  "error": "Error message",
  "suggestion": "Fix suggestion"
}
```

### List Response
```json
{
  "items": [...],
  "total": 5
}
```

## Key Constraints

| Constraint | Value |
|------------|-------|
| Max dataset samples | 1000 |
| Max preview rows | 50 |
| Default preview rows | 10 |
| Supported config formats | .yaml, .yml |
| Supported dataset format | .jsonl |

## Module Structure

```
company_eval_framework.mcp
  ├── server      # FastMCP setup
  ├── tools       # Tool implementations
  ├── resources   # Resource handlers
  └── types       # Pydantic models
```

## Tool Annotations

| Tool | Read Only | Destructive | Idempotent | Open World |
|------|-----------|-------------|------------|------------|
| run_evaluation | ❌ | ❌ | ❌ | ✅ |
| list_configs | ✅ | ❌ | ✅ | ❌ |
| list_eval_suites | ✅ | ❌ | ✅ | ❌ |
| validate_config | ✅ | ❌ | ✅ | ❌ |
| get_evaluation_results | ✅ | ❌ | ✅ | ❌ |
| analyze_failures | ✅ | ❌ | ✅ | ❌ |
| generate_dataset | ❌ | ❌ | ❌ | ❌ |
| preview_dataset | ✅ | ❌ | ✅ | ❌ |
