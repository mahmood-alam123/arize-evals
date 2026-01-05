"""API routes for dataset management."""

import uuid
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db, Dataset, DatasetExample, Run, TestCase, Failure
from ..schemas import (
    DatasetCreate,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetSummaryResponse,
    DatasetExampleCreate,
    DatasetExampleResponse,
    DatasetFromRunCreate,
    DatasetGenerateCreate,
    DatasetFromFailuresCreate,
    FailureStatsResponse,
    FailureStatItem,
)

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("", response_model=DatasetListResponse)
def list_datasets(
    app_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all datasets with optional filtering."""
    query = db.query(Dataset).order_by(Dataset.created_at.desc())

    if app_type:
        query = query.filter(Dataset.app_type == app_type)

    total = query.count()
    datasets = query.offset(offset).limit(limit).all()

    return DatasetListResponse(
        datasets=[DatasetSummaryResponse.model_validate(d) for d in datasets],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/by-name/{name}", response_model=DatasetDetailResponse)
def get_dataset_by_name(name: str, db: Session = Depends(get_db)):
    """Get a dataset by its name (for YAML config integration)."""
    dataset = db.query(Dataset).filter(Dataset.name == name).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        source=dataset.source,
        source_run_id=dataset.source_run_id,
        generation_config=dataset.generation_config,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a dataset including all examples."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        source=dataset.source,
        source_run_id=dataset.source_run_id,
        generation_config=dataset.generation_config,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.post("", response_model=DatasetDetailResponse, status_code=201)
def create_dataset(dataset_data: DatasetCreate, db: Session = Depends(get_db)):
    """Create a new dataset with examples."""
    # Check if name already exists
    existing = db.query(Dataset).filter(Dataset.name == dataset_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Dataset '{dataset_data.name}' already exists")

    dataset = Dataset(
        id=str(uuid.uuid4()),
        name=dataset_data.name,
        description=dataset_data.description,
        app_type=dataset_data.app_type,
        num_examples=len(dataset_data.examples),
    )
    db.add(dataset)
    db.flush()

    # Add examples
    for example_data in dataset_data.examples:
        example = DatasetExample(
            dataset_id=dataset.id,
            input=example_data.input,
            expected_output=example_data.expected_output,
            context=example_data.context,
            metadata=example_data.metadata,
        )
        db.add(example)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.post("/{dataset_id}/examples", response_model=DatasetExampleResponse, status_code=201)
def add_example(dataset_id: str, example_data: DatasetExampleCreate, db: Session = Depends(get_db)):
    """Add an example to an existing dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    example = DatasetExample(
        dataset_id=dataset_id,
        input=example_data.input,
        expected_output=example_data.expected_output,
        context=example_data.context,
        metadata=example_data.metadata,
    )
    db.add(example)

    # Update example count
    dataset.num_examples += 1

    db.commit()
    db.refresh(example)

    return DatasetExampleResponse.model_validate(example)


@router.post("/upload", response_model=DatasetDetailResponse, status_code=201)
async def upload_dataset(
    name: str = Query(...),
    description: Optional[str] = Query(None),
    app_type: Optional[str] = Query(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a JSONL file to create a new dataset."""
    # Check if name already exists
    existing = db.query(Dataset).filter(Dataset.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Dataset '{name}' already exists")

    # Read and parse JSONL file
    content = await file.read()
    lines = content.decode("utf-8").strip().split("\n")

    examples = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            examples.append(data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON on line {i+1}: {e}")

    if not examples:
        raise HTTPException(status_code=400, detail="File contains no valid examples")

    # Create dataset
    dataset = Dataset(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        app_type=app_type,
        num_examples=len(examples),
    )
    db.add(dataset)
    db.flush()

    # Add examples
    for data in examples:
        example = DatasetExample(
            dataset_id=dataset.id,
            input=data.get("input", ""),
            expected_output=data.get("expected_output") or data.get("output"),
            context=data.get("context"),
            metadata=json.dumps(data.get("metadata")) if data.get("metadata") else None,
        )
        db.add(example)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete a dataset and all its examples."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    db.delete(dataset)
    db.commit()
    return None


@router.delete("/{dataset_id}/examples/{example_id}", status_code=204)
def delete_example(dataset_id: str, example_id: int, db: Session = Depends(get_db)):
    """Delete an example from a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    example = db.query(DatasetExample).filter(
        DatasetExample.id == example_id,
        DatasetExample.dataset_id == dataset_id
    ).first()
    if not example:
        raise HTTPException(status_code=404, detail=f"Example {example_id} not found")

    db.delete(example)
    dataset.num_examples -= 1
    db.commit()
    return None


@router.get("/{dataset_id}/export")
def export_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Export a dataset as a JSONL file."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    def generate_jsonl():
        for example in dataset.examples:
            record = {"input": example.input}
            if example.expected_output:
                record["expected_output"] = example.expected_output
            if example.context:
                record["context"] = example.context
            if example.example_metadata:
                try:
                    record["metadata"] = json.loads(example.example_metadata)
                except json.JSONDecodeError:
                    record["metadata"] = example.example_metadata
            yield json.dumps(record) + "\n"

    filename = f"{dataset.name.replace(' ', '_')}.jsonl"
    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/from-run", response_model=DatasetDetailResponse, status_code=201)
def create_dataset_from_run(data: DatasetFromRunCreate, db: Session = Depends(get_db)):
    """Create a dataset from a previous run's test cases."""
    # Verify run exists
    run = db.query(Run).filter(Run.id == data.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {data.run_id} not found")

    # Check if name already exists
    existing = db.query(Dataset).filter(Dataset.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Dataset '{data.name}' already exists")

    # Get test cases
    query = db.query(TestCase).filter(TestCase.run_id == data.run_id)
    if data.include_failures_only:
        # Join with Failure to only get failed test cases
        query = query.join(Failure, Failure.test_case_id == TestCase.id)
    test_cases = query.all()

    if not test_cases:
        raise HTTPException(status_code=400, detail="No test cases found for this run")

    # Create dataset
    description = data.description or f"Imported from run '{run.app_name}' on {run.started_at.strftime('%Y-%m-%d')}"
    dataset = Dataset(
        id=str(uuid.uuid4()),
        name=data.name,
        description=description,
        app_type=run.app_type,
        num_examples=len(test_cases),
        source="run_import",
        source_run_id=data.run_id,
    )
    db.add(dataset)
    db.flush()

    # Create examples from test cases
    for tc in test_cases:
        metadata = {}
        if tc.prompt:
            metadata["prompt"] = tc.prompt
        if tc.trace_id:
            metadata["trace_id"] = tc.trace_id

        example = DatasetExample(
            dataset_id=dataset.id,
            input=tc.input,
            expected_output=tc.output,
            context=tc.context,
            example_metadata=json.dumps(metadata) if metadata else None,
        )
        db.add(example)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        source=dataset.source,
        source_run_id=dataset.source_run_id,
        generation_config=dataset.generation_config,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.get("/failure-stats", response_model=FailureStatsResponse)
def get_failure_stats(
    app_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get failure statistics grouped by failure type and app name."""
    # Query failures with run info
    query = db.query(
        Failure.failure_type,
        Run.app_name,
        func.count(Failure.id).label("count")
    ).join(
        TestCase, TestCase.id == Failure.test_case_id
    ).join(
        Run, Run.id == TestCase.run_id
    ).group_by(
        Failure.failure_type, Run.app_name
    )

    if app_name:
        query = query.filter(Run.app_name == app_name)

    results = query.all()

    # Aggregate by failure_type
    stats_map = {}
    for failure_type, app, count in results:
        if failure_type not in stats_map:
            stats_map[failure_type] = {"count": 0, "app_names": set()}
        stats_map[failure_type]["count"] += count
        stats_map[failure_type]["app_names"].add(app)

    stats = [
        FailureStatItem(
            failure_type=ft,
            count=data["count"],
            app_names=list(data["app_names"])
        )
        for ft, data in sorted(stats_map.items(), key=lambda x: -x[1]["count"])
    ]

    return FailureStatsResponse(stats=stats)


@router.post("/from-failures", response_model=DatasetDetailResponse, status_code=201)
def create_dataset_from_failures(data: DatasetFromFailuresCreate, db: Session = Depends(get_db)):
    """Create a dataset targeting specific failure patterns using LLM generation."""
    # Check if name already exists
    existing = db.query(Dataset).filter(Dataset.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Dataset '{data.name}' already exists")

    # Get failure examples
    query = db.query(
        Failure.failure_type,
        TestCase.input,
        TestCase.output,
        Run.app_name,
        Run.app_type
    ).join(
        TestCase, TestCase.id == Failure.test_case_id
    ).join(
        Run, Run.id == TestCase.run_id
    )

    if data.app_name:
        query = query.filter(Run.app_name == data.app_name)
    if data.failure_types:
        query = query.filter(Failure.failure_type.in_(data.failure_types))

    failures = query.all()

    if not failures:
        raise HTTPException(status_code=400, detail="No failures found matching the criteria")

    # Group by failure type
    failure_groups = {}
    app_type = None
    for ft, input_text, output, app, at in failures:
        if ft not in failure_groups:
            failure_groups[ft] = []
        failure_groups[ft].append({"input": input_text, "output": output})
        app_type = app_type or at

    # For now, we'll use the actual failure inputs as examples
    # In a full implementation, this would call an LLM to generate similar inputs
    examples_to_create = []
    for failure_type, examples in failure_groups.items():
        # Take up to num_examples_per_type from each failure type
        for ex in examples[:data.num_examples_per_type]:
            examples_to_create.append({
                "input": ex["input"],
                "expected_output": ex["output"],
                "metadata": {"source_failure_type": failure_type}
            })

    # Create dataset
    generation_config = {
        "method": "failure_extraction",
        "model": data.model,
        "failure_types": list(failure_groups.keys()),
        "app_name": data.app_name,
    }

    dataset = Dataset(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description or f"Dataset targeting failure patterns: {', '.join(failure_groups.keys())}",
        app_type=app_type,
        num_examples=len(examples_to_create),
        source="failure_analysis",
        generation_config=json.dumps(generation_config),
    )
    db.add(dataset)
    db.flush()

    for ex in examples_to_create:
        example = DatasetExample(
            dataset_id=dataset.id,
            input=ex["input"],
            expected_output=ex.get("expected_output"),
            context=ex.get("context"),
            example_metadata=json.dumps(ex.get("metadata")) if ex.get("metadata") else None,
        )
        db.add(example)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        source=dataset.source,
        source_run_id=dataset.source_run_id,
        generation_config=dataset.generation_config,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )


@router.post("/generate", response_model=DatasetDetailResponse, status_code=201)
def generate_synthetic_dataset(data: DatasetGenerateCreate, db: Session = Depends(get_db)):
    """Generate a synthetic dataset using LLM."""
    # Check if name already exists
    existing = db.query(Dataset).filter(Dataset.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Dataset '{data.name}' already exists")

    # Generate examples using LLM
    # For now, we'll create placeholder examples
    # In a full implementation, this would call OpenAI/Anthropic to generate
    config = data.generation_config

    # Placeholder generation - in production this would use an LLM
    generated_examples = []

    # Use example_inputs if provided, otherwise generate placeholders
    if config.example_inputs:
        for i, input_text in enumerate(config.example_inputs[:data.num_examples]):
            generated_examples.append({
                "input": input_text,
                "expected_output": None,  # LLM would generate expected outputs too
            })
    else:
        # Generate placeholder inputs based on app_type
        app_type_prompts = {
            "simple_chat": [
                "How do I get started with your product?",
                "What are your pricing plans?",
                "Can you help me troubleshoot an issue?",
                "How do I contact support?",
                "What features are included?",
            ],
            "rag": [
                "What does the documentation say about authentication?",
                "How do I configure the API rate limits?",
                "What are the best practices for error handling?",
                "Can you explain the data model?",
                "What integrations are supported?",
            ],
            "agent": [
                "Schedule a meeting for tomorrow at 3pm",
                "Find all emails from last week about the project",
                "Create a new task for reviewing the proposal",
                "Search for documents related to Q4 planning",
                "Send a reminder to the team about the deadline",
            ],
            "multi_agent": [
                "Research competitor pricing and create a summary report",
                "Analyze the sales data and generate recommendations",
                "Review the codebase and suggest improvements",
                "Plan the sprint and assign tasks to team members",
                "Investigate the bug and propose a fix",
            ],
        }
        prompts = app_type_prompts.get(data.app_type, app_type_prompts["simple_chat"])
        for i in range(min(data.num_examples, len(prompts) * 4)):
            generated_examples.append({
                "input": prompts[i % len(prompts)] + (f" (variant {i // len(prompts) + 1})" if i >= len(prompts) else ""),
                "expected_output": None,
            })

    # Create dataset
    generation_config_json = {
        "model": config.model,
        "app_description": config.app_description,
        "system_prompt": config.system_prompt,
        "example_inputs": config.example_inputs,
        "temperature": config.temperature,
        "num_requested": data.num_examples,
    }

    dataset = Dataset(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description or f"Synthetic {data.app_type} dataset",
        app_type=data.app_type,
        num_examples=len(generated_examples),
        source="synthetic",
        generation_config=json.dumps(generation_config_json),
    )
    db.add(dataset)
    db.flush()

    for ex in generated_examples:
        example = DatasetExample(
            dataset_id=dataset.id,
            input=ex["input"],
            expected_output=ex.get("expected_output"),
            context=ex.get("context"),
            example_metadata=None,
        )
        db.add(example)

    db.commit()
    db.refresh(dataset)

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        app_type=dataset.app_type,
        num_examples=dataset.num_examples,
        source=dataset.source,
        source_run_id=dataset.source_run_id,
        generation_config=dataset.generation_config,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        examples=[DatasetExampleResponse.model_validate(e) for e in dataset.examples],
    )
