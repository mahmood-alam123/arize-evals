# MCP Server Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client                                │
│                    (Claude Code, etc.)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ stdio transport
                           │ (JSON-RPC)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastMCP Server                                │
│                  (company-eval-mcp)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                    Tool Registry                       │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  Core Tools (4)                                       │     │
│  │  • run_evaluation          • list_configs             │     │
│  │  • list_eval_suites        • validate_config          │     │
│  │                                                        │     │
│  │  Analysis Tools (2)                                   │     │
│  │  • get_evaluation_results  • analyze_failures         │     │
│  │                                                        │     │
│  │  Dataset Tools (2)                                    │     │
│  │  • generate_dataset        • preview_dataset          │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                  Resource Registry                     │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  • eval://config/{path}                               │     │
│  │  • eval://dataset/{path}                              │     │
│  │  • eval://results/latest                              │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  tools.py                                                        │
│  • Tool implementations                                          │
│  • Input validation (Pydantic)                                   │
│  • Error handling                                                │
│  • Helper functions                                              │
│                                                                   │
│  resources.py                                                    │
│  • Resource handlers                                             │
│  • File reading                                                  │
│  • Data formatting                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  File System                                                     │
│  • Configuration files (YAML)                                    │
│  • Dataset files (JSONL)                                         │
│  • Results cache (in-memory)                                     │
│                                                                   │
│  External Systems                                                │
│  • Eval framework CI functions                                   │
│  • App adapters                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Tool Flow Example: Running an Evaluation

```
┌──────────────┐
│ MCP Client   │
│ sends tool   │
│ call request │
└──────┬───────┘
       │
       │ {"tool": "run_evaluation", "params": {"config_path": "..."}}
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ FastMCP Server (server.py)                                   │
│ • Receives tool call                                         │
│ • Routes to run_evaluation_tool()                            │
│ • Validates input using RunEvaluationInput (Pydantic)        │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ Validated params + MCP context
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Tool Implementation (tools.py)                               │
│                                                               │
│ 1. Load config (YAML)                                        │
│    └─ report_progress(0.1, "Loading config...")             │
│                                                               │
│ 2. Validate required fields                                  │
│    └─ report_progress(0.2, "Validating...")                 │
│                                                               │
│ 3. Execute evaluation                                        │
│    └─ report_progress(0.5, "Running adapter...")            │
│    └─ report_progress(0.7, "Computing metrics...")          │
│                                                               │
│ 4. Build result object (Pydantic)                            │
│    └─ EvaluationResult(passed=..., metrics=...)             │
│                                                               │
│ 5. Cache result globally                                     │
│    └─ _last_evaluation_result = result.model_dump()         │
│                                                               │
│ 6. Return JSON response                                      │
│    └─ report_progress(1.0, "Complete!")                     │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ JSON result
       │
       ▼
┌──────────────────┐
│ MCP Client       │
│ displays results │
│ to user          │
└──────────────────┘
```

## Data Flow: Resource Access

```
┌──────────────┐
│ MCP Client   │
│ reads        │
│ resource     │
└──────┬───────┘
       │
       │ {"resource": "eval://config/my_app.yaml"}
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ FastMCP Server (server.py)                                   │
│ • Receives resource request                                  │
│ • Matches URI template: eval://config/{path}                 │
│ • Extracts path parameter                                    │
│ • Routes to config_resource()                                │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ path = "my_app.yaml"
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Resource Handler (resources.py)                              │
│                                                               │
│ get_config_resource(path):                                   │
│   1. Resolve file path                                       │
│   2. Check if exists                                         │
│   3. Read file contents                                      │
│   4. Return raw YAML                                         │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ YAML content
       │
       ▼
┌──────────────────┐
│ MCP Client       │
│ receives YAML    │
│ content          │
└──────────────────┘
```

## Module Dependencies

```
server.py
  ├─ imports → tools.py
  │              ├─ uses → types.py (Pydantic models)
  │              └─ depends on → yaml, json, pathlib
  │
  └─ imports → resources.py
                 ├─ uses → types.py (indirect)
                 └─ depends on → yaml, json, pathlib

pyproject.toml
  └─ defines → mcp optional dependency
              └─ provides → company-eval-mcp entry point
                            └─ calls → server.main()
```

## Type Hierarchy

