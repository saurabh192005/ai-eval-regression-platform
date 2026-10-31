from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Dataset, TestCase
from app.schemas.dataset import DatasetCreate, DatasetOut, TestCaseCreate, TestCaseOut

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


def get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.post("", response_model=DatasetOut, status_code=201)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_db)):
    dataset = Dataset(**payload.model_dump())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.scalars(select(Dataset).order_by(Dataset.id)).all()


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    return get_dataset_or_404(db, dataset_id)


@router.post("/{dataset_id}/test-cases", response_model=list[TestCaseOut], status_code=201)
def add_test_cases(dataset_id: int, payload: list[TestCaseCreate], db: Session = Depends(get_db)):
    get_dataset_or_404(db, dataset_id)
    if not payload:
        raise HTTPException(status_code=422, detail="Provide at least one test case")
    cases = [
        TestCase(
            dataset_id=dataset_id,
            input_text=c.input_text,
            expected_output=c.expected_output,
            evaluation_type=c.evaluation_type,
            meta=c.metadata,
        )
        for c in payload
    ]
    db.add_all(cases)
    db.commit()
    for c in cases:
        db.refresh(c)
    return cases


@router.get("/{dataset_id}/test-cases", response_model=list[TestCaseOut])
def list_test_cases(dataset_id: int, db: Session = Depends(get_db)):
    get_dataset_or_404(db, dataset_id)
    return db.scalars(select(TestCase).where(TestCase.dataset_id == dataset_id).order_by(TestCase.id)).all()