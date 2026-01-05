"""
Database models and operations for the Quality Dashboard.
"""

import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

Base = declarative_base()


class Run(Base):
    """An evaluation run (one per ci-run execution)."""

    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    app_name = Column(String, nullable=False)
    app_type = Column(String, nullable=False)
    eval_suite = Column(String, nullable=False)
    dataset_size = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    git_branch = Column(String, nullable=True)
    git_commit = Column(String, nullable=True)
    config_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Cost tracking (in USD)
    total_cost = Column(Float, nullable=True)  # Total cost of the run
    app_cost = Column(Float, nullable=True)  # Cost of running the app
    eval_cost = Column(Float, nullable=True)  # Cost of running evaluations

    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_runs_app_name", "app_name"),
        Index("idx_runs_started_at", "started_at"),
    )


class Metric(Base):
    """Metric results for a run."""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    name = Column(String, nullable=False)
    mean_score = Column(Float, nullable=False)
    failure_rate = Column(Float, nullable=False)
    threshold_type = Column(String, nullable=True)
    threshold_value = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False)

    run = relationship("Run", back_populates="metrics")

    __table_args__ = (Index("idx_metrics_run_id", "run_id"),)


class TestCase(Base):
    """Individual test case in a run."""

    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    conversation_id = Column(String, nullable=False)
    input = Column(Text, nullable=False)  # User's input/question
    output = Column(Text, nullable=True)  # Model's response
    context = Column(Text, nullable=True)  # RAG context
    prompt = Column(Text, nullable=True)  # Full prompt sent to LLM (system + context + input)
    trace_id = Column(String, ForeignKey("traces.id"), nullable=True)  # Link to trace

    run = relationship("Run", back_populates="test_cases")
    scores = relationship("TestCaseScore", back_populates="test_case", cascade="all, delete-orphan")
    failure = relationship("Failure", back_populates="test_case", uselist=False, cascade="all, delete-orphan")
    trace = relationship("Trace", backref="test_case")

    __table_args__ = (Index("idx_test_cases_run_id", "run_id"),)


class TestCaseScore(Base):
    """Per-metric score for a test case."""

    __tablename__ = "test_case_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    label = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)

    test_case = relationship("TestCase", back_populates="scores")


class Failure(Base):
    """Failure analysis for a test case."""

    __tablename__ = "failures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    failure_type = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)

    test_case = relationship("TestCase", back_populates="failure")


class Trace(Base):
    """A trace represents an end-to-end request through the LLM application."""

    __tablename__ = "traces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "chat_completion", "rag_query"
    project_name = Column(String, nullable=True)  # Group traces by project
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)  # Duration in milliseconds
    status = Column(String, default="running")  # running, completed, error
    input = Column(Text, nullable=True)  # Initial input to the trace
    output = Column(Text, nullable=True)  # Final output of the trace
    trace_metadata = Column(Text, nullable=True)  # JSON metadata
    total_tokens = Column(Integer, nullable=True)
    total_cost = Column(Float, nullable=True)  # USD
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_traces_project_name", "project_name"),
        Index("idx_traces_start_time", "start_time"),
        Index("idx_traces_name", "name"),
    )


class Span(Base):
    """A span represents a single operation within a trace (LLM call, tool call, etc.)."""

    __tablename__ = "spans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String, ForeignKey("traces.id"), nullable=False)
    parent_span_id = Column(String, nullable=True)  # For nested spans
    name = Column(String, nullable=False)  # e.g., "llm_call", "tool_call", "retrieval"
    span_type = Column(String, nullable=False)  # llm, tool, retrieval, chain, agent, custom
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String, default="running")  # running, completed, error

    # Input/Output
    input = Column(Text, nullable=True)  # JSON - messages, query, tool input
    output = Column(Text, nullable=True)  # JSON - response, tool output

    # LLM-specific fields
    model = Column(String, nullable=True)  # e.g., "gpt-4o", "claude-3-opus"
    provider = Column(String, nullable=True)  # openai, anthropic, azure
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)  # USD

    # Tool-specific fields
    tool_name = Column(String, nullable=True)  # Name of the tool called
    tool_args = Column(Text, nullable=True)  # JSON - arguments passed to tool

    # Error handling
    error_message = Column(Text, nullable=True)

    # Metadata
    span_metadata = Column(Text, nullable=True)  # JSON - custom metadata

    trace = relationship("Trace", back_populates="spans")

    __table_args__ = (
        Index("idx_spans_trace_id", "trace_id"),
        Index("idx_spans_span_type", "span_type"),
        Index("idx_spans_parent_span_id", "parent_span_id"),
    )


class Dataset(Base):
    """A dataset for evaluation."""

    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    app_type = Column(String, nullable=True)  # simple_chat, rag, agent, multi_agent
    num_examples = Column(Integer, default=0)
    source = Column(String, nullable=True)  # "upload", "run_import", "synthetic", "failure_analysis"
    source_run_id = Column(String, ForeignKey("runs.id"), nullable=True)
    generation_config = Column(Text, nullable=True)  # JSON: stores LLM generation params
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    examples = relationship("DatasetExample", back_populates="dataset", cascade="all, delete-orphan")
    source_run = relationship("Run", backref="derived_datasets")

    __table_args__ = (Index("idx_datasets_name", "name"),)


class DatasetExample(Base):
    """An example in a dataset."""

    __tablename__ = "dataset_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    input = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # For RAG
    example_metadata = Column(Text, nullable=True)  # JSON

    dataset = relationship("Dataset", back_populates="examples")

    __table_args__ = (Index("idx_dataset_examples_dataset_id", "dataset_id"),)


class IntegrationConfig(Base):
    """Webhook integration configuration for notifications (Slack, Teams)."""

    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_type = Column(String, nullable=False)  # "slack" or "teams"
    webhook_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    notify_on_pass = Column(Boolean, default=False)
    notify_on_fail = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_integration_type", "integration_type"),)


# Database connection
DATABASE_URL = "sqlite:///./eval_results.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