```
BaseModel (Pydantic)
  │
  ├─ MetricResult
  │    • name: str
  │    • mean_score: float
  │    • threshold_type: Optional[Literal["min", "max"]]
  │    • threshold_value: Optional[float]
  │    • passed: bool
  │
  ├─ FailureExample
  │    • input_text: str
  │    • expected_output: Optional[str]
  │    • actual_output: str
  │    • failure_reason: str
  │
  ├─ FailureAnalysis
  │    • total_failures: int
  │    • failure_rate: float
  │    • common_patterns: List[str]
  │    • examples: List[FailureExample]
  │
  ├─ EvaluationResult
  │    • passed: bool
  │    • app_name: str
  │    • app_type: str
  │    • eval_suite: str
  │    • dataset_size: int
  │    • metrics: List[MetricResult]
  │    • failure_analysis: Optional[FailureAnalysis]
  │    • execution_time_seconds: float
  │
  ├─ ConfigSummary
  │    • path: str
  │    • app_name: str
  │    • app_type: str
  │    • eval_suite: str
  │    • dataset_path: Optional[str]
  │    • adapter_module: str
  │
  ├─ EvalSuiteInfo
  │    • name: str
  │    • description: str
  │    • typical_app_types: List[str]
  │    • metrics_evaluated: List[str]
  │
  └─ DatasetPreview
       • path: str
       • total_rows: int
       • preview_rows: List[dict]
       • columns: List[str]
```

## Tool Annotation Matrix

| Tool | readOnly | destructive | idempotent | openWorld |
|------|----------|-------------|------------|-----------|
| run_evaluation | ❌ | ❌ | ❌ | ✅ |
| list_configs | ✅ | ❌ | ✅ | ❌ |
| list_eval_suites | ✅ | ❌ | ✅ | ❌ |
| validate_config | ✅ | ❌ | ✅ | ❌ |
| get_evaluation_results | ✅ | ❌ | ✅ | ❌ |
| analyze_failures | ✅ | ❌ | ✅ | ❌ |
| generate_dataset | ❌ | ❌ | ❌ | ❌ |
| preview_dataset | ✅ | ❌ | ✅ | ❌ |

Legend:
- ✅ = True (hint applies)
- ❌ = False (hint does not apply)

## Error Handling Strategy

```
┌─────────────────────────────────────────────────┐
│              Tool Called                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Input Valid?  │
         └───────┬───────┘
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
       YES             NO
         │               │
         │               └─→ Return JSON error
         │                   with suggestion
         ▼
  ┌──────────────┐
  │ Try Execute  │
  └──────┬───────┘
         │
         ▼
  ┌──────────────────┐
  │ Catch Exceptions │
  └──────┬───────────┘
         │
  ┌──────┴──────┐
  │             │
  ▼             ▼
FileNotFound   Other
  │             │
  └─────┬───────┘
        │
        ▼
   Return JSON error
   with context and
   actionable suggestion
```

## Result Caching Pattern

```
Global Variable: _last_evaluation_result

┌──────────────────────────┐
│  run_evaluation          │
│  executes and stores:    │
│  _last_evaluation_result │
│  = result.model_dump()   │
└────────────┬─────────────┘
             │
             │ Result cached
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌──────────┐    ┌──────────┐
│ get_     │    │ analyze_ │
│ results  │    │ failures │
└──────────┘    └──────────┘
    │                 │
    └────────┬────────┘
             │
             ▼
    Read from cache
    and return to user
```

## File Organization

```
eval_framework/
├── src/company_eval_framework/mcp/
│   ├── __init__.py         [Entry point, exports]
│   ├── types.py            [Pydantic models]
│   ├── tools.py            [Business logic]
│   ├── resources.py        [Resource handlers]
│   └── server.py           [FastMCP setup]
│
├── examples/
│   └── configs/
│       └── example_chatbot.yaml
│
├── pyproject.toml          [Package config]
├── README.md               [Full docs]
├── QUICKSTART.md           [Setup guide]
├── IMPLEMENTATION_SUMMARY.md
└── test_mcp.py            [Test suite]
```

## Deployment Model

```
┌────────────────────────────────────────────────┐
│            User's Environment                   │
│                                                 │
│  1. Install:                                    │
│     pip install -e ".[mcp]"                     │
│                                                 │
│  2. Configure MCP Client:                       │
│     Add to ~/.claude.json                       │
│                                                 │
│  3. Use:                                        │
│     MCP client spawns process                   │
│     └─→ runs "company-eval-mcp"                │
│         └─→ executes server.main()             │
│             └─→ mcp.run() [stdio transport]    │
│                                                 │
│  4. Communicate:                                │
│     Client ←─ stdio ─→ Server                  │
└────────────────────────────────────────────────┘
```

## Key Design Patterns Used

1. **Dependency Injection**: MCP Context passed to tools
2. **Factory Pattern**: Pydantic models create validated instances
3. **Singleton Pattern**: Global result cache
4. **Strategy Pattern**: Different suite implementations
5. **Template Method**: URI templates for resources
6. **Facade Pattern**: FastMCP abstracts protocol complexity
