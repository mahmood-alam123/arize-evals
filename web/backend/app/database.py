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
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    context = Column(Text, nullable=True)

    run = relationship("Run", back_populates="test_cases")
    scores = relationship("TestCaseScore", back_populates="test_case", cascade="all, delete-orphan")
    failure = relationship("Failure", back_populates="test_case", uselist=False, cascade="all, delete-orphan")

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
