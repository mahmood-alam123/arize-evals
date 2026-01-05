"""API routes for tracing (LLM calls, tool calls, etc.)."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db, Trace, Span
from ..schemas import (
    TraceCreate,
    TraceDetailResponse,
    TraceListResponse,
    TraceSummaryResponse,
    SpanCreate,
    SpanResponse,
)

router = APIRouter(prefix="/api/traces", tags=["traces"])


@router.get("", response_model=TraceListResponse)
def list_traces(
    project_name: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all traces with optional filtering."""
    query = db.query(Trace).order_by(Trace.start_time.desc())

    if project_name:
        query = query.filter(Trace.project_name == project_name)
    if name:
        query = query.filter(Trace.name.ilike(f"%{name}%"))
    if status:
        query = query.filter(Trace.status == status)

    total = query.count()
    traces = query.offset(offset).limit(limit).all()

    # Get span counts for each trace
    trace_summaries = []
    for trace in traces:
        span_count = db.query(func.count(Span.id)).filter(Span.trace_id == trace.id).scalar()
        trace_summaries.append(
            TraceSummaryResponse(
                id=trace.id,
                name=trace.name,
                project_name=trace.project_name,
                start_time=trace.start_time,
                end_time=trace.end_time,
                duration_ms=trace.duration_ms,
                status=trace.status,
                total_tokens=trace.total_tokens,
                total_cost=trace.total_cost,
                span_count=span_count,
                created_at=trace.created_at,
            )
        )

    return TraceListResponse(
        traces=trace_summaries,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{trace_id}", response_model=TraceDetailResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a trace including all spans."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    return TraceDetailResponse(
        id=trace.id,
        name=trace.name,
        project_name=trace.project_name,
        start_time=trace.start_time,
        end_time=trace.end_time,
        duration_ms=trace.duration_ms,
        status=trace.status,
        input=trace.input,
        output=trace.output,
        metadata=trace.metadata,
        total_tokens=trace.total_tokens,
        total_cost=trace.total_cost,
        error_message=trace.error_message,
        created_at=trace.created_at,
        spans=[SpanResponse.model_validate(s) for s in trace.spans],
    )


@router.post("", response_model=TraceDetailResponse, status_code=201)
def create_trace(trace_data: TraceCreate, db: Session = Depends(get_db)):
    """Create a new trace with optional spans."""
    trace = Trace(
        id=str(uuid.uuid4()),
        name=trace_data.name,
        project_name=trace_data.project_name,
        start_time=trace_data.start_time,
        end_time=trace_data.end_time,
        duration_ms=trace_data.duration_ms,
        status=trace_data.status,
        input=trace_data.input,
        output=trace_data.output,
        metadata=trace_data.metadata,
        total_tokens=trace_data.total_tokens,
        total_cost=trace_data.total_cost,
        error_message=trace_data.error_message,
    )
    db.add(trace)
    db.flush()

    # Add spans
    for span_data in trace_data.spans:
        span = Span(
            id=str(uuid.uuid4()),
            trace_id=trace.id,
            parent_span_id=span_data.parent_span_id,
            name=span_data.name,
            span_type=span_data.span_type,
            start_time=span_data.start_time,
            end_time=span_data.end_time,
            duration_ms=span_data.duration_ms,
            status=span_data.status,
            input=span_data.input,
            output=span_data.output,
            model=span_data.model,
            provider=span_data.provider,
            prompt_tokens=span_data.prompt_tokens,
            completion_tokens=span_data.completion_tokens,
            total_tokens=span_data.total_tokens,
            cost=span_data.cost,
            tool_name=span_data.tool_name,
            tool_args=span_data.tool_args,
            error_message=span_data.error_message,
            metadata=span_data.metadata,
        )
        db.add(span)

    db.commit()
    db.refresh(trace)

    return TraceDetailResponse(
        id=trace.id,
        name=trace.name,
        project_name=trace.project_name,
        start_time=trace.start_time,
        end_time=trace.end_time,
        duration_ms=trace.duration_ms,
        status=trace.status,
        input=trace.input,
        output=trace.output,
        metadata=trace.metadata,
        total_tokens=trace.total_tokens,
        total_cost=trace.total_cost,
        error_message=trace.error_message,
        created_at=trace.created_at,
        spans=[SpanResponse.model_validate(s) for s in trace.spans],
    )


@router.post("/{trace_id}/spans", response_model=SpanResponse, status_code=201)
def add_span(trace_id: str, span_data: SpanCreate, db: Session = Depends(get_db)):
    """Add a span to an existing trace."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    span = Span(
        id=str(uuid.uuid4()),
        trace_id=trace_id,
        parent_span_id=span_data.parent_span_id,
        name=span_data.name,
        span_type=span_data.span_type,
        start_time=span_data.start_time,
        end_time=span_data.end_time,
        duration_ms=span_data.duration_ms,
        status=span_data.status,
        input=span_data.input,
        output=span_data.output,
        model=span_data.model,
        provider=span_data.provider,
        prompt_tokens=span_data.prompt_tokens,
        completion_tokens=span_data.completion_tokens,
        total_tokens=span_data.total_tokens,
        cost=span_data.cost,
        tool_name=span_data.tool_name,
        tool_args=span_data.tool_args,
        error_message=span_data.error_message,
        metadata=span_data.metadata,
    )
    db.add(span)
    db.commit()
    db.refresh(span)

    return SpanResponse.model_validate(span)


@router.patch("/{trace_id}", response_model=TraceDetailResponse)
def update_trace(
    trace_id: str,
    end_time: Optional[str] = None,
    duration_ms: Optional[float] = None,
    status: Optional[str] = None,
    output: Optional[str] = None,
    total_tokens: Optional[int] = None,
    total_cost: Optional[float] = None,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Update a trace (typically to mark it as completed)."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    if end_time is not None:
        from datetime import datetime
        trace.end_time = datetime.fromisoformat(end_time)
    if duration_ms is not None:
        trace.duration_ms = duration_ms
    if status is not None:
        trace.status = status
    if output is not None:
        trace.output = output
    if total_tokens is not None:
        trace.total_tokens = total_tokens
    if total_cost is not None:
        trace.total_cost = total_cost
    if error_message is not None:
        trace.error_message = error_message

    db.commit()
    db.refresh(trace)

    return TraceDetailResponse(
        id=trace.id,
        name=trace.name,
        project_name=trace.project_name,
        start_time=trace.start_time,
        end_time=trace.end_time,
        duration_ms=trace.duration_ms,
        status=trace.status,
        input=trace.input,
        output=trace.output,
        metadata=trace.metadata,
        total_tokens=trace.total_tokens,
        total_cost=trace.total_cost,
        error_message=trace.error_message,
        created_at=trace.created_at,
        spans=[SpanResponse.model_validate(s) for s in trace.spans],
    )


@router.delete("/{trace_id}", status_code=204)
def delete_trace(trace_id: str, db: Session = Depends(get_db)):
    """Delete a trace and all its spans."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")

    db.delete(trace)
    db.commit()
    return None
