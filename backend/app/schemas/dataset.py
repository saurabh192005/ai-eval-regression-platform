from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    version: str = "v1"


class DatasetOut(DatasetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class TestCaseCreate(BaseModel):
    input_text: str = Field(min_length=1)
    expected_output: str | None = None
    evaluation_type: str = "exact_match"
    metadata: dict | None = None


class TestCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    input_text: str
    expected_output: str | None
    evaluation_type: str
    metadata: dict | None = Field(default=None, validation_alias="meta")
    created_at: datetime