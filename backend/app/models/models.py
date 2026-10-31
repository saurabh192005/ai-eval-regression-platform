from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"
    __test__ = False  # stops pytest from collecting this class

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id", ondelete="CASCADE"), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    expected_output: Mapped[str | None] = mapped_column(Text)
    evaluation_type: Mapped[str] = mapped_column(String(50), default="exact_match")
    meta: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="test_cases")


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    parameters: Mapped[dict | None] = mapped_column(JSON)
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    dataset_version: Mapped[str] = mapped_column(String(50))
    model_config_id: Mapped[int] = mapped_column(ForeignKey("model_configs.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    is_baseline: Mapped[bool] = mapped_column(default=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TestCaseResult(Base):
    __tablename__ = "test_case_results"
    __test__ = False

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id"), index=True)
    response: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column()
    latency_ms: Mapped[float | None] = mapped_column(Float)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)


class MetricResult(Base):
    __tablename__ = "metric_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True)
    metric_name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(30))  # higher_is_better / lower_is_better
    details: Mapped[dict | None] = mapped_column(JSON)


class RegressionReport(Base):
    __tablename__ = "regression_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    baseline_run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), index=True)
    candidate_run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    summary: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())