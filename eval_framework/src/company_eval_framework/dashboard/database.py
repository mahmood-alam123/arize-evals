"""
Database models and operations for the Quality Dashboard.

Uses SQLAlchemy with async SQLite support.
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
    app_type = Column(String, nullable=False)  # simple_chat, rag, agent, multi_agent
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

    # Relationships
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
    threshold_type = Column(String, nullable=True)  # min, max, or NULL
    threshold_value = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False)

    # Relationships
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
    context = Column(Text, nullable=True)  # For RAG

    # Relationships
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
    score = Column(Float, nullable=False)  # 0.0 or 1.0
    label = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)

    # Relationships
    test_case = relationship("TestCase", back_populates="scores")


class Failure(Base):
    """Failure analysis for a test case."""

    __tablename__ = "failures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    failure_type = Column(String, nullable=False)  # hallucination, retrieval_error, etc.
    explanation = Column(Text, nullable=True)

    # Relationships
    test_case = relationship("TestCase", back_populates="failure")


class Database:
    """Database connection and operations manager."""

    def __init__(self, db_path: str = "eval_results.db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    # Run operations

    def create_run(
        self,
        app_name: str,
        app_type: str,
        eval_suite: str,
        dataset_size: int,
        passed: bool,
        started_at: datetime,
        finished_at: Optional[datetime] = None,
        duration_seconds: Optional[float] = None,
        git_branch: Optional[str] = None,
        git_commit: Optional[str] = None,
        config_path: Optional[str] = None,
    ) -> Run:
        """Create a new evaluation run."""
        with self.get_session() as session:
            run = Run(
                app_name=app_name,
                app_type=app_type,
                eval_suite=eval_suite,
                dataset_size=dataset_size,
                passed=passed,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration_seconds,
                git_branch=git_branch,
                git_commit=git_commit,
                config_path=config_path,
            )
            session.add(run)
            session.commit()
            session.refresh(run)
            return run

    def get_runs(
        self,
        app_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Run]:
        """Get list of runs, optionally filtered by app name."""
        with self.get_session() as session:
            query = session.query(Run).order_by(Run.started_at.desc())
            if app_name:
                query = query.filter(Run.app_name == app_name)
            runs = query.offset(offset).limit(limit).all()
            # Detach from session
            session.expunge_all()
            return runs

    def get_run(self, run_id: str) -> Optional[Run]:
        """Get a single run by ID with all related data."""
        with self.get_session() as session:
            run = session.query(Run).filter(Run.id == run_id).first()
            if run:
                # Eagerly load relationships
                _ = run.metrics
                _ = run.test_cases
                for tc in run.test_cases:
                    _ = tc.scores
                    _ = tc.failure
                session.expunge_all()
            return run

    def get_run_count(self, app_name: Optional[str] = None) -> int:
        """Get total count of runs."""
        with self.get_session() as session:
            query = session.query(Run)
            if app_name:
                query = query.filter(Run.app_name == app_name)
            return query.count()

    # Metric operations

    def add_metrics(self, run_id: str, metrics: list[dict]) -> list[Metric]:
        """Add metrics to a run."""
        with self.get_session() as session:
            metric_objects = []
            for m in metrics:
                metric = Metric(
                    run_id=run_id,
                    name=m["name"],
                    mean_score=m["mean_score"],
                    failure_rate=m.get("failure_rate", 1.0 - m["mean_score"]),
                    threshold_type=m.get("threshold_type"),
                    threshold_value=m.get("threshold_value"),
                    passed=m["passed"],
                )
                session.add(metric)
                metric_objects.append(metric)
            session.commit()
            session.expunge_all()
            return metric_objects

    # Test case operations

    def add_test_cases(self, run_id: str, test_cases: list[dict]) -> list[TestCase]:
        """Add test cases to a run."""
        with self.get_session() as session:
            tc_objects = []
            for tc in test_cases:
                test_case = TestCase(
                    run_id=run_id,
                    conversation_id=tc["conversation_id"],
                    input=tc["input"],
                    output=tc.get("output"),
                    context=tc.get("context"),
                )
                session.add(test_case)
                session.flush()  # Get the ID

                # Add scores
                for score in tc.get("scores", []):
                    tc_score = TestCaseScore(
                        test_case_id=test_case.id,
                        metric_name=score["metric_name"],
                        score=score["score"],
                        label=score.get("label"),
                        explanation=score.get("explanation"),
                    )
                    session.add(tc_score)

                # Add failure if present
                if tc.get("failure"):
                    failure = Failure(
                        test_case_id=test_case.id,
                        failure_type=tc["failure"]["failure_type"],
                        explanation=tc["failure"].get("explanation"),
                    )
                    session.add(failure)

                tc_objects.append(test_case)

            session.commit()
            session.expunge_all()
            return tc_objects

    def get_failure_summary(self, run_id: str) -> dict:
        """Get failure type distribution for a run."""
        with self.get_session() as session:
            failures = (
                session.query(Failure)
                .join(TestCase)
                .filter(TestCase.run_id == run_id)
                .all()
            )

            distribution = {}
            for f in failures:
                distribution[f.failure_type] = distribution.get(f.failure_type, 0) + 1

            total = len(failures)
            return {
                "total_failures": total,
                "distribution": distribution,
            }


# Global database instance (initialized on first use)
_db: Optional[Database] = None


def get_database(db_path: str = "eval_results.db") -> Database:
    """Get or create the global database instance."""
    global _db
    if _db is None or _db.db_path != db_path:
        _db = Database(db_path)
        _db.create_tables()
    return _db
