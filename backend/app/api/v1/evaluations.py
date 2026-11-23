from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import (Dataset, EvaluationRun, MetricResult, ModelConfig, TestCase,
                               TestCaseResult)
from app.schemas.evaluation import EvaluationCreate, EvaluationOut, MetricOut, ResultOut
from app.services.evaluation_service import execute_run

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


def _get_run(db: Session, run_id: int) -> EvaluationRun:
    run = db.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return run


@router.post("", response_model=EvaluationOut, status_code=202)
def create_evaluation(payload: EvaluationCreate, background: BackgroundTasks, db: Session = Depends(get_db)):
    if payload.provider != "groq":
        raise HTTPException(status_code=422, detail="Only the 'groq' provider is supported")
    dataset = db.get(Dataset, payload.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    n_cases = db.scalars(select(TestCase.id).where(TestCase.dataset_id == dataset.id)).all()
    if not n_cases:
        raise HTTPException(status_code=422, detail="Dataset has no test cases")

    cfg = ModelConfig(provider=payload.provider, model_name=payload.model_name,
                      parameters=payload.parameters, prompt_version=payload.prompt_version)
    db.add(cfg)
    db.flush()
    run = EvaluationRun(dataset_id=dataset.id, dataset_version=dataset.version,
                        model_config_id=cfg.id, status="pending")
    db.add(run)
    db.commit()
    db.refresh(run)
    background.add_task(execute_run, run.id)
    return run


@router.get("/{run_id}", response_model=EvaluationOut)
def get_evaluation(run_id: int, db: Session = Depends(get_db)):
    return _get_run(db, run_id)


@router.get("/{run_id}/results", response_model=list[ResultOut])
def get_results(run_id: int, db: Session = Depends(get_db)):
    _get_run(db, run_id)
    return db.scalars(select(TestCaseResult).where(TestCaseResult.run_id == run_id)
                      .order_by(TestCaseResult.id)).all()


@router.get("/{run_id}/metrics", response_model=list[MetricOut])
def get_metrics(run_id: int, db: Session = Depends(get_db)):
    _get_run(db, run_id)
    return db.scalars(select(MetricResult).where(MetricResult.run_id == run_id)
                      .order_by(MetricResult.id)).all()