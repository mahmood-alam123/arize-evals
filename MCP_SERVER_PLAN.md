# MCP Server Implementation Plan

## Overview

Add an MCP (Model Context Protocol) server to the eval framework, enabling AI assistants to run evaluations, analyze results, and manage datasets conversationally.

## Package Structure

```
eval_framework/src/company_eval_framework/
├── mcp/                    # NEW
│   ├── __init__.py
│   ├── server.py           # FastMCP server setup
│   ├── tools.py            # Tool implementations (8 tools)
│   ├── resources.py        # MCP resources for configs/datasets
│   └── types.py            # Pydantic response models
```

## MCP Tools

### Core Tools
| Tool | Description |
|------|-------------|
| `run_evaluation` | Execute full evaluation pipeline from config file |
| `list_configs` | Discover available eval configs in a directory |
| `list_eval_suites` | List available suites (basic_chat, basic_rag, agent, multi_agent) |
| `validate_config` | Validate config without running |

### Analysis Tools
| Tool | Description |
|------|-------------|
| `get_evaluation_results` | Get detailed results from last evaluation |
| `analyze_failures` | Deep-dive into failure patterns with examples |

### Dataset Tools
| Tool | Description |
|------|-------------|
| `generate_dataset` | Generate synthetic test datasets |
| `preview_dataset` | Preview contents of a dataset file |

## MCP Resources

| Resource URI | Description |
|--------------|-------------|
| `eval://config/{path}` | Read config file contents (YAML) |
| `eval://dataset/{path}` | Read dataset sample (first 10 rows of JSONL) |
| `eval://results/latest` | Read results from the most recent evaluation run |

## Key Type Definitions

```python
class EvaluationResult(BaseModel):
    passed: bool
    app_name: str
    app_type: str
    eval_suite: str
    dataset_size: int
    metrics: list[MetricResult]
    failure_analysis: Optional[FailureAnalysis]
    execution_time_seconds: float

class MetricResult(BaseModel):
    name: str
    mean_score: float
    threshold_type: Optional[Literal["min", "max"]]
    threshold_value: Optional[float]
    passed: bool
```

## Installation Changes

**pyproject.toml:**
```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0.0"]

[project.scripts]
company-eval-mcp = "company_eval_framework.mcp.server:main"
```

**Usage:**
```bash
# Install with MCP support
pip install -e "eval_framework/[mcp]"

# Run MCP server
company-eval-mcp
```

**Claude Code config (~/.claude.json or similar):**
```json
{
  "mcpServers": {
    "company-eval": {
      "command": "company-eval-mcp"
    }
  }
}
```

## Implementation Steps

### Step 1: Create MCP module structure
- Create `mcp/` directory with `__init__.py`
- Create `types.py` with Pydantic models

### Step 2: Implement server.py
- Set up FastMCP server instance
- Configure stdio transport (default for CLI tools)
- Add entry point registration

### Step 3: Implement core tools
- `run_evaluation` - wrap `run_ci_evaluation()` with progress reporting
- `list_configs` - glob for config files, parse and summarize
- `list_eval_suites` - return static suite definitions
- `validate_config` - load config with error catching

### Step 4: Implement analysis tools
- Add result caching mechanism to store last run results
- `get_evaluation_results` - return cached detailed results
- `analyze_failures` - filter and format failure examples

### Step 5: Implement dataset tools
- `generate_dataset` - wrap existing CLI logic
- `preview_dataset` - read JSONL and return sample rows

### Step 6: Implement resources (resources.py)
- `eval://config/{path}` - read and return YAML config contents
- `eval://dataset/{path}` - read first 10 rows of JSONL dataset
- `eval://results/latest` - return cached results from last run

### Step 7: Update package configuration
- Add `mcp` optional dependency to pyproject.toml
- Add `company-eval-mcp` entry point
- Update `__init__.py` exports

## Files to Create/Modify

| File | Action |
|------|--------|
| `eval_framework/src/company_eval_framework/mcp/__init__.py` | Create |
| `eval_framework/src/company_eval_framework/mcp/types.py` | Create |
| `eval_framework/src/company_eval_framework/mcp/server.py` | Create |
| `eval_framework/src/company_eval_framework/mcp/tools.py` | Create |
| `eval_framework/src/company_eval_framework/mcp/resources.py` | Create |
| `eval_framework/pyproject.toml` | Modify (add mcp dep + entry point) |

## Progress Reporting

For long-running evaluations, use MCP Context for progress:
```python
await ctx.report_progress(progress=0.3, total=1.0, message="Running adapter")
```

## Error Handling

- Config not found → Clear error message with path
- Adapter import fails → Show module path and ImportError
- API key missing → Check env vars early, suggest resolution
- Evaluation fails → Return partial results with error details
