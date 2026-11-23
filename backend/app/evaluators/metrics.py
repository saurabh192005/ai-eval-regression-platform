import math
import statistics

from app.core.pricing import PRICES_PER_MILLION, PRICING_VERSION
from app.evaluators.exact_match import EVALUATOR_VERSION


def _p95(values: list[float]) -> float:
    s = sorted(values)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]


def compute_metrics(results, model_name: str) -> list[dict]:
    total = len(results)
    answered = [r for r in results if r.error is None]
    scored = [r for r in answered if r.is_correct is not None]
    out: list[dict] = []

    def add(name, value, direction, details=None):
        out.append({"metric_name": name, "value": float(value), "direction": direction, "details": details})

    errors = total - len(answered)
    add("error_rate", errors / total if total else 0, "lower_is_better", {"errors": errors, "total": total})

    if scored:
        correct = sum(1 for r in scored if r.is_correct)
        add("correctness_rate", correct / len(scored), "higher_is_better",
            {"correct": correct, "scored": len(scored), "evaluator": EVALUATOR_VERSION})

    lat = [r.latency_ms for r in answered if r.latency_ms is not None]
    if lat:
        add("latency_ms_avg", statistics.mean(lat), "lower_is_better")
        add("latency_ms_median", statistics.median(lat), "lower_is_better")
        add("latency_ms_p95", _p95(lat), "lower_is_better", {"sample_size": len(lat)})

    if answered:
        in_tok = sum(r.input_tokens or 0 for r in answered)
        out_tok = sum(r.output_tokens or 0 for r in answered)
        add("total_tokens", in_tok + out_tok, "lower_is_better",
            {"input_tokens": in_tok, "output_tokens": out_tok, "source": "provider_reported"})
        price = PRICES_PER_MILLION.get(model_name)
        if price:
            cost = (in_tok * price[0] + out_tok * price[1]) / 1_000_000
            add("estimated_cost_usd", cost, "lower_is_better",
                {"estimated": True, "pricing_version": PRICING_VERSION})
    return out