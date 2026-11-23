import time
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.evaluators.exact_match import is_match
from app.evaluators.metrics import compute_metrics
from app.models.models import EvaluationRun, MetricResult, ModelConfig, TestCase, TestCaseResult
from app.providers import groq_provider

REQUEST_DELAY_S = 0.5
MAX_RETRIES = 2


def _now():
    return datetime.now(timezone.utc)


def _call_with_retry(prompt: str, model: str, params: dict):
    res = None
    for attempt in range(MAX_RETRIES + 1):
        res = groq_provider.generate(prompt, model, temperature=params.get("temperature", 0.0))
        if res.error != "rate_limited" or attempt == MAX_RETRIES:
            break
        time.sleep(2 * (attempt + 1))
    return res


def execute_run(run_id: int) -> None:
    with SessionLocal() as db:
        run = db.get(EvaluationRun, run_id)
        cfg = db.get(ModelConfig, run.model_config_id)
        cases = db.scalars(
            select(TestCase).where(TestCase.dataset_id == run.dataset_id).order_by(TestCase.id)
        ).all()
        run.status = "running"
        run.started_at = _now()
        db.commit()

        final_status = "failed"
        try:
            for case in cases:
                res = _call_with_retry(case.input_text, cfg.model_name, cfg.parameters or {})
                correct = None
                if res.error is None and case.expected_output is not None:
                    correct = is_match(res.text or "", case.expected_output)
                db.add(TestCaseResult(
                    run_id=run_id, test_case_id=case.id, response=res.text, is_correct=correct,
                    latency_ms=res.latency_ms, input_tokens=res.input_tokens,
                    output_tokens=res.output_tokens, error=res.error,
                ))
                db.commit()
                time.sleep(REQUEST_DELAY_S)

            results = db.scalars(select(TestCaseResult).where(TestCaseResult.run_id == run_id)).all()
            for m in compute_metrics(results, cfg.model_name):
                db.add(MetricResult(run_id=run_id, **m))
            errors = sum(1 for r in results if r.error)
            if errors == 0:
                final_status = "completed"
            elif errors < len(results):
                final_status = "completed_with_errors"
        except Exception:
            db.rollback()
        finally:
            run = db.get(EvaluationRun, run_id)
            run.status = final_status
            run.finished_at = _now()
            db.commit()