# Quick Start Guide: MCP Server for Eval Framework

This guide will help you set up and start using the MCP server for the evaluation framework.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Installation

### Step 1: Install the Package

Navigate to the `eval_framework` directory and install with MCP support:

```bash
cd eval_framework
pip install -e ".[mcp]"
```

This will install:
- The evaluation framework
- The MCP server (`mcp>=1.0.0`)
- All required dependencies (PyYAML, Pydantic)

### Step 2: Verify Installation

Test that the server is installed correctly:

```bash
company-eval-mcp --help
```

You should see usage information for the MCP server.

## Configuration

### For Claude Code

Add the MCP server to your Claude Code configuration file (`~/.claude.json`):

```json
{
  "mcpServers": {
    "company-eval": {
      "command": "company-eval-mcp"
    }
  }
}
```

### For Other MCP Clients

The server runs using stdio transport, making it compatible with any MCP client that supports this transport method. Consult your client's documentation for how to add custom MCP servers.

## Quick Test

### Test the Server Directly

You can test the server implementation using the provided test script:

```bash
cd eval_framework
python test_mcp.py
```

This will run through all the tools and show you example outputs.

### Test with MCP Inspector

The MCP Inspector is a useful tool for testing MCP servers:

```bash
npx @modelcontextprotocol/inspector company-eval-mcp
```

This will open an interactive interface where you can:
- View all available tools
- Test tool calls with sample inputs
- Inspect resources
- See detailed request/response logs

## Basic Usage Examples

### Example 1: List Available Evaluation Suites

**Tool:** `list_eval_suites`

**Input:** None required

**What it does:** Shows you all available evaluation suites (basic_chat, basic_rag, agent, multi_agent) with descriptions and the metrics they evaluate.

### Example 2: Generate a Test Dataset

**Tool:** `generate_dataset`

**Input:**
```json
{
  "output_path": "my_dataset.jsonl",
  "num_samples": 20,
  "app_type": "chat"
}
```

**What it does:** Creates a synthetic dataset with 20 test cases suitable for a chat application.

### Example 3: Validate a Configuration

**Tool:** `validate_config`

**Input:**
```json
{
  "config_path": "configs/my_app.yaml"
}
```

**What it does:** Checks if your configuration file is valid without running the evaluation.

### Example 4: Run an Evaluation

**Tool:** `run_evaluation`

**Input:**
```json
{
  "config_path": "configs/my_app.yaml"
}
```

**What it does:** Runs a complete evaluation using the specified configuration and returns detailed results.

### Example 5: Analyze Failures

**Tool:** `analyze_failures`

**Input:** None required (uses results from last evaluation)

**What it does:** Provides a detailed breakdown of any failures from the most recent evaluation, including patterns and specific examples.

## Working with Resources

Resources provide read-only access to files and data:

### Access a Configuration File

**URI:** `eval://config/my_app.yaml`

**Returns:** Raw YAML contents of the configuration file

### Preview a Dataset

**URI:** `eval://dataset/datasets/test_data.jsonl`

**Returns:** JSON preview of the first 10 rows

### View Latest Results

**URI:** `eval://results/latest`

**Returns:** Complete results from the most recent evaluation

## Creating Your First Evaluation

### Step 1: Create a Configuration File

Create a YAML file (e.g., `my_app.yaml`):

```yaml
app_name: "My App"
app_type: "chat"
eval_suite: "basic_chat"
adapter_module: "my_package.adapters.my_adapter"
dataset_path: "datasets/my_data.jsonl"

metrics:
  - name: "accuracy"
    threshold_type: "min"
    threshold_value: 0.8
```

### Step 2: Generate or Prepare a Dataset

Use the `generate_dataset` tool to create test data:

```json
{
  "output_path": "datasets/my_data.jsonl",
  "num_samples": 50,
  "app_type": "chat"
}
```

Or prepare your own JSONL file with test cases.

### Step 3: Validate Your Configuration

Before running, validate your setup:

```json
{
  "config_path": "my_app.yaml"
}
```

### Step 4: Run the Evaluation

Execute the evaluation:

```json
{
  "config_path": "my_app.yaml"
}
```

### Step 5: Analyze Results

Check the results and analyze any failures:

1. Use `get_evaluation_results` to see detailed metrics
2. Use `analyze_failures` to understand what went wrong

## Troubleshooting

### Server Won't Start

**Issue:** `command not found: company-eval-mcp`

**Solution:** Make sure you installed with `pip install -e ".[mcp]"` and that your Python scripts directory is in your PATH.

### Tool Returns Error

**Issue:** Tools return errors about missing files or invalid configurations

**Solution:** 
- Use `validate_config` to check your configuration before running
- Ensure all file paths are correct and accessible
- Check that required fields are present in your config

### Import Errors

**Issue:** `ModuleNotFoundError` when running tools

**Solution:**
- Verify you're in the correct directory
- Ensure all dependencies are installed
- Check that the package is installed in editable mode

## Next Steps

- Read the full README.md for detailed API documentation
- Explore the example configurations in `examples/configs/`
- Create your own adapter to evaluate your application
- Integrate the MCP server into your development workflow

## Getting Help

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the example configurations and test scripts
3. Use the MCP Inspector to debug tool calls
4. Examine the error messages - they include suggestions for resolution
