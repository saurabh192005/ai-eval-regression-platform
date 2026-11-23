from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    dataset_id: int
    provider: str = "groq"
    model_name: str = Field(min_length=1)
    parameters: dict | None = None
    prompt_version: str | None = "v1"


class EvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    dataset_version: str
    model_config_id: int
    status: str
    is_baseline: bool
    started_at: datetime | None
    finished_at: datetime | None


class ResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_case_id: int
    response: str | None
    is_correct: bool | None
    latency_ms: float | None
    input_tokens: int | None
    output_tokens: int | None
    error: str | None


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_name: str
    value: float
    direction: str
    details: dict | None