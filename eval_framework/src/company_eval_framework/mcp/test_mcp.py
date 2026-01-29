#!/usr/bin/env python3
"""
Simple test script to verify the MCP server implementation.

This script demonstrates how to use the MCP tools programmatically.
Note: In production, these tools would be called through the MCP protocol.
"""

import asyncio
import json
from pathlib import Path

# Import the tool functions directly for testing
from company_eval_framework.mcp.tools import (
    list_eval_suites,
    list_configs,
    validate_config,
    generate_dataset,
    preview_dataset,
    ListConfigsInput,
    ValidateConfigInput,
    GenerateDatasetInput,
    PreviewDatasetInput,
)


async def main():
    print("=" * 70)
    print("MCP Server Test Suite")
    print("=" * 70)
    print()

    # Test 1: List available eval suites
    print("Test 1: Listing evaluation suites...")
    print("-" * 70)
    result = await list_eval_suites()
    data = json.loads(result)
    print(f"Found {data['total']} evaluation suites:")
    for suite in data['suites']:
        print(f"  - {suite['name']}: {suite['description']}")
    print()

    # Test 2: List configurations
    print("Test 2: Listing configurations...")
    print("-" * 70)
    result = await list_configs(ListConfigsInput(directory="examples/configs"))
    data = json.loads(result)
    print(f"Found {data.get('total', 0)} configuration files in examples/configs:")
    for config in data.get('configs', []):
        print(f"  - {config['path']}: {config['app_name']} ({config['app_type']})")
    print()

    # Test 3: Validate a configuration
    print("Test 3: Validating configuration...")
    print("-" * 70)
    config_path = "examples/configs/example_chatbot.yaml"
    if Path(config_path).exists():
        result = await validate_config(ValidateConfigInput(config_path=config_path))
        data = json.loads(result)
        print(f"Configuration valid: {data['valid']}")
        if data.get('errors'):
            print("Errors:")
            for error in data['errors']:
                print(f"  - {error}")
        if data.get('warnings'):
            print("Warnings:")
            for warning in data['warnings']:
                print(f"  - {warning}")
        if data.get('config_summary'):
            print(f"Summary: {data['config_summary']}")
    else:
        print(f"Configuration file not found: {config_path}")
    print()

    # Test 4: Generate a dataset
    print("Test 4: Generating synthetic dataset...")
    print("-" * 70)
    dataset_path = "examples/datasets/test_generated.jsonl"
    Path(dataset_path).parent.mkdir(parents=True, exist_ok=True)
    
    result = await generate_dataset(GenerateDatasetInput(
        output_path=dataset_path,
        num_samples=5,
        app_type="chat"
    ))
    data = json.loads(result)
    if data.get('success'):
        print(f"Generated dataset at: {data['path']}")
        print(f"Number of samples: {data['num_samples']}")
        print("Preview of first sample:")
        if data.get('preview'):
            print(f"  {json.dumps(data['preview'][0], indent=2)}")
    print()

    # Test 5: Preview the dataset
    print("Test 5: Previewing dataset...")
    print("-" * 70)
    if Path(dataset_path).exists():
        result = await preview_dataset(PreviewDatasetInput(
            dataset_path=dataset_path,
            num_rows=3
        ))
        data = json.loads(result)
        print(f"Dataset: {data['path']}")
        print(f"Total rows: {data['total_rows']}")
        print(f"Columns: {', '.join(data['columns'])}")
        print(f"Preview ({len(data['preview_rows'])} rows):")
        for i, row in enumerate(data['preview_rows'], 1):
            print(f"  Row {i}: {json.dumps(row, indent=4)}")
    print()

    print("=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
