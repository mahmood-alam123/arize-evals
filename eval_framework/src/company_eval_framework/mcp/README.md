# Company Eval Framework MCP Server

An MCP (Model Context Protocol) server that enables AI assistants to run evaluations, analyze results, and manage datasets conversationally.

## Features

- **Run Evaluations**: Execute full evaluation pipelines from configuration files
- **Configuration Management**: Discover, validate, and manage evaluation configs
- **Result Analysis**: Get detailed results and analyze failure patterns
- **Dataset Tools**: Generate synthetic datasets and preview existing ones
- **Resource Access**: Access configs, datasets, and results through MCP resources

## Installation

### Standard Installation

```bash
pip install -e .
```

### With MCP Support

```bash
pip install -e ".[mcp]"
```

### For Development

```bash
pip install -e ".[mcp,dev]"
```

## Usage

### Running the MCP Server

```bash
company-eval-mcp
```

The server runs using stdio transport, making it suitable for integration with MCP clients like Claude Code.

### Configuration for MCP Clients

Add the server to your MCP client configuration. For Claude Code, add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "company-eval": {
      "command": "company-eval-mcp"
    }
  }
}
```

## Available Tools

### Core Tools

#### `run_evaluation`
Execute a full evaluation pipeline from a configuration file.

**Parameters:**
- `config_path` (str): Path to the evaluation configuration YAML file

**Returns:** JSON with evaluation results including metrics, pass/fail status, and execution time.

**Example:**
```json
{
  "config_path": "configs/my_app.yaml"
}
```

#### `list_configs`
Discover available evaluation configurations in a directory.

**Parameters:**
- `directory` (str, optional): Directory to search (default: current directory)

**Returns:** JSON list of configuration summaries.

**Example:**
```json
{
  "directory": "./configs"
}
```

#### `list_eval_suites`
List available evaluation suites with their descriptions.

**Parameters:** None

**Returns:** JSON list of evaluation suites with descriptions, typical app types, and metrics evaluated.

#### `validate_config`
Validate an evaluation configuration without running it.

**Parameters:**
- `config_path` (str): Path to the configuration file to validate

**Returns:** JSON with validation results, errors, and warnings.

**Example:**
```json
{
  "config_path": "configs/my_app.yaml"
}
```

### Analysis Tools

#### `get_evaluation_results`
Get detailed results from the most recent evaluation run.

**Parameters:** None

**Returns:** JSON with complete evaluation results from the last run.

#### `analyze_failures`
Deep-dive into failure patterns from the last evaluation.

**Parameters:** None

**Returns:** JSON with failure analysis including patterns, examples, and statistics.

### Dataset Tools

#### `generate_dataset`
Generate a synthetic test dataset for evaluation.

**Parameters:**
- `output_path` (str): Path where the dataset should be saved
- `num_samples` (int, optional): Number of samples to generate (default: 10, max: 1000)
- `app_type` (str, optional): Type of app (default: "chat")

**Returns:** JSON with dataset path and preview of generated samples.

**Example:**
```json
{
  "output_path": "datasets/test_data.jsonl",
  "num_samples": 50,
  "app_type": "rag"
}
```

#### `preview_dataset`
Preview the contents of a dataset file.

**Parameters:**
- `dataset_path` (str): Path to the dataset file
- `num_rows` (int, optional): Number of rows to preview (default: 10, max: 50)

**Returns:** JSON with dataset preview, column names, and total row count.

**Example:**
```json
{
  "dataset_path": "datasets/test_data.jsonl",
  "num_rows": 5
}
```

## Available Resources

Resources provide read-only access to data through URI templates.

### `eval://config/{path}`
Access evaluation configuration files.

**Example:** `eval://config/my_app.yaml`

**Returns:** Raw YAML contents of the configuration file.

### `eval://dataset/{path}`
Access dataset files with automatic preview.

**Example:** `eval://dataset/datasets/test_data.jsonl`

**Returns:** JSON preview of the first 10 rows from the dataset.

### `eval://results/latest`
Access results from the most recent evaluation run.

**Example:** `eval://results/latest`

**Returns:** Cached evaluation results from the last run.

## Configuration File Format

Evaluation configuration files are YAML files with the following structure:

```yaml
# Required fields
app_name: "My Application"
app_type: "chat"  # or "rag", "agent", "multi_agent"
eval_suite: "basic_chat"  # or "basic_rag", "agent", "multi_agent"
adapter_module: "my_package.adapters.my_adapter"

# Optional but recommended
dataset_path: "datasets/test_data.jsonl"
metrics:
  - name: "accuracy"
    threshold_type: "min"
    threshold_value: 0.8
  - name: "response_time"
    threshold_type: "max"
    threshold_value: 2.0
```

## Evaluation Suites

| Suite | Description | App Types | Metrics |
|-------|-------------|-----------|---------|
| `basic_chat` | Conversational AI apps | chat, chatbot | response_quality, coherence, relevance |
| `basic_rag` | Retrieval-augmented generation | rag, qa | factual_accuracy, context_usage, citation_quality |
| `agent` | Autonomous agent systems | agent, assistant | task_completion, tool_usage, reasoning_quality |
| `multi_agent` | Multi-agent collaboration | multi_agent, orchestrator | coordination, task_distribution, collective_performance |

## Architecture

The MCP server is built using the FastMCP framework and follows best practices for MCP server development:

### Project Structure

```
eval_framework/src/company_eval_framework/
├── mcp/
│   ├── __init__.py          # Module exports
│   ├── server.py            # FastMCP server setup & tool registration
│   ├── tools.py             # Tool implementations
│   ├── resources.py         # MCP resource handlers
│   └── types.py             # Pydantic response models
```

### Key Components

- **server.py**: Initializes the FastMCP server and registers all tools and resources
- **tools.py**: Implements the business logic for each tool with proper error handling
- **resources.py**: Provides resource access for configs, datasets, and results
- **types.py**: Defines Pydantic models for structured responses

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/
```

### Testing the MCP Server

You can test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector company-eval-mcp
```

## Error Handling

All tools implement comprehensive error handling:

- Clear, actionable error messages
- Suggestions for resolution
- Proper validation of inputs
- Graceful handling of missing files and invalid configurations

## Progress Reporting

Long-running operations (like `run_evaluation`) report progress through the MCP context:

```python
await ctx.report_progress(0.5, "Running adapter on dataset...")
```

This allows MCP clients to show progress indicators to users.

## Contributing

When adding new tools or resources:

1. Define input models in `tools.py` using Pydantic
2. Implement the tool function with proper error handling
3. Register the tool in `server.py` with appropriate annotations
4. Add comprehensive docstrings with parameter descriptions
5. Update this README with the new functionality

## License

See LICENSE file for details.
