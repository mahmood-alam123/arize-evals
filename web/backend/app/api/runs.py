"""API routes for evaluation runs."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db, Run, Metric, TestCase, TestCaseScore, Failure
from ..schemas import (
    RunCreate,
    RunCreatedResponse,
    RunDetailResponse,
    RunListResponse,
    RunSummaryResponse,
    MetricResponse,
    TestCaseResponse,
    TestCaseScoreResponse,
    FailureResponse,
    RunComparisonResponse,
    MetricComparison,
)

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=RunListResponse)
def list_runs(
    app_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all evaluation runs."""
    query = db.query(Run).order_by(Run.started_at.desc())
    if app_name:
        query = query.filter(Run.app_name == app_name)

    total = query.count()
    runs = query.offset(offset).limit(limit).all()

    return RunListResponse(
        runs=[RunSummaryResponse.model_validate(r) for r in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a run."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

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
        total_cost=run.total_cost,
        app_cost=run.app_cost,
        eval_cost=run.eval_cost,
        created_at=run.created_at,
        metrics=[MetricResponse.model_validate(m) for m in run.metrics],
        test_cases=[
            TestCaseResponse(
                id=tc.id,
                conversation_id=tc.conversation_id,
                input=tc.input,
                output=tc.output,
                context=tc.context,
                prompt=tc.prompt,
                trace_id=tc.trace_id,
                scores=[TestCaseScoreResponse.model_validate(s) for s in tc.scores],
                failure=FailureResponse.model_validate(tc.failure) if tc.failure else None,
            )
            for tc in run.test_cases
        ],
    )


@router.post("", response_model=RunCreatedResponse, status_code=201)
def create_run(run_data: RunCreate, db: Session = Depends(get_db)):
    """Create a new evaluation run."""
    import uuid

    run = Run(
        id=str(uuid.uuid4()),
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
        total_cost=run_data.total_cost,
        app_cost=run_data.app_cost,
        eval_cost=run_data.eval_cost,
    )
    db.add(run)
    db.flush()

    # Add metrics
    for m in run_data.metrics:
        metric = Metric(
            run_id=run.id,
            name=m.name,
            mean_score=m.mean_score,
            failure_rate=m.failure_rate,
            threshold_type=m.threshold_type,
            threshold_value=m.threshold_value,
            passed=m.passed,
        )
        db.add(metric)

    # Add test cases
    for tc_data in run_data.test_cases:
        tc = TestCase(
            run_id=run.id,
            conversation_id=tc_data.conversation_id,
            input=tc_data.input,
            output=tc_data.output,
            context=tc_data.context,
            prompt=tc_data.prompt,
            trace_id=tc_data.trace_id,
        )
        db.add(tc)
        db.flush()

        for score in tc_data.scores:
            tc_score = TestCaseScore(
                test_case_id=tc.id,
                metric_name=score.metric_name,
                score=score.score,
                label=score.label,
                explanation=score.explanation,
            )
            db.add(tc_score)

        if tc_data.failure:
            failure = Failure(
                test_case_id=tc.id,
                failure_type=tc_data.failure.failure_type,
                explanation=tc_data.failure.explanation,
            )
            db.add(failure)

    db.commit()
    return RunCreatedResponse(id=run.id)


@router.get("/compare/{run_a_id}/{run_b_id}", response_model=RunComparisonResponse)
def compare_runs(run_a_id: str, run_b_id: str, db: Session = Depends(get_db)):
    """Compare two evaluation runs side-by-side."""
    run_a = db.query(Run).filter(Run.id == run_a_id).first()
    run_b = db.query(Run).filter(Run.id == run_b_id).first()

    if not run_a:
        raise HTTPException(status_code=404, detail=f"Run {run_a_id} not found")
    if not run_b:
        raise HTTPException(status_code=404, detail=f"Run {run_b_id} not found")

    # Build metric comparison
    metrics_a = {m.name: m for m in run_a.metrics}
    metrics_b = {m.name: m for m in run_b.metrics}
    all_metric_names = set(metrics_a.keys()) | set(metrics_b.keys())

    metric_comparisons = []
    improved_count = 0
    regressed_count = 0

    for name in sorted(all_metric_names):
        m_a = metrics_a.get(name)
        m_b = metrics_b.get(name)

        score_a = m_a.mean_score if m_a else 0.0
        score_b = m_b.mean_score if m_b else 0.0
        passed_a = m_a.passed if m_a else False
        passed_b = m_b.passed if m_b else False

        delta = score_b - score_a
        delta_percent = (delta / score_a * 100) if score_a > 0 else None

        # Determine if improved (higher score = better)
        improved = score_b > score_a

        if improved:
            improved_count += 1
        elif score_b < score_a:
            regressed_count += 1

        metric_comparisons.append(
            MetricComparison(
                name=name,
                run_a_score=score_a,
                run_b_score=score_b,
                delta=delta,
                delta_percent=delta_percent,
                run_a_passed=passed_a,
                run_b_passed=passed_b,
                improved=improved,
            )
        )

    summary = {
        "total_metrics": len(metric_comparisons),
        "improved": improved_count,
        "regressed": regressed_count,
        "unchanged": len(metric_comparisons) - improved_count - regressed_count,
        "run_a_passed": run_a.passed,
        "run_b_passed": run_b.passed,
    }

    return RunComparisonResponse(
        run_a=RunSummaryResponse.model_validate(run_a),
        run_b=RunSummaryResponse.model_validate(run_b),
        metrics=metric_comparisons,
        summary=summary,
    )
