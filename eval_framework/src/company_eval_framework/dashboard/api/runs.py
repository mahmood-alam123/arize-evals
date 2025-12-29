"""
API routes for evaluation runs.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import get_database
from ..schemas import (
    FailureSummaryResponse,
    RunCreate,
    RunCreatedResponse,
    RunDetailResponse,
    RunListResponse,
    RunSummaryResponse,
    MetricResponse,
    TestCaseResponse,
    TestCaseScoreResponse,
    FailureResponse,
)

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=RunListResponse)
def list_runs(
    app_name: Optional[str] = Query(None, description="Filter by app name"),
    limit: int = Query(50, ge=1, le=100, description="Number of runs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """List all evaluation runs, most recent first."""
    db = get_database()
    runs = db.get_runs(app_name=app_name, limit=limit, offset=offset)
    total = db.get_run_count(app_name=app_name)

    return RunListResponse(
        runs=[RunSummaryResponse.model_validate(r) for r in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str):
    """Get detailed information about a specific run."""
    db = get_database()
    run = db.get_run(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # Convert to response model with nested data
    return RunDetailResponse(
        id=run.id,
        app_name=run.app_name,
        app_type=run.app_type,
        eval_suite=run.eval_suite,
        dataset_size=run.dataset_size,
        passed=run.passed,
        started_at=run.started_at,
        finished_at=run.finished_at,
        duration_seconds=run.duration_seconds,
        git_branch=run.git_branch,
        git_commit=run.git_commit,
        config_path=run.config_path,
        created_at=run.created_at,
        metrics=[MetricResponse.model_validate(m) for m in run.metrics],
        test_cases=[
            TestCaseResponse(
                id=tc.id,
                conversation_id=tc.conversation_id,
                input=tc.input,
                output=tc.output,
                context=tc.context,
                scores=[TestCaseScoreResponse.model_validate(s) for s in tc.scores],
                failure=FailureResponse.model_validate(tc.failure) if tc.failure else None,
            )
            for tc in run.test_cases
        ],
    )


@router.post("", response_model=RunCreatedResponse, status_code=201)
def create_run(run_data: RunCreate):
    """Create a new evaluation run with all its data."""
    db = get_database()

    # Create the run
    run = db.create_run(
        app_name=run_data.app_name,
        app_type=run_data.app_type,
        eval_suite=run_data.eval_suite,
        dataset_size=run_data.dataset_size,
        passed=run_data.passed,
        started_at=run_data.started_at,
        finished_at=run_data.finished_at,
        duration_seconds=run_data.duration_seconds,
        git_branch=run_data.git_branch,
        git_commit=run_data.git_commit,
        config_path=run_data.config_path,
    )

    # Add metrics
    if run_data.metrics:
        db.add_metrics(
            run.id,
            [m.model_dump() for m in run_data.metrics],
        )

    # Add test cases
    if run_data.test_cases:
        db.add_test_cases(
            run.id,
            [tc.model_dump() for tc in run_data.test_cases],
        )

    return RunCreatedResponse(id=run.id)


@router.get("/{run_id}/failures/summary", response_model=FailureSummaryResponse)
def get_failure_summary(run_id: str):
    """Get failure type distribution for a run."""
    db = get_database()

    # Verify run exists
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    summary = db.get_failure_summary(run_id)
    return FailureSummaryResponse(**summary)
